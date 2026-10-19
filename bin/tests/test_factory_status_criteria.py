"""`bin/factory status --criteria` measures the ARCHITECTURE.md trust criteria from one target's run directories.

A synthetic runs root holds one run per count: a PR in one round, a PR after an environment-lost round, a
parallel-cap exit, SKIP lines and two judge send-backs, a round-0 stop, an abandon, and a round-0 stop that a
relaunch went past. Another target's run sits under <owner>__<repo>/ and counts only with -C. No network, no model.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
CRITERIA = ROOT / "bin/factory.d/criteria.py"
INHERITED = ("FACTORY_ROOT", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER")
CACHE = "/home/u/.claude/plugins/cache/seed-skills/sam-cc-setup/0.9.4/agents"
CHECKOUT = "/home/u/loam/cultivation/marketplace/sam-cc-setup/agents"
JUDGE_SHA = hashlib.sha256((AGENTS / "judge.md").read_bytes()).hexdigest()
REVIEWER_SHA = hashlib.sha256((AGENTS / "reviewer.md").read_bytes()).hexdigest()
OLD = "0" * 64
PASS = json.dumps({"rows": {"correct": "pass", "verified": "pass", "honest": "pass"}, "fixes": [], "verdict": "pass"})
FAIL = json.dumps({"rows": {"correct": "fail", "verified": "pass", "honest": "pass"}, "fixes": ["x"], "verdict": "fail"})


def graders(base: str, judge: str, reviewer: str) -> list[dict]:
    return [{"event": "grader", "role": "judge", "file": f"{base}/judge.md", "sha256": judge},
            {"event": "grader", "role": "reviewer", "file": f"{base}/reviewer.md", "sha256": reviewer}]


def call(rnd: int, role: str, usd: float | None) -> dict:
    return {"round": rnd, "role": role, "model": "m", "cost_usd": usd}


def run_dir(root: pathlib.Path, label: str, status: str, ledger: list[dict], log: list[str],
            checks: dict[int, str], judges: dict[int, str]) -> None:
    d = root / label
    d.mkdir(parents=True)
    (d / "status").write_text(status + "\n")
    (d / "ledger.jsonl").write_text("".join(json.dumps(e) + "\n" for e in ledger))
    (d / "factory.log").write_text("".join(f"2026-10-19T00:00:00Z {line}\n" for line in log))
    for n, text in checks.items():
        (d / f"round-{n}.checks").write_text(text)
    for n, text in judges.items():
        (d / f"round-{n}.judge.json").write_text(text)


def loam_runs(runs: pathlib.Path) -> None:
    run_dir(runs, "1/aaaa0001", "pr-opened",
            graders(CACHE, JUDGE_SHA, OLD) + [call(1, "worker", 2.0), call(1, "judge", 0.5), call(1, "reviewer", 0.25),
                                              call(1, "codex-review", None)],
            ["===== round 1 =====", "EXIT pr-opened (0): https://github.com/o/loam/pull/2 after 1 rounds"],
            {0: "FAIL a\n", 1: "PASS a\n"}, {1: PASS})
    # The first EXIT comes before any round (a parallel-cap exit), the second loses round 1 to the environment.
    run_dir(runs, "2/aaaa0002", "pr-opened",
            graders(CHECKOUT, JUDGE_SHA, REVIEWER_SHA) + [call(1, "worker", 1.0), call(1, "worker", 1.0),
                                                          call(1, "judge", 0.5), call(2, "worker", 1.0),
                                                          call(2, "judge", 0.5), call(3, "worker", 1.0),
                                                          call(3, "judge", 0.5)],
            ["EXIT stopped-environment (4): parallel cap: 1 other live run(s), MAX_PARALLEL=1",
             "===== round 1 =====",
             "EXIT stopped-environment (4): the worker call failed before doing work: unknown error",
             "===== round 1 =====", "===== round 2 =====", "===== round 3 =====",
             "EXIT pr-opened (0): https://github.com/o/loam/pull/3 after 3 rounds"],
            {0: "FAIL a\n", 1: "PASS a\n", 2: "PASS a\nSKIP b slow\nSKIP c net\n", 3: "PASS a\nSKIP b slow\n"},
            {1: FAIL, 2: "", 3: PASS})
    run_dir(runs, "3/aaaa0003", "ticket-defect", graders(CACHE, JUDGE_SHA, OLD),
            ["EXIT ticket-defect (3): check a passes on base"], {0: "PASS a\n"}, {})
    run_dir(runs, "4/aaaa0004", "abandon", [call(1, "worker", 4.0)],
            ["===== round 1 =====", "EXIT abandon (5): ABANDON the goal needs a do-not-touch path"],
            {0: "FAIL a\n"}, {})
    run_dir(runs, "5/aaaa0005", "pr-opened",
            graders(CACHE, JUDGE_SHA, OLD) + [call(1, "worker", 1.0), call(1, "judge", 0.5)],
            ["EXIT ticket-defect (3): check a passes on base", "resuming after round 0", "===== round 1 =====",
             "EXIT pr-opened (0): https://github.com/o/loam/pull/6 after 1 rounds"],
            {0: "PASS a\n", 1: "PASS a\n"}, {1: PASS})
    run_dir(runs, "o__r/7/bbbb0007", "pr-opened",
            graders(CACHE, JUDGE_SHA, OLD) + [call(1, "worker", 9.0), call(2, "worker", 1.0)],
            ["===== round 1 =====", "===== round 2 =====", "EXIT pr-opened (0): https://github.com/o/r/pull/8"],
            {0: "FAIL a\n", 1: "PASS a\n", 2: "PASS a\n"}, {1: FAIL, 2: PASS})


def factory(*args: str, runs: pathlib.Path) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k not in INHERITED}
    return subprocess.run([str(ROOT / "bin/factory"), *args], cwd=ROOT, env={**env, "FACTORY_RUNS_ROOT": str(runs)},
                          capture_output=True, text=True, check=False)


def block(out: str, header: str) -> list[str]:
    """The lines of one `== <header>` section, up to the blank line that ends it."""
    lines = out.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("== " + header))
    end = next((i for i in range(start + 1, len(lines)) if not lines[i]), len(lines))
    return lines[start + 1:end]


class StatusCriteriaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.runs = pathlib.Path(self.tmp.name) / "runs"
        loam_runs(self.runs)

    def test_table_and_stop_counts_from_the_loam_runs_only(self) -> None:
        proc = factory("status", "--criteria", runs=self.runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(f": 5 runs under {self.runs} ", proc.stdout.splitlines()[0])
        self.assertEqual(proc.stdout.splitlines()[1:8], [
            "runs                            5",
            "PR opened                       3",
            "spend                           13.75 usd",
            "spend on runs with no PR        4.00 usd",
            "median rounds to PR             1",
            "grader spend                    2.75 usd",
            "PR runs the judge sent back     1 of 3",
        ])
        self.assertEqual(block(proc.stdout, "stops"), [
            "round-0 stops (ticket-defect)   2 exits; 1 run stopped for good (0.00 usd); relaunched past it: 5/aaaa0005",
            "worker abandons                 1 exit; 1 run stopped for good (4.00 usd)",
            "judge send-backs                2 rounds with a non-pass judge verdict, in 1 run",
        ])

    def test_each_criterion_from_architecture_md_gets_a_verdict_or_unmeasured(self) -> None:
        out = factory("status", "--criteria", runs=self.runs).stdout
        crit = dict(zip(*[iter(block(out, "criteria"))] * 2))
        self.assertEqual(crit["- rounds lost to environment failures: 0 (baseline 2)"],
                         "    FAIL: measured 1 (2/aaaa0002 round 1)")
        self.assertEqual(crit["- SKIP lines per round: 0"],
                         "    FAIL: measured 2 (the most in one round-N.checks; 3 in all 10)")
        self.assertEqual(crit["- median rounds to PR: at most 5 (lean-v3 median)"],
                         "    PASS: measured 1 (over 3 PR runs)")
        self.assertTrue(crit["- stalls whose first failing grader row is scope: 0 (baseline 3 of 4)"].startswith(
            "    UNMEASURED: no judge.json has a scope row (rows seen: correct, honest, verified)"))
        for line in ("- operator actions from voice note to a running loop on Track B: at most 3",
                     "- operator actions after the PR opens: at most 1 once F9 lands",
                     "- judge fails citing a worker-written measurement: 0 (S2 had at least four)"):
            self.assertTrue(crit[line].startswith("    UNMEASURED: "), (line, crit[line]))
        self.assertEqual(len(crit), 7, crit)

    def test_grader_versions_and_sha_match_against_this_checkout(self) -> None:
        out = factory("status", "--criteria", runs=self.runs).stdout
        self.assertEqual(block(out, "graders"), [
            f"0.9.4       3 runs  judge {JUDGE_SHA[:8]} =   reviewer 00000000 !=",
            f"checkout    1 run   judge {JUDGE_SHA[:8]} =   reviewer {REVIEWER_SHA[:8]} = ",
            "none        1 run   (no grader event in the ledger)",
        ])

    def test_dash_C_reports_the_other_targets_runs(self) -> None:
        repo = pathlib.Path(self.tmp.name) / "r"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", "https://github.com/o/r.git"], check=True)
        proc = factory("-C", str(repo), "status", "--criteria", runs=self.runs)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(": 1 run under ", proc.stdout.splitlines()[0])
        self.assertEqual(proc.stdout.splitlines()[1:8], [
            "runs                            1",
            "PR opened                       1",
            "spend                           10.00 usd",
            "spend on runs with no PR        0.00 usd",
            "median rounds to PR             2",
            "grader spend                    0.00 usd",
            "PR runs the judge sent back     1 of 1",
        ])

    def test_thresholds_come_from_the_doc_and_a_scope_row_is_measured(self) -> None:
        runs = pathlib.Path(self.tmp.name) / "scope"
        scope = json.dumps({"rows": {"correct": "pass", "scope": "fail"}, "fixes": ["x"], "verdict": "fail"})
        run_dir(runs, "9/cccc0009", "pr-opened", [], ["===== round 1 =====", "EXIT pr-opened (0): u"],
                {1: "PASS a\n"}, {1: scope})
        arch = pathlib.Path(self.tmp.name) / "ARCHITECTURE.md"
        arch.write_text("Criteria written in advance:\n\n- median rounds to PR: at most 0\n"
                        "- stalls whose first failing grader row is scope: 0\n- a new criterion: 0\n\nAfter.\n- x: 0\n")
        proc = subprocess.run(["python3", "-I", str(CRITERIA), str(runs), str(arch), str(AGENTS), "t"],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(block(proc.stdout, "criteria"), [
            "- median rounds to PR: at most 0", "    FAIL: measured 1 (over 1 PR run)",
            "- stalls whose first failing grader row is scope: 0", "    FAIL: measured 1 (9/cccc0009)",
            "- a new criterion: 0", "    UNMEASURED: criteria.py has no measure for this line",
        ])
        empty = subprocess.run(["python3", "-I", str(CRITERIA), str(runs / "none"), str(arch), str(AGENTS), "t"],
                               capture_output=True, text=True, check=False).stdout
        self.assertEqual(block(empty, "criteria")[1], f"    UNMEASURED: no run directory under {runs / 'none'}")


if __name__ == "__main__":
    unittest.main()
