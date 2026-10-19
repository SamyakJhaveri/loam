#!/usr/bin/env python3
"""`bin/factory status --criteria`: the trust criteria of docs/factory/ARCHITECTURE.md (Metrics), measured.

Usage:
  criteria.py <runs-root> <ARCHITECTURE.md> <agents-dir> <target>

Reads one target's run directories, <runs-root>/<issue>/<sha8>/ with a `status` file (LOOP.md), and
calls nothing: no model, no gh, no git. Another target's runs sit one level deeper, under
<runs-root>/<owner>__<repo>/, so they never count here. The criteria and their thresholds are read
from ARCHITECTURE.md, their one home; a line this file cannot measure prints `UNMEASURED: <why>`.
The graders section compares each run's ledger grader events with <agents-dir>/<role>.md.
python3 stdlib only.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import statistics
import sys

MARKER = "Criteria written in advance"
GRADER_ROLES = ("judge", "reviewer", "codex-review")


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def ledger(run):
    out = []
    for line in read(os.path.join(run, "ledger.jsonl")).splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict):
            out.append(entry)
    return out


def round_files(run, suffix):
    """{N: path} for each round-N.<suffix> in the run directory."""
    out = {}
    for path in glob.glob(os.path.join(run, "round-*." + suffix)):
        m = re.fullmatch(r"round-(\d+)\." + re.escape(suffix), os.path.basename(path))
        if m:
            out[int(m.group(1))] = path
    return out


def judge_rows(path):
    """(verdict, rows) of one judge reply; an absent, empty, or invalid file has no verdict, a fail (LOOP.md)."""
    try:
        reply = json.loads(read(path))
    except ValueError:
        reply = None
    if not isinstance(reply, dict):
        return None, {}
    rows = reply.get("rows")
    return reply.get("verdict"), rows if isinstance(rows, dict) else {}


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


def usd(entries):
    return sum(e["cost_usd"] for e in entries if isinstance(e.get("cost_usd"), (int, float)))


def grader_version(path):
    """The plugin-cache version directory a grader file came from, or `checkout` for the fallback copy."""
    return os.path.basename(os.path.dirname(os.path.dirname(path))) if "/plugins/cache/" in path else "checkout"


class Run:
    def __init__(self, root, run):
        self.label = os.path.relpath(run, root)
        self.status = read(os.path.join(run, "status")).strip()
        entries = ledger(run)
        self.spend = usd(entries)
        self.grader_spend = usd([e for e in entries if e.get("role") in GRADER_ROLES])
        checks = round_files(run, "checks")
        self.rounds = len([n for n in checks if n > 0])
        self.checks = [read(p) for p in checks.values()]
        self.judges = [judge_rows(p) for _, p in sorted(round_files(run, "judge.json").items())]
        self.sendbacks = len([v for v, _ in self.judges if v != "pass"])
        self.exits = exits(read(os.path.join(run, "factory.log")))
        # The last event per role: freeze writes one pair per frozen set, so a later pair graded later rounds.
        self.graders = {e.get("role"): e for e in entries if e.get("event") == "grader"}

    def first_failing_row(self):
        """grader_first_fail's judge part: the first non-pass row of the last graded round."""
        rows = self.judges[-1][1] if self.judges else {}
        return next((k for k, v in rows.items() if v != "pass"), None)


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


def scope_stalls(runs):
    seen = sorted({k for r in runs for _, rows in r.judges for k in rows})
    if "scope" not in seen:
        return None, (f"no judge.json has a scope row (rows seen: {', '.join(seen) or 'none'}); a scope defect "
                      "now fails the do-not-touch check or draws a reviewer finding, and neither names a row")
    hit = [r.label for r in runs if r.first_failing_row() == "scope"]
    return len(hit), ", ".join(hit)


def environment_rounds(runs):
    lost = [f"{r.label} round {n}" for r in runs for kind, n in r.exits if kind == "stopped-environment" and n is not None]
    return len(lost), ", ".join(lost)


def skip_lines(runs):
    per = [len([ln for ln in text.splitlines() if ln.startswith("SKIP")]) for r in runs for text in r.checks]
    if not per:
        return None, "no round-N.checks file"
    return max(per), f"the most in one round-N.checks; {sum(per)} in all {len(per)}"


MEASURES = {
    "operator actions from voice note to a running loop on Track B": unmeasured(
        "a run directory starts at launch, after the brief and the ticket, and records no operator action"),
    "operator actions after the PR opens": unmeasured(
        "a run directory ends at pr-opened; what the operator does on the PR happens on GitHub"),
    "stalls whose first failing grader row is scope": scope_stalls,
    "rounds lost to environment failures": environment_rounds,
    "SKIP lines per round": skip_lines,
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


def stop_line(runs, kind):
    """Exits of one kind; a run whose final status is another kind was relaunched past the stop."""
    n = sum(1 for r in runs for k, _ in r.exits if k == kind)
    ended = [r for r in runs if r.status == kind]
    past = [r.label for r in runs if r.status != kind and any(k == kind for k, _ in r.exits)]
    line = f"{count(n, 'exit')}; {count(len(ended), 'run')} stopped for good ({sum(r.spend for r in ended):.2f} usd)"
    return line + (f"; relaunched past it: {', '.join(past)}" if past else "")


def main(argv):
    if len(argv) != 5:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    root, arch, agents, target = argv[1:]
    crit = criteria(arch)
    if crit is None:
        print(f"criteria: no '{MARKER}' list in {arch}", file=sys.stderr)
        return 2
    runs = sorted((Run(root, os.path.dirname(p)) for p in glob.glob(os.path.join(glob.escape(root), "*", "*", "status"))),
                  key=lambda r: (r.label.split("/")[0].zfill(12), r.label))
    prs = [r for r in runs if r.status == "pr-opened"]
    out = [f"== trust criteria for {target}: {count(len(runs), 'run')} under {root} (read-only, no model call)"]

    med = median_rounds(runs)[0]
    table = [
        ("runs", len(runs)),
        ("PR opened", len(prs)),
        ("spend", f"{sum(r.spend for r in runs):.2f} usd"),
        ("spend on runs with no PR", f"{sum(r.spend for r in runs if r.status != 'pr-opened'):.2f} usd"),
        ("median rounds to PR", "-" if med is None else num(med)),
        ("grader spend", f"{sum(r.grader_spend for r in runs):.2f} usd"),
        ("PR runs the judge sent back", f"{len([r for r in prs if r.sendbacks])} of {len(prs)}"),
    ]
    out += [f"{k:<31} {v}" for k, v in table]

    out.append("\n== stops")
    out.append(f"{'round-0 stops (ticket-defect)':<31} {stop_line(runs, 'ticket-defect')}")
    out.append(f"{'worker abandons':<31} {stop_line(runs, 'abandon')}")
    out.append(f"{'judge send-backs':<31} {count(sum(r.sendbacks for r in runs), 'round')} with a non-pass judge "
               f"verdict, in {count(len([r for r in runs if r.sendbacks]), 'run')}")

    out.append(f"\n== criteria ({os.path.basename(arch)}, Metrics)")
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

    out.append("\n== graders (each run's ledger grader events; = or != the factory checkout's agents/<role>.md)")
    current = {}
    for role in ("judge", "reviewer"):
        try:
            with open(os.path.join(agents, role + ".md"), "rb") as fh:
                current[role] = hashlib.sha256(fh.read()).hexdigest()
        except OSError:
            current[role] = None
    groups = {}
    for r in runs:
        events = [r.graders.get(role) for role in ("judge", "reviewer")]
        if not any(events):
            key = ("none", ())
        else:
            versions = sorted({grader_version(e.get("file", "")) for e in events if e})
            key = ("+".join(versions), tuple(
                (role, (e or {}).get("sha256", "")[:8] or "-",
                 "=" if e and current[role] and e.get("sha256") == current[role] else "!=")
                for role, e in zip(("judge", "reviewer"), events)))
        groups[key] = groups.get(key, 0) + 1

    def order(key):
        version = key[0]
        return ({"checkout": 1, "none": 2}.get(version, 0), [int(x) for x in re.findall(r"\d+", version)], key)

    for key in sorted(groups, key=order):
        version, shas = key
        detail = "  ".join(f"{role} {sha} {mark:<2}" for role, sha, mark in shas) or "(no grader event in the ledger)"
        n = groups[key]
        out.append(f"{version:<9} {n:>3} run{'s' if n != 1 else ' '}  {detail}")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
