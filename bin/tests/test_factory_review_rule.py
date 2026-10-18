"""The loop and both eval scorers read one reviewer rule: a high or medium finding blocks, the verdict word does not.

The loop side sources bin/factory (FACTORY_SOURCED=1) and runs the real run_review and call_json; the eval side
runs `bin/factory eval reviewer` as a program and imports eval_score.py. A fake `claude` on PATH answers every
call with the reply named in its prompt, so no model is called.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, sys
reply = sys.stdin.read().rsplit("REPLY ", 1)[1].splitlines()[0]
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": reply}))
"""


def finding(severity: str) -> dict[str, object]:
    return {"severity": severity, "file": "bin/x", "line": 3, "defect": "d", "fix": "f"}


# name -> (reply, what the loop does with it). The verdict word disagrees with the outcome in every case.
CASES = {
    "merge-medium": ({"verdict": "merge", "findings": [finding("medium")]}, "fix"),
    "merge-high": ({"verdict": "merge", "findings": [finding("high")]}, "fix"),
    "fix-low": ({"verdict": "fix", "findings": [finding("low")]}, "merge"),
}


def load_eval_score():
    spec = importlib.util.spec_from_file_location("eval_score", ROOT / "bin/factory.d/eval_score.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class ReviewRuleTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        fake = self.tmp / "bin/claude"
        fake.parent.mkdir()
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        self.env = {**os.environ, "PATH": f"{fake.parent}:{os.environ['PATH']}",
                    "FACTORY_RUNS_ROOT": str(self.tmp / "runs")}

    def loop_outcome(self, name: str, reply: dict[str, object]) -> tuple[str, int]:
        """(fix|merge from run_review, reviewer calls in the ledger) for one reply through the real call_json."""
        run = self.tmp / f"run-{name}"
        (run / "frozen").mkdir(parents=True)
        (run / "frozen/reviewer.schema.json").write_text("{}")
        script = (f"RUN='{run}'; WORKTREE='{run}'; LEDGER=\"$RUN/ledger.jsonl\"; DAILY=\"$RUN/daily.jsonl\"; KEY=t\n"
                  'touch "$LEDGER" "$DAILY"; date -u +%s > "$RUN/launched"\n'
                  f"build_evidence() {{ printf 'REPLY %s\\n' '{json.dumps(reply)}'; }}\n"
                  "run_review 1; echo \"rc:$?\"")
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**self.env, "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)
        self.assertIn("rc:", proc.stdout, proc.stderr)
        calls = [json.loads(x) for x in (run / "ledger.jsonl").read_text().splitlines()]
        return ("fix" if "rc:1" in proc.stdout else "merge"), sum(c.get("role") == "reviewer" for c in calls)

    def test_loop_and_eval_scorers_agree(self) -> None:
        cases = self.tmp / "cases/reviewer"
        for name, (reply, outcome) in CASES.items():
            (cases / name).mkdir(parents=True)
            (cases / name / "prompt.md").write_text(f"## Ticket\n\nREPLY {json.dumps(reply)}\n")
            (cases / name / "expected.json").write_text(json.dumps({"verdict": outcome}))
        proc = subprocess.run(["bin/factory", "eval", "reviewer", "--evals-dir", str(self.tmp / "cases"),
                               "--graders-dir", str(AGENTS)], cwd=ROOT, env=self.env,
                              capture_output=True, text=True, check=False)
        eval_score = load_eval_score()
        for name, (reply, outcome) in CASES.items():
            with self.subTest(name):
                # The loop: accepted on the first call (no refutation re-call), blocked by severity alone.
                self.assertEqual(self.loop_outcome(name, reply), (outcome, 1))
                # bin/factory eval scores what the loop did, not the verdict word.
                self.assertIn(f"eval reviewer/{name}: OK {outcome}", proc.stdout, proc.stderr)
                # eval_score.py: a clean copy counts a false alarm exactly when the loop blocks.
                self.assertEqual(eval_score.hit("reviewer", {"verdict": "merge"}, reply), outcome == "fix")
                # and a planted defect on bin/x is caught exactly when a blocking finding names it.
                mutant = {"verdict": "fix", "defect_class": "logic-bug", "defect_file": "bin/x"}
                self.assertEqual(eval_score.hit("reviewer", mutant, reply), outcome == "fix")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
