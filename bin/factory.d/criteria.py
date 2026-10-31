#!/usr/bin/env python3
"""`bin/factory status --criteria`: the trust criteria of docs/factory/ARCHITECTURE.md (Metrics), measured.

Usage:
  criteria.py <runs-root> <ARCHITECTURE.md> <target>

Reads one target's run directories, <runs-root>/<issue>/<sha8>/ with a `status` file (LOOP.md), and
calls no model and no gh. Another target's runs sit one level deeper, under <runs-root>/<owner>__<repo>/, so
they never count here. Its git calls are a `git log` of the target's default branch (origin/HEAD, else
origin/main, else main; as of the last fetch) for the escaped defects line: merged factory PRs that a later
commit reverts or names in a `Caused-by: #<pr>` line. Only merge-commit PRs count; a squash or rebase merge
leaves no `Merge pull request` commit, so it is in neither number. The criteria and their thresholds are read
from ARCHITECTURE.md, their one home; a line this file cannot measure prints `UNMEASURED: <why>`, and a
lower bound within its threshold prints `INCONCLUSIVE`, since what it omits could pass the threshold.
python3 stdlib only.
"""
from __future__ import annotations

import glob
import json
import os
import re
import statistics
import subprocess
import sys

MARKER = "Criteria written in advance"
REHEARSAL = "file ticket: no GitHub call"  # open_pr's pr-opened message for a file ticket, which opens no PR
PASS_OVER = "SKIPPED:"  # bin/check's marker for a step that did not run; lib.sh's guard copies it into the checks file
STALLS = ("stuck", "no-change", "stopped-cap")
LOWER = "lower bound"  # a measure's fourth element: the value may undercount, so it prints INCONCLUSIVE, not PASS
# The worker's claim, the last line of its last message that reads `CLAIM: <state>` (_common.md); only done claims done.
CLAIM_LINE = re.compile(r"^[\s*`>_]*CLAIM:\s*([A-Za-z]+)", re.M)
# FAIL names only the supervisor writes (round_checks), so the worker's Stop hook never prints them; under LOAM_HOOK,
# guard passes a `guard bin/check` line without running it (lib.sh), so its name joins them per run.
HOOK_BLIND = {"do-not-touch", "worktree-dirty"}
GUARDED_CHECK = re.compile(r"(?:^|[;&|{(])\s*guard bin/check(?=[\s;&|)}]|$)")  # a command, not a quoted word
# A round with no CLAIM line, from before _common.md asked for one, falls back to this text matcher. A completion
# claim: done (not done-checks), complete or finished (not after the or a), all [n] checks pass or print, no FAIL, or
# check: PASSED. A failure: fail, failure, could not, cannot, incomplete or unfinished. A pass (passes,
# passed) alone is no signal. A negation flips only the next claim, failure or pass in its clause: a denied claim or
# pass is a failure, and a denied failure is no signal. A requirement (requires, must, should) makes the next signal in
# its clause no signal, and if, unless or once every later signal of its sentence, since they state what should or
# would hold, not what does. The last signal of a sentence decides it; a question claims nothing.
CLAIM = re.compile(r"\b(?:(?<!\bthe )(?<!\ba )(?:done(?![- ]checks?\b)|completed?|finished)\b"
                   r"|all (?:\w+ ){0,2}(?:done[- ])?checks? (?:now )?(?:pass|print)|no fail\b|check: passed)", re.I)
FAILS = re.compile(r"\bfail(?:s|ed|ing|ures?)?\b|\bcould(?: not|n't)|\bcannot\b|\bcan't\b|\b(?:in|un)(?:complete|finished)\b",
                   re.I)
PASSES = re.compile(r"\bpass(?:es|ed|ing)?\b", re.I)
NEGATED = re.compile(r"\b(?:not|never|no|nowhere|nothing|none)\b|n't", re.I)
REQUIRED = re.compile(r"\b(?:requires?|required|must|needs?|should|would)\b", re.I)
HYPOTHETICAL = re.compile(r"\b(?:if|unless|once)\b", re.I)
CLAUSE = re.compile(r"[;,]|\b(?:but|because|and|so|while|although|since|which)\b", re.I)
# A factory PR's merge commit, its PR number, and what a later commit says to name it as the cause of a defect.
FACTORY_PR = re.compile(r"Merge pull request #(\d+) from [^/\s]+/factory/\S")
REVERTS = re.compile(r"\bThis reverts commit ([0-9a-f]{7,40})\b")
CAUSED_BY = re.compile(r"^Caused-by: #(\d+)\b", re.M | re.I)
SIGNAL = {("claim", False): True, ("claim", True): False, ("fail", False): False, ("pass", True): False}


def read(path, missing=""):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return missing


def round_files(run, suffix):
    """{N: path} for each round-N.<suffix> in the run directory."""
    out = {}
    for path in glob.glob(os.path.join(run, "round-*." + suffix)):
        m = re.fullmatch(r"round-(\d+)\." + re.escape(suffix), os.path.basename(path))
        if m:
            out[int(m.group(1))] = path
    return out


def loads(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


def exits(log):
    """[(kind, round, message)] per EXIT line of factory.log; round is the last `===== round N =====` since the
    previous EXIT or `===== launch =====`, or None when the launch stopped before a round began (a parallel-cap
    exit). The launch line keeps a relaunch's early exit off the round a killed launch left with no EXIT."""
    out, rnd = [], None
    for line in log.splitlines():
        if re.fullmatch(r"\S+ ===== launch =====", line):
            rnd = None
            continue
        m = re.fullmatch(r"\S+ ===== round (\d+) =====", line)
        if m:
            rnd = int(m.group(1))
            continue
        m = re.match(r"\S+ EXIT (\S+) \(\d+\):? ?(.*)", line)
        if m:
            out.append((m.group(1), rnd, m.group(2)))
            rnd = None
    return out


class Run:
    def __init__(self, root, run):
        self.dir = run
        self.label = os.path.relpath(run, root)
        self.status = read(os.path.join(run, "status")).strip()
        self.checks = {n: read(p).splitlines() for n, p in round_files(run, "checks").items()}
        self.rounds = len([n for n in self.checks if n > 0])
        log = read(os.path.join(run, "factory.log"), None)
        self.exits = None if log is None else exits(log)  # None: the exits are unknown, not absent
        self.date = next((ln[:10] for ln in reversed((log or "").splitlines()) if re.match(r"\d{4}-\d\d-\d\dT", ln)), None)
        events = read(os.path.join(run, "owner-events.jsonl"), None)  # None: the run predates owner-events.jsonl
        self.events = None if events is None else [e for e in map(loads, events.splitlines()) if isinstance(e, dict)]
        self.pr_closed = os.path.exists(os.path.join(run, "pr-closed"))


def count(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def num(x):
    return str(int(x)) if float(x).is_integer() else str(x)


# ---- the criteria: name -> runs -> (value, detail), or (None, why) when the run record cannot measure it

def no_log(runs):
    missing = [r.label for r in runs if r.exits is None]
    return f"no factory.log in {', '.join(missing)}" if missing else None


def median_rounds(runs):
    done = [r for r in runs if r.status == "pr-opened"]
    if why := no_log(done):
        return None, why
    prs = [r.rounds for r in done
           if not any(kind == "pr-opened" and msg.startswith(REHEARSAL) for kind, _, msg in r.exits)]
    if not prs:
        return None, "no run opened a PR"
    return statistics.median(prs), f"over {count(len(prs), 'PR run')}"


def environment_rounds(runs):
    if why := no_log(runs):
        return None, why
    lost = [f"{r.label} round {n}" for r in runs for kind, n, _ in r.exits if kind == "stopped-environment" and n is not None]
    return len(lost), ", ".join(lost)


def operator_actions(phase, since, omits):
    """The most owner-events.jsonl lines of one phase in one run: a lower bound, since only some owner work is seen."""
    def measure(runs):
        seen = [r for r in runs if r.events is not None and (phase == "launch" or r.pr_closed
                                                             or any(e.get("phase") == phase for e in r.events))]
        if not seen:
            return None, f"no run directory records {since} in owner-events.jsonl"
        n, label = max((sum(e.get("phase") == phase for e in r.events), r.label) for r in seen)
        return n, f"most in one run, {label}, of {count(len(seen), 'run')}; omits {omits}", f"at least {n}", LOWER
    return measure


def fail_names(lines):
    """The check name of each FAIL line, in order: lib.sh's `FAIL name: why`, or round_checks' `FAIL do-not-touch paths`."""
    return [line[5:].split(" ", 1)[0].rstrip(":") for line in lines if line.startswith("FAIL ")]


def first_fail(lines):
    return next(iter(fail_names(lines)), None)


def scope_stalls(runs):
    if why := no_log(runs):
        return None, why
    # A stall is a run, and a scope stall when any of its stall exits is: a relaunch that stalls again, for scope or
    # another reason, is the same run. An exit reads its last checked round, since no-change and a ticket-budget or
    # wall-clock cap exit after the round's `===== round N =====` line and before round-N.checks.
    stalls = [(r, [max((k for k in r.checks if k <= n), default=None) for kind, n, _ in r.exits
                   if kind in STALLS and n is not None]) for r in runs if any(kind in STALLS for kind, _, _ in r.exits)]
    scope = [f"{r.label} round {n}" for r, ns in stalls
             if (n := next((k for k in ns if first_fail(r.checks.get(k, [])) == "do-not-touch"), None)) is not None]
    return len(scope), f"of {count(len(stalls), 'stall')}" + (f": {', '.join(scope)}" if scope else "")


def pass_over_lines(runs):
    """Rounds of runs whose frozen lib.sh copies the marker past /dev/null, or whose checks show one: an older guard
    dropped them, so its rounds would read 0 for markers it never wrote."""
    runs = [r for r in runs if ">&9" in read(os.path.join(r.dir, "frozen", "lib.sh"))
            or any(line.startswith(PASS_OVER) for lines in r.checks.values() for line in lines)]
    rounds = [(sum(line.startswith(PASS_OVER) for line in lines), r.label, n)
              for r in runs for n, lines in r.checks.items() if n > 0]
    if not rounds:
        return None, "no run with a worker round froze a lib.sh that copies pass-over markers"
    most, label, n = max(rounds)
    return most, f"{label} round {n}" if most else f"over {count(len(rounds), 'round')}"


def judge_notes(runs):
    """Failing judge rows citing worker-written notes, over the failing rows that carry evidence_kind (ticket 13)."""
    rows, notes, kinds = 0, [], False
    for r in runs:
        for n, path in sorted(round_files(r.dir, "judge.json").items()):
            j = loads(read(path))
            if not isinstance(j, dict) or not isinstance(j.get("evidence_kind"), dict):
                continue
            kinds = True
            ev = j["evidence_kind"]
            for row, v in (j.get("rows") or {}).items():
                if v == "fail" and row in ev:
                    rows += 1
                    if ev[row] == "notes":
                        notes.append(f"{r.label} round {n} {row}")
    if not kinds:
        return None, "no round-N.judge.json carries evidence_kind (ticket 13)"
    return len(notes), ", ".join(notes), f"{len(notes)} of {rows}"


def last_message(run, n):
    """(kind, text) of round n's last worker message: round-n.last.txt for Codex, .result of round-n.result.json for
    Claude (one object, or an array whose last result element is it); text is None when the round left none."""
    last = os.path.join(run, f"round-{n}.last.txt")
    if os.path.exists(last):
        return "codex", read(last)
    j = loads(read(os.path.join(run, f"round-{n}.result.json")))
    if isinstance(j, list):
        j = next((x for x in reversed(j) if isinstance(x, dict) and x.get("type") == "result"), j[-1] if j else None)
    text = j.get("result") if isinstance(j, dict) else None
    return "claude", text if isinstance(text, str) else None


def signals(clause):
    """The clause's signals in order, True for a claim and False for a failure. A match inside an earlier kind's match
    (the no of no FAIL, the not of could not) is not a match of its own."""
    spans = []
    for kind, rx in (("claim", CLAIM), ("fail", FAILS), ("pass", PASSES), ("not", NEGATED), ("required", REQUIRED)):
        spans += [(m.start(), m.end(), kind) for m in rx.finditer(clause)
                  if all(m.end() <= a or m.start() >= b for a, b, _ in spans)]
    negated = required = False
    for _, _, kind in sorted(spans):
        if kind == "not":
            negated = True
        elif kind == "required":
            required = True
        else:
            if not required and (kind, negated) in SIGNAL:
                yield SIGNAL[kind, negated]
            negated = required = False


def claims_done(text):
    """The first sentence whose last signal is a claim of the work done or its checks passing, or None."""
    for sentence in re.split(r"(?<=[.!?])\s+|\n", text):
        found = [v for clause in CLAUSE.split(HYPOTHETICAL.split(sentence, 1)[0]) for v in signals(clause)]
        if found and found[-1] and not sentence.rstrip().endswith("?"):
            return sentence.strip()
    return None


def claim(text):
    """(counts, said) of a last worker message: its last CLAIM line, which counts when its state is done, or with none,
    counts None and claims_done's sentence, None when the text matcher reads no claim."""
    lines = list(CLAIM_LINE.finditer(text))
    if lines:
        return lines[-1].group(1).lower() == "done", lines[-1].group(0).strip(" *`>_")
    return None, claims_done(text)


def guarded(run):
    """The names on the `guard bin/check` lines of the run's frozen checks, which the Stop hook passes unrun."""
    return {name for line in read(os.path.join(run, "frozen", "checks.sh")).splitlines() if GUARDED_CHECK.search(line)
            for name in re.findall(r"\b(?:pass|fail) ([\w.-]+)", line)}


def premature_done(runs):
    """Failing rounds whose worker claims done in its last message's CLAIM line, or for a round with none, the text
    matcher's claims_done. A counted round is hook-blind when every FAIL it printed is a check its Stop hook passes.
    While a failing round is read by the matcher, which can miss a claim, a count within the threshold is no PASS."""
    kinds, silent, matched, failing, rows, blind = {"claude": 0, "codex": 0}, 0, 0, 0, [], []
    for r in runs:
        for n, lines in sorted(r.checks.items()):
            names = fail_names(lines)
            if n == 0 or not names:
                continue
            failing += 1
            kind, text = last_message(r.dir, n)
            if text is None:
                silent += 1
                continue
            counts, said = claim(text)
            if counts is None:
                matched += 1
            if counts or counts is None and said:
                kinds[kind] += 1
                # The round, its first FAIL line and the claim, so a reader can settle a text matcher's read.
                rows.append(f"{r.label} round {n} ({kind}): {next(ln for ln in lines if ln.startswith('FAIL '))} | {said}")
                if set(names) <= HOOK_BLIND | guarded(r.dir):
                    blind.append(f"{r.label} round {n}")
    detail = f"claude {kinds['claude']}, codex {kinds['codex']}"
    if silent:
        detail += f"; {count(silent, 'failing round')} with no worker message"
    if matched:
        detail += f"; {matched} with no CLAIM line, read by the text matcher"
    if blind:
        detail += f"; {len(blind)} failed only checks the worker's Stop hook cannot fail: {', '.join(blind)}"
    n = sum(kinds.values())
    return n, detail, f"{n} of {count(failing, 'failing round')}", LOWER if matched else None, rows


def history(target):
    """{sha: (parents, message)} of every commit on the target's default branch, origin/HEAD, origin/main or main,
    or the reason git could not read it."""
    for rev in ("origin/HEAD", "origin/main", "main"):
        proc = subprocess.run(["git", "-C", target, "log", "--format=%H %P%x1f%B%x1e", rev, "--"],
                              capture_output=True, text=True, errors="replace", check=False)
        if proc.returncode == 0:
            break
    else:
        return None, f"git log of {target} failed: {(proc.stderr.strip().splitlines() or [proc.returncode])[-1]}"
    commits = {}
    for record in proc.stdout.split("\x1e"):
        head, _, message = record.strip("\n").partition("\x1f")
        if head:
            sha, *parents = head.split()
            commits[sha] = (parents, message)
    return commits, None


def escaped_defects(target):
    """The escaped defects line: merged factory PRs that a later commit reverts (the merge or one of its commits) or
    names in a Caused-by line. A commit of the PR's own branch is not later, so a worker's revert of its own commit
    inside the PR does not count."""
    commits, why = history(target)
    if commits is None:
        return f"escaped defects: UNMEASURED: {why}"
    children = {}
    for sha, (parents, _) in commits.items():
        for p in parents:
            children.setdefault(p, []).append(sha)

    def descendants(sha):  # sha and every commit that has it as an ancestor
        seen, todo = {sha}, [sha]
        while todo:
            for c in children.get(todo.pop(), []):
                if c not in seen:
                    seen.add(c)
                    todo.append(c)
        return seen

    prs = {sha: m.group(1) for sha, (parents, message) in commits.items()
           if len(parents) > 1 and (m := FACTORY_PR.match(message))}
    escaped = {}
    for sha, (_, message) in commits.items():
        later = descendants(sha) if REVERTS.search(message) or CAUSED_BY.search(message) else None
        hits = {m for m, pr in prs.items() if pr in CAUSED_BY.findall(message)}
        for prefix in REVERTS.findall(message):
            for target_sha in (c for c in commits if c.startswith(prefix)):
                # A merge introduces a commit when its second parent descends from it and its first does not.
                below = descendants(target_sha)
                hits |= {m for m in prs if m == target_sha or (commits[m][0][1] in below and commits[m][0][0] not in below)}
        for m in hits:
            if m not in later:
                escaped.setdefault(m, sha)
    listed = ", ".join(f"#{prs[m]} ({escaped[m][:8]})" for m in sorted(escaped, key=lambda m: int(prs[m])))
    return f"escaped defects: {len(escaped)} of {count(len(prs), 'merged factory PR')}" + (f": {listed}" if listed else "")


# A measure returns (value, detail), (value, detail, shown), where shown replaces the value in the verdict line, or
# (value, detail, shown, LOWER) for a lower bound: it can show a threshold is exceeded, never that it is met, and a
# fifth element, rows, prints a line per counted case under the verdict.
MEASURES = {
    "operator actions from voice note to a running loop on Track B": operator_actions(
        "launch", "a launch", "owner work outside the issue's events and the lint, run and stop subcommands run outside Claude Code"),
    "operator actions after the PR opens": operator_actions("pr", "a closed PR", "owner work outside the PR's events"),
    "stalls whose first failing grader row is scope": scope_stalls,
    "rounds lost to environment failures": environment_rounds,
    "lines per round marking a passed-over step": pass_over_lines,
    "median rounds to PR": median_rounds,
    "judge fails citing a worker-written measurement": judge_notes,
    "rounds whose last worker message claims done while the checks printed FAIL": premature_done,
}


def criteria(arch):
    """[(line, name, rule)] of the list that follows the MARKER line, up to its first non-item line."""
    lines = read(arch).splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith(MARKER)), None)
    if start is None:
        return None
    out = []
    for line in lines[start + 1:]:
        if not line.startswith("- "):
            if out or line.strip():
                break
            continue
        name, _, rule = line[2:].partition(": ")
        out.append((line[2:], name, rule))
    return out


def main(argv):
    if len(argv) != 4:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    root, arch, target = argv[1:]
    crit = criteria(arch)
    if crit is None:
        print(f"criteria: no '{MARKER}' list in {arch}", file=sys.stderr)
        return 2
    runs = sorted((Run(root, os.path.dirname(p)) for p in glob.glob(os.path.join(glob.escape(root), "*", "*", "status"))),
                  key=lambda r: (r.label.split("/")[0].zfill(12), r.label))
    out = [f"== trust criteria for {target}: {count(len(runs), 'run')} under {root} "
           f"({os.path.basename(arch)}, Metrics; read-only, no model call)"]
    for line, name, rule in crit:
        out.append(f"- {line}")
        m = re.match(r"(?:at most )?(\d+)\b", rule)
        if name not in MEASURES:
            out.append("    UNMEASURED: criteria.py has no measure for this line")
            continue
        value, detail, *shown = MEASURES[name](runs) if runs else (None, f"no run directory under {root}")
        lower, rows = shown[1:2] == [LOWER], shown[2] if len(shown) > 2 else []
        # A FAIL names the date of its latest run in the detail or its rows, from that run's factory.log.
        named = " ".join([str(detail), *rows])
        dates = [r.date for r in runs if r.date and re.search(rf"(?<![\w/]){re.escape(r.label)}\b", named)]
        if value is None:
            out.append(f"    UNMEASURED: {detail}")
        elif not m:
            out.append(f"    UNMEASURED: the threshold '{rule}' does not start with a number")
        else:
            verdict = "FAIL" if value > int(m.group(1)) else "INCONCLUSIVE" if lower else "PASS"
            out.append(f"    {verdict}: measured {shown[0] if shown else num(value)}" + (f" ({detail})" if detail else "")
                       + (f"; latest {max(dates)}" if verdict == "FAIL" and dates else ""))
            out += [f"      {row}" for row in rows]
    out.append(escaped_defects(target))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
