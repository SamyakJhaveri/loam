"""The run's caps: the default round cap is three, so after round 3 the run stops stopped-cap before a fourth worker
call (owner, 12 Nov 2026); and MAX_HOURS stops the run before each long step that makes no model call: the round's
checks, the full gate, the mutation sweep and the Rows measured commands (L01 ran 73.7 min past its 4 h cap in round checks and learn, 13 Nov 2026).

`bin/factory` is sourced (FACTORY_SOURCED=1) with no FACTORY_ cap in the environment and an empty Worker section,
so apply_caps leaves the default. The real main_loop runs; the worker call is stubbed to record its round and stop.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class RoundCapTests(unittest.TestCase):
    def main_loop(self, last_done: int) -> tuple[subprocess.CompletedProcess, pathlib.Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run = pathlib.Path(tmp.name)
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_RUNS_ROOT=str(run / "runs"))
        script = (". bin/factory\n"
                  f"RUN='{run}'; LOG=\"$RUN/log\"; DECISIONS=\"$RUN/decisions.md\"; KEY=t; IS_FILE=1; BRANCH=t\n"
                  'BODY=""; apply_caps\n'
                  "notify() { :; }; check_frozen() { :; }; assert_caps() { :; }\n"
                  f'worker_round() {{ echo "$1" > "$RUN/worker-called"; exit 0; }}\n'
                  f"ROUND={last_done}; main_loop\n")
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, check=False, timeout=60)
        return proc, run

    def test_fourth_round_is_refused(self) -> None:
        proc, run = self.main_loop(3)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertEqual((run / "status").read_text().strip(), "stopped-cap")
        self.assertIn("round cap: 3 rounds", proc.stderr)
        self.assertFalse((run / "worker-called").exists())

    def test_third_round_runs(self) -> None:
        proc, run = self.main_loop(2)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual((run / "worker-called").read_text().strip(), "3")


class HourCapTests(unittest.TestCase):
    """The launch is 5 h old against a 4 h cap when each step starts; the frozen checks.sh and mutation_sweep.py and the
    ticket's Rows measured command the steps would run record that they ran."""

    def step(self, call: str) -> tuple[subprocess.CompletedProcess, pathlib.Path]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        run = pathlib.Path(tmp.name) / "run"
        wt = pathlib.Path(tmp.name) / "wt"
        (run / "frozen").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(wt)], check=True)
        subprocess.run(["git", "-C", str(wt), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
                        "--allow-empty", "-m", "base"], check=True)
        head = subprocess.run(["git", "-C", str(wt), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
        (run / "base.sha").write_text(head + "\n")
        for name in ("protected.txt", "exempt.txt"):
            (run / "frozen" / name).write_text("")
        checks = run / "frozen" / "checks.sh"
        checks.write_text(f"#!/bin/sh\ntouch '{run}/checks-ran'\necho CHECKS-END\n")
        checks.chmod(0o755)
        (run / "frozen" / "mutation_sweep.py").write_text(
            f"open('{run}/sweep-ran', 'w').write('')\nopen(__import__('sys').argv[3], 'w').write('{{\"mutants\": []}}')\n")
        (run / "round-1.checks").write_text("DEFERRED: bin/check\ncheck: PASSED\nCHECKS-END\n")
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_RUNS_ROOT=str(run / "runs"), FACTORY_MAX_HOURS="4")
        script = (". bin/factory\n"
                  f"RUN='{run}'; WORKTREE='{wt}'; LOG=\"$RUN/log\"; DECISIONS=\"$RUN/decisions.md\"; KEY=t; IS_FILE=1\n"
                  f'BRANCH=t; BODY=$\'## Rows measured\\n\\n- speed: touch {run}/rows-ran; echo 1 | 1\\n\'; apply_caps; touch "$DECISIONS"; GRADED_SHA=$(cat "$RUN/base.sha")\n'
                  "notify() { :; }; check_frozen() { :; }\n"
                  'stale() { echo $(( $(date -u +%s) - 5 * 3600 )) > "$RUN/launched"; }\n'
                  'date -u +%s > "$RUN/launched"\n'
                  f"{call}\n")
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, check=False, timeout=60)
        return proc, run

    def assert_capped(self, proc: subprocess.CompletedProcess, run: pathlib.Path) -> None:
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertEqual((run / "status").read_text().strip(), "stopped-cap")
        self.assertIn("EXIT stopped-cap (2): wall clock: 5h of 4h", proc.stderr)
        self.assertFalse((run / "checks-ran").exists(), "the checks ran past the cap")
        self.assertFalse((run / "sweep-ran").exists(), "the mutation sweep ran past the cap")
        self.assertFalse((run / "rows-ran").exists(), "the Rows measured command ran past the cap")

    def test_a_worker_call_that_ends_past_the_cap_stops_before_the_round_checks(self) -> None:
        # The worker call starts in time (its own cap check passes) and ends past the cap.
        self.assert_capped(*self.step("worker_round() { stale; }; ROUND=0; main_loop"))

    def test_the_full_gate_does_not_start_past_the_cap(self) -> None:
        self.assert_capped(*self.step("stale; ROUND=1; gate_last"))

    def test_the_mutation_sweep_does_not_start_past_the_cap(self) -> None:
        self.assert_capped(*self.step("stale; ROUND=1; run_mutation_sweep 1"))

    def test_the_rows_measured_commands_do_not_start_past_the_cap(self) -> None:
        self.assert_capped(*self.step("stale; ROUND=1; measure_rows 1"))

    def test_a_measured_sample_that_ends_past_the_cap_stops_the_next_sample(self) -> None:
        proc, run = self.step('BODY=$\'## Rows measured\\n\\n- runs=2 speed: echo x >> "$RUN/samples"; stale; echo 1 | 1\\n\'\n'
                              "ROUND=1; measure_rows 1")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertEqual((run / "status").read_text().strip(), "stopped-cap")
        self.assertEqual((run / "samples").read_text(), "x\n")

    def test_in_time_the_steps_run(self) -> None:
        # The same calls inside the cap reach the checks and the sweep, so the tests above can see them run.
        proc, run = self.step("ROUND=1; measure_rows 1; run_mutation_sweep 1; gate_last; echo gate=$?")
        self.assertIn("gate=0", proc.stdout, proc.stderr)
        self.assertTrue((run / "rows-ran").exists())
        self.assertTrue((run / "checks-ran").exists())
        self.assertTrue((run / "sweep-ran").exists())


if __name__ == "__main__":
    unittest.main()
