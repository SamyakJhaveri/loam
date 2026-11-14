"""A worker call killed by CALL_TIMEOUT_SEC books a no-result row and the stop names its commits (#319).

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real worker_round runs with a fake `claude` or `codex` on PATH
that commits once in the worktree and then exits with no result event, as a call that `timeout` killed does. The
real record, assert_call_ok, and finish follow. A file ticket, so notify only logs. No network.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "REPO", "RUN", "LOG")
SUBJECT = "ticket 7: the fix"

# Both fakes commit in the worktree (the supervisor's cwd for the call), print a stream with no result event
# (claude) or no turn.completed event (codex), and exit 124 as a call that `timeout` killed does. An empty
# FAKE_SUBJECT skips the commit.
FAKE_CLAUDE = """#!/usr/bin/env bash
cat > /dev/null
# With FAKE_MECH set, only the first call writes a mechanism paragraph.
[ -z "${FAKE_MECH:-}" ] || [ -e "$FAKE_MECH.seen" ] || { echo first > "$FAKE_MECH"; touch "$FAKE_MECH.seen"; }
echo '{"type":"system","subtype":"init"}'
[ -z "${FAKE_SUBJECT:-}" ] || git -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$FAKE_SUBJECT"
exit 124
"""
FAKE_CODEX = """#!/usr/bin/env bash
for arg in "$@"; do [ "$arg" != mcp ] || { echo '[]'; exit 0; }; done
printf '%s\\n' "$@" > "$FAKE_ARGS"
echo '{"type":"thread.started"}'
[ -z "${FAKE_SUBJECT:-}" ] || git -c user.name=t -c user.email=t@t commit -q --allow-empty -m "$FAKE_SUBJECT"
exit 124
"""


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


class KilledRoundTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.wt = self.top / "wt"
        self.wt.mkdir()
        git("init", "-q", "-b", "factory/7", cwd=self.wt)
        git("commit", "-q", "--allow-empty", "-m", "base", cwd=self.wt)
        self.run_dir = self.top / "run"
        (self.run_dir / "frozen").mkdir(parents=True)
        (self.run_dir / "tasks").mkdir()
        for name in ("_common.md", "unattended.md"):
            (self.run_dir / "frozen" / name).write_text("")
        (self.run_dir / "frozen" / "worker-settings.json").write_text("{}")
        self.bin = self.top / "bin"
        self.bin.mkdir()
        (self.top / "codex-home").mkdir()  # the factory's own Codex login, which every Codex call needs
        (self.top / "codex-home" / "auth.json").write_text("{}\n")
        for name, text in (("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX)):
            (self.bin / name).write_text(text)
            (self.bin / name).chmod(0o755)

    def worker_round(self, kind: str, subject: str, stubs: str = "") -> subprocess.CompletedProcess[str]:
        """Round 1 of a `kind` worker whose old ticket names ROUND_BUDGET_USD=7, which is ignored; the fake commits `subject` if non-empty."""
        script = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; LOG=\"$RUN/factory.log\"; KEY=7; IS_FILE=1\n"
            'LEDGER="$RUN/ledger.jsonl"; DAILY="$RUN/daily.jsonl"; DECISIONS="$RUN/decisions.md"\n'
            'touch "$LEDGER" "$DAILY" "$DECISIONS"; date -u +%s > "$RUN/launched"\n'
            "BODY=$'## Worker\\n\\nROUND_BUDGET_USD=7\\n'; apply_caps\n"
            f"WORKER_KIND={kind}; CODEX_PATH='{self.bin}'\n{stubs}\n"
            "worker_round 1; echo returned:$?\n"
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED and not k.startswith("FACTORY_")}
        return subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                                   "FACTORY_CODEX_HOME": str(self.top / "codex-home"),
                                   "FACTORY_RUNS_ROOT": str(self.top / "runs"), "FAKE_SUBJECT": subject,
                                   "FAKE_ARGS": str(self.top / "codex-args"), "FAKE_MECH": str(self.run_dir / "mechanism.md"),
                                   "CLAUDE_CONFIG_DIR": str(self.top / "claude-config"),
                                   "PATH": f"{self.bin}:{env['PATH']}"},
                              capture_output=True, text=True, check=False)

    def ledger(self) -> list[dict]:
        return [json.loads(x) for x in (self.run_dir / "ledger.jsonl").read_text().splitlines()]

    def daily(self) -> list[dict]:
        return [json.loads(x) for x in (self.run_dir / "daily.jsonl").read_text().splitlines()]

    def assert_stopped(self, proc: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(proc.returncode, 4, proc.stderr)  # stopped-environment, from finish
        self.assertEqual((self.run_dir / "status").read_text().strip(), "stopped-environment")
        self.assertIn("no result event", proc.stderr)

    def test_killed_claude_round_books_a_no_result_row_and_the_stop_names_its_commit(self) -> None:
        proc = self.worker_round("claude", SUBJECT)
        self.assertEqual(git("log", "-1", "--format=%s", cwd=self.wt), SUBJECT)  # the fake did commit
        self.assert_stopped(proc)
        rows = self.ledger()
        # No cost was reported, so none is booked: no dollar ceiling exists to charge (13 Nov 2026).
        self.assertEqual([(r["round"], r["role"], r["subtype"], r["cost_usd"]) for r in rows], [(1, "worker", "no-result", 0)])
        self.assertEqual([r["cost_usd"] for r in self.daily()], [0])
        self.assertIn(SUBJECT, proc.stderr)
        self.assertNotIn("failed before doing work", proc.stderr)

    def test_each_killed_grader_attempt_books_a_no_result_row(self) -> None:
        # audit3 C1: a judge or reviewer call with no result (killed, or crashed) still gets a ledger row per attempt.
        (self.run_dir / "judge.schema.json").write_text("{}")
        (self.run_dir / "judge.prompt.md").write_text("grade it\n")
        proc = self.worker_round("claude", "", 'call_json 1 judge judge "$RUN/judge.prompt.md" "$RUN/judge.schema.json"; exit 0')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual([(r["role"], r["cost_usd"], r["subtype"]) for r in self.ledger()],
                         [("judge", 0, "no-result"), ("judge", 0, "no-result"), ("judge", 0, "no-result")])
        self.assertEqual([r["cost_usd"] for r in self.daily()], [0, 0, 0])

    def test_each_round_starts_with_its_header_in_decisions_md_once(self) -> None:
        # audit3 F2: parity P3 and the method-evidence checker give decisions.md lines after `Round N` to round N, so
        # the supervisor writes that line before the round's call; a relaunched round adds no second one. The round's
        # start sha, the checker's base, is kept from the first attempt, so a commit that attempt made stays in the round.
        (self.run_dir / "decisions.md").write_text("pstack: tdd | /p/skills/tdd/SKILL.md | x | y | z\n")
        start = git("rev-parse", "HEAD", cwd=self.wt)
        self.worker_round("claude", "first attempt")
        self.assertNotEqual(git("rev-parse", "HEAD", cwd=self.wt), start)  # the fake did commit
        self.worker_round("claude", "")
        self.assertEqual((self.run_dir / "decisions.md").read_text(),
                         "pstack: tdd | /p/skills/tdd/SKILL.md | x | y | z\nRound 1\n")
        self.assertEqual((self.run_dir / "round-1.start.sha").read_text().strip(), start)

    def test_a_round_after_a_method_evidence_fail_keeps_that_rounds_start(self) -> None:
        # audit F1: else round 2 could only write a method: line, commit nothing, and pass on an empty range.
        head = git("rev-parse", "HEAD", cwd=self.wt)
        # Round 1's verdict file: a FAIL, none (a dirty tree or do-not-touch round never ran the checker), a PASS.
        for verdict, want in (("FAIL method-evidence: no method\n", "0" * 40), (None, "0" * 40),
                              ("PASS method-evidence: ok\n", head)):
            with self.subTest(verdict=verdict):
                (self.run_dir / "round-2.start.sha").unlink(missing_ok=True)
                (self.run_dir / "round-1.method-evidence").unlink(missing_ok=True)
                if verdict:
                    (self.run_dir / "round-1.method-evidence").write_text(verdict)
                # The fake worker's call ends with no result, so the round stops; its start sha is written first.
                self.worker_round("claude", "", f"echo {'0' * 40} > \"$RUN/round-1.start.sha\"; worker_round 2")
                self.assertEqual((self.run_dir / "round-2.start.sha").read_text().strip(), want)

    def test_method_evidence_is_shadow_a_fail_or_a_fault_never_blocks_the_round(self) -> None:
        # Owner ruling of 12 Nov 2026: the check runs and records its line for one batch, but round-N.checks never
        # holds it, so it sends no worker back, and a checker fault does not stop the run.
        for verdict, code, want in (("FAIL method-evidence: no method", 1, "FAIL method-evidence: no method"),
                                    ("", 2, "ERROR method-evidence: the checker could not grade round 1 (exit 2)")):
            with self.subTest(code=code):
                (self.run_dir / "frozen" / "method_evidence.py").write_text(f"print({verdict!r})\nraise SystemExit({code})\n")
                for f in ("round-1.checks", "round-1.method-evidence"):
                    (self.run_dir / f).unlink(missing_ok=True)
                proc = self.worker_round("claude", "", "ROUND=1; do_not_touch_hits() { :; }; "
                                         "run_checks() { printf 'PASS x\\n\\nCHECKS-END\\n' > \"$2\"; }; "
                                         'round_checks "$RUN/round-1.checks"; echo checked; exit 0')
                self.assertIn("checked", proc.stdout, proc.stderr)
                self.assertEqual((self.run_dir / "round-1.checks").read_text(), "PASS x\n\nCHECKS-END\n")
                self.assertIn(want, (self.run_dir / "round-1.method-evidence").read_text())

    def test_the_round_header_starts_its_own_line_after_a_last_line_with_no_newline(self) -> None:
        # audit4 2: appended bare, the header joined the last decision (`...zRound 1`), which parity then never read
        # as a header, so the round's method lines went to the round before.
        (self.run_dir / "decisions.md").write_text("pstack: tdd | /p/skills/tdd/SKILL.md | x | y | z")
        self.worker_round("claude", "")
        self.assertEqual((self.run_dir / "decisions.md").read_text(),
                         "pstack: tdd | /p/skills/tdd/SKILL.md | x | y | z\nRound 1\n")

    def test_the_round_header_is_no_change_for_the_no_change_stop(self) -> None:
        # The supervisor's own `Round N` line must not make a round that changed nothing look changed.
        proc = self.worker_round("claude", "", 'a=$(round_sig); echo "Round 2" >> "$DECISIONS"; b=$(round_sig)\n'
                                 'echo "a worker line" >> "$DECISIONS"; c=$(round_sig)\n'
                                 '[ "$a" = "$b" ] && [ "$b" != "$c" ] && echo same-then-changed; exit 0')
        self.assertIn("same-then-changed", proc.stdout, proc.stderr)

    def test_killed_claude_round_with_no_commit_says_so(self) -> None:
        proc = self.worker_round("claude", "")
        self.assert_stopped(proc)
        self.assertEqual(self.ledger()[0]["cost_usd"], 0)
        self.assertIn("no commits", proc.stderr)

    def test_killed_codex_round_keeps_cost_null_and_names_its_commit(self) -> None:
        proc = self.worker_round("codex", SUBJECT)
        self.assert_stopped(proc)
        rows = self.ledger()
        self.assertEqual([(r["round"], r["role"], r["cost_usd"]) for r in rows], [(1, "worker", None)])
        self.assertIn(SUBJECT, proc.stderr)

    def test_codex_round_may_write_the_worker_files_and_drops_an_earlier_paragraph(self) -> None:
        # decisions.md and mechanism.md sit outside the worktree, so the sandbox must name their directory (#330),
        # and an earlier round's paragraph must not describe this round's diff.
        (self.run_dir / "mechanism.md").write_text("An earlier round's account.\n")
        self.worker_round("codex", SUBJECT)
        args = (self.top / "codex-args").read_text().splitlines()
        self.assertIn(["--add-dir", str(self.run_dir)], [args[i:i + 2] for i in range(len(args) - 1)])
        self.assertFalse((self.run_dir / "mechanism.md").exists())

    def test_a_retried_claude_call_drops_the_paragraph_its_first_call_wrote(self) -> None:
        # The first call writes a paragraph and hits a usage limit; the retry, in the same round, writes none (#330).
        proc = self.worker_round("claude", "", 'limit_wait() { [ ! -e "$RUN/waited" ] && touch "$RUN/waited"; }')
        self.assertTrue((self.run_dir / "waited").exists(), proc.stderr)
        self.assertTrue((self.run_dir / "mechanism.md.seen").exists(), proc.stderr)
        self.assertFalse((self.run_dir / "mechanism.md").exists())


if __name__ == "__main__":
    unittest.main()
