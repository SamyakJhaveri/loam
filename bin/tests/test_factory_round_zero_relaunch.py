"""A relaunch of a body that round 0 stopped runs round 0 again; a run that passed round 0 resumes past it.

`bin/factory` is sourced (FACTORY_SOURCED=1) and cmd_run runs a file ticket over a throwaway repository.
The target gate, the re-exec into the frozen copy, and the worker loop are shell stubs; freeze and round 0
are the real ones. No network, no `claude`.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
GRADERS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
TICKET = """# Relaunch fixture

## Done checks

```done-checks
if [ -f marker ]; then pass has-marker; else fail has-marker "no marker at the root"; fi
```
"""
# The worker loop stops the way a lost login does in round 1: before any round-1 file exists.
STUBS = ("assert_target_ready() { :; }; exec_frozen() { :; }; "
         'main_loop() { echo "main_loop from round $ROUND"; finish stopped-environment "stub worker round"; }')


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class RoundZeroRelaunchTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.main, self.runs = self.top / "main", self.top / "runs"
        self.ticket = self.top / "relaunch.md"
        self.ticket.write_text(TICKET)
        self.main.mkdir()
        git("init", "-q", "-b", "main", cwd=self.main)

    def base(self, with_marker: bool) -> None:
        if with_marker:
            (self.main / "marker").write_text("already done\n")
            git("add", "marker", cwd=self.main)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base", cwd=self.main)

    def launch(self) -> subprocess.CompletedProcess[str]:
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), FACTORY_RUNS_ROOT=str(self.runs), FACTORY_WORKER_ADVISOR="")
        script = f". bin/factory\n{STUBS}\nMAIN_CHECKOUT='{self.main}'; GRADERS_DIR='{GRADERS}'\ncmd_run '{self.ticket}'"
        return subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, capture_output=True, text=True, check=False)

    def run_dir(self) -> pathlib.Path:
        (d,) = (self.runs / "relaunch").iterdir()
        return d

    def status(self) -> str:
        return (self.run_dir() / "status").read_text().strip()

    def log(self) -> str:
        return (self.run_dir() / "factory.log").read_text()

    def test_unchanged_relaunch_runs_round_zero_again(self) -> None:
        self.base(with_marker=True)
        first = self.launch()
        self.assertEqual(first.returncode, 3, first.stderr)
        self.assertEqual(self.status(), "ticket-defect")
        # The exit line names the file that holds the passing check.
        evidence = self.log().splitlines()[-1].rsplit("see ", 1)[1]
        self.assertIn("PASS has-marker", pathlib.Path(evidence).read_text())
        again = self.launch()
        self.assertNotIn("resuming after round", self.log())
        self.assertNotIn("main_loop from round", again.stdout)
        self.assertEqual(again.returncode, 3, again.stderr)
        self.assertEqual(self.status(), "ticket-defect")
        self.assertEqual(self.log().count("EXIT ticket-defect"), 2)

    def test_relaunch_after_an_early_stop_still_runs_round_zero(self) -> None:
        # A stop before round 0 overwrites the ticket-defect status, so the status alone cannot be the rule.
        self.base(with_marker=True)
        self.assertEqual(self.launch().returncode, 3)
        stop = self.run_dir() / "FACTORY_STOP"
        stop.touch()
        self.assertEqual(self.launch().returncode, 2)
        self.assertEqual(self.status(), "stopped")
        stop.unlink()
        again = self.launch()
        self.assertNotIn("resuming after round", self.log())
        self.assertEqual(again.returncode, 3, again.stderr)
        self.assertEqual(self.status(), "ticket-defect")

    def test_run_that_passed_round_zero_resumes_past_it(self) -> None:
        # The control: a stop after a clean round 0 resumes, as runs/66, runs/78, and distbench/293 did.
        self.base(with_marker=False)
        first = self.launch()
        self.assertIn("main_loop from round 0", first.stdout, first.stderr)
        self.assertEqual(self.status(), "stopped-environment")
        again = self.launch()
        self.assertIn("main_loop from round 0", again.stdout, again.stderr)
        self.assertIn("resuming after round 0", self.log())
        self.assertEqual(self.log().count("every non-guard check fails on base"), 1)


if __name__ == "__main__":
    unittest.main()
