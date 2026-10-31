"""The loop keeps running worker rounds after a judge fail and opens the PR at the first judge pass.

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real main_loop runs: checks, grade_round, graders, run_judge,
run_review, call_json, and open_pr. Only worker_round, notify and alert are stubbed (alert, so finish's heartbeat pause
never reaches the host's real bin/alert); the worker stub makes one commit per round. A fake `claude` on PATH answers
the judge by its call number and the reviewer always clean, and logs each call; a fake `gh` records its arguments.
The worktree's origin is a local bare repository. No network.
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
TICKET = "## Goal and why\n\nMake the widget work.\n\n## Merge checklist\n\n- read the diff\n"
PR_URL = "https://github.com/acme/widget/pull/9"

# The rubric's first line names the role; the judge's reply is judge.<call number> in the run dir.
FAKE_CLAUDE = """#!/usr/bin/env python3
import json, pathlib, sys
run = pathlib.Path(%r)
role = sys.stdin.read().split("ROLE ", 1)[1].split()[0]
with (run / "claude-calls").open("a") as f:
    f.write(role + "\\n")
n = (run / "claude-calls").read_text().split().count(role)
reply = (run / ("%%s.%%d" %% (role, n))).read_text() if role == "judge" else json.dumps({"verdict": "merge", "findings": []})
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": reply}))
"""

FAKE_GH = """#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
with open(%r, "a") as f:
    f.write(json.dumps({"args": args}) + "\\n")
if args[:2] == ["pr", "view"]:
    sys.exit(1)
if args[:2] == ["pr", "create"]:
    print(%r)
if args[:2] == ["issue", "create"]:
    print("https://github.com/acme/widget/issues/10")
"""

JUDGE_PASS = {"verdict": "pass", "rows": {"widget": "pass"}, "evidence": {"widget": "ok"}, "fixes": [], "backlog": []}
JUDGE_FAIL = {"verdict": "fail", "rows": {"widget": "fail"}, "evidence": {}, "fixes": ["make the widget work"], "backlog": []}

LOOP = """notify() { :; }
alert() { :; }
worker_round() { echo "$1" >> "$RUN/worker-rounds"; git -C "$WORKTREE" -c user.name=t -c user.email=t@t commit -q --allow-empty -m "round $1"; }
( cd "$RUN/frozen" && sha256_of * > sha256 )
echo "GRADER_FAIL_ROUNDS=$GRADER_FAIL_ROUNDS" >&2
main_loop
"""


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


class VerifierFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        origin = self.top / "origin.git"
        git("init", "-q", "--bare", str(origin), cwd=self.top)
        self.wt = self.top / "wt"
        self.wt.mkdir()
        git("init", "-q", "-b", "main", cwd=self.wt)
        git("remote", "add", "origin", str(origin), cwd=self.wt)
        git("commit", "-q", "--allow-empty", "-m", "base", cwd=self.wt)
        base = git("rev-parse", "HEAD", cwd=self.wt)
        git("checkout", "-q", "-b", "factory/7", cwd=self.wt)
        self.run_dir = self.top / "run"
        frozen = self.run_dir / "frozen"
        frozen.mkdir(parents=True)
        (frozen / "issue.md").write_text("# Widget works\n")
        (frozen / "judge.md").write_text("ROLE judge\n")
        (frozen / "reviewer.md").write_text("ROLE reviewer\n")
        (frozen / "checks.sh").write_text("#!/bin/sh\necho 'PASS widget'\necho CHECKS-END\n")
        (frozen / "checks.sh").chmod(0o755)
        for name in ("judge.schema.json", "reviewer.schema.json", "role-settings.json"):
            (frozen / name).write_text("{}")
        for name in ("protected.txt", "exempt.txt"):
            (frozen / name).write_text("")
        (self.run_dir / "base.sha").write_text(base + "\n")
        (self.run_dir / "round-0.checks").write_text("FAIL widget: not yet\nCHECKS-END\n")
        self.gh_log = self.top / "gh-calls.jsonl"
        self.bin = self.top / "bin"
        self.bin.mkdir()
        for name, text in (("claude", FAKE_CLAUDE % str(self.run_dir)), ("gh", FAKE_GH % (str(self.gh_log), PR_URL))):
            (self.bin / name).write_text(text)
            (self.bin / name).chmod(0o755)

    def run_loop(self, judges: list[dict]) -> str:
        """Run the real main_loop; judges[k] is the judge's reply on call k+1. Return the loop's stderr."""
        for k, reply in enumerate(judges, start=1):
            (self.run_dir / f"judge.{k}").write_text(json.dumps(reply))
        script = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; BRANCH=factory/7; ISSUE=7; KEY=7; IS_FILE=0; MAX_ROUNDS={len(judges)}\n"
            'LEDGER="$RUN/ledger.jsonl"; DAILY="$RUN/daily.jsonl"; DECISIONS="$RUN/decisions.md"; LOG="$RUN/factory.log"\n'
            'touch "$LEDGER" "$DAILY" "$DECISIONS"; date -u +%s > "$RUN/launched"; date -u +%s > "$RUN/started"\n'
            'BODY="$TICKET"; CODEX_REVIEW=no\n'
            + LOOP
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED}
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                                   "FACTORY_RUNS_ROOT": str(self.top / "runs"), "REPO": "acme/widget",
                                   "TICKET": TICKET, "PATH": f"{self.bin}:{env['PATH']}"},
                              capture_output=True, text=True, check=False)
        return proc.stderr

    def counts(self) -> tuple[int, int]:
        """(worker rounds, judge calls) the run made."""
        rounds = self.run_dir / "worker-rounds"
        calls = self.run_dir / "claude-calls"
        return (len(rounds.read_text().split()) if rounds.exists() else 0,
                calls.read_text().split().count("judge") if calls.exists() else 0)

    def pr_creates(self) -> list[list[str]]:
        calls = [json.loads(x) for x in self.gh_log.read_text().splitlines()] if self.gh_log.exists() else []
        return [c["args"] for c in calls if c["args"][:2] == ["pr", "create"]]

    def test_a_judge_that_fails_then_passes_opens_a_ready_pr_after_the_second_round(self) -> None:
        # A third reply would pass too, so a loop that ran past the pass would still find a judge to call.
        stderr = self.run_loop([JUDGE_FAIL, JUDGE_PASS, JUDGE_PASS])
        self.assertIn(f"EXIT pr-opened (0): {PR_URL} after 2 rounds", stderr)
        self.assertEqual((self.run_dir / "status").read_text(), "pr-opened\n")
        self.assertEqual(self.counts(), (2, 2))
        self.assertEqual((self.run_dir / "round-1.fixes").read_text(), "- make the widget work\n")
        creates = self.pr_creates()
        self.assertEqual(len(creates), 1, creates)
        self.assertNotIn("--draft", creates[0])
        self.assertNotIn("Draft:", (self.run_dir / "pr-body.md").read_text())

    def test_a_judge_that_never_passes_drafts_the_pr_at_the_grader_round_cap(self) -> None:
        stderr = self.run_loop([JUDGE_FAIL] * 5)
        cap = int(stderr.split("GRADER_FAIL_ROUNDS=", 1)[1].split()[0])
        self.assertLess(cap, 5)
        self.assertIn(f"grader-round cap: {cap} grader-fail rounds", (self.run_dir / "factory.log").read_text())
        self.assertIn(f"EXIT pr-opened (0): {PR_URL} after {cap} rounds", stderr)
        self.assertEqual(self.counts(), (cap, cap))
        creates = self.pr_creates()
        self.assertEqual(len(creates), 1, creates)
        self.assertIn("--draft", creates[0])
        self.assertIn("Draft: opened at the grader-round cap; the judge failed widget.",
                      (self.run_dir / "pr-body.md").read_text())


if __name__ == "__main__":
    unittest.main()
