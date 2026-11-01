"""A `bin/factory next` tick that completes beats the host's healthchecks check; one that refuses does not.

The last run of the day used to pause the check, so the check heard nothing while the cron tick refused for
hours on a precondition (1 Nov 2026). Now every real tick that returns 0 beats, which also resumes a paused
check, a refusing tick stays silent, and no run pauses it, so the check goes red after its grace.

`bin/factory` is sourced (FACTORY_SOURCED=1); `alert` records its arguments, and gh, git, the gates and the
probes are shell functions. No network, no tmux, no `claude`.
"""

from __future__ import annotations

import os
import pathlib
import signal
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

# A tick with an empty frontier: every gate passes, the pull is refused (git prints no branch), gh lists nothing.
STUBS = ("assert_target_ready() { :; }; claude_logged_in() { :; }; claude_version_ok() { :; }; "
         "pr_closed_events() { :; }; target_repo() { echo o/r; }; git() { :; }; gh() { :; }; "
         'alert() { echo "$*" >> "$ALERTS"; }; ')


class NextBeatTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs = pathlib.Path(tmp.name) / "runs"
        self.runs.mkdir()
        self.alerts = pathlib.Path(tmp.name) / "alerts"
        self.alerts.touch()

    def tick(self, pre: str = "", *flags: str) -> tuple[subprocess.CompletedProcess[str], list[str]]:
        proc = subprocess.run(
            ["bash", "-c", f". bin/factory\n{STUBS}{pre}cmd_next {' '.join(flags)}"],
            cwd=ROOT, capture_output=True, text=True, check=False,
            env={**os.environ, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), "FACTORY_MAX_PARALLEL": "1",
                 "FACTORY_RUNS_ROOT": str(self.runs), "ALERTS": str(self.alerts)},
        )
        return proc, self.alerts.read_text().splitlines()

    def test_a_tick_with_nothing_to_launch_beats(self) -> None:
        proc, sent = self.tick()
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "nothing to launch"), proc.stderr)
        self.assertEqual(sent, ["--ping beat"])

    def test_a_paused_timer_beats(self) -> None:
        # FACTORY_STOP is the owner's own pause of the timer, not a fault, so the check stays green.
        (self.runs / "FACTORY_STOP").touch()
        proc, sent = self.tick()
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "paused"), proc.stderr)
        self.assertEqual(sent, ["--ping beat"])

    def test_a_refusing_tick_does_not_beat(self) -> None:
        for name, pre in (("login", "claude_logged_in() { return 1; }; "),
                          ("frontier", "gh() { return 1; }; ")):
            with self.subTest(refusal=name):
                self.alerts.write_text("")
                proc, sent = self.tick(pre)
                self.assertEqual(proc.returncode, 1, proc.stderr)
                self.assertEqual(sent, [])

    def test_a_failed_beat_does_not_fail_the_tick(self) -> None:
        proc, _ = self.tick('alert() { echo "$*" >> "$ALERTS"; return 1; }; ')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("healthchecks beat failed", proc.stderr)

    def held_slot(self, status: str, owner: int | None = None) -> pathlib.Path:
        d = self.runs / "7" / "abcd1234"
        d.mkdir(parents=True)
        (d / "status").write_text(status + "\n")
        (d / "launched").write_text("1\n")
        if owner is not None:
            lstart = subprocess.run(["ps", "-o", "lstart=", "-p", str(owner)], capture_output=True, text=True,
                                    env={**os.environ, "TZ": "UTC", "LC_ALL": "C"}, check=True).stdout.strip()
            (d / "owner").write_text(f"{owner} {lstart}\n")
        return d

    def test_full_slots_held_by_a_suspended_run_do_not_beat(self) -> None:
        # A run stopped whole keeps its lease and owner, so it holds the only slot with no progress; the old run
        # heartbeat stopped with it, and now the tick refuses instead. Continued, the same slot is an idle tick again.
        sup = subprocess.Popen(["sleep", "60"], start_new_session=True)
        self.addCleanup(sup.wait)
        self.addCleanup(sup.kill)
        self.held_slot("running", sup.pid)
        os.kill(sup.pid, signal.SIGSTOP)
        for _ in range(50):
            stat = subprocess.run(["ps", "-o", "stat=", "-p", str(sup.pid)], capture_output=True, text=True).stdout
            if stat.strip().startswith("T"):
                break
            time.sleep(0.1)
        proc, sent = self.tick()
        self.assertEqual((proc.returncode, proc.stdout.strip()), (1, "nothing to launch"), proc.stderr)
        self.assertIn("is stopped (SIGSTOP or a stopped job)", proc.stderr)
        self.assertEqual(sent, [])
        os.kill(sup.pid, signal.SIGCONT)
        proc, sent = self.tick()
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "nothing to launch"), proc.stderr)
        self.assertEqual(sent, ["--ping beat"])

    def test_full_slots_held_by_a_pr_awaiting_review_beat(self) -> None:
        # A pr-opened run holds its slot while its ticket worktree stands, with no process; that is a normal wait.
        self.held_slot("pr-opened")
        checkout = self.runs.parent / "checkout"
        pathlib.Path(f"{checkout}-7").mkdir()
        proc, sent = self.tick(f"MAIN_CHECKOUT='{checkout}'; ")
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "nothing to launch"), proc.stderr)
        self.assertEqual(sent, ["--ping beat"])

    def test_dry_run_and_frontier_do_not_beat(self) -> None:
        for flag in ("--dry-run", "--frontier"):
            with self.subTest(flag=flag):
                proc, sent = self.tick("", flag)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(sent, [])


if __name__ == "__main__":
    unittest.main()
