"""A reviewer or Codex review past its one block that still blocks, or replies with nothing parseable, opens a draft PR.
The Codex review runs beside the judge and the reviewer, which run one after the other, and ends with the run.

A Codex review with no parseable reply is called once more; two bad replies draft the PR but never reach a worker.
A judge or reviewer with no parseable reply after its three calls never reaches a worker either (#312): the
reviewer's finding drafts the PR without spending its one block, and the judge's opens the draft at once.

`bin/factory` is sourced (FACTORY_SOURCED=1) and two rounds run the loop's `graders "$ROUND" && open_pr` line with the
real graders, call_json, run_codex_review, open_pr, and file_backlog. Fake `claude`, `codex`, and `gh` scripts sit
on PATH: claude answers with the reply named in its prompt, codex logs its -o file and writes the reply for its call
number (or nothing), and gh records its arguments and body. The worktree's origin is a local bare repository. No network.
"""

from __future__ import annotations

import json
import os
import pathlib
import signal
import subprocess
import tempfile
import time
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG")
TICKET = "## Goal and why\n\nMake the widget work.\n\n## Merge checklist\n\n- read the diff\n"
PR_URL = "https://github.com/acme/widget/pull/9"

# FAKE_SPANS names a file each fake call appends "<who> <start> <end>" to after sleeping FAKE_SLEEP (claude) or
# FAKE_CODEX_SLEEP (codex) seconds, 3 by default; it first creates FAKE_SPANS.<who>.ready, once its session exists.
# A reply of STOP writes FACTORY_STOP into the run dir 1 s in, then answers with text that is not JSON, so the grader
# calls again. A Claude call waits first for the file FAKE_WAIT_FOR names, when set.
SPAN = """
start = time.time()
if os.environ.get("FAKE_SPANS"):
    open(os.environ["FAKE_SPANS"] + "." + WHO + ".ready", "w").close()
    time.sleep(float(os.environ.get(SLEEP, "3")))
    with open(os.environ["FAKE_SPANS"], "a") as f:
        f.write("%s %f %f\\n" % (WHO, start, time.time()))
"""

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, os, sys, time
prompt = sys.stdin.read()
reply = prompt.rsplit("REPLY ", 1)[1].splitlines()[0]
WHO, SLEEP = prompt.split("ROLE ", 1)[1].split()[0], "FAKE_SLEEP"
if reply == "STOP":
    time.sleep(1)
    open(os.path.join(os.environ["FAKE_RUN"], "FACTORY_STOP"), "w").close()
    reply = "not json"
while os.environ.get("FAKE_WAIT_FOR") and not os.path.exists(os.environ["FAKE_WAIT_FOR"]):
    time.sleep(0.05)
""" + SPAN + """print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": reply}))
"""

FAKE_CODEX = """#!/usr/bin/env python3
import os, pathlib, sys, time
WHO, SLEEP = "codex", "FAKE_CODEX_SLEEP"
""" + SPAN + """out = pathlib.Path(sys.argv[sys.argv.index("-o") + 1])
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
JUDGE_FAIL = {"verdict": "fail", "rows": {"widget": "fail"}, "evidence": {}, "fixes": ["make the widget work"], "backlog": []}
# An empty result is what a reply with no text looks like to call_json; the other is text that is not JSON.
UNPARSEABLE = (("missing", ""), ("not-json", "this is not json"))
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
        self.addCleanup(subprocess.run, ["pkill", "-f", str(self.top)], check=False)
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

    def run_loop(self, reviews: list[object], codex: list[str | None] | None = None,
                 judges: list[object] | None = None, env_extra: dict[str, str] | None = None,
                 status: int = 0, inject: str = "") -> tuple[str, list[dict]]:
        """Run one round per reply of `graders "$ROUND" && open_pr`; return the loop's stderr and the gh calls."""
        proc = subprocess.run(**self.loop_cmd(reviews, codex, judges, env_extra, inject), capture_output=True, check=False)
        self.assertEqual(proc.returncode, status, proc.stderr)
        calls = [json.loads(x) for x in self.gh_log.read_text().splitlines()] if self.gh_log.exists() else []
        return proc.stderr, calls

    def loop_cmd(self, reviews: list[object], codex: list[str | None] | None = None,
                 judges: list[object] | None = None, env_extra: dict[str, str] | None = None,
                 inject: str = "") -> dict:
        """subprocess arguments for run_loop's loop; `inject` is shell run after bin/factory is sourced.

        reviews[k] is the reviewer's reply in round k+1 (a string goes verbatim, anything else as JSON).
        judges[k], when given, is the judge's reply in round k+1 the same way; the judge passes otherwise.
        codex, when given, turns the Codex review on: codex[k] is the -o file text of Codex call k+1, None for no file.
        """
        for k, reply in enumerate(reviews, start=1):
            judge = judges[k - 1] if judges else JUDGE_PASS
            (self.run_dir / f"reply.judge.{k}").write_text(judge if isinstance(judge, str) else json.dumps(judge))
            (self.run_dir / f"reply.reviewer.{k}").write_text(reply if isinstance(reply, str) else json.dumps(reply))
        for k, text in enumerate(codex or [], start=1):
            if text is not None:
                (self.run_dir / f"codex-reply.{k}").write_text(text)
        script = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; BRANCH=factory/7; ISSUE=7; KEY=7; IS_FILE=0\n"
            'LEDGER="$RUN/ledger.jsonl"; DAILY="$RUN/daily.jsonl"; DECISIONS="$RUN/decisions.md"; LOG="$RUN/factory.log"\n'
            'touch "$LEDGER" "$DAILY"; date -u +%s > "$RUN/launched"; date -u +%s > "$RUN/started"\n'
            f"BODY=\"$TICKET\"; CODEX_REVIEW={'yes' if codex is not None else 'no'}; CODEX_PATH='{self.bin}'\n"
            "notify() { :; }; alert() { :; }\n" + inject +
            'build_evidence() { printf \'ROLE %s\\nREPLY %s\\n\' "$(basename "$1" .md)" "$(cat "$RUN/reply.$(basename "$1" .md).$ROUND")"; }\n'
            f'for ROUND in $(seq 1 {len(reviews)}); do graders "$ROUND" && open_pr; done\n'
            "echo 'no PR opened' >&2; exit 9\n"
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED}
        return {"args": ["bash", "-c", f". bin/factory\n{script}"], "cwd": ROOT, "text": True,
                "env": {**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT),
                        "FACTORY_RUNS_ROOT": str(self.top / "runs"), "REPO": "acme/widget",
                        "TICKET": TICKET, "PATH": f"{self.bin}:{env['PATH']}",
                        "FAKE_RUN": str(self.run_dir), **(env_extra or {})}}

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

    def run_clean(self) -> str:
        """The run's `bin/factory status` clean column."""
        env = {k: v for k, v in os.environ.items() if k not in INHERITED}
        return subprocess.run(["bash", "-c", f". bin/factory\nrun_clean '{self.run_dir}'"], cwd=ROOT,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT)},
                              capture_output=True, text=True, check=True).stdout

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
                self.assertEqual(self.run_clean(), "yes")

    def test_two_unparseable_codex_reviews_open_a_draft_without_a_worker_round(self) -> None:
        for name, text in (("missing", None), ("empty", ""), ("not-json", "this is not json")):
            with self.subTest(name):
                self.new_run()
                stderr, calls = self.run_loop([CLEAN_REVIEW, CLEAN_REVIEW], codex=[text, text])
                # The finding is kept for the draft and the issue, but a worker cannot rerun Codex, so it gets nothing.
                self.assertEqual(self.codex_fixes(), [])
                self.assertEqual(self.codex_calls(), ["round-1.codex-review.json"] * 2)
                self.assert_draft_with_filed_finding(stderr, calls, "codex review output unparseable", rounds=1)
                # Each bad call's log line points at its own stream, and a run whose Codex review never ran is not clean.
                log = (self.run_dir / "factory.log").read_text()
                for call in (1, 2):
                    self.assertIn(f"on call {call} of 2; see {self.run_dir}/round-1.codex-review.{call}.jsonl", log)
                self.assertEqual(self.run_clean(), "no")

    def fixes(self, round_: int) -> str:
        f = self.run_dir / f"round-{round_}.fixes"
        return f.read_text() if f.exists() else ""

    def test_an_unparseable_reviewer_drafts_the_pr_and_is_not_sent_to_the_worker(self) -> None:
        for name, text in UNPARSEABLE:
            with self.subTest(name):
                self.new_run()
                stderr, calls = self.run_loop([text])
                # The finding is kept for the draft and the issue, but a worker cannot rerun the reviewer, so it gets nothing.
                self.assertEqual(self.fixes(1), "")
                review = json.loads((self.run_dir / "round-1.review.json").read_text())
                self.assertIs(review["unparseable"], True)
                self.assertEqual([f["severity"] for f in review["findings"]], ["high"])
                self.assert_draft_with_filed_finding(stderr, calls, "reviewer output unparseable", rounds=1)
                self.assertEqual(self.run_clean(), "no")

    def test_an_unparseable_reviewer_does_not_spend_its_one_block(self) -> None:
        for name, text in UNPARSEABLE:
            with self.subTest(name):
                self.new_run()
                # Round 1: the judge fails and the reviewer is unparseable. Round 2: the reviewer's first real block.
                # Round 3: clean, so the PR is ready.
                stderr, calls = self.run_loop(
                    [text, {"verdict": "fix", "findings": [review_finding("high", "real defect")]}, CLEAN_REVIEW],
                    judges=[JUDGE_FAIL, JUDGE_PASS, JUDGE_PASS])
                self.assertEqual(self.fixes(1), "- make the widget work\n")
                self.assertIn("real defect", self.fixes(2))
                self.assertIn(f"EXIT pr-opened (0): {PR_URL} after 3 rounds", stderr)
                self.assertNotIn("--draft", self.pr_create(calls)["args"])
                self.assertEqual(self.issues(calls), [])

    def test_an_unparseable_judge_opens_a_draft_without_a_worker_round(self) -> None:
        for name, text in UNPARSEABLE:
            with self.subTest(name):
                self.new_run()
                stderr, calls = self.run_loop([CLEAN_REVIEW], judges=[text])
                # Not a pass: the PR is a draft, and nothing is queued for a worker, who cannot rerun the judge.
                self.assertEqual(self.fixes(1), "")
                self.assertEqual((self.run_dir / "status").read_text(), "pr-opened\n")
                self.assertIn(f"EXIT pr-opened (0): {PR_URL} after 1 rounds", stderr)
                pr = self.pr_create(calls)
                self.assertIn("--draft", pr["args"])
                reason = pr["body"].split("\n\n", 2)[1]
                self.assertTrue(reason.startswith("Draft: "), reason)
                self.assertIn("judge output unparseable", reason)
                self.assertIn("- judge output unparseable", pr["body"].split("## Backlog", 1)[1])
                issues = self.issues(calls)
                self.assertEqual(len(issues), 1, calls)
                self.assertIn("needs-triage", issues[0]["args"])
                self.assertIn("judge output unparseable", issues[0]["body"])
                self.assertIn(PR_URL, issues[0]["body"])
                self.assertEqual(self.run_clean(), "no")

    def test_an_unparseable_judge_with_reviewer_fixes_queued_takes_a_worker_round(self) -> None:
        for name, text in UNPARSEABLE:
            with self.subTest(name):
                self.new_run()
                # Round 1: the judge is unparseable and the reviewer blocks for the first time with a real finding.
                # That finding is a fix for the worker, so the round is a normal fail, not a draft; round 2 passes.
                stderr, calls = self.run_loop(
                    [{"verdict": "fix", "findings": [review_finding("high", "real defect")]}, CLEAN_REVIEW],
                    judges=[text, JUDGE_PASS])
                self.assertIn("real defect", self.fixes(1))
                self.assertNotIn("rerun", self.fixes(1))
                self.assertIn(f"EXIT pr-opened (0): {PR_URL} after 2 rounds", stderr)
                self.assertNotIn("--draft", self.pr_create(calls)["args"])
                self.assertEqual(self.issues(calls), [])

    def test_a_parseable_judge_fail_still_sends_its_fixes_to_the_worker(self) -> None:
        self.new_run()
        stderr, calls = self.run_loop([CLEAN_REVIEW, CLEAN_REVIEW], judges=[JUDGE_FAIL, JUDGE_PASS])
        self.assertEqual(self.fixes(1), "- make the widget work\n")
        self.assertIn(f"EXIT pr-opened (0): {PR_URL} after 2 rounds", stderr)
        self.assertNotIn("--draft", self.pr_create(calls)["args"])
        self.assertEqual(self.issues(calls), [])
        self.assertEqual(self.run_clean(), "no")

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

    def assert_codex_gone(self, calls: list[str] | None = None, zombie: int = 0) -> None:
        """Within 15 s no fake call or job (but an unreaped `zombie`) is left, and no call file but `calls`."""
        deadline = time.time() + 15
        while True:
            left = subprocess.run(["pgrep", "-f", str(self.top)], capture_output=True, text=True, check=False).stdout
            left = "".join(x + "\n" for x in left.split() if x != str(zombie))
            if not left or time.time() > deadline:
                break
            time.sleep(0.2)
        self.assertEqual(left, "", "a fake call outlived the supervisor")
        self.assertEqual(sorted(x.name for x in self.run_dir.glob("call*")), calls or [])

    def test_the_codex_review_runs_beside_the_judge_and_the_reviewer(self) -> None:
        # The Codex review only reads the tree, so its call overlaps both Claude graders, which still run one after
        # the other. Each fake call takes 3 s, the Codex one 6 s, so a slow runner still shows the overlap.
        self.new_run()
        spans_file = self.top / "spans"
        stderr, _ = self.run_loop([CLEAN_REVIEW], codex=[json.dumps(CLEAN_CODEX)],
                                  env_extra={"FAKE_SPANS": str(spans_file), "FAKE_CODEX_SLEEP": "6"})
        self.assertIn(f"EXIT pr-opened (0): {PR_URL} after 1 rounds", stderr)
        spans = {who: (float(a), float(b)) for who, a, b in (x.split() for x in spans_file.read_text().splitlines())}
        self.assertEqual(sorted(spans), ["codex", "judge", "reviewer"])
        self.assertLessEqual(spans["judge"][1], spans["reviewer"][0], spans)
        self.assertLess(spans["codex"][0], spans["judge"][1], spans)
        self.assertGreater(spans["codex"][1], spans["reviewer"][0], spans)

    def test_a_stop_the_reviewer_asks_for_ends_the_codex_review_running_beside_it(self) -> None:
        # The reviewer's first reply writes FACTORY_STOP, so its second call stops the run while the Codex review's
        # 60 s call still runs: the supervisor ends that call and exits at once, and grades nothing.
        self.new_run()
        started = time.time()
        stderr, calls = self.run_loop(["STOP"], codex=[json.dumps(CLEAN_CODEX)], status=2,
                                      env_extra={"FAKE_SPANS": str(self.top / "spans"), "FAKE_SLEEP": "0",
                                                 "FAKE_CODEX_SLEEP": "60"})
        self.assertLess(time.time() - started, 30)
        self.assertEqual(calls, [])
        self.assertEqual((self.run_dir / "status").read_text(), "stopped\n")
        self.assertFalse((self.run_dir / "round-1.graded.sha").exists())
        log = (self.run_dir / "factory.log").read_text()
        self.assertIn("judge verdict: pass", log)
        self.assertNotIn("codex review verdict", log)
        self.assertRegex(log.splitlines()[-1], "EXIT stopped \\(2\\): FACTORY_STOP before the reviewer call$")
        self.assert_codex_gone()

    def start_graders(self) -> subprocess.Popen:
        """The loop in a session of its own, once the judge's call and the Codex review's call both run."""
        self.new_run()
        proc = subprocess.Popen(**self.loop_cmd([CLEAN_REVIEW], codex=[json.dumps(CLEAN_CODEX)], env_extra={
            "FAKE_SPANS": str(self.top / "spans"), "FAKE_SLEEP": "60", "FAKE_CODEX_SLEEP": "60"}),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(lambda: proc.poll() is None and proc.kill() or proc.wait())
        ready = [self.run_dir / "call", self.run_dir / "call-codex-review", self.run_dir / "round-1.watch.codex-review",
                 self.top / "spans.judge.ready", self.top / "spans.codex.ready"]
        deadline = time.time() + 20
        while not all(f.exists() for f in ready):
            self.assertLess(time.time(), deadline, [f.name for f in ready if not f.exists()])
            time.sleep(0.1)
        return proc

    def test_term_to_the_supervisor_ends_the_codex_review(self) -> None:
        # TERM to the supervisor alone, while the judge's call and the Codex review's call both run, ends both.
        proc = self.start_graders()
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=30), 143)
        self.assert_codex_gone()

    def test_term_as_the_judge_call_ends_still_ends_the_codex_review(self) -> None:
        # TERM lands on the first trap change after the judge's call is reaped, while the Codex review runs: the
        # supervisor must never be left with TERM's default action there, or it dies and leaves the job running.
        self.new_run()
        inject = ('trap() { builtin trap "$@"; if [ -n "$CODEX_JOB" ] && [ -z "${INJECTED:-}" ] '
                  '&& [[ " ${FUNCNAME[*]} " == *" call_end "* ]]; then INJECTED=1; builtin kill -TERM $$; fi; }\n')
        self.run_loop([CLEAN_REVIEW], codex=[json.dumps(CLEAN_CODEX)], status=143, inject=inject,
                      env_extra={"FAKE_SPANS": str(self.top / "spans"), "FAKE_SLEEP": "0", "FAKE_CODEX_SLEEP": "60",
                                 "FAKE_WAIT_FOR": str(self.top / "spans.codex.ready")})
        self.assertIn("ending the Codex review", (self.run_dir / "factory.log").read_text())
        self.assert_codex_gone()

    def test_term_while_the_supervisor_ends_the_codex_review_is_held_until_it_is_reaped(self) -> None:
        # The reviewer's FACTORY_STOP finishes the run; TERM lands as finish signals the Codex review. The supervisor
        # keeps the job's pid and holds the signal until the job is reaped, then exits as finish decided.
        self.new_run()
        inject = ('kill() { if [ "${FUNCNAME[1]:-}" = codex_job_end ] && [ -z "${INJECTED:-}" ]; then INJECTED=1; '
                  'builtin kill -TERM $$; fi; builtin kill "$@"; }\n')
        self.run_loop(["STOP"], codex=[json.dumps(CLEAN_CODEX)], status=2, inject=inject,
                      env_extra={"FAKE_SPANS": str(self.top / "spans"), "FAKE_SLEEP": "0", "FAKE_CODEX_SLEEP": "60",
                                 "FAKE_WAIT_FOR": str(self.top / "spans.codex.ready")})
        self.assertEqual((self.run_dir / "status").read_text(), "stopped\n")
        log = (self.run_dir / "factory.log").read_text()
        self.assertIn("the supervisor ended the codex-review job", log)
        self.assertNotIn("the supervisor got TERM during a model call", log)
        self.assert_codex_gone()

    def assert_sigkill_leaves_no_codex_review(self, group: bool, reap: bool) -> None:
        # Nothing traps SIGKILL, so a watcher in a session of its own ends the Codex review's call once the supervisor
        # is gone. The judge's call has a session of its own and outlives the supervisor by design (holds_slot); the
        # test ends it, and its call file stays for holds_slot to judge.
        proc = self.start_graders()
        os.killpg(proc.pid, signal.SIGKILL) if group else proc.kill()
        if reap:
            proc.wait(timeout=10)
        os.killpg(int((self.run_dir / "call").read_text().split()[0]), signal.SIGKILL)
        self.assert_codex_gone(["call"], zombie=0 if reap else proc.pid)
        self.assertIn("the supervisor is gone; ending the Codex review", (self.run_dir / "factory.log").read_text())

    def test_a_sigkilled_supervisor_leaves_no_codex_review_running(self) -> None:
        self.assert_sigkill_leaves_no_codex_review(group=False, reap=True)

    def test_a_sigkilled_supervisor_not_yet_reaped_leaves_no_codex_review_running(self) -> None:
        # Its parent has not waited for it, so it is a zombie, which kill -0 still finds.
        self.assert_sigkill_leaves_no_codex_review(group=False, reap=False)

    def test_a_sigkilled_supervisor_process_group_leaves_no_codex_review_running(self) -> None:
        # The job shell dies with the supervisor's group, but the Codex call has a session of its own.
        self.assert_sigkill_leaves_no_codex_review(group=True, reap=True)

    def test_no_codex_call_runs_before_its_watcher_has_a_session_of_its_own(self) -> None:
        # The watcher's session start is delayed 5 s; a kill of the supervisor's process group 3 s into that gap
        # takes the job and the watcher with it, so a Codex call made meanwhile would run on unwatched.
        self.new_run()
        inject = ('eval "orig_$(declare -f exec_in_session)"\n'
                  'exec_in_session() { if [ "$1" = "$BASH" ]; then : > "$RUN/watch-delayed"; sleep 5; fi; '
                  'orig_exec_in_session "$@"; }\n')
        proc = subprocess.Popen(**self.loop_cmd([CLEAN_REVIEW], codex=[json.dumps(CLEAN_CODEX)], inject=inject,
                                                env_extra={"FAKE_SPANS": str(self.top / "spans"), "FAKE_SLEEP": "60",
                                                           "FAKE_CODEX_SLEEP": "60"}),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.addCleanup(lambda: proc.poll() is None and proc.kill() or proc.wait())
        deadline = time.time() + 20
        while not all(f.exists() for f in (self.run_dir / "watch-delayed", self.top / "spans.judge.ready")):
            self.assertLess(time.time(), deadline)
            time.sleep(0.1)
        codex_ready = self.top / "spans.codex.ready"
        deadline = time.time() + 3
        while not codex_ready.exists() and time.time() < deadline:
            time.sleep(0.1)
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=10)
        os.killpg(int((self.run_dir / "call").read_text().split()[0]), signal.SIGKILL)
        self.assertFalse(codex_ready.exists(), "the Codex call started before its watcher had a session of its own")
        self.assert_codex_gone(["call"])

    def test_a_watcher_that_never_starts_stops_the_run_without_a_codex_call(self) -> None:
        self.new_run()
        inject = ('eval "orig_$(declare -f exec_in_session)"\n'
                  'exec_in_session() { [ "$1" != "$BASH" ] || sleep 60; orig_exec_in_session "$@"; }\n')
        stderr, calls = self.run_loop([CLEAN_REVIEW], codex=[json.dumps(CLEAN_CODEX)], status=4, inject=inject)
        self.assertIn("did not start in a session of its own within 10 s", stderr)
        self.assertEqual(calls, [])
        self.assertFalse((self.run_dir / "codex-calls").exists())


if __name__ == "__main__":
    unittest.main()
