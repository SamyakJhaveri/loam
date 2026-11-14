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

import fcntl
import fnmatch
import json
import os
import pathlib
import pty
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
OVERNIGHT = ROOT / "bin" / "overnight"
# driver.sh starts each call under a Linux-only wrapper (prctl PR_SET_CHILD_SUBREAPER, /proc); it runs only on jhaveris.
LINUX_ONLY = unittest.skipUnless(sys.platform.startswith("linux"), "the driver's call wrapper needs Linux prctl and /proc")


# The protocol's read of DistBench (Grader window), which the driver runs for the call into grader-window.txt.
GRADER_READ = ["pr", "list", "-R", "SamyakJhaveri/distbench", "--state", "open", "--limit", "100", "--json",
               "number,title,files", "--jq", '.[] | select((.title | test("grader|regrade"; "i")) or any(.files[].path; '
               'test("(^|/)grader\\\\.py$|regrade"; "i"))) | .number']


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
        # run() starts each call through ~/loam/bin/claude-account exec, on the temp home's accounts (env below).
        (self.home / "loam/bin/claude-account").symlink_to(ROOT / "bin/claude-account")
        self.fake = self.home / "fake"
        self.fake.mkdir()
        # Hour 12 for `date +%H`, so no run in 07:00-07:59 Pacific starts the morning-report call first.
        write_exec(self.fake / "date",
                   f'#!/bin/sh\n[ "$*" = +%H ] && {{ echo 12; exit 0; }}\nexec {shutil.which("date")} "$@"\n')
        self.acc = self.home / "acc"
        self.runs = self.home / "runs"

    def env(self) -> dict[str, str]:
        # The account dir, settings file and runs root are the temp home's, so no test switches the host's account
        # or starts its switch cooldown.
        return {**os.environ, "HOME": str(self.home), "PATH": f"{self.fake}:{os.environ['PATH']}",
                "CLAUDE_ACCOUNTS_DIR": str(self.acc), "CLAUDE_SETTINGS_FILE": str(self.home / "settings.json"),
                "FACTORY_RUNS_ROOT": str(self.runs)}

    def accounts(self, stored: tuple[str, ...] = ("a", "b"), active: str = "a") -> None:
        """Stored accounts (a and b), one active (a; none for "")."""
        self.acc.mkdir()
        for n in stored:
            (self.acc / f"{n}.token").write_text("sk-ant-oat01-fake\n")
        if active:
            (self.acc / "active").write_text(f"{active}\n")
        (self.home / "settings.json").write_text("{}\n")

    def active(self) -> str:
        return (self.acc / "active").read_text().strip()

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
        # The call reads DistBench only through the driver's grader-window.txt; no allow rule opens gh on it.
        # Two wildcard rules deny every gh spelling and checkout path that names DistBench (#641); prose in the
        # repo's own spelling, with no slash before it, still runs.
        self.assertEqual([r for r in deny if "distbench" in r.lower()], ["Bash(*distbench*)", "Bash(*/DistBench*)"])
        pats = [r[5:-1] for r in deny if "distbench" in r.lower()]

        def denied(c: str) -> bool:
            return any(fnmatch.fnmatchcase(c, p) for p in pats)

        for cmd in ("gh issue view 1 -R SamyakJhaveri/distbench", "gh pr comment 5 --body x --repo=SamyakJhaveri/distbench",
                    "gh pr comment 5 --body x -RSamyakJhaveri/distbench", "gh api /repos/samyakjhaveri/DistBench/issues",
                    "GH_REPO=SamyakJhaveri/distbench gh pr comment 5 --body x", "cd ~ && cd distbench && gh pr comment 5"):
            self.assertTrue(denied(cmd), cmd)
        for cmd in ("gh pr list -R SamyakJhaveri/loam", 'gh pr comment 5 -R SamyakJhaveri/loam --body "left open: '
                    'grader window: DistBench grader-fix PR 3 open"', "gh pr comment 5 -R SamyakJhaveri/loam --body-file n.md"):
            self.assertFalse(denied(cmd), cmd)
        self.assertNotIn("allow", s["permissions"])

    def test_protocol_reads_the_grader_window_from_the_drivers_file(self) -> None:
        protocol = (OVERNIGHT / "protocol.md").read_text()
        p = re.search(r"(?ms)^\*\*Grader window\.\*\*.*?(?=^\*\*Codex panel\.\*\*)", protocol)
        self.assertIsNotNone(p)
        self.assertIn("O/grader-window.txt", p[0])
        self.assertIn("at the gate, read the whole file once and judge all three conditions from that one copy", p[0])
        self.assertNotIn("gh pr list -R SamyakJhaveri/distbench", p[0])
        lines = p[0].splitlines()
        self.assertIn("At step 8, before the merge, read that file: the window is clear only when line 2 is `exit 0`, "
                      "`read_at` is at most five minutes old, and no number follows.", lines)
        self.assertIn("A number leaves the PR open (step 9) with `left open: grader window: DistBench grader-fix PR "
                      "#<m> open`; any other `exit`, a `read_at` more than five minutes old, or a missing file leaves "
                      "it open with `left open: grader window: DistBench read failed or stale`.", lines)
        self.assertIn("grader-window.txt", re.search(r"(?m)^Run state lives.*$", protocol)[0])
        loop = (ROOT / "docs/factory/LOOP.md").read_text()
        self.assertIn("grader-window.txt", re.search(r"(?m)^Its run state \(.*$", loop)[0])
        # The driver runs the protocol's read, argument for argument.
        self.assertIn("gh " + " ".join(GRADER_READ[:-1]) + " '" + GRADER_READ[-1] + "'", (OVERNIGHT / "driver.sh").read_text())

    @LINUX_ONLY
    def test_driver_call_reads_the_repo_settings_and_protocol(self) -> None:
        args = self.home / "claude.args"
        write_exec(self.fake / "setsid", '#!/bin/sh\nexec "$@"\n')
        write_exec(self.fake / "sleep", "#!/bin/sh\nexit 0\n")
        write_exec(self.fake / "gh", '#!/bin/sh\ncase "$*" in *"pr list"*) echo 7 ;; esac\nexit 0\n')
        write_exec(self.fake / "claude", '#!/bin/sh\necho "$CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS" >> "$HOME/ceiling"\n'
                   'printf "%s\\n" "$@" >> "$HOME/claude.args"\nexit 0\n')
        # An inherited ceiling is overridden, so background agents are never stopped (#679). Appended, since a later
        # call the setsid wrapper keeps alive past killpg could truncate the file just before the read.
        env = {**self.env(), "CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "600000"}
        # Its own session, so the loop and every child it starts die together.
        p = subprocess.Popen(["bash", str(ROOT / "bin/overnight/driver.sh")], env=env, cwd=ROOT,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            deadline = time.monotonic() + 20
            while not (args.exists() and args.stat().st_size) and time.monotonic() < deadline:
                time.sleep(0.2)
        finally:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
        self.assertEqual((self.home / "ceiling").read_text().splitlines()[0], "0")
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
        """Fake gh with one pending PR, a sleep of 0.1 s that logs each interval to events (so the driver's 15 s polls
        are fast), and a claude that appends its pid to calls.txt, runs `tool` and runs until killed. On DistBench the
        fake gh answers only the protocol's exact read, compared argument by argument: it logs `read`, prints dist and
        exits with rc; any other DistBench call logs `bad` and exits 9."""
        real_sleep = shutil.which("sleep")
        write_exec(self.fake / "sleep", f'#!/bin/sh\necho "sleep $*" >> "$HOME/events"\nexec {real_sleep} 0.1\n')
        (self.home / "want").write_bytes(b"".join(a.encode() + b"\0" for a in GRADER_READ))
        (self.home / "dist").write_text("9\n")
        (self.home / "rc").write_text("0\n")
        write_exec(self.fake / "gh", '#!/bin/sh\ncase "$*" in *SamyakJhaveri/distbench*) printf "%s\\0" "$@" | '
                   'cmp -s - "$HOME/want" || { echo bad >> "$HOME/events"; exit 9; }; echo read >> "$HOME/events"; '
                   'cat "$HOME/dist"; exit "$(cat "$HOME/rc")" ;; *"pr list"*) echo 7 ;; esac\nexit 0\n')
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

    @LINUX_ONLY
    def test_closing_the_drivers_terminal_leaves_its_call_running(self) -> None:
        self.accounts()
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
            self.assertEqual(len(fields), 4, "call.pid lacks the log.md line count, the output path or the account")
            self.assertEqual(fields[3], "a", "call.pid does not name the account the call started on")
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

    @LINUX_ONLY
    def test_restarted_driver_adopts_a_left_call_and_ends_it_after_its_outcome_line(self) -> None:
        calls = self.start_call_fakes()
        prompt = f"Read {self.home}/loam/bin/overnight/protocol.md and process one pull request as it says."
        left = subprocess.Popen(["sh", str(self.fake / "claude"), "-p", prompt], env=self.env(),
                                start_new_session=True)
        self.addCleanup(lambda: (self.kill_group(left.pid), left.wait()))
        self.assertTrue(self.wait_for(lambda: self.calls(calls)))
        (self.state / "log.md").write_text("earlier block\noutcome issue 3: merged\n")
        (self.state / "call.pid").write_text(f"{left.pid} 2 {self.state}/calls/none.json\n")
        window = self.state / "grader-window.txt"
        window.write_text("read_at 1970-01-01T00:00:00Z\nexit 0\n")
        t0 = self.utc()
        driver = self.start_driver()
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)[1:]])
        # About 20 of the driver's 15 s polls: the left call still runs and the driver started none of its own.
        time.sleep(2)
        self.assertIsNone(driver.poll())
        self.assertIsNone(left.poll(), "the driver ended a healthy call an earlier driver left")
        self.assertEqual(len(self.calls(calls)), 1, "the driver started a second call beside the one it adopted")
        self.assertIn(f"adopted call {left.pid} left by an earlier driver", (self.state / "driver.log").read_text())
        # The adopted call's stale grader-window.txt is refreshed on every poll.
        got = window.read_text().splitlines()
        self.assertTrue(t0 <= got[0].removeprefix("read_at ") <= self.utc(), got)
        self.assertEqual(got[1:], ["exit 0", "9"])
        self.assert_a_read_after_every_poll(3)
        with (self.state / "log.md").open("a") as f:
            f.write("outcome issue 8: merged\n")
        self.assertTrue(self.wait_for(lambda: left.poll() is not None, 20), "the adopted call outlived its outcome line")
        self.assertIn(f"ended call {left.pid} 120 s after its outcome line", (self.state / "driver.log").read_text())
        self.assertTrue(self.wait_for(lambda: len(self.calls(calls)) >= 2), "the driver started no call after it")

    def test_watch_reads_only_before_an_outcome_and_ends_after_nine_polls(self) -> None:
        # Run the shipped watcher without real sleeps or reads.
        driver = (OVERNIGHT / "driver.sh").read_text()
        watch = re.search(r"(?ms)^watch\(\).*?^}", driver)[0]
        (self.state / "log.md").write_text("earlier block\noutcome issue 8: merged\n")
        for before, limit in ((1, 9), (2, 4)):
            with self.subTest(before=before):
                script = '''set -u
O=$1
before=$2
limit=$3
polls_seen=0
reads=0
stamp() { echo test; }
sleep() {
  [ "$1" = 15 ] || exit 2
  [ "$polls_seen" -lt "$limit" ] || { echo "bounded $reads"; exit 0; }
  polls_seen=$((polls_seen + 1))
  echo "sleep $1"
}
grader_window() { reads=$((reads + 1)); echo read; }
end_call() { echo "ended $polls_seen $reads"; }
''' + watch + '\nwatch "$$" "$before"\n'
                got = subprocess.run(["bash", "-c", script, "watch-test", str(self.state), str(before), str(limit)],
                                     text=True, capture_output=True, check=True, timeout=5)
                expected = (["sleep 15"] * 9 + ["ended 9 0"] if before == 1 else
                            ["sleep 15", "read"] * limit + [f"bounded {limit}"])
                self.assertEqual(got.stdout.splitlines(), expected)

    def utc(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def assert_a_read_after_every_poll(self, n: int) -> None:
        ev = (self.home / "events").read_text().splitlines()
        self.assertNotIn("bad", ev, "the driver ran a DistBench gh call other than the protocol's read")
        polls = [i for i, e in enumerate(ev) if e == "sleep 15"]
        self.assertGreaterEqual(len(polls), n)
        missed = [i for i in polls if i + 1 < len(ev) and ev[i + 1] != "read"]
        self.assertEqual(missed, [], f"a 15 s poll with no DistBench read right after it: {ev}")

    @LINUX_ONLY
    def test_driver_writes_the_grader_window_before_a_call_and_after_every_poll(self) -> None:
        window = self.state / "grader-window.txt"
        calls = self.start_call_fakes(f'cp "{window}" "$HOME/seen.txt"')
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)])
        t0 = self.utc()
        self.start_driver()
        self.assertTrue(self.wait_for(lambda: self.calls(calls)), "the driver started no call")
        # The fake claude logs its pid before it copies the file, so wait for the copy itself.
        copy = self.home / "seen.txt"
        self.assertTrue(self.wait_for(lambda: copy.exists() and copy.read_text().endswith("\n"), 10),
                        "the call saw no grader-window.txt")
        seen = copy.read_text().splitlines()
        self.assertTrue(t0 <= seen[0].removeprefix("read_at ") <= self.utc(), seen)
        self.assertEqual(seen[1:], ["exit 0", "9"], "the call started without a fresh grader-window.txt")

        def lines() -> list[str]:
            return window.read_text().splitlines() if window.exists() else []
        # A failed read carries gh's status, and the next poll's read recovers.
        (self.home / "dist").write_text("")
        (self.home / "rc").write_text("3\n")
        self.assertTrue(self.wait_for(lambda: lines()[1:] == ["exit 3"], 10), lines())
        self.assertRegex((self.state / "driver.log").read_text(),
                         r"(?m)^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ grader-window read failed: exit 3$")
        (self.home / "rc").write_text("0\n")
        self.assertTrue(self.wait_for(lambda: lines()[1:] == ["exit 0"], 10), lines())
        self.assertTrue(t0 <= lines()[0].removeprefix("read_at ") <= self.utc(), lines())
        self.assertTrue(self.wait_for(lambda: (self.home / "events").read_text().splitlines().count("sleep 15") >= 3, 10),
                        "the driver did not reach three watch polls")
        self.assert_a_read_after_every_poll(3)

    @LINUX_ONLY
    def test_killing_the_drivers_group_ends_its_grader_read(self) -> None:
        # Every test's cleanup, and an operator, stop the driver by killing its process group; a grader-window read
        # outside that group outlived it and wrote into the removed temp home (ENOTEMPTY on CI, 13 Nov).
        calls = self.start_call_fakes()
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)])
        real_sleep = shutil.which("sleep")
        write_exec(self.fake / "gh", '#!/bin/sh\ncase "$*" in *SamyakJhaveri/distbench*) '
                   f'echo start >> "$HOME/reads"; {real_sleep} 1; echo late >> "$HOME/reads" ;; *"pr list"*) echo 7 ;; esac\nexit 0\n')
        driver = self.start_driver()
        reads = self.home / "reads"
        self.assertTrue(self.wait_for(lambda: reads.exists()), "the driver started no grader read")
        self.kill_group(driver.pid)
        driver.wait()
        time.sleep(2)
        self.assertNotIn("late", reads.read_text().split(), "a grader read outlived the driver's process group")

    @LINUX_ONLY
    def test_a_child_left_by_the_grader_read_does_not_hold_the_driver(self) -> None:
        # A child gh leaves holding its stdout must neither keep the driver from writing the window nor write into it
        # later (Codex review, 13 Nov): REAP ends it, and the read it outlived fails.
        calls = self.start_call_fakes()
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)])
        real_sleep = shutil.which("sleep")
        write_exec(self.fake / "gh", '#!/bin/sh\ncase "$*" in *SamyakJhaveri/distbench*) '
                   f'({real_sleep} 3; echo 99) & echo 9 ;; *"pr list"*) echo 7 ;; esac\nexit 0\n')
        self.start_driver()
        window = self.state / "grader-window.txt"
        self.assertTrue(self.wait_for(lambda: window.exists(), 2.5), "the driver waited on the read's child")
        time.sleep(3)  # past the child's write
        self.assertEqual(window.read_text().splitlines()[1:], ["exit 120"])

    @LINUX_ONLY
    def test_a_child_writing_after_gh_exits_fails_the_read(self) -> None:
        # gh's stdout is shared with every process gh starts, so bytes a child writes once gh has exited are not gh's
        # answer; a read that gh outlived by any process is a failed read, never a window (Codex round 2, 14 Nov).
        calls = self.start_call_fakes()
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)])
        write_exec(self.fake / "gh", f"""#!{sys.executable}
import os, sys, time
if "SamyakJhaveri/distbench" not in sys.argv:
    print(7 if "list" in sys.argv else "")
    sys.exit(0)
gh = os.getpid()
if os.fork() == 0:  # waits for gh to exit, then writes 99 for 2 s
    while os.getppid() == gh:
        pass
    end = time.monotonic() + 2
    while time.monotonic() < end:
        os.write(1, b"99\\n")
        time.sleep(0.001)
    os._exit(0)
print(9)
""")
        self.start_driver()
        window = self.state / "grader-window.txt"
        self.assertTrue(self.wait_for(lambda: window.exists(), 10), "the driver wrote no window")
        self.assertEqual(window.read_text().splitlines()[1:], ["exit 120"])
        # The call starts after this window; wait for its pid, so cleanup ends it before removing the home.
        self.assertTrue(self.wait_for(lambda: self.calls(calls)), "the driver started no call")

    @LINUX_ONLY
    def test_files_the_call_changes_in_its_state_dir_during_the_read_do_not_change_the_answer(self) -> None:
        # The call can write the state dir while the read runs; whatever it removes or puts there, the window holds
        # gh's answer (Codex, 14 Nov: an emptied capture file there read as a clear window).
        calls = self.start_call_fakes()
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)])
        write_exec(self.fake / "gh", '#!/bin/sh\ncase "$*" in *SamyakJhaveri/distbench*) echo 9; '
                   f'for f in "{self.state}"/*; do [ -f "$f" ] || continue; case $f in *.md|*.txt) ;; *) rm -f "$f"; : > "$f" ;; esac; done ;; '
                   '*"pr list"*) echo 7 ;; esac\nexit 0\n')
        self.start_driver()
        window = self.state / "grader-window.txt"
        self.assertTrue(self.wait_for(lambda: window.exists(), 10), "the driver wrote no window")
        self.assertEqual(window.read_text().splitlines()[1:], ["exit 0", "9"])
        # The call starts after this window; wait for its pid, so cleanup ends it before removing the home.
        self.assertTrue(self.wait_for(lambda: self.calls(calls)), "the driver started no call")

    @LINUX_ONLY
    def test_a_planted_link_does_not_redirect_the_grader_window_write(self) -> None:
        # The call can write the state dir; links planted at the old temp name and at the window itself must not
        # make the unsandboxed driver write through them (Codex review of PR #660).
        victim = self.home / "victim"
        victim.write_text("keep\n")
        (self.state / "grader-window.tmp").symlink_to(victim)
        (self.state / "grader-window.txt").symlink_to(victim)
        calls = self.start_call_fakes()
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)])
        self.start_driver()
        self.assertTrue(self.wait_for(lambda: self.calls(calls)), "the driver started no call")
        window = self.state / "grader-window.txt"
        self.assertTrue(self.wait_for(lambda: not window.is_symlink(), 10), "the window is still the planted link")
        self.assertEqual(window.read_text().splitlines()[1:], ["exit 0", "9"])
        self.assertEqual(victim.read_text(), "keep\n", "the driver wrote through a planted link")

    @LINUX_ONLY
    def test_a_window_file_the_call_swaps_at_publication_is_not_published(self) -> None:
        # The call can write all of ~/.local/state/loam. At the moment the driver renames its new window into place,
        # the call replaces every grader-window file there with a forged clear window; the window must still hold gh's
        # answer (Codex loam-775 at d4bcaca2: the temp file was renamed by a name the call could swap).
        hook = self.home / "hook"
        hook.mkdir()
        (hook / "SwapAtRename.pm").write_text(r"""package SwapAtRename;
*CORE::GLOBAL::rename = sub {
  if ($_[1] =~ m{/grader-window\.txt\z}) {
    require File::Find; require POSIX;
    open(my $m, ">>", "$ENV{HOME}/swaps") or die; print $m "$_[0]\n"; close $m;
    File::Find::find({no_chdir => 1, wanted => sub {
      return unless m{/grader-window[^/]*\z} && -f;
      unlink $_; open(my $f, ">", $_) or die; print $f POSIX::strftime("read_at %FT%TZ\nexit 0\n", gmtime); close $f }},
      "$ENV{HOME}/.local/state/loam") }
  CORE::rename($_[0], $_[1]) };
1;
""")
        calls = self.start_call_fakes()
        self.addCleanup(lambda: [self.kill_group(c) for c in self.calls(calls)])
        p = subprocess.Popen(["bash", str(OVERNIGHT / "driver.sh")], cwd=ROOT, start_new_session=True,
                             env={**self.env(), "PERL5LIB": str(hook), "PERL5OPT": "-MSwapAtRename"},
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(lambda: (self.kill_group(p.pid), p.wait()))
        self.assertTrue(self.wait_for(lambda: self.calls(calls)), "the driver started no call")
        self.assertTrue((self.home / "swaps").exists(), "no window publication reached the swap")
        self.assertEqual((self.state / "grader-window.txt").read_text().splitlines()[1:], ["exit 0", "9"],
                         f"the driver published a window file the call swapped: {(self.home / 'swaps').read_text()}")

    @LINUX_ONLY
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
        # setsid runs in the child after $! is known, so wait for it rather than read the session once (CI race, PR 742).
        call = self.calls(calls)[0]
        self.assertTrue(self.wait_for(lambda: os.getsid(child) != os.getsid(call)), "the tool child shares the call's session")
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
        # The driver logs the removal only after git returns, so wait for the line too.
        log = self.state / "driver.log"
        self.assertTrue(self.wait_for(lambda: log.exists() and f"removed {self.home}/loam-9" in log.read_text(), 10),
                        "the driver logged no removal of the closed PR's ticket worktree")
        self.assertFalse((self.home / "calls.txt").exists(), "the driver started a call with nothing pending")


    # Usage limits (#615): the driver switches only through `bin/claude-account switch <the call's account>`.
    LIMIT = ('{"is_error":true,"result":"You\u0027ve hit your session limit - resets 6am","total_cost_usd":0,'
             '"num_turns":1}')

    def limit_fakes(self, hook: str, stored: tuple[str, ...] = ("a", "b"), active: str = "a") -> dict[str, str]:
        """Accounts a (active) and b, a gh with one pending PR, and a claude whose first call runs `hook` and replies
        with a usage limit, every later call with a plain result. The fake sleep keeps the 15 s polls short, lets the
        5 s retry pause through and ends the driver at any other pause, so a run stops after the call that follows
        the limit. Returns the driver's environment."""
        self.accounts(stored, active)
        self.runs.mkdir()
        (self.home / ".local/state/loam-factory").mkdir(parents=True)
        write_exec(self.fake / "gh", '#!/bin/sh\ncase "$*" in *"pr list"*) echo 7 ;; esac\nexit 0\n')
        write_exec(self.fake / "claude", '#!/bin/bash\necho x >> "$H/calls"\n'
                   'if [ -e "$H/c1" ]; then echo "{\\"result\\":\\"ok\\"}"; exit 0; fi\n'
                   'touch "$H/c1"; eval "$HOOK"\nprintf "%s\\n" "$LIM"\n')
        write_exec(self.fake / "sleep", '#!/bin/bash\ncase $1 in 15) exec /bin/sleep 0.2 ;; 1) exec /bin/sleep 1 ;; '
                   '5) exit 0 ;; esac\nkill -TERM "$PPID"\n')
        return {**self.env(), "H": str(self.home), "W": str(ROOT), "LIM": self.LIMIT, "HOOK": hook}

    def driver(self, env: dict[str, str]) -> subprocess.Popen:
        p = subprocess.Popen(["timeout", "60", "bash", str(self.home / "loam/bin/overnight/driver.sh")], env=env,
                             cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(lambda: (self.kill_group(p.pid), p.wait()))
        return p

    def n_calls(self) -> int:
        f = self.home / "calls"
        return len(f.read_text().splitlines()) if f.exists() else 0

    def log(self) -> str:
        return (self.state / "driver.log").read_text()

    def leave_a_call(self, env: dict[str, str]) -> None:
        """Start a driver, stop it while its first call runs (the call's hook waits for $H/go), and leave the call."""
        d1 = self.driver(env)
        self.assertTrue(self.wait_for(lambda: (self.home / "c1").exists() and (self.state / "call.pid").exists()
                                      and (self.state / "call.pid").stat().st_size), "the driver started no call")
        wrapper = int((self.state / "call.pid").read_text().split()[0])
        self.addCleanup(lambda: self.kill_group(wrapper))
        d1.terminate()
        d1.wait()

    def adopt_it(self, env: dict[str, str]) -> None:
        d2 = self.driver(env)
        self.assertTrue(self.wait_for(lambda: "adopted call" in (self.log() if (self.state / "driver.log").exists()
                                                                  else "")), "the restarted driver adopted no call")
        (self.home / "go").touch()
        d2.wait(70)

    @LINUX_ONLY
    def test_a_usage_limit_on_the_active_account_switches_and_retries(self) -> None:
        self.driver(self.limit_fakes(":")).wait(70)
        self.assertEqual(self.active(), "b")
        self.assertGreaterEqual(self.n_calls(), 2, "the driver did not retry after the switch")
        self.assertIn("usage limit on account a: active account now b; retrying", self.log())

    @LINUX_ONLY
    def test_a_usage_limit_with_no_other_account_switches_nothing(self) -> None:
        self.driver(self.limit_fakes(":", stored=("a",))).wait(70)
        self.assertEqual(self.active(), "a")
        self.assertIn("usage limit and no other account to switch to", self.log())
        self.assertEqual(self.n_calls(), 1, "the driver retried at once with no account to switch to")

    @LINUX_ONLY
    def test_a_call_with_no_active_account_records_none_and_switches_nothing(self) -> None:
        self.driver(self.limit_fakes(f'cp "{self.state}/call.pid" "$H/seen"', active="")).wait(70)
        self.assertEqual(len((self.home / "seen").read_text().split()), 3, "call.pid names an account with none active")
        self.assertFalse((self.acc / "active").exists(), "the driver switched with no account recorded")
        self.assertIn("usage limit on a call with no recorded account: switched nothing", self.log())

    @LINUX_ONLY
    def test_a_usage_limit_keeps_a_switch_the_factory_made_during_the_call(self) -> None:
        hook = ('FACTORY_SOURCED=1 FACTORY_ROOT="$W" CALL_ACCOUNT=a bash -c ". \\"$W/bin/factory\\"; LOG=/dev/null; '
                'LEDGER=/dev/null; limit_switch" > /dev/null 2>&1')
        self.driver(self.limit_fakes(hook)).wait(70)
        self.assertEqual(self.active(), "b", "the driver switched the host back to the account the call ran on")
        self.assertIn("already switched from a", self.log())

    @LINUX_ONLY
    def test_a_usage_limit_within_the_cooldown_switches_nothing(self) -> None:
        self.driver(self.limit_fakes('date +%s > "$FACTORY_RUNS_ROOT/limit-switch"')).wait(70)
        self.assertEqual(self.active(), "a", "the driver switched within 300 s of another caller's switch")
        self.assertIn("usage limit on account a: another caller switched under 300 s ago; switched nothing", self.log())
        self.assertEqual(self.n_calls(), 1, "the driver retried at once inside the cooldown")

    @LINUX_ONLY
    @unittest.skipUnless(shutil.which("flock"), "claude-account switch takes its lock with flock")
    def test_a_usage_limit_waits_for_the_switch_lock_then_switches(self) -> None:
        held = self.home / "held"
        p = self.driver(self.limit_fakes(f'for i in $(seq 100); do [ -e "{held}" ] && break; /bin/sleep 0.1; done'))
        self.assertTrue(self.wait_for(lambda: (self.home / "c1").exists()), "the driver started no call")
        self.runs.mkdir(exist_ok=True)
        with (self.runs / "limit-switch.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            held.touch()
            time.sleep(4)
            self.assertEqual(self.active(), "a", "the driver switched while another caller held the lock")
        p.wait(70)
        self.assertEqual(self.active(), "b", "the driver did not switch once the lock was free")

    @LINUX_ONLY
    def test_an_adopted_call_keeps_a_switch_made_after_it_started(self) -> None:
        env = self.limit_fakes('for i in $(seq 300); do [ -e "$H/go" ] && break; /bin/sleep 0.1; done')
        self.leave_a_call(env)
        self.assertEqual((self.state / "call.pid").read_text().split()[3], "a")
        subprocess.run([str(ROOT / "bin/claude-account"), "use", "b"], env=env, check=True, capture_output=True)
        self.adopt_it(env)
        self.assertEqual(self.active(), "b", "the adopted call's limit switched the host back to a")

    @LINUX_ONLY
    def test_an_adopted_call_on_the_active_account_still_switches(self) -> None:
        env = self.limit_fakes('for i in $(seq 300); do [ -e "$H/go" ] && break; /bin/sleep 0.1; done')
        self.leave_a_call(env)
        self.adopt_it(env)
        self.assertEqual(self.active(), "b", "the adopted call's usage limit switched nothing")
        self.assertGreaterEqual(self.n_calls(), 2, "the driver read no result of the adopted call, or did not retry")

    @LINUX_ONLY
    def test_an_adopted_calls_limit_within_the_cooldown_keeps_the_normal_pacing(self) -> None:
        env = self.limit_fakes('for i in $(seq 300); do [ -e "$H/go" ] && break; /bin/sleep 0.1; done')
        self.leave_a_call(env)
        (self.runs / "limit-switch").write_text(f"{int(time.time())}\n")
        self.adopt_it(env)
        self.assertEqual(self.active(), "a", "the driver switched within 300 s of another caller's switch")
        self.assertIn("usage limit on account a: another caller switched under 300 s ago; switched nothing", self.log())
        self.assertEqual(self.n_calls(), 1, "the driver started a call at once after an adopted call's limit")

    @LINUX_ONLY
    def test_an_adopted_call_with_no_recorded_account_switches_nothing(self) -> None:
        # A record a driver before #615 left: pid, log line count and output path only.
        env = self.limit_fakes('for i in $(seq 300); do [ -e "$H/go" ] && break; /bin/sleep 0.1; done')
        self.leave_a_call(env)
        pid = self.state / "call.pid"
        pid.write_text(" ".join(pid.read_text().split()[:3]) + "\n")
        self.adopt_it(env)
        self.assertEqual(self.active(), "a")
        self.assertIn("usage limit on a call with no recorded account: switched nothing", self.log())

    @LINUX_ONLY
    def test_only_samyaks_same_repo_prs_start_a_call_or_reach_pick(self) -> None:
        # Loam is public and gh names a fork PR's branch without its owner (#678): a fork's factory/<n> PR, a fork PR
        # Samyak authored and another author's same-repo PR must start no call; Samyak's same-repo PR starts one, and
        # the Pick line's own command lists only it. The fake gh answers as gh does: only the --json fields asked for,
        # through the --jq filter.
        if not shutil.which("jq"):
            self.skipTest("jq is not installed")
        write_exec(self.fake / "sleep", f"#!/bin/sh\nexec {shutil.which('sleep')} 0.1\n")
        write_exec(self.fake / "gh", "\n".join([
            "#!/bin/sh",
            'case "$*" in *SamyakJhaveri/distbench*) exit 0 ;; *"pr list"*) ;; *) exit 0 ;; esac',
            "f=; q=; while [ $# -gt 0 ]; do case $1 in --json) f=$2; shift ;; -q | --jq) q=$2; shift ;; esac; shift; done",
            'echo list >> "$HOME/events"',
            'jq --arg f "$f" \'[.[] | with_entries(select(.key as $k | $f | split(",") | index($k)))]\' "$HOME/prs.json"'
            ' | jq -r "${q:-.}"', ""]))
        write_exec(self.fake / "claude", '#!/bin/sh\nprintf "%s\\n" "$*" >> "$HOME/calls"\nexit 0\n')
        kinds = [(True, "mallory", "mallory"), (True, "SamyakJhaveri", "org"), (False, "writer", "SamyakJhaveri"),
                 (False, "SamyakJhaveri", "SamyakJhaveri")]
        prs = [{"number": 900 + i, "title": f"factory ticket {900 + i}", "isDraft": False,
                "headRefName": f"factory/{900 + i}", "isCrossRepository": cross,
                "author": {"id": f"U_{i}", "is_bot": False, "login": login, "name": login},
                "headRepositoryOwner": {"id": f"O_{i}", "login": owner, "name": owner},
                "body": f"Closes #{900 + i}", "labels": []} for i, (cross, login, owner) in enumerate(kinds)]
        events, calls = self.home / "events", self.home / "calls"

        def lists() -> int:
            return events.read_text().split().count("list") if events.exists() else 0

        def pr_calls() -> int:
            return calls.read_text().count("process one pull request") if calls.exists() else 0

        for own, expected in ((False, 0), (True, 1)):
            events.unlink(missing_ok=True)
            (self.home / "prs.json").write_text(json.dumps(prs if own else prs[:3]))
            p = subprocess.Popen(["bash", str(OVERNIGHT / "driver.sh")], env=self.env(), cwd=ROOT,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            try:
                self.assertTrue(self.wait_for(lambda: lists() >= 3 or pr_calls() >= 1, 20), "the driver did not poll")
            finally:
                self.kill_group(p.pid)
                p.wait()
            time.sleep(0.3)
            self.assertEqual(min(pr_calls(), 1), expected, f"PR calls with Samyak's same-repo PR open: {own}")
        line = re.search(r"(?m)^1\. \*\*Pick\.\*\* `([^`]*)`", (OVERNIGHT / "protocol.md").read_text())
        self.assertIsNotNone(line, "protocol.md has no Pick line with a command")
        out = subprocess.run(["bash", "-c", line.group(1)], env=self.env(), capture_output=True, text=True, check=True)
        listed = json.loads(out.stdout)
        self.assertEqual([x["headRefName"] for x in listed], ["factory/903"])
        self.assertTrue({"number", "title", "isDraft", "body", "labels"} <= set(listed[0]))


if __name__ == "__main__":
    unittest.main()
