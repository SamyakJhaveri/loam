"""The capture hook's background sync rebases onto the remote before it pushes (#342, slice 3.2).

Two clones of one bare store stand in for two machines. Machine A captures and pushes first; machine B, now
behind, captures next. Without the pull B's push is rejected and its capture never leaves B; with it B's
capture lands on the remote beside A's, both INDEX lines kept by the union merge. No network.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HOOK = ROOT / "seed/.claude/hooks/mem-capture.sh"

# Commits are made with a fixed identity, and git's background maintenance is off so TemporaryDirectory
# cleanup does not race a detached `git maintenance run --auto`.
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@localhost",
    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@localhost",
    "GIT_CONFIG_COUNT": "3",
    "GIT_CONFIG_KEY_0": "gc.auto", "GIT_CONFIG_VALUE_0": "0",
    "GIT_CONFIG_KEY_1": "maintenance.auto", "GIT_CONFIG_VALUE_1": "false",
    "GIT_CONFIG_KEY_2": "init.defaultBranch", "GIT_CONFIG_VALUE_2": "main",
}
for _key in ("LOAM_MEMSTORE", "LOAM_MEMSTORE_REMOTE", "GIT_SSH", "GIT_SSH_COMMAND", "GIT_SSH_VARIANT"):
    GIT_ENV.pop(_key, None)


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, env=GIT_ENV, capture_output=True, text=True,
                          check=True, timeout=30).stdout.strip()


class TwoMachineTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name).resolve()
        self.cwd = self.top / "project"
        self.cwd.mkdir()
        self.origin = self.top / "origin.git"
        git("init", "-q", "--bare", str(self.origin), cwd=self.top)
        seed = self.top / "seed"
        git("init", "-q", str(seed), cwd=self.top)
        (seed / "README").write_text("memory store\n")
        git("add", "-A", cwd=seed)
        git("commit", "-qm", "base", cwd=seed)
        git("push", "-q", str(self.origin), "main", cwd=seed)

    def capture(self, store: pathlib.Path, sid: str) -> None:
        transcript = self.top / f"{sid}.jsonl"
        transcript.write_text(json.dumps({"type": "user", "message": {"role": "user", "content": f"prompt {sid}"}}) + "\n")
        r = subprocess.run(
            ["bash", str(HOOK)],
            input=json.dumps({"hook_event_name": "SessionEnd", "transcript_path": str(transcript),
                              "session_id": sid, "cwd": str(self.cwd)}),
            capture_output=True, text=True, timeout=30, cwd=self.cwd,
            env={**GIT_ENV, "LOAM_MEMSTORE": str(store)},
        )
        self.assertEqual(r.returncode, 0, r.stderr)

    def remote_index(self) -> str:
        try:
            return git("show", "main:traces/project/INDEX.md", cwd=self.origin)
        except subprocess.CalledProcessError:
            return ""

    def wait_for_remote(self, *sids: str) -> str:
        # The push runs in the background, so poll the bare repo; the bound only matters when it never lands.
        deadline = time.monotonic() + 15
        index = self.remote_index()
        while not all(f" | {s} | " in index for s in sids) and time.monotonic() < deadline:
            time.sleep(0.2)
            index = self.remote_index()
        return index

    def test_the_second_machine_rebases_and_its_capture_lands(self) -> None:
        a, b = self.top / "store-a", self.top / "store-b"
        git("clone", "-q", str(self.origin), str(a), cwd=self.top)
        git("clone", "-q", str(self.origin), str(b), cwd=self.top)

        self.capture(a, "sess-a")
        self.assertIn(" | sess-a | ", self.wait_for_remote("sess-a"), "machine A's capture never reached the remote")

        self.capture(b, "sess-b")
        index = self.wait_for_remote("sess-a", "sess-b")
        log = (b / "reports/sync.log").read_text() if (b / "reports/sync.log").exists() else ""
        self.assertIn(" | sess-b | ", index, f"machine B's capture never reached the remote; sync.log: {log}")
        self.assertIn(" | sess-a | ", index, "machine B's push dropped machine A's INDEX line")
        tree = git("ls-tree", "-r", "--name-only", "main", "traces/project", cwd=self.origin).splitlines()
        self.assertTrue(any(p.endswith("-sess-a.jsonl.gz") for p in tree), tree)
        self.assertTrue(any(p.endswith("-sess-b.jsonl.gz") for p in tree), tree)

        # B ends clean on main with no rebase left in progress.
        self.assertEqual(git("symbolic-ref", "HEAD", cwd=b), "refs/heads/main")
        self.assertFalse((b / ".git/rebase-merge").exists(), "rebase left in progress")
        self.assertEqual(git("status", "--porcelain", cwd=b), "")


if __name__ == "__main__":
    unittest.main()
