"""The capture hook's background sync rebases onto the remote before it pushes (#342, slice 3.2).

Two clones of one bare store stand in for two machines. Machine A captures and pushes first; machine B, now
behind, captures next. Without the pull B's push is rejected and its capture never leaves B; with it B's
capture lands on the remote beside A's, both INDEX lines kept by the union merge. No network.

PausedRebaseTests: a smudge filter in A's store holds A's background rebase open mid-rebase (HEAD detached,
rebase in progress) while it writes s2's trace, so another hook can run inside that window: a second capture, a
recall whose fetch fails, mem-weekly.sh, a SIGKILL of only the sync's shell, or a SIGKILL of the whole sync (with or
without a stale index.lock, or one that cannot be removed) followed by the next capture. Each must leave every
capture on main and, once the remote is reachable, on the remote; none may write into, or abort, a rebase another
process owns, and none may run one of the git hooks A's store sets.

LockTests: a capture that cannot take the store lock in time keeps its data in the spool under .git and the
next holder lands it; a directory left at the lock path by the earlier mkdir lock does not block captures.
RecallBoundTests: a recall whose rebase hangs ends within its five-second hook timeout and leaves main clean.
OverlapTests: of two overlapping captures of one session, the one that read the longer transcript wins, whichever
publishes last.
DeadlineTests: a clean filter that hangs `git add` and `git status` cannot hold capture or recall past its hook
timeout; the capture stays spooled and lands once the filter returns.
NoHookTests: store git runs no git hook, even one the store's core.hooksPath names, so a hook's background child
cannot keep the store lock after a capture, a recall (its fetch and rebase included) or mem-weekly.sh returns.
ConfigHookTests: the same for hooks defined in the store's or the global config (git 2.54 and later).
SigningTests: a global commit.gpgsign with no usable key does not keep a capture in the spool.
"""

from __future__ import annotations

import datetime
import fcntl
import gzip
import json
import os
import pathlib
import shutil
import signal
import subprocess
import tempfile
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
HOOK = ROOT / "seed/.claude/hooks/mem-capture.sh"
RECALL = ROOT / "seed/.claude/hooks/mem-recall.sh"
WEEKLY = ROOT / "seed/bin/mem-weekly.sh"

# Commits are made with a fixed identity, and git's background maintenance is off so the scratch directory's
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
        # A background sync can still be writing under .git after its push lands, so a cleanup race is no failure.
        self.top = pathlib.Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.top, ignore_errors=True)
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

    def start_capture(self, store: pathlib.Path, sid: str, rewrite: bool = True) -> subprocess.Popen:
        transcript = self.top / f"{sid}.jsonl"
        if rewrite:
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

    def recall(self, store: pathlib.Path, timeout: float = 30) -> None:
        r = subprocess.run(
            ["bash", str(RECALL)],
            input=json.dumps({"hook_event_name": "SessionStart", "session_id": "recall", "cwd": str(self.cwd)}),
            capture_output=True, text=True, timeout=timeout, cwd=self.cwd,
            env={**GIT_ENV, "LOAM_MEMSTORE": str(store)},
        )
        self.assertEqual(r.returncode, 0, r.stderr)

    def weekly(self, store: pathlib.Path) -> None:
        none = str(self.top / "none")
        r = subprocess.run(["bash", str(WEEKLY)], capture_output=True, text=True, timeout=60, cwd=self.cwd,
                           env={**GIT_ENV, "LOAM_MEMSTORE": str(store), "CLAUDE_CONFIG_DIR": none, "CODEX_HOME": none})
        self.assertEqual(r.returncode, 0, r.stderr)

    @staticmethod
    def spool(store: pathlib.Path) -> list[pathlib.Path]:
        d = store / ".git/loam-spool"
        return sorted(e for e in d.iterdir() if not e.name.startswith(".")) if d.is_dir() else []

    @staticmethod
    def in_tree(store: pathlib.Path, sid: str) -> bool:
        index = store / "traces/project/INDEX.md"
        return index.exists() and f" | {sid} | " in index.read_text()

    def two_stores(self) -> tuple[pathlib.Path, pathlib.Path]:
        a, b = self.top / "store-a", self.top / "store-b"
        git("clone", "-q", str(self.origin), str(a), cwd=self.top)
        git("clone", "-q", str(self.origin), str(b), cwd=self.top)
        return a, b

    def pause_rebase(self, store: pathlib.Path, sid: str) -> None:
        # While the pause file exists, the next write of sid's trace into this store's working tree (by a rebase
        # onto origin/main) runs a smudge filter that writes its pid and blocks until the go file appears. Store
        # git runs no hooks, so the pause is a filter, which runs inside the rebase while git holds index.lock.
        self.pause, self.paused, self.go = self.top / "pause", self.top / "paused", self.top / "go"
        git("config", "filter.pause.smudge",
            f"if [ -f '{self.pause}' ]; then rm -f '{self.pause}'; echo $$ > '{self.paused}';"
            f" while [ ! -f '{self.go}' ]; do sleep 0.05; done; fi; cat", cwd=store)
        (store / ".git/info").mkdir(exist_ok=True)
        (store / ".git/info/attributes").write_text(f"traces/project/*-{sid}.jsonl.gz filter=pause\n")
        self.addCleanup(self.go.touch)
        self.pause.touch()

    @staticmethod
    def until(cond, what: str, bound: float = 15) -> None:
        deadline = time.monotonic() + bound
        while not cond():
            if time.monotonic() > deadline:
                raise AssertionError(f"timed out waiting for {what}")
            time.sleep(0.05)

    def remote_index(self) -> str:
        try:
            return git("show", "main:traces/project/INDEX.md", cwd=self.origin)
        except subprocess.CalledProcessError:
            return ""

    def hooks(self, store: pathlib.Path, *names: str, child: bool = True) -> pathlib.Path:
        # Each hook logs its name and, with child, starts a background child that would keep any fd it inherited,
        # fd 9 too.
        hooks, self.ran = self.top / "hooks", self.top / "hook-ran"
        hooks.mkdir()
        tail = "sleep 20 > /dev/null 2>&1 &\n" if child else ""
        for name in names:
            (hooks / name).write_text(f"#!/bin/sh\nbasename \"$0\" >> '{self.ran}'\n{tail}")
            (hooks / name).chmod(0o755)
        git("config", "core.hooksPath", str(hooks), cwd=store)
        return hooks

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
        self.a, b = self.two_stores()
        # No store hook may run in A's capture, its background sync, recall or mem-weekly.sh.
        self.hooks(self.a, "pre-commit", "prepare-commit-msg", "commit-msg", "post-commit", "reference-transaction",
                   "post-checkout", "post-rewrite", "pre-rebase", "pre-push", "post-merge", "post-index-change", child=False)
        self.capture(self.a, "s0")
        self.wait_for_remote("s0")
        self.capture(b, "s1")
        self.assertIn(" | s1 | ", self.wait_for_remote("s0", "s1"))  # A is now behind the remote
        self.pause_rebase(self.a, "s2")  # the rebase replays A's own s2 commit with HEAD detached
        self.capture(self.a, "s2")
        self.until(self.paused.exists, "A's sync to reach its rebase")
        self.assertTrue((self.a / ".git/rebase-merge").exists())

    def on_main(self, sid: str) -> bool:
        return f" | {sid} | " in git("show", "main:traces/project/INDEX.md", cwd=self.a)

    def assert_clean_main(self) -> None:
        self.assertEqual(git("symbolic-ref", "HEAD", cwd=self.a), "refs/heads/main")
        self.assertFalse((self.a / ".git/rebase-merge").exists(), "rebase left in progress")
        self.assertFalse(self.ran.exists(), f"a store hook ran: {self.ran.read_text() if self.ran.exists() else ''}")

    def assert_rebase_untouched(self) -> None:
        self.assertTrue((self.a / ".git/rebase-merge").exists(), "the paused rebase was aborted")
        self.assertEqual(subprocess.run(["git", "symbolic-ref", "-q", "HEAD"], cwd=self.a, env=GIT_ENV).returncode, 1,
                         "HEAD left the paused rebase's detached state")

    def test_a_capture_during_the_rebase_keeps_its_index_line(self) -> None:
        p = self.start_capture(self.a, "s3")
        self.until(lambda: self.spool(self.a), "s3's spool entry")  # s3 holds its data before the rebase resumes
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

    def sync_chain(self) -> list[int]:
        # From the paused filter up its parents (git rebase, the bound's python3 if any) to the sync's bash shell.
        chain = [int(self.paused.read_text())]
        while True:
            ppid = int(subprocess.run(["ps", "-o", "ppid=", "-p", str(chain[-1])], capture_output=True,
                                      text=True).stdout)
            chain.append(ppid)
            comm = subprocess.run(["ps", "-o", "comm=", "-p", str(ppid)], capture_output=True, text=True).stdout
            if comm.strip().endswith("bash"):
                return chain

    def kill_the_sync(self) -> None:
        # Outermost first: a git that outlives its filter falls back to the unfiltered blob and goes on.
        for pid in reversed(self.sync_chain()):
            os.kill(pid, signal.SIGKILL)
        time.sleep(0.3)  # the filter's last `sleep 0.05` child exits

    def test_killing_only_the_sync_shell_keeps_its_live_rebase_locked(self) -> None:
        os.kill(self.sync_chain()[-1], signal.SIGKILL)
        self.capture(self.a, "s3")  # the rebase's git still holds the lock: s3 spools and leaves it alone
        self.assert_rebase_untouched()
        self.assertFalse(self.in_tree(self.a, "s3"), "s3 wrote into the live rebase")
        self.go.touch()
        self.until(lambda: not (self.a / ".git/rebase-merge").exists(), "the live rebase to finish")
        self.capture(self.a, "s4")
        index = self.wait_for_remote("s0", "s1", "s2", "s3", "s4")
        for sid in ("s0", "s1", "s2", "s3", "s4"):
            self.assertIn(f" | {sid} | ", index, f"{sid} missing from the remote INDEX")
        self.assert_clean_main()

    def test_a_stale_index_lock_from_the_killed_sync_is_cleared(self) -> None:
        self.kill_the_sync()
        (self.a / ".git/index.lock").touch()  # the killed git was writing the index
        self.capture(self.a, "s5")
        index = self.wait_for_remote("s2", "s5")
        self.assertIn(" | s5 | ", index, "s5 never reached the remote")
        self.assertTrue(self.on_main("s5"), "s5 is not on A's main")
        self.assert_clean_main()

    def test_an_unrecoverable_rebase_keeps_the_capture_in_the_spool(self) -> None:
        self.kill_the_sync()
        (self.a / ".git/index.lock").unlink()  # the killed git's, left while the filter paused it
        (self.a / ".git/index.lock").mkdir()  # an index.lock nothing can remove, so the abort fails
        self.capture(self.a, "s5")
        self.assert_rebase_untouched()
        self.assertFalse(self.in_tree(self.a, "s5"), "s5 wrote into the half-done rebase")
        self.assertEqual(len(self.spool(self.a)), 1, "s5 is not in the spool")
        (self.a / ".git/index.lock").rmdir()
        self.capture(self.a, "s6")
        index = self.wait_for_remote("s2", "s5", "s6")
        for sid in ("s2", "s5", "s6"):
            self.assertIn(f" | {sid} | ", index, f"{sid} missing from the remote INDEX")
            self.assertTrue(self.on_main(sid), f"{sid} is not on A's main")
        self.assertEqual(self.spool(self.a), [], "the spool was not drained")
        self.assert_clean_main()

    def test_weekly_waits_for_the_lock_and_leaves_the_rebase_alone(self) -> None:
        self.weekly(self.a)  # the paused sync holds the lock past weekly's wait
        self.assert_rebase_untouched()
        self.go.touch()
        index = self.wait_for_remote("s2")
        self.assertIn(" | s2 | ", index, "the capture's sync never pushed")
        self.until(lambda: not (self.a / ".git/rebase-merge").exists(), "the rebase to finish")
        self.weekly(self.a)
        self.assertTrue(self.on_main("s2"), "s2 is not on A's main")
        self.assert_clean_main()
        log = (self.a / "reports/sync.log").read_text()
        self.assertIn("weekly: store busy", log)
        self.assertNotIn("weekly sync failed", log)

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


class LockTests(Base):
    def test_a_capture_while_the_lock_is_held_lands_via_the_spool(self) -> None:
        a, _ = self.two_stores()
        with open(a / ".git/loam-mem.lock", "a") as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            self.capture(a, "s3")  # waits out its bound, then exits 0
            self.assertEqual(len(self.spool(a)), 1, "the capture was dropped, not spooled")
            self.assertFalse(self.in_tree(a, "s3"), "the capture wrote the tree without the lock")
        self.capture(a, "s4")
        index = self.wait_for_remote("s3", "s4")
        self.assertIn(" | s3 | ", index, "the spooled capture never landed")
        self.assertIn(" | s4 | ", index)
        self.assertEqual(self.spool(a), [], "the spool was not drained")
        tree = git("ls-tree", "-r", "--name-only", "main", "traces/project", cwd=self.origin).splitlines()
        self.assertTrue(any(p.endswith("-s3.jsonl.gz") for p in tree), tree)

    def test_an_old_lock_directory_does_not_block_captures(self) -> None:
        a, _ = self.two_stores()
        (a / ".git/loam-mem.lock").mkdir()  # left by the earlier mkdir lock
        self.capture(a, "s1")
        self.assertIn(" | s1 | ", self.wait_for_remote("s1"), "the capture never reached the remote")


class RecallBoundTests(Base):
    def test_a_hung_recall_rebase_ends_within_the_timeout_and_is_aborted(self) -> None:
        a, b = self.two_stores()
        self.capture(a, "s0")
        self.wait_for_remote("s0")
        self.capture(b, "s1")
        self.wait_for_remote("s0", "s1")  # A is now behind the remote
        self.pause_rebase(a, "s1")  # recall's fast-forward onto origin/main pauses and is never released
        start = time.monotonic()
        self.recall(a, timeout=15)
        self.assertLess(time.monotonic() - start, 5, "recall overran its five-second hook timeout")
        self.assertTrue(self.paused.exists(), "recall's rebase never ran")
        self.assertEqual(git("symbolic-ref", "HEAD", cwd=a), "refs/heads/main")
        self.assertFalse((a / ".git/rebase-merge").exists(), "recall left its rebase in progress")
        self.assertFalse((a / ".git/index.lock").exists())
        self.capture(a, "s2")  # the lock is free again
        self.assertIn(" | s2 | ", self.wait_for_remote("s0", "s1", "s2"))


class OverlapTests(Base):
    def test_an_older_capture_published_last_never_overwrites_the_newer_trace(self) -> None:
        store, sid = self.top / "store", "s1"
        traces = store / "traces/project"
        traces.mkdir(parents=True)
        # The barrier: A reads the transcript, then opens the session's .sha, here a FIFO that holds A until the
        # test closes its write end. Opening that end succeeds only once A is waiting on the FIFO.
        fifo = traces / f"{datetime.date.today().isoformat()}-{sid}.sha"
        os.mkfifo(fifo)
        a = self.start_capture(store, sid)
        held: list[int] = []

        def a_waits() -> bool:
            try:
                held.append(os.open(fifo, os.O_WRONLY | os.O_NONBLOCK))
                return True
            except OSError:
                return False

        self.until(a_waits, "capture A to read the transcript")
        fifo.unlink()  # B finds no .sha
        with (self.top / f"{sid}.jsonl").open("a") as fh:
            fh.write(json.dumps({"type": "user", "message": {"role": "user", "content": "the final turn"}}) + "\n")
        self.finish(self.start_capture(store, sid, rewrite=False))  # B
        os.close(held.pop())  # A resumes with the shorter transcript, publishes, and drains
        self.finish(a)
        trace = next(traces.glob(f"*-{sid}.jsonl.gz"))
        self.assertIn(b"the final turn", gzip.decompress(trace.read_bytes()), "A's older transcript overwrote B's")
        self.assertEqual(git("status", "--porcelain", cwd=store), "", "the newest trace is not committed")
        self.assertEqual(self.spool(store), [], "the stale entry was left in the spool")


class DeadlineTests(Base):
    def test_a_hanging_clean_filter_cannot_hold_capture_or_recall_past_their_timeouts(self) -> None:
        store = self.top / "store"
        git("init", "-q", str(store), cwd=self.top)
        go = self.top / "go"
        self.addCleanup(go.touch)
        git("config", "filter.hang.clean", f"while [ ! -f '{go}' ]; do sleep 0.05; done; cat", cwd=store)
        (store / ".git/info/attributes").write_text("* filter=hang\n")

        start = time.monotonic()
        self.capture(store, "s1")
        self.assertLess(time.monotonic() - start, 10, "capture overran its ten-second hook timeout")
        self.assertEqual(len(self.spool(store)), 1, "the uncommitted capture left the spool")

        (store / "handoff").mkdir()
        (store / "handoff/project.md").write_text("a note\n")
        start = time.monotonic()
        self.recall(store, timeout=30)
        self.assertLess(time.monotonic() - start, 5, "recall overran its five-second hook timeout")

        go.touch()  # the filter returns from now on
        self.capture(store, "s2")
        index = git("show", "main:traces/project/INDEX.md", cwd=store)
        for sid in ("s1", "s2"):
            self.assertIn(f" | {sid} | ", index, f"{sid} is not on main")
        self.assertEqual(self.spool(store), [], "the spool was not drained")


class NoHookTests(Base):
    def assert_no_hook_and_lock_free(self, store: pathlib.Path) -> None:
        self.assertFalse(self.ran.exists(), f"a store hook ran: {self.ran.read_text() if self.ran.exists() else ''}")
        with open(store / ".git/loam-mem.lock", "a") as fh:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                self.fail("the store lock is still held after the script returned")

    def last_subject(self, store: pathlib.Path) -> str:
        return git("log", "-1", "--format=%s", cwd=store)

    def test_capture_recall_and_weekly_commit_without_running_a_hook(self) -> None:
        store = self.top / "store"
        git("init", "-q", str(store), cwd=self.top)
        self.hooks(store, "post-commit")
        self.capture(store, "s1")
        self.assertTrue(self.last_subject(store).startswith("capture "))
        self.assert_no_hook_and_lock_free(store)
        (store / "handoff").mkdir()
        (store / "handoff/project.md").write_text("a note\n")
        self.recall(store)
        self.assertTrue(self.last_subject(store).startswith("handoff "))
        self.assert_no_hook_and_lock_free(store)
        (store / "notes/project").mkdir(parents=True)
        (store / "notes/project/n.md").write_text("a note\n")
        self.weekly(store)
        self.assertTrue(self.last_subject(store).startswith("weekly "))
        self.assert_no_hook_and_lock_free(store)

    def test_recall_fetch_and_rebase_reach_origin_without_running_a_hook(self) -> None:
        a, b = self.two_stores()
        (b / "two").write_text("two\n")
        git("add", "two", cwd=b)
        git("commit", "-qm", "two", cwd=b)
        git("push", "-q", "origin", "main", cwd=b)  # A is now one commit behind the remote
        self.hooks(a, "reference-transaction", "post-checkout")
        self.recall(a)
        self.assertEqual(git("rev-parse", "HEAD", cwd=a), git("rev-parse", "main", cwd=self.origin))
        self.assert_no_hook_and_lock_free(a)


class ConfigHookTests(NoHookTests):
    # Git 2.54 and later also run hooks defined in config (hook.<name>.event and hook.<name>.command), which
    # core.hooksPath does not reach. Each event gets one such hook in the store's config and one, with a dotted
    # name, in the global config. Older git runs neither, so there these tests pass trivially.
    def setUp(self) -> None:
        super().setUp()
        patcher = mock.patch.dict(GIT_ENV, {"GIT_CONFIG_GLOBAL": str(self.top / "global.gitconfig")})
        patcher.start()
        self.addCleanup(patcher.stop)

    def hooks(self, store: pathlib.Path, *names: str) -> None:
        self.ran = self.top / "hook-ran"
        for name in names:
            for scope, hook in (("--local", f"leak-{name}"), ("--global", f"my.odd.{name}")):
                git("config", scope, f"hook.{hook}.event", name, cwd=store)
                git("config", scope, f"hook.{hook}.command",
                    f"echo {scope}-{name} >> '{self.ran}'; sleep 20 > /dev/null 2>&1 &", cwd=store)


class SigningTests(Base):
    def test_a_global_commit_gpgsign_does_not_keep_the_capture_in_the_spool(self) -> None:
        # Signing fails here (gpg.program is `false`), as it does with commit.gpgsign set and no usable key.
        config = self.top / "global.gitconfig"
        config.write_text("[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = false\n")
        store = self.top / "store"
        git("init", "-q", str(store), cwd=self.top)
        with mock.patch.dict(GIT_ENV, {"GIT_CONFIG_GLOBAL": str(config)}):
            self.capture(store, "s1")
        self.assertEqual(self.spool(store), [], "the capture stayed in the spool")
        self.assertTrue(git("log", "-1", "--format=%s", cwd=store).startswith("capture "))


if __name__ == "__main__":
    unittest.main()
