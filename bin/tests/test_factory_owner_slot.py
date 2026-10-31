"""holds_slot frees a running run's slot only when its supervisor is surely gone (docs/factory/LOOP.md, Parallel runs).

Each test writes a run dir with status `running` and an `owner` line, sources bin/factory (FACTORY_SOURCED=1) with
`alert` stubbed to a file, and asks holds_slot. A freed run reads stopped-environment and alerts once; a held one
keeps `running` and sends nothing. A run dir with a `lease` file is judged by the flock lease alone (LeaseSlotTests);
one without it by the owner line (OwnerSlotTests).
"""

from __future__ import annotations

import datetime
import hashlib
import os
import pathlib
import signal
import subprocess
import tempfile
import time
import unittest
import uuid

import bsd_shapes

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG")
OLD = "Thu Jan  1 00:00:00 1970"
# The lease path runs where the script says it does (flock(1) and bash 4.1+), so a Mac with Homebrew's flock and bash
# 3.2 still runs the owner-line tests and skips the lease ones.
HAVE_FLOCK = subprocess.run(["bash", "-c", '. bin/factory; echo "$HAVE_FLOCK"'], cwd=ROOT,
                            env={**os.environ, "FACTORY_SOURCED": "1"}, stdin=subprocess.DEVNULL,
                            capture_output=True, text=True, check=True).stdout.strip() != ""


def lstart(pid: int) -> str:
    out = subprocess.run(["ps", "-o", "lstart=", "-p", str(pid)], env={**os.environ, "TZ": "UTC", "LC_ALL": "C"},
                         capture_output=True, text=True, check=True).stdout
    return out.rstrip()  # macOS pads lstart with trailing spaces; cmd_run trims them


def dead_pid() -> int:
    p = subprocess.Popen(["true"])
    p.wait()
    return p.pid


def state(pid: int) -> str:
    out = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)], capture_output=True, text=True, check=False).stdout
    return out.strip()[:1]


def wait_until(cond) -> None:
    for _ in range(100):
        if cond():
            return
        time.sleep(0.05)
    raise AssertionError("condition never held")


class SlotCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.run_dir = self.top / "runs" / "7" / "abcd1234"
        self.run_dir.mkdir(parents=True)
        (self.run_dir / "status").write_text("running\n")
        self.alerts = self.top / "alerts.txt"
        self.path = os.environ["PATH"]

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
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env={**base, "FACTORY_SOURCED": "1", "PATH": self.path},
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


class OwnerSlotTests(SlotCase):
    flock = HAVE_FLOCK

    def test_dead_owner_frees_the_slot_and_reads_stopped_environment(self) -> None:
        self.owner(f"{dead_pid()} {OLD}")
        self.assert_freed()

    def test_padded_owner_line_with_a_dead_pid_frees_the_slot(self) -> None:
        # cmd_run on macOS before #448 wrote lstart with its trailing spaces.
        self.owner(f"{dead_pid()} {OLD}    ")
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
        # A malformed line also holds, so the spy proves holds_slot parsed the line and asked owner_gone.
        pid, consulted = self.live(), self.top / "consulted"
        self.owner(f"{pid} {lstart(pid)}")
        self.assert_held(f'eval "real_$(declare -f owner_gone)"\n'
                         f'owner_gone() {{ printf \'%s\\n\' "$*" > \'{consulted}\'; real_owner_gone "$@"; }}')
        self.assertEqual(consulted.read_text(), f"{pid} {lstart(pid)}\n")

    def test_live_pid_with_a_malformed_start_holds_the_slot(self) -> None:
        self.owner(f"{self.live()} garbage")
        self.assert_held()

    def test_start_time_two_seconds_off_holds_the_slot(self) -> None:
        # A wall-clock step moves ps lstart; a gap this small is the same process, not a reused pid.
        pid = self.live()
        t = datetime.datetime.strptime(lstart(pid), "%a %b %d %H:%M:%S %Y") - datetime.timedelta(seconds=2)
        self.owner(f"{pid} {t:%a %b} {t.day:2d} {t:%H:%M:%S %Y}")
        self.assert_held()

    def test_date_failing_or_printing_nothing_holds_the_slot(self) -> None:
        pid = self.live()
        self.owner(f"{pid} {OLD}")
        for stub in ("date() { return 1; }", "date() { :; }"):
            with self.subTest(stub=stub):
                self.assert_held(stub)

    def test_one_date_printing_nothing_holds_the_slot(self) -> None:
        # An empty epoch must not read as 0, or a live owner two seconds off would look 56 years gone.
        pid = self.live()
        live = lstart(pid)
        t = datetime.datetime.strptime(live, "%a %b %d %H:%M:%S %Y") - datetime.timedelta(seconds=2)
        rec = f"{t:%a %b} {t.day:2d} {t:%H:%M:%S %Y}"
        self.owner(f"{pid} {rec}")
        for target in (live, rec):
            stub = f'date() {{ case "$*" in *"{target}"*) return 0 ;; esac; command date "$@"; }}'
            with self.subTest(target=target):
                self.assert_held(stub)

    def test_ps_failing_on_a_live_pid_holds_the_slot(self) -> None:
        pid = self.live()
        self.owner(f"{pid} {OLD}")
        for stub in ("ps() { return 1; }", "ps() { :; }"):
            with self.subTest(stub=stub):
                self.assert_held(stub)

    def test_relaunch_writes_its_owner_and_running_before_preparing(self) -> None:
        # A relaunch over a reaped run (stopped-environment, dead owner) must hold its slot through the long
        # preparation, so cmd_run's first step after the launch line already sees this process as the owner.
        body = "# Owner fixture\n\n## Worker\nworker: claude\n"
        ticket = self.top / "relaunch.md"
        ticket.write_text(body)
        run_dir = self.top / "runs" / "relaunch" / hashlib.sha256(body.rstrip("\n").encode()).hexdigest()[:8]
        run_dir.mkdir(parents=True)
        (run_dir / "status").write_text("stopped-environment\n")
        (run_dir / "owner").write_text(f"{dead_pid()} {OLD}\n")
        seen = self.top / "seen"
        script = (f". bin/factory\n{'' if self.flock else 'HAVE_FLOCK='}\nMAIN_CHECKOUT='{self.top}'\n"
                  "assert_target_ready() { :; }; claude_version_ok() { echo ok; }\n"
                  "nav_arm_resolve() { { cat \"$RUN/owner\" \"$RUN/status\"; echo \"$$\"; "
                  "TZ=UTC LC_ALL=C ps -o lstart= -p $$; "
                  "if [ ! -f \"$RUN/lease\" ]; then echo none; elif flock -n \"$RUN/lease\" true; then echo free; "
                  f"else echo held; fi; }} > '{seen}'; exit 0; }}\n"
                  f"cmd_run '{ticket}'")
        base = {k: v for k, v in os.environ.items()
                if k not in INHERITED and k not in ("FACTORY_FROZEN", "FACTORY_NAV_ARM")}
        proc = subprocess.Popen(["bash", "-c", script], cwd=ROOT,
                                env={**base, "FACTORY_SOURCED": "1", "FACTORY_RUNS_ROOT": str(self.top / "runs"),
                                     "PATH": self.path},
                                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, err = proc.communicate()
        self.assertTrue(seen.exists(), err)
        owner, status, pid, start, lease = seen.read_text().splitlines()
        self.assertEqual(int(pid), proc.pid)
        self.assertEqual(owner, f"{pid} {start.rstrip()}")
        self.assertEqual(status, "running")
        self.assertEqual(lease, "held" if self.flock else "none")   # macOS has no flock(1): the owner line decides

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

    def test_dead_owner_holds_while_its_model_call_lives(self) -> None:
        # call_start puts the call in a session of its own, so a SIGKILL to the supervisor's group leaves it running
        # (reparented to init) and writing the worktree; the slot holds until the call is gone.
        ready = self.top / "ready"
        script = (f". bin/factory\nRUN='{self.run_dir}'; LOG='{self.top}/factory.log'\n"
                  f"call_start '{self.top}' sh -c 'echo $$ > \"{ready}\"; exec sleep 60'\nwait")
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        sup = subprocess.Popen(["bash", "-c", script], cwd=ROOT,
                               env={**base, "FACTORY_SOURCED": "1", "PATH": self.path}, stdin=subprocess.DEVNULL, start_new_session=True)
        wait_until(lambda: ready.exists() and ready.read_text().strip() != "")
        call = int(ready.read_text())
        self.addCleanup(lambda: subprocess.run(["pkill", "-KILL", "-g", str(call)], check=False))
        os.killpg(sup.pid, signal.SIGKILL)
        sup.wait()
        self.owner(f"{sup.pid} {OLD}")
        self.assert_held()
        os.killpg(call, signal.SIGKILL)
        wait_until(lambda: not self.holds())
        self.assertEqual((self.run_dir / "status").read_text(), "stopped-environment\n")
        self.assertEqual(len(self.alerts.read_text().splitlines()), 1)


@unittest.skipUnless(HAVE_FLOCK, "the lease needs flock(1) and bash 4.1+")
class LeaseSlotTests(SlotCase):
    """A run dir with a `lease` holds its slot exactly while some process holds an flock on it, whatever `owner` says."""

    def setUp(self) -> None:
        super().setUp()
        (self.run_dir / "lease").touch()

    def hold(self, script: str) -> int:
        # A shell in a session of its own takes the lease on fd 9, then runs script, which touches $2 once it is ready.
        ready = self.top / "ready"
        p = subprocess.Popen(["bash", "-c", f'exec 9>> "$1" && flock -n 9 && {{ {script}; }}', "_",
                              str(self.run_dir / "lease"), str(ready)], start_new_session=True)
        self.addCleanup(p.wait)   # cleanups run last in, first out: the kill first
        self.addCleanup(lambda: subprocess.run(["pkill", "-KILL", "-g", str(p.pid)], check=False))
        wait_until(ready.exists)
        return p.pid

    def test_no_holder_frees_the_slot_once_though_the_owner_pid_lives(self) -> None:
        self.owner(f"{os.getpid()} {lstart(os.getpid())}")
        self.assert_freed()
        self.assertFalse(self.holds())
        self.assertEqual(len(self.alerts.read_text().splitlines()), 1)

    def test_live_holder_holds_the_slot_whatever_owner_says(self) -> None:
        self.owner(f"{dead_pid()} {OLD}")
        self.hold('touch "$2"; exec sleep 60')
        self.assert_held()

    def test_child_that_outlives_its_supervisor_holds_the_slot_until_it_exits(self) -> None:
        # The supervisor exits and is reaped; the sleep it started inherited fd 9 and keeps the lease.
        self.owner(f"{dead_pid()} {OLD}")
        group = self.hold('sleep 60 & touch "$2"; exit 0')
        self.assert_held()
        os.killpg(group, signal.SIGKILL)
        wait_until(lambda: not self.holds())
        self.assertEqual((self.run_dir / "status").read_text(), "stopped-environment\n")
        self.assertEqual(len(self.alerts.read_text().splitlines()), 1)

    @unittest.skipUnless(os.path.exists("/proc/self/environ"), "call_tagged reads /proc")
    def test_tagged_call_process_that_closed_the_lease_holds_the_slot(self) -> None:
        # Node's child processes close the descriptors they are not given, so a model call's tool shell can outlive
        # every lease holder; it still carries the call's FACTORY_CALL_TAG, and the slot holds until it exits.
        tag = f"test.{uuid.uuid4().hex}"   # bin/check may itself run inside a call, with a tag of its own
        (self.run_dir / "call").write_text(f"{dead_pid()} {tag}\n")
        self.owner(f"{dead_pid()} {OLD}")
        p = subprocess.Popen(["sleep", "60"], env={**os.environ, "FACTORY_CALL_TAG": tag})
        self.addCleanup(p.wait)
        self.addCleanup(p.kill)
        self.assert_held()
        p.kill()
        p.wait()
        self.assert_freed()

    def test_launch_refused_by_a_held_lease_leaves_the_incumbent_as_it_was(self) -> None:
        # Both launches of one ticket body share the run dir; the refused one must not write its status, `launched`
        # or launch line, or the incumbent would lose its slot, its MAX_HOURS clock or its round.
        body = "# Lease fixture\n\n## Worker\nworker: claude\n"
        ticket = self.top / "contend.md"
        ticket.write_text(body)
        run_dir = self.top / "runs" / "contend" / hashlib.sha256(body.rstrip("\n").encode()).hexdigest()[:8]
        run_dir.mkdir(parents=True)
        for name, text in (("status", "running\n"), ("launched", "12345\n"), ("factory.log", "incumbent\n")):
            (run_dir / name).write_text(text)
        p = subprocess.Popen(["flock", str(run_dir / "lease"), "sleep", "60"], start_new_session=True)
        self.addCleanup(p.wait)
        self.addCleanup(lambda: subprocess.run(["pkill", "-KILL", "-g", str(p.pid)], check=False))
        wait_until(lambda: subprocess.run(["flock", "-n", str(run_dir / "lease"), "true"]).returncode != 0)
        script = (f". bin/factory\nMAIN_CHECKOUT='{self.top}'\n"
                  "assert_target_ready() { :; }; claude_version_ok() { echo ok; }\n"
                  # The 65 s wait, made a single try.
                  'flock() { if [ "$1" = -w ]; then shift 2; set -- -n "$@"; fi; command flock "$@"; }\n'
                  f"cmd_run '{ticket}'")
        base = {k: v for k, v in os.environ.items()
                if k not in INHERITED and k not in ("FACTORY_FROZEN", "FACTORY_NAV_ARM")}
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT,
                              env={**base, "FACTORY_SOURCED": "1", "FACTORY_RUNS_ROOT": str(self.top / "runs"),
                                   "PATH": self.path},
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("another launch of this ticket, or a process one left running, holds it", proc.stderr)
        self.assertEqual((run_dir / "status").read_text(), "running\n")
        self.assertEqual((run_dir / "launched").read_text(), "12345\n")
        self.assertEqual((run_dir / "factory.log").read_text(), "incumbent\n")
        self.run_dir = run_dir
        self.assert_held()

    def launch(self, ticket: pathlib.Path, extra: str = "", env: dict[str, str] | None = None
               ) -> subprocess.CompletedProcess[str]:
        # cmd_run on a file ticket, with the target and claude checks stubbed and flock's 65 s wait made a single try.
        script = (f". bin/factory\nMAIN_CHECKOUT='{self.top}'\n"
                  "assert_target_ready() { :; }; claude_version_ok() { echo ok; }\n"
                  'flock() { if [ "$1" = -w ]; then shift 2; set -- -n "$@"; fi; command flock "$@"; }\n'
                  f"{extra}\ncmd_run '{ticket}'")
        base = {k: v for k, v in os.environ.items()
                if k not in INHERITED and k not in ("FACTORY_FROZEN", "FACTORY_NAV_ARM", "FACTORY_SLOT_FD")}
        return subprocess.run(["bash", "-c", script], cwd=ROOT,
                              env={**base, "FACTORY_SOURCED": "1", "FACTORY_RUNS_ROOT": str(self.top / "runs"),
                                   "PATH": self.path, **(env or {})},
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False, timeout=30)

    def ticket(self, name: str) -> tuple[pathlib.Path, pathlib.Path]:
        body = "# Lease fixture\n\n## Worker\nworker: claude\n"
        ticket = self.top / f"{name}.md"
        ticket.write_text(body)
        run_dir = self.top / "runs" / name / hashlib.sha256(body.rstrip("\n").encode()).hexdigest()[:8]
        run_dir.mkdir(parents=True)
        return ticket, run_dir

    @unittest.skipUnless(os.path.exists("/proc/self/environ"), "call_tagged reads /proc")
    def test_launch_refused_while_a_tagged_call_of_the_last_run_lives(self) -> None:
        # The killed run's model call closed the lease and still writes the worktree; a relaunch must not prepare it,
        # on a host with no flock (a Mac, HAVE_FLOCK=) too.
        for name, extra in (("orphan", ""), ("orphan-noflock", "HAVE_FLOCK=")):
            with self.subTest(name):
                ticket, run_dir = self.ticket(name)
                tag = f"test.{uuid.uuid4().hex}"
                files = {"status": "running\n", "launched": "12345\n", "owner": f"{dead_pid()} {OLD}\n",
                         "factory.log": "incumbent\n", "call": f"{dead_pid()} {tag}\n"}
                for file, text in files.items():
                    (run_dir / file).write_text(text)
                p = subprocess.Popen(["sleep", "60"], env={**os.environ, "FACTORY_CALL_TAG": tag})
                self.addCleanup(p.wait)
                self.addCleanup(p.kill)
                proc = self.launch(ticket, extra)
                self.assertEqual(proc.returncode, 4, proc.stderr)
                self.assertIn("still runs", proc.stderr)
                for file, text in files.items():
                    self.assertEqual((run_dir / file).read_text(), text, file)

    def test_frozen_pass_keeps_the_lease_it_inherited(self) -> None:
        # The frozen re-exec inherits the locked descriptor; a second open of `lease` in it would wait on its own lock.
        ticket, run_dir = self.ticket("frozen")
        seen = self.top / "seen"
        proc = self.launch(ticket, (f'exec {{FACTORY_SLOT_FD}}>> "{run_dir}/lease"; flock -n "$FACTORY_SLOT_FD"\n'
                                    f"export FACTORY_SLOT_FD; nav_arm_resolve() {{ touch '{seen}'; exit 0; }}"),
                           {"FACTORY_FROZEN": str(run_dir / "frozen" / "factory")})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(seen.exists(), proc.stderr)

    def test_heartbeat_does_not_hold_the_lease(self) -> None:
        # A beat outlives a killed supervisor by up to 300 s; it must not keep the run's slot meanwhile.
        hb = self.top / "hb"
        script = (f". bin/factory\nalert() {{ :; }}; LOG=/dev/null\n"
                  f'exec {{FACTORY_SLOT_FD}}>> "{self.run_dir}/lease"; flock -n "$FACTORY_SLOT_FD" || exit 7\n'
                  f"export FACTORY_SLOT_FD; heartbeat_start; echo \"$HEARTBEAT\" > '{hb}'")
        base = {k: v for k, v in os.environ.items() if k not in INHERITED}
        sup = subprocess.Popen(["bash", "-c", script], cwd=ROOT, env={**base, "FACTORY_SOURCED": "1", "PATH": self.path},
                               stdin=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(lambda: subprocess.run(["pkill", "-KILL", "-g", str(sup.pid)], check=False))
        self.assertEqual(sup.wait(timeout=30), 0)
        self.assertNotIn(state(int(hb.read_text())), ("", "Z"))   # the beat outlives its supervisor
        self.assert_freed()

    def test_launched_with_no_status_holds_only_while_its_lease_is_held(self) -> None:
        # A launch killed between `launched` and its first status leaves no status; its free lease frees the slot.
        (self.run_dir / "status").unlink()
        (self.run_dir / "launched").write_text("12345\n")
        self.assertFalse(self.holds())
        self.hold('touch "$2"; exec sleep 60')
        self.assertTrue(self.holds())
        self.assertFalse((self.run_dir / "status").exists())
        self.assertFalse(self.alerts.exists())


class MacShapeOwnerSlotTests(OwnerSlotTests):
    """Every test again with macOS ps and date (bsd_shapes) and no flock(1), so Linux CI guards the Mac paths too."""

    flock = False

    def setUp(self) -> None:
        super().setUp()
        self.path = bsd_shapes.path(self.top / "bin")


if __name__ == "__main__":
    unittest.main()
