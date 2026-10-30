#!/usr/bin/env python3
"""`bin/factory status --criteria`: the trust criteria of docs/factory/ARCHITECTURE.md (Metrics), measured.

Usage:
  criteria.py <runs-root> <ARCHITECTURE.md> <target>

Reads one target's run directories, <runs-root>/<issue>/<sha8>/ with a `status` file (LOOP.md), and
calls nothing: no model, no gh, no git. Another target's runs sit one level deeper, under
<runs-root>/<owner>__<repo>/, so they never count here. The criteria and their thresholds are read
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
import sys

MARKER = "Criteria written in advance"
REHEARSAL = "file ticket: no GitHub call"  # open_pr's pr-opened message for a file ticket, which opens no PR
PASS_OVER = "SKIPPED:"  # bin/check's marker for a step that did not run; lib.sh's guard copies it into the checks file
STALLS = ("stuck", "no-change", "stopped-cap")
LOWER = "lower bound"  # a measure's fourth element: the value may undercount, so it prints INCONCLUSIVE, not PASS
# A completion claim: done (not done-checks), complete or finished (not after the or a), all [n] checks pass or print,
# no FAIL, or check: PASSED. NEGATED, before a claim or a FAILS match in its clause, denies it; the last signal of a
# sentence decides it, so a failure after a claim cancels it and a claim after a past failure stands.
CLAIM = re.compile(r"\b(?:(?<!\bthe )(?<!\ba )(?:done(?![- ]checks?\b)|completed?|finished)\b"
                   r"|all (?:\w+ ){0,2}(?:done[- ])?checks? (?:now )?(?:pass|print)|no fail\b|check: passed)", re.I)
NEGATED = re.compile(r"\b(?:not|never|no|nowhere|nothing|none|cannot)\b|n't", re.I)
FAILS = re.compile(r"\bfail(?:s|ed|ing)?\b|\bcould not\b|\bcannot\b|\bcan't\b", re.I)


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


def first_fail(lines):
    """The check name of the first FAIL line: lib.sh's `FAIL name: why`, or round_checks' `FAIL do-not-touch paths`."""
    for line in lines:
        if line.startswith("FAIL "):
            return line[5:].split(" ", 1)[0].rstrip(":")
    return None


def scope_stalls(runs):
    if why := no_log(runs):
        return None, why
    stalls = [(r, n) for r in runs for kind, n, _ in r.exits if kind in STALLS]
    # The stall's last checked round: no-change and a ticket-budget or wall-clock cap exit after the round's
    # `===== round N =====` line and before round-N.checks, so they read the round before.
    last = [(r, max((k for k in r.checks if n is not None and k <= n), default=None)) for r, n in stalls]
    scope = [f"{r.label} round {n}" for r, n in last if first_fail(r.checks.get(n, [])) == "do-not-touch"]
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


def claims_done(text):
    """True when some sentence's last signal is a claim of the work done or its checks passing that its clause does not
    deny, rather than a failure it does not deny."""
    for sentence in re.split(r"(?<=[.!?])\s+|\n", text):
        last = False
        for clause in re.split(r"[;,]|\bbut\b", sentence):
            signals = [(m.start(), not NEGATED.search(clause[:m.start()])) for m in CLAIM.finditer(clause)]
            signals += [(m.start(), False) for m in FAILS.finditer(clause) if not NEGATED.search(clause[:m.start()])]
            if signals:
                last = max(signals)[1]
        if last:
            return True
    return False


def premature_done(runs):
    kinds, silent = {"claude": 0, "codex": 0}, 0
    for r in runs:
        for n, lines in r.checks.items():
            if n == 0 or not any(line.startswith("FAIL") for line in lines):
                continue
            kind, text = last_message(r.dir, n)
            if text is None:
                silent += 1
            elif claims_done(text):
                kinds[kind] += 1
    detail = f"claude {kinds['claude']}, codex {kinds['codex']}"
    if silent:
        detail += f"; {count(silent, 'failing round')} with no worker message"
    return sum(kinds.values()), detail


# A measure returns (value, detail), (value, detail, shown), where shown replaces the value in the verdict line, or
# (value, detail, shown, LOWER) for a lower bound: it can show a threshold is exceeded, never that it is met.
MEASURES = {
    "operator actions from voice note to a running loop on Track B": operator_actions(
        "launch", "a launch", "owner work outside the issue's events and the lint, run and stop subcommands"),
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
        lower = shown[1:] == [LOWER]
        if value is None:
            out.append(f"    UNMEASURED: {detail}")
        elif not m:
            out.append(f"    UNMEASURED: the threshold '{rule}' does not start with a number")
        else:
            verdict = "FAIL" if value > int(m.group(1)) else "INCONCLUSIVE" if lower else "PASS"
            out.append(f"    {verdict}: measured {shown[0] if shown else num(value)}" + (f" ({detail})" if detail else ""))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
