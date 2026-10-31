"""The real build_evidence assembles a grader's evidence from a run dir and a git worktree.

Sources bin/factory (FACTORY_SOURCED=1) and runs build_evidence unstubbed, so the factory-macos CI job runs
its path-reading loop on bash 3.2 (#457). The diff holds two content files, one with a space in its path.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_NOSYSTEM": "1"}
FENCE = "~~~~~~~~~~~~ evidence"  # bin/factory's FENCE: the graders read worker text only between these lines (#38)


class BuildEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        # No inherited GIT_* (a caller's GIT_DIR would aim git at its own repo) and no user or system config.
        self.env = {**{k: v for k, v in os.environ.items() if not k.startswith("GIT_")}, **GIT_ENV,
                    "GIT_CONFIG_GLOBAL": str(self.tmp / "gitconfig")}
        wt = self.tmp / "wt"
        wt.mkdir()
        self.git(wt, "init", "-q")
        (wt / "a b.md").write_text("space old\n")
        (wt / "x.txt").write_text("plain old\n")
        self.git(wt, "add", "-A")
        self.git(wt, "commit", "-q", "-m", "base")
        base = self.git(wt, "rev-parse", "HEAD").strip()
        (wt / "a b.md").write_text("space new\n")
        (wt / "x.txt").write_text("plain new\n")
        self.git(wt, "commit", "-q", "-am", "head")
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True)
        (run / "base.sha").write_text(base + "\n")
        (run / "frozen/issue.md").write_text("TICKET-TEXT\n")
        (run / "round-1.checks").write_text("CHECKS-TEXT\n")
        (run / "round-1.measure").write_text("MEASURE-TEXT\n")
        (run / "decisions.md").write_text("DECISIONS-TEXT\n")
        (self.tmp / "rubric.md").write_text("RUBRIC-TEXT\n")
        self.wt, self.run, self.base = wt, run, base

    def git(self, cwd: pathlib.Path, *args: str) -> str:
        return subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=cwd, env=self.env,
                              capture_output=True, text=True, check=True).stdout

    def evidence(self, cap: int) -> str:
        script = (f"RUN='{self.run}'; ROUND=1; WORKTREE='{self.wt}'; DECISIONS='{self.run}/decisions.md'\n"
                  f"build_evidence '{self.tmp}/rubric.md' {cap}")
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**self.env, "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def test_full_evidence(self) -> None:
        out = self.evidence(1000)
        for text in ("RUBRIC-TEXT", "TICKET-TEXT", "CHECKS-TEXT", "MEASURE-TEXT", "DECISIONS-TEXT"):
            self.assertIn(text, out)
        # The stat names both files; each file's own hunk is in the content diff.
        self.assertRegex(out, r"(?m)^ a b\.md +\| +2 \+-$")
        self.assertRegex(out, r"(?m)^ x\.txt +\| +2 \+-$")
        self.assertIn("diff --git a/a b.md b/a b.md", out)
        self.assertIn("-space old\n+space new\n", out)
        self.assertIn("diff --git a/x.txt b/x.txt", out)
        self.assertIn("-plain old\n+plain new\n", out)
        self.assertNotIn("[content diff capped at", out)
        # Five fenced sections (ticket, checks, measure, decisions, diff), each opened and closed.
        self.assertEqual(out.splitlines().count(FENCE), 10)
        self.assertIn(f"\n## Diff ({self.base[:8]}...HEAD)\n\n{FENCE}\n", out)
        self.assertTrue(out.endswith(f"\n{FENCE}\n"))
        self.assertEqual((self.run / "round-1.diff").read_text().count("diff --git"), 2)

    def test_capped_evidence(self) -> None:
        out = self.evidence(3)
        self.assertIn("RUBRIC-TEXT", out)
        self.assertIn("diff --git a/a b.md b/a b.md", out)
        self.assertNotIn("+plain new", out)
        self.assertIn("[content diff capped at 3 lines; the stat above is complete]", out)
        self.assertTrue(out.endswith(f"[content diff capped at 3 lines; the stat above is complete]\n{FENCE}\n"))


if __name__ == "__main__":
    unittest.main()
