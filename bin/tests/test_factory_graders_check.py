"""graders-check reads the mismatch count of the scores line it picks for each grader file (#607).

A fresh line with some cases mismatched prints one INFO line naming the count; one that matched none of its cases
warns STALE, since eval counts a case it could not build as a mismatch; a clean line, or one with no mismatch field,
prints only `graders-check: OK`. Only DRIFT sets the exit code. Each test writes a scratch --evals-dir keyed to the
checkout's agent files' sha256, so evals/scores.jsonl is never read or written. No `claude`, no network.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"


def sha(grader: str) -> str:
    return hashlib.sha256((AGENTS / f"{grader}.md").read_bytes()).hexdigest()


class GradersCheckMismatchTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.evals = pathlib.Path(tmp.name)
        self.date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def line(self, grader: str, cases: int, clean: int, mismatch: int | None) -> dict:
        row = {"grader": grader, "sha256": sha(grader), "cases": cases, "clean": clean, "mutants": cases - clean}
        if mismatch is not None:
            row["mismatch"] = mismatch
        row["date"] = self.date
        return row

    def check(self, *rows: dict) -> tuple[int, list[str]]:
        (self.evals / "scores.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
        proc = subprocess.run(["bin/factory", "graders-check", "--evals-dir", str(self.evals)], cwd=ROOT,
                              capture_output=True, text=True, check=False)
        return proc.returncode, (proc.stdout + proc.stderr).splitlines()

    def where(self, grader: str) -> str:
        return f"for sha256 {sha(grader)} in {self.evals}/scores.jsonl"

    def test_a_clean_replay_prints_only_ok(self) -> None:
        rc, out = self.check(self.line("judge", 9, 1, 0), self.line("reviewer", 8, 3, 0))
        self.assertEqual((rc, out), (0, ["graders-check: OK"]))

    def test_a_line_without_a_mismatch_field_prints_only_ok(self) -> None:
        rc, out = self.check(self.line("judge", 9, 1, None), self.line("reviewer", 8, 3, None))
        self.assertEqual((rc, out), (0, ["graders-check: OK"]))

    def test_a_partial_mismatch_prints_one_info_line(self) -> None:
        rc, out = self.check(self.line("judge", 9, 1, 0), self.line("reviewer", 8, 3, 3))
        self.assertEqual((rc, out), (0, [
            f"INFO reviewer: last replay mismatched 3 of 8 cases {self.where('reviewer')}",
            "graders-check: OK"]))

    def test_a_replay_that_matched_no_case_warns_stale(self) -> None:
        rc, out = self.check(self.line("judge", 4, 1, 4), self.line("reviewer", 8, 3, 0))
        self.assertEqual((rc, out), (0, [
            f"WARN STALE judge: last replay matched none of its 4 cases {self.where('judge')}",
            "graders-check: OK"]))

    def test_the_newest_line_decides(self) -> None:
        # An older all-miss line under the same hash says nothing once a newer clean replay follows it.
        rc, out = self.check(self.line("judge", 4, 1, 4), self.line("judge", 9, 1, 0), self.line("reviewer", 8, 3, 0))
        self.assertEqual((rc, out), (0, ["graders-check: OK"]))


if __name__ == "__main__":
    unittest.main()
