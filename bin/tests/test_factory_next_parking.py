"""`bin/factory next` parks a ticket only on a run of its current body, so a body edit relaunches it,
and it lints every candidate before picking one, so a labelled issue that is not a ticket is skipped (#314).

`bin/factory` is sourced (FACTORY_SOURCED=1) with a temp runs root. park_status is called directly,
and cmd_next --dry-run runs with gh, the origin, the login and version probes, and the toolchain gate stubbed as shell functions,
so the frontier lines carry the bodies the way the real query does. No network, no tmux, no `claude`.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import pathlib
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

# The smallest body `bin/factory lint` accepts, as the issue body gh returns it (no trailing newline).
CLEAN = (ROOT / "bin/tests/fixtures/clean-ticket.md").read_text().rstrip("\n")

# Carries the label but is not a ticket: no done-checks block, no sections. #314's case.
NOT_A_TICKET = "A note that someone labelled ready-for-agent.\n\nNo done-checks block here."


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

    def run_dir(self, issue: int, body: str, status: str) -> None:
        d = self.runs / str(issue) / key(body)
        d.mkdir(parents=True)
        (d / "status").write_text(status + "\n")
        (d / "launched").write_text("1\n")

    def park_status(self, issue: int, body: str) -> str:
        proc = sourced(f'park_status {issue} "$BODY_ARG"', {"FACTORY_RUNS_ROOT": str(self.runs), "BODY_ARG": body})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout.strip()

    def next_dry_run(self, *frontier: tuple[int, str],
                     mine: tuple[tuple[int, str], ...] = (), **env: str) -> subprocess.CompletedProcess[str]:
        """cmd_next --dry-run over the given unassigned (issue, body) frontier, lowest number first as gh sorts it,
        and `mine`, the ready-for-agent issues assigned to the runner."""
        def lines(issues: tuple[tuple[int, str], ...]) -> str:
            return " ".join(f"'{issue} {base64.b64encode(body.encode()).decode()}'" for issue, body in issues) or "''"
        stubs = ("assert_toolchain_env() { :; }; claude_logged_in() { :; }; claude_version_ok() { :; }; target_repo() { echo o/r; }; "
                 f"gh() {{ case $2 in repos/*) printf '%s\\n' {lines(frontier)} ;; issues\\?*) printf '%s\\n' {lines(mine)} ;; esac; }}; "
                 "cmd_next --dry-run")
        return sourced(stubs, {"FACTORY_RUNS_ROOT": str(self.runs), **env})

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

    def test_same_body_stopped_environment_relaunches(self) -> None:
        body = CLEAN
        self.run_dir(7, body, "stopped-environment")
        self.assertEqual(self.park_status(7, body), "stopped-environment")
        proc = self.next_dry_run((7, body))
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)

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

    def test_runner_assigned_issue_relaunches_only_after_a_past_daily_stop(self) -> None:
        # The launch assigned the issue to the runner and nothing unassigns it (#386): of the runner's own,
        # only a stopped-daily run of an earlier UTC day launches, and the rest are skipped without a line.
        # Four slots, so #6's running run, which holds one, leaves room to launch.
        for issue, status in ((5, "stopped-cap"), (6, "running"), (7, "stopped-daily"), (8, "pr-opened")):
            self.run_dir(issue, CLEAN, status)
        os.utime(self.runs / "7" / key(CLEAN) / "status", (86400, 86400))
        mine = tuple((n, CLEAN) for n in (5, 6, 7, 8))
        proc = self.next_dry_run(mine=mine, FACTORY_MAX_PARALLEL="4")
        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
        self.assertEqual(proc.stderr, "")
        proc = self.next_dry_run(mine=tuple(m for m in mine if m[0] != 7), FACTORY_MAX_PARALLEL="4")
        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
        self.assertEqual(proc.stderr, "")

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


if __name__ == "__main__":
    unittest.main()
