"""`bin/factory status --criteria` measures the ARCHITECTURE.md trust criteria from one target's run directories.

A synthetic runs root holds a PR in one round, a PR after a parallel-cap exit and an environment-lost round, a PR
whose first launch died mid-round and whose relaunch hit the parallel cap, a file-ticket rehearsal that opens no PR,
and an abandoned run with more rounds than any PR. Another target's run sits under <owner>__<repo>/ and counts only
with -C. A second root holds one run with the records the other criteria read: owner-events.jsonl, a stall, a
pass-over marker, judge evidence_kind, and Claude and Codex worker messages. No network, no model.
"""

from __future__ import annotations

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
        self.assertEqual(verdict["rounds lost to environment failures"], "    FAIL: measured 1 (2/aaaa0002 round 1)")
        self.assertEqual(verdict["median rounds to PR"], "    PASS: measured 2 (over 3 PR runs)")
        self.assertEqual(verdict["stalls whose first failing grader row is scope"], "    PASS: measured 0 (of 0 stalls)")
        self.assertEqual(verdict["rounds whose last worker message claims done while the checks printed FAIL"],
                         "    PASS: measured 0 (claude 0, codex 0)")
        # A run from before owner-events.jsonl, evidence_kind and guard's marker copy shows no operator action, no cited
        # notes and no marker, which is not zero of them.
        for name in ("operator actions from voice note to a running loop on Track B",
                     "operator actions after the PR opens", "judge fails citing a worker-written measurement",
                     "lines per round marking a passed-over step"):
            self.assertTrue(verdict[name].startswith("    UNMEASURED: "), (name, verdict[name]))
        self.assertEqual(len(verdict), 8, verdict)
        # One header line and the eight criteria: no run table, stop counts, or grader versions.
        lines = proc.stdout.splitlines()
        self.assertIn(f": 5 runs under {self.runs} ", lines[0])
        self.assertEqual(len(lines), 1 + 2 * 8, proc.stdout)

    def test_the_run_records_measure_the_other_criteria(self) -> None:
        runs = pathlib.Path(self.tmp.name) / "records"
        # A relaunch after the stall opened the PR, so the median has its run too.
        run_dir(runs, "7/abcd1234", "pr-opened",
                ["===== launch =====", "===== round 1 =====", "===== round 2 =====", "===== round 3 =====",
                 "EXIT stuck (1): same failing set"], 3)
        d = runs / "7/abcd1234"
        (d / "round-1.checks").write_text("SKIPPED: gpu\nSKIPPED: node\nFAIL a: b\n")
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
        (d / "round-3.last.txt").write_text("Finished the change.\n")
        proc = factory("status", "--criteria", runs=runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("UNMEASURED", proc.stdout)
        verdict = verdicts(proc.stdout)
        self.assertTrue(verdict["operator actions from voice note to a running loop on Track B"]
                        .startswith("    PASS: measured at least 3 (most in one run, 7/abcd1234, of 1 run; omits "))
        self.assertTrue(verdict["operator actions after the PR opens"].startswith("    PASS: measured at least 1 ("))
        self.assertEqual(verdict["stalls whose first failing grader row is scope"],
                         "    FAIL: measured 1 (of 1 stall: 7/abcd1234 round 3)")
        self.assertEqual(verdict["lines per round marking a passed-over step"],
                         "    FAIL: measured 2 (7/abcd1234 round 1)")
        self.assertEqual(verdict["judge fails citing a worker-written measurement"],
                         "    FAIL: measured 1 of 2 (7/abcd1234 round 3 correct)")
        self.assertEqual(verdict["rounds whose last worker message claims done while the checks printed FAIL"],
                         "    FAIL: measured 2 (claude 1, codex 1)")

    def test_a_run_that_froze_the_copying_guard_measures_zero_pass_over_lines(self) -> None:
        frozen = self.runs / "1/aaaa0001/frozen"
        frozen.mkdir()
        (frozen / "lib.sh").write_text((ROOT / "bin/factory.d/lib.sh").read_text())
        proc = factory("status", "--criteria", runs=self.runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(verdicts(proc.stdout)["lines per round marking a passed-over step"],
                         "    PASS: measured 0 (over 1 round)")

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
        env = {k: v for k, v in os.environ.items() if k not in ("FACTORY_CALL_TAG", "LOAM_HOOK", "FACTORY_BY_NEXT")}
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

    def test_grader_first_fail_names_unparseable_grader_replies(self) -> None:
        judge_run = pathlib.Path(self.tmp.name) / "judge-unparseable"
        judge_run.mkdir()
        (judge_run / "round-2.judge.json").write_text(
            '{"verdict":"fail","unparseable":true,"rows":{},"findings":[]}\n'
        )
        (judge_run / "round-2.review.json").write_text('{"verdict":"merge","findings":[]}\n')

        proc = grader_first_fail(judge_run)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "judge:unparseable")

        review_run = pathlib.Path(self.tmp.name) / "review-unparseable"
        review_run.mkdir()
        (review_run / "round-1.judge.json").write_text(
            '{"verdict":"pass","rows":{"correct":"pass","verified":"pass","honest":"pass"}}\n'
        )
        (review_run / "round-1.review.json").write_text(
            '{"verdict":"fix","unparseable":true,"findings":[]}\n'
        )

        proc = grader_first_fail(review_run)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "review:unparseable")

        parsed_run = pathlib.Path(self.tmp.name) / "parsed-judge"
        parsed_run.mkdir()
        (parsed_run / "round-3.judge.json").write_text(
            '{"verdict":"fail","rows":{"correct":"pass","verified":"fail","honest":"pass"}}\n'
        )
        (parsed_run / "round-3.review.json").write_text('{"verdict":"merge","findings":[]}\n')

        proc = grader_first_fail(parsed_run)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout, "judge:verified")

    def test_thresholds_come_from_the_doc(self) -> None:
        arch = pathlib.Path(self.tmp.name) / "ARCHITECTURE.md"
        arch.write_text("Criteria written in advance:\n\n- median rounds to PR: at most 1\n- a new criterion: 0\n"
                        "\nAfter.\n- x: 0\n")

        def criteria(runs: pathlib.Path) -> list[str]:
            proc = subprocess.run(["python3", "-I", str(CRITERIA), str(runs), str(arch), "t"],
                                  capture_output=True, text=True, check=False)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            return proc.stdout.splitlines()[1:]

        self.assertEqual(criteria(self.runs), [
            "- median rounds to PR: at most 1", "    FAIL: measured 2 (over 3 PR runs)",
            "- a new criterion: 0", "    UNMEASURED: criteria.py has no measure for this line",
        ])
        self.assertEqual(criteria(self.runs / "none")[1], f"    UNMEASURED: no run directory under {self.runs / 'none'}")


if __name__ == "__main__":
    unittest.main()
