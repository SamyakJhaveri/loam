#!/usr/bin/env python3
"""NAV-01 metrics (docs/research/memory-design-v2-2026-09-21.md).

Reads one or more factory run directories and prints the eight protocol metrics
per run, from files the factory already writes. python3 stdlib only; names no
model of its own - it reads model and arm from the ledger.

Usage:
  nav01-metrics.py [RUN_DIR ...] [--runs-root DIR --issues a,b,c] [--json]

A run directory is <runs-root>/<issue>/<sha>/, holding a `status` file, a
`ledger.jsonl`, and per-round `round-N.jsonl` / `round-N.checks` /
`round-N.diff` / `round-N.*.json`. The arm of a run is the `nav_arm` of its
first worker ledger line, or `base` when that field is absent (older runs).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# The JSON output keys, in column order; the done-check reads them by name.
COLUMNS = ["rounds", "turns_r1", "tokens_r1", "cost_usd", "first_file_turn", "grader", "honesty", "setup", "arm"]
NA = "n/a"
FILE_TOOLS = {"Read", "Edit", "Write", "NotebookEdit"}
DEFAULT_RUNS_ROOT = os.path.expanduser("~/.local/state/loam-factory/runs")


# ---- readers ----------------------------------------------------------------

def read_jsonl(path):
    """The parsed dict objects of a JSONL file; unparseable lines skipped, [] when absent."""
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    out.append(obj)
    except OSError:
        pass
    return out


def read_json(path):
    """Parse one JSON object from a file; None when absent or unparseable."""
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            obj = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    return obj if isinstance(obj, dict) else None


def read_status(run):
    try:
        with open(os.path.join(run, "status"), encoding="utf-8", errors="replace") as fh:
            return fh.read().strip()
    except OSError:
        return ""


def round_numbers(run, suffix):
    """The N>=1 of every round-N<suffix> file under run, ascending (round-0 excluded)."""
    ns = []
    try:
        names = os.listdir(run)
    except OSError:
        return ns
    for name in names:
        if name.startswith("round-") and name.endswith(suffix):
            middle = name[len("round-"):-len(suffix)]
            if middle.isdigit() and int(middle) >= 1:
                ns.append(int(middle))
    return sorted(ns)


def tool_uses(events):
    """Yield (name, input_dict) for every tool_use block across the events."""
    for event in events:
        msg = event.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                inp = block.get("input")
                yield block.get("name"), inp if isinstance(inp, dict) else {}


def worker_line(lines, round_n):
    for obj in lines:
        if obj.get("role") == "worker" and obj.get("round") == round_n:
            return obj
    return None


def arm_of(lines):
    for obj in lines:
        if obj.get("role") == "worker":
            nav = obj.get("nav_arm")
            return nav if isinstance(nav, str) and nav else "base"
    return "base"


# ---- the eight metrics ------------------------------------------------------

def metric_rounds(run, lines):
    if read_status(run) != "pr-opened":
        return NA
    ns = round_numbers(run, ".checks")
    if ns:
        return max(ns)
    rounds = [o.get("round") for o in lines if o.get("role") == "worker" and isinstance(o.get("round"), int)]
    return max(rounds) if rounds else NA


def metric_turns_r1(events):
    return sum(1 for e in events if e.get("type") == "assistant")


def _usage_tokens(usage):
    if not isinstance(usage, dict):
        return None
    try:
        return int(usage.get("input_tokens", 0) or 0) + int(usage.get("output_tokens", 0) or 0)
    except (TypeError, ValueError):
        return None


def metric_tokens_r1(lines, events):
    worker = worker_line(lines, 1)
    tokens = _usage_tokens(worker.get("usage")) if worker else None
    if tokens is None:
        for e in events:
            if e.get("type") == "result":
                tokens = _usage_tokens(e.get("usage"))
                break
    return tokens if tokens is not None else NA


def metric_cost(lines):
    total = 0.0
    seen = False
    for obj in lines:
        if obj.get("role") != "worker":
            continue
        seen = True
        cost = obj.get("cost_usd")
        if isinstance(cost, (int, float)):
            total += cost
    return total if seen else NA


def diff_paths(run):
    """Repo-relative paths of the highest-numbered round-N.diff's `diff --git a/.. b/..` lines."""
    ns = round_numbers(run, ".diff")
    if not ns:
        return []
    seen, out = set(), []
    try:
        with open(os.path.join(run, f"round-{max(ns)}.diff"), encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if not line.startswith("diff --git "):
                    continue
                for tok in line.split()[2:]:
                    path = tok[2:] if tok.startswith(("a/", "b/")) else tok
                    if path and path not in seen:
                        seen.add(path)
                        out.append(path)
    except OSError:
        return []
    return out


def bash_path_tokens(command):
    """Path-like tokens of a shell command: whitespace-split, quotes stripped, keep tokens
    with a '/' or a filename extension; '.' and '..' dropped."""
    tokens = []
    for raw in command.split():
        tok = raw.strip("'\"`(),;:")
        if not tok or tok in (".", ".."):
            continue
        if "/" in tok:
            tokens.append(tok)
            continue
        root, ext = os.path.splitext(tok)
        if root and len(ext) > 1:
            tokens.append(tok)
    return tokens


def path_matches(candidate, dps):
    """Equality, a trailing-path suffix, or an equal non-empty basename (worker paths are
    absolute under the worktree; diff paths are repo-relative)."""
    if not candidate:
        return False
    cbase = os.path.basename(candidate.rstrip("/"))
    for dp in dps:
        if candidate == dp or candidate.endswith("/" + dp) or dp.endswith("/" + candidate):
            return True
        if cbase and cbase == os.path.basename(dp.rstrip("/")):
            return True
    return False


def metric_first_file_turn(events, dps):
    if not dps:
        return NA
    idx = 0
    for event in events:
        if event.get("type") != "assistant":
            continue
        idx += 1
        candidates = []
        msg = event.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None
        for block in content if isinstance(content, list) else []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            inp = block.get("input")
            inp = inp if isinstance(inp, dict) else {}
            if block.get("name") in FILE_TOOLS:
                for key in ("file_path", "notebook_path"):
                    value = inp.get(key)
                    if isinstance(value, str) and value:
                        candidates.append(value)
            elif block.get("name") == "Bash":
                cmd = inp.get("command")
                if isinstance(cmd, str):
                    candidates.extend(bash_path_tokens(cmd))
        if any(path_matches(c, dps) for c in candidates):
            return idx
    return NA


def metric_grader(run):
    ns = round_numbers(run, ".judge.json")
    if not ns:
        return NA
    n = max(ns)
    judge = read_json(os.path.join(run, f"round-{n}.judge.json"))
    if judge is None:
        return NA
    rows = judge.get("rows")
    if isinstance(rows, dict) and rows:
        score = f"{sum(1 for v in rows.values() if v == 'pass')}/{len(rows)}"
    else:
        score = "0/0"
    if judge.get("verdict") != "pass":
        first = "judge"
    elif _has_finding(run, n, "review", ("high", "medium")):
        first = "reviewer"
    elif _has_finding(run, n, "codex-review", ("critical", "high")):
        first = "codex-review"
    else:
        first = "none"
    return f"{first} {score}"


def _has_finding(run, n, stem, severities):
    doc = read_json(os.path.join(run, f"round-{n}.{stem}.json"))
    if not doc:
        return False
    return any(isinstance(f, dict) and f.get("severity") in severities for f in doc.get("findings") or [])


def metric_honesty(arm, events):
    if arm == "C":
        return sum(1 for name, inp in tool_uses(events)
                   if name == "Bash" and isinstance(inp.get("command"), str) and "semble search" in inp["command"])
    if arm == "B":
        return sum(1 for name, _ in tool_uses(events) if isinstance(name, str) and name.lower() == "lsp")
    return "-"


def metric_setup(lines):
    worker = worker_line(lines, 1)
    ms = worker.get("duration_ms") if worker else None
    return int(ms) // 1000 if isinstance(ms, (int, float)) else NA


# ---- assembly and output ----------------------------------------------------

def metrics_for(run):
    lines = read_jsonl(os.path.join(run, "ledger.jsonl"))
    events = read_jsonl(os.path.join(run, "round-1.jsonl"))
    arm = arm_of(lines)
    dps = diff_paths(run)
    return {
        "rounds": metric_rounds(run, lines),
        "turns_r1": metric_turns_r1(events),
        "tokens_r1": metric_tokens_r1(lines, events),
        "cost_usd": metric_cost(lines),
        "first_file_turn": metric_first_file_turn(events, dps),
        "grader": metric_grader(run),
        "honesty": metric_honesty(arm, events),
        "setup": metric_setup(lines),
        "arm": arm,
    }


def run_label(run):
    run = os.path.normpath(run)
    parent = os.path.basename(os.path.dirname(run))
    base = os.path.basename(run)
    return f"{parent}/{base}" if parent else base


def cell(value):
    return f"{round(value, 4)}" if isinstance(value, float) else str(value)


def markdown(rows):
    header = ["run"] + COLUMNS
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    for label, row in rows:
        out.append("| " + " | ".join([label] + [cell(row[c]) for c in COLUMNS]) + " |")
    return "\n".join(out)


def collect_runs(args):
    runs = list(args.run_dirs)
    if args.issues:
        for issue in args.issues.split(","):
            issue = issue.strip()
            if not issue:
                continue
            issue_dir = os.path.join(args.runs_root, issue)
            try:
                names = sorted(os.listdir(issue_dir))
            except OSError:
                print(f"warning: no issue directory {issue_dir}", file=sys.stderr)
                continue
            for name in names:
                run = os.path.join(issue_dir, name)
                if os.path.isfile(os.path.join(run, "status")):
                    runs.append(run)
    return runs


def main():
    ap = argparse.ArgumentParser(description="NAV-01 metrics for factory run directories.")
    ap.add_argument("run_dirs", nargs="*", metavar="RUN_DIR", help="a run directory <runs-root>/<issue>/<sha>")
    ap.add_argument("--runs-root", default=DEFAULT_RUNS_ROOT, help="runs root that --issues expands under")
    ap.add_argument("--issues", help="comma list of issue dirs under --runs-root to expand into run directories")
    ap.add_argument("--json", action="store_true", help="print a JSON array instead of a markdown table")
    args = ap.parse_args()

    runs = collect_runs(args)
    if not runs:
        print("no run directories: pass RUN_DIR, or --issues with --runs-root", file=sys.stderr)
        return 2

    rows = [(run_label(run), metrics_for(run)) for run in runs]
    if args.json:
        print(json.dumps([row for _, row in rows]))
    else:
        print(markdown(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
