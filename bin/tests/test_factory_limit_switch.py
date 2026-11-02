"""Two runs on one host share the Claude account, so a usage-limit switch must not undo another run's switch.

Each case sources bin/factory (FACTORY_SOURCED=1) in its own run dir under one runs root, with ROOT pointed at a
temp home whose bin/claude-account is a fake: it keeps the active name in a file, stores accounts a and b, and
appends `<from> <to>` to `switches` on each `use`. CALL_ACCOUNT names the account the limited call ran under, as
the call sites record it, and limit_wait gets a usage-limit reply; its sleep to the reset is stubbed, so a run either
retries at once or reports the sleep (the lock's 1 s waits still sleep). The host-wide cooldown is the epoch second
in <runs root>/limit-switch.

OwnerLockTests take owner_lock, the run dir's flock on owner.flock, the way limit_switch takes limit-switch.lock: the
kernel frees it when its holder exits, so it has no age rule.
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
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG",
             "FACTORY_RUNS_ROOT", "CLAUDE_ACCOUNTS_DIR", "CLAUDE_SETTINGS_FILE")
FAKE = """#!/usr/bin/env bash
d=$FAKE_ACCOUNTS; a=$(cat "$d/active")
case $1 in
  status) echo "active: $a; stored: a b" ;;
  other) if [ "$a" = a ]; then echo b; else echo a; fi ;;
  use) sleep "${FAKE_USE_SLEEP:-0}"; echo "$a $2" >> "$d/switches"; echo "$2" > "$d/active" ;;
esac
"""


class LimitSwitchTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.home = self.top / "home"
        (self.home / "bin").mkdir(parents=True)
        fake = self.home / "bin" / "claude-account"
        fake.write_text(FAKE)
        fake.chmod(0o755)
        self.acc = self.top / "accounts"
        self.acc.mkdir()
        (self.acc / "active").write_text("a\n")
        self.runs = self.top / "runs"

    def limited(self, issue: str, account: str, *, use_sleep: float = 0) -> subprocess.Popen[str]:
        run = self.runs / issue / "0000aaaa"
        run.mkdir(parents=True, exist_ok=True)
        (run / "launched").write_text(f"{int(time.time())}\n")
        result = run / "result.json"
        result.write_text(json.dumps({"is_error": True, "result": "You've hit your session limit - resets 3am (UTC)"}))
        script = (f". bin/factory\nROOT='{self.home}'; RUN='{run}'; LOG=/dev/null; LEDGER='{run}/ledger.jsonl'\n"
                  f"MAX_HOURS=48; CALL_ACCOUNT={account}\n"
                  "set_status() { :; }; log() { :; }\n"
                  "sleep() { if [ \"$1\" -gt 60 ]; then echo slept; else command sleep \"$1\"; fi; }\n"
                  f"limit_wait '{result}' && echo returned")
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        env = {**base, "FACTORY_SOURCED": "1", "FACTORY_RUNS_ROOT": str(self.runs), "FAKE_ACCOUNTS": str(self.acc),
               "FAKE_USE_SLEEP": str(use_sleep)}
        return subprocess.Popen(["bash", "-c", script], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def outcome(self, proc: subprocess.Popen[str]) -> str:
        out, err = proc.communicate(timeout=60)
        self.assertTrue(out.strip().endswith("returned"), out + err)
        return "slept" if "slept" in out else "retried"

    def switches(self) -> list[str]:
        f = self.acc / "switches"
        return f.read_text().splitlines() if f.exists() else []

    def active(self) -> str:
        return (self.acc / "active").read_text().strip()

    def test_two_runs_limited_on_one_account_switch_once(self) -> None:
        self.assertEqual(self.outcome(self.limited("1", "a")), "retried")
        self.assertEqual(self.outcome(self.limited("2", "a")), "retried")
        self.assertEqual(self.switches(), ["a b"])
        self.assertEqual(self.active(), "b")

    def test_limited_on_the_new_account_within_the_cooldown_sleeps(self) -> None:
        self.assertEqual(self.outcome(self.limited("1", "a")), "retried")
        self.assertEqual(self.outcome(self.limited("2", "b")), "slept")
        self.assertEqual(self.switches(), ["a b"])
        self.assertEqual(self.active(), "b")

    def test_limited_on_the_new_account_after_the_cooldown_switches_back(self) -> None:
        self.assertEqual(self.outcome(self.limited("1", "a")), "retried")
        (self.runs / "limit-switch").write_text(f"{int(time.time()) - 301}\n")
        self.assertEqual(self.outcome(self.limited("2", "b")), "retried")
        self.assertEqual(self.switches(), ["a b", "b a"])

    def test_two_runs_limited_at_once_switch_once(self) -> None:
        procs = [self.limited(issue, "a", use_sleep=1) for issue in ("1", "2")]
        self.assertEqual([self.outcome(p) for p in procs], ["retried", "retried"])
        self.assertEqual(self.switches(), ["a b"])
        self.assertEqual(self.active(), "b")
        self.assertFalse((self.runs / "limit-switch.d").exists())


class OwnerLockTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.run_dir = self.top / "run"
        self.run_dir.mkdir()

    def sourced(self, script: str) -> list[str]:
        return ["bash", "-c", f". bin/factory\n{script}", "_", str(self.run_dir), str(self.top / "ready")]

    def env(self) -> dict[str, str]:
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        return {**base, "FACTORY_SOURCED": "1", "FACTORY_RUNS_ROOT": str(self.top / "runs")}

    def holder(self, script: str) -> subprocess.Popen[bytes]:
        # Takes owner_lock with one try, runs script, touches $2, then sleeps, so the lock stays as script left it.
        p = subprocess.Popen(self.sourced(f'owner_lock "$1" 1 || exit 1; {script}; touch "$2"; exec sleep 60'),
                             cwd=ROOT, env=self.env(), stdin=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(p.wait)
        self.addCleanup(lambda: subprocess.run(["pkill", "-KILL", "-g", str(p.pid)], check=False))
        for _ in range(100):
            if (self.top / "ready").exists():
                break
            self.assertIsNone(p.poll(), "the holder could not take owner_lock")
            time.sleep(0.05)
        else:
            self.fail("the holder never took owner_lock")
        return p

    def try_lock(self) -> str:
        proc = subprocess.run(self.sourced('owner_lock "$1" 1 && echo got || echo busy'), cwd=ROOT, env=self.env(),
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False, timeout=30)
        return proc.stdout.strip()

    def test_a_live_holder_keeps_the_lock_however_old_it_looks(self) -> None:
        self.holder(":")
        old = time.time() - 300
        for f in (self.run_dir, *self.run_dir.iterdir()):
            os.utime(f, (old, old))
        self.assertEqual(self.try_lock(), "busy")

    def test_a_killed_holder_frees_the_lock_at_once(self) -> None:
        p = self.holder(":")
        self.assertEqual(self.try_lock(), "busy")
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
        self.assertEqual(self.try_lock(), "got")

    def test_owner_unlock_frees_the_lock_while_the_holder_lives(self) -> None:
        p = self.holder('owner_unlock "$1"')
        self.assertIsNone(p.poll())
        self.assertEqual(self.try_lock(), "got")

    def test_a_waiting_caller_gets_the_lock_once_the_holder_exits(self) -> None:
        p = self.holder(":")
        waiter = subprocess.Popen(self.sourced('owner_lock "$1" 20 && echo got || echo busy'), cwd=ROOT, env=self.env(),
                                  stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, text=True)
        time.sleep(1)
        self.assertIsNone(waiter.poll(), "the waiter took a held lock")
        os.killpg(p.pid, signal.SIGKILL)
        out, _ = waiter.communicate(timeout=30)
        self.assertEqual(out.strip(), "got")

    def test_the_old_mkdir_path_stays_free(self) -> None:
        # A relaunch of a run frozen before owner.flock runs its copy's owner_lock, a mkdir of owner.lock.
        self.holder(":")
        self.assertFalse((self.run_dir / "owner.lock").exists())
        self.assertTrue((self.run_dir / "owner.flock").is_file())

    def test_an_old_owner_lock_held_by_a_frozen_run_is_left_alone(self) -> None:
        # A frozen copy's owner.lock is an empty directory, held while it exists; owner_lock, owner_unlock and
        # env_park_alert, which takes and drops owner.flock, must leave it there and empty. Empty, as the old mkdir lock
        # is, so an `rmdir owner.lock` left in any of them would remove it and fail here.
        old = self.run_dir / "owner.lock"
        old.mkdir()
        proc = subprocess.run(self.sourced('owner_lock "$1" 1 && owner_unlock "$1" && env_park_alert "$1" 7'), cwd=ROOT,
                              env=self.env(), stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
                              timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(old.is_dir())
        self.assertEqual(list(old.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
