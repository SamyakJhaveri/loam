#!/usr/bin/env python3
"""`bin/factory status --criteria`: the trust criteria of docs/factory/ARCHITECTURE.md (Metrics), measured.

Usage:
  criteria.py <runs-root> <ARCHITECTURE.md> <target>

Reads one target's run directories, <runs-root>/<issue>/<sha8>/ with a `status` file (LOOP.md), and
calls nothing: no model, no gh, no git. Another target's runs sit one level deeper, under
<runs-root>/<owner>__<repo>/, so they never count here. The criteria and their thresholds are read
from ARCHITECTURE.md, their one home; a line this file cannot measure prints `UNMEASURED: <why>`.
python3 stdlib only.
"""
from __future__ import annotations

import glob
import os
import re
import statistics
import sys

MARKER = "Criteria written in advance"


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def round_files(run, suffix):
    """{N: path} for each round-N.<suffix> in the run directory."""
    out = {}
    for path in glob.glob(os.path.join(run, "round-*." + suffix)):
        m = re.fullmatch(r"round-(\d+)\." + re.escape(suffix), os.path.basename(path))
        if m:
            out[int(m.group(1))] = path
    return out


def exits(log):
    """[(kind, round)] per EXIT line of factory.log; round is the last `===== round N =====` since the
    previous EXIT, or None when the launch stopped before a round began (a parallel-cap exit)."""
    out, rnd = [], None
    for line in log.splitlines():
        m = re.fullmatch(r"\S+ ===== round (\d+) =====", line)
        if m:
            rnd = int(m.group(1))
            continue
        m = re.match(r"\S+ EXIT (\S+) \(\d+\)", line)
        if m:
            out.append((m.group(1), rnd))
            rnd = None
    return out


class Run:
    def __init__(self, root, run):
        self.label = os.path.relpath(run, root)
        self.status = read(os.path.join(run, "status")).strip()
        self.rounds = len([n for n in round_files(run, "checks") if n > 0])
        self.exits = exits(read(os.path.join(run, "factory.log")))


def count(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def num(x):
    return str(int(x)) if float(x).is_integer() else str(x)


# ---- the criteria: name -> runs -> (value, detail), or (None, why) when the run record cannot measure it

def unmeasured(why):
    return lambda runs: (None, why)


def median_rounds(runs):
    prs = [r.rounds for r in runs if r.status == "pr-opened"]
    if not prs:
        return None, "no run reached pr-opened"
    return statistics.median(prs), f"over {count(len(prs), 'PR run')}"


def environment_rounds(runs):
    lost = [f"{r.label} round {n}" for r in runs for kind, n in r.exits if kind == "stopped-environment" and n is not None]
    return len(lost), ", ".join(lost)


MEASURES = {
    "operator actions from voice note to a running loop on Track B": unmeasured(
        "a run directory starts at launch, after the brief and the ticket, and records no operator action"),
    "operator actions after the PR opens": unmeasured(
        "a run directory ends at pr-opened; what the operator does on the PR happens on GitHub"),
    "stalls whose first failing grader row is scope": unmeasured(
        "the judge has no scope row; a scope defect fails the do-not-touch check or draws a reviewer finding"),
    "rounds lost to environment failures": environment_rounds,
    "SKIP lines per round": unmeasured(
        "no check can print one: lib.sh has no skip helper, ticket lint refuses the word, and the guard line sends "
        "bin/check's SKIPPED: lines to /dev/null"),
    "median rounds to PR": median_rounds,
    "judge fails citing a worker-written measurement": unmeasured(
        "a judge.json fix is free text; no field says whether a fail cites a worker-written measurement"),
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
        value, detail = MEASURES[name](runs) if runs else (None, f"no run directory under {root}")
        if value is None:
            out.append(f"    UNMEASURED: {detail}")
        elif not m:
            out.append(f"    UNMEASURED: the threshold '{rule}' does not start with a number")
        else:
            verdict = "PASS" if value <= int(m.group(1)) else "FAIL"
            out.append(f"    {verdict}: measured {num(value)}" + (f" ({detail})" if detail else ""))
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
