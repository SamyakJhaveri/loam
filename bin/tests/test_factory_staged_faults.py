"""Staged faults: the failures that cost real runs, played through the real supervisor (lean plan S3-05).

Each test launches a ticket with `bin/factory next` on test_factory_e2e.py's harness (a scratch HOME, so bin/alert finds
no webhook and only logs to the scratch alerts.jsonl; the scripted claude, gh and tmux stand-ins) and stages one fault:
  - the worker's call answers with the real weekly usage-limit reply: the run waits and retries the same call, and
    the reply is not a round and not a stop;
  - the pane's process group gets the hangup that `tmux kill-session` sends while the worker call runs: the run ends
    stopped-killed with one fail alert, and the call's processes, in a session of their own, go too;
  - the supervisor is killed (`kill <pid>`) while it waits out a usage limit: it ends at once, not when the wait would
    end, with one fail alert, and leaves no sleep holding the run's lease.
A `sleep` stand-in, first on PATH for the run, turns the long limit wait (600 s or more) into one that ends when the
test writes $E2E_STATE/wake, and writes each such wait's seconds and pid to $E2E_STATE/long-sleeps once it runs;
shorter sleeps are real.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import signal
import time

import test_factory_e2e as e2e

FAULT_DEADLINE_SEC = 30  # the killed paths take seconds (call_abort's grace is 5 s); this only turns a hang into a fail
SLEEP = """#!/bin/sh
case "$1" in
  [0-9]*) if [ "${1%%[!0-9]*}" -ge 600 ]; then
            echo "$1 $$" >> "$E2E_STATE/long-sleeps"
            while [ ! -e "$E2E_STATE/wake" ]; do REAL_SLEEP 0.1; done
            exit 0
          fi ;;
esac
exec REAL_SLEEP "$@"
"""


class StagedFaultTests(e2e.E2EHarness):
    def setUp(self) -> None:
        super().setUp()
        shim = self.top / "shim"
        shim.mkdir()
        real = shutil.which("sleep")
        self.assertIsNotNone(real)
        (shim / "sleep").write_text(SLEEP.replace("REAL_SLEEP", str(real)), encoding="utf-8")
        (shim / "sleep").chmod(0o755)
        self.env["PATH"] = f"{shim}{os.pathsep}{self.env['PATH']}"

    def launch(self, scenario: str) -> pathlib.Path:
        self.seed((1, e2e.ticket(scenario)))
        t = self.tick()
        self.assertEqual(t.stdout, "launched #1\n", t.stderr)
        deadline = time.monotonic() + e2e.RUN_DEADLINE_SEC
        while not list((self.runs / "1").glob("*/owner")):
            if time.monotonic() > deadline:
                self.fail(f"#1's run wrote no owner\n{self.diag(1)}")
            time.sleep(0.1)
        return self.run_dir(1)

    def wait_status(self, run: pathlib.Path, want: str) -> None:
        deadline = time.monotonic() + e2e.RUN_DEADLINE_SEC
        while (status := self.read(run / "status").strip() if (run / "status").exists() else "") != want:
            if not self.alive(self.owner(run)) or time.monotonic() > deadline:
                self.fail(f"#1's status is {status!r}, never {want!r}\n{self.diag(1)}")
            time.sleep(0.1)

    def wait_long_sleep(self, run: pathlib.Path) -> int:
        """The pid of the limit wait's sleep stand-in, once it runs: the status is written before the sleep starts."""
        deadline = time.monotonic() + e2e.RUN_DEADLINE_SEC
        log = self.state / "long-sleeps"
        while not (log.exists() and (text := self.read(log)).endswith("\n")):
            if not self.alive(self.owner(run)) or time.monotonic() > deadline:
                self.fail(f"#1's limit wait started no long sleep\n{self.diag(1)}")
            time.sleep(0.1)
        lines = text.splitlines()
        self.assertEqual(len(lines), 1, lines)
        return int(lines[0].split()[1])

    def owner(self, run: pathlib.Path) -> int:
        return int(self.read(run / "owner").split()[0])

    def alive(self, pid: int) -> bool:
        return e2e.start_time(pid) is not None

    def wait_gone(self, pid: int) -> None:
        deadline = time.monotonic() + FAULT_DEADLINE_SEC
        while self.alive(pid):
            if time.monotonic() > deadline:
                self.fail(f"the supervisor {pid} still runs {FAULT_DEADLINE_SEC}s after the fault\n{self.diag(1)}")
            time.sleep(0.1)

    def fail_alerts(self) -> list[dict]:
        log = pathlib.Path(self.env["HOME"]) / ".local/state/loam/alerts.jsonl"
        rows = [json.loads(x) for x in self.read(log).splitlines()] if log.exists() else []
        return [r for r in rows if r["level"] == "fail"]

    def assert_killed_once(self, run: pathlib.Path, sig: str) -> None:
        self.assertEqual(self.read(run / "status").strip(), "stopped-killed", self.diag(1))
        alerts = self.fail_alerts()
        self.assertEqual(len(alerts), 1, alerts)
        self.assertEqual((alerts[0]["source"], alerts[0]["run"]), ("factory", "issue 1"))
        self.assertIn(sig, alerts[0]["text"])
        self.assertIn("EXIT stopped-killed", self.read(run / "factory.log"))
        self.assertEqual(self.calls("unknown"), [])

    def test_the_real_usage_limit_reply_waits_and_retries_the_same_call(self) -> None:
        run = self.launch("limit")
        self.wait_status(run, "waiting-limit")
        self.wait_long_sleep(run)
        log = self.read(run / "factory.log")
        # limit_wait parses only a same-day reset ("resets 1:30pm"), so this weekly reply's "resets Nov 13, 5am" falls
        # back to the 20-minute wait and retries; parsing the date is a follow-up, and this pins today's behavior.
        self.assertIn("usage limit, not a round: You've hit your weekly limit · resets Nov 13, 5am "
                      "(America/Los_Angeles); waiting 1200s", log)
        self.assertNotIn("failed before doing work", log)
        (self.state / "wake").touch()
        self.assertEqual(self.wait_run(1), "pr-opened", self.diag(1))
        # Two worker calls, both round 1: the limited call is retried, not graded, booked or counted as a round.
        self.assertEqual(self.workers(), 2)
        self.assertEqual(self.last_round(run), 1)
        self.assertEqual([(r["role"], r["subtype"]) for r in self.ledger(run)],
                         [("worker", "success"), ("judge", "success"), ("reviewer", "success")])
        self.assertEqual(self.fail_alerts(), [])

    def test_a_killed_pane_ends_the_run_and_its_call_with_one_alert(self) -> None:
        run = self.launch("hang")
        self.wait_started(1)
        call_group = int(self.read(run / "call.group").split()[0])
        supervisor, pane = self.owner(run), self.session(1)["pid"]
        os.killpg(pane, signal.SIGHUP)  # the pane's terminal closing hangs up its process group
        self.wait_gone(supervisor)
        self.assert_killed_once(run, "SIGHUP")
        with self.assertRaises(ProcessLookupError, msg="the worker call's processes outlived the killed run"):
            os.killpg(call_group, 0)

    def test_a_supervisor_killed_in_a_limit_wait_ends_at_once(self) -> None:
        run = self.launch("limit")
        self.wait_status(run, "waiting-limit")
        sleep = self.wait_long_sleep(run)
        self.assertTrue(self.alive(sleep), "the limit wait's sleep ended before the supervisor was killed")
        supervisor = self.owner(run)
        os.kill(supervisor, signal.SIGTERM)
        self.wait_gone(supervisor)
        self.assert_killed_once(run, "SIGTERM")
        tag = f"E2E_STATE={self.state}".encode()
        sleeps = []
        for f in pathlib.Path("/proc").glob("[0-9]*"):
            try:
                if tag in (f / "environ").read_bytes().split(b"\0") and b"/shim/sleep" in (f / "cmdline").read_bytes():
                    sleeps.append(f.name)
            except OSError:
                continue
        self.assertEqual(sleeps, [], "the limit wait's sleep outlived its supervisor and holds the run's lease")


if __name__ == "__main__":
    import unittest

    unittest.main()
