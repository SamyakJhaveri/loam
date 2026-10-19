"""A round is never green when the done-checks block aborts before a FAIL line or glues its result mid-line (#180).

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real round_zero and main_loop run a checks.sh built, as
freeze builds it, from the real lib.sh and a block. The worker call and the graders are stubbed, so no model is
called; main_loop prints GREEN when it reaches the graders.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

# The second check reads a variable no one sets; under lib.sh's `set -u` the block dies after `PASS a`, exit 1.
ABORT_AFTER_PASS = ['true && pass a || fail a "x"',
                    'echo "$FACTORY_TEST_UNSET" > /dev/null && pass b || fail b "x"',
                    'true && pass c || fail c "x"']
# The failing command prints without a trailing newline, so lib.sh's FAIL lands mid-line.
GLUED_FAIL = ['true && pass a || fail a "x"',
              '{ printf "no newline"; false; } && pass b || fail b "x"']
# The control: a guard and a check, both passing.
CLEAN = ['guard true && pass g || fail g "x"',
         'true && pass a || fail a "x"']
# Run 60's shape: a real check whose line quotes a ticket body holding its own `pass a || fail a`.
NESTED_QUOTE = ['body=\'true && pass a || fail a "x"\'; grep -qF \'pass a\' <<<"$body" && pass nested || fail nested "x"']

# On base only the guard passes before the block dies, so no FAIL line is printed.
ABORT_ON_BASE = ['guard true && pass g || fail g "x"',
                 'echo "$FACTORY_TEST_UNSET" > /dev/null && pass b || fail b "x"',
                 'false && pass c || fail c "x"']
GLUED_PASS = ['false && pass a || fail a "x"',
              '{ printf "no newline"; true; } && pass b || fail b "x"']
FAILS_ON_BASE = ['guard true && pass g || fail g "x"',
                 'false && pass a || fail a "x"',
                 '{ printf "no newline"; false; } && pass b || fail b "x"']

FREEZE = """BODY=$(cat "$RUN/issue.md")
mkdir -p "$RUN/frozen"
{ cat "$ROOT/bin/factory.d/lib.sh"; echo; dc_block; echo; echo 'exit $((n_fail > 0))'; } > "$RUN/frozen/checks.sh"
chmod +x "$RUN/frozen/checks.sh"
"""


def git(*args: str, cwd: pathlib.Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


class ChecksGreenTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git("init", "-q", "-b", "main", cwd=self.repo)
        git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "base", cwd=self.repo)
        self.env = {**os.environ, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                    "FACTORY_RUNS_ROOT": str(self.tmp / "runs")}
        self.env.pop("FACTORY_TEST_UNSET", None)

    def sourced(self, name: str, block: list[str], script: str) -> tuple[subprocess.CompletedProcess, pathlib.Path]:
        run = self.tmp / f"run-{name}"
        run.mkdir()
        (run / "issue.md").write_text("```done-checks\n" + "\n".join(block) + "\n```\n")
        prelude = f"RUN='{run}'; LOG=\"$RUN/log\"; KEY=t; IS_FILE=1\n"
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{prelude}{FREEZE}{script}"], cwd=ROOT,
                              env=self.env, capture_output=True, text=True, check=False)
        return proc, run

    def main_loop(self, name: str, block: list[str]) -> tuple[bool, str]:
        """(green, round-1 checks output): one round, then the round cap stops a failing round."""
        script = (f"WORKTREE='{self.repo}'; DECISIONS=\"$RUN/decisions.md\"; BRANCH=t; MAX_ROUNDS=1\n"
                  'touch "$DECISIONS"\n'
                  "worker_round() { :; }; check_frozen() { :; }; assert_caps() { :; }; do_not_touch_hits() { :; }\n"
                  "measure_rows() { echo GREEN; exit 0; }\n"
                  "main_loop")
        proc, run = self.sourced(name, block, script)
        green = "GREEN" in proc.stdout
        if not green:
            self.assertEqual((run / "status").read_text().strip(), "stopped-cap", proc.stderr)
        return green, (run / "round-1.checks").read_text()

    def round_zero(self, name: str, block: list[str]) -> tuple[bool, str]:
        """(accepted, the log): round 0 at the repo's HEAD; a rejected block ends ticket-defect."""
        script = (f"MAIN_CHECKOUT='{self.repo}'; WORKTREE='{self.tmp}/wt-{name}'\n"
                  'git -C "$MAIN_CHECKOUT" rev-parse HEAD > "$RUN/base.sha"\n'
                  "round_zero; echo ROUND0-ACCEPTED")
        proc, run = self.sourced(name, block, script)
        accepted = "ROUND0-ACCEPTED" in proc.stdout
        if not accepted:
            self.assertEqual(proc.returncode, 3, proc.stderr)
            self.assertEqual((run / "status").read_text().strip(), "ticket-defect")
        return accepted, proc.stderr

    def test_main_loop_block_that_aborts_is_not_green(self) -> None:
        green, checks = self.main_loop("abort", ABORT_AFTER_PASS)
        self.assertFalse(green, checks)
        self.assertIn("FAIL checks-aborted: checks.sh exited 1", checks)

    def test_main_loop_glued_fail_is_not_green(self) -> None:
        green, checks = self.main_loop("glued", GLUED_FAIL)
        self.assertFalse(green, checks)
        self.assertIn("\nFAIL b: x\n", checks)

    def test_main_loop_clean_block_is_green(self) -> None:
        green, checks = self.main_loop("clean", CLEAN)
        self.assertTrue(green, checks)

    def test_main_loop_check_quoting_a_nested_block_is_green(self) -> None:
        green, checks = self.main_loop("nested", NESTED_QUOTE)
        self.assertTrue(green, checks)
        self.assertIn("PASS nested\n", checks)

    def test_round_zero_rejects_a_block_that_aborts_on_base(self) -> None:
        accepted, log = self.round_zero("abort", ABORT_ON_BASE)
        self.assertFalse(accepted, log)
        self.assertIn("checks.sh aborted on", log)

    def test_round_zero_rejects_a_glued_pass_on_base(self) -> None:
        accepted, log = self.round_zero("glued", GLUED_PASS)
        self.assertFalse(accepted, log)
        self.assertIn("check b passes on", log)

    def test_round_zero_accepts_a_block_that_fails_on_base(self) -> None:
        accepted, log = self.round_zero("clean", FAILS_ON_BASE)
        self.assertTrue(accepted, log)


if __name__ == "__main__":
    unittest.main()
