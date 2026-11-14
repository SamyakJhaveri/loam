"""bin/factory.d/compare.py on planted run folders and a planted attended ledger: the factory row counts
file tickets only, sums every run's cost_usd (Codex nulls as 0), counts high and critical findings from
both reviewers across rounds, and counts rounds beyond the first plus re-launched runs; the attended row
counts High, Critical and CONFIRMED rows, builders as units, and review rounds beyond the first."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "bin/factory.d/compare.py"
START = 1794442173  # 2026-11-12T00:09:33Z


def plant_run(run: pathlib.Path, costs: list[tuple[int, str, float | None]], end_ts: str,
              reviews: dict[str, list[str]], metrics_spend: float | None = None) -> None:
    run.mkdir(parents=True)
    (run / "started").write_text(f"{START}\n")
    (run / "status").write_text("pr-opened\n")
    rows = [{"ts": "2026-11-12T00:09:35Z", "event": "grader", "role": "judge"}]
    rows += [{"round": rnd, "role": role, "cost_usd": usd, "ts": "2026-11-12T01:00:00Z"} for rnd, role, usd in costs]
    rows[-1]["ts"] = end_ts
    (run / "ledger.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    for name, severities in reviews.items():
        (run / name).write_text(json.dumps({"verdict": "fix", "findings": [{"severity": s} for s in severities]}))
    if metrics_spend is not None:
        (run / "pr-body.md").write_text(f"## Metrics\n\nrounds: 2, spend: {metrics_spend} usd, wall: 1 min, denials: 0\n")


LEDGER = "\n".join([
    "id\tsource\tstatement\tstatus\tbuilder\tfault_commit\tcheck\tclosed_by",
    "V-a-01\ts\tfable-code 7: runner trusts the session id -> CONFIRMED\topen\tU8\t\t\tC10",
    "V-a-02\ts\tfable-code 5: a cut turn in a fork -> PARTLY\topen\tU8\t\t\tC10",
    "RVA-u04-1-1\ts\tHigh, U4. runner.py:4969 restores unfiltered tails\topen\tU4/U1\t\t\tC10",
    "RVA-u04-1-2\ts\tMedium, U4. runner.py:4457 the lock comes late\topen\tU4\t\t\tC10",
    "RVA-u09-1-1\ts\tMedium (Codex: High). telemetry.py:216 a cut last line\topen\tU9\t\t\tC10",
    "RVA-u13-3-1\ts\tCritical. bin/calibrate:70 a deny-list\topen\tU13\t\t\tC10",
    "R08-W6\ts\tNo unit owns: the packagers' programs, CONFIRMED by the lead\topen\tno unit\t\t\tC11",
    "ASK-01\ts\tA question for the owner\topen\towner\t\t\towner 1",
]) + "\n"


class Compare(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.root = self.tmp / "runs"
        # W10: two rounds, one high reviewer finding, one critical Codex finding, medium and low ignored.
        plant_run(self.root / "W10-alpha/aaaa1111",
                  [(1, "worker", 3.25), (1, "reviewer", 0.5), (1, "codex-review", None), (2, "worker", 1.0)],
                  "2026-11-12T02:09:33Z",
                  {"round-1.review.json": ["high", "medium", "low"], "round-1.codex-review.json": ["critical"],
                   "round-2.review.json": ["low"]},
                  metrics_spend=4.75)
        # W11a: re-launched; the abandoned first run (one round) and the second (three rounds) both count.
        plant_run(self.root / "W11a-beta/bbbb0001", [(1, "worker", 2.0)], "2026-11-12T00:39:33Z",
                  {"round-1.review.json": ["medium"]})
        plant_run(self.root / "W11a-beta/bbbb0002",
                  [(1, "worker", 1.5), (2, "worker", 0.25), (3, "worker", 0.25)], "2026-11-12T01:09:33Z",
                  {"round-3.review.json": ["high", "high"]}, metrics_spend=9.99)
        # A GitHub-issue run: not a file ticket, so skipped whatever it holds.
        plant_run(self.root / "253/cccc2222", [(1, "worker", 100.0)], "2026-11-12T09:09:33Z",
                  {"round-1.review.json": ["high"]})
        self.ledger = self.tmp / "ledger.tsv"
        self.ledger.write_text(LEDGER)

    def run_compare(self) -> tuple[dict[str, dict[str, str]], list[str]]:
        done = subprocess.run([sys.executable, str(SCRIPT), "--runs", str(self.root), "--ledger", str(self.ledger)],
                              capture_output=True, text=True, check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        lines = done.stdout.splitlines()
        header = lines[0].split("\t")
        table = {line.split("\t")[0]: dict(zip(header, line.split("\t"))) for line in lines[1:3]}
        return table, lines[3:]

    def test_factory_row(self) -> None:
        row = self.run_compare()[0]["factory"]
        self.assertEqual(row["n"], "2")
        self.assertEqual(row["serious"], "4")  # W10: high + critical; W11a: two high in round 3
        self.assertEqual(row["reruns"], "4")  # W10: 1 round more; W11a: 0 + 2 rounds more + 1 re-launch
        self.assertEqual(row["cost_usd"], "8.75")  # W10 4.75 + W11a 2.0 + 2.0
        self.assertEqual(row["wall_min"], "210.00")  # W10 120; W11a 30 + 60

    def test_attended_row(self) -> None:
        row = self.run_compare()[0]["attended"]
        self.assertEqual(row["n"], "5")  # U8, U4, U1, U9, U13
        self.assertEqual(row["serious"], "4")  # CONFIRMED, High, Critical, CONFIRMED with no builder
        self.assertEqual(row["reruns"], ">=2")  # u13 reached round 3
        self.assertEqual(row["cost_usd"], "unknown")

    def test_an_f_ticket_run_counts(self) -> None:
        # The PR 713 proof run F103-factory-gate-class was skipped as "not named for" a file ticket.
        plant_run(self.root / "F103-gate/dddd3333", [(1, "worker", 1.0)], "2026-11-12T03:09:33Z", {})
        row = self.run_compare()[0]["factory"]
        self.assertEqual((row["n"], row["cost_usd"]), ("3", "9.75"))

    def test_metrics_mismatch_warns_and_skip_is_counted(self) -> None:
        rest = self.run_compare()[1]
        warns = [line for line in rest if line.startswith("warn:")]
        self.assertEqual(len(warns), 1)
        self.assertIn("W11a-beta/bbbb0002", warns[0])
        self.assertTrue(any("1 run folders" in line and "skipped" in line for line in rest))


if __name__ == "__main__":
    unittest.main()
