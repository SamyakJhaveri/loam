"""`bin/factory next` parks a ticket only on a run of its current body, so a body edit relaunches it,
and it lints every candidate before picking one, so a labelled issue that is not a ticket is skipped (#314).

`bin/factory` is sourced (FACTORY_SOURCED=1) with a temp runs root. park_status is called directly,
and cmd_next --dry-run (or --frontier) runs with gh, the origin, the login and version probes, and the toolchain gate stubbed as shell functions,
so the frontier lines carry the bodies the way the real query does. No network, no tmux, no `claude`.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

# The smallest body `bin/factory lint` accepts, as the issue body gh returns it (no trailing newline).
CLEAN = (ROOT / "bin/tests/fixtures/clean-ticket.md").read_text().rstrip("\n")

# Carries the label but is not a ticket: no done-checks block, no sections. #314's case.
NOT_A_TICKET = "A note that someone labelled ready-for-agent.\n\nNo done-checks block here."

# An editor GraphQL returns as null with a lastEditedAt: the body was edited by an account GitHub no longer names.
UNNAMED = "<unnamed>"


def sourced(script: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Run `script` in a bash that has sourced bin/factory from the repo root."""
    return subprocess.run(
        ["bash", "-c", f". bin/factory\n{script}"],
        cwd=ROOT, env={**os.environ, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), **(env or {})},
        capture_output=True, text=True, check=False,
    )


def key(body: str) -> str:
    """The run-dir key cmd_run computes: the first 8 hex digits of the body's sha256."""
    return hashlib.sha256(body.encode()).hexdigest()[:8]


class ParkingTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs = pathlib.Path(tmp.name)
        log = tempfile.TemporaryDirectory()
        self.addCleanup(log.cleanup)
        self.gql_log = pathlib.Path(log.name) / "gql.log"
        self.gql_log.touch()
        self.gh_log = pathlib.Path(log.name) / "gh.log"
        self.gh_log.touch()

    def run_dir(self, issue: int, body: str, status: str) -> None:
        d = self.runs / str(issue) / key(body)
        d.mkdir(parents=True)
        (d / "status").write_text(status + "\n")
        (d / "launched").write_text("1\n")

    def park_status(self, issue: int, body: str) -> str:
        proc = sourced(f'park_status {issue} "$BODY_ARG"', {"FACTORY_RUNS_ROOT": str(self.runs), "BODY_ARG": body})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.strip()

    def next_dry_run(self, *frontier: tuple[int, str], mine: tuple[tuple[int, str], ...] = (),
                     authors: dict[int, str] | None = None, editors: dict[int, str | None] | None = None,
                     now: int | None = None, pre: str = "", flag: str = "--dry-run",
                     **env: str) -> subprocess.CompletedProcess[str]:
        """cmd_next `flag` (--dry-run by default) over the given unassigned (issue, body) frontier, lowest number first as gh sorts it,
        and `mine`, the ready-for-agent issues assigned to the runner. Each issue is written by `authors`' login,
        SamyakJhaveri by default, and last edited by `editors`' login (None: the editor call fails; UNNAMED: a null
        editor with a lastEditedAt), by no one by default. Each editor call is logged to GQL_LOG, every gh call to GH_LOG. `now` pins the
        epoch `date -u +%s` prints, so a backoff boundary does not move while the test runs."""
        def lines(issues: tuple[tuple[int, str], ...]) -> str:
            return " ".join(f"'{issue} {(authors or {}).get(issue, 'SamyakJhaveri')} {base64.b64encode(body.encode()).decode()}'"
                            for issue, body in issues) or "''"
        def doc(who: str) -> str:
            issue = {"editor": None, "lastEditedAt": "2026-10-30T00:00:00Z"} if who == UNNAMED else {"editor": {"login": who}}
            return json.dumps({"data": {"repository": {"issue": issue}}})
        edits = "".join(f'*" number={issue} "*) {"return 1" if who is None else f"doc={doc(who)!r}"} ;; '
                        for issue, who in (editors or {}).items())
        clock = "" if now is None else f'date() {{ if [ "$*" = "-u +%s" ]; then echo {now}; else command date "$@"; fi; }}; '
        stubs = (pre + clock + "assert_toolchain_env() { :; }; claude_logged_in() { :; }; claude_version_ok() { :; }; target_repo() { echo o/r; }; "
                 'gh() { echo "$*" >> "$GH_LOG"; '
                 "case $2 in graphql) local a p= q= doc='{\"data\":{\"repository\":{\"issue\":{\"editor\":null}}}}'; "
                 'for a; do [ "$p" = --jq ] && q=$a; p=$a; done; echo "$*" >> "$GQL_LOG"; '
                 f"case \"$* \" in {edits}esac; jq -r \"$q\" <<<\"$doc\" ;; repos/*) printf '%s\\n' {lines(frontier)} ;; "
                 f"/issues\\?*) printf '%s\\n' {lines(mine)} ;; esac; }}; "
                 f"cmd_next {flag}")
        return sourced(stubs, {"FACTORY_MAX_PARALLEL": "1", "FACTORY_RUNS_ROOT": str(self.runs), "GQL_LOG": str(self.gql_log),
                               "GH_LOG": str(self.gh_log), **env})

    def test_old_body_abandon_does_not_park_a_new_body(self) -> None:
        self.run_dir(7, CLEAN + "\nthe old body", "abandon")
        self.assertEqual(self.park_status(7, CLEAN + "\nthe new body"), "none")
        proc = self.next_dry_run((7, CLEAN + "\nthe new body"))
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        self.assertNotIn("parked", proc.stderr)

    def test_same_body_abandon_parks(self) -> None:
        body = CLEAN + "\n- a list item"
        self.run_dir(7, body, "abandon")
        self.assertEqual(self.park_status(7, body), "abandon")
        proc = self.next_dry_run((7, body))
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("parked #7: last run exited abandon", proc.stderr)

    def test_same_body_stopped_environment_waits_an_hour_then_relaunches(self) -> None:
        # stopped-environment pages at once, so a lasting machine fault must not page every tick (#440).
        body = CLEAN
        self.run_dir(7, body, "stopped-environment")
        self.assertEqual(self.park_status(7, body), "stopped-environment")
        proc = self.next_dry_run((7, body))
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("waiting #7: last run stopped on the environment", proc.stderr)
        past = time.time() - 3601
        os.utime(self.runs / "7" / key(body) / "status", (past, past))
        proc = self.next_dry_run((7, body))
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        # On a pinned clock: half the hour still waits, and the stop exactly an hour old relaunches.
        now = int(time.time())
        for age, out in ((1800, "nothing to launch"), (3599, "nothing to launch"), (3600, "would launch #7")):
            with self.subTest(age=age):
                os.utime(self.runs / "7" / key(body) / "status", (now - age, now - age))
                proc = self.next_dry_run((7, body), now=now)
                self.assertEqual(proc.stdout.strip(), out, proc.stderr)

    def test_same_body_stopped_daily_waits_today_and_relaunches_on_a_later_day(self) -> None:
        # A daily-budget stop says nothing about the ticket (#386): the UTC date of its status file decides.
        self.run_dir(7, CLEAN, "stopped-daily")
        proc = self.next_dry_run((7, CLEAN))
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("waiting #7: daily budget spent", proc.stderr)
        self.assertNotIn("parked", proc.stderr)
        os.utime(self.runs / "7" / key(CLEAN) / "status", (86400, 86400))
        proc = self.next_dry_run((7, CLEAN))
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)

    def test_runner_assigned_issue_relaunches_only_after_a_relaunchable_stop(self) -> None:
        # The launch assigned the issue to the runner and nothing unassigns it (#386, #440): of the runner's own,
        # a stopped-daily run of an earlier UTC day, a stopped-environment run past its backoff, and a stopped run
        # launch, and the rest are skipped without a line. Four slots, so #6's running run, which holds one, leaves room.
        for issue, status in ((5, "stopped-cap"), (6, "running"), (8, "pr-opened")):
            self.run_dir(issue, CLEAN, status)
        for status in ("stopped-daily", "stopped-environment", "stopped"):
            with self.subTest(status=status):
                self.run_dir(7, CLEAN, status)
                mine = tuple((n, CLEAN) for n in (5, 6, 7, 8))
                if status == "stopped-environment":
                    # Every launch assigns the issue, so the hour's wait must hold on this path: a later clean #9 launches.
                    proc = self.next_dry_run((9, CLEAN), mine=mine, FACTORY_MAX_PARALLEL="4")
                    self.assertEqual(proc.stdout.strip(), "would launch #9", proc.stderr)
                    self.assertIn("waiting #7: last run stopped on the environment", proc.stderr)
                os.utime(self.runs / "7" / key(CLEAN) / "status", (86400, 86400))
                proc = self.next_dry_run(mine=mine, FACTORY_MAX_PARALLEL="4")
                self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
                self.assertEqual(proc.stderr, "")
                shutil.rmtree(self.runs / "7")
        proc = self.next_dry_run(mine=tuple((n, CLEAN) for n in (5, 6, 8)), FACTORY_MAX_PARALLEL="4")
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertEqual(proc.stderr, "")

    def test_runner_assigned_ticket_defect_relaunches_only_after_a_body_edit(self) -> None:
        # The launch assigned #7 to the runner; its run ended ticket-defect, so the same body parks, and the body the
        # owner corrects keys a new run dir with no run yet, which launches like a new ticket (#467, #468).
        self.run_dir(7, CLEAN, "ticket-defect")
        proc = self.next_dry_run(mine=((7, CLEAN),))
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        proc = self.next_dry_run(mine=((7, CLEAN + "\n- the corrected line"),))
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)

    def test_runner_assigned_issue_that_never_ran_is_held(self) -> None:
        # Assigned to the runner by hand with no run of any body: the owner holds it, so next leaves it; the same
        # issue unassigned launches. A lint line under the issue dir is not a run.
        (self.runs / "7").mkdir()
        (self.runs / "7" / "owner-events.jsonl").write_text("{}\n")
        proc = self.next_dry_run(mine=((7, CLEAN),))
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertEqual(proc.stderr, "")
        proc = self.next_dry_run((7, CLEAN))
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)

    def test_edited_body_waits_while_a_run_of_the_old_body_runs_or_awaits_merge(self) -> None:
        # Both bodies share the issue's branch and worktree, so a spare slot must not launch the edited body beside
        # the old body's live run, its live model call, or its open PR (pr-opened with no pr-closed marker, even with
        # the worktree gone, as the overnight driver leaves it); assigned or not. A closed PR frees it, worktree or not.
        edited = CLEAN + "\n- the corrected line"
        co = self.runs.parent / f"{self.runs.name}-co"
        self.addCleanup(shutil.rmtree, co.parent / f"{co.name}-7", True)
        pre = f"MAIN_CHECKOUT='{co}'; "
        for case in ("running", "call", "pr-opened"):
            with self.subTest(case=case):
                self.run_dir(7, CLEAN, {"call": "stopped-environment"}.get(case, case))
                d = self.runs / "7" / key(CLEAN)
                if case == "call":
                    os.utime(d / "status", (86400, 86400))
                    p = subprocess.Popen(["sleep", "60"], start_new_session=True)
                    self.addCleanup(p.wait)
                    self.addCleanup(subprocess.run, ["kill", "-KILL", "--", f"-{p.pid}"], check=False)
                    (d / "call").write_text(f"{p.pid} test.{key(str(p.pid))}\n")
                if case == "pr-opened":
                    (d / "factory.log").write_text(
                        "2026-10-31T00:00:00Z EXIT pr-opened (0): https://github.com/o/r/pull/9 after 1 rounds\n")
                for frontier, mine in ((((7, edited),), ()), ((), ((7, edited),))):
                    proc = self.next_dry_run(*frontier, mine=mine, pre=pre, FACTORY_MAX_PARALLEL="2")
                    self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
                    self.assertIn("waiting #7: a run of another body still runs or awaits merge", proc.stderr)
                if case == "call":
                    subprocess.run(["kill", "-KILL", "--", f"-{p.pid}"], check=False)
                    p.wait()
                if case == "pr-opened":
                    (co.parent / f"{co.name}-7").mkdir()
                    (d / "pr-closed").write_text("2026-10-31T01:00:00Z\n")
                proc = self.next_dry_run(mine=((7, edited),), pre=pre, FACTORY_MAX_PARALLEL="2")
                expect = "nothing to launch" if case == "running" else "would launch #7"
                self.assertEqual(proc.stdout.strip(), expect, proc.stderr)
                shutil.rmtree(self.runs / "7")

    def test_runner_assigned_stop_waits_while_its_stop_file_remains(self) -> None:
        # cmd_run exits stopped at once while FACTORY_STOP is in the run dir, so #7 must not take the pick from #8
        # every tick (#440); removing the file makes it eligible again.
        self.run_dir(7, CLEAN, "stopped")
        (self.runs / "7" / key(CLEAN) / "FACTORY_STOP").touch()
        proc = self.next_dry_run((8, CLEAN), mine=((7, CLEAN),))
        self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
        self.assertEqual(proc.stderr, "")
        (self.runs / "7" / key(CLEAN) / "FACTORY_STOP").unlink()
        proc = self.next_dry_run((8, CLEAN), mine=((7, CLEAN),))
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)

    def test_unassigned_stop_waits_while_its_stop_file_remains(self) -> None:
        # A run stopped before prepare_worktree never assigned its issue, so the skip must hold for the unassigned too.
        self.run_dir(7, CLEAN, "stopped")
        (self.runs / "7" / key(CLEAN) / "FACTORY_STOP").touch()
        proc = self.next_dry_run((7, CLEAN), (8, CLEAN))
        self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
        self.assertEqual(proc.stderr, "")

    def test_relaunchable_run_waits_while_a_process_of_it_still_runs(self) -> None:
        # A stuck model call outlives finish stopped-environment; cmd_run refuses a relaunch while it, or any process
        # holding the run's lease, still runs, and writes no status, so #7 must not take the pick from #8 every tick.
        cases = ["call"] + (["lease"] if sourced('echo "$HAVE_FLOCK"').stdout.strip() else [])
        for holder in cases:
            with self.subTest(holder=holder):
                self.run_dir(7, CLEAN, "stopped-environment")
                d = self.runs / "7" / key(CLEAN)
                os.utime(d / "status", (86400, 86400))
                if holder == "call":
                    p = subprocess.Popen(["sleep", "60"], start_new_session=True)
                    self.addCleanup(p.wait)
                    self.addCleanup(subprocess.run, ["kill", "-KILL", "--", f"-{p.pid}"], check=False)
                    (d / "call").write_text(f"{p.pid} test.{key(str(p.pid))}\n")
                else:
                    (d / "lease").touch()
                    p = subprocess.Popen(["flock", str(d / "lease"), "sleep", "60"], start_new_session=True)
                    self.addCleanup(p.wait)
                    self.addCleanup(subprocess.run, ["kill", "-KILL", "--", f"-{p.pid}"], check=False)
                    for _ in range(100):
                        if subprocess.run(["flock", "-n", str(d / "lease"), "true"]).returncode != 0:
                            break
                        time.sleep(0.05)
                # A live call also holds #7's slot whatever its status (#467), so #8 needs a second slot.
                slots = "2" if holder == "call" else "1"
                if holder == "call":
                    proc = self.next_dry_run((8, CLEAN), mine=((7, CLEAN),))
                    self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
                proc = self.next_dry_run((8, CLEAN), mine=((7, CLEAN),), FACTORY_MAX_PARALLEL=slots)
                self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
                self.assertIn("waiting #7: a process of its last run still runs", proc.stderr)
                subprocess.run(["kill", "-KILL", "--", f"-{p.pid}"], check=False)
                p.wait()
                proc = self.next_dry_run((8, CLEAN), mine=((7, CLEAN),))
                self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
                shutil.rmtree(self.runs / "7")

    # cmd_run's launch with GitHub, the gates and bin/alert stubbed; assert_parallel, the first step after the launch's
    # state is written, ends it the way the case needs, and the stop is aged past the hour's backoff.
    ENV_STOP = 'finish stopped-environment "the worker call returned no result event"'

    def launch(self, issue: int, body: str, outcome: str = ENV_STOP, age: int = 86400, stubs: str = "") -> None:
        d = self.runs / str(issue) / key(body)
        script = (f"load_ticket() {{ ISSUE={issue}; KEY={issue}; REPO=o/r; IS_FILE=0; BODY=\"$BODY_ARG\"; }}; "
                  "assert_target_ready() { :; }; claude_version_ok() { :; }; owner_events() { :; }; alert() { :; }; "
                  f"assert_parallel() {{ {outcome}; }}; {stubs}cmd_run {issue}")
        sourced(script, {"FACTORY_RUNS_ROOT": str(self.runs), "BODY_ARG": body, "FACTORY_BY_NEXT": "1"})
        self.assertIn("===== launch =====", (d / "factory.log").read_text())
        if (d / "status").exists():
            os.utime(d / "status", (age, age))

    def test_three_environment_stops_with_no_round_progress_park(self) -> None:
        # A worker call with no result event stops before its round's checks, so a relaunch reruns the same round and
        # MAX_ROUNDS never trips; every relaunch costs ROUND_BUDGET_USD and a page (#547). The third such stop in a row parks.
        mine = ((7, CLEAN),)
        self.launch(7, CLEAN, 'echo CHECKS-END > "$RUN/round-0.checks"; ' + self.ENV_STOP)
        for _ in range(2):
            proc = self.next_dry_run(mine=mine)
            self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
            self.launch(7, CLEAN)
        proc = self.next_dry_run((8, CLEAN), mine=mine)
        self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
        self.assertIn("parked #7: stopped on the environment 3 times in a row with no new round since", proc.stderr)

    def test_a_round_between_environment_stops_resets_the_count(self) -> None:
        mine = ((7, CLEAN),)
        self.launch(7, CLEAN)
        self.launch(7, CLEAN, 'echo CHECKS-END > "$RUN/round-0.checks"; ' + self.ENV_STOP)   # round 0 before this stop
        self.launch(7, CLEAN)
        proc = self.next_dry_run(mine=mine)
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        self.assertNotIn("parked", proc.stderr)
        self.launch(7, CLEAN)
        proc = self.next_dry_run(mine=mine)
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("parked #7", proc.stderr)

    def test_a_daily_stop_between_environment_stops_keeps_the_count(self) -> None:
        # A stopped-daily makes no worker call and writes no round, so it must not clear the count, or env, env, daily
        # would loop for good; while it waits for its UTC day it is not parked.
        mine = ((7, CLEAN),)
        self.launch(7, CLEAN)
        self.launch(7, CLEAN)
        self.launch(7, CLEAN, 'finish stopped-daily "the daily budget is spent"', age=int(time.time()))
        proc = self.next_dry_run(mine=mine)
        self.assertIn("waiting #7: daily budget spent", proc.stderr)
        self.assertNotIn("parked", proc.stderr)
        os.utime(self.runs / "7" / key(CLEAN) / "status", (86400, 86400))
        proc = self.next_dry_run(mine=mine)
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        self.launch(7, CLEAN)
        proc = self.next_dry_run(mine=mine)
        self.assertIn("parked #7", proc.stderr)

    def test_a_reaped_run_counts_as_an_environment_stop(self) -> None:
        # A supervisor killed mid-run writes no EXIT line; holds_slot, at next's slot count, writes stopped-environment.
        mine = ((7, CLEAN),)
        d = self.runs / "7" / key(CLEAN)
        self.launch(7, CLEAN)
        self.launch(7, CLEAN, "exit 9")
        self.assertEqual((d / "status").read_text().strip(), "running")
        reap = sourced(f"alert() {{ :; }}; holds_slot '{d}/'", {"FACTORY_RUNS_ROOT": str(self.runs)})
        self.assertEqual(reap.returncode, 1, reap.stderr)
        self.assertEqual((d / "status").read_text().strip(), "stopped-environment")
        os.utime(d / "status", (86400, 86400))
        proc = self.next_dry_run(mine=mine)
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        self.launch(7, CLEAN)
        proc = self.next_dry_run(mine=mine)
        self.assertIn("parked #7", proc.stderr)

    def test_a_launch_that_cannot_take_its_owner_lock_still_counts(self) -> None:
        # The early exits before the status write (no start time, owner.lock held, owner unwritable) stop on the
        # environment too; each must count, or a launch that never gets the lock retries hourly for good.
        for _ in range(3):
            self.launch(7, CLEAN, ":", stubs="owner_lock() { return 1; }; ")
            self.assertEqual((self.runs / "7" / key(CLEAN) / "status").read_text().strip(), "stopped-environment")
        proc = self.next_dry_run(mine=((7, CLEAN),))
        self.assertIn("parked #7", proc.stderr)

    def test_a_run_frozen_before_the_count_still_counts(self) -> None:
        # A relaunch execs the run's frozen bin/factory, which may predate env-stops; the live pass counts before that exec.
        d = self.runs / "7" / key(CLEAN)
        (d / "frozen").mkdir(parents=True)
        old = d / "frozen" / "factory"   # an older supervisor: it knows nothing of env-stops and stops on the environment
        old.write_text('#!/bin/bash\necho stopped-environment > "$(dirname "$(dirname "$0")")/status"\nexit 4\n')
        old.chmod(0o755)
        for _ in range(3):
            self.launch(7, CLEAN, ":", stubs="prepare_worktree() { :; }; freeze() { :; }; ")
        proc = self.next_dry_run(mine=((7, CLEAN),))
        self.assertIn("parked #7", proc.stderr)

    def test_a_parked_stop_alerts_once(self) -> None:
        # next runs every ten minutes; the park pages once per stop, and a later stop pages once more.
        d = self.runs / "7" / key(CLEAN)
        for _ in range(3):
            self.launch(7, CLEAN)
        sent = self.runs / "alerts"
        sent.touch()
        def alerts(during: str = "") -> int:
            tick = f"alert() {{ echo \"$*\" >> '{sent}'; {during} }}; env_park_alert '{d}' 7"
            self.assertEqual(sourced(tick, {"FACTORY_RUNS_ROOT": str(self.runs)}).returncode, 0)
            return len(sent.read_text().splitlines())
        self.assertEqual(alerts(), 1)
        self.assertEqual(alerts(), 1)
        self.assertIn("--level needs-you", sent.read_text())
        self.launch(7, CLEAN)   # a relaunch by hand that stops the same way alerts once more
        self.assertEqual(alerts(), 2)
        self.launch(7, CLEAN, 'finish stopped "FACTORY_STOP"')   # relaunched and stopped otherwise: no longer parked
        self.assertEqual(alerts(), 2)

    def test_the_alert_records_the_stop_it_was_sent_for(self) -> None:
        # A launch by hand rewrites env-stops while the alert is in flight; env-parked must keep the line the alert was
        # sent for, or that launch's own park alert is lost.
        d = self.runs / "7" / key(CLEAN)
        for _ in range(3):
            self.launch(7, CLEAN)
        sent = self.runs / "alerts"
        sent.touch()
        sent_for = (d / "env-stops").read_text()
        relaunch = f"echo '-1 3 4' > '{d}/env-stops';"
        tick = f"alert() {{ echo \"$*\" >> '{sent}'; {relaunch} }}; env_park_alert '{d}' 7"
        self.assertEqual(sourced(tick, {"FACTORY_RUNS_ROOT": str(self.runs)}).returncode, 0)
        self.assertEqual((d / "env-parked").read_text(), sent_for)
        tick = f"alert() {{ echo \"$*\" >> '{sent}'; }}; env_park_alert '{d}' 7"
        sourced(tick, {"FACTORY_RUNS_ROOT": str(self.runs)})
        self.assertEqual(len(sent.read_text().splitlines()), 2)

    def test_a_tick_inside_a_launch_does_not_take_its_alert(self) -> None:
        # A cron next that runs while a launch has written its env-stops line but not yet its status must not mark that
        # launch alerted, or the alert for the stop it then makes is lost.
        d = self.runs / "7" / key(CLEAN)
        for _ in range(3):
            self.launch(7, CLEAN)
        sent = self.runs / "alerts"
        sent.touch()
        page = f"alert() {{ case \"$*\" in *needs-you*) echo \"$*\" >> '{sent}' ;; esac; }}; "
        self.assertEqual(sourced(page + f"env_park_alert '{d}' 7", {"FACTORY_RUNS_ROOT": str(self.runs)}).returncode, 0)
        tick_inside = ('set_status() { [ "$1" = running ] && env_park_alert "$RUN" 7; '
                       'printf "%s\\n" "$1" > "$RUN/status"; log "status: $1"; }; ')
        self.launch(7, CLEAN, stubs=page + tick_inside)
        self.assertEqual(len(sent.read_text().splitlines()), 1)   # nothing went out inside the launch
        self.assertEqual(sourced(page + f"env_park_alert '{d}' 7", {"FACTORY_RUNS_ROOT": str(self.runs)}).returncode, 0)
        self.assertEqual(len(sent.read_text().splitlines()), 2)   # the stop it made pages once

    def spend_today(self, usd: float) -> None:
        (self.runs / "ledger-daily.jsonl").write_text(
            json.dumps({"date": time.strftime("%Y-%m-%d", time.gmtime()), "ticket": "7", "role": "worker", "cost_usd": usd}) + "\n")

    def test_a_daily_stop_today_launches_no_other_ticket(self) -> None:
        # The daily ledger is the runner's, across targets: after a daily stop with that ledger spent, a fresh ticket
        # would only assign, build and stop at its first cap check, so nothing launches until the UTC date moves on (#386).
        self.run_dir(7, CLEAN, "stopped-daily")
        self.spend_today(140)
        caps = {"FACTORY_DAILY_BUDGET_USD": "150", "FACTORY_ROUND_BUDGET_USD": "15"}   # not the shell's
        proc = self.next_dry_run((8, CLEAN), mine=((7, CLEAN),), **caps)
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("waiting: a run stopped at today's daily budget; nothing launches before 00:00 UTC", proc.stderr)
        os.utime(self.runs / "7" / key(CLEAN) / "status", (86400, 86400))
        proc = self.next_dry_run((8, CLEAN), mine=((7, CLEAN),), **caps)
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        other = self.runs / "acme_widget" / "9" / key(CLEAN)
        other.mkdir(parents=True)
        (other / "status").write_text("stopped-daily\n")
        proc = self.next_dry_run((8, CLEAN), **caps)
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)

    def test_a_daily_stop_under_a_lower_ticket_cap_does_not_block_the_runner(self) -> None:
        # #7's Worker section set a lower DAILY_BUDGET_USD; the shared ledger still has room at the runner's caps
        # (here FACTORY_DAILY_BUDGET_USD=100 with the default 15 usd round), so the fresh #8 launches.
        self.run_dir(7, CLEAN, "stopped-daily")
        self.spend_today(80)
        proc = self.next_dry_run((8, CLEAN), FACTORY_DAILY_BUDGET_USD="100", FACTORY_ROUND_BUDGET_USD="15")
        self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
        self.spend_today(90)
        proc = self.next_dry_run((8, CLEAN), FACTORY_DAILY_BUDGET_USD="100", FACTORY_ROUND_BUDGET_USD="15")
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("waiting: a run stopped at today's daily budget", proc.stderr)

    def test_issue_assigned_to_someone_else_is_not_listed(self) -> None:
        # Neither query returns it, so its past daily stop launches nothing.
        self.run_dir(7, CLEAN, "stopped-daily")
        os.utime(self.runs / "7" / key(CLEAN) / "status", (86400, 86400))
        proc = self.next_dry_run()
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)

    def test_trailing_newlines_strip_as_load_ticket_does(self) -> None:
        # gh returns the body raw; load_ticket's $(...) strips its trailing newlines before cmd_run keys it.
        self.run_dir(7, CLEAN, "abandon")
        proc = self.next_dry_run((7, CLEAN + "\n\n"))
        self.assertIn("parked #7: last run exited abandon", proc.stderr)


class ResumeTests(unittest.TestCase):
    """A relaunch of a run stopped between its graders grades the same round instead of starting a new one (#386)."""

    def resume(self, graded: bool, checks_now: str = "PASS a", moved: bool = False, last: int = 6,
               earlier_graded: tuple[int, ...] = (), earlier_passed: tuple[int, ...] = (),
               graders_pass: bool = True) -> tuple[str, str]:
        """(status, stdout) of cmd_run on a run whose last round of `last` passed its checks, its graders stubbed to
        pass or fail. checks_now is what the frozen checks print when run again; moved adds a clean commit after
        the last round; earlier_graded are rounds whose graders all ran and failed (no judge pass on disk);
        earlier_passed are rounds whose graders all ran and passed, then lost their push or PR create."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        runs, wt = pathlib.Path(tmp.name) / "runs", pathlib.Path(tmp.name) / "wt"
        wt.mkdir()
        commit = ["git", "-C", str(wt), "-c", "user.email=a@b", "-c", "user.name=a", "commit", "-q", "--allow-empty", "-m"]
        subprocess.run(["git", "-C", str(wt), "init", "-q"], check=True)
        subprocess.run([*commit, "base"], check=True)
        run = runs / "7" / key(CLEAN)
        (run / "frozen").mkdir(parents=True)
        (run / "frozen" / "issue.md").write_text(CLEAN)
        (run / "frozen" / "checks.sh").write_text(f"#!/bin/sh\nprintf '{checks_now}\\nCHECKS-END\\n'\n")
        (run / "frozen" / "checks.sh").chmod(0o755)
        for name in ("protected.txt", "exempt.txt"):
            (run / "frozen" / name).write_text("")
        (run / "base.sha").write_text(subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], check=True,
                                                     capture_output=True, text=True).stdout)
        if moved:
            subprocess.run([*commit, "a hand fix while the run was stopped"], check=True)
        for n in range(last + 1):
            (run / f"round-{n}.checks").write_text("PASS a\nCHECKS-END\n")
        for n in (*earlier_graded, *earlier_passed, *((last,) if graded else ())):
            (run / f"round-{n}.graded.sha").write_text("0" * 40 + "\n")
        for n in earlier_passed:
            (run / f"round-{n}.judge.json").write_text('{"verdict": "pass", "rows": {}, "fixes": []}\n')
            (run / f"round-{n}.fixes").write_text("")
        stubs = (f"MAX_ROUNDS={last}; GRADER_FAIL_ROUNDS=2; "
                 "assert_target_ready() { :; }; claude_version_ok() { :; }; "
                 'load_ticket() { ISSUE=7; KEY=7; REPO=o/r; BODY="$BODY_ARG"; }; '
                 "nav_arm_resolve() { :; }; assert_parallel() { :; }; prepare_worktree() { :; }; freeze() { :; }; "
                 "exec_frozen() { :; }; heartbeat_start() { :; }; heartbeat_stop() { :; }; check_frozen() { :; }; "
                 "measure_rows() { :; }; notify() { :; }; worker_round() { echo WORKER $1; }; "
                 'graders() { echo "GRADED $1 $(cat "$RUN/status")"; ' + ("}; " if graders_pass else "false; }; ") +
                 'open_pr() { echo "OPEN_PR ${1:-}"; finish pr-opened "PR at round $ROUND"; }; '
                 "cmd_run 7")
        env = {"FACTORY_RUNS_ROOT": str(runs), "FACTORY_WORKTREE": str(wt), "BODY_ARG": CLEAN}
        proc = sourced(stubs, env)
        return (run / "status").read_text().strip(), proc.stdout

    def test_green_round_with_unfinished_graders_is_graded_not_capped(self) -> None:
        status, out = self.resume(graded=False)
        self.assertEqual(status, "pr-opened", out)
        self.assertIn("GRADED 6 running", out)
        self.assertNotIn("WORKER", out)

    def test_moved_head_whose_checks_now_fail_is_not_graded(self) -> None:
        # round-6.checks proved the old HEAD only; a clean commit made while the run was stopped is checked again.
        status, out = self.resume(graded=False, checks_now="FAIL a: broken", moved=True)
        self.assertEqual(status, "stopped-cap", out)
        self.assertNotIn("GRADED", out)

    def test_earlier_grader_fail_rounds_count_after_a_relaunch(self) -> None:
        # Round 1 failed its graders; round 2's graders were cut off, and on the relaunch they fail again: that is
        # the second grader-fail round, so the PR opens as a draft instead of round 3 hitting the round cap.
        status, out = self.resume(graded=False, last=2, earlier_graded=(1,), graders_pass=False)
        self.assertEqual(status, "pr-opened", out)
        self.assertIn("GRADED 2 running", out)
        self.assertIn("OPEN_PR draft", out)
        self.assertNotIn("WORKER", out)

    def test_earlier_round_whose_graders_passed_is_not_a_grader_fail(self) -> None:
        # Round 1 passed every grader and lost its PR create; round 2's graders were cut off and fail on the relaunch.
        # That is the first grader-fail round, so no draft opens and the run resumes into the loop.
        status, out = self.resume(graded=False, last=2, earlier_passed=(1,), graders_pass=False)
        self.assertIn("GRADED 2 running", out)
        self.assertNotIn("OPEN_PR", out)
        self.assertEqual(status, "stopped-cap", out)

    def test_round_whose_graders_finished_resumes_into_the_loop(self) -> None:
        status, out = self.resume(graded=True)
        self.assertEqual(status, "stopped-cap", out)
        self.assertNotIn("GRADED", out)


class LintTests(ParkingTests):
    """A candidate whose body fails lint is skipped with one stderr line and never launched (#314)."""

    def test_clean_ticket_launches(self) -> None:
        proc = self.next_dry_run((7, CLEAN))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        self.assertEqual(proc.stderr, "")

    def test_lowest_issue_failing_lint_is_skipped_for_the_next_clean_one(self) -> None:
        proc = self.next_dry_run((5, NOT_A_TICKET), (6, CLEAN))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "would launch #6", proc.stderr)
        self.assertIn("lint failed #5:", proc.stderr)
        self.assertIn("remove ready-for-agent", proc.stderr)
        self.assertNotIn("#6", proc.stderr)

    def test_every_candidate_failing_lint_launches_nothing(self) -> None:
        proc = self.next_dry_run((5, NOT_A_TICKET), (6, NOT_A_TICKET + " Twice."))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("lint failed #5:", proc.stderr)
        self.assertIn("lint failed #6:", proc.stderr)

    def test_syntax_error_reports_the_lint_line_not_bash_s_temp_file(self) -> None:
        # bash -n names the deleted temp file on its own first stderr line; the timer keeps the LINT line.
        broken = CLEAN.replace('true && pass ok || fail ok "no"', "if then ( pass ok")
        self.assertNotEqual(broken, CLEAN)
        proc = self.next_dry_run((7, broken))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("lint failed #7: the done-checks block plus lib.sh does not pass bash -n", proc.stderr)
        self.assertNotIn("factory-lint", proc.stderr)

    # A candidate another account wrote or last edited is passed over with one stderr line, as is one whose
    # editor gh could not read; the owner's own edit launches (#389).

    def test_issue_another_account_wrote_is_passed_over(self) -> None:
        proc = self.next_dry_run((7, CLEAN), (8, CLEAN), authors={7: "someone-else"})
        self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
        self.assertIn("not owner #7: written or last edited by someone-else; edit the body as SamyakJhaveri", proc.stderr)

    def test_issue_another_account_last_edited_is_passed_over(self) -> None:
        proc = self.next_dry_run((7, CLEAN), (8, CLEAN), editors={7: "someone-else", 8: "SamyakJhaveri"})
        self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
        self.assertIn("not owner #7: written or last edited by someone-else", proc.stderr)
        self.assertNotIn("#8", proc.stderr)

    def test_failed_editor_call_never_launches(self) -> None:
        proc = self.next_dry_run((7, CLEAN), editors={7: None})
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("not owner #7: could not read the last editor with gh", proc.stderr)

    # next --frontier lists every issue next would launch, by next's own rules, whatever FACTORY_STOP and the slots say,
    # and writes nothing (#477).

    def test_frontier_lists_every_launchable_issue_in_launch_order(self) -> None:
        bodies = {n: CLEAN + f"\nissue {n}" for n in (5, 6, 8, 9, 10, 11, 12)}
        self.run_dir(6, bodies[6], "stopped")       # the runner's own, relaunchable: listed in number order
        self.run_dir(8, bodies[8], "abandon")       # parked on its current body
        held = self.runs / "99" / "abcdef12"        # launched with no status yet: holds the one slot
        held.mkdir(parents=True)
        (held / "launched").write_text("1\n")
        (self.runs / "FACTORY_STOP").touch()
        frontier = ((5, bodies[5]), (7, NOT_A_TICKET), (8, bodies[8]), (9, bodies[9]), (10, bodies[10]),
                    (11, bodies[11]), (12, bodies[12]))
        proc = self.next_dry_run(*frontier, mine=((6, bodies[6]),), authors={9: "someone-else"},
                                 editors={11: "someone-else"}, flag="--frontier")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "#5\n#6\n#10\n#12\n", proc.stderr)
        self.assertIn("lint failed #7", proc.stderr)
        self.assertIn("parked #8", proc.stderr)
        self.assertIn("not owner #9: written or last edited by someone-else", proc.stderr)
        self.assertIn("not owner #11: written or last edited by someone-else", proc.stderr)
        self.assertIn(" number=12 ", self.gql_log.read_text() + " ")   # the editor call runs past the first pick

    def test_frontier_over_an_empty_frontier_prints_nothing(self) -> None:
        proc = self.next_dry_run(flag="--frontier")
        self.assertEqual((proc.returncode, proc.stdout), (0, ""), proc.stderr)

    def test_frontier_writes_nothing(self) -> None:
        # The three states a real tick writes on: a running run whose owner is gone (holds_slot reaps it and alerts),
        # an env-parked run (env_park_alert writes env-parked and alerts), and a pr-opened run whose PR may have closed
        # (pr_closed_events asks gh for its state). The gone-owner run is an older body of candidate #13, so both the
        # slot loop and issue_busy must ask with peek.
        body = CLEAN + "\nissue 12"
        d12 = self.runs / "12" / key(body)
        self.run_dir(12, body, "stopped-environment")
        (d12 / "env-stops").write_text("-1 2 1\n")
        body13 = CLEAN + "\nissue 13"
        r40, r13 = self.runs / "40" / "abcdef12", self.runs / "13" / "abcdef12"
        r40.mkdir(parents=True)
        (r40 / "status").write_text("pr-opened\n")
        (r40 / "factory.log").write_text("2026-11-01T00:00:00Z EXIT pr-opened (0): https://github.com/o/r/pull/40\n")
        r13.mkdir(parents=True)
        (r13 / "status").write_text("running\n")
        (r13 / "launched").write_text("1\n")
        dead = subprocess.Popen(["true"])
        dead.wait()
        (r13 / "owner").write_text(f"{dead.pid} Thu Jan  1 00:00:00 1970\n")
        def snap() -> list[tuple[str, bytes]]:
            return sorted((str(f.relative_to(self.runs)), f.read_bytes() if f.is_file() else b"") for f in self.runs.rglob("*"))
        before = snap()
        alerts = self.runs.parent / f"{self.runs.name}.alerts"
        self.addCleanup(lambda: alerts.unlink(missing_ok=True))
        proc = self.next_dry_run((12, body), (13, body13), pre=f"alert() {{ echo \"$*\" >> '{alerts}'; }}; ", flag="--frontier")
        self.assertEqual((proc.returncode, proc.stdout), (0, "#13\n"), proc.stderr)
        self.assertIn("parked #12", proc.stderr)
        self.assertEqual(snap(), before)
        self.assertFalse(alerts.exists())
        self.assertNotIn("issues/40", self.gh_log.read_text())

    def test_install_refuses_a_read_only_flag(self) -> None:
        cron = self.runs.parent / f"{self.runs.name}.crontab"
        self.addCleanup(lambda: cron.unlink(missing_ok=True))
        for flags in ("--frontier --install", "--install --dry-run"):
            proc = self.next_dry_run(pre=f"crontab() {{ echo \"$*\" >> '{cron}'; }}; ", flag=flags)
            self.assertEqual(proc.returncode, 2, flags)
            self.assertIn("usage: bin/factory [-C <repo>] next", proc.stderr + proc.stdout)
            self.assertFalse(cron.exists(), flags)

    def test_issue_an_unnamed_account_last_edited_is_passed_over(self) -> None:
        proc = self.next_dry_run((7, CLEAN), (8, CLEAN), editors={7: UNNAMED})
        self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
        self.assertIn("not owner #7: last edited by an account GitHub no longer names; edit the body as SamyakJhaveri", proc.stderr)
        self.assertNotIn("#8", proc.stderr)

    def test_no_editor_call_after_the_pick(self) -> None:
        # A stalled GraphQL costs a tick one timeout, not one per candidate; later candidates still get the author check.
        proc = self.next_dry_run((7, CLEAN), (8, CLEAN), (9, CLEAN), authors={9: "someone-else"}, editors={8: None})
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        self.assertEqual(proc.stderr.strip(), "not owner #9: written or last edited by someone-else; "
                         "edit the body as SamyakJhaveri or remove ready-for-agent")
        calls = self.gql_log.read_text().splitlines()
        self.assertEqual(len(calls), 1, calls)
        self.assertIn(" number=7 ", calls[0] + " ")

    def test_runner_assigned_issue_another_account_edited_does_not_relaunch(self) -> None:
        self.run_dir(7, CLEAN, "stopped-daily")
        os.utime(self.runs / "7" / key(CLEAN) / "status", (86400, 86400))
        proc = self.next_dry_run(mine=((7, CLEAN),), editors={7: "someone-else"})
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("not owner #7", proc.stderr)


class LoadTicketOwnerTests(unittest.TestCase):
    """run reads the body with its author and editor in one call, so an edit by another account after next's
    owner check never reaches the run (#389)."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.runs = pathlib.Path(tmp.name)

    def load(self, author: str, editor: str | None) -> subprocess.CompletedProcess[str]:
        issue = {"body": CLEAN, "author": {"login": author}, "editor": editor and {"login": editor}}
        if editor == UNNAMED:
            issue.update(editor=None, lastEditedAt="2026-10-30T00:00:00Z")
        doc = json.dumps({"data": {"repository": {"issue": issue}}})
        return sourced(f"target_repo() {{ echo o/r; }}; gh() {{ printf '%s\\n' '{doc}'; }}; "
                       'load_ticket 7; printf "BODY=%s" "$BODY"',
                       {"FACTORY_RUNS_ROOT": str(self.runs), "FACTORY_FROZEN": ""})

    def test_body_another_account_last_edited_is_refused(self) -> None:
        proc = self.load("SamyakJhaveri", "someone-else")
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("not owner #7: written or last edited by someone-else", proc.stderr)
        self.assertNotIn("BODY=", proc.stdout)

    def test_body_another_account_wrote_is_refused(self) -> None:
        proc = self.load("someone-else", "SamyakJhaveri")
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("not owner #7: written or last edited by someone-else", proc.stderr)

    def test_body_an_unnamed_account_last_edited_is_refused(self) -> None:
        proc = self.load("SamyakJhaveri", UNNAMED)
        self.assertEqual(proc.returncode, 4, proc.stderr)
        self.assertIn("not owner #7: last edited by an account GitHub no longer names; edit the body as SamyakJhaveri", proc.stderr)
        self.assertNotIn("BODY=", proc.stdout)

    def test_owner_body_loads_as_fetched(self) -> None:
        for editor in (None, "SamyakJhaveri"):
            proc = self.load("SamyakJhaveri", editor)
            self.assertEqual(proc.stdout, f"BODY={CLEAN}", proc.stderr)


if __name__ == "__main__":
    unittest.main()
