"""Whole tickets from `bin/factory next` to a pull request, through the real supervisor (#576).

The other factory tests source bin/factory and stub the functions around the one they test; these run real
`bin/factory -C <target> next` ticks and the runs they launch, through round 0, worker rounds, the checks and the
graders to a PR, so a change to a stage, or to a joint between two stages, fails here. Stand-ins sit only at the host's
edges: bin/tests/fixtures/factory-e2e holds a scripted `claude`, a `gh` over a local issue store and a `tmux` with no
server (each file says what it answers), and each exits 2, logged to unknown.log, on a call it does not know.

Each test copies this checkout (every file but .git and .venv) into a scratch directory as the factory home, a git
repository on a branch other than main, so `next`'s pull of its own checkout refuses and nothing writes this one. The
target is a scratch project with an executable bin/check and a standing list, whose origin is a bare repository at a
path ending github.com/o/r.git, so target_repo reads o/r while push and fetch stay local. Every subprocess gets an
explicit environment, never os.environ: a scratch HOME (bin/alert finds no config and posts nothing; the run dirs, the
daily ledger and the user settings are the test's own), a scratch TMPDIR, a git identity, and PATH with the stand-ins
first. Linux only: the runner is Linux, and the stand-ins and the cleanup read /proc.
"""

from __future__ import annotations

import glob
import json
import os
import pathlib
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
STANDINS = ROOT / "bin/tests/fixtures/factory-e2e"
OWNER = "SamyakJhaveri"  # bin/factory's TICKET_OWNER: next launches only issues this login wrote
RUN_DEADLINE_SEC = 150  # a run here takes seconds; the deadline only turns a hang into a failure
# The target's bin/check records where it ran, outside the worktrees, so a guard that never runs it fails test_pass.
CHECK = '#!/bin/sh\npwd >> "$E2E_STATE/check.log"\n'
STANDING = "# Standing\n\n## Standing do-not-touch list\n\n- `bin/check`\n"


def ticket(scenario: str, caps: str = "") -> str:
    """A body `bin/factory lint` accepts; the claude stand-in's worker acts on its e2e-scenario line."""
    return f"""# e2e {scenario}
Brief: one end-to-end scenario
Blocked by: none

## Goal and why
Write done.txt in the project root.
e2e-scenario: {scenario}

## Do not touch
The standing list.

## Out of scope
Everything else.

## Done checks
```done-checks
predict done-file test ! -e done.txt
test -f done.txt && pass done-file || fail done-file "done.txt is missing"
guard bin/check > /dev/null 2>&1 && pass check-green || fail check-green "bin/check is red"
```

## Worker
worker: claude
codex-review: no
effort: low
contract: 2
goal: the done-checks block prints no FAIL line, or stop after 5 turns
{caps}
## Decisions
none"""


def uncopied(d: str, names: list[str]) -> list[str]:
    """What the factory home's copy leaves out: .git and .venv at the top, and any entry a plain copy cannot read, such
    as the device nodes a sandbox mounts over the dotfiles it protects (as tar, too, cannot copy them)."""
    out = []
    for n in names:
        p = os.path.join(d, n)
        mode = os.lstat(p).st_mode
        if (d == str(ROOT) and n in (".git", ".venv")) or not (
                stat.S_ISLNK(mode) or ((stat.S_ISREG(mode) or stat.S_ISDIR(mode)) and os.access(p, os.R_OK))):
            out.append(n)
    return out


def start_time(pid: int) -> str | None:
    """/proc/<pid>/stat's start time, or None when the process is gone or a zombie (as the tmux stand-in reads it)."""
    try:
        stat = pathlib.Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except OSError:
        return None
    fields = stat[stat.rindex(")") + 2:].split()
    return None if fields[0] in ("Z", "X") else fields[19]


@unittest.skipUnless(sys.platform.startswith("linux"), "the factory runner is Linux, and the stand-ins and the "
                     "cleanup read /proc; the factory-macos CI job runs bin/tests/test_factory*.py")
class EndToEndTests(unittest.TestCase):
    def setUp(self) -> None:
        self.top = pathlib.Path(tempfile.mkdtemp(prefix="factory-e2e-")).resolve()
        self.addCleanup(shutil.rmtree, self.top, True)
        self.addCleanup(self.kill_strays)
        home, tmp, self.state = self.top / "home", self.top / "tmp", self.top / "state"
        for d in (home, tmp, self.state):
            d.mkdir()
        self.env = {
            "HOME": str(home), "TMPDIR": str(tmp), "LANG": "C.UTF-8", "E2E_STATE": str(self.state),
            "PATH": f"{STANDINS}{os.pathsep}{os.environ.get('PATH', os.defpath)}",
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "e2e", "GIT_AUTHOR_EMAIL": "e2e@example.invalid",
            "GIT_COMMITTER_NAME": "e2e", "GIT_COMMITTER_EMAIL": "e2e@example.invalid",
        }
        self.runs = home / ".local/state/loam-factory/runs/o__r"
        # The factory home: a plain copy, made a repository on a branch other than main.
        self.home = self.top / "loam"
        shutil.copytree(ROOT, self.home, symlinks=True, ignore=uncopied)
        self.git(self.home, "init", "-q", "-b", "e2e-home")
        self.git(self.home, "add", "-A")
        self.git(self.home, "commit", "-q", "-m", "factory home")
        # The target: a bare origin under github.com/o/r.git and the clone next works on.
        seed = self.top / "seed"
        for name, text in {"bin/check": CHECK, "docs/factory/STANDING.md": STANDING,
                           "README.md": "e2e target\n"}.items():
            (seed / name).parent.mkdir(parents=True, exist_ok=True)
            (seed / name).write_text(text, encoding="utf-8")
        (seed / "bin/check").chmod(0o755)
        self.git(self.top, "init", "-q", "-b", "main", str(seed))
        self.git(seed, "add", "-A")
        self.git(seed, "commit", "-q", "-m", "base")
        self.bare = self.top / "remote/github.com/o/r.git"
        self.git(self.top, "clone", "-q", "--bare", str(seed), str(self.bare))
        self.proj = self.top / "proj"
        self.git(self.top, "clone", "-q", str(self.bare), str(self.proj))

    def git(self, cwd: pathlib.Path, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=cwd, env=self.env, capture_output=True, text=True,
                              check=True).stdout.strip()

    def seed(self, *issues: tuple[int, str]) -> None:
        """The gh store: these ready-for-agent issues, written by OWNER and never edited, with no PR yet."""
        store = {"repo": "o/r", "login": OWNER, "origin": str(self.bare), "next": max(n for n, _ in issues) + 1,
                 "issues": {str(n): {"number": n, "title": f"e2e #{n}", "body": body, "author": OWNER, "editor": None,
                                     "lastEditedAt": None, "labels": ["ready-for-agent"], "assignees": [],
                                     "state": "open", "created_at": "2026-11-01T00:00:00Z", "events": []}
                            for n, body in issues},
                 "prs": {}}
        (self.state / "gh.json").write_text(json.dumps(store), encoding="utf-8")

    def store(self) -> dict:
        return json.loads((self.state / "gh.json").read_text(encoding="utf-8"))

    def tick(self, **env: str) -> subprocess.CompletedProcess[str]:
        """One `bin/factory -C <target> next`, as the runner's cron line runs it from the factory home."""
        return subprocess.run([str(self.home / "bin/factory"), "-C", str(self.proj), "next"], cwd=self.home,
                              env={**self.env, **env}, capture_output=True, text=True, timeout=120)

    def calls(self, tool: str) -> list[dict]:
        log = self.state / f"{tool}.log"
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []

    def workers(self) -> int:
        return sum(c["kind"] == "worker" for c in self.calls("claude"))

    def launches(self) -> list[str]:
        """The session name of each new-session call."""
        return [c["argv"][c["argv"].index("-s") + 1] for c in self.calls("tmux") if c["argv"][:1] == ["new-session"]]

    def session(self, issue: int) -> dict | None:
        f = self.state / "tmux" / f"o__r-{issue}.session.json"
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None

    def session_alive(self, issue: int) -> bool:
        s = self.session(issue)
        return s is not None and s["start"] is not None and start_time(s["pid"]) == s["start"]

    def run_dir(self, issue: int) -> pathlib.Path:
        dirs = sorted((self.runs / str(issue)).glob("*/"))
        self.assertEqual(len(dirs), 1, f"one run dir of #{issue}: {dirs}")
        return dirs[0]

    def read(self, path: pathlib.Path) -> str:
        return path.read_text(encoding="utf-8")

    def diag(self, issue: int) -> str:
        """What a failure shows: the run's log, the tmux log of its launches, and any call a stand-in refused."""
        out = []
        for f in [*sorted((self.runs / str(issue)).glob("*/factory.log")), self.runs / f"{issue}.tmux.log",
                  self.state / "unknown.log"]:
            if f.exists():
                out.append(f"--- {f}\n" + "\n".join(self.read(f).splitlines()[-40:]))
        return "\n".join(out)

    def wait_run(self, issue: int) -> str:
        """Wait for the process the issue's tmux session started to exit; its run's status."""
        deadline = time.monotonic() + RUN_DEADLINE_SEC
        while self.session_alive(issue):
            if time.monotonic() > deadline:
                self.fail(f"#{issue}'s run still runs after {RUN_DEADLINE_SEC}s\n{self.diag(issue)}")
            time.sleep(0.2)
        self.assertEqual(self.calls("unknown"), [], self.diag(issue))
        return self.read(self.run_dir(issue) / "status").strip()

    def wait_started(self, issue: int) -> None:
        """Wait for the parallel worker of the issue to write its marker; fail at once when its run exits first."""
        deadline = time.monotonic() + RUN_DEADLINE_SEC
        while not (self.state / f"started-{issue}").exists():
            if not self.session_alive(issue) or time.monotonic() > deadline:
                self.fail(f"#{issue}'s worker never started\n{self.diag(issue)}")
            time.sleep(0.1)

    def ledger(self, run: pathlib.Path) -> list[dict]:
        """The run's call rows, without the grader-file lines freeze writes."""
        rows = [json.loads(line) for line in self.read(run / "ledger.jsonl").splitlines()]
        return [r for r in rows if "event" not in r]

    def last_round(self, run: pathlib.Path) -> int:
        return max(int(p.name.split("-")[1].split(".")[0]) for p in run.glob("round-*.checks"))

    def kill_strays(self) -> None:
        """Release any waiting worker, then kill every process that carries this test's E2E_STATE: a run a failed
        test left, its model call (in a session of its own), and the heartbeat sleep each run leaves for 300 s."""
        (self.state / "release").touch()
        tag = f"E2E_STATE={self.state}".encode()
        for _ in range(50):
            pids = []
            for f in glob.glob("/proc/[0-9]*/environ"):
                try:
                    if tag in pathlib.Path(f).read_bytes().split(b"\0"):
                        pids.append(int(f.split("/")[2]))
                except (OSError, ValueError):
                    continue
            pids = [p for p in pids if p != os.getpid()]
            if not pids:
                return
            for p in pids:
                try:
                    os.kill(p, signal.SIGKILL)
                except OSError:
                    pass
            time.sleep(0.1)

    def test_pass_opens_a_ready_pr(self) -> None:
        self.seed((1, ticket("pass")))
        t = self.tick()
        self.assertEqual(t.stdout, "launched #1\n", t.stderr)
        self.assertEqual(self.wait_run(1), "pr-opened", self.diag(1))
        run = self.run_dir(1)
        prs = list(self.store()["prs"].values())
        self.assertEqual([(p["head"], p["base"], p["draft"]) for p in prs], [("factory/1", "main", False)], prs)
        self.assertIn("Closes #1", prs[0]["body"])
        self.assertIn("The e2e stand-in worker writes done.txt", prs[0]["body"])  # mechanism.md opens the body
        head = self.git(self.bare, "rev-parse", "refs/heads/factory/1")
        self.assertEqual(self.git(self.bare, "log", "-1", "--format=%s", head), "e2e: write done.txt")
        self.assertEqual(self.git(self.bare, "show", f"{head}:done.txt"), "done")
        self.assertRegex(self.read(run / "round-0.checks"), r"(?m)^FAIL done-file:")
        n = self.last_round(run)
        self.assertEqual(n, 1)
        checks = self.read(run / f"round-{n}.checks")
        self.assertRegex(checks, r"(?m)^PASS done-file$")
        self.assertNotRegex(checks, r"(?m)^FAIL")
        self.assertEqual([(r["role"], r["subtype"]) for r in self.ledger(run)],
                         [("worker", "success"), ("judge", "success"), ("reviewer", "success")])
        self.assertEqual(json.loads(self.read(run / f"round-{n}.judge.json"))["verdict"], "pass")
        review = json.loads(self.read(run / f"round-{n}.review.json"))
        self.assertIn("verdict", review)
        self.assertNotIn("unparseable", review)
        self.assertEqual(self.read(run / f"round-{n}.graded.sha").strip(), head)
        # The done-checks' guard ran the target's bin/check in round 0 (its base worktree) and in the worker round.
        wt = self.top / "proj-1"
        self.assertEqual(self.read(self.state / "check.log").splitlines(), [f"{wt}-base", str(wt)])
        # The next tick does not relaunch #1; a cap of 2 leaves a free slot, so the frontier is what passes it over.
        before = (self.workers(), self.launches())
        t = self.tick(FACTORY_MAX_PARALLEL="2")
        self.assertEqual(t.stdout, "nothing to launch\n", t.stderr)
        self.assertEqual((self.workers(), self.launches()), before)
        self.assertEqual(self.calls("unknown"), [])

    def test_fail_ends_stuck_and_is_not_relaunched(self) -> None:
        self.seed((1, ticket("fail")))
        t = self.tick()
        self.assertEqual(t.stdout, "launched #1\n", t.stderr)
        self.assertEqual(self.wait_run(1), "stuck", self.diag(1))
        run = self.run_dir(1)
        self.assertEqual(self.store()["prs"], {})
        self.assertEqual(self.workers(), 2)
        for n in (1, 2):
            self.assertRegex(self.read(run / f"round-{n}.checks"), r"(?m)^FAIL done-file:")
        # The launch assigned #1, so the next tick reads it among the runner's own and passes a stuck run over silently.
        self.assertEqual(self.store()["issues"]["1"]["assignees"], [OWNER])
        before = (self.workers(), self.launches())
        t = self.tick()
        self.assertEqual(t.stdout, "nothing to launch\n", t.stderr)
        self.assertNotIn("#1", t.stderr)
        self.assertEqual(self.read(run / "status").strip(), "stuck")
        self.assertEqual((self.workers(), self.launches()), before)
        self.assertEqual(self.calls("unknown"), [])

    def test_no_result_stops_on_the_environment(self) -> None:
        self.seed((1, ticket("no-result", "ROUND_BUDGET_USD=3")))
        t = self.tick()
        self.assertEqual(t.stdout, "launched #1\n", t.stderr)
        self.assertEqual(self.wait_run(1), "stopped-environment", self.diag(1))
        run = self.run_dir(1)
        worker = [c for c in self.calls("claude") if c["kind"] == "worker"]
        self.assertEqual(len(worker), 1)
        self.assertEqual(worker[0]["argv"][worker[0]["argv"].index("--max-budget-usd") + 1], "3")
        # No result event: the row charges the call's ceiling, the ticket's ROUND_BUDGET_USD, and no round follows.
        self.assertEqual([(r["role"], r["subtype"], r["cost_usd"]) for r in self.ledger(run)],
                         [("worker", "no-result", 3)])
        self.assertTrue((run / "round-0.checks").exists())
        self.assertFalse((run / "round-1.checks").exists())
        self.assertEqual(self.store()["prs"], {})
        self.assertIn("the worker call ended with no result event", self.read(run / "factory.log"))
        self.assertEqual(self.calls("unknown"), [])

    def test_stop_loop_parks_after_the_third_stop(self) -> None:
        # #563: a call that keeps ending with no result relaunched every backoff until next parked it at the third stop.
        self.seed((1, ticket("no-result")))
        for stop in (1, 2, 3):
            t = self.tick()
            self.assertEqual(t.stdout, "launched #1\n", f"launch {stop}: {t.stderr}")
            self.assertEqual(self.wait_run(1), "stopped-environment", self.diag(1))
            status = self.run_dir(1) / "status"
            aged = time.time() - 2 * 3600  # past ENV_BACKOFF_SEC, so only the park can hold #1
            os.utime(status, (aged, aged))
        t = self.tick()
        self.assertEqual(t.stdout, "nothing to launch\n", t.stderr)
        self.assertIn("parked #1: stopped on the environment 3 times in a row", t.stderr)
        self.assertEqual(self.launches(), ["o__r-1"] * 3)
        self.assertEqual(self.workers(), 3)
        self.assertEqual(self.calls("unknown"), [])

    def test_parallel_two_launches_under_the_cap(self) -> None:
        self.seed(*((n, ticket("parallel")) for n in (1, 2, 3)))
        # The first launch starts the tmux server with no cap in its environment, so #2 gets its cap only from next's -e
        # (#573: the caps did not reach the run tmux started).
        t = self.tick()
        self.assertEqual(t.stdout, "launched #1\n", t.stderr)
        self.wait_started(1)
        t = self.tick(FACTORY_MAX_PARALLEL="2")
        self.assertEqual(t.stdout, "launched #2\n", t.stderr)
        self.wait_started(2)
        t = self.tick(FACTORY_MAX_PARALLEL="2")
        self.assertEqual(t.stdout, "nothing to launch\n", t.stderr)
        server = json.loads(self.read(self.state / "tmux/server-env.json"))
        self.assertNotIn("FACTORY_MAX_PARALLEL", server)
        self.assertEqual(self.session(2)["env"]["FACTORY_MAX_PARALLEL"], "2")
        self.assertEqual(self.launches(), ["o__r-1", "o__r-2"])
        self.assertFalse((self.runs / "3").exists())
        self.assertEqual(self.store()["issues"]["3"]["assignees"], [])
        (self.state / "release").touch()
        for n in (1, 2):
            self.assertEqual(self.wait_run(n), "pr-opened", self.diag(n))
        prs = sorted((p["head"], p["draft"]) for p in self.store()["prs"].values())
        self.assertEqual(prs, [("factory/1", False), ("factory/2", False)])
        for n in (1, 2):
            wt = self.top / f"proj-{n}"
            self.assertEqual(self.git(wt, "rev-parse", "--abbrev-ref", "HEAD"), f"factory/{n}")
            self.assertEqual(self.git(wt, "rev-parse", "HEAD"), self.git(self.bare, "rev-parse", f"factory/{n}"))
            self.assertEqual(self.git(self.bare, "log", "-1", "--format=%s", f"factory/{n}"), "e2e: write done.txt")
        self.assertEqual(self.calls("unknown"), [])


if __name__ == "__main__":
    unittest.main()
