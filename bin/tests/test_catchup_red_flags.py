"""Behavior of the catchup skill's red-flags.sh: work that exists in only one copy.

Runs the real script in a throwaway clone of a throwaway bare remote, with git's
global config and the tmux server isolated, so the only flags are the fixture's.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "seed/.agents/skills/catchup/red-flags.sh"


class RedFlagsOneCopyTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name).resolve()
        base = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "TMUX"))}
        self.env = {**base, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@users.noreply.github.com",
                    "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@users.noreply.github.com",
                    "TMUX_TMPDIR": str(self.tmp)}
        src = self.tmp / "src"
        self.git(self.tmp, "init", "-q", "-b", "main", str(src))
        (src / "README.md").write_text("fixture\n", encoding="utf-8")
        self.git(src, "add", "README.md")
        self.git(src, "commit", "-qm", "fixture")
        self.git(self.tmp, "clone", "-q", "--bare", str(src), "remote.git")
        self.git(self.tmp, "clone", "-q", "remote.git", "clone")
        self.clone = self.tmp / "clone"

    def git(self, cwd: pathlib.Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True, text=True, check=True)

    def flags(self) -> list[str]:
        r = subprocess.run(["bash", str(SCRIPT)], cwd=self.clone, env=self.env,
                           capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        return [line for line in r.stdout.splitlines() if line.startswith("FLAG:")]

    def test_clean_clone_is_silent(self) -> None:
        self.assertEqual([], self.flags())

    def test_local_only_commit_is_flagged_by_branch(self) -> None:
        self.git(self.clone, "switch", "-qc", "wip")
        (self.clone / "notes.md").write_text("only here\n", encoding="utf-8")
        self.git(self.clone, "add", "notes.md")
        self.git(self.clone, "commit", "-qm", "local only")

        self.assertEqual(["FLAG: 1 commits exist only in this clone, on no remote-tracking ref;"
                          " by local ref: heads/wip 1"], self.flags())

    def test_dirty_other_worktree_is_counted(self) -> None:
        wt = self.tmp / "wt"
        self.git(self.clone, "worktree", "add", "-q", str(wt), "-b", "side")
        (wt / "scratch.txt").write_text("unsaved\n", encoding="utf-8")

        self.assertEqual([f"FLAG: uncommitted changes in 1 paths in worktree {wt}"], self.flags())


if __name__ == "__main__":
    unittest.main()
