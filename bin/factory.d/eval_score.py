#!/usr/bin/env python3
"""Score saved grader replies on a mutated eval set (F37, #206).

Usage:
  eval_score.py <cases-root> <replies-root>

<cases-root> is mutate.py's output, <grader>/<case>/expected.json. <replies-root> holds
<model>/r<k>/<grader>-<case>.json, the EVAL_OUT layout of `bin/factory eval`: each the
`claude -p --output-format json` output of one case. Reply paths are built from the cases
tree, never parsed from file names. A missing or unparseable reply is a miss on a mutant,
a false alarm on a clean copy, and a disagreement.

Prints TSV rows grader, model, metric, value, sorted: recall:<class>, false_alarm (cut_rate
for the lean-critic, whose job is cuts), agreement, usd, and n:<metric> for each rate's
trial count. Each pair of models A and B scored on the same repeats also gets model A+B
(recall and false alarm only): caught when either catches on the same r<k>, a false alarm
when either fails the clean copy. python3 stdlib only.
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path


def load_reply(path):
    """(reply object or None, cost in USD) of one saved reply; None when missing or unparseable."""
    try:
        with open(path, encoding="utf-8") as fh:
            out = json.load(fh)
    except (OSError, ValueError):
        return None, 0.0
    if isinstance(out, list):  # RESULT_OBJ in bin/factory
        results = [e for e in out if isinstance(e, dict) and e.get("type") == "result"]
        out = results[-1] if results else (out[-1] if out else {})
    if not isinstance(out, dict):
        return None, 0.0
    cost = out.get("total_cost_usd") or 0
    text = out.get("result")
    if not isinstance(text, str):
        return None, cost
    # A reply wrapped in prose or code fences: the object runs from the first brace to the last.
    for cand in (text, text[text.find("{"):text.rfind("}") + 1]):
        try:
            reply = json.loads(cand)
        except ValueError:
            continue
        if isinstance(reply, dict) and "verdict" in reply:
            return reply, cost
    return None, cost


def failing_rows(reply):
    rows = reply.get("rows")
    return frozenset(k for k, v in rows.items() if v == "fail") if isinstance(rows, dict) else frozenset()


def metric(grader, exp):
    if "defect_class" in exp:
        return f"recall:{exp['defect_class']}"
    return "cut_rate" if grader == "lean-critic" else "false_alarm"


def hit(grader, exp, reply):
    """A mutant caught, or on a clean copy a false alarm (a cut, for the lean-critic)."""
    if "defect_class" not in exp:
        return reply is None or reply.get("verdict") == ("fail" if grader == "judge" else "fix")
    if reply is None:
        return False
    if grader == "judge":
        return reply.get("verdict") == "fail" and set(exp.get("failing_rows", [])) <= failing_rows(reply)
    f = exp["defect_file"]
    files = [x.get("file") for x in reply.get("findings") or [] if isinstance(x, dict)]
    return reply.get("verdict") == "fix" and any(isinstance(p, str) and (p == f or p.endswith("/" + f)) for p in files)


def rate(hits, trials):
    return str((Decimal(hits) / Decimal(trials)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def tally(grader, cases, repeats, caught):
    """metric -> [hits, trials] over every case times every repeat."""
    out = {}
    for case, exp in cases:
        t = out.setdefault(metric(grader, exp), [0, 0])
        for r in repeats:
            t[0] += caught(case, exp, r)
            t[1] += 1
    return out


def main(argv):
    if len(argv) != 3:
        print("usage: eval_score.py <cases-root> <replies-root>", file=sys.stderr)
        return 2
    cases_root, replies_root = Path(argv[1]), Path(argv[2])
    models = sorted(d.name for d in replies_root.iterdir() if d.is_dir())
    rows = []
    for gdir in sorted(d for d in cases_root.iterdir() if d.is_dir()):
        grader = gdir.name
        cases = [(d.name, json.loads((d / "expected.json").read_text(encoding="utf-8")))
                 for d in sorted(gdir.iterdir()) if (d / "expected.json").is_file()]
        # model -> r<k> -> case -> (reply, cost), for the repeats that hold a reply for this grader.
        got = {}
        for m in models:
            reps = sorted((d for d in (replies_root / m).iterdir() if d.is_dir() and re.fullmatch(r"r\d+", d.name)),
                          key=lambda d: int(d.name[1:]))
            for rdir in reps:
                paths = {case: rdir / f"{grader}-{case}.json" for case, _ in cases}
                if any(p.is_file() for p in paths.values()):
                    got.setdefault(m, {})[rdir.name] = {case: load_reply(p) for case, p in paths.items()}
        for m, by_rep in got.items():
            for name, (hits, trials) in tally(grader, cases, by_rep,
                                              lambda c, e, r: hit(grader, e, by_rep[r][c][0])).items():
                rows += [(grader, m, name, rate(hits, trials)), (grader, m, f"n:{name}", str(trials))]
            agree = 0
            for case, _ in cases:
                sigs = [(rep[case][0]["verdict"], failing_rows(rep[case][0]) if grader == "judge" else None)
                        if rep[case][0] is not None else None for rep in by_rep.values()]
                agree += None not in sigs and len(set(sigs)) == 1
            rows += [(grader, m, "agreement", rate(agree, len(cases))), (grader, m, "n:agreement", str(len(cases)))]
            usd = sum(cost for rep in by_rep.values() for _, cost in rep.values())
            rows.append((grader, m, "usd", f"{usd:.2f}"))
        for a, b in itertools.combinations(sorted(got), 2):
            common = sorted(set(got[a]) & set(got[b]))
            if not common:
                continue
            def either(c, e, r, a=a, b=b):
                return hit(grader, e, got[a][r][c][0]) or hit(grader, e, got[b][r][c][0])
            for name, (hits, trials) in tally(grader, cases, common, either).items():
                rows.append((grader, f"{a}+{b}", name, rate(hits, trials)))
    for row in sorted(rows):
        print("\t".join(row))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
