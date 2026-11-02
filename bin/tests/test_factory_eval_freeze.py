"""`bin/factory eval-freeze` records each frozen case's tree base, the merge base of the run's base and graded
commits that its three-dot Diff starts from, and freezes no case whose tree base does not resolve, since case_tree
would then fall back to the Diff heading's commit, which need not be that base.

Runs the real eval-freeze against a small git repository standing in for the checkout.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def git(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


class EvalFreezeTests(unittest.TestCase):
    def test_freeze_records_the_tree_base_and_refuses_a_round_without_one(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = pathlib.Path(tmp_dir.name)
        repo = tmp / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "t@example.com")
        git(repo, "config", "user.name", "t")
        (repo / "a.txt").write_text("one\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "fork point")
        fork = git(repo, "rev-parse", "HEAD")
        git(repo, "checkout", "-qb", "ticket")
        (repo / "a.txt").write_text("two\n")
        git(repo, "commit", "-qam", "graded")
        graded = git(repo, "rev-parse", "HEAD")
        git(repo, "checkout", "-q", "-")
        (repo / "b.txt").write_text("main moves on\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "run base")
        base = git(repo, "rev-parse", "HEAD")
        runs = []
        for sha8, with_graded in (("aaaaaaaa", True), ("bbbbbbbb", False)):
            run = tmp / "runs" / "7" / sha8
            run.mkdir(parents=True)
            (run / "base.sha").write_text(base + "\n")
            if with_graded:
                (run / "round-1.graded.sha").write_text(graded + "\n")
            (run / "round-1.judge.json").write_text(json.dumps({"verdict": "pass"}))
            (run / "round-1.review.json").write_text(json.dumps({"verdict": "merge", "findings": []}))
            for g in ("judge", "review"):
                (run / f"round-1.{g}.prompt.md").write_text(f"rubric\n## Ticket\n\nticket 7\n\n## Diff ({base[:8]}...HEAD)\n")
            runs.append(run)
        evals = tmp / "evals"
        env = {**os.environ, "FACTORY_ROOT": str(repo)}
        proc = subprocess.run([str(ROOT / "bin/factory"), "eval-freeze", "--evals-dir", str(evals), *map(str, runs)],
                              env=env, capture_output=True, text=True, check=False)
        self.assertIn(f"frozen {runs[0]}: 7-aaaaaaaa round-1", proc.stdout, proc.stdout + proc.stderr)
        for g in ("judge", "reviewer"):
            exp = json.loads((evals / "clean" / g / "7-aaaaaaaa" / "expected.json").read_text())
            self.assertEqual(exp["tree_base"], fork, "the tree base is the merge base, not the run's base")
        self.assertIn(f"not frozen {runs[1]}: no tree base", proc.stdout)
        self.assertFalse((evals / "clean" / "judge" / "7-bbbbbbbb").exists())


if __name__ == "__main__":
    unittest.main()
