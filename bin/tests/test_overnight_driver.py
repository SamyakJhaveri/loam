"""The overnight driver runs from the repo (#476): bin/overnight/driver.sh starts each call with the settings.json and
protocol.md beside it, bin/overnight/watchdog.sh restarts ~/loam/bin/overnight/driver.sh, a call's settings deny it
any write to bin/overnight, and the protocol writes lessons into docs/factory/LESSONS.md on the PR branch.

The scripts run for real with HOME a temp dir whose loam/bin/overnight links to this checkout, and fake claude, gh,
tmux, pgrep, setsid, sleep and alert, so nothing reaches GitHub, Slack, tmux or a model.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import signal
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
OVERNIGHT = ROOT / "bin" / "overnight"


def write_exec(path: pathlib.Path, text: str) -> None:
    path.write_text(text)
    path.chmod(0o755)


class OvernightDriverTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = pathlib.Path(tmp.name)
        self.state = self.home / ".local/state/loam/overnight"
        self.state.mkdir(parents=True)
        (self.home / "loam/bin").mkdir(parents=True)
        (self.home / "loam/bin/overnight").symlink_to(OVERNIGHT)
        write_exec(self.home / "loam/bin/alert", "#!/bin/sh\nexit 0\n")
        self.fake = self.home / "fake"
        self.fake.mkdir()

    def env(self) -> dict[str, str]:
        return {**os.environ, "HOME": str(self.home), "PATH": f"{self.fake}:{os.environ['PATH']}"}

    def test_scripts_are_executable(self) -> None:
        for name in ("driver.sh", "watchdog.sh"):
            self.assertTrue(os.access(OVERNIGHT / name, os.X_OK), name)

    def test_settings_keep_every_rule_and_deny_writes_to_the_driver(self) -> None:
        s = json.loads((OVERNIGHT / "settings.json").read_text())
        deny = s["permissions"]["deny"]
        for rule in ("ScheduleWakeup", "CronCreate", "Bash(crontab *)", "Bash(git push origin main *)",
                     "Edit(~/loam/bin/overnight/**)", "Write(~/loam/bin/overnight/**)"):
            self.assertIn(rule, deny)
        self.assertEqual(s["sandbox"]["filesystem"]["allowWrite"], ["~/.local/state/loam"])
        self.assertEqual(s["sandbox"]["filesystem"]["denyWrite"], ["~/loam/bin/overnight"])
        self.assertEqual(s["sandbox"]["network"]["allowedDomains"], ["github.com"])

    def test_driver_call_reads_the_repo_settings_and_protocol(self) -> None:
        args = self.home / "claude.args"
        write_exec(self.fake / "setsid", '#!/bin/sh\nexec "$@"\n')
        write_exec(self.fake / "sleep", "#!/bin/sh\nexit 0\n")
        write_exec(self.fake / "gh", '#!/bin/sh\ncase "$*" in *"pr list"*) echo 7 ;; esac\nexit 0\n')
        write_exec(self.fake / "claude", '#!/bin/sh\nprintf "%s\\n" "$@" >> "$HOME/claude.args"\nexit 0\n')
        # Its own session, so the loop and every child it starts die together.
        p = subprocess.Popen(["bash", str(ROOT / "bin/overnight/driver.sh")], env=self.env(), cwd=ROOT,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            deadline = time.monotonic() + 20
            while not (args.exists() and args.stat().st_size) and time.monotonic() < deadline:
                time.sleep(0.2)
        finally:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
        lines = args.read_text().splitlines()
        call = lines[: lines.index("-p", 1)] if "-p" in lines[1:] else lines
        settings = pathlib.Path(call[call.index("--settings") + 1])
        self.assertTrue(settings.samefile(OVERNIGHT / "settings.json"), settings)
        protocol = re.search(r"/\S*protocol\.md", call[-1])
        self.assertIsNotNone(protocol, call[-1])
        self.assertTrue(pathlib.Path(protocol[0]).samefile(OVERNIGHT / "protocol.md"), protocol[0])
        self.assertFalse((self.state / "lessons.md").exists())
        # The watchdog's stuck-call pgrep must still find a call of the repo's driver.
        pattern = re.search(r'pgrep -of "([^"]+)"', (OVERNIGHT / "watchdog.sh").read_text())[1]
        self.assertRegex(" ".join(["claude", *call]), pattern)

    def test_watchdog_restarts_the_repo_driver(self) -> None:
        write_exec(self.fake / "tmux", '#!/bin/sh\ncase "$1" in has-session) exit 1 ;; '
                   'new*) printf "%s\\n" "$@" > "$HOME/tmux.args" ;; esac\nexit 0\n')
        write_exec(self.fake / "pgrep", "#!/bin/sh\nexit 1\n")
        subprocess.run(["bash", str(OVERNIGHT / "watchdog.sh")], env=self.env(), cwd=ROOT, check=True,
                       capture_output=True, timeout=30)
        cmd = (self.home / "tmux.args").read_text().splitlines()[-1]
        driver = re.search(r"/\S*driver\.sh", cmd)
        self.assertIsNotNone(driver, cmd)
        self.assertEqual(driver[0], f"{self.home}/loam/bin/overnight/driver.sh")
        self.assertTrue(pathlib.Path(driver[0]).samefile(OVERNIGHT / "driver.sh"))

    def test_protocol_writes_lessons_into_the_repo_before_the_merge_gate(self) -> None:
        protocol = (OVERNIGHT / "protocol.md").read_text()
        self.assertNotIn("O/lessons.md", protocol)
        self.assertNotIn("lessons.md", (OVERNIGHT / "driver.sh").read_text())
        learn = re.search(r"^7\. \*\*Learn.*$", protocol, re.M)
        self.assertIsNotNone(learn)
        self.assertIn("`~/.local/state/loam/worktrees/overnight-<n>/docs/factory/LESSONS.md`", learn[0])
        self.assertIn("git push origin HEAD:<branch>", learn[0])
        self.assertRegex(protocol, r"(?m)^8\. \*\*Merge gate")
        self.assertTrue((ROOT / "docs/factory/LESSONS.md").read_text().count("\n## From PR #") >= 19)


if __name__ == "__main__":
    unittest.main()
