"""The run's caps: the default round cap is three, so after round 3 the run stops stopped-cap before a fourth worker
call (owner, 12 Nov 2026); and MAX_HOURS counts this launch's round 0 plus the duration_ms of each model call the ledger
booked since the launch, checked only before a worker call. A round whose call started inside the cap runs its checks,
the full gate, the mutation sweep and the Rows measured commands however long the host's locks hold them, and the
cap stops only the next worker call. The replays feed J119's and L01's real ledgers (distbench, 13 and 16 Nov 2026):
J119 passed its checks after a 7.5 h lock wait and lost the round to a wall clock of 11 h on 8 h with 3.8 h of model
time; neither may stop at a cap.

`bin/factory` is sourced (FACTORY_SOURCED=1) with no FACTORY_ cap in the environment and an empty Worker section,
so apply_caps leaves the default. The real main_loop runs; the worker call is stubbed to record its round and stop.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import time
import unittest
from datetime import datetime, timezone

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


def epoch(iso: str) -> int:
    return int(datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp())


def iso(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


HOUR = 3600


class HourCapTests(unittest.TestCase):
    """MAX_HOURS is 4. A launch 5 h old stands for a host lock wait: the frozen checks.sh makes the launch 5 h older
    each time it runs, and records that it ran, as do the frozen mutation_sweep.py and the ticket's Rows measured
    command."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.run = run = pathlib.Path(tmp.name) / "run"
        self.wt = wt = pathlib.Path(tmp.name) / "wt"
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
        checks.write_text(f"#!/bin/sh\ntouch '{run}/checks-ran'\n"
                          f"echo $(( $(cat '{run}/launched') - 5 * {HOUR} )) > '{run}/launched'\n"
                          "echo DEFERRED: bin/check\necho CHECKS-END\n")
        checks.chmod(0o755)
        (run / "frozen" / "mutation_sweep.py").write_text(
            f"open('{run}/sweep-ran', 'w').write('')\nopen(__import__('sys').argv[3], 'w').write('{{\"mutants\": []}}')\n")
        (run / "round-1.checks").write_text("DEFERRED: bin/check\ncheck: PASSED\nCHECKS-END\n")
        (run / "ledger.jsonl").write_text("")
        self.launch(time.time())

    def launch(self, at: float, round0_end: float | None = None) -> None:
        (self.run / "launched").write_text(f"{int(at)}\n")
        if round0_end is not None:
            (self.run / "round-0.checks").write_text("CHECKS-END\n")
            os.utime(self.run / "round-0.checks", (round0_end, round0_end))

    def book(self, *rows: tuple[str, float, int | None]) -> None:
        with (self.run / "ledger.jsonl").open("a") as f:
            for role, ts, ms in rows:
                f.write(json.dumps({"round": 1, "role": role, "duration_ms": ms, "ts": iso(ts)}) + "\n")

    def step(self, call: str) -> subprocess.CompletedProcess:
        run = self.run
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_RUNS_ROOT=str(run / "runs"), FACTORY_MAX_HOURS="4")
        script = (". bin/factory\n"
                  f"RUN='{run}'; WORKTREE='{self.wt}'; LOG=\"$RUN/log\"; LEDGER=\"$RUN/ledger.jsonl\"; KEY=t; IS_FILE=1\n"
                  f'DECISIONS="$RUN/decisions.md"; BRANCH=t; BODY=$\'## Rows measured\\n\\n- speed: touch {run}/rows-ran; echo 1 | 1\\n\'\n'
                  'apply_caps; touch "$DECISIONS"; GRADED_SHA=$(cat "$RUN/base.sha")\n'
                  "notify() { :; }; check_frozen() { :; }\n"
                  'worker_round() { echo "$1" >> "$RUN/worker-calls"; }; grade_round() { echo graded > "$RUN/graded"; exit 0; }\n'
                  f"{call}\n")
        return subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, check=False, timeout=60)

    def assert_capped(self, proc: subprocess.CompletedProcess, why: str) -> None:
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertEqual((self.run / "status").read_text().strip(), "stopped-cap")
        self.assertIn(f"EXIT stopped-cap (2): model time: {why}", proc.stderr)
        self.assertFalse((self.run / "worker-calls").exists(), "the worker call started past the cap")

    def test_a_round_that_waits_5_h_on_its_checks_reaches_its_graders(self) -> None:
        proc = self.step("ROUND=0; main_loop")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue((self.run / "checks-ran").exists())
        self.assertEqual((self.run / "graded").read_text().strip(), "graded", proc.stderr)

    def test_the_steps_after_the_graders_run_5_h_into_a_launch(self) -> None:
        self.launch(time.time() - 5 * HOUR)
        proc = self.step("ROUND=1; measure_rows 1; run_mutation_sweep 1; gate_last; echo gate=$?")
        self.assertIn("gate=0", proc.stdout, proc.stderr)
        for ran in ("rows-ran", "sweep-ran", "checks-ran"):
            self.assertTrue((self.run / ran).exists(), ran)

    def test_model_calls_that_reach_the_cap_stop_the_next_worker_call(self) -> None:
        now = time.time()
        self.book(("worker", now, 3 * HOUR * 1000), ("judge", now, HOUR * 1000))
        self.assert_capped(self.step("ROUND=1; main_loop"), "4h of 4h since this launch")

    def test_round_zero_counts_toward_the_cap(self) -> None:
        self.launch(time.time() - 4 * HOUR, round0_end=time.time())
        self.assert_capped(self.step("ROUND=0; main_loop"), "4h of 4h since this launch")

    def test_an_earlier_launch_s_round_zero_and_calls_count_nothing(self) -> None:
        self.launch(time.time(), round0_end=time.time() - 2 * HOUR)
        self.book(("worker", time.time() - HOUR, 10 * HOUR * 1000))
        proc = self.step("ROUND=0; main_loop")
        self.assertEqual((self.run / "worker-calls").read_text().split(), ["1"], proc.stderr)

    def replay(self, launched: str, round0_end: str, rows: list[tuple[str, str, int | None]],
               worker_calls: list[str], max_hours: int) -> list[str]:
        """The status each worker call of a real run would meet, its ledger replayed up to that call's start."""
        out = []
        for start in worker_calls:
            (self.run / "ledger.jsonl").write_text("")
            (self.run / "status").unlink(missing_ok=True)
            self.launch(epoch(launched), round0_end=epoch(round0_end))
            self.book(*[(role, epoch(ts), ms) for role, ts, ms in rows if epoch(ts) <= epoch(start)])
            proc = self.step(f"MAX_HOURS={max_hours}; assert_caps; echo in-cap")
            out.append(proc.stdout.strip() or (self.run / "status").read_text().strip())
        return out

    J119 = ("2026-11-16T05:34:22Z", "2026-11-16T06:58:08Z",
            [("judge", "2026-11-16T05:34:22Z", None), ("reviewer", "2026-11-16T05:34:22Z", None),
             ("worker", "2026-11-16T09:23:32Z", 8722053)],
            ["2026-11-16T06:58:09Z", "2026-11-16T16:52:49Z"])
    L01 = ("2026-11-13T08:36:32Z", "2026-11-13T09:11:33Z",
           [("judge", "2026-11-13T08:36:31Z", None), ("reviewer", "2026-11-13T08:36:31Z", None),
            ("worker", "2026-11-13T11:08:18Z", 7004439), ("judge", "2026-11-13T11:44:36Z", 33083),
            ("reviewer", "2026-11-13T11:47:49Z", 191813), ("codex-review", "2026-11-13T11:51:06Z", 197000),
            ("worker", "2026-11-13T11:53:04Z", 116569), ("learn-writer", "2026-11-13T13:39:11Z", 454232),
            ("learn-review", "2026-11-13T13:45:09Z", 356330), ("learn-review", "2026-11-13T13:47:52Z", 163000),
            ("verifier", "2026-11-13T13:50:13Z", 139651)],
           ["2026-11-13T09:11:33Z", "2026-11-13T11:51:06Z", "2026-11-13T13:50:13Z"])

    def test_j119_and_l01_replayed_meet_no_cap(self) -> None:
        # J119 ran 8 h, L01 4 h; their last call is one more worker round after everything they booked.
        self.assertEqual(self.replay(*self.J119, max_hours=8), ["in-cap"] * 2)
        self.assertEqual(self.replay(*self.L01, max_hours=4), ["in-cap"] * 3)
        # J119's 1.4 h round 0 and 2.4 h worker call are 3 h of model time after its round, so a 3 h cap stops it.
        self.assertEqual(self.replay(*self.J119, max_hours=3), ["in-cap", "stopped-cap"])


if __name__ == "__main__":
    unittest.main()
