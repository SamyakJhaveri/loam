"""A worker call killed by CALL_TIMEOUT_SEC is charged its ceiling and the stop names its commits (#319).

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
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG")
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
        for name, text in (("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX)):
            (self.bin / name).write_text(text)
            (self.bin / name).chmod(0o755)

    def worker_round(self, kind: str, subject: str, stubs: str = "") -> subprocess.CompletedProcess[str]:
        """Round 1 of a `kind` worker whose ticket sets ROUND_BUDGET_USD=7; the fake commits `subject` if non-empty."""
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

    def test_killed_claude_round_is_charged_its_ceiling_and_the_stop_names_its_commit(self) -> None:
        proc = self.worker_round("claude", SUBJECT)
        self.assertEqual(git("log", "-1", "--format=%s", cwd=self.wt), SUBJECT)  # the fake did commit
        self.assert_stopped(proc)
        rows = self.ledger()
        self.assertEqual([(r["round"], r["role"]) for r in rows], [(1, "worker")])
        self.assertEqual(rows[0]["cost_usd"], 7, rows[0])  # the ticket's ROUND_BUDGET_USD, not the default 15
        self.assertEqual([r["cost_usd"] for r in self.daily()], [7])
        self.assertIn(SUBJECT, proc.stderr)
        self.assertNotIn("failed before doing work", proc.stderr)
        # The caps read the same number.
        spent = subprocess.run(["bash", "-c", f". bin/factory\nLEDGER='{self.run_dir}/ledger.jsonl'; ticket_spent"],
                               cwd=ROOT, env={**os.environ, "FACTORY_SOURCED": "1"},
                               capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(spent, "7")

    def test_killed_claude_round_with_no_commit_says_so(self) -> None:
        proc = self.worker_round("claude", "")
        self.assert_stopped(proc)
        self.assertEqual(self.ledger()[0]["cost_usd"], 7)
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
