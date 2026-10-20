"""A reviewer or Codex review past its one block that still blocks, or replies with nothing parseable, opens a draft PR.

A Codex review with no parseable reply is called once more; two bad replies draft the PR but never reach a worker.

`bin/factory` is sourced (FACTORY_SOURCED=1) and two rounds run the loop's `graders "$ROUND" && open_pr` line with the
real graders, call_json, run_codex_review, open_pr, and file_backlog. Fake `claude`, `codex`, and `gh` scripts sit
on PATH: claude answers with the reply named in its prompt, codex logs its -o file and writes the reply for its call
number (or nothing), and gh records its arguments and body. The worktree's origin is a local bare repository. No network.
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

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, sys
reply = sys.stdin.read().rsplit("REPLY ", 1)[1].splitlines()[0]
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": reply}))
"""

FAKE_CODEX = """#!/usr/bin/env python3
import pathlib, sys
out = pathlib.Path(sys.argv[sys.argv.index("-o") + 1])
calls = out.parent / "codex-calls"
with calls.open("a") as f:
    f.write(out.name + "\\n")
reply = out.parent / ("codex-reply.%d" % len(calls.read_text().splitlines()))
if reply.exists():
    out.write_text(reply.read_text())
"""

FAKE_GH = """#!/usr/bin/env python3
import json, sys
args = sys.argv[1:]
rec = {"args": args}
if "--body-file" in args:
    p = args[args.index("--body-file") + 1]
    rec["body"] = sys.stdin.read() if p == "-" else open(p).read()
with open(%r, "a") as f:
    f.write(json.dumps(rec) + "\\n")
if args[:2] == ["pr", "view"]:
    sys.exit(1)
if args[:2] == ["pr", "create"]:
    print(%r)
if args[:2] == ["issue", "create"]:
    print("https://github.com/acme/widget/issues/10")
"""

JUDGE_PASS = {"verdict": "pass", "rows": {"widget": "pass"}, "evidence": {"widget": "ok"}, "fixes": [], "backlog": []}
CLEAN_REVIEW = {"verdict": "merge", "findings": []}
CLEAN_CODEX = {"verdict": "approve", "summary": "looks fine", "findings": [], "next_steps": []}


def review_finding(severity: str, defect: str) -> dict[str, object]:
    return {"severity": severity, "file": "bin/x", "line": 3, "defect": defect, "fix": "f"}


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


class CappedReviewTests(unittest.TestCase):
    def new_run(self) -> None:
        """A fresh worktree, bare origin, run directory, and fake bin for one subtest."""
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
        git("commit", "-q", "--allow-empty", "-m", "ticket 7: the fix", cwd=self.wt)
        self.run_dir = self.top / "run"
        frozen = self.run_dir / "frozen"
        frozen.mkdir(parents=True)
        (frozen / "issue.md").write_text("# Widget works\n")
        (frozen / "codex-review.prompt.md").write_text("Review the diff against <base>.\n")
        for name in ("judge.schema.json", "reviewer.schema.json", "review-output.schema.json", "role-settings.json"):
            (frozen / name).write_text("{}")
        (self.run_dir / "base.sha").write_text(base + "\n")
        (self.run_dir / "decisions.md").write_text("- kept it small\n")
        self.gh_log = self.top / "gh-calls.jsonl"
        self.bin = self.top / "bin"
        self.bin.mkdir()
        for name, text in (("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX), ("gh", FAKE_GH % (str(self.gh_log), PR_URL))):
            (self.bin / name).write_text(text)
            (self.bin / name).chmod(0o755)

    def run_loop(self, reviews: list[object], codex: list[str | None] | None = None) -> tuple[str, list[dict]]:
        """Run rounds 1 and 2 of `graders "$ROUND" && open_pr`; return the loop's stderr and the gh calls.

        reviews[k] is the reviewer's reply in round k+1 (a string goes verbatim, anything else as JSON).
        codex, when given, turns the Codex review on: codex[k] is the -o file text of Codex call k+1, None for no file.
        """
        for k, reply in enumerate(reviews, start=1):
            (self.run_dir / f"reply.judge.{k}").write_text(json.dumps(JUDGE_PASS))
            (self.run_dir / f"reply.reviewer.{k}").write_text(reply if isinstance(reply, str) else json.dumps(reply))
        for k, text in enumerate(codex or [], start=1):
            if text is not None:
                (self.run_dir / f"codex-reply.{k}").write_text(text)
        script = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; BRANCH=factory/7; ISSUE=7; KEY=7; IS_FILE=0\n"
            'LEDGER="$RUN/ledger.jsonl"; DAILY="$RUN/daily.jsonl"; DECISIONS="$RUN/decisions.md"; LOG="$RUN/factory.log"\n'
            'touch "$LEDGER" "$DAILY"; date -u +%s > "$RUN/launched"; date -u +%s > "$RUN/started"\n'
            f"BODY=\"$TICKET\"; CODEX_REVIEW={'yes' if codex is not None else 'no'}; CODEX_PATH='{self.bin}'\n"
            "notify() { :; }\n"
            'build_evidence() { printf \'REPLY %s\\n\' "$(cat "$RUN/reply.$(basename "$1" .md).$ROUND")"; }\n'
            'for ROUND in 1 2; do graders "$ROUND" && open_pr; done\n'
            "echo 'no PR opened' >&2; exit 9\n"
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED}
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                                   "FACTORY_RUNS_ROOT": str(self.top / "runs"), "REPO": "acme/widget",
                                   "TICKET": TICKET, "PATH": f"{self.bin}:{env['PATH']}"},
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        calls = [json.loads(x) for x in self.gh_log.read_text().splitlines()] if self.gh_log.exists() else []
        return proc.stderr, calls

    def pr_create(self, calls: list[dict]) -> dict:
        creates = [c for c in calls if c["args"][:2] == ["pr", "create"]]
        self.assertEqual(len(creates), 1, calls)
        return creates[0]

    def issues(self, calls: list[dict]) -> list[dict]:
        return [c for c in calls if c["args"][:2] == ["issue", "create"]]

    def assert_draft_with_filed_finding(self, stderr: str, calls: list[dict], finding: str, rounds: int = 2) -> None:
        self.assertIn(f"EXIT pr-opened (0): {PR_URL} after {rounds} rounds", stderr)
        pr = self.pr_create(calls)
        self.assertIn("--draft", pr["args"])
        # The reason is the first line under `Closes #<issue>` (LOOP.md, step 8), and it names the finding.
        reason = pr["body"].split("\n\n", 2)[1]
        self.assertTrue(pr["body"].startswith("Closes #7\n\n"), pr["body"])
        self.assertTrue(reason.startswith("Draft: "), reason)
        self.assertIn(finding, reason)
        issues = self.issues(calls)
        self.assertEqual(len(issues), 1, calls)
        self.assertIn("needs-triage", issues[0]["args"])
        self.assertIn(finding, issues[0]["body"])
        self.assertIn(PR_URL, issues[0]["body"])

    def test_reviewer_past_its_one_block_opens_a_draft_and_files_the_finding(self) -> None:
        first_block = review_finding("high", "first defect")
        for name, second, finding in (
            ("unparseable", "this is not json", "reviewer output unparseable"),
            ("new-medium", {"verdict": "merge", "findings": [review_finding("medium", "second defect")]},
             "second defect"),
        ):
            with self.subTest(name):
                self.new_run()
                stderr, calls = self.run_loop([{"verdict": "fix", "findings": [first_block]}, second])
                self.assertIn("first defect", (self.run_dir / "round-1.fixes").read_text())
                self.assert_draft_with_filed_finding(stderr, calls, finding)

    def codex_fixes(self) -> list[str]:
        fixes = self.run_dir / "round-1.fixes"
        return [x for x in fixes.read_text().splitlines() if "codex" in x.lower()] if fixes.exists() else []

    def codex_calls(self) -> list[str]:
        return (self.run_dir / "codex-calls").read_text().splitlines()

    def test_a_codex_review_with_no_parseable_output_is_called_once_more(self) -> None:
        for name, text in (("missing", None), ("empty", ""), ("not-json", "this is not json")):
            with self.subTest(name):
                self.new_run()
                stderr, calls = self.run_loop([CLEAN_REVIEW, CLEAN_REVIEW], codex=[text, json.dumps(CLEAN_CODEX)])
                self.assertEqual(self.codex_fixes(), [])
                self.assertEqual(self.codex_calls(), ["round-1.codex-review.json"] * 2)
                self.assertIn(f"EXIT pr-opened (0): {PR_URL} after 1 rounds", stderr)
                self.assertNotIn("--draft", self.pr_create(calls)["args"])
                self.assertEqual(self.issues(calls), [])

    def test_two_unparseable_codex_reviews_open_a_draft_without_a_worker_round(self) -> None:
        for name, text in (("missing", None), ("empty", ""), ("not-json", "this is not json")):
            with self.subTest(name):
                self.new_run()
                stderr, calls = self.run_loop([CLEAN_REVIEW, CLEAN_REVIEW], codex=[text, text])
                # The finding is kept for the draft and the issue, but a worker cannot rerun Codex, so it gets nothing.
                self.assertEqual(self.codex_fixes(), [])
                self.assertEqual(self.codex_calls(), ["round-1.codex-review.json"] * 2)
                self.assert_draft_with_filed_finding(stderr, calls, "codex review output unparseable", rounds=1)

    def test_a_multi_paragraph_finding_files_one_issue_with_the_whole_finding(self) -> None:
        codex = json.dumps({"verdict": "needs-attention", "summary": "s", "next_steps": [], "findings": [
            {"severity": "high", "file": "bin/x", "line_start": 3, "line_end": 3, "confidence": 0.9, "title": "t",
             "body": "first para\n\nsecond para", "recommendation": "r1\nr2"}]})
        for name, reviews, codex_replies, finding in (
            ("reviewer", [{"verdict": "fix", "findings": [review_finding("high", "first defect")]},
                          {"verdict": "merge", "findings": [review_finding("medium", "second\n\nIt spans\n  two.")]}],
             None, "reviewer [medium] bin/x:3 second It spans two. Fix: f"),
            ("codex", [CLEAN_REVIEW, CLEAN_REVIEW], [codex, codex],
             "Codex review [high] bin/x:3 t: first para second para Fix: r1 r2"),
        ):
            with self.subTest(name):
                self.new_run()
                stderr, calls = self.run_loop(reviews, codex=codex_replies)
                self.assert_draft_with_filed_finding(stderr, calls, finding)
                self.assertIn("but 1 blocking", self.pr_create(calls)["body"])
                args = self.issues(calls)[0]["args"]
                self.assertEqual(args[args.index("--title") + 1], finding[:80])

    def test_clean_reviewer_and_clean_codex_open_a_ready_pr_and_file_nothing(self) -> None:
        for name, codex in (("reviewer only", None), ("with codex", [json.dumps(CLEAN_CODEX)] * 2)):
            with self.subTest(name):
                self.new_run()
                stderr, calls = self.run_loop([CLEAN_REVIEW, CLEAN_REVIEW], codex=codex)
                self.assertIn(f"EXIT pr-opened (0): {PR_URL} after 1 rounds", stderr)
                pr = self.pr_create(calls)
                self.assertNotIn("--draft", pr["args"])
                self.assertNotIn("Draft:", pr["body"])
                self.assertEqual(self.issues(calls), [])


if __name__ == "__main__":
    unittest.main()
