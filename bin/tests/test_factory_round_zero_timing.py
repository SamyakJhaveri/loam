"""Round 0 times the done-checks block on base against the worker's Stop hook timeout, and the worker prompt lists
each check's base seconds.

A block that outruns the Stop hook is cancelled at every stop, so round 0 ends such a run as ticket-defect, naming each
check over a third of the timeout (300 s of 900 s); distbench's J31 spent 90 min in one block call. bin/factory is
sourced (FACTORY_SOURCED=1) and the real round_zero and build_worker_prompt run over a scratch repository, with a frozen
worker-settings.json whose Stop hook timeout is 3 s, so a check of 2 s stands for one over 300 s.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
BLOCK = ('sleep 2; fail slow-a "not yet"\n'
         'fail quick "not yet"\n'
         'sleep 2; fail slow-b "not yet"')


class RoundZeroTimingTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        repo = self.tmp / "repo"
        repo.mkdir()
        git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "base"]):
            subprocess.run(git + args, check=True)
        self.run_dir = self.tmp / "run"
        (self.run_dir / "frozen").mkdir(parents=True)
        shutil.copy(ROOT / "bin/factory.d/_common.md", self.run_dir / "frozen/_common.md")

    def round_one(self, hook_timeout: int) -> str:
        """stdout of the real round_zero over BLOCK at the scratch repo's base, then round 1's worker prompt."""
        run = self.run_dir
        (run / "frozen/worker-settings.json").write_text(json.dumps(
            {"hooks": {"Stop": [{"hooks": [{"type": "command", "timeout": hook_timeout, "command": "true"}]}]}}))
        (run / "issue.md").write_text(f"## Done checks\n\n```done-checks\n{BLOCK}\n```\n")
        script = (f"RUN='{run}'; WORKTREE='{run}/wt'; MAIN_CHECKOUT='{self.tmp}/repo'; LOG=\"$RUN/log\"\n"
                  'finish() { echo "FINISH $1: $2"; exit 0; }\n'
                  'BODY=$(cat "$RUN/issue.md"); git -C "$MAIN_CHECKOUT" rev-parse HEAD > "$RUN/base.sha"\n'
                  "{ cat bin/factory.d/lib.sh; echo; dc_block; echo; echo \"$CHECKS_END\"; echo 'exit $((n_fail > 0))'; }"
                  ' > "$RUN/frozen/checks.sh"; chmod +x "$RUN/frozen/checks.sh"\n'
                  'round_zero; echo ROUND0-OK; WORKER_KIND=claude; round=1; cat "$(build_worker_prompt 1)"')
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**os.environ, "FACTORY_SOURCED": "1", "HOME": str(self.tmp)},
                              capture_output=True, text=True, check=False, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def times(self) -> list[tuple[int, str]]:
        rows = (self.run_dir / "round-0.times").read_text().split("\n")
        return [(int(secs), name) for secs, name in (row.split() for row in rows if row)]

    def test_a_block_slower_than_the_stop_hook_is_a_ticket_defect_naming_its_slow_checks(self) -> None:
        out = self.round_one(hook_timeout=3)
        (finish,) = [line for line in out.splitlines() if line.startswith("FINISH")]
        self.assertRegex(finish, r"^FINISH ticket-defect: the done-checks block took \d+ s on \w{8}, over the worker "
                                 r"Stop hook's 3 s timeout; checks over 1 s: slow-a \(\d+ s\), slow-b \(\d+ s\); see ")
        self.assertNotIn("quick", finish)
        self.assertNotIn("ROUND0-OK", out)
        self.assertFalse((self.run_dir / "round-0.checks").exists())

    def test_round_one_prompt_lists_each_check_s_seconds_on_base(self) -> None:
        out = self.round_one(hook_timeout=30)
        self.assertIn("ROUND0-OK", out)
        times = self.times()
        self.assertEqual([name for _, name in times], ["slow-a", "quick", "slow-b"])
        secs = dict((name, s) for s, name in times)
        self.assertGreaterEqual(secs["slow-a"], 2)
        self.assertGreaterEqual(secs["slow-b"], 2)
        self.assertLessEqual(secs["quick"], 1)
        prompt = out.split("ROUND0-OK\n", 1)[1]
        self.assertIn("## Done-check seconds on base (round 0)", prompt)
        self.assertIn("".join(f"{s} {name}\n" for s, name in times), prompt)

    def test_no_prompt_line_asks_the_worker_to_run_the_whole_block(self) -> None:
        # The Stop hook runs the block at every stop; an order to run it as well ran it 3-5 times a round.
        prompt = self.round_one(hook_timeout=30).split("ROUND0-OK\n", 1)[1]
        self.assertNotIn("checks.sh", prompt)
        self.assertNotRegex(prompt.lower(), r"run the done-checks block")


if __name__ == "__main__":
    unittest.main()
