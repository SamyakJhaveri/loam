#!/usr/bin/env python3
"""Compare the factory with the attended helpers on serious findings, reruns, cost and wall time.

Usage:
  compare.py --runs <runs root> --ledger <ledger.tsv>

Factory arm: under <runs root> (one target's folder, such as
~/.local/state/loam-factory/runs/SamyakJhaveri__distbench) each <ticket>/<run> folder whose ticket is a
distbench file ticket (W<nn>, an optional lowercase letter, then `-` or the end); other folders are
counted and skipped. Per run, from ledger.jsonl: cost is the sum of `cost_usd` (the sum bin/factory
prints as Metrics spend; Codex calls carry null and are not in it), rounds the highest worker round,
wall the last row's `ts` less `started`. Serious findings are those of severity high or critical in
every round-N.review.json and round-N.codex-review.json. Reruns are rounds beyond the first plus run
folders beyond the first for one ticket. A pr-body.md Metrics spend that differs from the ledger sum
prints a warning line.

Attended arm: distbench docs/tickets/ledger.tsv, columns found by name. A serious finding is a row
whose statement starts with High or Critical or carries a CONFIRMED verdict. The unit is a builder
(the `builder` column split on `/`, less owner, lead, no unit and -). Reruns are a floor: review rounds
beyond the first in RVA-u<unit>-<round>-<k> ids, since a round with no finding leaves no row. Cost
and wall time are unknown (see the notes it prints).

Prints a TSV table (header, one row per arm; medians are per unit), then `run:` lines for each
factory run and `note:` lines. No verdict: the arms share no ticket and were not randomized.
"""

import argparse
import json
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

FILE_TICKET = re.compile(r"[WF]\d+[a-z]?(-|$)")  # W: batch-1 tickets; F: factory tickets (F103)
SERIOUS_SEVERITY = {"high", "critical"}
ATTENDED_SERIOUS = re.compile(r"^(High|Critical)\b|\bCONFIRMED\b")
NOT_A_UNIT = {"owner", "lead", "no unit", "-", ""}
REVIEW_ROUND = re.compile(r"RVA-u(\d+)-(\d+)-\d+")
METRICS_SPEND = re.compile(r"^rounds: \d+, spend: ([0-9.]+) usd", re.MULTILINE)


def jsonl(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def epoch(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=timezone.utc).timestamp()


def serious_in(run):
    count = 0
    for path in sorted(run.glob("round-*.review.json")) + sorted(run.glob("round-*.codex-review.json")):
        try:
            findings = json.loads(path.read_text(encoding="utf-8")).get("findings") or []
        except ValueError:
            continue
        count += sum(str(f.get("severity", "")).lower() in SERIOUS_SEVERITY for f in findings)
    return count


def factory_run(run):
    ledger = jsonl(run / "ledger.jsonl")
    cost = sum(r.get("cost_usd") or 0 for r in ledger)
    rounds = max((r["round"] for r in ledger if r.get("role") == "worker" and isinstance(r.get("round"), int)),
                 default=0)
    stamps = [epoch(r["ts"]) for r in ledger if isinstance(r.get("ts"), str)]
    started = run / "started"
    start = float(started.read_text().strip()) if started.is_file() else min(stamps, default=0)
    wall = (max(stamps) - start) / 60 if stamps else 0.0
    status = (run / "status").read_text().strip() if (run / "status").is_file() else "?"
    warn = None
    body = run / "pr-body.md"
    if body.is_file() and (m := METRICS_SPEND.search(body.read_text(encoding="utf-8"))):
        if abs(float(m.group(1)) - cost) > 0.005:
            warn = f"Metrics spend {float(m.group(1)):.2f} differs from the ledger sum {cost:.2f}"
    return {"status": status, "rounds": rounds, "serious": serious_in(run), "cost": cost, "wall": wall,
            "warn": warn}


def factory(root):
    tickets, skipped = {}, 0
    for ticket in sorted(p for p in root.iterdir() if p.is_dir()):
        runs = sorted(r for r in ticket.iterdir() if (r / "ledger.jsonl").is_file())
        if not runs:
            continue
        if not FILE_TICKET.match(ticket.name):
            skipped += len(runs)
            continue
        tickets[ticket.name] = {r.name: factory_run(r) for r in runs}
    return tickets, skipped


def attended(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    c_id, c_statement, c_builder = (header.index(n) for n in ("id", "statement", "builder"))
    serious, per_unit, rounds = 0, {}, {}
    for line in lines[1:]:
        row = line.split("\t")
        if len(row) != len(header):
            continue
        units = [u.strip() for u in row[c_builder].split("/") if u.strip() not in NOT_A_UNIT]
        hit = bool(ATTENDED_SERIOUS.search(row[c_statement]))
        serious += hit
        for unit in units:
            per_unit[unit] = per_unit.get(unit, 0) + hit
        if m := REVIEW_ROUND.fullmatch(row[c_id]):
            rounds[m.group(1)] = max(rounds.get(m.group(1), 1), int(m.group(2)))
    return {"rows": len(lines) - 1, "serious": serious, "per_unit": per_unit,
            "reruns": sum(r - 1 for r in rounds.values())}


def fmt(x):
    return f"{x:.2f}" if isinstance(x, float) else str(x)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()

    tickets, skipped = factory(args.runs)
    att = attended(args.ledger)

    per_ticket = [list(runs.values()) for runs in tickets.values()]
    t_serious = [sum(r["serious"] for r in rs) for rs in per_ticket]
    t_reruns = [sum(max(r["rounds"] - 1, 0) for r in rs) + len(rs) - 1 for rs in per_ticket]
    t_cost = [sum(r["cost"] for r in rs) for rs in per_ticket]
    t_wall = [sum(r["wall"] for r in rs) for rs in per_ticket]

    def med(xs):
        return float(statistics.median(xs)) if xs else "-"

    print("\t".join(["arm", "n", "unit", "serious", "serious_median", "reruns", "cost_usd", "cost_median",
                     "wall_min", "wall_median"]))
    print("\t".join(fmt(x) for x in ["factory", len(per_ticket), "ticket", sum(t_serious), med(t_serious),
                                     sum(t_reruns), float(sum(t_cost)), med(t_cost), float(sum(t_wall)),
                                     med(t_wall)]))
    units = att["per_unit"]
    print("\t".join(fmt(x) for x in ["attended", len(units), "builder", att["serious"],
                                     med(list(units.values())), f">={att['reruns']}", "unknown", "-",
                                     "unknown", "-"]))

    for ticket, runs in tickets.items():
        for name, r in runs.items():
            print(f"run: {ticket}/{name} {r['status']} rounds {r['rounds']} serious {r['serious']} "
                  f"cost {r['cost']:.2f} wall {r['wall']:.0f}")
            if r["warn"]:
                print(f"warn: {ticket}/{name}: {r['warn']}")
    print(f"note: factory n counts file tickets (W<nn>); {skipped} run folders under {args.runs} skipped as "
          "not named for one.")
    print("note: factory cost excludes Codex review calls, whose ledger cost_usd is null (tokens only).")
    print(f"note: attended: {att['rows']} ledger rows; serious counts each row once, serious_median is per "
          "builder; rows naming no builder (owner, lead, no unit, -) count in the total only.")
    print("note: attended reruns are a floor: review rounds beyond the first in RVA-u<unit>-<round> ids; "
          "a round with no finding leaves no row.")
    print("note: attended cost unknown: bin/usage-audit reports tokens per session, agent and model, with no "
          "ticket or builder key and no USD price, so it cannot attribute cost to a builder.")
    print("note: attended wall time unknown: ledger.tsv records no times.")
    print("note: no verdict: the arms share no ticket and were not randomized; compare per-arm rows only.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
