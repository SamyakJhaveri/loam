"""holds_slot frees a running run's slot only when its supervisor is surely gone (docs/factory/LOOP.md, Parallel runs).

Each test writes a run dir with status `running` and an `owner` line, sources bin/factory (FACTORY_SOURCED=1) with
`alert` stubbed to a file, and asks holds_slot. A freed run reads stopped-environment and alerts once; a held one
keeps `running` and sends nothing.
"""

from __future__ import annotations

import datetime
import os
import pathlib
import signal
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG")
OLD = "Thu Jan  1 00:00:00 1970"


def lstart(pid: int) -> str:
    out = subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], env={**os.environ, "TZ": "UTC", "LC_ALL": "C"},
                         capture_output=True, text=True, check=True).stdout
    return out.rstrip("\n")


def dead_pid() -> int:
    p = subprocess.Popen(["true"])
    p.wait()
    return p.pid


def state(pid: int) -> str:
    try:
        return pathlib.Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except FileNotFoundError:
        return ""


def wait_until(cond) -> None:
    for _ in range(100):
        if cond():
            return
        time.sleep(0.05)
    raise AssertionError("condition never held")


class OwnerSlotTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.run_dir = self.top / "runs" / "7" / "abcd1234"
        self.run_dir.mkdir(parents=True)
        (self.run_dir / "status").write_text("running\n")
        self.alerts = self.top / "alerts.txt"

    def live(self) -> int:
        p = subprocess.Popen(["sleep", "60"])
        self.addCleanup(p.wait)
        self.addCleanup(p.kill)
        return p.pid

    def owner(self, line: str) -> None:
        (self.run_dir / "owner").write_text(line + "\n")

    def holds(self, extra: str = "") -> bool:
        script = (f". bin/factory\nRUNS_BASE='{self.top}/runs'; LOG='{self.top}/factory.log'\n"
                  f"alert() {{ printf '%s\\n' \"$*\" >> '{self.alerts}'; }}\n{extra}\n"
                  f"holds_slot '{self.run_dir}' && echo held || echo free")
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env={**base, "FACTORY_SOURCED": "1"},
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
        self.assertIn(proc.stdout.strip(), ("held", "free"), proc.stderr)
        return proc.stdout.strip() == "held"

    def assert_freed(self, extra: str = "") -> None:
        self.assertFalse(self.holds(extra))
        self.assertEqual((self.run_dir / "status").read_text(), "stopped-environment\n")
        self.assertEqual(len(self.alerts.read_text().splitlines()), 1)

    def assert_held(self, extra: str = "") -> None:
        self.assertTrue(self.holds(extra))
        self.assertEqual((self.run_dir / "status").read_text(), "running\n")
        self.assertFalse(self.alerts.exists())

    def test_dead_owner_frees_the_slot_and_reads_stopped_environment(self) -> None:
        self.owner(f"{dead_pid()} {OLD}")
        self.assert_freed()

    def test_live_pid_with_another_start_time_frees_the_slot(self) -> None:
        self.owner(f"{self.live()} {OLD}")
        self.assert_freed()

    def test_zombie_owner_frees_the_slot(self) -> None:
        p = subprocess.Popen(["true"])
        self.addCleanup(p.wait)
        wait_until(lambda: state(p.pid) == "Z")
        self.owner(f"{p.pid} {lstart(p.pid)}")
        self.assert_freed()

    def test_live_owner_holds_the_slot(self) -> None:
        pid = self.live()
        self.owner(f"{pid} {lstart(pid)}")
        self.assert_held()

    def test_live_pid_with_a_malformed_start_holds_the_slot(self) -> None:
        self.owner(f"{self.live()} garbage")
        self.assert_held()

    def test_start_time_two_seconds_off_holds_the_slot(self) -> None:
        # A wall-clock step moves ps lstart; a gap this small is the same process, not a reused pid.
        pid = self.live()
        t = datetime.datetime.strptime(lstart(pid), "%a %b %d %H:%M:%S %Y") - datetime.timedelta(seconds=2)
        self.owner(f"{pid} {t:%a %b} {t.day:2d} {t:%H:%M:%S %Y}")
        self.assert_held()

    def test_ps_failing_on_a_live_pid_holds_the_slot(self) -> None:
        pid = self.live()
        self.owner(f"{pid} {OLD}")
        for stub in ("ps() { return 1; }", "ps() { :; }"):
            with self.subTest(stub=stub):
                self.assert_held(stub)

    def test_relaunch_newer_than_a_dead_owner_holds_the_slot(self) -> None:
        self.owner(f"{dead_pid()} {OLD}")
        (self.run_dir / "launched").write_text("1\n")
        os.utime(self.run_dir / "owner", (time.time() - 60, time.time() - 60))
        self.assert_held()

    def test_dead_group_leader_holds_while_a_member_lives(self) -> None:
        # The leader exits and is reaped; the sleep it left keeps the leader's pid as its process group id.
        p = subprocess.Popen(["sh", "-c", "sleep 60 & exit 0"], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p.wait()
        self.addCleanup(lambda: subprocess.run(["pkill", "-KILL", "-g", str(p.pid)], check=False))
        self.owner(f"{p.pid} {OLD}")
        self.assert_held()
        os.killpg(p.pid, signal.SIGKILL)
        wait_until(lambda: not self.holds())
        self.assertEqual((self.run_dir / "status").read_text(), "stopped-environment\n")
        self.assertEqual(len(self.alerts.read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
