"""The default round cap is three: after round 3 the run stops stopped-cap before a fourth worker call (owner, 12 Nov 2026).

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


if __name__ == "__main__":
    unittest.main()
