"""A judge pass with a failing or missing row refutes itself, like a pass that ships a fix.

judge.md says "`verdict` is `pass` only if every row is `pass`", and verdict_consistent enforces it for every row
judge.schema.json requires. bin/factory is sourced (FACTORY_SOURCED=1) and the real verdict_consistent, call_json, and run_judge run. A fake
`claude` on PATH answers every call with the reply named in its prompt, so no model is called.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "bin/factory.d/judge.schema.json"

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, sys
reply = sys.stdin.read().rsplit("REPLY ", 1)[1].splitlines()[0]
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": reply}))
"""


def reply(verdict: str, verified: str, fixes: list[str]) -> dict[str, object]:
    return {"rows": {"correct": "pass", "verified": verified, "honest": "pass"}, "evidence": {},
            "fixes": fixes, "backlog": [], "verdict": verdict}


ROW_FAILS_VERDICT_PASSES = reply("pass", "fail", [])
ALL_ROWS_PASS = reply("pass", "pass", [])
FAIL_WITH_FIX = reply("fail", "fail", ["add the missing test to bin/x"])
EMPTY_ROWS_PASS = {**ALL_ROWS_PASS, "rows": {}}
PARTIAL_ROWS_PASS = {**ALL_ROWS_PASS, "rows": {"correct": "pass", "honest": "pass"}}


class VerdictRowsTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        fake = self.tmp / "bin/claude"
        fake.parent.mkdir()
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        self.env = {**os.environ, "PATH": f"{fake.parent}:{os.environ['PATH']}", "FACTORY_SOURCED": "1",
                    "FACTORY_RUNS_ROOT": str(self.tmp / "runs")}

    def sourced(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["bash", "-c", f". bin/factory\n{script}", "_", *args], cwd=ROOT, env=self.env,
                              capture_output=True, text=True, check=False)

    def consistent(self, obj: dict[str, object]) -> bool:
        path = self.tmp / "reply.json"
        path.write_text(json.dumps(obj))
        proc = self.sourced('verdict_consistent "$1" "$2"', str(path), str(SCHEMA))
        # A broken guard exits non-zero with usage text, and that must not count as a refutation.
        self.assertEqual(proc.stdout + proc.stderr, "")
        return proc.returncode == 0

    def judge_round(self, name: str, obj: dict[str, object]) -> tuple[int, int, str]:
        """(run_judge exit, judge calls in the ledger, last prompt) for one reply through the real call_json."""
        run = self.tmp / f"run-{name}"
        (run / "frozen").mkdir(parents=True)
        shutil.copy(SCHEMA, run / "frozen/judge.schema.json")
        script = (f"RUN='{run}'; WORKTREE='{run}'; LEDGER=\"$RUN/ledger.jsonl\"; DAILY=\"$RUN/daily.jsonl\"; KEY=t\n"
                  'touch "$LEDGER" "$DAILY"; date -u +%s > "$RUN/launched"\n'
                  f"build_evidence() {{ printf 'REPLY %s\\n' '{json.dumps(obj)}'; }}\n"
                  'run_judge 1; echo "rc:$?"')
        proc = self.sourced(script)
        self.assertIn("rc:", proc.stdout, proc.stderr)
        calls = [json.loads(x) for x in (run / "ledger.jsonl").read_text().splitlines()]
        rc = int(proc.stdout.rsplit("rc:", 1)[1].split()[0])
        return rc, sum(c.get("role") == "judge" for c in calls), (run / "round-1.judge.prompt.md").read_text()

    def test_failing_row_with_pass_verdict_is_inconsistent(self) -> None:
        self.assertFalse(self.consistent(ROW_FAILS_VERDICT_PASSES))

    def test_missing_rows_with_pass_verdict_are_inconsistent(self) -> None:
        # jq's all() is true on an empty set, so a judge that leaves a row out must not pass by omission.
        self.assertFalse(self.consistent(EMPTY_ROWS_PASS))
        self.assertFalse(self.consistent(PARTIAL_ROWS_PASS))
        rc, calls, prompt = self.judge_round("rows-empty", EMPTY_ROWS_PASS)
        self.assertEqual((rc, calls), (1, 3))
        self.assertIn("## Refutation", prompt)

    def test_schema_requires_the_rubric_rows(self) -> None:
        # The schema carries the row names verdict_consistent requires; they must match judge.md's rubric table.
        judge = (ROOT / "cultivation/marketplace/sam-cc-setup/agents/judge.md").read_text()
        table = judge.split("## Rubric", 1)[1].split("\n## ", 1)[0]
        rubric_rows = [r for r in re.findall(r"^\| (\w+) \|", table, re.M) if r != "Row"]
        required = json.loads(SCHEMA.read_text())["properties"]["rows"].get("required", [])
        self.assertEqual(sorted(required), sorted(rubric_rows))

    def test_controls_stay_consistent(self) -> None:
        self.assertTrue(self.consistent(ALL_ROWS_PASS))
        self.assertTrue(self.consistent(FAIL_WITH_FIX))

    def test_failing_row_takes_the_refutation_path_and_the_round_fails(self) -> None:
        rc, calls, prompt = self.judge_round("row-fail", ROW_FAILS_VERDICT_PASSES)
        # The fake repeats the same reply, so every refuted call is refuted again and the judge falls to fail.
        self.assertEqual((rc, calls), (1, 3))
        self.assertIn("## Refutation", prompt)
        # Control: an all-pass reply is accepted on the first call with no refutation.
        rc, calls, prompt = self.judge_round("all-pass", ALL_ROWS_PASS)
        self.assertEqual((rc, calls), (0, 1))
        self.assertNotIn("## Refutation", prompt)

    def test_refutation_shows_the_failing_row(self) -> None:
        _, _, prompt = self.judge_round("row-shown", ROW_FAILS_VERDICT_PASSES)
        refutation = prompt.split("## Refutation", 1)[1]
        self.assertIn('"verified":"fail"', refutation)
        self.assertIn("contradicts the rows,", refutation)


if __name__ == "__main__":
    unittest.main()
