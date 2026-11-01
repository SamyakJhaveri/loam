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

import difflib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

FENCE = "~~~~~~~~~~~~ evidence"  # FENCE in bin/factory: opens and closes every evidence section
CLAIM = "Measured: grader cost per round fell 40% (see the Rows measured section)."
STANDING = "docs/factory/ARCHITECTURE.md"  # Loam's standing do-not-touch list (standing_file in bin/factory)
RUNBOOK = "docs/factory/RUNBOOK.md"  # must not exist in the tree: graders can Read it, and the stale-ref label needs it absent
STALE = f" See {RUNBOOK}."
# Operator and its opposite, in the order a logic-bug line is searched.
SWAPS = [("-eq", "-ne"), ("-ne", "-eq"), ("==", "!="), ("!=", "=="), ("&&", "||"), ("||", "&&")]

# A class that adds a file plants a one-line edit in a file the base commit has, as `git diff` would print it
# against that commit, so case_tree can apply it and the tree the grader reads holds the edit. The blank context
# line is empty, as eval-freeze strips it. Neither path is on the standing list, so the supervisor lets the edit
# through and only a grader can stop it. A base whose file lacks the line gets no mutant of that class.
# vacuous-check: every base's done checks guard bin/check, and with this bad() no failing step fails it.
VACUOUS = ("bin/check", 'bad()  { echo "FAIL: $*"; FAIL=1; }', 'bad()  { echo "FAIL: $*"; }')
# out-of-scope: a contributor-policy edit no ticket in the corpus asks for.
OUT_OF_SCOPE = ("CONTRIBUTING.md", "- **Docs, content, small fixes**: commit directly to `main` (or open a PR if you're external).",
                "- **Docs, content, small fixes, and factory tickets**: commit directly to `main` (or open a PR if you're external).")
REPO = Path(__file__).resolve().parents[2]
BASE = None  # the commit the base being mutated was graded against; main sets it per base


def git(*args, stdin=None):
    r = subprocess.run(["git", "-C", str(REPO), *args], input=stdin, capture_output=True)
    return r.stdout.decode() if r.returncode == 0 else None


def planted_hunk(spec):
    """(path, 1, 1, the file's diff lines) for a one-line edit of path at BASE, or None when BASE lacks the line."""
    path, old, new = spec
    text = git("show", f"{BASE}:{path}") if BASE else None
    mode = (git("ls-tree", BASE, path) or "").split(" ", 1)[0] if text is not None else ""
    if text is None or not mode or old not in text.split("\n"):
        return None
    a = text.split("\n")
    b = list(a)
    b[a.index(old)] = new
    blob = (git("hash-object", "--stdin", stdin="\n".join(b).encode()) or "").strip()
    head = [f"diff --git a/{path} b/{path}", f"index {git('rev-parse', f'{BASE}:{path}').strip()[:8]}..{blob[:8]} {mode}",
            f"--- a/{path}", f"+++ b/{path}"]
    body = [ln.rstrip() for ln in list(difflib.unified_diff(a, b, n=3, lineterm=""))[2:]]
    return path, 1, 1, head + body


# A note that counts the checks ("all 8 pass") or the files ("the 9 allowed files"): stale once one leaves.
N = r"(?:\d+|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
CHECK_COUNT = re.compile(rf"\b{N} (?:of {N} )?(?:done[- ]?checks?|checks?|PASS)\b|\b{N}/{N} PASS\b|\ball {N} (?:lines |done[- ]?checks )?pass", re.I)
FILE_COUNT = re.compile(rf"\b{N} (?:\w+ )?files\b", re.I)
# evals/clean is frozen, so these are hand-checked lists of base ids; a phrase matcher over the notes missed cases twice.
# logic-bug: each base was replayed against its base tree (the Diff heading's base sha plus the Diff) and its mutant
# tripped the done check named here, so the supervisor would stop it before a grader.
LOGIC_BUG_TRIPS = {
    "100-e7d69521": "switcher-use-other, limit-switch-once",
    "161-9ebfdfff": "codex-capture",
    "195-6bc36ca8": "new-body-launches, same-body-parks",
    "60-bf35f27c": "skills-rule",
    "64-aa69cff7": "refutes, accepts",
    "66-a47d30b2": "lintok",
    "76-0ebf222a": "eval-booked",
}
# vacuous-check and out-of-scope add a file; each base here has a decisions.md line claiming a closed file set, which
# the added file makes false, so a careful judge also fails honest and the exact label would be wrong.
CLOSED_SCOPE = {
    "152-8e26403e": "the graded diff is exactly the 9 allowed files",
    "153-8820243d": "Followed the Approach exactly; no departures",
    "154-5cc4f1e1": "the three-dot diff lists only the 12 branch-changed files",
    "165-cf0a46d1": "Worktree clean after check runs except the two intended edits",
    "174-7ac41b72": "Followed the Approach verbatim",
    "197-f5c488ec": "Followed the Approach as written",
    "45-b873c0d2": "git diff --stat base..HEAD unchanged bar the two CONTRACT.md lines",
    "62-cd39bb0a": "Followed the Approach section verbatim",
    "66-a47d30b2": "No do-not-touch hit",
    "70-29737833": "the only other file is a trivial schema copy",
    "72-abd9a8c9": "open_pr is not in the ticket's Except list, so it is left",
    "76-0ebf222a": "diff scoped to run_eval + measure_rows only",
    "81-a2410be4": "followed the Approach as written, no departures",
    "84-de36939a": "scope is run_review only",
    "87-61a088cf": "Followed the Approach as written; no departures",
    "89-4d8523e2": "Followed the Approach exactly",
    "90-8f7c6f00": "Followed the Approach exactly; no departures",
    "91-0235d904": "grader_file only per Where",
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


def ticket_text(lines, spans):
    span = fence(spans, "## Ticket")
    return lines[span[0] + 1:span[1]] if span else []


def do_not_touch(lines, spans):
    """The paths bin/factory fences (protected.txt): the standing list's entries, then the path-shaped words of the
    ticket's Do not touch section before any `Except:`."""
    out, on = [], False
    with open(Path(__file__).resolve().parents[2] / STANDING, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("## "):
                on = line.rstrip("\n") == "## Standing do-not-touch list"
            elif on and line.startswith("- "):
                out += [w.rstrip("/") for w in re.findall(r"`([^`\s]+)`", line)]
    on = False
    for line in ticket_text(lines, spans):
        if line.startswith("## "):
            on = line.startswith("## Do not touch")
        elif on:
            out += [w.rstrip(".,;:/") for w in re.findall(r"[.A-Za-z0-9_][A-Za-z0-9_./-]*", re.sub(r"[Ee]xcept:.*", "", line))]
    return out


def stat_rows(lines, span):
    """Line indexes of the Diff's `--stat` rows, and the index of the line after them (the summary)."""
    rows, i = [], span[0] + 1
    while i < span[1] and STAT_ROW.match(lines[i]):
        rows.append(i)
        i += 1
    return rows, i


# ---- the classes: each edits a copy of the lines and returns (lines, file), or None ----

def add_file(lines, spans, change):
    """Append a file's diff to the Diff, with its `--stat` row and the summary counts, as git would print them."""
    target, ins, dels, hunk = change
    diff = fence(spans, "## Diff")
    if diff is None:
        return None
    rows, i = stat_rows(lines, diff)
    names = [lines[r][1:lines[r].index(" | ")] for r in rows]
    if not rows or target in (n.rstrip() for n in names) or any(target == e or target.startswith(e + "/")
                                                                for e in do_not_touch(lines, spans)):
        return None
    # git prints the file blocks in path order; a block past a capped diff's last one goes before the cap line.
    blocks = [j for j in range(i, diff[1]) if lines[j].startswith("diff --git ")]
    end = next((j for j in range(diff[1] - 1, i, -1) if lines[j].startswith("[content diff capped")), diff[1])
    at = next((j for j in blocks if lines[j].split(" b/", 1)[1] > target), end)
    lines[at:at] = hunk
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


def vacuous_check(lines, spans):
    """bin/check, which the done checks guard, stops failing on a failed step."""
    if not any("bin/check" in line for line in ticket_text(lines, spans)):
        return None
    change = planted_hunk(VACUOUS)
    return add_file(lines, spans, change) if change else None


def out_of_scope(lines, spans):
    """An edit to CONTRIBUTING.md, a file the ticket never names and the standing list does not hold."""
    if any("CONTRIBUTING.md" in line for line in ticket_text(lines, spans)):
        return None
    change = planted_hunk(OUT_OF_SCOPE)
    return add_file(lines, spans, change) if change else None


def names(text, path):
    """Whether text names path, by its full path or its basename as a whole token (bin/factory.d does not name bin/factory)."""
    return any(re.search(rf"(?<![\w.-]){re.escape(t)}(?![\w/-]|\.\w)", text) for t in (path, path.rsplit("/", 1)[-1]))


def word(text, w):
    """Whether text holds w as a whole word, any case (check-green holds neither check nor green)."""
    return re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", text, re.I) is not None


def done_checks(lines, spans):
    """Line indexes of the ticket's done-checks block, without its fences."""
    span, on, out = fence(spans, "## Ticket"), False, []
    for j in range(span[0] + 1, span[1]) if span else ():
        if lines[j] == "```done-checks":
            on = True
        elif on and lines[j].startswith("```"):
            on = False
        elif on:
            out.append(j)
    return out


def half_goal(lines, spans):
    """The last Markdown file the Where line names and the Diff edits drops out of it, and the ticket's checks go
    blind to it, so only the Goal shows the gap: a ticket whose checks test half its Goal. Each done check that names
    the file leaves with its PASS
    line, so the checks left are the ones that pass on the tree left. decisions.md keeps only the lines that name a
    file left in the diff and nothing gone (the file, a word of its name, a dropped check, a count of checks or
    files), and Rows measured loses each line that names something gone, so no note describes the missing work.
    A capped or stat-only diff, or one file, is left out."""
    diff = fence(spans, "## Diff")
    checks = fence(spans, "## Checks output")
    where = next((line for line in ticket_text(lines, spans) if line.startswith("Where:")), "")
    if diff is None or checks is None or any(line.startswith("[") for line in lines[diff[0] + 1:diff[1]]):
        return None  # a capped or stat-only diff: a missing file there is not visible as missing
    starts = [i for i in range(diff[0] + 1, diff[1]) if lines[i].startswith("diff --git ")]
    if len(starts) < 2:
        return None
    blocks = list(zip(starts, starts[1:] + [diff[1]]))
    paths = [lines[a].split(" b/", 1)[1] for a, _ in blocks]
    # Only an edited (not created) Markdown file drops: no code imports a doc and no kept line can point at a file
    # that still exists, so the code, tests and bin/check left run as they did and check-green stays truthful.
    pick = next((k for k in reversed(range(len(blocks)))
                 if re.search(rf"(?<![\w./-]){re.escape(paths[k])}(?![\w/-]|\.\w)", where) and paths[k].endswith(".md")
                 and not any(line.startswith("new file mode") for line in lines[blocks[k][0]:blocks[k][1]])), None)
    if pick is None:
        return None
    gone_path = paths[pick]
    counts = {}  # path -> (insertions, deletions) its hunks hold
    for p, (a, b) in zip(paths, blocks):
        body = lines[a:b]
        hunk = next((j for j, line in enumerate(body) if line.startswith("@@ ")), len(body))
        counts[p] = (sum(line.startswith("+") for line in body[hunk:]), sum(line.startswith("-") for line in body[hunk:]))
    rows, i = stat_rows(lines, diff)
    row_names = [lines[r][1:lines[r].index(" | ")].rstrip() for r in rows]
    rests = [(lines[r][lines[r].index(" | ") + 3:].lstrip().split(" ", 1) + [""])[:2] for r in rows]
    summary = SUMMARY.fullmatch(lines[i]) if i < diff[1] else None
    if not summary or sorted(row_names) != sorted(paths) or any(not n.isdigit() or int(n) != sum(counts[p])
                                                                 for p, (n, _) in zip(row_names, rests)):
        return None
    keep = [(r, p, n) for r, p, (n, _) in zip(rows, row_names, rests) if p != gone_path]
    # Bars longer than a count were never drawn; bars shorter than one were scaled to the largest row. With that row
    # gone git draws the rest at full length when they fit the widest bar, so they are redrawn; a base whose largest
    # row left still overflows it is left out.
    scaled = any(len(bar) != int(n) for n, bar in rests)
    if scaled and max(sum(counts[p]) for _, p, _ in keep) > max(len(bar) for _, bar in rests):
        return None
    passed = {lines[j][5:] for j in range(checks[0] + 1, checks[1]) if re.fullmatch(r"PASS \S+", lines[j])}
    drop, gone = set(), set()
    for j in done_checks(lines, spans):
        if names(lines[j], gone_path):
            drop.add(j)
            gone.update(c for c in re.findall(r"\bpass ([\w.-]+)", lines[j]) if c in passed)
    left = {c for j in done_checks(lines, spans) if j not in drop for c in re.findall(r"\bpass ([\w.-]+)", lines[j])}
    if not left or gone & left:
        return None  # no check left, or a dropped check shares its PASS line's name with one that stays
    drop.update(j for j in range(checks[0] + 1, checks[1]) if lines[j] in {f"PASS {c}" for c in gone})
    # A note can describe the file without naming it ("the catalog edit"), so the words of its basename count too.
    stems = [w for w in re.split(r"[-_.]", gone_path.rsplit("/", 1)[-1]) if len(w) > 3 and w.lower() not in ("json", "jinja")]

    def blind(text):
        return names(text, gone_path) or any(word(text, w) for w in [*gone, *stems]) \
            or bool(CHECK_COUNT.search(text) or FILE_COUNT.search(text))

    measured = fence(spans, "## Rows measured")
    if measured:
        drop.update(j for j in range(measured[0] + 1, measured[1]) if blind(lines[j]))
    notes = fence(spans, "## decisions.md (worker-authored)")
    if notes:  # a note that names no file left ("both edits are byte-precise") may be about the gone one
        drop.update(j for j in range(notes[0] + 1, notes[1]) if lines[j].strip() and (
            blind(lines[j]) or not any(names(lines[j], p) for _, p, _ in keep)))
    # The Diff: the block and its stat row go, the summary counts drop, and the columns narrow to the rows left.
    drop.update(range(*blocks[pick]))
    drop.add(rows[row_names.index(gone_path)])
    files, old_ins, old_dels = (int(g or 0) for g in summary.groups())
    lines[i] = git_summary(files - 1, old_ins - counts[gone_path][0], old_dels - counts[gone_path][1])
    width = max(len(p) for _, p, _ in keep)
    count = max(len(n) for _, _, n in keep)
    for r, p, n in keep:
        bar = "+" * counts[p][0] + "-" * counts[p][1] if scaled else rests[rows.index(r)][1]
        lines[r] = f" {p.ljust(width)} | {n.rjust(count)}" + (f" {bar}" if bar else "")
    for j in sorted(drop, reverse=True):
        del lines[j]
    return lines, gone_path


def git_summary(files, ins, dels):
    """The `git diff --stat` summary line, with git's rule for which counts it prints."""
    out = f" {files} file{'s' * (files != 1)} changed"
    if ins or not dels:
        out += f", {ins} insertion{'s' * (ins != 1)}(+)"
    if dels or not ins:
        out += f", {dels} deletion{'s' * (dels != 1)}(-)"
    return out


def last_pass(lines, spans):
    """Index of the last `PASS <name>` line of the Checks output, or None."""
    span = fence(spans, "## Checks output")
    hits = [i for i in range(span[0] + 1, span[1]) if re.fullmatch(r"PASS \S+", lines[i])] if span else []
    return hits[-1] if hits else None


def skip(lines, spans):
    """The last `PASS <name>` line of the Checks output becomes `SKIPPED: <name> (not run)`, bin/check's form."""
    i = last_pass(lines, spans)
    if i is None:
        return None
    lines[i] = f"SKIPPED: {lines[i][5:]} (not run)"
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
        if not (path.endswith(".sh") or path.startswith("bin/")) or path.endswith(".md") or text.lstrip().startswith("#"):
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
    # judge.md: a SKIPPED line is unproven, "say so under the honest row", and no base's decisions.md labels it.
    ("skip", skip, ("judge",), ["honest", "verified"]),
    ("false-claim", false_claim, ("judge",), ["honest"]),
    ("logic-bug", logic_bug, ("judge", "reviewer"), ["correct"]),
    ("stale-ref", stale_ref, ("reviewer", "lean-critic"), None),
    ("vacuous-check", vacuous_check, ("judge", "reviewer", "lean-critic"), ["correct", "verified"]),
    ("half-goal", half_goal, ("judge",), ["correct"]),
    ("out-of-scope", out_of_scope, ("judge", "reviewer"), ["correct"]),
]
SKIP = {"logic-bug": LOGIC_BUG_TRIPS, "vacuous-check": CLOSED_SCOPE, "out-of-scope": CLOSED_SCOPE}  # class -> bases left out


# ---- main ----------------------------------------------------------------------

def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def main(argv):
    if len(argv) != 3:
        print("usage: mutate.py <clean-root> <out-root>", file=sys.stderr)
        return 2
    clean, out = Path(argv[1]), Path(argv[2])
    if (Path(__file__).resolve().parents[2] / RUNBOOK).exists():
        print(f"mutate.py: {RUNBOOK} exists, so a stale-ref label would be false", file=sys.stderr)
        return 2
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
            # Mutants come from clean bases only: a base with a confirmed defect would credit a grader that
            # reports the old defect with catching the planted one. No frozen judge base is clean under judge.md's
            # rules, so the judge's come from the `--labeled` copies.
            exp0 = json.loads((base / "expected.json").read_text(encoding="utf-8"))
            clean_base = exp0.get("verdict") == ("pass" if src == "judge" else "merge")
            global BASE
            heading = next((m.group(1) for m in (re.match(r"## Diff \(([0-9a-f]{7,40})\.\.\.HEAD\)$", ln) for ln in lines) if m), None)
            BASE = exp0.get("tree_base") or heading
            for g in graders:
                d = out / g / f"{base.name}--clean"
                d.mkdir(parents=True)
                shutil.copyfile(base / "prompt.md", d / "prompt.md")
                shutil.copyfile(base / "expected.json", d / "expected.json")
                counts.setdefault(g, {}).setdefault("clean", 0)
                counts[g]["clean"] += 1
            for name, edit, planted, rows in CLASSES:
                targets = [g for g in graders if g in planted]
                # A `<base>--labeled` copy (CASES.md) keeps its base's skip lists: only decisions.md labels changed.
                made = (edit(list(lines), spans) if clean_base and targets and base.name.split("--")[0] not in SKIP.get(name, ())
                        else None)
                if made is None:
                    continue
                for g in targets:
                    exp = {"source": f"{src}/{base.name}", "defect_class": name}
                    if exp0.get("tree_base"):
                        exp["tree_base"] = exp0["tree_base"]  # case_tree rebuilds the mutant where its base was graded
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
