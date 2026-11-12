"""A judge fail on only bookkeeping rows (JUDGE_SHADOW_ROWS, `honest`) whose fixes name no file but decisions.md logs
judge-shadow and does not block (owner, 12 Nov 2026); a fail on a substantive row (`correct`, `verified`), or with a fix
that names a file of the change, still fails the graders.

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real graders, run_judge and run_review run over a throwaway git
worktree. Only the model call (call_json) is stubbed: it writes the reply named for its role and records the role, so
the test sees whether the reviewer was reached. The evidence bundle and the mutation sweep are stubbed. No network.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS_PASS = {"correct": "pass", "verified": "pass", "honest": "pass"}
CLEAN_REVIEW = {"verdict": "merge", "findings": []}


def judge(rows: dict[str, str], fixes: list[str]) -> dict[str, object]:
    return {"verdict": "fail", "rows": rows, "evidence": {}, "fixes": fixes, "backlog": []}


class JudgeShadowTests(unittest.TestCase):
    def graders(self, judge_reply: dict[str, object]) -> tuple[int, pathlib.Path, str]:
        """(graders' exit, the run dir, the log) for one round whose judge returns judge_reply."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        top = pathlib.Path(tmp.name)
        wt, run = top / "wt", top / "run"
        wt.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=wt, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "b"],
                       cwd=wt, check=True)
        (run / "frozen").mkdir(parents=True)
        shutil.copy(ROOT / "bin/factory.d/judge.schema.json", run / "frozen/judge.schema.json")
        (run / "reply.judge").write_text(json.dumps(judge_reply))
        (run / "reply.review").write_text(json.dumps(CLEAN_REVIEW))
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_RUNS_ROOT=str(top / "runs"))
        script = (". bin/factory\n"
                  f"RUN='{run}'; LOG=\"$RUN/log\"; WORKTREE='{wt}'; CODEX_REVIEW=no; REVIEW_BLOCKED=0\n"
                  "build_evidence() { :; }; run_mutation_sweep() { echo sweep >> \"$RUN/calls\"; }\n"
                  'call_json() { echo "$3" >> "$RUN/calls"; cp "$RUN/reply.$2" "$RUN/round-$1.$2.json"; }\n'
                  "graders 1; echo \"graders=$?\"\n")
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, check=False, timeout=60)
        self.assertIn("graders=", proc.stdout, proc.stderr)
        return int(proc.stdout.split("graders=")[1].split()[0]), run, (run / "log").read_text()

    def test_bookkeeping_row_fail_reaches_the_reviewer_and_logs_judge_shadow(self) -> None:
        rc, run, log = self.graders(judge({**ROWS_PASS, "honest": "fail"}, ["label the SKIP step unverified in decisions.md"]))
        self.assertEqual(rc, 0, log)
        self.assertIn("judge-shadow", log)
        self.assertEqual((run / "calls").read_text().split(), ["judge", "sweep", "reviewer"])
        self.assertEqual((run / "round-1.fixes").read_text(), "")
        self.assertEqual((run / "round-1.judge-shadow").read_text().strip(), "honest")

    def test_substantive_fix_beside_a_bookkeeping_row_fail_still_fails(self) -> None:
        # Every row but honest passes, yet one fix is for the change itself: the fail blocks on it, as with no honest fail.
        crash, label = "fix the crash in bin/x when the input is empty", "label the SKIP step unverified in decisions.md"
        rc, run, log = self.graders(judge({**ROWS_PASS, "honest": "fail"}, [crash, label]))
        self.assertEqual(rc, 1, log)
        self.assertNotIn("judge-shadow", log)
        self.assertEqual((run / "round-1.fixes").read_text(), f"- {crash}\n- {label}\n")
        self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_substantive_row_fail_still_fails(self) -> None:
        # Each fix is bookkeeping, so only the row guard (or the required-row guard) can block these.
        label = "label the run unverified in decisions.md"
        for name, rows in (("correct", {**ROWS_PASS, "correct": "fail"}),
                           ("verified", {**ROWS_PASS, "verified": "fail"}),
                           ("verified and honest", {**ROWS_PASS, "verified": "fail", "honest": "fail"}),
                           ("correct missing", {"verified": "pass", "honest": "fail"})):
            with self.subTest(name):
                rc, run, log = self.graders(judge(rows, [label]))
                self.assertEqual(rc, 1, log)
                self.assertNotIn("judge-shadow", log)
                self.assertEqual((run / "round-1.fixes").read_text(), f"- {label}\n")
                self.assertFalse((run / "round-1.judge-shadow").exists())

    def test_fix_naming_another_file_beside_decisions_md_still_fails(self) -> None:
        # The fix names decisions.md, but also a file of the change: it is not bookkeeping, so the fail blocks.
        mixed = "fix the crash in bin/x when input is empty, and drop the decisions.md line that says it is handled"
        rc, run, log = self.graders(judge({**ROWS_PASS, "honest": "fail"}, [mixed]))
        self.assertEqual(rc, 1, log)
        self.assertNotIn("judge-shadow", log)
        self.assertEqual((run / "round-1.fixes").read_text(), f"- {mixed}\n")
        self.assertFalse((run / "round-1.judge-shadow").exists())

if __name__ == "__main__":
    unittest.main()
