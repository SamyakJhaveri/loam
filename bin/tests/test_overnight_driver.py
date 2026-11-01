"""The overnight driver runs from the repo (#476): bin/overnight/driver.sh starts each call with the settings.json and
protocol.md beside it, bin/overnight/watchdog.sh restarts ~/loam/bin/overnight/driver.sh, a call's settings deny it
any write to bin/overnight, and the protocol writes lessons into docs/factory/LESSONS.md on the PR branch. Closing
the driver's terminal leaves its call running, a restarted driver adopts that call instead of starting a second one,
the call's wrapper ends a tool child in a session of its own, and the driver frees a merged PR's slot even with
nothing pending and no outcome line.

The scripts run for real with HOME a temp dir whose loam/bin/overnight links to this checkout, and fake claude, gh,
tmux, pgrep, sleep and alert, so nothing reaches GitHub, Slack, tmux or a model.
"""

from __future__ import annotations

import json
import os
import pathlib
import pty
import re
import shutil
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


    def start_call_fakes(self, tool: str = "") -> pathlib.Path:
        """Fake gh with one pending PR, a sleep of 0.1 s (so the driver's 15 s polls are fast), and a claude that
        appends its pid to calls.txt, runs `tool` and runs until killed."""
        real_sleep = shutil.which("sleep")
        write_exec(self.fake / "sleep", f"#!/bin/sh\nexec {real_sleep} 0.1\n")
        write_exec(self.fake / "gh", '#!/bin/sh\ncase "$*" in *"pr list"*) echo 7 ;; esac\nexit 0\n')
        write_exec(self.fake / "claude",
                   f'#!/bin/sh\necho $$ >> "$HOME/calls.txt"\n{tool}\nwhile :; do {real_sleep} 1; done\n')
        return self.home / "calls.txt"

    def alive(self, pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        return True

    def wait_for(self, cond, timeout: float = 30) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if cond():
                return True
            time.sleep(0.1)
        return cond()

    def kill_group(self, pid: int) -> None:
        """KILL the process group pid is in (a fake claude is in its wrapper's), never the test's own."""
        try:
            g = os.getpgid(pid)
            if g != os.getpgrp():
                os.killpg(g, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

    def calls(self, path: pathlib.Path) -> list[int]:
        return [int(x) for x in path.read_text().split()] if path.exists() else []

    def test_closing_the_drivers_terminal_leaves_its_call_running(self) -> None:
        calls = self.start_call_fakes()
        bash, env = shutil.which("bash"), self.env()
        pid, master = pty.fork()
        if pid == 0:
            try:
                os.chdir(ROOT)
                os.execve(bash, [bash, str(OVERNIGHT / "driver.sh")], env)
            finally:
                os._exit(127)
        call, wrapper = 0, 0
        try:
            self.assertTrue(self.wait_for(lambda: self.calls(calls)), "the driver started no call")
            call = self.calls(calls)[0]
            self.assertTrue(self.wait_for(lambda: (self.state / "call.pid").exists()))
            wrapper = int((self.state / "call.pid").read_text().split()[0])
            os.close(master)
            master = -1
            self.assertTrue(self.wait_for(lambda: os.waitpid(pid, os.WNOHANG)[0] == pid), "the driver kept running")
            pid = 0
            time.sleep(1)
            self.assertTrue(self.alive(call), "closing the driver's terminal ended its call")
            self.assertTrue(self.alive(wrapper), "closing the driver's terminal ended the call's wrapper")
            fields = (self.state / "call.pid").read_text().split()
            self.assertEqual(int(fields[0]), wrapper)
            self.assertEqual(len(fields), 3, "call.pid lacks the log.md line count and the output path")
        finally:
            if master >= 0:
                os.close(master)
            for c in (wrapper, call):
                if c:
                    self.kill_group(c)
            if pid:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)

    def run_driver_until_its_call(self, calls: pathlib.Path, n: int) -> None:
        # A narrow COLUMNS, as in a tmux pane, must not cut the call's args the driver matches.
        p = subprocess.Popen(["bash", str(OVERNIGHT / "driver.sh")], env={**self.env(), "COLUMNS": "80"}, cwd=ROOT,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            self.assertTrue(self.wait_for(lambda: len(self.calls(calls)) >= n), "the driver started no call")
        finally:
            self.kill_group(p.pid)
            p.wait()
            for c in self.calls(calls)[n - 1:]:
                self.kill_group(c)

    def start_driver(self) -> subprocess.Popen:
        # A narrow COLUMNS, as in a tmux pane, must not cut the call's args the driver matches.
        p = subprocess.Popen(["bash", str(OVERNIGHT / "driver.sh")], env={**self.env(), "COLUMNS": "80"}, cwd=ROOT,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(lambda: (self.kill_group(p.pid), p.wait()))
        return p

    def test_restarted_driver_adopts_a_left_call_and_ends_it_after_its_outcome_line(self) -> None:
        calls = self.start_call_fakes()
        prompt = f"Read {self.home}/loam/bin/overnight/protocol.md and process one pull request as it says."
        left = subprocess.Popen(["sh", str(self.fake / "claude"), "-p", prompt], env=self.env(),
                                start_new_session=True)
        self.addCleanup(lambda: (self.kill_group(left.pid), left.wait()))
        self.assertTrue(self.wait_for(lambda: self.calls(calls)))
        (self.state / "log.md").write_text("earlier block\noutcome issue 3: merged\n")
        (self.state / "call.pid").write_text(f"{left.pid} 2 {self.state}/calls/none.json\n")
        driver = self.start_driver()
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)[1:]])
        # About 20 of the driver's 15 s polls: the left call still runs and the driver started none of its own.
        time.sleep(2)
        self.assertIsNone(driver.poll())
        self.assertIsNone(left.poll(), "the driver ended a healthy call an earlier driver left")
        self.assertEqual(len(self.calls(calls)), 1, "the driver started a second call beside the one it adopted")
        self.assertIn(f"adopted call {left.pid} left by an earlier driver", (self.state / "driver.log").read_text())
        with (self.state / "log.md").open("a") as f:
            f.write("outcome issue 8: merged\n")
        self.assertTrue(self.wait_for(lambda: left.poll() is not None, 20), "the adopted call outlived its outcome line")
        self.assertIn(f"ended call {left.pid} 120 s after its outcome line", (self.state / "driver.log").read_text())
        self.assertTrue(self.wait_for(lambda: len(self.calls(calls)) >= 2), "the driver started no call after it")

    def test_driver_leaves_a_reused_pid_alone(self) -> None:
        calls = self.start_call_fakes()
        other = subprocess.Popen([shutil.which("sleep"), "300"], start_new_session=True)
        self.addCleanup(lambda: (self.kill_group(other.pid), other.wait()))
        (self.state / "call.pid").write_text(f"{other.pid} 0 {self.state}/calls/none.json\n")
        self.run_driver_until_its_call(calls, 1)
        self.assertIsNone(other.poll(), "the driver killed a process that is not a driver call")


    @unittest.skipUnless(shutil.which("setsid"), "the tool child starts its session with setsid")
    def test_wrapper_ends_a_tool_child_in_a_session_of_its_own(self) -> None:
        # Claude Code starts each Bash tool shell in a new session (#434), out of reach of a group kill.
        calls = self.start_call_fakes(f'setsid {shutil.which("sleep")} 300 &\necho $! >> "$HOME/tool.txt"')
        tool = self.home / "tool.txt"
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)])
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(tool)])
        self.start_driver()
        self.assertTrue(self.wait_for(lambda: self.calls(tool)), "the call started no tool child")
        child = self.calls(tool)[0]
        self.assertNotEqual(os.getsid(child), os.getsid(self.calls(calls)[0]))
        with (self.state / "log.md").open("a") as f:
            f.write("outcome issue 8: merged\n")
        self.assertTrue(self.wait_for(lambda: not self.alive(self.calls(calls)[0]), 20), "the call was not ended")
        self.assertTrue(self.wait_for(lambda: not self.alive(child), 10),
                        "a tool child in its own session outlived the call")

    def test_reap_frees_a_closed_prs_worktree_with_nothing_pending(self) -> None:
        # The call ended between gh pr merge and its outcome line; next wrote pr-closed. No open PR is left.
        git = {**self.env(), "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
               "GIT_COMMITTER_EMAIL": "t@t"}
        loam = self.home / "loam"
        for cmd in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "x"],
                    ["worktree", "add", "-q", "--detach", str(self.home / "loam-9")]):
            subprocess.run(["git", "-C", str(loam), *cmd], env=git, check=True, capture_output=True)
        run = self.home / ".local/state/loam-factory/runs/9/20261031T000000Z"
        run.mkdir(parents=True)
        (run / "status").write_text("pr-opened\n")
        (run / "pr-closed").write_text("2026-10-31T00:00:00Z\n")
        write_exec(self.fake / "sleep", f"#!/bin/sh\nexec {shutil.which('sleep')} 0.1\n")
        write_exec(self.fake / "gh", "#!/bin/sh\nexit 0\n")
        write_exec(self.fake / "claude", '#!/bin/sh\necho call >> "$HOME/calls.txt"\nexit 0\n')
        self.start_driver()
        self.assertTrue(self.wait_for(lambda: not (self.home / "loam-9").exists(), 20),
                        "the driver left the closed PR's ticket worktree holding the slot")
        self.assertIn(f"removed {self.home}/loam-9", (self.state / "driver.log").read_text())
        self.assertFalse((self.home / "calls.txt").exists(), "the driver started a call with nothing pending")


if __name__ == "__main__":
    unittest.main()
