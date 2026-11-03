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
next holder lands it; a directory left at the lock path by the earlier mkdir lock does not block captures; a trace
the store's exclude file ignores is still committed, and stays spooled until a commit holds it. A capture removes an
index.lock only when a holder scan that ran to its end finds no holder, so a git outside the store lock, paused with it
open or (`git commit -a` in its editor) working in the store, keeps it and the capture spools, and the paused git's
index and commit (with its message) land; an index.lock no process holds is removed at once.
IndexLockTests (Linux, where the scan reads /proc): a process whose main thread has exited, holding index.lock in
another thread, keeps it, and so does a holder scan made to fail or stall at its listing of /proc; each such capture
spools its entry within the hook timeout, and the next capture whose scan ends clear removes the lock and lands both.
ScanTests: the three copies of the store lock block are identical, and each one's scan, sourced on its own, finds a
process with index.lock open and a git working in the store (not another process there) on /proc, and on the lsof
branch, reached with a stand-in lsof, keeps the lock when lsof reports a holder, fails, stalls or is missing.
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
import re
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

    def start_capture(self, store: pathlib.Path, sid: str, rewrite: bool = True,
                      env: dict[str, str] | None = None) -> subprocess.Popen:
        transcript = self.top / f"{sid}.jsonl"
        if rewrite:
            transcript.write_text(json.dumps({"type": "user", "message": {"role": "user", "content": f"prompt {sid}"}}) + "\n")
        p = subprocess.Popen(["bash", str(HOOK)], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, text=True, cwd=self.cwd,
                             env={**GIT_ENV, "LOAM_MEMSTORE": str(store), **(env or {})})
        p.stdin.write(json.dumps({"hook_event_name": "SessionEnd", "transcript_path": str(transcript),
                                  "session_id": sid, "cwd": str(self.cwd)}))
        p.stdin.close()
        return p

    def finish(self, p: subprocess.Popen) -> None:
        self.assertEqual(p.wait(timeout=30), 0, p.stderr.read())
        p.stderr.close()

    def capture(self, store: pathlib.Path, sid: str, env: dict[str, str] | None = None) -> None:
        self.finish(self.start_capture(store, sid, env=env))

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

    def index_lock_store(self) -> None:
        # A store with no remote, and the index.lock path a holder or a fault test plants.
        self.store = self.top / "store"
        git("init", "-q", str(self.store), cwd=self.top)
        self.lock = self.store / ".git/index.lock"

    def head_index(self) -> str:
        return git("show", "HEAD:traces/project/INDEX.md", cwd=self.store)

    def assert_both_landed(self) -> None:
        self.assertFalse(self.lock.exists(), "the stale index.lock was kept")
        self.assertEqual(self.spool(self.store), [], "the spool was not drained")
        index = self.head_index()
        for sid in ("s1", "s2"):
            self.assertIn(f" | {sid} | ", index, f"{sid} is not in HEAD")

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

    def test_the_drain_removes_only_old_tmp_directories_under_the_lock(self) -> None:
        a, _ = self.two_stores()
        spool = a / ".git/loam-spool"
        old, mid, new = spool / ".tmp-99999", spool / ".tmp-99997", spool / ".tmp-99998"
        now = time.time()
        for d, age in ((old, 600), (mid, 240), (new, 0)):
            d.mkdir(parents=True)
            (d / "trace.jsonl.gz").write_text("x")
            os.utime(d, (now - age, now - age))
        with open(a / ".git/loam-mem.lock", "a") as held:
            fcntl.flock(held, fcntl.LOCK_EX)
            self.capture(a, "s1")
            self.assertEqual(len(self.spool(a)), 1, "the capture was not spooled")
            self.assertTrue(old.is_dir(), "the old .tmp- directory was removed without the lock")
        self.capture(a, "s2")
        self.assertTrue(self.in_tree(a, "s1") and self.in_tree(a, "s2"), "both sessions must be committed")
        self.assertFalse(old.exists(), "the ten-minute-old .tmp- directory was kept")
        self.assertTrue((mid / "trace.jsonl.gz").is_file(), "the four-minute-old .tmp- directory was removed")
        self.assertTrue((new / "trace.jsonl.gz").is_file(), "the fresh .tmp- directory was removed")

    def test_an_old_lock_directory_does_not_block_captures(self) -> None:
        a, _ = self.two_stores()
        (a / ".git/loam-mem.lock").mkdir()  # left by the earlier mkdir lock
        self.capture(a, "s1")
        self.assertIn(" | s1 | ", self.wait_for_remote("s1"), "the capture never reached the remote")

    @unittest.skipIf(os.geteuid() == 0, "root writes a read-only .git/objects")
    def test_an_excluded_trace_stays_spooled_until_committed(self) -> None:
        store = self.top / "store"
        git("init", "-q", str(store), cwd=self.top)
        exclude = store / ".git/info/exclude"
        exclude.parent.mkdir(exist_ok=True)
        exclude.write_text("traces/\n")
        objects = store / ".git/objects"
        mode = objects.stat().st_mode
        objects.chmod(mode & ~0o222)
        self.addCleanup(objects.chmod, mode)
        self.capture(store, "s1")  # its commit fails
        self.assertEqual(len(self.spool(store)), 1, "the uncommitted capture left the spool")
        self.assertNotEqual(subprocess.run(["git", "rev-parse", "-q", "--verify", "HEAD"], cwd=store,
                                           capture_output=True).returncode, 0, "the failed commit made a HEAD")
        objects.chmod(mode)
        self.capture(store, "s1")
        trace = next((store / "traces/project").glob("*-s1.jsonl.gz")).relative_to(store).as_posix()
        self.assertEqual(git("rev-parse", f"HEAD:{trace}", cwd=store),
                         git("hash-object", trace, cwd=store), "the ignored trace is not in HEAD")
        self.assertIn(" | s1 | ", git("show", "HEAD:traces/project/INDEX.md", cwd=store))
        self.assertEqual(self.spool(store), [], "the spool was not drained")
        self.assertEqual(exclude.read_text(), "traces/\n", "the exclude rule was changed")
        subprocess.run(["git", "check-ignore", "-q", "--no-index", trace], cwd=store, check=True)

    def test_a_trace_a_clean_filter_rewrites_leaves_the_spool(self) -> None:
        store = self.top / "store"
        git("init", "-q", str(store), cwd=self.top)
        git("config", "filter.b64.clean", "base64", cwd=store)  # stands in for git-lfs
        git("config", "filter.b64.smudge", "base64 -d", cwd=store)
        (store / ".git/info").mkdir(exist_ok=True)
        (store / ".git/info/attributes").write_text("*.gz filter=b64\n")
        for sid in ("s1", "s2"):
            self.capture(store, sid)
            self.assertEqual(self.spool(store), [], f"{sid}'s committed entry stayed in the spool")

    def test_a_git_add_outside_the_store_lock_keeps_its_index_lock(self) -> None:
        self.index_lock_store()
        inside, go = self.top / "inside", self.top / "go"
        clean = self.top / "clean.sh"
        clean.write_text(f"#!/bin/sh\ntouch '{inside}'; while [ ! -f '{go}' ]; do sleep 0.05; done; cat\n")
        clean.chmod(0o755)
        git("config", "filter.slow.clean", str(clean), cwd=self.store)
        (self.store / ".git/info").mkdir(exist_ok=True)
        (self.store / ".git/info/attributes").write_text("user.txt filter=slow\n")
        (self.store / "user.txt").write_text("user\n")
        add = subprocess.Popen(["git", "add", "user.txt"], cwd=self.store, env=GIT_ENV,
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        self.addCleanup(add.stderr.close)
        self.addCleanup(add.wait, 30)
        self.addCleanup(go.touch)
        self.until(inside.exists, "the git add to pause in its clean filter")
        self.capture(self.store, "s1")
        self.assertTrue(self.lock.is_file(), "the capture removed the live git add's index.lock")
        self.assertEqual(len(self.spool(self.store)), 1, "s1 is not in the spool")
        go.touch()
        self.assertEqual(add.wait(timeout=30), 0, add.stderr.read())
        status = subprocess.run(["git", "status", "--porcelain"], cwd=self.store, env=GIT_ENV,
                                capture_output=True, text=True)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(git("diff", "--cached", "--name-only", cwd=self.store), "user.txt")
        self.capture(self.store, "s2")
        self.assert_both_landed()

    def test_a_git_commit_paused_in_its_editor_keeps_its_index_lock(self) -> None:
        # `git commit -a` writes index.lock and closes it before it runs the editor, so no process has it open.
        self.index_lock_store()
        (self.store / "user.txt").write_text("user\n")
        git("add", "user.txt", cwd=self.store)
        git("commit", "-qm", "user", cwd=self.store)
        (self.store / "user.txt").write_text("edited\n")
        inside, go = self.top / "inside", self.top / "go"
        editor = self.top / "editor.sh"
        editor.write_text(f"#!/bin/sh\ntouch '{inside}'; while [ ! -f '{go}' ]; do sleep 0.05; done; echo 'user message' > \"$1\"\n")
        editor.chmod(0o755)
        commit = subprocess.Popen(["git", "commit", "-a"], cwd=self.store, env={**GIT_ENV, "GIT_EDITOR": str(editor)},
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        self.addCleanup(commit.stderr.close)
        self.addCleanup(commit.wait, 30)
        self.addCleanup(go.touch)
        self.until(inside.exists, "the git commit to pause in its editor")
        self.assertTrue(self.lock.is_file(), "the paused git commit holds no index.lock")
        self.capture(self.store, "s1")
        self.assertTrue(self.lock.is_file(), "the capture removed the paused git commit's index.lock")
        self.assertEqual(len(self.spool(self.store)), 1, "s1 is not in the spool")
        go.touch()
        self.assertEqual(commit.wait(timeout=30), 0, commit.stderr.read())
        status = subprocess.run(["git", "status", "--porcelain"], cwd=self.store, env=GIT_ENV,
                                capture_output=True, text=True)
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(git("log", "-1", "--format=%B", cwd=self.store), "user message", "the user's commit did not land")
        self.assertEqual(git("show", "HEAD:user.txt", cwd=self.store), "edited")
        self.capture(self.store, "s2")
        self.assert_both_landed()
        self.assertEqual(git("log", "-1", "--format=%B", "HEAD~1", cwd=self.store), "user message")
        self.assertEqual(git("show", "HEAD:user.txt", cwd=self.store), "edited")

    def test_an_index_lock_no_process_holds_is_removed(self) -> None:
        self.index_lock_store()
        self.lock.touch()
        self.capture(self.store, "s1")
        self.assertFalse(self.lock.exists(), "the stale index.lock was kept")
        self.assertEqual(self.spool(self.store), [], "the spool was not drained")
        self.assertIn(" | s1 | ", self.head_index())


# A process that holds the file argv[1] open in a second thread after its main thread exits, so its leader is a
# zombie whose /proc/<pid>/fd cannot be read. It touches argv[2] once the leader is a zombie and exits when argv[3]
# appears.
THREAD_HOLDER = """
import ctypes, os, sys, threading, time
f = open(sys.argv[1])
def hold():
    status = "/proc/%d/status" % os.getpid()
    for _ in range(500):
        if "\\tZ" in open(status).read().split("State:")[1][:4]:
            break
        time.sleep(0.01)
    open(sys.argv[2], "w").close()
    for _ in range(400):
        if os.path.exists(sys.argv[3]):
            break
        time.sleep(0.05)
threading.Thread(target=hold).start()
ctypes.CDLL(None).pthread_exit(None)
"""

# A sitecustomize.py whose audit hook touches {fired} and then runs {fault} when a python3 lists /proc itself.
SCAN_FAULT = """import os, sys, time
def h(e, a):
    if e in ("os.listdir", "os.scandir") and a and isinstance(a[0], (str, bytes)) and os.fsdecode(a[0]).rstrip("/") == "/proc":
        open({fired!r}, "a").close()
        {fault}
sys.addaudithook(h)
"""


@unittest.skipUnless(os.path.isdir("/proc/self/fd"), "the holder scan under test reads /proc")
class IndexLockTests(Base):
    def setUp(self) -> None:
        super().setUp()
        self.index_lock_store()

    def test_a_thread_outliving_its_main_thread_keeps_the_index_lock(self) -> None:
        self.lock.touch()
        inside, go = self.top / "inside", self.top / "go"
        holder = subprocess.Popen(["python3", "-c", THREAD_HOLDER, str(self.lock), str(inside), str(go)])
        self.addCleanup(holder.wait, 30)
        self.addCleanup(go.touch)
        self.until(inside.exists, "the holder's main thread to exit")
        status = pathlib.Path(f"/proc/{holder.pid}/status").read_text()
        self.assertRegex(status, r"(?m)^State:\tZ", "the holder's leader is not a zombie")
        self.assertRegex(status, r"(?m)^Threads:\t2$", "the holder's second thread is gone")
        self.capture(self.store, "s1")
        self.assertTrue(self.lock.exists(), "the capture removed an index.lock a live thread holds")
        self.assertEqual(len(self.spool(self.store)), 1, "s1 is not in the spool")
        go.touch()
        holder.wait(timeout=30)
        self.capture(self.store, "s2")
        self.assert_both_landed()

    def assert_a_faulty_scan_keeps_the_lock(self, fault: str) -> None:
        self.lock.touch()  # no process holds it
        inj, fired = self.top / "inj", self.top / "fired"
        inj.mkdir()
        (inj / "sitecustomize.py").write_text(SCAN_FAULT.format(fired=str(fired), fault=fault))
        t0 = time.monotonic()
        self.capture(self.store, "s1", env={"PYTHONPATH": str(inj)})
        took = time.monotonic() - t0
        self.assertTrue(fired.exists(), "the holder scan never listed /proc")
        self.assertTrue(self.lock.exists(), "a scan that did not finish removed the index.lock")
        self.assertEqual(len(self.spool(self.store)), 1, "s1 is not in the spool")
        self.assertLess(took, 10, "the capture outran the hook's ten-second timeout")
        self.capture(self.store, "s2")
        self.assert_both_landed()

    def test_a_failed_holder_scan_keeps_the_index_lock(self) -> None:
        self.assert_a_faulty_scan_keeps_the_lock('raise PermissionError(13, "injected", "/proc")')

    def test_a_stalled_holder_scan_keeps_the_index_lock(self) -> None:
        self.assert_a_faulty_scan_keeps_the_lock("time.sleep(30)")


LOCK_BLOCK = re.compile(r"^# --- The store lock.*?^# --- end of the store lock block\.$", re.S | re.M)

# A stand-in lsof that logs its arguments and answers each query from LSOF_LOCK (a query naming the lock) or
# LSOF_CWD (the query for a git's cwd): "RC" or "RC:PIDS" exits RC after printing PIDS, "sleep" hangs.
FAKE_LSOF = """#!/bin/sh
printf '%s\\n' "$*" >> "$LSOF_LOG"
case "$*" in *" -d cwd "*) a=$LSOF_CWD ;; *) a=$LSOF_LOCK ;; esac
[ "$a" = sleep ] && exec sleep 30
case "$a" in *:*) echo "${a#*:}" ;; esac
exit "${a%%:*}"
"""


class ScanTests(Base):
    """index_lock_free from each script's copy of the lock block, sourced on its own, on both of its branches."""

    SCRIPTS = (HOOK, RECALL, WEEKLY)

    def setUp(self) -> None:
        super().setUp()
        self.index_lock_store()
        self.lock.touch()
        self.log = self.top / "lsof.log"

    def test_the_three_copies_of_the_lock_block_are_identical(self) -> None:
        blocks = [LOCK_BLOCK.search(s.read_text()) for s in self.SCRIPTS]
        self.assertTrue(all(blocks), "a script has no store lock block")
        self.assertEqual(blocks[0].group(0), blocks[1].group(0), "mem-recall.sh's lock block differs")
        self.assertEqual(blocks[0].group(0), blocks[2].group(0), "mem-weekly.sh's lock block differs")

    def scan(self, script: pathlib.Path, no_proc: bool = False, path: str | None = None, **env: str) -> int:
        # With no_proc, the block's probe for /proc names a missing path, so a Linux host runs the lsof branch.
        block = LOCK_BLOCK.search(script.read_text()).group(0)
        if no_proc:
            self.assertEqual(block.count("/proc/self/fd"), 1, "the block's /proc probe moved")
            block = block.replace("/proc/self/fd", str(self.top / "no-proc/self/fd"))
        src = self.top / "block.sh"
        src.write_text(block + "\n")
        self.log.unlink(missing_ok=True)
        r = subprocess.run([shutil.which("bash"), "-c", '. "$1"; index_lock_free "$STORE/.git/index.lock" "$STORE"', "_", str(src)],
                           env={**GIT_ENV, "STORE": str(self.store), "LSOF_LOG": str(self.log),
                                **({"PATH": path} if path else {}), **env},
                           capture_output=True, text=True, timeout=30)
        return r.returncode

    def fake_lsof_path(self) -> str:
        bin_ = self.top / "fake-bin"
        bin_.mkdir(exist_ok=True)
        (bin_ / "lsof").write_text(FAKE_LSOF)
        (bin_ / "lsof").chmod(0o755)
        return f"{bin_}:{os.environ['PATH']}"

    def test_lsof_finding_no_holder_clears_the_lock(self) -> None:
        path = self.fake_lsof_path()
        for script in self.SCRIPTS:
            self.assertEqual(self.scan(script, True, path, LSOF_LOCK="1", LSOF_CWD="1"), 0, script.name)
            self.assertEqual(self.log.read_text().splitlines(), [
                f"-t -n -P -- {self.lock}", f"-t -n -P -a -c /^git$/ -d cwd -- {self.store}"], script.name)

    def test_lsof_reporting_a_holder_or_failing_keeps_the_lock(self) -> None:
        path = self.fake_lsof_path()
        cases = {"the lock open": ("0:4242", "1"), "a pid with exit 1": ("1:4242", "1"), "an error": ("2", "1"),
                 "a git in the store": ("1", "0:4242"), "an error on the cwd query": ("1", "2")}
        for script in self.SCRIPTS:
            for what, (lock, cwd) in cases.items():
                self.assertNotEqual(self.scan(script, True, path, LSOF_LOCK=lock, LSOF_CWD=cwd), 0,
                                    f"{script.name}: lsof reporting {what} cleared the lock")

    def test_a_stalled_lsof_keeps_the_lock_at_the_deadline(self) -> None:
        path = self.fake_lsof_path()
        for script in self.SCRIPTS:
            t0 = time.monotonic()
            self.assertNotEqual(self.scan(script, True, path, LSOF_LOCK="sleep", LSOF_CWD="1",
                                          DEADLINE=str(time.time() + 1)), 0, script.name)
            self.assertLess(time.monotonic() - t0, 5, f"{script.name}: the lsof scan outran $DEADLINE")

    def test_no_lsof_keeps_the_lock(self) -> None:
        bin_ = self.top / "no-lsof-bin"
        bin_.mkdir()
        for tool in ("python3", "git"):
            (bin_ / tool).symlink_to(os.path.realpath(shutil.which(tool)))
        for script in self.SCRIPTS:
            self.assertNotEqual(self.scan(script, True, str(bin_)), 0, f"{script.name}: no lsof cleared the lock")

    def scan_beside(self, script: pathlib.Path, cmd: list[str], ready) -> int:
        # Scan while cmd runs in the store, once ready(pid) holds; its stdin
        # is a pipe left open, so a command reading stdin waits.
        p = subprocess.Popen(cmd, cwd=self.store, stdin=subprocess.PIPE)
        try:
            self.until(lambda: ready(p.pid), f"{cmd[0]} to start")
            return self.scan(script)
        finally:
            p.kill()
            p.wait()
            p.stdin.close()

    @unittest.skipUnless(os.path.isdir("/proc/self/fd"), "the /proc scan reads /proc")
    def test_the_proc_scan_finds_an_open_lock_and_a_git_in_the_store(self) -> None:
        sleep = os.path.realpath(shutil.which("sleep"))
        git = os.path.realpath(shutil.which("git"))
        opened = self.top / "opened"
        hold = ["python3", "-c", "import sys, time; f = open(sys.argv[1]); open(sys.argv[2], 'w').close(); time.sleep(60)",
                str(self.lock), str(opened)]

        def runs(exe: str):
            return lambda pid: os.readlink(f"/proc/{pid}/exe") == exe

        for script in self.SCRIPTS:
            opened.unlink(missing_ok=True)
            self.assertEqual(self.scan(script), 0, f"{script.name}: an index.lock no one holds was kept")
            self.assertNotEqual(self.scan_beside(script, hold, lambda pid: opened.exists()), 0,
                                f"{script.name}: a process with the index.lock open was missed")
            self.assertNotEqual(self.scan_beside(script, ["git", "hash-object", "--stdin"], runs(git)), 0,
                                f"{script.name}: a git working in the store was missed")
            self.assertEqual(self.scan_beside(script, ["sleep", "60"], runs(sleep)), 0,
                             f"{script.name}: a process in the store that is not git counted as a holder")


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
    # core.hooksPath does not reach. Each event gets one such hook in the store's config, and three in the global
    # config: a dotted name, a name holding `=` and the nameless `[hook]` one. Older git runs none of them, so
    # there the tests only show the scripts still commit with the flags these keys add.
    def setUp(self) -> None:
        super().setUp()
        patcher = mock.patch.dict(GIT_ENV, {"GIT_CONFIG_GLOBAL": str(self.top / "global.gitconfig")})
        patcher.start()
        self.addCleanup(patcher.stop)

    def hooks(self, store: pathlib.Path, *names: str) -> None:
        self.ran = self.top / "hook-ran"
        for name in names:
            for scope, key in (("--local", f"hook.leak-{name}"), ("--global", f"hook.my.odd.{name}"),
                               ("--global", f"hook.eq={name}"), ("--global", "hook")):
                git("config", scope, "--add", f"{key}.event", name, cwd=store)
                git("config", scope, f"{key}.command",
                    f"echo {key}-{name} >> '{self.ran}'; sleep 20 > /dev/null 2>&1 &", cwd=store)


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
