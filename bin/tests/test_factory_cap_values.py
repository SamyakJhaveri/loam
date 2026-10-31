"""A cap value that is not a positive number fails lint and stops a launch (#427).

GNU timeout reads a duration of 0 as no limit, so NET_TIMEOUT_SEC=0 or CALL_TIMEOUT_SEC=0 would drop the bound
the cap exists for. Each test plants 0, -5 and abc: through a Worker line (check_worker, apply_caps), through
FACTORY_<NAME> (apply_caps), and through FACTORY_NET_TIMEOUT_SEC, which lint, next and status read at load
without apply_caps. A good whole number and a good decimal still pass.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
BAD = ("0", "-5", "abc")
CAPS = ("MAX_ROUNDS", "ROUND_BUDGET_USD", "GRADER_BUDGET_USD", "TICKET_BUDGET_USD", "DAILY_BUDGET_USD",
        "MAX_HOURS", "MAX_TURNS", "CALL_TIMEOUT_SEC", "NET_TIMEOUT_SEC", "MAX_PARALLEL")
WORKER = "## Worker\nworker: claude\ncodex-review: no\neffort: high\ngoal: x, or stop after 5 turns\n"


def clean_env(**extra: str) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
    return {**env, **extra}


def sourced(script: str, **extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", "-c", ". bin/factory\n" + script], cwd=ROOT, env=clean_env(FACTORY_SOURCED="1", **extra),
                          stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False, timeout=60)


class CheckWorkerTests(unittest.TestCase):
    def errs(self, line: str) -> subprocess.CompletedProcess:
        return sourced('SRC=t; ERRS=0; BODY="$CAP_BODY"; check_worker; echo "errs=$ERRS"', CAP_BODY=WORKER + line + "\n")

    def test_bad_values_are_one_error_naming_the_cap(self) -> None:
        for name in ("NET_TIMEOUT_SEC", "CALL_TIMEOUT_SEC", "MAX_PARALLEL", "ROUND_BUDGET_USD"):
            for v in BAD:
                with self.subTest(name=name, v=v):
                    proc = self.errs(f"{name}={v}")
                    self.assertIn("errs=1", proc.stdout, proc.stderr)
                    self.assertIn(name, proc.stderr)

    def test_decimal_in_a_whole_number_cap_is_an_error(self) -> None:
        proc = self.errs("NET_TIMEOUT_SEC=2.5")
        self.assertIn("errs=1", proc.stdout, proc.stderr)

    def test_good_values_pass(self) -> None:
        for line in ("NET_TIMEOUT_SEC=30", "ROUND_BUDGET_USD=2.5", "DAILY_BUDGET_USD=100", "MAX_PARALLEL=1"):
            with self.subTest(line=line):
                proc = self.errs(line)
                self.assertIn("errs=0", proc.stdout, proc.stderr)


class ApplyCapsTests(unittest.TestCase):
    def test_bad_environment_value_exits_naming_the_cap(self) -> None:
        for name in CAPS:
            for v in BAD:
                with self.subTest(name=name, v=v):
                    proc = sourced('BODY=""; apply_caps; echo applied', **{f"FACTORY_{name}": v})
                    self.assertEqual(proc.returncode, 2, proc.stdout)
                    self.assertNotIn("applied", proc.stdout)
                    self.assertIn(f"FACTORY_{name}", proc.stderr)

    def test_bad_worker_line_exits_naming_the_cap(self) -> None:
        for v in BAD:
            with self.subTest(v=v):
                proc = sourced(f'BODY=$(printf "## Worker\\nCALL_TIMEOUT_SEC={v}\\n"); apply_caps; echo applied')
                self.assertEqual(proc.returncode, 2, proc.stdout)
                self.assertIn("CALL_TIMEOUT_SEC", proc.stderr)

    def test_good_values_are_set(self) -> None:
        proc = sourced('BODY=$(printf "## Worker\\nNET_TIMEOUT_SEC=30\\nROUND_BUDGET_USD=2.5\\n"); apply_caps '
                       '&& echo "ok $NET_TIMEOUT_SEC $ROUND_BUDGET_USD $MAX_TURNS"', FACTORY_MAX_TURNS="40")
        self.assertIn("ok 30 2.5 40", proc.stdout, proc.stderr)


class LoadTimeTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.bin = pathlib.Path(tmp.name)
        gh = self.bin / "gh"
        gh.write_text("#!/usr/bin/env bash\nexit 1\n")
        gh.chmod(0o755)

    def run_factory(self, *args: str, **extra: str) -> subprocess.CompletedProcess:
        env = clean_env(PATH=f"{self.bin}:{os.environ['PATH']}", FACTORY_RUNS_ROOT=str(self.bin / "runs"), **extra)
        return subprocess.run([str(ROOT / "bin" / "factory"), *args], cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, check=False, timeout=60)

    def test_lint_next_and_status_fail_naming_the_cap(self) -> None:
        for args in (("lint", "7"), ("next", "--dry-run"), ("status",)):
            for v in BAD:
                with self.subTest(args=args, v=v):
                    proc = self.run_factory(*args, FACTORY_NET_TIMEOUT_SEC=v)
                    self.assertEqual(proc.returncode, 2, proc.stderr)
                    self.assertIn("FACTORY_NET_TIMEOUT_SEC", proc.stderr)


if __name__ == "__main__":
    unittest.main()
