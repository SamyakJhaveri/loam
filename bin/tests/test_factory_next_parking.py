"""`bin/factory next` parks a ticket only on a run of its current body, so a body edit relaunches it,
and it lints every candidate before picking one, so a labelled issue that is not a ticket is skipped (#314).

`bin/factory` is sourced (FACTORY_SOURCED=1) with a temp runs root. park_status is called directly,
and cmd_next --dry-run (or --frontier) runs with gh, the origin, the login and version probes stubbed as shell functions,
so the frontier lines carry the bodies the way the real query does. The retry test models tmux's environment
and executes its session command against a frozen-supervisor fixture. No network, no tmux, no `claude`.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import pathlib
import shlex
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

# A runner whose calls bill an API key: since 13 Nov 2026 no runner has a daily budget, on any billing route.
BILLED = {"ANTHROPIC_API_KEY": "sk-ant-test"}


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
        SamyakJhaveri by default, and last edited by `editors`' login (None: GitHub cannot resolve the issue; UNNAMED: a
        null editor with a lastEditedAt), by no one by default. The one editor call is answered as GitHub's GraphQL does,
        one `i<N>` alias per issue; an issue it cannot resolve has a null alias and an `errors` entry, and then gh prints the
        raw body whatever --jq asks and exits 1. Each editor call is logged to GQL_LOG, every gh call to GH_LOG. `now` pins
        the epoch `date -u +%s` prints, so a backoff boundary does not move while the test runs."""
        def lines(issues: tuple[tuple[int, str], ...]) -> str:
            return " ".join(f"'{issue} {(authors or {}).get(issue, 'SamyakJhaveri')} {base64.b64encode(body.encode()).decode()}'"
                            for issue, body in issues) or "''"
        def alias(who: str | None) -> dict | None:
            if who == UNNAMED:
                return {"editor": None, "lastEditedAt": "2026-10-30T00:00:00Z"}
            return {"editor": {"login": who}, "lastEditedAt": "2026-10-30T00:00:00Z"} if who else {"editor": None, "lastEditedAt": None}
        everyone = {issue: (editors or {}).get(issue, "") for issue, _ in frontier + mine}
        doc: dict = {"data": {"repository": {f"i{issue}": None if who is None else alias(who) for issue, who in everyone.items()}}}
        gone = [issue for issue, who in everyone.items() if who is None]
        if gone:
            doc["errors"] = [{"message": f"Could not resolve to an Issue with the number of {issue}."} for issue in gone]
        reply = f"echo {shlex.quote(json.dumps(doc))}; return 1" if gone else f'jq -r "$q" <<< {shlex.quote(json.dumps(doc))}'
        clock = "" if now is None else f'date() {{ if [ "$*" = "-u +%s" ]; then echo {now}; else command date "$@"; fi; }}; '
        stubs = (pre + clock + "claude_logged_in() { :; }; claude_version_ok() { :; }; target_repo() { echo o/r; }; "
                 'gh() { echo "$*" >> "$GH_LOG"; '
                 "case $2 in graphql) local a p= q=.; "
                 'for a; do [ "$p" = --jq ] && q=$a; p=$a; done; echo "$*" >> "$GQL_LOG"; '
                 f"{reply} ;; repos/*) printf '%s\\n' {lines(frontier)} ;; "
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

    def test_retry_forwards_exports_needed_by_an_existing_frozen_supervisor(self) -> None:
        self.run_dir(7, CLEAN, "stopped")
        run = self.runs / "7" / key(CLEAN)
        frozen = run / "frozen"
        frozen.mkdir()
        (frozen / "sha256").write_text("already frozen\n")
        resumed = self.runs / "resumed"
        # A supervisor frozen before a launch requirement was retired still reads its old exports.
        supervisor = (
            '#!/usr/bin/env bash\n'
            '[ "$*" = "run 7" ] || exit 8\n'
            '[ -x "${LOAM_FACTORY_RETRY_NODE:-}/bin/node" ] || exit 4\n'
            '[ -x "${LOAM_FACTORY_RETRY_CHECK:-}" ] || exit 4\n'
            '[ "${LOAM_FACTORY_LOCAL_ONLY+x}" != x ] || exit 5\n'
            f'echo resumed > {shlex.quote(str(resumed))}\n'
        )
        (frozen / "factory").write_text(supervisor)
        (frozen / "factory").chmod(0o755)
        old_bin = self.runs / "prior tools" / "bin"
        old_bin.mkdir(parents=True)
        for name in ("node", "check"):
            (old_bin / name).write_text("#!/bin/sh\nexit 0\n")
            (old_bin / name).chmod(0o755)

        # Only replace run's setup: keep the actual launch command, freeze's reuse and exec_frozen.
        checkout = self.runs / "checkout"
        (checkout / "bin").mkdir(parents=True)
        (checkout / "bin/factory.d").symlink_to(ROOT / "bin/factory.d")
        launcher = checkout / "bin/factory"
        launcher.write_text(
            '#!/usr/bin/env bash\n'
            f'export FACTORY_ROOT={shlex.quote(str(ROOT))} FACTORY_SOURCED=1\n'
            f'. {shlex.quote(str(ROOT / "bin/factory"))}\n'
            f'RUN={shlex.quote(str(run))}; SRC=7\n'
            'freeze\nexec_frozen\n'
        )
        launcher.chmod(0o755)
        pre = f'ROOT={shlex.quote(str(checkout))}; LOAM_FACTORY_LOCAL_ONLY=private; alert() {{ :; }}; ' + '''
tmux() {
  [ "$1" = has-session ] && return 1
  [ "$1" = new-session ] || return 2
  shift
  local forwarded=()
  while [ "$#" -gt 1 ]; do
    case "$1" in
      -e) forwarded+=("$2"); shift 2 ;;
      -s) shift 2 ;;
      -d) shift ;;
      *) return 2 ;;
    esac
  done
  env -i PATH="$PATH" HOME="$HOME" "${forwarded[@]}" bash -c "$1"
}; '''
        proc = self.next_dry_run(mine=((7, CLEAN),), flag="", pre=pre,
                                 LOAM_FACTORY_RETRY_NODE=str(old_bin.parent),
                                 LOAM_FACTORY_RETRY_CHECK=str(old_bin / "check"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "launched #7", proc.stderr)
        self.assertTrue(resumed.exists(), (self.runs / "7.tmux.log").read_text())
        self.assertEqual((frozen / "factory").read_text(), supervisor)

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

    def test_a_stopped_daily_run_from_before_the_caps_went_relaunches_at_once(self) -> None:
        # A run that stopped at a daily budget before 13 Nov 2026 relaunches as stopped does, the same UTC day and on
        # an API key, and even with the shared daily ledger past any old budget.
        self.run_dir(7, CLEAN, "stopped-daily")
        (self.runs / "ledger-daily.jsonl").write_text(
            json.dumps({"date": time.strftime("%Y-%m-%d", time.gmtime()), "ticket": "7", "role": "worker", "cost_usd": 1e9}) + "\n")
        proc = self.next_dry_run((7, CLEAN), FACTORY_DAILY_BUDGET_USD="150", **BILLED)
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        self.assertNotIn("daily budget", proc.stderr)

    def test_runner_assigned_issue_relaunches_only_after_a_relaunchable_stop(self) -> None:
        # The launch assigned the issue to the runner and nothing unassigns it (#386, #440): of the runner's own,
        # a stopped-daily run of an earlier UTC day, a stopped-environment run past its backoff, and a stopped run
        # launch, and each of the rest is passed over with its line (#617). Four slots, so #6's running run, which holds
        # one, leaves room.
        for issue, status in ((5, "stopped-cap"), (6, "running"), (8, "pr-opened")):
            self.run_dir(issue, CLEAN, status)
        others = ("parked #5: last run exited stopped-cap; edit the body or remove ready-for-agent\n"
                  "waiting #6: its run is running\n"
                  "waiting #8: its PR awaits merge or close\n")
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
                self.assertEqual(proc.stderr, others)
                shutil.rmtree(self.runs / "7")
        proc = self.next_dry_run(mine=tuple((n, CLEAN) for n in (5, 6, 8)), FACTORY_MAX_PARALLEL="4")
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertEqual(proc.stderr, others)

    def test_runner_assigned_ticket_defect_relaunches_only_after_a_body_edit(self) -> None:
        # The launch assigned #7 to the runner; its run ended ticket-defect, so the same body parks, and the body the
        # owner corrects keys a new run dir with no run yet, which launches like a new ticket (#467, #468).
        self.run_dir(7, CLEAN, "ticket-defect")
        proc = self.next_dry_run(mine=((7, CLEAN),))
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        proc = self.next_dry_run(mine=((7, CLEAN + "\n- the corrected line"),))
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)

    def test_runner_assigned_issue_that_never_ran_is_held(self) -> None:
        # Assigned to the runner by hand with no run of any body: the owner holds it, so next leaves it, with its line
        # (#617); the same issue unassigned launches. A lint line under the issue dir is not a run.
        (self.runs / "7").mkdir()
        (self.runs / "7" / "owner-events.jsonl").write_text("{}\n")
        proc = self.next_dry_run(mine=((7, CLEAN),))
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertEqual(proc.stderr, "held #7: assigned to the runner with no run of any body; unassign it to let next launch it\n")
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
                if case == "running":
                    # A live run holds its lease (cmd_run); a run dir with no lease holds no slot.
                    (d / "lease").touch()
                    p = subprocess.Popen(["flock", str(d / "lease"), "sleep", "60"], start_new_session=True)
                    self.addCleanup(p.wait)
                    self.addCleanup(subprocess.run, ["kill", "-KILL", "--", f"-{p.pid}"], check=False)
                    for _ in range(100):
                        if subprocess.run(["flock", "-n", str(d / "lease"), "true"]).returncode != 0:
                            break
                        time.sleep(0.05)
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
                if case == "running":
                    subprocess.run(["kill", "-KILL", "--", f"-{p.pid}"], check=False)
                    p.wait()
                shutil.rmtree(self.runs / "7")

    def test_runner_assigned_stop_waits_while_its_stop_file_remains(self) -> None:
        # cmd_run exits stopped at once while FACTORY_STOP is in the run dir, so #7 must not take the pick from #8
        # every tick (#440), and says why on its line (#617); removing the file makes it eligible again.
        self.run_dir(7, CLEAN, "stopped")
        (self.runs / "7" / key(CLEAN) / "FACTORY_STOP").touch()
        proc = self.next_dry_run((8, CLEAN), mine=((7, CLEAN),))
        self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
        self.assertEqual(proc.stderr, "stopped #7: its run directory holds FACTORY_STOP (bin/factory stop); remove the file to let it launch\n")
        (self.runs / "7" / key(CLEAN) / "FACTORY_STOP").unlink()
        proc = self.next_dry_run((8, CLEAN), mine=((7, CLEAN),))
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)

    def test_unassigned_stop_waits_while_its_stop_file_remains(self) -> None:
        # A run stopped before prepare_worktree never assigned its issue, so the skip must hold for the unassigned too.
        self.run_dir(7, CLEAN, "stopped")
        (self.runs / "7" / key(CLEAN) / "FACTORY_STOP").touch()
        proc = self.next_dry_run((7, CLEAN), (8, CLEAN))
        self.assertEqual(proc.stdout.strip(), "would launch #8", proc.stderr)
        self.assertEqual(proc.stderr, "stopped #7: its run directory holds FACTORY_STOP (bin/factory stop); remove the file to let it launch\n")

    def test_relaunchable_run_waits_while_a_process_of_it_still_runs(self) -> None:
        # A stuck model call outlives finish stopped-environment; cmd_run refuses a relaunch while it, or any process
        # holding the run's lease, still runs, and writes no status, so #7 must not take the pick from #8 every tick.
        for holder in ("call", "lease"):
            with self.subTest(holder=holder):
                self.run_dir(7, CLEAN, "stopped-environment")
                d = self.runs / "7" / key(CLEAN)
                os.utime(d / "status", (86400, 86400))
                (d / "lease").touch()   # cmd_run creates it before any call
                if holder == "call":
                    p = subprocess.Popen(["sleep", "60"], start_new_session=True)
                    self.addCleanup(p.wait)
                    self.addCleanup(subprocess.run, ["kill", "-KILL", "--", f"-{p.pid}"], check=False)
                    (d / "call").write_text(f"{p.pid} test.{key(str(p.pid))}\n")
                else:
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
        # MAX_ROUNDS never trips; every relaunch costs a call and a page (#547). The third such stop in a row parks.
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
        # The early exits before the status write (no start time, owner.flock held, owner unwritable) stop on the
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
                 "exec_frozen() { :; }; check_frozen() { :; }; method_evidence() { :; }; "
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
        # With none picked, a failed read is a refusal (exit 1), so a real tick sends no healthchecks beat.
        proc = self.next_dry_run((7, CLEAN), editors={7: None})
        self.assertEqual((proc.returncode, proc.stdout.strip()), (1, "nothing to launch"), proc.stderr)
        self.assertIn("not owner #7: could not read the last editor with gh", proc.stderr)
        self.assertIn("refused: a candidate was passed over on a failed GitHub read", proc.stderr)
        # A later candidate still launches, and then the tick is not a refusal.
        proc = self.next_dry_run((7, CLEAN), (8, CLEAN), editors={7: None})
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "would launch #8"), proc.stderr)

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
        self.assertIn("i12: issue(number: 12) ", self.gql_log.read_text())   # the editor read names every candidate

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
        self.assertNotIn("pullRequest", self.gh_log.read_text())

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

    def test_one_editor_call_names_every_candidate(self) -> None:
        # One GraphQL read gives every candidate's last editor, the ready list's and the runner's own, however many are
        # passed over, so a tick makes one editor read, not one per candidate (#598); each still gets its own verdict.
        self.run_dir(13, CLEAN + "\nan older body", "stopped")
        proc = self.next_dry_run((7, NOT_A_TICKET), (8, CLEAN), (9, CLEAN), (10, CLEAN), (12, CLEAN), mine=((13, CLEAN),),
                                 authors={9: "someone-else"}, editors={8: "someone-else", 10: None})
        self.assertEqual((proc.returncode, proc.stdout.strip()), (0, "would launch #12"), proc.stderr)
        self.assertIn("lint failed #7", proc.stderr)
        self.assertIn("not owner #8: written or last edited by someone-else", proc.stderr)
        self.assertIn("not owner #9: written or last edited by someone-else", proc.stderr)
        self.assertIn("not owner #10: could not read the last editor with gh", proc.stderr)
        calls = self.gql_log.read_text().splitlines()
        self.assertEqual(len(calls), 1, calls)
        for issue in (7, 8, 9, 10, 12, 13):
            self.assertIn(f"i{issue}: issue(number: {issue}) ", calls[0])

    def test_runner_assigned_issue_another_account_edited_does_not_relaunch(self) -> None:
        self.run_dir(7, CLEAN, "stopped-daily")
        os.utime(self.runs / "7" / key(CLEAN) / "status", (86400, 86400))
        proc = self.next_dry_run(mine=((7, CLEAN),), editors={7: "someone-else"})
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertIn("not owner #7", proc.stderr)


# A stand-in for gh that answers next's reads as GitHub does: the two listings as REST JSON through the real --jq (the
# repository listing newest first, one 100-issue page unless --paginate), and the editor read with one alias per issue.
# Each call is logged one per line to $GH_LOG; the issues come from the JSON at $STORE, number -> {as, bl, body}.
GH_STAND_IN = """#!/usr/bin/env python3
import json, os, re, subprocess, sys
a = sys.argv[1:]
store = json.load(open(os.environ["STORE"]))
open(os.environ["GH_LOG"], "a").write(" ".join(a) + "\\n")
jq = a[a.index("--jq") + 1] if "--jq" in a else "."
path = a[1] if len(a) > 1 else ""
def rest(n, i):
    return {"number": int(n), "user": {"login": "SamyakJhaveri"}, "body": i["body"], "pull_request": None,
            "assignees": [{"login": x} for x in i["as"]], "issue_dependencies_summary": {"blocked_by": i["bl"]},
            "repository": {"full_name": "o/r"}}
if path == "graphql":
    q = next(x.split("=", 1)[1] for x in a if x.startswith("query="))
    doc = {"data": {"repository": {k: {"editor": None, "lastEditedAt": None}
                                   for k in re.findall(r"(i[0-9]+): issue\\(number", q)}}}
elif path.startswith("repos/o/r/issues?"):
    doc = sorted((rest(n, i) for n, i in store.items() if not ("assignee=none" in path and i["as"])),
                 key=lambda x: -x["number"])
    doc = doc if "--paginate" in a else doc[:100]
elif path.startswith("/issues?"):
    doc = [rest(n, i) for n, i in store.items() if "SamyakJhaveri" in i["as"]]
else:
    sys.exit(2)
r = subprocess.run(["jq", "-r", jq], input=json.dumps(doc), capture_output=True, text=True)
sys.stdout.write(r.stdout)
sys.exit(r.returncode)
"""


class PassedOverTests(unittest.TestCase):
    """Every ready issue the frontier loop passes over gets one stderr line with its reason, read from the same listings and
    the same one editor read (#617)."""

    def test_each_passed_over_issue_gets_one_line_and_an_older_clean_issue_still_launches(self) -> None:
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        tmp = pathlib.Path(t.name)
        runs, bin_dir = tmp / "runs", tmp / "bin"
        bin_dir.mkdir()
        (bin_dir / "gh").write_text(GH_STAND_IN)
        (bin_dir / "gh").chmod(0o755)
        me, other = ["SamyakJhaveri"], ["mallory"]
        store = {19: (["SamyakJhaveri"], None, CLEAN), 20: ([], None, CLEAN), 21: ([], 2, "x"), 22: (other, 0, "x"), 23: (me, 0, "x"), 24: (me, 0, "x"), 25: (me, 0, "x"),
                 26: ([], 0, "x"), 27: (me, 1, "x"), 28: (me, 0, "x"), 29: ([], 0, CLEAN), 30: (me, 0, "x"),
                 31: ([], 3, ""), 32: (other, 0, ""), 33: (["mallory", "eve"], 0, CLEAN)}
        # 100 newer issues assigned to another account fill the repository listing's first page.
        store.update({n: (other, 0, "x") for n in range(101, 201)})
        (tmp / "store.json").write_text(json.dumps({n: {"as": a, "bl": b, "body": body} for n, (a, b, body) in store.items()}))
        def run(issue: int, status: str | None, *files: tuple[str, str]) -> None:
            d = runs / str(issue) / key(store[issue][2])
            d.mkdir(parents=True)
            if status:
                (d / "status").write_text(status + "\n")
            for name, text in files:
                (d / name).write_text(text)
        def pr(n: int) -> tuple[str, str]:
            return "factory.log", f"2026-11-01T00:00:00Z EXIT pr-opened (0): https://github.com/o/r/pull/{n} after 1 rounds\n"
        run(19, "stopped")   # relaunchable, were its blocker count readable
        run(23, "pr-opened", pr(123))
        run(25, "stuck")
        run(26, None, ("FACTORY_STOP", ""))
        run(28, "pr-opened", pr(128), ("pr-closed", "2026-11-01T01:00:00Z\n"))
        run(30, "running")
        run(33, "stopped-daily")   # of an earlier day, so it would relaunch were it not another account's
        os.utime(runs / "33" / key(CLEAN) / "status", (86400, 86400))
        gh_log = tmp / "gh.log"
        proc = sourced("assert_target_ready() { :; }; claude_logged_in() { :; }; claude_version_ok() { :; }; "
                       "target_repo() { echo o/r; }; cmd_next --dry-run",
                       {"PATH": f"{bin_dir}:{os.environ['PATH']}", "STORE": str(tmp / "store.json"), "GH_LOG": str(gh_log),
                        "FACTORY_RUNS_ROOT": str(runs), "FACTORY_MAX_PARALLEL": "2"})
        self.assertEqual((proc.returncode, proc.stdout), (0, "would launch #29\n"), proc.stderr)
        expect = {
            19: "blocked #19: the listing gave no native blocker count (?); it waits until it does",
            20: "blocked #20: the listing gave no native blocker count (?); it waits until it does",
            21: "blocked #21: 2 open native blocker(s); it launches once they close",
            22: "assigned #22: assigned to mallory, not the runner; unassign it or remove ready-for-agent",
            23: "waiting #23: its PR awaits merge or close",
            24: "held #24: assigned to the runner with no run of any body; unassign it to let next launch it",
            25: "parked #25: last run exited stuck; edit the body or remove ready-for-agent",
            26: "stopped #26: its run directory holds FACTORY_STOP (bin/factory stop); remove the file to let it launch",
            27: "blocked #27: 1 open native blocker(s); it launches once they close",
            28: "parked #28: its PR closed but the issue is still open; edit the body or remove ready-for-agent",
            30: "waiting #30: its run is running",
            31: "blocked #31: 3 open native blocker(s); it launches once they close",
            32: "assigned #32: assigned to mallory, not the runner; unassign it or remove ready-for-agent",
            33: "assigned #33: assigned to mallory,eve, not the runner; unassign it or remove ready-for-agent",
        }
        lines = proc.stderr.splitlines()
        for issue, line in expect.items():
            with self.subTest(issue=issue):
                self.assertEqual([x for x in lines if f"#{issue}: " in x], [line], proc.stderr)
        self.assertEqual(len(lines), len(expect) + 100, proc.stderr)
        # The same reads as before: two listings and one editor read naming every candidate (no PR read under --dry-run).
        calls = gh_log.read_text().splitlines()
        self.assertEqual([c.split(" ", 2)[:2] for c in calls], [["api", "repos/o/r/issues?labels=ready-for-agent&state=open&per_page=100"],
                                                                ["api", "/issues?filter=assigned&labels=ready-for-agent&state=open&per_page=100"],
                                                                ["api", "graphql"]], calls)
        self.assertIn("--paginate", calls[0].split())
        for issue in store:
            self.assertIn(f"i{issue}: issue(number: {issue}) ", calls[2])


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
