"""The capture hook's background sync rebases onto the remote before it pushes (#342, slice 3.2).

Two clones of one bare store stand in for two machines. Machine A captures and pushes first; machine B, now
behind, captures next. Without the pull B's push is rejected and its capture never leaves B; with it B's
capture lands on the remote beside A's, both INDEX lines kept by the union merge. No network.

PausedRebaseTests: a post-checkout hook in A's store holds A's background rebase open mid-rebase (HEAD detached,
rebase in progress), so another hook can run inside that window: a second capture, a recall whose fetch fails,
or a SIGKILL of the sync followed by the next capture. Each must leave every capture on main and, once the
remote is reachable, on the remote.
"""

from __future__ import annotations

import json
import os
import pathlib
import signal
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HOOK = ROOT / "seed/.claude/hooks/mem-capture.sh"
RECALL = ROOT / "seed/.claude/hooks/mem-recall.sh"

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


class Base(unittest.TestCase):
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

    def start_capture(self, store: pathlib.Path, sid: str) -> subprocess.Popen:
        transcript = self.top / f"{sid}.jsonl"
        transcript.write_text(json.dumps({"type": "user", "message": {"role": "user", "content": f"prompt {sid}"}}) + "\n")
        p = subprocess.Popen(["bash", str(HOOK)], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, text=True, cwd=self.cwd,
                             env={**GIT_ENV, "LOAM_MEMSTORE": str(store)})
        p.stdin.write(json.dumps({"hook_event_name": "SessionEnd", "transcript_path": str(transcript),
                                  "session_id": sid, "cwd": str(self.cwd)}))
        p.stdin.close()
        return p

    def finish(self, p: subprocess.Popen) -> None:
        self.assertEqual(p.wait(timeout=30), 0, p.stderr.read())
        p.stderr.close()

    def capture(self, store: pathlib.Path, sid: str) -> None:
        self.finish(self.start_capture(store, sid))

    def recall(self, store: pathlib.Path) -> None:
        r = subprocess.run(
            ["bash", str(RECALL)],
            input=json.dumps({"hook_event_name": "SessionStart", "session_id": "recall", "cwd": str(self.cwd)}),
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


class TwoMachineTests(Base):
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


class PausedRebaseTests(Base):
    def setUp(self) -> None:
        super().setUp()
        self.a, b = self.top / "store-a", self.top / "store-b"
        git("clone", "-q", str(self.origin), str(self.a), cwd=self.top)
        git("clone", "-q", str(self.origin), str(b), cwd=self.top)
        self.capture(self.a, "s0")
        self.wait_for_remote("s0")
        self.capture(b, "s1")
        self.assertIn(" | s1 | ", self.wait_for_remote("s0", "s1"))  # A is now behind the remote

        # While the pause file exists, the next checkout in A (its sync's rebase onto origin/main) writes the
        # hook's pid and blocks until the go file appears.
        self.pause, self.paused, self.go = self.top / "pause", self.top / "paused", self.top / "go"
        hook = self.a / ".git/hooks/post-checkout"
        hook.write_text(f"""#!/bin/sh
[ -f '{self.pause}' ] || exit 0
rm -f '{self.pause}'; echo $$ > '{self.paused}'
while [ ! -f '{self.go}' ]; do sleep 0.05; done
""")
        hook.chmod(0o755)
        self.addCleanup(self.go.touch)
        self.pause.touch()
        self.capture(self.a, "s2")
        deadline = time.monotonic() + 15
        while not self.paused.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(self.paused.exists(), "A's sync never reached its rebase")
        self.assertTrue((self.a / ".git/rebase-merge").exists())

    def on_main(self, sid: str) -> bool:
        return f" | {sid} | " in git("show", "main:traces/project/INDEX.md", cwd=self.a)

    def assert_clean_main(self) -> None:
        self.assertEqual(git("symbolic-ref", "HEAD", cwd=self.a), "refs/heads/main")
        self.assertFalse((self.a / ".git/rebase-merge").exists(), "rebase left in progress")

    def test_a_capture_during_the_rebase_keeps_its_index_line(self) -> None:
        p = self.start_capture(self.a, "s3")
        time.sleep(0.5)
        self.go.touch()
        self.finish(p)
        index = self.wait_for_remote("s0", "s1", "s2", "s3")
        for sid in ("s0", "s1", "s2", "s3"):
            self.assertIn(f" | {sid} | ", index, f"{sid} missing from the remote INDEX")
        self.assert_clean_main()

    def test_a_recall_whose_fetch_fails_leaves_the_rebase_alone(self) -> None:
        offline = self.top / "origin.off"
        self.origin.rename(offline)
        self.recall(self.a)
        self.assertTrue((self.a / ".git/rebase-merge").exists(), "recall aborted the capture's rebase")
        offline.rename(self.origin)
        self.go.touch()
        index = self.wait_for_remote("s2")
        log = (self.a / "reports/sync.log").read_text()
        self.assertIn(" | s2 | ", index, f"the capture's sync never pushed; sync.log: {log}")
        self.assert_clean_main()

    def kill_the_sync(self) -> None:
        # The post-checkout hook's parent is git rebase, and its parent is the background sync's shell.
        hook = int(self.paused.read_text())
        rebase = int(subprocess.run(["ps", "-o", "ppid=", "-p", str(hook)], capture_output=True, text=True).stdout)
        sync = int(subprocess.run(["ps", "-o", "ppid=", "-p", str(rebase)], capture_output=True, text=True).stdout)
        for pid in (sync, rebase, hook):
            os.kill(pid, signal.SIGKILL)
        time.sleep(0.3)

    def test_after_a_kill_mid_rebase_the_next_capture_lands_on_main(self) -> None:
        self.kill_the_sync()
        self.capture(self.a, "s5")
        index = self.wait_for_remote("s2", "s5")
        self.assertIn(" | s5 | ", index, "s5 never reached the remote")
        self.assertTrue(self.on_main("s5"), "s5 is not on A's main")
        self.assert_clean_main()

    def test_after_a_kill_mid_rebase_offline_the_next_capture_and_recall_keep_it(self) -> None:
        self.kill_the_sync()
        self.origin.rename(self.top / "origin.off")
        self.capture(self.a, "s5")
        time.sleep(1)  # the background fetch fails and the sync exits
        self.recall(self.a)
        self.assertTrue(self.on_main("s5"), "s5 is not on A's main")
        self.assertTrue(self.on_main("s2"), "s2 is not on A's main")
        self.assert_clean_main()


if __name__ == "__main__":
    unittest.main()
