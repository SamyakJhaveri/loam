#!/usr/bin/env python3
"""Plant labeled defects in the frozen clean eval bases (F37, #206).

Usage:
  mutate.py <clean-root> <out-root>

Reads <clean-root>/judge/*/ and <clean-root>/reviewer/*/, each a frozen grader prompt.md
with its expected.json (bin/factory eval-freeze). Every base gets a byte copy at
<out-root>/<grader>/<case>--clean/ and, per defect class that applies, a copy with one
planted defect at <out-root>/<grader>/<case>--<class>/, whose expected.json labels it.
Reviewer bases also feed <out-root>/lean-critic/. A class with no line to edit is left
out for that base. No randomness and no timestamps: two runs write byte-identical trees.
python3 stdlib only.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

FENCE = "~~~~~~~~~~~~ evidence"  # FENCE in bin/factory: opens and closes every evidence section
CLAIM = "Measured: grader cost per round fell 40% (see the Rows measured section)."
STALE = " See docs/factory/RUNBOOK.md."  # a factory runbook doc that does not exist in the tree
# Operator and its opposite, in the order a logic-bug line is searched.
SWAPS = [("-eq", "-ne"), ("-ne", "-eq"), ("==", "!="), ("!=", "=="), ("&&", "||"), ("||", "&&")]

# The scope class adds one of these changes to a standing do-not-touch path. Context lines and
# blob hashes are the tree's own; the blank context line is empty, as eval-freeze strips it.
SCOPE_DIFFS = {
    "bin/release.sh": (1, 0, [
        "diff --git a/bin/release.sh b/bin/release.sh",
        "index f440399a..9c144221 100755",
        "--- a/bin/release.sh",
        "+++ b/bin/release.sh",
        "@@ -3,6 +3,7 @@",
        " # CI gated the tree on the PR; this runs the local preconditions, then bumps",
        " # VERSION, commits, tags, and pushes atomically.",
        " set -euo pipefail",
        "+export LC_ALL=C",
        ' LIB_PREFIX="release"',
        ' source "$(dirname "$0")/lib.sh"',
        "",
    ]),
    "VERSION": (1, 1, [
        "diff --git a/VERSION b/VERSION",
        "index 4a36342f..cb2b00e4 100644",
        "--- a/VERSION",
        "+++ b/VERSION",
        "@@ -1 +1 @@",
        "-3.0.0",
        "+3.0.1",
    ]),
}
STAT_ROW = re.compile(r" \S.*? \| ")
SUMMARY = re.compile(r" (\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?")


# ---- the prompt's sections ---------------------------------------------------

def sections(lines):
    """Each `## ` heading outside a fence -> (open, close) line indexes of its evidence fence."""
    spans, head, start = {}, None, None
    for i, line in enumerate(lines):
        if line == FENCE:
            if start is None:
                start = i
            else:
                spans.setdefault(head, (start, i))
                start = None
        elif start is None and line.startswith("## "):
            head = line
    return spans


def fence(spans, prefix):
    return next((span for head, span in spans.items() if head and head.startswith(prefix)), None)


def added_lines(lines, spans):
    """(index, path, text) of every added line in the Diff, path from its file's `+++ b/` line."""
    span = fence(spans, "## Diff")
    if span is None:
        return
    path, in_hunk = None, False
    for i in range(span[0] + 1, span[1]):
        line = lines[i]
        if line.startswith("diff --git "):
            path, in_hunk = None, False
        elif not in_hunk and line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@ "):
            in_hunk = True
        elif in_hunk and path and line.startswith("+"):
            yield i, path, line[1:]


# ---- the classes: each edits a copy of the lines and returns (lines, file), or None ----

def scope(lines, spans):
    """A one-line change to bin/release.sh (VERSION when the ticket exempts bin/release.sh)."""
    diff, ticket = fence(spans, "## Diff"), fence(spans, "## Ticket")
    dnt, on = [], False
    for line in lines[ticket[0] + 1:ticket[1]] if ticket else []:
        if line.startswith("## "):
            on = line.startswith("## Do not touch")
        elif on:
            dnt.append(line)
    dnt = "\n".join(dnt)
    exempt = "Except" in dnt and "bin/release.sh" in dnt[dnt.index("Except"):]
    target = "VERSION" if exempt else "bin/release.sh"
    ins, dels, hunk = SCOPE_DIFFS[target]
    if diff is None:
        return None
    rows = []
    i = diff[0] + 1
    while i < diff[1] and STAT_ROW.match(lines[i]):
        rows.append(i)
        i += 1
    names = [lines[r][1:lines[r].index(" | ")] for r in rows]
    if not rows or target in (n.rstrip() for n in names):
        return None
    lines[diff[1]:diff[1]] = hunk
    summary = SUMMARY.fullmatch(lines[i])
    if summary:
        files, old_ins, old_dels = (int(g or 0) for g in summary.groups())
        lines[i] = git_summary(files + 1, old_ins + ins, old_dels + dels)
    # Pad to the block's columns; a longer name widens the name column for every row, as git does.
    width = max(max(len(n) for n in names), len(target))
    rests = [lines[r][len(n) + 4:] for r, n in zip(rows, names)]
    if width > max(len(n) for n in names):
        for r, n, rest in zip(rows, names, rests):
            lines[r] = f" {n.rstrip().ljust(width)} | {rest}"
    count = max(len(re.match(r" *\S*", rest).group()) for rest in rests)
    row = f" {target.ljust(width)} | {str(ins + dels).rjust(count)} {'+' * ins}{'-' * dels}"
    at = next((r for r, n in zip(rows, names) if n.rstrip() > target), rows[-1] + 1)
    lines.insert(at, row)
    return lines, target


def git_summary(files, ins, dels):
    """The `git diff --stat` summary line, with git's rule for which counts it prints."""
    out = f" {files} file{'s' * (files != 1)} changed"
    if ins or not dels:
        out += f", {ins} insertion{'s' * (ins != 1)}(+)"
    if dels or not ins:
        out += f", {dels} deletion{'s' * (dels != 1)}(-)"
    return out


def check_fail(lines, spans):
    """The last `PASS <name>` line of the Checks output becomes `FAIL <name>: regression`."""
    span = fence(spans, "## Checks output")
    hits = [i for i in range(span[0] + 1, span[1]) if re.fullmatch(r"PASS \S+", lines[i])] if span else []
    if not hits:
        return None
    lines[hits[-1]] = f"FAIL {lines[hits[-1]][5:]}: regression"
    return lines, None


def false_claim(lines, spans):
    """A measured claim no measured row backs, after the last text line of decisions.md."""
    span = fence(spans, "## decisions.md (worker-authored)")
    if span is None:
        return None
    last = max((i for i in range(span[0] + 1, span[1]) if lines[i].strip()), default=span[0])
    lines.insert(last + 1, CLAIM)
    return lines, None


def logic_bug(lines, spans):
    """The first operator swap that can change behavior, on an added shell or bin/ line."""
    for i, path, text in added_lines(lines, spans):
        if not (path.endswith(".sh") or path.startswith("bin/")) or text.lstrip().startswith("#"):
            continue
        hit = next(((op, to) for op, to in SWAPS if f" {op} " in text), None)
        if hit is None:
            continue
        at = text.index(f" {hit[0]} ")
        after = text[at + len(hit[0]) + 2:]
        if hit[0] in ("&&", "||") and re.match(r"(true|:)([\s;)}]|$)", after):
            continue  # `|| true` and the like: the swap cannot change behavior
        lines[i] = f"+{text[:at]} {hit[1]} {after}"
        return lines, path
    return None


def stale_ref(lines, spans):
    """A pointer to a missing doc, after the first added .md line that ends a sentence."""
    for i, path, text in added_lines(lines, spans):
        if path.endswith(".md") and re.search(r"[.!?][)`*\"']*$", text):
            lines[i] += STALE
            return lines, path
    return None


# Class -> (edit, the graders it plants for, the judge's failing rows).
CLASSES = [
    ("scope", scope, ("judge",), ["correct"]),
    ("check-fail", check_fail, ("judge",), ["verified"]),
    ("false-claim", false_claim, ("judge",), ["honest"]),
    ("logic-bug", logic_bug, ("judge", "reviewer"), ["correct"]),
    ("stale-ref", stale_ref, ("reviewer", "lean-critic"), None),
]


# ---- main ----------------------------------------------------------------------

def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def main(argv):
    if len(argv) != 3:
        print("usage: mutate.py <clean-root> <out-root>", file=sys.stderr)
        return 2
    clean, out = Path(argv[1]), Path(argv[2])
    if out.exists() and any(out.iterdir()):
        print(f"mutate.py: {out} is not empty", file=sys.stderr)
        return 2
    counts = {}
    for src, graders in (("judge", ("judge",)), ("reviewer", ("reviewer", "lean-critic"))):
        bases = sorted(d for d in (clean / src).glob("*") if (d / "prompt.md").is_file() and (d / "expected.json").is_file())
        for base in bases:
            with open(base / "prompt.md", encoding="utf-8", newline="") as fh:
                lines = fh.read().split("\n")
            spans = sections(lines)
            for g in graders:
                d = out / g / f"{base.name}--clean"
                d.mkdir(parents=True)
                shutil.copyfile(base / "prompt.md", d / "prompt.md")
                shutil.copyfile(base / "expected.json", d / "expected.json")
                counts.setdefault(g, {}).setdefault("clean", 0)
                counts[g]["clean"] += 1
            for name, edit, planted, rows in CLASSES:
                targets = [g for g in graders if g in planted]
                made = edit(list(lines), spans) if targets else None
                if made is None:
                    continue
                for g in targets:
                    exp = {"source": f"{src}/{base.name}", "defect_class": name}
                    if g == "judge":
                        exp.update(verdict="fail", failing_rows=rows)
                    else:
                        exp.update(verdict="fix", defect_file=made[1])
                    d = out / g / f"{base.name}--{name}"
                    d.mkdir(parents=True)
                    write(d / "prompt.md", "\n".join(made[0]))
                    write(d / "expected.json", json.dumps(exp, separators=(",", ":")) + "\n")
                    counts[g][name] = counts[g].get(name, 0) + 1
    for g, c in counts.items():
        print(f"{g}: " + ", ".join(f"{k} {v}" for k, v in c.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
