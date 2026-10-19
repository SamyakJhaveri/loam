"""Round 0 exempts only a check that calls `guard` (CONTRACT.md, Done checks), read the way lint reads it.

bin/factory is sourced (FACTORY_SOURCED=1) and the real round_zero runs the block at the base commit of a scratch
repository whose README mentions a safeguard; `finish` is replaced so a ticket defect prints instead of exiting.
Lint's check_not_grep_only reads the same block through the same guard reading.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class RoundZeroGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        repo = self.tmp / "repo"
        repo.mkdir()
        (repo / "README.md").write_text("Adds a safeguard.\n")
        git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t"]
        for args in (["init", "-q"], ["add", "README.md"], ["commit", "-qm", "base"]):
            subprocess.run(git + args, check=True)

    def round_zero(self, checks: str) -> str:
        """stdout of the real round_zero over a done-checks block run at the scratch repo's base commit."""
        run = self.tmp / "run"
        (run / "frozen").mkdir(parents=True, exist_ok=True)
        (run / "issue.md").write_text(f"## Done checks\n\n```done-checks\n{checks}\n```\n")
        script = (f"RUN='{run}'; WORKTREE='{run}/wt'; MAIN_CHECKOUT='{self.tmp}/repo'; LOG=\"$RUN/log\"\n"
                  'finish() { echo "FINISH $1: $2"; exit 0; }\n'
                  'BODY=$(cat "$RUN/issue.md"); git -C "$MAIN_CHECKOUT" rev-parse HEAD > "$RUN/base.sha"\n'
                  "{ cat bin/factory.d/lib.sh; echo; dc_block; echo; echo 'exit $((n_fail > 0))'; }"
                  ' > "$RUN/frozen/checks.sh"; chmod +x "$RUN/frozen/checks.sh"\n'
                  "round_zero; echo ROUND0-OK")
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**os.environ, "FACTORY_SOURCED": "1"}, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def lint_errors(self, checks: str) -> str:
        """stderr of the real check_not_grep_only, the lint rule that drops guards, over a done-checks block."""
        body = f"## Done checks\n\n```done-checks\n{checks}\n```\n"
        proc = subprocess.run(["bash", "-c", '. bin/factory; SRC=t; BODY=$1; check_not_grep_only', "_", body],
                              cwd=ROOT, env={**os.environ, "FACTORY_SOURCED": "1"}, capture_output=True, text=True,
                              check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stderr

    def test_check_mentioning_safeguard_is_not_a_guard(self) -> None:
        out = self.round_zero(
            'guard true && pass check || fail check "base is broken"\n'
            'grep -q safeguard README.md && pass doc-says-safeguard || fail doc-says-safeguard "no safeguard"')
        self.assertIn("FINISH ticket-defect: check doc-says-safeguard passes on", out)

    def test_check_prefixed_guard_is_a_guard(self) -> None:
        out = self.round_zero(
            'guard true && pass check || fail check "base is broken"\n'
            '  guard grep -q safeguard README.md && pass indented || fail indented "no safeguard"\n'
            'test -e NEW.md && pass new-file || fail new-file "NEW.md is missing"')
        self.assertEqual(out.strip(), "ROUND0-OK")

    def test_guard_continued_over_two_lines_is_a_guard(self) -> None:
        out = self.round_zero(
            'guard true \\\n'
            '  && pass check || fail check "base is broken"\n'
            'test -e NEW.md && pass new-file || fail new-file "NEW.md is missing"')
        self.assertEqual(out.strip(), "ROUND0-OK")

    def test_guard_called_in_a_capture_is_a_guard(self) -> None:
        out = self.round_zero(
            'out=$(guard cat README.md) ; grep -q safeguard <<<"$out" && pass package || fail package "x"\n'
            'test -e NEW.md && pass new-file || fail new-file "NEW.md is missing"')
        self.assertEqual(out.strip(), "ROUND0-OK")

    def test_guard_called_in_a_brace_group_is_a_guard(self) -> None:
        out = self.round_zero(
            '[ -n "${LOAM_HOOK:-}" ] && pass green || { guard true && pass green || fail green "x"; }\n'
            'test -e NEW.md && pass new-file || fail new-file "NEW.md is missing"')
        self.assertEqual(out.strip(), "ROUND0-OK")

    def test_guard_in_a_condition_after_a_keyword_is_a_guard(self) -> None:
        out = self.round_zero(
            'if guard true; then pass if-cond; else fail if-cond "x"; fi\n'
            'if false; then :; elif guard true; then pass elif-cond; fi\n'
            'while guard true; do pass while-cond; break; done\n'
            'until guard true; do :; done && pass until-cond || fail until-cond "x"\n'
            'test -e NEW.md && pass new-file || fail new-file "NEW.md is missing"')
        self.assertEqual(out.strip(), "ROUND0-OK")

    def test_guard_in_a_body_after_a_keyword_is_a_guard(self) -> None:
        out = self.round_zero(
            'if true; then guard true && pass then-arm || fail then-arm "x"; fi\n'
            'if false; then :; else guard true && pass else-arm || fail else-arm "x"; fi\n'
            'for i in 1; do guard true && pass do-body || fail do-body "x"; done\n'
            'test -e NEW.md && pass new-file || fail new-file "NEW.md is missing"')
        self.assertEqual(out.strip(), "ROUND0-OK")

    def test_word_ending_in_a_keyword_before_guard_is_not_a_guard(self) -> None:
        out = self.round_zero(
            'guard true && pass check || fail check "base is broken"\n'
            'grep -q safeguard README.md && pass readme || fail readme "redo guard first"')
        self.assertIn("FINISH ticket-defect: check readme passes on", out)

    def test_check_named_with_guard_is_not_a_guard(self) -> None:
        out = self.round_zero(
            'guard true && pass check || fail check "base is broken"\n'
            'grep -q safeguard README.md && pass env-guard || fail env-guard "no safeguard"')
        self.assertIn("FINISH ticket-defect: check env-guard passes on", out)

    def test_reason_naming_guard_is_not_a_guard(self) -> None:
        out = self.round_zero(
            'guard true && pass check || fail check "base is broken"\n'
            'grep -q safeguard README.md && pass readme || fail readme "README has no guard line"')
        self.assertIn("FINISH ticket-defect: check readme passes on", out)

    def test_reason_or_comment_holding_guard_after_a_separator_is_not_a_guard(self) -> None:
        for tail in ('fail readme "README lacks the word; guard the docs"', 'fail readme "see (guard rules)"',
                     'fail readme "x| guard y"', "fail readme 'x; guard y'", 'fail readme "x" # old; guard y'):
            with self.subTest(tail=tail):
                out = self.round_zero('guard true && pass check || fail check "base is broken"\n'
                                      f'grep -q safeguard README.md && pass readme || {tail}')
                self.assertIn("FINISH ticket-defect: check readme passes on", out)

    def test_guard_after_time_or_an_assignment_is_a_guard(self) -> None:
        out = self.round_zero(
            'time guard true && pass timed || fail timed "x"\n'
            'LOAM_HOOK= guard true && pass hook-off || fail hook-off "x"\n'
            'A=1 B="two words" guard true && pass two-vars || fail two-vars "x"\n'
            'test -e NEW.md && pass new-file || fail new-file "NEW.md is missing"')
        self.assertEqual(out.strip(), "ROUND0-OK")

    def test_guard_in_a_quoted_capture_is_a_guard(self) -> None:
        out = self.round_zero(
            'grep -q safeguard <<<"$(guard cat README.md)" && pass quoted || fail quoted "x"\n'
            'test -e NEW.md && pass new-file || fail new-file "NEW.md is missing"')
        self.assertEqual(out.strip(), "ROUND0-OK")

    def test_lint_reads_guards_as_round_zero_does(self) -> None:
        for checks in ('guard bin/check >/dev/null && pass g || fail g "x"\n'
                       'grep -q a README.md && pass a || fail a "README lacks the word; guard the docs"',
                       'time guard true && pass t || fail t "x"\n'
                       'grep -q a README.md && pass a || fail a "x"'):
            with self.subTest(checks=checks):
                self.assertIn("all 1 non-guard done-checks grep source text", self.lint_errors(checks))


if __name__ == "__main__":
    unittest.main()
