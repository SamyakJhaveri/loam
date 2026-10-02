#!/usr/bin/env python3
"""Turn the exemplar-advisor workflow journal into evidence files: raw results, one suggestions file per
section, measured read coverage, and quote checks.

    paper-tool build_suggestions <workflow transcript dir> <out dir>

The workflow transcript dir (workflows/exemplar_advisor.js) holds journal.jsonl and agent-<id>.jsonl.
Saved code-truth reports in <out dir>/codetruth/*.md (codex_seat codetruth) and attack audits in
<out dir>/attack/*.md (prompts/codex_attack.md), each named after the model that wrote it, are matched to
the suggestions when present. Paths come from paper-tools.toml: codex.corpus_dir, build.text,
paper.sections_dir; paper.macros gives the words a quote may hold in place of a macro.
"""

import json
import re
import sys
from pathlib import Path

from codex_seat import flat, section_names, tex_text
from paper_config import load


def journal(wf: Path) -> dict:
    """label -> (agent id, result) for every agent that returned a result."""
    labels, results = {}, {}
    for ln in filter(None, (wf / "journal.jsonl").read_text().split("\n")):
        e = json.loads(ln)
        if e["type"] == "started":
            labels[e["agentId"]] = e["label"]
        elif e["type"] == "result":
            results[labels[e["agentId"]]] = (e["agentId"], e["result"])
    return results


def coverage(wf: Path, agent_id: str, root: Path) -> dict:
    """Measured read coverage, from a reader's own transcript (successful Read results only)."""
    calls, seen = {}, {}
    for ln in filter(None, (wf / f"agent-{agent_id}.jsonl").read_text().split("\n")):
        content = json.loads(ln).get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for b in content:
            if b.get("type") == "tool_use" and b["name"] == "Read":
                calls[b["id"]] = str(Path(root, b["input"]["file_path"]).resolve())
            elif (
                b.get("type") == "tool_result"
                and b.get("tool_use_id") in calls
                and not b.get("is_error")
            ):
                text = (
                    b["content"]
                    if isinstance(b["content"], str)
                    else "".join(c.get("text", "") for c in b["content"] if isinstance(c, dict))
                )
                nums = [int(m) for m in re.findall(r"^\s*(\d+)\t", text, re.M)]
                seen.setdefault(calls[b["tool_use_id"]], set()).update(nums)
    return seen


def in_ours(q: str, ours_flat: str, words: str) -> bool:
    """Verbatim in the PDF text or the sources; a quote taken from the LaTeX source is matched piece by
    piece around its macros, the words they print, cross references and citations."""
    if not flat(q):
        return False
    if flat(q) in ours_flat or flat(tex_text(q)) in ours_flat:
        return True
    pieces = re.split(rf"\\[A-Za-z]+(?:\{{[^}}]*\}})?{words}|\[\d+(?:[,-] ?\d+)*\]|\.\.\.|…", q)
    pieces = [flat(x) for x in pieces if len(flat(x)) >= 12]
    return bool(pieces) and all(x in ours_flat for x in pieces)


def in_paper(paper: str, q: str, corpus_flat: dict) -> bool:
    key = flat(q)
    ids = [p for p in corpus_flat if p in re.sub(r"[^a-z0-9]", "", paper.lower())] or list(
        corpus_flat
    )
    # readers may elide with "..." inside a quote: every piece of 25+ characters must be found
    pieces = [flat(p) for p in re.split(r"\.\.\.|…|\[\.\.\.\]", q)]
    pieces = [p for p in pieces if len(p) >= 25] or [key]
    return any(all(p in corpus_flat[i] for p in pieces) for i in ids)


def codetruth(path: Path, who: str) -> list:
    rows = []
    for block in re.findall(r"```jsonl\n(.*?)```", path.read_text(), re.S):
        for line in block.splitlines():
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows.append({"who": who, "key": flat(r["ours"]), **r})
    return rows


def truth_hits(ours: str, truth: list) -> list:
    """Code-truth findings on our sentence, matched by overlap of the flattened text."""
    key = flat(ours)
    if len(key) < 30:
        return []
    return [
        t
        for t in truth
        if key in t["key"]
        or t["key"] in key
        or any(key[i : i + 60] in t["key"] for i in range(0, max(1, len(key) - 60), 20))
    ]


def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        sys.exit("usage: build_suggestions.py <workflow transcript dir> <out dir>")
    wf, out = Path(argv[0]), Path(argv[1])
    cfg = load()
    root = cfg["project"]["root"]
    corpus = cfg["codex"]["corpus_dir"]
    main_txt = cfg["build"]["text"]

    # ---- journal
    results = journal(wf)
    for sub in ("reads", "advisors", "checks", "suggestions"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    for label, (_, res) in results.items():
        kind, _, name = label.partition(":")
        folder = {"read": "reads", "read-retry": "reads", "advise": "advisors", "check": "checks"}
        path = out / folder[kind] / f"{name}.json" if kind in folder else out / "coordinator.json"
        path.write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    advice = {
        s["section"]: s
        for label, (_, res) in results.items()
        if label.startswith("advise:")
        for s in res["sections"]
    }
    order = section_names(cfg)
    keys = sorted(advice, key=lambda k: order.index(k) if k in order else len(order))
    verdicts = {
        r["id"]: r
        for label, (_, res) in results.items()
        if label.startswith("check:")
        for r in res["results"]
    }

    # ---- measured read coverage
    cov_rows, missing_cov, papers_read = [], [], set()
    for label, (aid, res) in results.items():
        if not label.startswith("read"):
            continue
        seen = coverage(wf, aid, root)
        group = label.split(":", 1)[1].split("+")
        papers_read.update(group)
        for f in [corpus / f"{g}.txt" for g in group] + [main_txt]:
            total = f.read_text().count("\n")
            got = len({n for n in seen.get(str(f.resolve()), set()) if n <= total})
            cov_rows.append((label.split(":", 1)[1], f.name, got, total))
            if got < total:
                missing_cov.append((label, f.name, got, total))

    # ---- quote checks
    sources = sorted(cfg["paper"]["sections_dir"].glob("*.tex"))
    tex_all = "".join(tex_text(f.read_text()) for f in sources)
    ours_flat = flat(main_txt.read_text()) + "|" + flat(tex_all)
    corpus_flat = {f.stem: flat(f.read_text()) for f in corpus.glob("*.txt")}
    # the words the paper's macros print, so a quote that mixes source and PDF text still matches
    words = "".join(rf"|\b{re.escape(w)}\b" for w in cfg["paper"]["macros"].values() if w)

    # ---- code-truth findings, matched to suggestions by overlap of the paper sentence
    truth = [r for p in sorted((out / "codetruth").glob("*.md")) for r in codetruth(p, p.stem)]

    # ---- attack audits of the final list, by suggestion id
    attack = {}
    attack_files = sorted((out / "attack").glob("*.md"))
    for att in attack_files:
        # by line, not by fenced block: a code snippet inside a finding can itself contain a fence
        for line in att.read_text().split("\n"):
            if line.startswith('{"id"'):
                r = {**json.loads(line), "who": att.stem}
                # ids are "<section file stem>-NN"; a stem may hold hyphens and digits
                for i in re.findall(r"\w[\w-]*-\d+", json.dumps(r.get("id", ""))):
                    attack.setdefault(i, []).append(r)

    # ---- per-section files
    coord = results.get("coordinate", (None, None))[1]
    final = (
        {s["section"]: {f["id"]: f for f in s["final"]} for s in coord["sections"]} if coord else {}
    )
    top = coord["top"] if coord else []
    summary, stats, attacked = [], {"ours_missing": [], "quote_missing": []}, {}
    for key in keys:
        adv = advice[key]
        checks = {c["id"]: c for c in adv["checks"]}
        fin = final.get(key, {})
        order_in = sorted(
            adv["suggestions"],
            key=lambda s: (
                {"keep": 0, "revise": 0, "drop": 1}.get(
                    fin.get(s["id"], {}).get("action", "keep"), 0
                ),
                fin.get(s["id"], {}).get("rank", s["rank"]),
            ),
        )
        L = [
            f"# Suggestions: {key}",
            "",
            f"Source: `{key}.tex` in paper.sections_dir. Suggestions only; nothing here is applied to the paper.",
            f"Readers: {sum(1 for k in results if k.startswith('read'))} over {len(papers_read)} exemplar papers; "
            "then section advisors, fact checkers and one coordinator (workflows/exemplar_advisor.js).",
            "Each entry gives our sentence verbatim, the proposed text, and the exemplar quotes that show the move.",
            "",
            "## How the section reads against the exemplars",
            "",
            adv["diagnosis"],
            "",
        ]
        counts = {"keep": 0, "revise": 0, "drop": 0}
        for s in order_in:
            f = fin.get(
                s["id"],
                {
                    "action": "keep",
                    "rank": s["rank"],
                    "proposal": s["proposal"],
                    "reason": "(no coordinator ruling)",
                },
            )
            counts[f["action"]] += 1
            proposal = f["proposal"] if f["action"] == "revise" and f["proposal"] else s["proposal"]
            found = (
                in_ours(s["ours"], ours_flat, words)
                if s["kind"] in ("rewrite", "cut", "split", "merge", "move", "caption") or s["ours"]
                else True
            )
            if not found:
                stats["ours_missing"].append(s["id"])
            star = f" - top {top.index(s['id']) + 1} of the paper" if s["id"] in top else ""
            L += [
                f"## {s['id']} - {f['action'].upper()}{star}",
                "",
                f"Rank {f['rank']} in this section, priority {s['priority']}, {s['kind']}, {s['dimension']}; "
                f"skim pass: {s['skim_pass']}; {s['readers_agreeing']} reader(s) agree; "
                f"length {s['length_effect']} ({s['words_delta']:+d} words); facts kept: {'yes' if s['facts_kept'] else 'NO'}.",
                "",
                "**Ours"
                + (
                    ""
                    if found
                    else " (NOT FOUND verbatim in the paper text or sources; check before use)"
                )
                + ":** "
                + s["ours"],
                "",
            ]
            if f["action"] == "drop":
                L += ["**Advisor's proposal (dropped by the coordinator):** " + s["proposal"], ""]
            else:
                revised = " (revised by the coordinator)" if f["action"] == "revise" else ""
                L += [f"**Proposal{revised}:** " + proposal, ""]
                if f["action"] == "revise":
                    L += ["Advisor's version: " + s["proposal"], ""]
            L += ["**Why:** " + s["why"], "", "**Coordinator:** " + f["reason"], ""]
            for ex in s["exemplars"]:
                ok = in_paper(ex["paper"], ex["quote"], corpus_flat)
                if not ok:
                    stats["quote_missing"].append(f"{s['id']} ({ex['paper']})")
                L.append(
                    f"- Exemplar, {ex['paper']} ({ex['where']})"
                    + ("" if ok else " [QUOTE NOT FOUND in the paper's text]")
                    + f': "{ex["quote"]}"'
                )
            for cid in s["check_ids"]:
                c, v = checks.get(cid), verdicts.get(cid)
                if c:
                    L.append(
                        f"- Check {cid}: {c['claim']} -> **{v['verdict'] if v else 'not run'}**"
                        + (f". {v['evidence']}" if v else "")
                        + (
                            f" Corrected: {v['corrected_text']}"
                            if v and v["corrected_text"]
                            else ""
                        )
                    )
            for r in attack.get(s["id"], []):
                ev = (
                    r["evidence"]
                    if isinstance(r["evidence"], str)
                    else json.dumps(r["evidence"], ensure_ascii=False)
                )
                L.append(
                    f"- **Attack audit ({r['who']}), {r['problem']}, severity {r['severity']}:** {ev} Fix: {r['fix']}"
                )
                attacked.setdefault(key, []).append(s["id"])
            for t in truth_hits(s["ours"], truth):
                code = (
                    t["code"]
                    if isinstance(t["code"], str)
                    else "; ".join(c["location"] for c in t["code"])
                )
                L.append(
                    f"- Code-truth audit ({t['who']}) marks our sentence **{t['verdict']}**: {t['what_code_does']} Code: {code}"
                )
            L.append("")
        L += ["## Conflicts the advisor settled", ""]
        L += [f"- {c['issue']} -> {c['resolution']}" for c in adv["conflicts"]] + [""]
        L += ["## Reader suggestions the advisor dropped", ""]
        L += [f"- {d['reason']}: {d['ours']}" for d in adv["dropped"]] + [""]
        (out / "suggestions" / f"{key}.md").write_text("\n".join(L))
        vc = {}
        for cid in checks:
            if cid in verdicts:
                vc[verdicts[cid]["verdict"]] = vc.get(verdicts[cid]["verdict"], 0) + 1
        summary.append((key, len(adv["suggestions"]), counts, len(adv["dropped"]), len(checks), vc))

    # ---- report to stdout
    reads = [r for label, (_, r) in results.items() if label.startswith("read")]
    print(
        f"readers {len(reads)}; reader suggestions {sum(len(r['suggestions']) for r in reads)}; "
        f"moves {sum(len(r['moves']) for r in reads)}"
    )
    rs = [s for r in reads for s in r["suggestions"]]
    print(
        f"reader 'ours' quotes found: {sum(in_ours(s['ours'], ours_flat, words) for s in rs)}/{len(rs)}; "
        f"reader exemplar quotes found: "
        f"{sum(in_paper(s['exemplar_paper'], s['exemplar_quote'], corpus_flat) for s in rs)}/{len(rs)}"
    )
    print(
        f"coverage: {sum(g == t for _, _, g, t in cov_rows)}/{len(cov_rows)} files read in full; "
        f"short: {missing_cov}"
    )
    for row in summary:
        print(row)
    print("advisor 'ours' not found:", stats["ours_missing"])
    print("advisor exemplar quote not found:", stats["quote_missing"])
    (out / "coverage.tsv").write_text(
        "reader\tfile\tlines_read\tlines_total\n"
        + "".join(f"{a}\t{b}\t{c}\t{d}\n" for a, b, c, d in cov_rows)
    )

    # ---- README
    if not coord:
        return
    n_checks = sum(1 for k in results if k.startswith("check"))
    n_adv = sum(1 for k in results if k.startswith("advise"))
    vall = [v["verdict"] for v in verdicts.values()]
    R = [
        "# Exemplar-driven writing suggestions, all sections",
        "",
        "Suggestions only. Nothing in the paper was changed by this work; the owner chooses what goes in.",
        "Start with `suggestions/<section>.md`; each entry shows our sentence, the proposed text, the exemplar quotes, the fact checks and the audits.",
        "",
        "## What ran",
        "",
        "| Role | Count | Output |",
        "|---|---|---|",
        f"| Readers, exemplar papers plus our paper, read in full | {len(reads)} | `reads/` ({len(rs)} suggestions, {sum(len(r['moves']) for r in reads)} quoted moves) |",
        f"| Section advisors | {n_adv} | `advisors/` |",
        f"| Checkers | {n_checks} | `checks/` |",
        "| Coordinator | 1 | `coordinator.json` |",
    ]
    R += [
        f"| Code-truth audit of the paper ({p.stem}) | 1 | `codetruth/{p.name}` |"
        for p in sorted((out / "codetruth").glob("*.md"))
    ]
    R += [
        f"| Attack audit of the final list ({p.stem}) | 1 | `attack/{p.name}` |"
        for p in attack_files
    ]
    if not attack_files:
        R += ["| Attack audit of the final list | 0 | not yet run |"]
    R += [
        "",
        f"Input: `{main_txt.name}` ({main_txt.read_text().count(chr(10))} lines).",
        f"Measured read coverage, from each reader's own tool calls: {sum(g == t for _, _, g, t in cov_rows)} of {len(cov_rows)} file reads cover every line (`coverage.tsv`).",
        f"Quote checks by script: {len(stats['ours_missing'])} of {sum(r[1] for r in summary)} advisor quotes of our text are not found in the paper; exemplar quotes not found: {', '.join(stats['quote_missing']) or 'none'}.",
        "The workflow is the plugin's `workflows/exemplar_advisor.js`; the Codex prompts are its `prompts/codetruth.md` and `prompts/codex_attack.md`.",
        "",
        "## Counts by section",
        "",
        "| Section | Keep | Revise | Drop | Reader suggestions the advisor dropped | Facts checked | Supported | Partly | Entries the attack audit flags |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for key, n, counts, dropped, nchecks, vc in summary:
        flagged = len(set(attacked.get(key, []))) if attack_files else "n/a"
        R.append(
            f"| {key} | {counts['keep']} | {counts['revise']} | {counts['drop']} | {dropped} | {nchecks} | {vc.get('supported', 0)} | {vc.get('partly', 0)} | {flagged} |"
        )
    R += [
        "",
        f"Checks that came back contradicted: {vall.count('contradicted')}; not found: {vall.count('not-found')}.",
        "",
    ]
    if attack_files:
        rows = {json.dumps(r, sort_keys=True): r for rs_ in attack.values() for r in rs_}.values()
        kinds = {}
        for r in rows:
            kinds[(r["problem"], r["severity"])] = kinds.get((r["problem"], r["severity"]), 0) + 1
        live = [
            s["id"]
            for k in keys
            for s in advice[k]["suggestions"]
            if final.get(k, {}).get(s["id"], {}).get("action", "keep") != "drop"
        ]
        clean = [i for i in live if i not in attack]
        sev1 = sorted({i for i, rs_ in attack.items() for r in rs_ if r["severity"] == 1})
        R += [
            "## Attack audit of the final list",
            "",
            f"{len(rows)} findings on {len([i for i in live if i in attack])} of the {len(live)} kept or revised entries; {len(clean)} entries have no finding.",
            "The audit is strict by design: it reports every added or dropped fact and every added word, including ones the advisor had already marked.",
            "",
            "| Problem | Severity | Findings |",
            "|---|---|---|",
        ]
        R += [f"| {p} | {sv} | {n} |" for (p, sv), n in sorted(kinds.items())]
        R += [
            "",
            "Entries with a severity-1 finding (the proposal would state something the code contradicts): "
            + ", ".join(f"`{i}`" for i in sev1)
            + ".",
            "",
            "Entries with no finding: " + ", ".join(f"`{i}`" for i in clean) + ".",
            "",
        ]
    R += ["## The coordinator's top 15, in order", ""]
    for n, i in enumerate(top, 1):
        note = ""
        if attack_files:
            found = sorted(
                {f"{r['problem']} (severity {r['severity']})" for r in attack.get(i, [])}
            )
            note = " - attack: " + ", ".join(found) if found else " - no attack finding"
        R.append(f"{n}. `{i}`{note}")
    R += [
        "",
        "## Page budget (coordinator; word counts only, no build was run)",
        "",
        coord["page_budget"].replace(". ", ".\n"),
        "",
        "## The five skim passes",
        "",
    ]
    for sp in coord["skim_passes"]:
        R += [f"- **{sp['pass']}**: {sp['verdict']} Fixes: {sp['fix_ids']}"]
    R += ["", "## Consistency across sections", ""]
    for x in coord["cross_section"]:
        R += [f"- **{x['sections']}**: {x['issue']} -> {x['recommendation']}"]
    (out / "README.md").write_text("\n".join(R) + "\n")


if __name__ == "__main__":
    main()
