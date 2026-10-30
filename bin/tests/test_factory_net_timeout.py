"""A gh call cut off at NET_TIMEOUT_SEC in the frozen pass ends the run it owns stopped-environment (#382).

Since #422 cmd_run writes `owner` and `running` before it execs the frozen copy, whose load_ticket reads the issue
again with FACTORY_ROOT set. Each test writes a run dir with status `running`, puts a `gh` that hangs first on PATH,
and calls load_ticket from a sourced bin/factory with FACTORY_FROZEN naming the run. When the owner line names this
process, the cut-off call ends through finish (status, alert, exit 4); when it names another, load_ticket only exits 4.
WatchdogTests check that nothing escapes the limit: a gh function exported into the environment, a program that
ignores TERM (timeout -k), and net_watch, the path without GNU timeout, on both a TERM-ignoring program and a
function that returns 0 after the deadline, a call that stops itself, a function that exits 0 on TERM (124), and a
TERM-ignoring group member that outlives the leader.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "FACTORY_FROZEN", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER",
             "REPO", "RUN", "LOG")


class NetTimeoutTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.run_dir = self.top / "runs" / "7" / "abcd1234"
        (self.run_dir / "frozen").mkdir(parents=True)
        (self.run_dir / "status").write_text("running\n")
        (self.run_dir / "frozen" / "issue.md").write_text("# Net fixture\n")
        self.alerts = self.top / "alerts.txt"
        alert = self.run_dir / "frozen" / "alert"
        alert.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" >> '{self.alerts}'\n")
        alert.chmod(0o755)
        (self.top / "bin").mkdir()
        gh = self.top / "bin" / "gh"
        gh.write_text("#!/usr/bin/env bash\nexec sleep 600\n")
        gh.chmod(0o755)

    def load(self, owner: str) -> tuple[subprocess.CompletedProcess, float]:
        script = f"printf '%s x\\n' {owner} > '{self.run_dir}/owner'\n. bin/factory\nload_ticket 7"
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        env = {**base, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), "FACTORY_RUNS_ROOT": str(self.top / "runs"),
               "FACTORY_FROZEN": str(self.run_dir / "frozen" / "factory"), "FACTORY_NET_TIMEOUT_SEC": "2",
               "PATH": f"{self.top / 'bin'}:{os.environ['PATH']}"}
        start = time.monotonic()
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, check=False, timeout=60)
        return proc, time.monotonic() - start

    def test_owned_run_ends_stopped_environment(self) -> None:
        proc, took = self.load('"$$"')
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertLess(took, 30)
        self.assertEqual((self.run_dir / "status").read_text().strip(), "stopped-environment")
        alerts = self.alerts.read_text()
        self.assertIn("stopped on a machine or tool problem", alerts)
        self.assertIn("gh issue view #7", alerts)
        self.assertIn("EXIT stopped-environment (4): gh issue view #7", (self.run_dir / "factory.log").read_text())

    def test_run_owned_by_another_process_is_left_alone(self) -> None:
        proc, took = self.load("1")
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertLess(took, 30)
        self.assertIn("could not read issue #7", proc.stderr)
        self.assertEqual((self.run_dir / "status").read_text().strip(), "running")
        self.assertFalse(self.alerts.exists())


class WatchdogTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)

    def bash(self, script: str, **extra: str) -> tuple[subprocess.CompletedProcess, float]:
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        env = {**base, "FACTORY_RUNS_ROOT": str(self.top / "runs"), "FACTORY_NET_TIMEOUT_SEC": "1", **extra}
        start = time.monotonic()
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, check=False, timeout=60)
        return proc, time.monotonic() - start

    def test_exported_gh_function_is_cut_off(self) -> None:
        proc, took = self.bash("gh() { sleep 30; return 0; }; export -f gh; bin/factory lint 7")
        self.assertNotEqual(proc.returncode, 0, proc.stderr)
        self.assertLess(took, 8)
        self.assertIn("could not read the issue body with gh", proc.stderr)

    def test_program_ignoring_term_is_killed(self) -> None:
        (self.top / "bin").mkdir()
        gh = self.top / "bin" / "gh"
        gh.write_text("#!/usr/bin/env bash\ntrap '' TERM\nexec sleep 600\n")
        gh.chmod(0o755)
        proc, took = self.bash(". bin/factory; net gh issue view 7", FACTORY_SOURCED="1",
                               PATH=f"{self.top / 'bin'}:{os.environ['PATH']}")
        self.assertNotEqual(proc.returncode, 0, proc.stderr)
        self.assertLess(took, 15)

    def test_watchdog_without_timeout(self) -> None:
        ignore = "python3 -c 'import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(600)'"
        proc, took = self.bash(f". bin/factory; net_watch {ignore}", FACTORY_SOURCED="1")
        self.assertNotEqual(proc.returncode, 0, proc.stderr)
        self.assertLess(took, 15)
        proc, took = self.bash(". bin/factory; late() { sleep 30; echo late; return 0; }; out=$(net_watch late); "
                               "rc=$?; printf '%s %s' \"$rc\" \"$out\"", FACTORY_SOURCED="1")
        self.assertLess(took, 8)
        self.assertNotEqual(proc.stdout.split()[0], "0", proc.stdout)
        self.assertNotIn("late", proc.stdout)
        proc, took = self.bash(". bin/factory; out=$(net_watch bash -c 'kill -STOP $$; echo x'); echo \"rc=$? $out\"",
                               FACTORY_SOURCED="1")
        self.assertLess(took, 10)  # TERM and CONT end it at ~1 s, the KILL fallback at ~6 s; with no watchdog it hangs
        self.assertNotIn("rc=0", proc.stdout)
        self.assertNotIn("x", proc.stdout)
        proc, _ = self.bash(". bin/factory; f() { cat; echo err >&2; return 3; }; printf 'in\\n' | net_watch f; "
                            "echo \"rc=$?\"", FACTORY_SOURCED="1")
        self.assertEqual((proc.stdout, proc.stderr), ("in\nrc=3\n", "err\n"))

    def test_watchdog_call_exiting_zero_on_term_is_late(self) -> None:
        proc, took = self.bash(". bin/factory; f() { trap 'exit 0' TERM; sleep 30; }; net_watch f; echo \"rc=$?\"",
                               FACTORY_SOURCED="1")
        self.assertLess(took, 15)
        self.assertIn("rc=124", proc.stdout)

    def test_watchdog_kills_group_member_outliving_leader(self) -> None:
        proc, took = self.bash(". bin/factory; g() { bash -c 'trap \"\" TERM; sleep 20' & sleep 30; }; "
                               "out=$(net_watch g); echo \"rc=$?\"", FACTORY_SOURCED="1")
        self.assertLess(took, 15)
        self.assertIn("rc=124", proc.stdout)


if __name__ == "__main__":
    unittest.main()
