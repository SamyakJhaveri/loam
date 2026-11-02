"""A `predict NAME CMD...` line's CMD runs whole at round 0 only, and checks.sh carries no predict line (CONTRACT.md).

bin/factory is sourced (FACTORY_SOURCED=1) and the real round_zero runs the block at the base commit of a scratch
repository, with `finish` replaced so a ticket defect prints instead of exiting; lint runs as `bin/factory lint` over
a whole body. The freeze tests run the real cmd_run on a file ticket through freeze and round 0, with the target gate,
the re-exec into the frozen copy and the worker loop stubbed as in test_factory_round_zero_relaunch.py.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
LIB = ROOT / "bin/factory.d/lib.sh"
GREET = 'test -f g.txt && grep -q hello g.txt && pass greet || fail greet "g.txt lacks hello"'
GUARD = 'guard true && pass g || fail g "guard"'
GRADERS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
STUBS = ("assert_target_ready() { :; }; claude_version_ok() { :; }; exec_frozen() { :; }; "
         'main_loop() { finish stopped-environment "stub worker round"; }')


class PredictTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        repo = self.tmp / "repo"
        repo.mkdir()
        (repo / "g.txt").write_text("bye\n")
        git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        for args in (["init", "-q"], ["add", "g.txt"], ["commit", "-qm", "base"]):
            subprocess.run(git + args, check=True)

    def round_zero(self, checks: str) -> str:
        """stdout of the real round_zero over a done-checks block run at the scratch repo's base commit."""
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True, exist_ok=True)
        (run / "issue.md").write_text(f"## Done checks\n\n```done-checks\n{checks}\n```\n")
        script = (f"RUN='{run}'; WORKTREE='{run}/wt'; MAIN_CHECKOUT='{self.tmp}/repo'; LOG=\"$RUN/log\"\n"
                  'finish() { echo "FINISH $1: $2"; exit 0; }\n'
                  'BODY=$(cat "$RUN/issue.md"); git -C "$MAIN_CHECKOUT" rev-parse HEAD > "$RUN/base.sha"\n'
                  'cp bin/factory.d/lib.sh "$RUN/frozen/lib.sh"\n'
                  "{ cat bin/factory.d/lib.sh; echo; dc_script; echo; echo \"$CHECKS_END\"; echo 'exit $((n_fail > 0))'; }"
                  ' > "$RUN/frozen/checks.sh"; chmod +x "$RUN/frozen/checks.sh"\n'
                  "round_zero; echo ROUND0-OK")
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**os.environ, "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def lint(self, checks: str, worker: str = "contract: 2\n") -> tuple[int, str]:
        """Exit code and output of `bin/factory lint` over a whole body with this block and these extra Worker lines."""
        body = ("# Lint fixture\nBrief:\nfixture\nBlocked by: none\n\n## Goal and why\nfixture\n\n"
                "## Do not touch\nThe standing list.\n\n## Out of scope\nnothing\n\n"
                f"## Done checks\n```done-checks\n{checks}\n```\n\n"
                f"## Worker\nworker: claude\ncodex-review: no\neffort: high\n{worker}"
                "goal: the done-checks block prints no FAIL line, or stop after 60 turns\n\n## Decisions\nnone\n")
        path = self.tmp / "ticket.md"
        path.write_text(body)
        proc = subprocess.run(["bin/factory", "lint", str(path)], cwd=ROOT, capture_output=True, text=True,
                              check=False)
        return proc.returncode, proc.stdout + proc.stderr

    def cmd_run(self, stem: str, checks: str, status: str = "stopped-environment") -> pathlib.Path:
        """The run dir of the real cmd_run over a file ticket with this block, stopped by the stub worker loop."""
        ticket = self.tmp / f"{stem}.md"
        ticket.write_text(f"# Fixture\n\n## Done checks\n\n```done-checks\n{checks}\n```\n")
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
        env.update(FACTORY_SOURCED="1", FACTORY_ROOT=str(ROOT), FACTORY_RUNS_ROOT=str(self.tmp / "runs"),
                   FACTORY_WORKER_ADVISOR="")
        script = (f". bin/factory\n{STUBS}\nMAIN_CHECKOUT='{self.tmp}/repo'; GRADERS_DIR='{GRADERS}'\n"
                  f"cmd_run '{ticket}'")
        proc = subprocess.run(["bash", "-c", script], cwd=ROOT, env=env, capture_output=True, text=True, check=False)
        (run,) = (self.tmp / "runs" / stem).iterdir()
        self.assertEqual((run / "status").read_text().strip(), status, proc.stdout + proc.stderr)
        return run

    def test_correct_prediction_passes_round_zero(self) -> None:
        out = self.round_zero(f"predict greet test -f g.txt\n{GREET}")
        self.assertEqual(out.strip(), "ROUND0-OK")
        self.assertTrue((self.tmp / "run/round-0.checks").is_file())

    def test_wrong_prediction_is_a_ticket_defect(self) -> None:
        for predict in ("predict greet test ! -f g.txt", "predict greet return 7",
                        "predict greet test -f g.txt && grep -q hey g.txt", "predict greet grep -q bye g.txt | false"):
            with self.subTest(predict=predict):
                out = self.round_zero(f"{predict}\n{GREET}")
                self.assertIn("FINISH ticket-defect: the predict line for check greet exits", out)

    def test_predict_line_with_no_command_is_a_ticket_defect(self) -> None:
        for predict in ("predict greet", "predict greet # note"):
            with self.subTest(predict=predict):
                out = self.round_zero(f"{predict}\n{GREET}")
                self.assertIn("FINISH ticket-defect: the predict line for check greet has no command", out)

    def test_whole_line_prediction_holds(self) -> None:
        for predict in ("predict greet ! grep -q hello g.txt", "predict greet [[ -f g.txt ]]",
                        "predict greet test -f g.txt && ! grep -q hello g.txt",
                        'predict greet test "$(cat g.txt)" = bye', "predict greet false || true",
                        "predict greet test 'a ' = a\\ "):
            with self.subTest(predict=predict):
                self.assertEqual(self.round_zero(f"{predict}\n{GREET}").strip(), "ROUND0-OK")

    def test_body_without_predict_lines_runs_as_before(self) -> None:
        self.assertEqual(self.round_zero(GREET).strip(), "ROUND0-OK")

    def test_checks_sh_carries_no_predict_line(self) -> None:
        marker = self.tmp / "ran"
        out = self.round_zero(f"predict greet test -f g.txt && touch {marker}\n  predict  zzz true\n{GREET}")
        self.assertEqual(out.strip(), "ROUND0-OK")
        self.assertTrue(marker.is_file())
        marker.unlink()
        checks = (self.tmp / "run/frozen/checks.sh").read_text()
        self.assertNotRegex(checks, r"(?m)^\s*predict\s")
        proc = subprocess.run([str(self.tmp / "run/frozen/checks.sh")], cwd=self.tmp / "repo", capture_output=True,
                              text=True, check=False)
        self.assertIn("FAIL greet", proc.stdout)
        self.assertFalse(marker.exists())

    def test_freeze_leaves_the_predict_line_out_of_checks_sh(self) -> None:
        # Round 0 runs the predict text, which touches the marker; the frozen checks.sh must run none of it.
        marker = self.tmp / "ran"
        run = self.cmd_run("plain", f"predict greet test -f g.txt && touch {marker}\n{GREET}")
        self.assertTrue(marker.is_file(), "round 0 did not run the predict text")
        marker.unlink()
        checks = (run / "frozen/checks.sh").read_text()
        self.assertNotRegex(checks, r"(?m)^\s*predict\s")
        self.assertNotIn(str(marker), checks)
        proc = subprocess.run([str(run / "frozen/checks.sh")], cwd=self.tmp / "repo", capture_output=True,
                              text=True, check=False)
        self.assertIn("FAIL greet", proc.stdout)
        self.assertFalse(marker.exists())

    def test_continued_line_stops_the_run_before_any_of_it_runs(self) -> None:
        # The block takes no line continuations; a run never linted ends ticket-defect at round 0 with no text run.
        marker = self.tmp / "ran"
        for stem, block in (("continued", f"predict greet test -f g.txt && \\\n  touch {marker}\n{GREET}"),
                            ("split-keyword", f"pre\\\ndict greet true; touch {marker}\n{GREET}"),
                            ("after-comment", f"# note \\\ntouch {marker}\n{GREET}")):
            with self.subTest(stem=stem):
                self.cmd_run(stem, block, status="ticket-defect")
                self.assertFalse(marker.exists())

    def test_lint_rejects_a_line_that_ends_in_a_backslash(self) -> None:
        # bash reads `\\` as a literal backslash, so this predict line ends there; joining it with the next line
        # dropped the regression check from checks.sh while lint printed OK.
        for block in (f"{GREET}\npredict demo printf '%s' \\\\\nguard false && pass regression || fail regression broken",
                      f"predict greet test -f g.txt && \\\n  true\n{GREET}\n{GUARD}", f"# note \\\n{GREET}\n{GUARD}"):
            with self.subTest(block=block):
                rc, out = self.lint(block, worker="")
                self.assertNotEqual(rc, 0, out)
                self.assertIn("done-checks line ends in a backslash", out)

    def test_pipe_into_grep_q_passes(self) -> None:
        # grep -q exits at its first match and yes dies of SIGPIPE; the block and predict CMD run without pipefail.
        self.assertEqual(self.round_zero(f"predict greet yes | grep -q y\n{GREET}").strip(), "ROUND0-OK")
        for shell in (["bash"], ["bash", "-o", "pipefail"]):
            with self.subTest(shell=shell):
                proc = subprocess.run([*shell, "-c", f'. {LIB}; yes | grep -q y && pass piped || fail piped "exit $?"'],
                                      capture_output=True, text=True, check=False)
                self.assertIn("PASS piped", proc.stdout)

    def test_predict_is_quiet_when_a_block_sources_lib(self) -> None:
        proc = subprocess.run(["bash", "-c", f'. {LIB}; predict greet false; echo "rc=$?"'],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.stdout + proc.stderr, "rc=0\n")

    def test_lint_accepts_a_whole_line_prediction(self) -> None:
        for predict in ("predict greet test -f g.txt", "predict greet true", 'predict greet test ! -f "A&B|C>D"',
                        "predict greet test -f A\\&B", "predict greet test -f g.txt && grep -q hello g.txt",
                        "predict greet ! grep -q hello g.txt", "predict greet [[ -f g.txt ]]",
                        "predict greet test -f g.txt 2>/dev/null"):
            with self.subTest(predict=predict):
                rc, out = self.lint(f"{predict}\n{GREET}\n{GUARD}")
                self.assertEqual(rc, 0, out)

    def test_lint_rejects_a_predict_line_that_cannot_run_alone(self) -> None:
        for predict, why in (("predict greet", "has no command"), ("predict greet # test -f g.txt", "has no command"),
                             ("predict greet test -f g.txt )", "on its own line")):
            with self.subTest(predict=predict):
                rc, out = self.lint(f"{predict}\n{GREET}\n{GUARD}", worker="")
                self.assertNotEqual(rc, 0, out)
                self.assertIn(why, out)

    def test_lint_reads_pass_after_a_case_pattern(self) -> None:
        check = 'out=$(cat g.txt); case "$out" in *hello*) pass greet ;; *) fail greet "no hello" ;; esac'
        rc, out = self.lint(f"predict greet test -f g.txt\n{check}\n{GUARD}")
        self.assertEqual(rc, 0, out)
        rc, out = self.lint(f"{check}\n{GUARD}")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("check greet has no predict line", out)

    def test_lint_rejects_a_check_with_no_literal_pass_name(self) -> None:
        check = 'for n in greet; do test -f g.txt && pass "$n" || fail "$n" "no g.txt"; done'
        rc, out = self.lint(f"{check}\n{GUARD}")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("no literal name", out)
        rc, out = self.lint(f"{check}\n{GUARD}", worker="")
        self.assertEqual(rc, 0, out)

    def test_lint_wants_exactly_one_contract_line(self) -> None:
        rc, out = self.lint(f"predict greet test -f g.txt\n{GREET}\n{GUARD}", worker="contract: 2\ncontract: 3\n")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("contract: 2", out)


if __name__ == "__main__":
    unittest.main()
