"""Two runs on one host share the Claude account, so a usage-limit switch must not undo another run's switch.

Each case sources bin/factory (FACTORY_SOURCED=1) in its own run dir under one runs root, with ROOT pointed at a
temp home whose bin/claude-account is a fake: it keeps the active name in a file, stores accounts a and b, and
appends `<from> <to>` to `switches` on each `use`. CALL_ACCOUNT names the account the limited call ran under, as
the call sites record it, and limit_wait gets a usage-limit reply; sleep is stubbed, so a run either retries at
once or reports the sleep. The host-wide cooldown is the epoch second in <runs root>/limit-switch.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
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
                  "set_status() { :; }; log() { :; }; sleep() { echo slept; }\n"
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

    @unittest.skipUnless(shutil.which("flock"), "the host-wide lock needs flock(1); a Mac has none")
    def test_two_runs_limited_at_once_switch_once(self) -> None:
        procs = [self.limited(issue, "a", use_sleep=1) for issue in ("1", "2")]
        self.assertEqual([self.outcome(p) for p in procs], ["retried", "retried"])
        self.assertEqual(self.switches(), ["a b"])
        self.assertEqual(self.active(), "b")


if __name__ == "__main__":
    unittest.main()
