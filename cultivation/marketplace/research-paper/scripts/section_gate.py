#!/usr/bin/env python3
r"""One command for the mechanical checks on a rewritten paper section (the gate step of docs/section-loop.md).

    paper-tool section_gate paper/sections/results.tex
    paper-tool section_gate paper/sections/results.tex --base HEAD~1
    paper-tool section_gate paper/sections/results.tex --no-build

Run from inside the project; the project root and config come from paper_config.py. It compares the file on
disk with `git show BASE:FILE` (default HEAD, FILE relative to the project root) and runs, in order:
1. Tokens (check_revision_token_conservation.py): FAIL when a number, \cite key or \ref target of the base
   version appears nowhere in the revision. A repeated mention that now appears once is listed, not failed.
2. Banned terms: FAIL on a match of any regex in the banned-terms file (terms.banned; the project's rulings)
   outside % comments. With no such file, a NOTE says so and no term is banned.
3. style_lint.py (beside this script) on the file.
4. The build (build.command, run from the project root), undefined references in its log (build.log), then
   paper_limits.py.
5. Slack: the page where the references start and how many lines follow the heading on that page, and the pages
   the section occupies. A heading alone at the top of a page means the body is exactly full.
6. Extract: the section with % comment lines removed, written under $TMPDIR for the `blind-reader` agent.

Exit 0 when every check passes, 1 otherwise. The blind read itself is an agent run, not part of this script.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from paper_config import load

HERE = Path(__file__).resolve().parent
STYLE_LINT = HERE / "style_lint.py"


def strip_comments(tex: str) -> str:
    return "\n".join(line for line in tex.splitlines() if not line.lstrip().startswith("%"))


def lost_tokens(removed: dict, revision: str) -> list:
    """Tokens of the base version that appear nowhere in the revision (number words are skipped).

    A number written with thousands separators is kept if the revision writes it without them.
    """
    text = strip_comments(revision).replace("\\%", "%").replace("{,}", ",")
    lost = []
    for token in removed:
        if not re.search(r"\d", token) and not token.startswith("\\"):
            continue
        forms = {token}
        if re.fullmatch(r"\d{1,3}(,\d{3})+", token):
            forms.add(token.replace(",", ""))
        if not any(
            re.search(r"(?<![\w.])" + re.escape(form) + r"(?![\w%]|\.\d)", text) for form in forms
        ):
            lost.append(token)
    return lost


def banned_hits(revision: str, patterns: list) -> list:
    hits = []
    for number, line in enumerate(revision.splitlines(), 1):
        if line.lstrip().startswith("%"):
            continue
        for pattern in patterns:
            if re.search(pattern, line):
                hits.append((number, pattern, line.strip()[:90]))
    return hits


def read_patterns(path: Path) -> list:
    rows = [line.split("#")[0].strip() for line in path.read_text().splitlines()]
    return [row for row in rows if row]


def squash(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def slack(pdf_text: str, section_title: str) -> dict:
    """Where the references start and which pages the section occupies, from a pdftotext dump."""
    pages = pdf_text.split("\f")
    out = {"refs_page": None, "lines_after_refs": None, "section_pages": []}
    for number, page in enumerate(pages, 1):
        lines = page.splitlines()
        for index, line in enumerate(lines):
            if squash(line) in ("REFERENCES", "BIBLIOGRAPHY") and out["refs_page"] is None:
                out["refs_page"] = number
                out["lines_after_refs"] = len([x for x in lines[index + 1 :] if x.strip()])
    title = squash(section_title)
    heading = re.compile(r"^[IVX]+\. .*[A-Z] ?[A-Z]")
    starts = [
        n
        for n, page in enumerate(pages, 1)
        if any(heading.match(x) and squash(x).endswith(title) for x in page.splitlines())
    ]
    if starts:
        heads = [
            n
            for n, page in enumerate(pages, 1)
            if n >= starts[0]
            and any(heading.match(x) and not squash(x).endswith(title) for x in page.splitlines())
        ]
        last = min(heads[0] if heads else len(pages), out["refs_page"] or len(pages))
        out["section_pages"] = [starts[0], last]
    return out


def run(cmd: list, cwd=None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", type=Path)
    parser.add_argument("--base", default="HEAD")
    parser.add_argument(
        "--banned", type=Path, help="banned-terms file (default: terms.banned in paper-tools.toml)"
    )
    parser.add_argument("--no-build", action="store_true")
    args = parser.parse_args(argv)
    cfg = load()
    root = cfg["project"]["root"]

    revision = args.file.read_text()
    failed = []

    try:
        rel = args.file.resolve().relative_to(root.resolve())
    except ValueError:  # outside the project: git show fails below and says why
        rel = args.file
    base = run(["git", "show", f"{args.base}:{rel}"], cwd=root)
    if base.returncode != 0:
        print(f"FAIL tokens: cannot read {args.base}:{rel}: {base.stderr.strip()}")
        return 1
    with tempfile.NamedTemporaryFile("w", suffix=".tex", delete=False) as handle:
        handle.write(base.stdout)
    check = run(
        [sys.executable, str(HERE / "check_revision_token_conservation.py"), "pair"]
        + ["--source", handle.name, "--revision", str(args.file)]
    )
    os.unlink(handle.name)
    delta = json.loads(check.stdout)
    removed = {}
    for key in ("numbers_delta", "citations_delta", "latex_keys_delta"):
        removed.update(delta[key]["removed"])
    lost = lost_tokens(removed, revision)
    fewer = sorted(set(removed) - set(lost))
    print(
        f"{'FAIL' if lost else 'PASS'} tokens against {args.base}: lost {lost or 'none'}; mentioned less often {fewer}"
    )
    print(
        f"     added numbers {sorted(delta['numbers_delta']['added'])}; strength words {delta['strength_delta']}"
    )
    if lost:
        failed.append("tokens")

    banned = args.banned if args.banned is not None else cfg["terms"]["banned"]
    if args.banned is None and (banned is None or not banned.exists()):
        print(f"NOTE banned terms: no file at {banned} (terms.banned); no term is banned")
    else:
        hits = banned_hits(revision, read_patterns(banned))
        print(f"{'FAIL' if hits else 'PASS'} banned terms ({banned.name})")
        for number, pattern, line in hits:
            print(f"     {args.file}:{number}: /{pattern}/ {line}")
        if hits:
            failed.append("banned")

    lint = run([sys.executable, str(STYLE_LINT), str(args.file)])
    print(f"{'PASS' if lint.returncode == 0 else 'FAIL'} style_lint: {lint.stdout.strip()[-200:]}")
    if lint.returncode != 0:
        failed.append("style_lint")

    if not args.no_build:
        command = cfg["build"]["command"]
        log = cfg["build"]["log"]
        build = run(command, cwd=root)
        undefined = (
            log.read_text(errors="replace").count("undefined") if log and log.exists() else -1
        )
        ok = build.returncode == 0 and undefined == 0
        print(
            f"{'PASS' if ok else 'FAIL'} {' '.join(command)} exit {build.returncode}, "
            f"undefined references {undefined}"
        )
        if not ok:
            failed.append("build")
        limits = run([sys.executable, str(HERE / "paper_limits.py")])
        print(limits.stdout.strip())
        if limits.returncode != 0:
            failed.append("paper_limits")
        title = re.search(r"\\section\{([^}]*)\}", revision)
        text = run(["pdftotext", str(cfg["build"]["pdf"]), "-"]).stdout
        info = slack(text, title.group(1) if title else "")
        print(
            f"NOTE slack: references start on page {info['refs_page']} with {info['lines_after_refs']} "
            f"lines after the heading; section pages {info['section_pages']}"
        )

    extract = Path(os.environ.get("TMPDIR", "/tmp")) / f"{args.file.stem}_extract.tex"
    extract.write_text(strip_comments(revision) + "\n")
    print(
        f"NOTE extract for blind-reader: {extract} ({len(strip_comments(revision).split())} words)"
    )

    print(f"section_gate: {'FAILED ' + ', '.join(failed) if failed else 'all checks passed'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
