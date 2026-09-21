"""A worker round that hits its own cap is a finished round, and a file ticket keeps its commit.

`bin/factory` is sourced (FACTORY_SOURCED=1) and its helpers are called directly, on
checked-in fixtures and a throwaway repository. No `claude` on PATH, no `bin/factory run`.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "bin/factory.d/fixtures"


def sourced(script: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run `script` in a bash that has sourced bin/factory from the repo root."""
    return subprocess.run(
        ["bash", "-c", f". bin/factory\n{script}"],
        cwd=ROOT, env={**os.environ, "FACTORY_SOURCED": "1", **(env or {})},
        capture_output=True, text=True, check=False,
    )


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class ClassifyResultTests(unittest.TestCase):
    def classify(self, path: str) -> str:
        proc = sourced(f"classify_result '{path}'")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.strip()

    def test_round_budget_hit_is_a_completed_round(self) -> None:
        # The Session D result: subtype error_max_budget_usd, is_error true, 86 turns, cost past the cap.
        self.assertEqual(self.classify(str(FIXTURES / "budget-stop.result.json")), "completed")

    def test_unknown_error_subtype_is_the_environment(self) -> None:
        # error_zzz is no real subtype: the classifier must not depend on knowing any failure name.
        self.assertEqual(self.classify(str(FIXTURES / "environment.result.json")), "environment")

    def test_missing_result_is_no_result(self) -> None:
        self.assertEqual(self.classify("/nonexistent/result.json"), "no-result")

    def test_assert_call_ok_returns_for_a_completed_round(self) -> None:
        proc = sourced(f"ROUND=1; assert_call_ok worker '{FIXTURES / 'budget-stop.result.json'}'; echo returned:$?")
        self.assertIn("returned:0", proc.stdout, proc.stderr)
        self.assertIn("hit its own cap (error_max_budget_usd after 86 turns)", proc.stderr)

    def test_assert_call_ok_stops_for_the_environment(self) -> None:
        with tempfile.TemporaryDirectory() as run:
            proc = sourced(f"RUN='{run}'; IS_FILE=1; assert_call_ok worker '{FIXTURES / 'environment.result.json'}'")
            self.assertEqual(proc.returncode, 4, proc.stderr)  # stopped-environment
            self.assertEqual((pathlib.Path(run) / "status").read_text().strip(), "stopped-environment")
            self.assertIn("boom", proc.stderr)


class FileTicketBranchTests(unittest.TestCase):
    def test_file_ticket_commit_survives_worktree_removal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            top = pathlib.Path(tmp)
            main, run, wt = top / "main", top / "run", top / "main-ticket"
            main.mkdir()
            run.mkdir()
            git("init", "-q", "-b", "main", cwd=main)
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base", cwd=main)
            branch = "factory/ticket-0123abcd"
            prepare = (f"MAIN_CHECKOUT='{main}'; RUN='{run}'; WORKTREE='{wt}'; BRANCH='{branch}'; IS_FILE=1; "
                       "prepare_worktree; echo returned:$?")
            proc = sourced(prepare)
            self.assertIn("returned:0", proc.stdout, proc.stderr)
            self.assertEqual(git("rev-parse", "--abbrev-ref", "HEAD", cwd=wt), branch)
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                            "--allow-empty", "-m", "marker"], cwd=wt, check=True)
            # The same removal the EXIT trap runs for a file ticket.
            git("worktree", "remove", "--force", str(wt), cwd=main)
            self.assertFalse(wt.exists())
            self.assertEqual(git("log", "-1", "--format=%s", branch, cwd=main), "marker")
            # A relaunch with the branch present reuses it rather than exiting stopped-environment.
            proc = sourced(prepare)
            self.assertIn("returned:0", proc.stdout, proc.stderr)
            self.assertEqual(git("log", "-1", "--format=%s", "HEAD", cwd=wt), "marker")


if __name__ == "__main__":
    unittest.main()
