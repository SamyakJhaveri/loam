"""Round 0 times the done-checks block in its run on base, cut off at the worker Stop hook's timeout, and the worker
prompt lists each check's base seconds.

A block that does not end in that time on base is a ticket-defect naming each check over a third of it (300 s of
900 s); distbench's J31 spent 90 min in one block call. bin/factory is sourced (FACTORY_SOURCED=1) and the real
round_zero and build_worker_prompt run over a scratch repository with ROUND0_SECS set to 3, so a check of 2 s stands
for one over 300 s.
"""

from __future__ import annotations

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
        shutil.copy(ROOT / "bin/factory.d/lib.sh", self.run_dir / "frozen/lib.sh")

    def round_one(self, limit: int, block: str = BLOCK, loam: bool = True) -> str:
        """stdout of the real round_zero over block at the scratch repo's base, cut off at limit seconds, then round 1's
        prompt for a Claude worker and for a Codex worker, each after a `PROMPT <kind>` line."""
        run = self.run_dir
        (run / "issue.md").write_text(f"## Done checks\n\n```done-checks\n{block}\n```\n")
        script = (f"RUN='{run}'; WORKTREE='{run}/wt'; MAIN_CHECKOUT='{self.tmp}/repo'; LOG=\"$RUN/log\"\n"
                  f"ROUND0_SECS={limit}; TARGET_IS_LOAM={int(loam)}\n"
                  'finish() { echo "FINISH $1: $2"; exit 0; }\n'
                  'BODY=$(cat "$RUN/issue.md"); git -C "$MAIN_CHECKOUT" rev-parse HEAD > "$RUN/base.sha"\n'
                  "{ cat bin/factory.d/lib.sh; echo; dc_block; echo; echo \"$CHECKS_END\"; echo 'exit $((n_fail > 0))'; }"
                  ' > "$RUN/frozen/checks.sh"; chmod +x "$RUN/frozen/checks.sh"\n'
                  'round_zero; echo ROUND0-OK; round=1\n'
                  'for WORKER_KIND in claude codex; do echo "PROMPT $WORKER_KIND"; cat "$(build_worker_prompt 1)"; done')
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**os.environ, "FACTORY_SOURCED": "1", "HOME": str(self.tmp)},
                              capture_output=True, text=True, check=False, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def prompts(self, loam: bool = True) -> dict[str, str]:
        _, claude, codex = self.round_one(limit=30, loam=loam).split("ROUND0-OK\n", 1)[1].split("PROMPT ")
        return {"claude": claude, "codex": codex}

    def finish(self, out: str) -> str:
        (finish,) = [line for line in out.splitlines() if line.startswith("FINISH")]
        self.assertNotIn("ROUND0-OK", out)
        self.assertFalse((self.run_dir / "round-0.checks").exists())
        return finish

    def times(self) -> list[tuple[int, str]]:
        rows = (self.run_dir / "round-0.times").read_text().split("\n")
        return [(int(secs), name) for secs, name in (row.split() for row in rows if row)]

    def test_a_block_that_does_not_end_in_the_limit_is_a_ticket_defect_naming_its_slow_checks(self) -> None:
        finish = self.finish(self.round_one(limit=3))
        self.assertRegex(finish, r"^FINISH ticket-defect: the done-checks block did not end within 3 s on \w{8}, the "
                                 r"worker Stop hook's timeout; finished checks over 1 s: slow-a \(\d+ s\) \(a check still running "
                                 r"at the limit is not named\); see ")
        self.assertEqual([name for _, name in self.times()], ["slow-a", "quick"])

    def test_a_block_that_ends_inside_the_limit_is_not_cut_off(self) -> None:
        # Only timeout's own exit status ends the run: a block that ends a moment before the limit is not refused.
        self.assertIn("ROUND0-OK", self.round_one(limit=3, block='sleep 2.5; fail near "not yet"'))

    def test_a_nested_shell_that_sources_lib_sh_records_no_time(self) -> None:
        # Only the block's own results are its checks; a script it runs that sources lib.sh has its own clock.
        block = f"bash -c '. {self.run_dir}/frozen/lib.sh; fail inner x' > /dev/null; fail outer \"not yet\""
        self.assertIn("ROUND0-OK", self.round_one(limit=30, block=block))
        self.assertEqual([name for _, name in self.times()], ["outer"])

    def test_round_one_prompt_lists_each_check_s_seconds_on_base(self) -> None:
        out = self.round_one(limit=30)
        self.assertIn("ROUND0-OK", out)
        times = self.times()
        self.assertEqual([name for _, name in times], ["slow-a", "quick", "slow-b"])
        secs = dict((name, s) for s, name in times)
        self.assertGreaterEqual(secs["slow-a"], 2)
        self.assertGreaterEqual(secs["slow-b"], 2)
        self.assertLessEqual(secs["quick"], 1)
        for kind in ("claude", "codex"):
            prompt = out.split(f"PROMPT {kind}\n", 1)[1].split("PROMPT ", 1)[0]
            self.assertIn("## Done-check seconds on base (round 0)", prompt)
            self.assertIn("".join(f"{s} {name}\n" for s, name in times), prompt)

    def test_only_a_worker_with_no_stop_hook_is_told_to_run_the_whole_block(self) -> None:
        # A Claude worker's Stop hook runs the block at every stop; an order to run it as well ran it 3-5 times a round.
        # A Codex worker has no Stop hook, so its prompt carries the one run the hook would make.
        prompts = self.prompts()
        self.assertNotIn("checks.sh", prompts["claude"])
        (line,) = [line for line in prompts["codex"].splitlines() if "checks.sh" in line]
        self.assertIn(f"`LOAM_HOOK=1 bash {self.run_dir}/frozen/checks.sh`", line)
        self.assertIn("before you finish", line)


    def test_a_codex_worker_elsewhere_runs_the_lines_by_hand_when_the_block_calls_the_gate_another_way(self) -> None:
        # Under LOAM_HOOK only the exact `guard bin/check` passes unrun, so `guard ./bin/check` in checks.sh would run
        # another target's full gate, which its worker must never run.
        (line,) = [line for line in self.prompts(loam=False)["codex"].splitlines() if "checks.sh" in line]
        self.assertIn("other than exactly `guard bin/check`", line)
        self.assertIn("by hand", line)
        (line,) = [line for line in self.prompts()["codex"].splitlines() if "checks.sh" in line]
        self.assertNotIn("by hand", line)


if __name__ == "__main__":
    unittest.main()
