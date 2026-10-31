"""`bin/factory status --criteria` measures the ARCHITECTURE.md trust criteria from one target's run directories.

A synthetic runs root holds a PR in one round, a PR after a parallel-cap exit and an environment-lost round, a PR
whose first launch died mid-round and whose relaunch hit the parallel cap, a file-ticket rehearsal that opens no PR,
and an abandoned run with more rounds than any PR. Another target's run sits under <owner>__<repo>/ and counts only
with -C. A second root holds one run with the records the other criteria read: owner-events.jsonl, a stall, a
pass-over marker, judge evidence_kind, and Claude and Codex worker messages. No network, no model.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CRITERIA = ROOT / "bin/factory.d/criteria.py"
INHERITED = ("FACTORY_ROOT", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER")


def run_dir(root: pathlib.Path, label: str, status: str, log: list[str], rounds: int) -> None:
    d = root / label
    d.mkdir(parents=True)
    (d / "status").write_text(status + "\n")
    (d / "factory.log").write_text("".join(f"2026-10-19T00:00:00Z {line}\n" for line in log))
    for n in range(rounds + 1):
        (d / f"round-{n}.checks").write_text("PASS a\n")


def loam_runs(runs: pathlib.Path) -> None:
    run_dir(runs, "1/aaaa0001", "pr-opened",
            ["===== round 1 =====", "EXIT pr-opened (0): https://github.com/o/loam/pull/2 after 1 rounds"], 1)
    # The first EXIT comes before any round (a parallel-cap exit), the second loses round 1 to the environment.
    run_dir(runs, "2/aaaa0002", "pr-opened",
            ["EXIT stopped-environment (4): parallel cap: 1 other live run(s), MAX_PARALLEL=1",
             "===== round 1 =====",
             "EXIT stopped-environment (4): the worker call failed before doing work: unknown error",
             "===== round 1 =====", "===== round 2 =====", "===== round 3 =====",
             "EXIT pr-opened (0): https://github.com/o/loam/pull/3 after 3 rounds"], 3)
    # The first launch dies in round 2 with no EXIT line; the relaunch's parallel-cap exit loses no round.
    run_dir(runs, "3/aaaa0003", "pr-opened",
            ["===== launch =====", "===== round 1 =====", "===== round 2 =====",
             "===== launch =====", "EXIT stopped-environment (4): parallel cap: 1 other live run(s), MAX_PARALLEL=1",
             "===== launch =====", "resuming after round 1", "===== round 2 =====",
             "EXIT pr-opened (0): https://github.com/o/loam/pull/4 after 2 rounds"], 2)
    # A file ticket reaches pr-opened with no GitHub call, so its six rounds stay out of the median.
    run_dir(runs, "f7-rehearsal/cccc0005", "pr-opened",
            ["===== launch ====="] + [f"===== round {n} =====" for n in range(1, 7)]
            + ["EXIT pr-opened (0): file ticket: no GitHub call; the PR body is at /runs/f7-rehearsal/pr-body.md"], 6)
    # Not a PR run, so its five rounds stay out of the median.
    run_dir(runs, "4/aaaa0004", "abandon",
            [f"===== round {n} =====" for n in range(1, 6)] + ["EXIT abandon (5): ABANDON needs a do-not-touch path"], 5)
    run_dir(runs, "o__r/7/bbbb0007", "pr-opened",
            [f"===== round {n} =====" for n in range(1, 5)] + ["EXIT pr-opened (0): https://github.com/o/r/pull/8"], 4)


def verdicts(stdout: str) -> dict[str, str]:
    """Criterion name -> its verdict line."""
    lines = stdout.splitlines()
    return {line[2:].partition(": ")[0]: lines[i + 1] for i, line in enumerate(lines) if line.startswith("- ")}


def factory(*args: str, runs: pathlib.Path) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k not in INHERITED}
    return subprocess.run([str(ROOT / "bin/factory"), *args], cwd=ROOT, env={**env, "FACTORY_RUNS_ROOT": str(runs)},
                          capture_output=True, text=True, check=False)


def grader_first_fail(run: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-c", '. bin/factory; grader_first_fail "$1"', "_", str(run)],
        cwd=ROOT,
        env={**os.environ, "FACTORY_SOURCED": "1"},
        capture_output=True,
        text=True,
        check=False,
    )


class StatusCriteriaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.runs = pathlib.Path(self.tmp.name) / "runs"
        loam_runs(self.runs)

    def test_runs_without_the_new_records_leave_only_those_criteria_unmeasured(self) -> None:
        proc = factory("status", "--criteria", runs=self.runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        verdict = verdicts(proc.stdout)
        self.assertEqual(verdict["rounds lost to environment failures"], "    FAIL: measured 1 (2/aaaa0002 round 1); latest 2026-10-19")
        self.assertEqual(verdict["median rounds to PR"], "    PASS: measured 2 (over 3 PR runs)")
        self.assertEqual(verdict["stalls whose first failing grader row is scope"], "    PASS: measured 0 (of 0 stalls)")
        # The text matcher's count is an estimate (#443), so it never prints PASS or FAIL.
        self.assertEqual(verdict["rounds whose last worker message claims done while the checks printed FAIL"],
                         "    INCONCLUSIVE: estimate: 0 of 0 failing rounds (claude 0, codex 0; text matcher, see #443)")
        # A run from before owner-events.jsonl, evidence_kind and guard's marker copy shows no operator action, no cited
        # notes and no marker, which is not zero of them.
        for name in ("operator actions from voice note to a running loop on Track B",
                     "operator actions after the PR opens", "judge fails citing a worker-written measurement",
                     "lines per round marking a passed-over step"):
            self.assertTrue(verdict[name].startswith("    UNMEASURED: "), (name, verdict[name]))
        self.assertEqual(len(verdict), 8, verdict)
        # One header line, the eight criteria and the escaped defects line: no run table, stop counts, or grader
        # versions.
        lines = proc.stdout.splitlines()
        self.assertIn(f": 5 runs under {self.runs} ", lines[0])
        self.assertTrue(lines[-1].startswith("escaped defects: "), lines[-1])
        self.assertEqual(len(lines), 1 + 2 * 8 + 1, proc.stdout)

    def test_the_run_records_measure_the_other_criteria(self) -> None:
        runs = pathlib.Path(self.tmp.name) / "records"
        # A relaunch after the stall opened the PR, so the median has its run too.
        run_dir(runs, "7/abcd1234", "pr-opened",
                ["===== launch =====", "===== round 1 =====", "===== round 2 =====", "===== round 3 =====",
                 "EXIT stuck (1): same failing set"], 3)
        d = runs / "7/abcd1234"
        long_fail = "FAIL a: " + "b" * 70 + " the reason"
        (d / "round-1.checks").write_text(f"SKIPPED: gpu\nSKIPPED: node\n{long_fail}\n")
        (d / "round-2.checks").write_text("FAIL a: b\n")
        (d / "round-3.checks").write_text("FAIL do-not-touch seed/x\nFAIL a: b\n")
        (d / "owner-events.jsonl").write_text("".join(
            f'{{"phase":"{p}","kind":"{k}"}}\n' for p, k in
            [("launch", "opened"), ("launch", "labeled"), ("launch", "run"), ("pr", "merged")]) + "not json\n")
        (d / "round-3.judge.json").write_text(
            '{"verdict":"fix","rows":{"correct":"fail","verified":"fail","honest":"pass"},'
            '"evidence_kind":{"correct":"notes","verified":"diff","honest":"notes"}}\n')
        # Round 1 (Claude, an array reply) claims done; round 2 (Codex) says it is not done; round 3 (Codex) finished.
        (d / "round-1.result.json").write_text('[{"type":"system"},{"type":"result","result":"Done: all checks pass."}]')
        (d / "round-2.result.json").write_text('{"result":"ignored for a Codex round"}')
        (d / "round-2.last.txt").write_text("The done-checks still fail; this is not done yet.\n")
        # A claim past the first 100 characters of its sentence.
        long_claim = "Details " + "x" * 100 + " complete."
        (d / "round-3.last.txt").write_text(long_claim + "\n")
        proc = factory("status", "--criteria", runs=runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("UNMEASURED", proc.stdout)
        verdict = verdicts(proc.stdout)
        # A lower bound within an at-most threshold cannot show the threshold is met.
        self.assertTrue(verdict["operator actions from voice note to a running loop on Track B"]
                        .startswith("    INCONCLUSIVE: measured at least 3 (most in one run, 7/abcd1234, of 1 run; omits "))
        self.assertTrue(verdict["operator actions after the PR opens"].startswith("    INCONCLUSIVE: measured at least 1 ("))
        self.assertEqual(verdict["stalls whose first failing grader row is scope"],
                         "    FAIL: measured 1 (of 1 stall: 7/abcd1234 round 3); latest 2026-10-19")
        self.assertEqual(verdict["lines per round marking a passed-over step"],
                         "    FAIL: measured 2 (7/abcd1234 round 1); latest 2026-10-19")
        self.assertEqual(verdict["judge fails citing a worker-written measurement"],
                         "    FAIL: measured 1 of 2 (7/abcd1234 round 3 correct); latest 2026-10-19")
        self.assertEqual(verdict["rounds whose last worker message claims done while the checks printed FAIL"],
                         "    INCONCLUSIVE: estimate: 2 of 3 failing rounds (claude 1, codex 1; text matcher, see #443)")
        # Each counted round, its first FAIL line and the sentence read as a claim, so a reader can settle the estimate.
        lines = proc.stdout.splitlines()
        self.assertEqual(lines[lines.index(verdict["rounds whose last worker message claims done while the checks printed FAIL"])
                               + 1:-1], [f"      7/abcd1234 round 1 (claude): {long_fail} | Done: all checks pass.",
                                       f"      7/abcd1234 round 3 (codex): FAIL do-not-touch seed/x | {long_claim}"])

    def test_a_completion_claim_is_a_claim_and_a_failure_report_is_not(self) -> None:
        spec = importlib.util.spec_from_file_location("criteria", CRITERIA)
        criteria = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(criteria)
        # The first two are real messages of rounds whose checks printed FAIL (182/9c6475db, 382/3c4bed5f).
        for text in ("All seven done-checks pass, and `bin/check` prints `check: PASSED`.",
                     "The full done-checks block prints `PASS hung-push-stops`, `PASS hung-gh-cut-off` and "
                     "`PASS check-green`, with no FAIL line.",
                     "all 7 done-checks pass", "All done-checks pass; the work is complete.", "Done.",
                     "All ten done-checks pass on HEAD 641bedeb and none fails.",
                     "The checks were failing before the fix, but all seven done-checks pass now.",
                     "No failures remain and the implementation is complete.",
                     "There are no failures left, so the ticket is complete.",
                     "Implementation finished; none of the tests fail anymore."):
            self.assertTrue(criteria.claims_done(text), text)
        for text in ("I don't think we're done.", "We are nowhere near done.",
                     "The work is not even close to being complete.",
                     "I ran the complete test suite; two checks still fail.",
                     "I completed the first two checks; the third, bin/check, still fails on a lint error I could not fix.",
                     "Nothing is finished: bin/check still fails.",
                     "Round 2: seed/x is still outside scope; I could not fix it yet.",
                     "The done-checks still fail; this is not done yet.",
                     "The implementation is complete, but tests fail.",
                     "I completed the first two checks; the third failed.",
                     "I ran our complete test suite; two checks failed.",
                     "The implementation is complete, but bin/check does not pass because the integration test fails.",
                     "The implementation is complete, but one test failure remains.",
                     "The implementation is complete, but bin/check does not pass.",
                     "The code changes are done, but I couldn't get the integration test to run.",
                     "The feature is complete, but the docs are still incomplete.",
                     "The refactor is finished, though two done-checks still report failures.",
                     "Should I mark this ticket done?",
                     # A real ABANDON round's message (323/c45475fe), then the requirement before the report.
                     "I did not commit because the project requires `check: PASSED` before every commit.",
                     "The project requires `check: PASSED` before every commit, so I did not commit.",
                     "If the integration test passes on CI, the work is complete."):
            self.assertFalse(criteria.claims_done(text), text)

    def test_a_stall_before_its_rounds_checks_reads_the_last_checked_round(self) -> None:
        # no-change and a ticket-budget or wall-clock cap exit after `===== round 2 =====`, before round-2.checks.
        runs = pathlib.Path(self.tmp.name) / "stalls"
        for label, exit_line in (("5/aaaa0005", "EXIT no-change (1): HEAD and decisions.md are unchanged since round 1"),
                                 ("6/aaaa0006", "EXIT stopped-cap (3): ticket budget: 10 usd")):
            run_dir(runs, label, "stopped", ["===== launch =====", "===== round 1 =====", "===== round 2 =====",
                                              exit_line], 1)
            (runs / label / "round-1.checks").write_text("FAIL do-not-touch seed/x\nFAIL a: b\n")
        log6 = runs / "6/aaaa0006/factory.log"
        log6.write_text(log6.read_text().replace("2026-10-19", "2026-10-21"))
        # A run that stalls, is relaunched and stalls again is one stall, and a scope stall when any of its stalls is:
        # 8 never fails scope first; 9 stalls on scope, then on another failure; 10 stalls on scope, then its
        # relaunch hits the round cap before a round begins.
        stuck = "EXIT stuck (1): same failing set"
        for label, log in (("8/aaaa0008", ["===== round 1 =====", stuck, "===== launch =====", "===== round 2 =====", stuck]),
                           ("9/aaaa0009", ["===== round 1 =====", stuck, "===== launch =====", "===== round 2 =====", stuck]),
                           ("10/aaaa0010", ["===== round 1 =====", "===== round 2 =====", stuck, "===== launch =====",
                                            "EXIT stopped-cap (3): ROUND_CAP 2 reached"])):
            run_dir(runs, label, "stuck", ["===== launch ====="] + log, 2)
        (runs / "8/aaaa0008/round-2.checks").write_text("FAIL a: b\nFAIL do-not-touch seed/x\n")
        (runs / "9/aaaa0009/round-1.checks").write_text("FAIL do-not-touch seed/x\n")
        (runs / "9/aaaa0009/round-2.checks").write_text("FAIL a: b\n")
        (runs / "10/aaaa0010/round-2.checks").write_text("FAIL do-not-touch seed/x\n")
        proc = factory("status", "--criteria", runs=runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        # The FAIL names the date of its latest offending run, 6's.
        self.assertEqual(verdicts(proc.stdout)["stalls whose first failing grader row is scope"],
                         "    FAIL: measured 4 (of 5 stalls: 5/aaaa0005 round 1, 6/aaaa0006 round 1, 9/aaaa0009 round 1, "
                         "10/aaaa0010 round 2); latest 2026-10-21")

    def test_a_run_that_froze_the_copying_guard_measures_zero_pass_over_lines(self) -> None:
        frozen = self.runs / "1/aaaa0001/frozen"
        frozen.mkdir()
        (frozen / "lib.sh").write_text((ROOT / "bin/factory.d/lib.sh").read_text())
        proc = factory("status", "--criteria", runs=self.runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(verdicts(proc.stdout)["lines per round marking a passed-over step"],
                         "    PASS: measured 0 (over 1 round)")

    def test_lint_of_an_edited_body_reaches_the_launchs_run_dir_once(self) -> None:
        # A Claude Code session's lint (the stage-2 session's), which records nothing; then lint, an edit, lint again,
        # then a launch that FACTORY_STOP halts once its owner events are written. gh is a stub serving the body in
        # $BODY_FILE to lint's issue view and to run's GraphQL read (#389), written by the owner; its timeline read
        # fails, so the launch records no issue events.
        body = pathlib.Path(self.tmp.name) / "body"
        runs = pathlib.Path(self.tmp.name) / "lint-runs"
        runs.mkdir()
        (runs / "FACTORY_STOP").touch()
        script = (
            '. bin/factory; assert_target_ready() { :; }; claude_version_ok() { :; }; notify() { :; }; '
            'gh() { case "$1 $2" in "issue view") cat "$BODY_FILE" ;; "api graphql") jq -n --rawfile b "$BODY_FILE" '
            '\'{data: {repository: {issue: {body: $b, author: {login: "SamyakJhaveri"}, editor: null, lastEditedAt: null}}}}\' ;; '
            '*) return 1 ;; esac; }; '
            'echo "# one" > "$BODY_FILE"; CLAUDECODE=1 lint 9 > /dev/null 2>&1; lint 9 > /dev/null 2>&1; echo "# two" > "$BODY_FILE"; lint 9 > /dev/null 2>&1; '
            '(cmd_run 9) > /dev/null 2>&1; (cmd_run 9) > /dev/null 2>&1; true'
        )
        env = {k: v for k, v in os.environ.items() if k not in ("FACTORY_CALL_TAG", "LOAM_HOOK", "CLAUDECODE", "FACTORY_BY_NEXT")}
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, capture_output=True, text=True, check=False,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), "FACTORY_RUNS_ROOT": str(runs),
                                   "BODY_FILE": str(body)})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        (run,) = [d for d in (runs / "9").iterdir() if d.is_dir()]
        self.assertEqual((run / "status").read_text().strip(), "stopped")
        # Both lint lines, then each launch's run line; the relaunch does not add the lint lines again.
        kinds = [json.loads(line)["kind"] for line in (run / "owner-events.jsonl").read_text().splitlines()]
        self.assertEqual(kinds, ["lint", "lint", "run", "run"])
        self.assertFalse((runs / "9/owner-events.jsonl").exists())

    def test_owner_events_reads_the_operators_issue_and_pr_events(self) -> None:
        # gh is a stub that applies the real --jq program with jq to GitHub-shaped replies, keyed by the API path.
        gh_dir = pathlib.Path(self.tmp.name) / "gh"
        gh_dir.mkdir()
        (gh_dir / "user").write_text('{"login":"me"}')
        (gh_dir / "issue").write_text('{"user":{"login":"me"},"created_at":"T0","state":"closed"}')
        (gh_dir / "timeline").write_text("""[
          {"id":1,"event":"labeled","actor":{"login":"me"},"created_at":"T0"},
          {"id":2,"event":"assigned","actor":{"login":"me"},"created_at":"T1"},
          {"id":3,"event":"commented","actor":{"login":"me"},"created_at":"T1","body":"**Stopped.** worker text"},
          {"id":4,"event":"commented","actor":{"login":"me"},"created_at":"T1","body":"please also"},
          {"id":5,"event":"commented","actor":{"login":"other"},"created_at":"T1","body":"hi"},
          {"id":6,"event":"reviewed","user":{"login":"me"},"submitted_at":"T2"},
          {"id":7,"event":"merged","actor":{"login":"me"},"created_at":"T3"},
          {"id":8,"event":"closed","actor":{"login":"me"},"created_at":"T3"},
          {"sha":"abc","event":"committed","author":{"name":"me"}}]""")
        run = self.runs / "9/aaaa0009"
        run_dir(self.runs, "9/aaaa0009", "pr-opened",
                ["EXIT pr-opened (0): https://github.com/o/loam/pull/10 after 1 rounds, 2 usd"], 1)
        script = (
            '. bin/factory; net() { "$@"; }; '
            'gh() { local p="" f; case "$2" in user) f=user ;; */timeline) f=timeline ;; *) f=issue ;; esac; '
            'while [ $# -gt 0 ]; do [ "$1" = --jq ] && { p="$2"; shift; }; shift; done; jq -r "$p" "$GH_DIR/$f"; }; '
            'owner_events "$1" launch o/loam 9 && owner_events "$1" launch o/loam 9 && pr_closed_events && pr_closed_events'
        )
        env = {k: v for k, v in os.environ.items() if k not in ("FACTORY_CALL_TAG", "LOAM_HOOK", "CLAUDECODE", "FACTORY_BY_NEXT")}
        proc = subprocess.run(["bash", "-c", script, "_", str(run)], cwd=ROOT, capture_output=True, text=True, check=False,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_RUNS_ROOT": str(self.runs), "GH_DIR": str(gh_dir)})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        events = [(e["phase"], e["kind"], e["id"]) for e in map(json.loads, (run / "owner-events.jsonl").read_text().splitlines())]
        # The creation label, the assignment, notify's comment, another login's and a merge's closed are not actions;
        # a relaunch and a second tick add nothing.
        self.assertEqual(events, [("launch", "opened", "opened"), ("launch", "commented", "4"), ("launch", "reviewed", "6"),
                                  ("launch", "merged", "7"), ("pr", "commented", "4"), ("pr", "reviewed", "6"),
                                  ("pr", "merged", "7")])
        self.assertTrue((run / "pr-closed").exists())

    def test_next_reads_a_closed_prs_events_while_every_slot_is_held(self) -> None:
        # The run's PR is closed but its ticket worktree remains, so it holds the one slot and next launches nothing.
        run = self.runs / "9/aaaa0009"
        run_dir(self.runs, "9/aaaa0009", "pr-opened", ["EXIT pr-opened (0): https://github.com/o/loam/pull/10"], 1)
        (pathlib.Path(self.tmp.name) / "co-9").mkdir()
        script = (
            '. bin/factory; MAIN_CHECKOUT="$1/co"; assert_target_ready() { :; }; claude_logged_in() { :; }; '
            'claude_version_ok() { :; }; net() { "$@"; }; '
            'gh() { [ "$2" = repos/o/loam/issues/10 ] && echo closed; }; '
            'owner_events() { echo "{\\"phase\\":\\"$2\\"}" >> "$1/owner-events.jsonl"; }; cmd_next'
        )
        proc = subprocess.run(["bash", "-c", script, "_", self.tmp.name], cwd=ROOT, capture_output=True, text=True,
                              check=False, env={**os.environ, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                                                "FACTORY_RUNS_ROOT": str(self.runs), "FACTORY_MAX_PARALLEL": "1"})
        self.assertEqual((proc.returncode, proc.stdout), (0, "nothing to launch\n"), proc.stderr)
        self.assertEqual((run / "owner-events.jsonl").read_text(), '{"phase":"pr"}\n')
        self.assertTrue((run / "pr-closed").exists())

    def test_guard_copies_a_pass_over_marker_past_dev_null(self) -> None:
        # The guard line sends bin/check's output to /dev/null; its SKIPPED: lines still reach the checks file.
        proc = subprocess.run(
            ["bash", "-c", '. bin/factory.d/lib.sh; guard sh -c "echo SKIPPED: gpu; echo noise; exit 3" >/dev/null; '
             'echo "rc=$?"; guard echo SKIPPED: once'],
            cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(proc.stdout, "SKIPPED: gpu\nrc=3\nSKIPPED: once\n", proc.stderr)

    def test_dash_C_reports_only_the_other_targets_runs(self) -> None:
        repo = pathlib.Path(self.tmp.name) / "r"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", "https://github.com/o/r.git"], check=True)
        proc = factory("-C", str(repo), "status", "--criteria", runs=self.runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = proc.stdout.splitlines()
        self.assertIn(": 1 run under ", lines[0])
        self.assertIn("    PASS: measured 4 (over 1 PR run)", lines)

    def test_a_missing_factory_log_is_unmeasured_not_zero(self) -> None:
        # Exits come only from factory.log, so a run without one has unknown exits, not none.
        runs = pathlib.Path(self.tmp.name) / "nolog"
        run_dir(runs, "2/aaaa0002", "pr-opened", [], 1)
        (runs / "2/aaaa0002/factory.log").unlink()
        proc = factory("status", "--criteria", runs=runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = proc.stdout.splitlines()
        verdict = {line: lines[i + 1] for i, line in enumerate(lines) if line.startswith("- ")}
        for line in ("- rounds lost to environment failures: 0 (baseline 2)",
                     "- median rounds to PR: at most 5 (lean-v3 median)"):
            self.assertEqual(verdict[line], "    UNMEASURED: no factory.log in 2/aaaa0002", line)

    def test_grader_first_fail_names_the_first_grader_failure(self) -> None:
        def fallback(role: str) -> dict:
            # The object call_json writes after three rejected replies.
            judge = role == "judge"
            return {"verdict": "fail" if judge else "fix", "unparseable": True, "rows": {}, "evidence": {}, "fixes": [],
                    "backlog": ["judge output unparseable or inconsistent after 3 calls; rerun the judge on this round"]
                    if judge else [],
                    "findings": [{"severity": "high", "file": "-", "line": 0, "defect": f"{role} output unparseable",
                                  "fix": f"rerun the {role} on this round"}]}

        def envelope(reply: str) -> dict:
            # The claude -p --output-format json reply call_json saves as round-N.<stem>.raw.<attempt>.json.
            return {"type": "result", "subtype": "success", "result": reply}

        rows_pass = {"correct": "pass", "verified": "pass", "honest": "pass"}
        blocking_review = {"verdict": "fix", "findings": [{"severity": "high", "file": "bin/y", "line": 1,
                                                           "defect": "d", "fix": "f"}]}
        not_json = envelope("I ran out of turns before grading.")
        # Each case: the round's files, then the expected item. Each review blocks, so reading the review before the
        # judge, or a fallback's rows or findings before its unparseable flag, prints another item.
        cases = {
            "judge-unparseable": ({"judge.json": fallback("judge"), "judge.raw.3.json": not_json,
                                   "review.json": blocking_review}, "judge:unparseable"),
            "judge-inconsistent": ({"judge.json": fallback("judge"), "review.json": blocking_review,
                                    "judge.raw.3.json": envelope(json.dumps(
                                        {"verdict": "fail", "rows": rows_pass, "fixes": []}))}, "judge:inconsistent"),
            "review-unparseable": ({"judge.json": {"verdict": "pass", "rows": rows_pass, "fixes": []},
                                    "review.json": fallback("review"), "review.raw.3.json": not_json},
                                   "review:unparseable"),
            "review-inconsistent": ({"judge.json": {"verdict": "pass", "rows": rows_pass, "fixes": []},
                                     "review.json": fallback("review"),
                                     "review.raw.3.json": envelope("```json\n" + json.dumps(
                                         {"verdict": "fail", "findings": []}) + "\n```")},
                                    "review:inconsistent"),
            "judge-row": ({"judge.json": {"verdict": "fail", "rows": {**rows_pass, "verified": "fail"}, "fixes": ["x"]},
                           "review.json": blocking_review}, "judge:verified"),
            "judge-fail": ({"judge.json": {"verdict": "fail", "rows": rows_pass, "fixes": ["x"]},
                            "review.json": blocking_review}, "judge:fail"),
            "review-finding": ({"judge.json": {"verdict": "pass", "rows": rows_pass, "fixes": []},
                                "review.json": blocking_review}, "review:bin/y"),
        }
        for label, (files, expected) in cases.items():
            run = pathlib.Path(self.tmp.name) / label
            run.mkdir()
            for name, body in files.items():
                (run / f"round-2.{name}").write_text(json.dumps(body) + "\n")
            proc = grader_first_fail(run)
            self.assertEqual((proc.returncode, proc.stdout), (0, expected), (label, proc.stderr))

    def test_escaped_defects_are_later_reverts_and_caused_by_lines(self) -> None:
        repo = pathlib.Path(self.tmp.name) / "repo"

        def git(*args: str) -> str:
            return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *args], capture_output=True, text=True,
                                  check=True, env={**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}).stdout.strip()

        def pr(n: int, *messages: str) -> str:
            """Merge factory/<n>, one commit per message, as PR #<n>; the sha of its first commit."""
            git("checkout", "-q", "-b", f"factory/{n}", "main")
            for i, message in enumerate(messages):
                (repo / f"{n}-{i}").write_text(message)
                git("add", ".")
                git("commit", "-q", "-m", message)
            git("checkout", "-q", "main")
            git("merge", "-q", "--no-ff", "-m", f"Merge pull request #{n} from o/factory/{n}", f"factory/{n}")
            return git("rev-list", "--reverse", f"main^1..factory/{n}").split()[0]

        repo.mkdir()
        git("init", "-q", "-b", "main")
        git("commit", "-q", "--allow-empty", "-m", "base")
        pr(1, "one")
        git("revert", "-m", "1", "--no-edit", "HEAD")  # the whole merge
        first = pr(2, "two", "three")
        git("revert", "--no-edit", first)  # one commit of the PR, after it merged
        pr(3, "four")
        git("commit", "-q", "--allow-empty", "-m", "fix the four\n\nCaused-by: #3")
        # A revert inside the PR's own branch, and a Caused-by naming no factory PR, are no escape.
        git("checkout", "-q", "-b", "factory/4", "main")
        (repo / "five").write_text("five")
        git("add", ".")
        git("commit", "-q", "-m", "five")
        git("revert", "--no-edit", "HEAD")
        git("checkout", "-q", "main")
        git("merge", "-q", "--no-ff", "-m", "Merge pull request #4 from o/factory/4", "factory/4")
        git("commit", "-q", "--allow-empty", "-m", "fix\n\nCaused-by: #9")
        # A merge from a branch under feature/factory/ is no factory PR, though its work is reverted.
        git("checkout", "-q", "-b", "feature/factory/5", "main")
        (repo / "six").write_text("six")
        git("add", ".")
        git("commit", "-q", "-m", "six")
        git("checkout", "-q", "main")
        git("merge", "-q", "--no-ff", "-m", "Merge pull request #5 from o/feature/factory/5", "feature/factory/5")
        git("revert", "--no-edit", "-m", "1", "HEAD")
        # A checkout on a feature branch still measures main: this Caused-by never merged.
        git("checkout", "-q", "-b", "topic", "main")
        git("commit", "-q", "--allow-empty", "-m", "fix\n\nCaused-by: #4")
        proc = subprocess.run(["python3", "-I", str(CRITERIA), str(self.runs), str(ROOT / "docs/factory/ARCHITECTURE.md"),
                               str(repo)], capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertRegex(proc.stdout.splitlines()[-1],
                         r"^escaped defects: 3 of 4 merged factory PRs: #1 \(\w{8}\), #2 \(\w{8}\), #3 \(\w{8}\)$")

    def test_thresholds_come_from_the_doc(self) -> None:
        arch = pathlib.Path(self.tmp.name) / "ARCHITECTURE.md"
        arch.write_text("Criteria written in advance:\n\n- median rounds to PR: at most 1\n- a new criterion: 0\n"
                        "\nAfter.\n- x: 0\n")

        def criteria(runs: pathlib.Path) -> list[str]:
            proc = subprocess.run(["python3", "-I", str(CRITERIA), str(runs), str(arch), "t"],
                                  capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            lines = proc.stdout.splitlines()
            # The target t is no git checkout, so the escaped defects line cannot be measured.
            self.assertTrue(lines[-1].startswith("escaped defects: UNMEASURED: git log of t failed"), lines[-1])
            return lines[1:-1]

        self.assertEqual(criteria(self.runs), [
            "- median rounds to PR: at most 1", "    FAIL: measured 2 (over 3 PR runs)",
            "- a new criterion: 0", "    UNMEASURED: criteria.py has no measure for this line",
        ])
        self.assertEqual(criteria(self.runs / "none")[1], f"    UNMEASURED: no run directory under {self.runs / 'none'}")
        # A lower bound over its threshold fails, since the true count is at least as high.
        arch.write_text("Criteria written in advance:\n\n- operator actions after the PR opens: 0\n")
        (self.runs / "1/aaaa0001/owner-events.jsonl").write_text('{"phase":"pr","kind":"merged"}\n')
        self.assertTrue(criteria(self.runs)[1].startswith("    FAIL: measured at least 1 ("), criteria(self.runs))


if __name__ == "__main__":
    unittest.main()
