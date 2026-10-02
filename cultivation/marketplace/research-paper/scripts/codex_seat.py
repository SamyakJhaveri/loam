#!/usr/bin/env python3
r"""Run a paper-writing seat on a Codex model (codex.model in paper-tools.toml) from a Claude Code session.

    paper-tool codex_seat blind paper/sections/abstract.tex --venue "Example Conference 2030 (transit planning)"
    paper-tool codex_seat exemplar intro <paper id> paper/sections/abstract.tex paper/sections/introduction.tex
    paper-tool codex_seat whole all
    paper-tool codex_seat codetruth
    paper-tool codex_seat seat reviewer-generalist paper/build/main.txt
    paper-tool codex_seat save <codex output file> <report.md>
    paper-tool codex_seat merge <reports folder> <out folder>

Run from the project root. Each seat command (blind, exemplar, whole, codetruth, seat) writes a work folder
and a prompt under $TMPDIR/codex_seats/ and prints the one command that runs Codex. If your sandbox excludes
only the bare `node .../codex-companion.mjs` command, run it exactly as printed: a `cd`, a redirect or a pipe
added to it puts it back in the sandbox and it fails with EPERM or "workspace routing discovery failed".
Long runs belong in the lead session's background: run it with run_in_background; the task output file holds
the report, and `save` strips the progress lines from it.
The companion script is codex.companion, or else the one in the newest installed version of the Codex plugin.

- blind: the blind-reader seat (the plugin's agents/blind-reader.md) on one section, comments removed. The
  text, the venue and the paper.macros map are pasted into the prompt and Codex starts in an empty folder,
  so it loads no AGENTS.md and reads no file.
- exemplar: one exemplar paper (codex.manifest), read in full from its local text (codex.corpus_dir/<id>.txt),
  with the questions of section 2 of the plugin's docs/section-loop.md for the section type, then compared
  with our sections.
- whole: each named exemplar paper (or all) read in full against our whole built text (build.text).
- codetruth: one read-only pass, in the project root, that checks what the paper says the code does.
- seat: a review seat (the plugin's agents/<seat>.md) on PAPER. The work folder holds PAPER at its project
  path, the project's contract (paper/tools/contract.md) and config, and the plugin's scripts under plugin/,
  where the seat text's ${CLAUDE_PLUGIN_ROOT} now points; Codex runs with --write inside that folder only
  and writes OUT there. Copy OUT back yourself.
- save: copies a run's report without the progress lines; --text counts the lines of a file the model read.
- merge: pools the jsonl suggestions of saved reports (<paper>__<model>.md) into one file per section.
"""

import argparse
import csv
import json
import os
import re
import shutil
import sys
from pathlib import Path

from paper_config import load

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent
AGENTS = PLUGIN / "agents"
GUIDE = PLUGIN / "docs" / "section-loop.md"  # its section 2 table holds the exemplar questions
CONTRACT = Path("paper/tools/contract.md")  # relative to the project root
CODEX_CACHE = ".claude/plugins/cache/openai-codex/codex"  # under the home folder
WORK = Path(os.environ.get("TMPDIR", "/tmp")) / "codex_seats"
SECTION_TYPES = {
    "method": "Method",
    "results": "Results, discussion",
    "intro": "Abstract, introduction, related work",
}


def strip_comments(tex: str) -> str:
    return "\n".join(line for line in tex.splitlines() if not line.lstrip().startswith("%"))


def numbered(text: str) -> str:
    return "\n".join(f"{i:4d}  {line}" for i, line in enumerate(text.splitlines(), 1))


def macro_words(macros: dict) -> str:
    """paper.macros as prose: each text macro and the words it prints."""
    return "; ".join(f'{macro} prints "{text}"' for macro, text in macros.items())


def macro_prose(macros: dict) -> str:
    """What the LaTeX markup in a pasted section means, from paper.macros."""
    parts = ["LaTeX source", macro_words(macros), "a \\ref is a cross reference you cannot follow"]
    return "; ".join(p for p in parts if p)


def agent_body(seat: str) -> str:
    text = (AGENTS / f"{seat}.md").read_text()
    return text.split("\n---\n", 1)[1].strip()  # drop the YAML front matter


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        sys.exit(
            f"codex_seat: the agent file no longer contains {old!r}; update codex_seat.py to match it"
        )
    return text.replace(old, new, 1)


def companion(cfg) -> Path:
    """codex.companion, else codex-companion.mjs of the newest installed Codex plugin version."""
    if cfg["codex"]["companion"] is not None:
        return cfg["codex"]["companion"]
    found = sorted(
        (Path.home() / CODEX_CACHE).glob("*/scripts/codex-companion.mjs"),
        key=lambda p: [int(n) for n in re.findall(r"\d+", p.parents[1].name)],
    )
    if not found:
        sys.exit(
            f"codex_seat: no ~/{CODEX_CACHE}/*/scripts/codex-companion.mjs; install the Codex plugin, "
            "or set codex.companion in paper-tools.toml"
        )
    return found[-1]


def contract(cfg) -> Path:
    path = cfg["project"]["root"] / CONTRACT
    if not path.is_file():
        sys.exit(
            f"codex_seat: no review contract at {path}; copy the plugin's templates/contract.md there"
        )
    return path


def workdir(name: str) -> Path:
    d = WORK / name
    if d.exists():
        shutil.rmtree(d)
    (d / "cwd").mkdir(parents=True)
    return d


def finish(
    cfg, d: Path, prompt: str, model: str, effort: str, write: bool, cwd=None, tools="Read"
) -> None:
    (d / "prompt.md").write_text(prompt)
    cwd = cwd or d / "cwd"
    print(f"prompt: {d / 'prompt.md'} ({len(prompt)} characters)")
    if model == "fable":  # headless Claude Code; runs inside the sandbox, so a script is fine
        (d / "run.sh").write_text(
            f"cd {cwd} && claude -p --strict-mcp-config --no-session-persistence --setting-sources user "
            f"--tools {tools} --model claude-fable-5-1 --effort {effort} --output-format stream-json --verbose "
            f"< {d / 'prompt.md'} > {d / 'out.jsonl'} 2> {d / 'err.log'}\n"
        )
        print(f"bash {d / 'run.sh'}   # sandboxed; needs allowed_domains api.anthropic.com")
        return
    flags = " --write" if write else ""
    print(
        f"node {companion(cfg)} task{flags} --model {model} --effort {effort} --cwd {cwd} --prompt-file {d / 'prompt.md'}"
    )


def manifest(cfg) -> dict:
    path = cfg["codex"]["manifest"]
    if not path.is_file():
        sys.exit(
            f"codex_seat: no exemplar manifest at {path} (codex.manifest); "
            "start from the plugin's templates/exemplar_manifest.tsv"
        )
    return {r["id"]: r for r in csv.DictReader(path.open(), delimiter="\t")}


def question_row(row: str) -> tuple:
    # section 2 only: section 3 has a "Method" row too
    table = GUIDE.read_text().partition("\n## 2.")[2].partition("\n## 3.")[0]
    m = re.search(rf"^\| {re.escape(row)} \| (.+?) \| (.+?) \|$", table, re.M)
    if not m:
        sys.exit(f"codex_seat: no row {row!r} in the section 2 table of {GUIDE.name}")
    return m.group(1), m.group(2)


def blind_body() -> str:
    """The blind-reader seat text, rewritten for a reader that gets the section pasted in."""
    body = agent_body("blind-reader").split("\n## How the lead uses this seat")[0]
    body = replace_once(body, "Read exactly one file, once,", "Read exactly one text, once,")
    body = replace_once(
        body, "the path the lead gives you", "the text pasted at the end of this message"
    )
    body = replace_once(
        body,
        "you have only the Read tool",
        "run no shell command, web search or other tool; the text is pasted below",
    )
    return body


def cmd_blind(a, cfg) -> None:
    src = Path(a.section)
    text = strip_comments(src.read_text())
    body = blind_body()
    d = workdir(f"blind_{src.stem}_{a.model}")
    # the seat takes the venue, its field and the macro map from the task message; here that is the prompt
    task = (
        f"Venue and field: {a.venue}\n"
        f"Text macros (paper.macros): {macro_words(cfg['paper']['macros']) or 'none'}\n"
    )
    prompt = (
        f"{body}\n\n## Task message\n\n{task}\n"
        f"## The text ({src.name}, line-numbered)\n\n```latex\n{numbered(text)}\n```\n"
    )
    finish(cfg, d, prompt, a.model, a.effort, write=False)


def cmd_exemplar(a, cfg) -> None:
    papers = manifest(cfg)
    if a.paper not in papers:
        sys.exit(f"codex_seat: unknown paper {a.paper!r}; ids: {', '.join(papers)}")
    paper = papers[a.paper]
    txt = cfg["codex"]["corpus_dir"] / f"{a.paper}.txt"
    if not txt.exists():
        sys.exit(
            f"codex_seat: {txt} is missing; download the PDF in the manifest and run pdftotext on it"
        )
    row = SECTION_TYPES[a.type]
    questions_a, questions_b = question_row(row)
    ours = "\n".join(
        f"% ===== {Path(s).name}\n{strip_comments(Path(s).read_text())}" for s in a.ours
    )
    d = workdir(f"exemplar_{a.type}_{a.paper}")
    shutil.copy(txt, d / "cwd" / txt.name)
    prompt = (
        (PLUGIN / "prompts" / "codex_exemplar_reader.md")
        .read_text()
        .format(
            file=txt.name,
            title=paper["title"],
            url=paper["url"],
            section_type=row.lower(),
            questions_a=questions_a,
            questions_b=questions_b,
            macros=macro_prose(cfg["paper"]["macros"]),
            ours=numbered(ours),
        )
    )
    finish(cfg, d, prompt, a.model, a.effort, write=False)


def cmd_whole(a, cfg) -> None:
    papers = manifest(cfg)
    ids = list(papers) if a.papers == ["all"] else a.papers
    unknown = [p for p in ids if p not in papers]
    if unknown:
        sys.exit(f"codex_seat: unknown papers {unknown}; ids: {', '.join(papers)}")
    q = {k: question_row(row) for k, row in SECTION_TYPES.items()}
    template = (PLUGIN / "prompts" / "exemplar_reader_whole.md").read_text()
    ours = a.ours if a.ours is not None else cfg["build"]["text"]
    for pid in ids:
        txt = cfg["codex"]["corpus_dir"] / f"{pid}.txt"
        d = workdir(f"whole_{pid}_{a.model}")
        shutil.copy(txt, d / "cwd" / txt.name)
        shutil.copy(ours, d / "cwd" / "ours.txt")
        shutil.copy(contract(cfg), d / "cwd" / "contract.md")
        prompt = template.format(
            file=txt.name,
            title=papers[pid]["title"],
            url=papers[pid]["url"],
            max_pages=cfg["limits"]["max_pages"],
            q_method_a=q["method"][0],
            q_method_b=q["method"][1],
            q_results_a=q["results"][0],
            q_results_b=q["results"][1],
            q_intro_a=q["intro"][0],
            q_intro_b=q["intro"][1],
        )
        finish(cfg, d, prompt, a.model, a.effort, write=False)


def cmd_codetruth(a, cfg) -> None:
    d = workdir(f"codetruth_{a.model}")
    paper = a.paper if a.paper is not None else cfg["build"]["text"]
    prompt = (
        (PLUGIN / "prompts" / "codetruth.md")
        .read_text()
        .format(paper=paper, sections_dir=cfg["paper"]["sections_dir"])
    )
    root = cfg["project"]["root"]
    finish(cfg, d, prompt, a.model, a.effort, write=False, cwd=root, tools="Read,Grep,Glob")


def cmd_seat(a, cfg) -> None:
    paper = Path(a.paper)
    d = workdir(f"seat_{a.seat}")
    cwd = d / "cwd"
    tools = cwd / CONTRACT.parent
    tools.mkdir(parents=True)
    shutil.copy(contract(cfg), tools / "contract.md")
    if cfg["project"]["config"] is not None:  # the validator reads paper.smallcaps_names from it
        shutil.copy(cfg["project"]["config"], tools / "paper-tools.toml")
    shutil.copytree(HERE, cwd / "plugin/scripts", ignore=shutil.ignore_patterns("__pycache__"))
    (cwd / paper).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(paper, cwd / paper)
    (cwd / "out").mkdir()
    inputs = f"PAPER={paper}\nROOT={cwd}\nOUT={cwd / 'out'}\n"
    body = agent_body(a.seat).replace("${CLAUDE_PLUGIN_ROOT}", str(cwd / "plugin"))
    prompt = (
        f"{body}\n\n## Inputs\n\n{inputs}\n"
        "Your working directory is ROOT. Write only inside OUT. Do not use web search unless your seat file allows it.\n"
    )
    finish(cfg, d, prompt, a.model, a.effort, write=True, tools="Read,Grep,Glob,Bash")


def cmd_save(a, cfg) -> None:
    raw = Path(a.output).read_text()
    if a.output.endswith(".jsonl"):  # headless Claude stream-json: final result and Read calls
        events = [json.loads(ln) for ln in raw.splitlines() if ln.startswith("{")]
        report = next(
            (e.get("result", "") for e in reversed(events) if e.get("type") == "result"), ""
        )
        uses = [
            b
            for e in events
            if e.get("type") == "assistant"
            for b in e["message"].get("content", [])
            if b.get("type") == "tool_use"
        ]
        reads = [b["input"] for b in uses]
        searches = sum(b["name"] in ("WebSearch", "WebFetch") for b in uses)
    else:  # codex-companion progress lines, then the final message
        lines = raw.splitlines()
        report = "\n".join(
            ln
            for ln in lines
            if not ln.startswith("[codex] ") and not re.fullmatch(r"\[exited with code \d+\]", ln)
        )
        reads = [ln for ln in lines if ln.startswith("[codex] Running command: ")]
        searches = sum(ln.startswith("[codex] Searching: ") for ln in lines)
    Path(a.dest).parent.mkdir(parents=True, exist_ok=True)
    Path(a.dest).write_text(report.strip() + "\n")
    print(
        f"wrote {a.dest} ({report.count(chr(10)) + 1} lines); tool calls: {len(reads)}; web searches: {searches}"
    )
    for text in a.text or []:  # which lines of each file the model printed
        name = Path(text).name
        # count newlines, not splitlines(): that also splits on pdftotext's page breaks (\f)
        total = Path(text).read_text().count("\n")
        seen = set()
        for r in reads:
            if isinstance(r, dict):  # a Read call: offset (1-based) and limit (default 2000)
                if Path(r.get("file_path", "")).name == name:
                    lo = int(r.get("offset") or 1)
                    seen.update(range(lo, min(lo + int(r.get("limit") or 2000), total + 1)))
            elif name in r:
                if re.search(rf"\bcat\b[^|]*{re.escape(name)}", r):
                    seen.update(range(1, total + 1))
                for lo, hi in re.findall(r"(\d+),(\d+)p", r):
                    seen.update(range(int(lo), min(int(hi), total) + 1))
        print(
            f"lines of {name} read: {len(seen)} of {total} ({100 * len(seen) / max(total, 1):.1f}%)"
        )


def flat(s: str) -> str:
    """Lowercase letters and digits only, so a quote matches pdftotext output across breaks and hyphens."""
    return re.sub(r"[^a-z0-9]", "", s.lower().replace("-\n", ""))


def section_names(cfg) -> list:
    """Our section file stems in paper order, abstract first (paper.sections, else every .tex file)."""
    p = cfg["paper"]
    names = p["sections"] or [
        f.stem for f in sorted(p["sections_dir"].glob("*.tex")) if f != p["abstract_tex"]
    ]
    return ([p["abstract_tex"].stem] if p["abstract_tex"] else []) + names


def tex_text(tex: str) -> str:
    """Section source as plain words: comments, \\ref/\\cite/\\label arguments and command names removed."""
    tex = strip_comments(tex)
    tex = re.sub(r"\\(?:ref|cite|label|eqref|autoref)\{[^}]*\}", "", tex)
    return re.sub(r"\\[A-Za-z]+", "", tex)


def cmd_merge(a, cfg) -> None:
    """Pool the jsonl SUGGESTIONS blocks of saved reports (<paper>__<model>.md) into one file per section."""
    # A quote is found if it is in the PDF text or in the section sources: pdftotext interleaves the two
    # columns near floats, so a real sentence can be split in the built text.
    sources = sorted(cfg["paper"]["sections_dir"].glob("*.tex"))
    tex = "".join(tex_text(f.read_text()) for f in sources)
    ours = flat(Path(a.ours if a.ours is not None else cfg["build"]["text"]).read_text())
    ours += "|" + flat(tex)
    # a reader's section name maps to the first of our sections whose file name (letters only) it
    # contains, so "II. Related Work" goes to related-work; a name that matches none goes to "other"
    keys = [("".join(re.findall(r"[a-z]+", s.lower())), s) for s in section_names(cfg)]
    rows = []
    for f in sorted(Path(a.reports).glob("*__*.md")):
        paper, model = f.stem.split("__")
        for block in re.findall(r"```jsonl\n(.*?)```", f.read_text(), re.S):
            for line in block.splitlines():
                try:
                    s = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(s, dict) and s.get("ours"):
                    s.update(paper=paper, model=model, found=flat(s["ours"]) in ours)
                    rows.append(s)
    groups = []  # suggestions on the same span of our text, by containment of the flattened quote
    for s in rows:
        key = flat(s["ours"])
        for g in groups:
            if key and (key in g["key"] or g["key"] in key):
                g["items"].append(s)
                g["key"] = max(g["key"], key, key=len)
                break
        else:
            groups.append({"key": key, "items": [s]})
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    by_section = {}
    for g in groups:
        name = re.sub(r"\s+", "", g["items"][0].get("section", "")).lower()
        sec = next((file for key, file in keys if key and key in name), "other")
        by_section.setdefault(sec, []).append(g)
    for sec, gs in by_section.items():

        def rank(g):
            items = g["items"]
            return (
                -len({i["model"] for i in items}),
                -len({i["paper"] for i in items}),
                min(int(i.get("priority") or 3) for i in items),
            )

        lines = [
            f"# Suggestions for {sec}",
            "",
            "Suggestions only, pooled from the exemplar reads; nothing here is applied to the paper.",
            "Ranked by how many models, then how many exemplar papers, made a suggestion on the same text.",
            "`quote not found` means the quoted text of ours is not in the built PDF text: check it before use.",
            "",
        ]
        for n, g in enumerate(sorted(gs, key=rank), 1):
            items = g["items"]
            models = sorted({i["model"] for i in items})
            papers = sorted({i["paper"] for i in items})
            found = "" if all(i["found"] for i in items) else " - quote not found"
            lines += [
                f"## {n}. {len(models)} model(s), {len(papers)} paper(s){found}",
                "",
                f"Ours: {items[0]['ours']}",
                "",
            ]
            for i in items:
                kept = "" if i.get("facts_kept", True) else " [changes a fact]"
                lines.append(
                    f"- {i['model']} from {i['paper']} ({i.get('dimension', '?')}, {i.get('kind', '?')}, "
                    f"priority {i.get('priority', '?')}){kept}: {i.get('proposal', '')}"
                )
                lines.append(
                    f"  - Exemplar ({i.get('exemplar_where', '?')}): {i.get('exemplar_quote', '')}"
                )
                lines.append(f"  - Why: {i.get('why', '')}")
            lines.append("")
        (out / f"{sec}.md").write_text("\n".join(lines))
        print(f"{out / (sec + '.md')}: {len(gs)} suggestion groups")
    print(
        f"{len(rows)} suggestions from {len({(r['paper'], r['model']) for r in rows})} reports; "
        f"{sum(not r['found'] for r in rows)} quote not found"
    )


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    seats = (
        ("blind", cmd_blind),
        ("exemplar", cmd_exemplar),
        ("whole", cmd_whole),
        ("codetruth", cmd_codetruth),
        ("seat", cmd_seat),
    )
    for name, fn in seats:
        s = sub.add_parser(name)
        s.set_defaults(fn=fn)
        s.add_argument(
            "--model",
            default=None,
            help="a Codex model, or fable for headless Claude Code (default: codex.model in paper-tools.toml)",
        )
        s.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh"])
        if name == "blind":
            s.add_argument("section")
            s.add_argument(
                "--venue",
                required=True,
                help='the venue and its field, for example "Example Conference 2030 (transit planning)"',
            )
        elif name == "exemplar":
            s.add_argument("type", choices=SECTION_TYPES)
            s.add_argument("paper", help="an id from the exemplar manifest (codex.manifest)")
            s.add_argument("ours", nargs="+", help="our section files to compare with")
        elif name == "whole":
            s.add_argument(
                "papers", nargs="+", help="ids from the exemplar manifest (codex.manifest), or all"
            )
            s.add_argument(
                "--ours", default=None, help="pdftotext of our PDF (default: build.text)"
            )
        elif name == "codetruth":
            s.add_argument(
                "--paper", default=None, help="pdftotext of our PDF (default: build.text)"
            )
        else:
            s.add_argument("seat", help="a file name under the plugin's agents/, without .md")
            s.add_argument("paper", help="PAPER, relative to the project root")
    s = sub.add_parser("merge")
    s.set_defaults(fn=cmd_merge)
    s.add_argument("reports", help="folder of saved reports named <paper>__<model>.md")
    s.add_argument("out", help="folder for one suggestions file per section")
    s.add_argument("--ours", default=None, help="pdftotext of our PDF (default: build.text)")
    s = sub.add_parser("save")
    s.set_defaults(fn=cmd_save)
    s.add_argument("output", help="a codex task output file, or a Fable out.jsonl")
    s.add_argument("dest")
    s.add_argument(
        "--text",
        action="append",
        help="a file the model was told to read in full; reports how many of its lines it read (repeatable)",
    )
    return p


def main(argv=None) -> None:
    a = parser().parse_args(argv)
    cfg = load()
    if getattr(a, "model", "") is None:
        a.model = cfg["codex"]["model"]
    a.fn(a, cfg)


if __name__ == "__main__":
    main()
