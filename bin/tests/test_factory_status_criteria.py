"""`bin/factory status --criteria` measures the ARCHITECTURE.md trust criteria from one target's run directories.

A synthetic runs root holds a PR in one round, a PR after a parallel-cap exit and an environment-lost round, a PR
whose first launch died mid-round and whose relaunch hit the parallel cap, a file-ticket rehearsal that opens no PR,
and an abandoned run with more rounds than any PR. Another target's run sits under <owner>__<repo>/ and counts only
with -C. No network, no model.
"""

from __future__ import annotations

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


def factory(*args: str, runs: pathlib.Path) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k not in INHERITED}
    return subprocess.run([str(ROOT / "bin/factory"), *args], cwd=ROOT, env={**env, "FACTORY_RUNS_ROOT": str(runs)},
                          capture_output=True, text=True, check=False)


class StatusCriteriaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.runs = pathlib.Path(self.tmp.name) / "runs"
        loam_runs(self.runs)

    def test_two_criteria_are_measured_and_the_rest_print_unmeasured(self) -> None:
        proc = factory("status", "--criteria", runs=self.runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        lines = proc.stdout.splitlines()
        verdict = {line: lines[i + 1] for i, line in enumerate(lines) if line.startswith("- ")}
        # No check can get a SKIP line into round-N.checks, so seeing none is not a pass.
        self.assertTrue(verdict["- SKIP lines per round: 0"].startswith("    UNMEASURED: "),
                        verdict["- SKIP lines per round: 0"])
        self.assertEqual(verdict["- rounds lost to environment failures: 0 (baseline 2)"],
                         "    FAIL: measured 1 (2/aaaa0002 round 1)")
        self.assertEqual(verdict["- median rounds to PR: at most 5 (lean-v3 median)"],
                         "    PASS: measured 2 (over 3 PR runs)")
        for line in ("- operator actions from voice note to a running loop on Track B: at most 3",
                     "- operator actions after the PR opens: at most 1 once F9 lands",
                     "- stalls whose first failing grader row is scope: 0 (baseline 3 of 4)",
                     "- judge fails citing a worker-written measurement: 0 (S2 had at least four)"):
            self.assertTrue(verdict[line].startswith("    UNMEASURED: "), (line, verdict[line]))
        self.assertEqual(len(verdict), 7, verdict)
        # One header line and the seven criteria: no run table, stop counts, or grader versions.
        self.assertIn(f": 5 runs under {self.runs} ", lines[0])
        self.assertEqual(len(lines), 1 + 2 * 7, proc.stdout)

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
