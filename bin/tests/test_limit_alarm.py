"""bin/limit-alarm keeps the distbench lead on an account with usage, and the account is the host's: factory runs and the
overnight driver switch it too (#600). So limit-alarm books a lead limit against the account the lead runs on ($S/lead),
not the active one, and switches only through `bin/claude-account switch`, which holds the factory's host-wide lock and
five-minute cooldown and switches nothing once the host has left the account being switched from.

Each case runs the real bin/limit-alarm and the real bin/claude-account in a scratch HOME, with stand-in tmux (it logs
its arguments) and sleep: only the loop's `sleep 60` counts, the first runs HOOK (another caller acting between two
passes), the third ends limit-alarm, so the pass that sees the limit and the pass after it both run. The factory's
switch is bin/factory's own limit_switch, sourced, so the lock and cooldown files are the ones the factory writes.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOKEN = "CLAUDE_CODE_OAUTH_TOKEN"  # by name, so no token assignment appears for the merge secret grep
# limit-alarm runs only on jhaveris: it uses tac, date -d and stat -c, and claude-account switch uses flock(1).
LINUX_ONLY = unittest.skipUnless(sys.platform.startswith("linux"), "limit-alarm needs flock(1), tac and GNU date -d")
INHERITED = ("FACTORY_RUNS_ROOT", "CLAUDE_ACCOUNTS_DIR", "CLAUDE_SETTINGS_FILE", "FACTORY_SOURCED", "FACTORY_ROOT",
             "CALL_ACCOUNT", "T", "S", "PROJ", "ALERT", "LAUNCH", "STOPF", "PAIR", "ORDER", "HOLD_S", "IDLE_S", "BOOT_S",
             "BACK", "HOOK", "H", "W", "L", "LOG", "LEDGER", "RUN", "REPO")
TMUX = """#!/bin/bash
[ "$1" = display ] && echo 999999
echo "$*" >> "$H/tmux.log"
case "$*" in *--resume*) cat "$CLAUDE_ACCOUNTS_DIR/active" >> "$H/launched-on" ;; esac
exit 0
"""
# HOOK2 runs once, on restart's `sleep 2` before the launch keys, in the background with limit-alarm's fds closed (an
# inherited lock fd would hold the lock for it); the stand-in waits up to 3 s for it to finish.
SLEEP = """#!/bin/bash
if [ "$1" = 2 ] && [ -n "${HOOK2-}" ] && [ ! -e "$H/hook2" ]; then
  touch "$H/hook2"
  ( for p in /proc/$BASHPID/fd/*; do n=${p##*/}; [ "$n" -gt 2 ] && eval "exec $n>&-"; done
    eval "$HOOK2"; touch "$H/moved" ) > /dev/null 2>&1 &
  for _ in $(seq 30); do [ -e "$H/moved" ] && break; /bin/sleep 0.1; done
  exit 0
fi
[ "$1" = 60 ] || exit 0
n=$(( $(cat "$H/n" 2> /dev/null || echo 0) + 1 )); echo "$n" > "$H/n"
[ "$n" = 1 ] && { eval "$HOOK"; exit 0; }
[ "$n" -ge 3 ] && kill -TERM "$PPID"
exit 0
"""
LIMIT = json.dumps({"type": "assistant", "uuid": "u1", "sessionId": "s1", "isApiErrorMessage": True,
                    "message": {"content": [{"type": "text", "text": "You've hit your session limit - resets 6am"}]}},
                   separators=(",", ":"))  # limit-alarm greps the compact '"type":"assistant"' of a transcript
WRITE_LIMIT = 'printf "%s\\n" "$L" > "$H/proj/t.jsonl"'
STAMP = 'cp "$FACTORY_RUNS_ROOT/limit-switch" "$H/stamp"'  # the factory's cooldown stamp, kept to compare later
FACTORY_SWITCH = ('FACTORY_SOURCED=1 FACTORY_ROOT="$W" CALL_ACCOUNT=a bash -c ". \\"$W/bin/factory\\"; LOG=/dev/null; '
                  'LEDGER=/dev/null; limit_switch" > /dev/null 2>&1')


def write_exec(path: pathlib.Path, text: str) -> None:
    path.write_text(text)
    path.chmod(0o755)


class Host(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.h = pathlib.Path(tmp.name)
        for d in (".local/bin", "acc", "proj", "s"):
            (self.h / d).mkdir(parents=True)
        # A stale token left in the settings file by a pre-#644 `use`, which the first switch must drop (#644).
        (self.h / "settings.json").write_text(json.dumps({"env": {TOKEN: "sk-ant-oat01-fake-a", "KEEP": "1"}}) + "\n")
        self.accounts("a", "b")
        (self.h / "acc" / "active").write_text("a\n")
        (self.h / "s" / "lead").write_text("a\n")
        self.base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        self.base.update(HOME=str(self.h), H=str(self.h), W=str(ROOT), L=LIMIT,
                         CLAUDE_ACCOUNTS_DIR=str(self.h / "acc"), CLAUDE_SETTINGS_FILE=str(self.h / "settings.json"),
                         FACTORY_RUNS_ROOT=str(self.h / "runs"))

    def accounts(self, *names: str) -> None:
        for n in names:
            (self.h / "acc" / f"{n}.token").write_text(f"sk-ant-oat01-fake-{n}\n")

    def read(self, rel: str) -> str:
        p = self.h / rel
        return p.read_text().strip() if p.exists() else ""

    def active(self) -> str:
        return self.read("acc/active")

    def token(self) -> str:
        """The settings file's token, which `use` drops: calls get theirs from `claude-account exec` (#644)."""
        return json.loads((self.h / "settings.json").read_text()).get("env", {}).get(TOKEN, "")


@LINUX_ONLY
class LimitAlarmTests(Host):
    def setUp(self) -> None:
        super().setUp()
        (self.h / ".local/bin/claude-account").symlink_to(ROOT / "bin" / "claude-account")
        write_exec(self.h / ".local/bin/tmux", TMUX)
        write_exec(self.h / ".local/bin/sleep", SLEEP)
        (self.h / "runs").mkdir()

    def alarm(self, hook: str, order: str = "a b", **extra: str) -> int:
        (self.h / "n").unlink(missing_ok=True)
        env = {**self.base, "HOOK": hook, "T": "fake", "S": str(self.h / "s"), "PROJ": str(self.h / "proj"),
               "ALERT": "true", "LAUNCH": "launch", "STOPF": str(self.h / "STOP"), "PAIR": str(self.h / "pair.json"),
               "ORDER": order, "BOOT_S": "0", "BACK": "0", **extra}
        with open(self.h / "out", "a") as out:
            return subprocess.run(["timeout", "90", "bash", "bin/limit-alarm"], cwd=ROOT, env=env,
                                  stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT).returncode

    def until(self, account: str) -> int:
        return int(self.read(f"s/{account}.until") or 0)

    def tmux_count(self, prefix: str) -> int:
        return sum(1 for line in self.read("tmux.log").splitlines() if line.startswith(prefix))

    def restarts(self) -> int:
        return sum(1 for line in self.read("tmux.log").splitlines() if "--resume s1" in line)

    def log(self) -> str:
        return self.read("out")

    def test_factory_switch_kept_and_next_limit_booked_on_new_account(self) -> None:
        now = int(time.time())
        self.alarm(f'{FACTORY_SWITCH} && [ "$(cat "$CLAUDE_ACCOUNTS_DIR/active")" = b ] && {STAMP} && {WRITE_LIMIT}')
        self.assertEqual(self.active(), "b", self.log())
        self.assertNotEqual(self.read("stamp"), "")
        self.assertEqual(self.read("runs/limit-switch"), self.read("stamp"), "limit-alarm adopted b, not switched")
        self.assertGreater(self.until("a"), now)
        self.assertEqual(self.read("s/b.until"), "")
        self.assertEqual((self.restarts(), self.tmux_count("paste-buffer")), (1, 1), self.log())
        self.assertEqual(self.read("s/lead"), "b")
        (self.h / "proj" / "t.jsonl").write_text(LIMIT.replace("u1", "u2") + "\n")
        self.alarm(":")
        self.assertGreater(self.until("b"), now, self.log())

    def test_cooldown_honored(self) -> None:
        self.alarm(f'date +%s > "$FACTORY_RUNS_ROOT/limit-switch"; {WRITE_LIMIT}')
        self.assertEqual(self.active(), "a", self.log())
        self.assertEqual(self.restarts(), 0)

    def test_waits_for_lock_then_switches(self) -> None:
        hold = ('flock "$FACTORY_RUNS_ROOT/limit-switch.lock" bash -c "touch $H/held; /bin/sleep 4; '
                'cat $CLAUDE_ACCOUNTS_DIR/active > $H/at-release" > /dev/null 2>&1 & '
                'for i in $(seq 50); do [ -e "$H/held" ] && break; /bin/sleep 0.1; done')
        self.alarm(f"{hold}; {WRITE_LIMIT}")
        self.assertEqual(self.read("at-release"), "a")
        self.assertEqual(self.active(), "b", self.log())

    def test_restarted_alarm_keeps_lead_account(self) -> None:
        self.alarm('kill -TERM "$PPID"')
        subprocess.run(["bash", "-c", '. bin/factory; LOG=/dev/null; LEDGER=/dev/null; limit_switch'], cwd=ROOT,
                       env={**self.base, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), "CALL_ACCOUNT": "a"},
                       stdin=subprocess.DEVNULL, capture_output=True, check=True)
        self.assertEqual(self.active(), "b")
        stamp = self.read("runs/limit-switch")
        self.alarm(WRITE_LIMIT)
        self.assertEqual(self.active(), "b", self.log())
        self.assertEqual(self.read("runs/limit-switch"), stamp, "limit-alarm adopted b, not switched")
        self.assertEqual(self.read("s/b.until"), "")
        self.assertEqual(self.read("s/lead"), "b")

    def test_host_moved_to_limited_account_switches_on_from_it(self) -> None:
        self.accounts("c")
        (self.h / "s" / "b.until").write_text(f"{int(time.time()) + 7200}\n")
        self.alarm(f'"$W/bin/claude-account" use b > /dev/null 2>&1; {WRITE_LIMIT}', order="a b c")
        self.assertEqual(self.active(), "c", self.log())
        self.assertGreaterEqual(self.restarts(), 1)
        self.assertEqual(self.read("s/lead"), "c")

    def test_host_moved_while_waiting_on_lock_restarts_nothing(self) -> None:
        self.accounts("c")
        (self.h / "s" / "b.until").write_text(f"{int(time.time()) + 7200}\n")
        hold = ('flock "$FACTORY_RUNS_ROOT/limit-switch.lock" bash -c "touch $H/held; /bin/sleep 4; '
                '$W/bin/claude-account use b; date +%s > $FACTORY_RUNS_ROOT/limit-switch; touch $H/released" '
                '> /dev/null 2>&1 & for i in $(seq 50); do [ -e "$H/held" ] && break; /bin/sleep 0.1; done')
        self.alarm(f"{hold}; {WRITE_LIMIT}", order="a b c")
        self.assertEqual(self.active(), "b", self.log())
        self.assertEqual(self.restarts(), 0, self.log())
        self.assertEqual((self.read("s/switched"), self.read("s/lead")), ("", "a"))

    def test_host_moved_during_restart_lead_launches_on_recorded_account(self) -> None:
        self.accounts("c")
        (self.h / "acc" / "active").write_text("b\n")
        (self.h / "s" / "c.until").write_text(f"{int(time.time()) + 7200}\n")
        self.alarm(WRITE_LIMIT, order="a b c", HOOK2=FACTORY_SWITCH.replace("CALL_ACCOUNT=a", "CALL_ACCOUNT=b"))
        self.assertEqual((self.read("launched-on"), self.read("s/lead")), ("b", "b"), self.log())
        for _ in range(100):  # the factory's switch goes through once limit-alarm releases the lock
            if (self.h / "moved").exists():
                break
            time.sleep(0.1)
        self.assertEqual(self.active(), "c", self.log())

    def test_lead_reset_with_host_on_limited_account_moves_host_back_without_restart(self) -> None:
        self.accounts("c")
        (self.h / "acc" / "active").write_text("b\n")
        (self.h / "s" / "b.until").write_text(f"{int(time.time()) + 7200}\n")
        (self.h / "s" / "seen").write_text("u1\n")  # the lead's old limit line, already booked and since reset
        (self.h / "proj" / "t.jsonl").write_text(LIMIT + "\n")
        self.alarm(":", order="a b c")
        self.assertEqual(self.active(), "a", self.log())
        self.assertEqual((self.restarts(), self.tmux_count("paste-buffer")), (0, 1), self.log())
        self.assertEqual(self.read("s/lead"), "a")

    def test_refuses_to_arm_without_lead_account(self) -> None:
        (self.h / "s" / "lead").unlink()
        self.assertEqual(self.alarm(":"), 1)
        self.assertIn(str(self.h / "s" / "lead"), self.log())
        self.assertFalse((self.h / "s" / "lead").exists())
        self.assertEqual(self.active(), "a")
        (self.h / "s" / "lead").write_text("zz\n")  # names no stored account
        self.assertEqual(self.alarm(":"), 1)
        self.assertEqual(self.active(), "a")


@LINUX_ONLY
class SwitchTests(Host):
    def switch(self, *args: str) -> subprocess.Popen[str]:
        return subprocess.Popen([str(ROOT / "bin" / "claude-account"), "switch", *args], env=self.base,
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    def code(self, *args: str) -> int:
        p = self.switch(*args)
        out, _ = p.communicate(timeout=90)
        self.assertNotIn("sk-ant-oat01", out)
        return p.returncode

    def stamp(self, value: int) -> None:
        (self.h / "runs" / "limit-switch").write_text(f"{value}\n")

    def test_protocol(self) -> None:
        self.assertEqual(self.code(), 2)
        self.assertEqual(self.code("a"), 0)
        self.assertEqual((self.active(), self.token()), ("b", ""))
        self.assertEqual(json.loads((self.h / "settings.json").read_text())["env"], {"KEEP": "1"})
        self.assertRegex(self.read("runs/limit-switch"), r"^[0-9]+$")
        self.stamp(1)
        self.assertEqual(self.code("a"), 0, "a stale <from> switches nothing")
        self.assertEqual((self.active(), self.read("runs/limit-switch")), ("b", "1"))
        self.stamp(int(time.time()))
        self.assertEqual(self.code("b"), 3, "inside the cooldown")
        self.assertEqual(self.active(), "b")
        self.stamp(int(time.time()) - 301)
        self.assertEqual(self.code("b"), 0)
        self.assertEqual((self.active(), self.token()), ("a", ""))
        self.stamp(1)
        self.assertEqual(self.code("a", "c"), 1, "no stored token for c")
        self.assertEqual((self.active(), self.read("runs/limit-switch")), ("a", "1"))

    def test_waits_for_lock(self) -> None:
        (self.h / "runs").mkdir()
        holder = subprocess.Popen(["flock", str(self.h / "runs" / "limit-switch.lock"), "-c", "touch held; sleep 3"],
                                  cwd=self.h)
        self.addCleanup(holder.wait)
        while not (self.h / "held").exists():
            time.sleep(0.05)
        p = self.switch("a")
        time.sleep(1.5)
        self.assertEqual((self.active(), self.token(), self.read("runs/limit-switch")), ("a", "sk-ant-oat01-fake-a", ""))
        p.communicate(timeout=90)
        self.assertEqual(p.returncode, 0)
        self.assertEqual((self.active(), self.token()), ("b", ""))


if __name__ == "__main__":
    unittest.main()
