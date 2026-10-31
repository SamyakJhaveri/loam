"""The SessionStart recall hook's store pull leaves the store as it was when the pull fails (#177).

mem-recall.sh pulls the memory store from its origin before it builds the manifest, bounded to five seconds.
ConflictTests: origin and the store changed the same line, so the rebase conflicts; abort() must undo it, leaving
no rebase in progress, HEAD, the working tree and the local commit unchanged, and one line in reports/sync.log.
HangTests: an ssh remote whose `ssh` writes its pid and sleeps; on the time bound killpg must kill the whole
pull group, so the hook returns near the bound and the ssh grandchild is gone. No network.
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
HOOK = ROOT / "seed/.claude/hooks/mem-recall.sh"

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


def recall(store: pathlib.Path, cwd: pathlib.Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    # The test's own timeout sits well above the hook's five-second bound, so a broken bound fails, not hangs.
    return subprocess.run(
        ["bash", str(HOOK)],
        input=json.dumps({"hook_event_name": "SessionStart", "source": "startup",
                          "session_id": "recall-pull-test", "cwd": str(cwd)}),
        capture_output=True, text=True, timeout=40, cwd=cwd,
        env={**GIT_ENV, "LOAM_MEMSTORE": str(store), **(env or {})},
    )


def alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class Base(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name).resolve()
        self.cwd = self.top / "project"
        self.cwd.mkdir()


class ConflictTests(Base):
    def test_a_conflicted_rebase_is_aborted_and_logged(self) -> None:
        origin = self.top / "origin.git"
        git("init", "-q", "--bare", str(origin), cwd=self.top)
        store = self.top / "store"
        git("init", "-q", str(store), cwd=self.top)
        # reports/ is where the hook writes sync.log; ignore it as a real store would not track it.
        (store / ".gitignore").write_text("reports/\n")
        (store / "notes.md").write_text("shared line\n")
        git("add", "-A", cwd=store)
        git("commit", "-qm", "base", cwd=store)
        git("remote", "add", "origin", str(origin), cwd=store)
        git("push", "-q", "origin", "main", cwd=store)

        other = self.top / "other"
        git("clone", "-q", str(origin), str(other), cwd=self.top)
        (other / "notes.md").write_text("line from the other machine\n")
        git("commit", "-qam", "other machine", cwd=other)
        git("push", "-q", "origin", "main", cwd=other)

        (store / "notes.md").write_text("line from this machine\n")
        git("commit", "-qam", "this machine", cwd=store)
        head = git("rev-parse", "HEAD", cwd=store)

        r = recall(store, self.cwd)
        self.assertEqual(r.returncode, 0, r.stderr)

        gitdir = store / ".git"
        self.assertFalse((gitdir / "rebase-merge").exists(), "rebase left in progress")
        self.assertFalse((gitdir / "rebase-apply").exists(), "rebase left in progress")
        self.assertEqual(git("symbolic-ref", "HEAD", cwd=store), "refs/heads/main")
        self.assertEqual(git("rev-parse", "HEAD", cwd=store), head)
        self.assertEqual(git("status", "--porcelain", cwd=store), "")
        self.assertEqual((store / "notes.md").read_text(), "line from this machine\n")
        log = (store / "reports/sync.log").read_text()
        self.assertEqual(len(log.splitlines()), 1, log)
        self.assertIn(" recall pull: ", log)


class HangTests(Base):
    def test_a_hung_ssh_remote_is_killed_whole_within_the_bound(self) -> None:
        store = self.top / "store"
        git("init", "-q", str(store), cwd=self.top)
        git("remote", "add", "origin", "ssh://git@memstore.invalid/store.git", cwd=store)
        pids = self.top / "ssh.pids"
        shim = self.top / "fake-ssh"
        shim.write_text(f"#!/bin/sh\necho $$ >> '{pids}'\nexec sleep 60\n")
        shim.chmod(0o755)

        def reap() -> None:
            for line in pids.read_text().split() if pids.exists() else ():
                try:
                    os.kill(int(line), 9)
                except ProcessLookupError:
                    pass
        self.addCleanup(reap)

        # GIT_SSH_VARIANT=ssh skips git's `ssh -G` probe, so the only ssh call is the fetch's.
        start = time.monotonic()
        r = recall(store, self.cwd, {"GIT_SSH_COMMAND": str(shim), "GIT_SSH_VARIANT": "ssh"})
        elapsed = time.monotonic() - start
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLess(elapsed, 12, "the hook did not return near its five-second bound")
        self.assertGreater(elapsed, 4, "the pull ended before the bound, so the hang was not exercised")

        started = [int(p) for p in pids.read_text().split()]
        self.assertTrue(started, "the ssh shim never ran")
        deadline = time.monotonic() + 5
        while any(alive(p) for p in started) and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertEqual([p for p in started if alive(p)], [], "an ssh grandchild outlived the hook")
        self.assertIn(" recall pull: timeout", (store / "reports/sync.log").read_text())


if __name__ == "__main__":
    unittest.main()
