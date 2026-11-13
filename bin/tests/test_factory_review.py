"""The verifier and the learn step (bin/factory.d/review.sh, design-pick.md unit U4).

`bin/factory` is sourced (FACTORY_SOURCED=1) and review.sh after it, so verify_round and learn_run run with the real
call_start, record and Codex helpers. A fake `claude` on PATH logs each call (argv, prompt, and the HEAD of the
directory it runs in) and answers with the next numbered reply file, or fails when there is none; a fake `codex`
writes its numbered reply to its -o file. `alert` is replaced by a function that logs each needs-you line. No network.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest
import unittest.mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "REPO", "RUN", "LOG")
AUDIT = ROOT / "cultivation/marketplace/sam-cc-setup/skills/audit"

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, os, pathlib, subprocess, sys
d = pathlib.Path(os.environ["FAKE_DIR"])
log = d / "claude-calls.jsonl"
n = len(log.read_text().splitlines()) + 1 if log.exists() else 1
head = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
with log.open("a") as f:
    f.write(json.dumps({"argv": sys.argv[1:], "head": head, "prompt": sys.stdin.read()}) + "\\n")
reply = d / ("claude-reply.%d" % n)
if not reply.exists():
    print(json.dumps({"type": "result", "subtype": "error_during_execution", "is_error": True, "result": ""}))
    sys.exit(1)
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0.01,
                  "result": reply.read_text(), "modelUsage": {}}))
"""

FAKE_CODEX = """#!/usr/bin/env python3
import os, pathlib, sys
if "mcp" in sys.argv:
    print("[]")
    sys.exit(0)
d = pathlib.Path(os.environ["FAKE_DIR"])
calls = d / "codex-calls"
with calls.open("a") as f:
    f.write("call\\n")
reply = d / ("codex-reply.%d" % len(calls.read_text().splitlines()))
if reply.exists():
    pathlib.Path(sys.argv[sys.argv.index("-o") + 1]).write_text(reply.read_text())
"""


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


def review(*findings: tuple[str, str]) -> dict:
    return {"verdict": "fix" if findings else "merge",
            "findings": [{"severity": s, "file": "src/a.py", "line": 3 + i, "defect": d, "fix": "fix " + d}
                         for i, (s, d) in enumerate(findings)]}


def codex(*findings: tuple[str, str]) -> dict:
    return {"verdict": "needs-attention" if findings else "approve", "summary": "s", "next_steps": [],
            "findings": [{"severity": s, "title": t, "body": "body " + t, "file": "src/b.py", "line_start": 7 + i,
                          "line_end": 7 + i, "confidence": 0.9, "recommendation": "do " + t}
                         for i, (s, t) in enumerate(findings)]}


def verdict(id_: str, v: str, cmd: str = "", output: str = "", note: str = "n") -> dict:
    return {"id": id_, "verdict": v, "cmd": cmd, "output": output, "note": note}


class AuditAnchorTest(unittest.TestCase):
    def test_the_verifier_finds_the_section_it_is_sent_to(self) -> None:
        # verify.md sends the verifier to a heading in the audit skill; a rewrite that renames it leaves the verifier lost.
        self.assertIn("`## Verify findings`", (ROOT / "bin/factory.d/verify.md").read_text())
        self.assertIn("\n## Verify findings\n", (AUDIT / "SKILL.md").read_text())


class ReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.wt = self.top / "wt"
        self.wt.mkdir()
        git("init", "-q", "-b", "main", cwd=self.wt)
        git("commit", "-q", "--allow-empty", "-m", "base", cwd=self.wt)
        self.base = git("rev-parse", "HEAD", cwd=self.wt)
        (self.wt / "a.txt").write_text("change\n")
        git("add", "a.txt", cwd=self.wt)
        git("commit", "-q", "-m", "the change", cwd=self.wt)
        self.sha = git("rev-parse", "HEAD", cwd=self.wt)
        self.run_dir = self.top / "run"
        frozen = self.run_dir / "frozen"
        frozen.mkdir(parents=True)
        (frozen / "issue.md").write_text("# Widget\n\n## Goal and why\n\nMake it work.\n")
        (frozen / "role-settings.json").write_text("{}")
        shutil.copy(ROOT / "bin/factory.d/reviewer.schema.json", frozen / "reviewer.schema.json")
        (self.run_dir / "base.sha").write_text(self.base + "\n")
        self.fake = self.top / "fake"
        self.bin = self.top / "bin"
        self.fake.mkdir()
        self.bin.mkdir()
        (self.top / "codex-home").mkdir()
        (self.top / "codex-home" / "auth.json").write_text("{}\n")
        for name, text in (("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX)):
            (self.bin / name).write_text(text)
            (self.bin / name).chmod(0o755)

    def put(self, name: str, obj: object) -> None:
        (self.run_dir / name).write_text(obj if isinstance(obj, str) else json.dumps(obj))

    def replies(self, *objs: object) -> None:
        for k, obj in enumerate(objs, start=1):
            (self.fake / f"claude-reply.{k}").write_text(obj if isinstance(obj, str) else json.dumps(obj))

    def bash(self, body: str, daily: str = "1000", codex_review: str = "yes",
             preset: str = "", **extra: str) -> subprocess.CompletedProcess:
        script = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; GRADED_SHA='{self.sha}'; ISSUE=''; KEY=W1; IS_FILE=1\n"
            'LEDGER="$RUN/ledger.jsonl"; DAILY="$RUN/daily.jsonl"; DECISIONS="$RUN/decisions.md"; LOG="$RUN/factory.log"\n'
            'touch "$LEDGER" "$DAILY"; date -u +%s > "$RUN/launched"\n'
            f"CODEX_REVIEW={codex_review}; CODEX_PATH='{self.bin}'; DAILY_BUDGET_USD={daily}; GRADER_BUDGET_USD=1\n"
            f"{preset}\n"
            f". '{ROOT}/bin/factory.d/review.sh'\n"
            "ticket_name() { echo W1; }\n"
            'alert() { printf \'%s\\n\' "${*: -1}" >> "$RUN/alerts"; }\n'
            f"{body}\n"
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED}
        return subprocess.run(["bash", "-c", f". bin/factory\n{script}"], cwd=ROOT,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), "FAKE_DIR": str(self.fake),
                                   "FACTORY_CODEX_HOME": str(self.top / "codex-home"),
                                   "FACTORY_RUNS_ROOT": str(self.top / "runs"), "REPO": "acme/widget",
                                   "PATH": f"{self.bin}:{env['PATH']}", **extra},
                              capture_output=True, text=True, check=False)

    def verify(self, **kw: str) -> tuple[int, str]:
        proc = self.bash('verify_round 1; echo "rc=$?"', **kw)
        self.assertIn("rc=", proc.stdout, proc.stderr)
        return int(proc.stdout.split("rc=")[-1]), proc.stderr

    def claude_calls(self) -> list[dict]:
        log = self.fake / "claude-calls.jsonl"
        return [json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []

    def read(self, name: str) -> str:
        f = self.run_dir / name
        return f.read_text() if f.exists() else ""

    def alerts(self) -> list[str]:
        return self.read("alerts").splitlines()

    def test_each_verdict_is_routed(self) -> None:
        self.put("round-1.review.json", review(("high", "real bug"), ("medium", "half bug"), ("medium", "made up"),
                                               ("low", "nit")))
        self.put("round-1.codex-review.json", codex(("critical", "invented crash"), ("high", "bare reject"),
                                                    ("medium", "codex nit")))
        self.replies({"findings": [
            verdict("reviewer-0", "CONFIRMED"), verdict("reviewer-1", "PARTLY", note="only the first half"),
            verdict("reviewer-2", "REJECTED", "python3 -c 'print(1)'", "1", note="src/a.py:5 handles it"),
            verdict("codex-0", "REJECTED", "grep -n crash src/b.py", "", note="no output"),
            verdict("codex-1", "REJECTED", "true", "(exit 0)", note="src/b.py:8 guards it")]})
        rc, err = self.verify()
        self.assertEqual(rc, 1, err)
        # One verifier call: Bash in auto mode, the audit skill readable, run in a checkout at the graded sha.
        [call] = self.claude_calls()
        argv = call["argv"]
        self.assertEqual(argv[argv.index("--tools") + 1], "Bash,Read,Grep,Glob")
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "auto")
        self.assertEqual(argv[argv.index("--add-dir") + 1], str(AUDIT))
        self.assertEqual(call["head"], self.sha)
        self.assertIn(f"{AUDIT}/SKILL.md", call["prompt"])
        for shown in ("real bug", "half bug", "made up", "invented crash", "bare reject"):
            self.assertIn(shown, call["prompt"])
        self.assertNotIn("codex nit", call["prompt"])
        # findings.json lists every finding; verify.json exactly the blocking ones.
        findings = json.loads(self.read("round-1.findings.json"))
        self.assertEqual([f["id"] for f in findings],
                         ["reviewer-0", "reviewer-1", "reviewer-2", "reviewer-3", "codex-0", "codex-1", "codex-2"])
        ver = json.loads(self.read("round-1.verify.json"))
        self.assertEqual(ver["sha"], self.sha)
        by = {v["id"]: v for v in ver["findings"]}
        self.assertEqual(set(by), {"reviewer-0", "reviewer-1", "reviewer-2", "codex-0", "codex-1"})
        # A REJECTED with no output is no verdict: it stays UNVERIFIED and reaches the worker marked so.
        self.assertEqual(by["codex-0"]["verdict"], "UNVERIFIED")
        self.assertEqual(by["codex-1"]["verdict"], "REJECTED")
        self.assertEqual((by["codex-1"]["cmd"], by["codex-1"]["output"]), ("true", "(exit 0)"))
        fixes = self.read("round-1.fixes")
        self.assertIn("- src/a.py:3 real bug Fix: fix real bug\n", fixes)
        self.assertIn("half bug Fix: fix half bug (verifier: PARTLY: only the first half)", fixes)
        self.assertIn("- src/b.py:7 [critical] invented crash: body invented crash Fix: do invented crash (UNVERIFIED:", fixes)
        for absent in ("made up", "bare reject", "nit"):
            self.assertNotIn(absent, fixes)
        rejected = self.read("round-1.rejected").splitlines()
        self.assertEqual(rejected, ["- src/a.py:5 made up Fix: fix made up REJECTED: src/a.py:5 handles it",
                                    "- src/b.py:8 [high] bare reject: body bare reject Fix: do bare reject REJECTED: src/b.py:8 guards it"])
        # The rejected high raises needs-you, the rejected medium does not; the UNVERIFIED one raises its own.
        alerts = self.alerts()
        self.assertEqual(len([a for a in alerts if "rejected the codex [high] src/b.py:8" in a]), 1, alerts)
        self.assertFalse([a for a in alerts if "src/a.py:5" in a], alerts)
        self.assertEqual(len([a for a in alerts if "UNVERIFIED" in a]), 1, alerts)
        roles = [json.loads(x)["role"] for x in self.read("ledger.jsonl").splitlines()]
        self.assertEqual(roles, ["verifier"])

    def test_no_blocking_finding_makes_no_call(self) -> None:
        self.put("round-1.review.json", review(("low", "nit")))
        self.put("round-1.codex-review.json", codex(("medium", "codex nit")))
        rc, err = self.verify()
        self.assertEqual(rc, 0, err)
        self.assertEqual(self.claude_calls(), [])
        self.assertEqual(json.loads(self.read("round-1.verify.json")), {"sha": self.sha, "findings": []})
        self.assertEqual(self.read("round-1.fixes"), "")

    def test_all_rejected_queues_no_fix(self) -> None:
        self.put("round-1.review.json", review(("medium", "made up")))
        self.replies({"findings": [verdict("reviewer-0", "REJECTED", "cat src/a.py", "ok")]})
        rc, err = self.verify(codex_review="no")
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(self.claude_calls()), 1)
        self.assertEqual(self.read("round-1.fixes"), "")
        self.assertIn("made up", self.read("round-1.rejected"))

    def test_a_failed_call_sends_every_blocking_finding_unverified_and_alerts(self) -> None:
        self.put("round-1.review.json", review(("high", "real bug"), ("low", "nit")))
        self.put("round-1.codex-review.json", codex(("high", "codex bug")))
        rc, err = self.verify()   # no reply file: the fake claude fails
        self.assertEqual(rc, 1, err)
        self.assertEqual(len(self.claude_calls()), 1)
        ver = json.loads(self.read("round-1.verify.json"))
        self.assertEqual({v["id"]: v["verdict"] for v in ver["findings"]},
                         {"reviewer-0": "UNVERIFIED", "codex-0": "UNVERIFIED"})
        fixes = self.read("round-1.fixes")
        self.assertIn("real bug Fix: fix real bug (UNVERIFIED:", fixes)
        self.assertIn("codex bug: body codex bug Fix: do codex bug (UNVERIFIED:", fixes)
        self.assertNotIn("nit", fixes)
        self.assertEqual(len([a for a in self.alerts() if "UNVERIFIED" in a]), 1, self.alerts())

    def test_each_source_blocks_once(self) -> None:
        self.put("round-1.review.json", review(("high", "real bug")))
        self.put("round-1.codex-review.json", codex(("high", "codex bug")))
        self.replies({"findings": [verdict("reviewer-0", "CONFIRMED"), verdict("codex-0", "CONFIRMED")]})
        rc, err = self.verify(preset="REVIEW_BLOCKED=1")
        self.assertEqual(rc, 1, err)
        fixes = self.read("round-1.fixes")
        self.assertIn("codex bug", fixes)
        self.assertNotIn("real bug", fixes)

    def learn(self, **kw: str) -> subprocess.CompletedProcess:
        proc = self.bash('learn_run "$@"; echo "rc=$?"', **kw)
        self.assertIn("rc=0", proc.stdout, proc.stderr)
        return proc

    def test_no_follow_ups_make_no_draft(self) -> None:
        self.put("round-1.judge.json", {"verdict": "pass", "backlog": []})
        self.put("round-1.review.json", review(("low", "nit")))
        self.learn(preset="ROUND=1")
        self.assertEqual(self.read("followups.md"), "")
        self.assertEqual(self.claude_calls(), [])
        self.assertFalse((self.run_dir / "learn" / "draft.md").exists())

    def test_the_daily_cap_stops_learn_calls(self) -> None:
        self.put("round-1.judge.json", {"verdict": "pass", "backlog": ["the gate ran serially"]})
        self.put("daily.jsonl", json.dumps({"date": "x", "cost_usd": 0}) + "\n")
        # one call's cap (1 usd) alone passes 0.5; only an API-billed run has a daily budget (Decision 6)
        self.learn(preset="ROUND=1", daily="0.5", ANTHROPIC_API_KEY="sk-ant-test")
        self.assertEqual(self.read("followups.md"), "- judge-backlog [-] -:0 the gate ran serially\n")
        self.assertEqual(self.claude_calls(), [])
        self.assertFalse((self.fake / "codex-calls").exists())
        self.assertFalse((self.run_dir / "learn" / "draft.md").exists())

    def test_a_killed_learn_call_is_charged_its_ceiling(self) -> None:
        # audit3 C1: the writer's claude exits with no envelope, as a CALL_TIMEOUT_SEC kill leaves it; it may have
        # spent up to its --max-budget-usd, so the ledger and the daily file book GRADER_BUDGET_USD (1 here).
        self.put("round-1.judge.json", {"verdict": "pass", "backlog": ["x"]})
        (self.bin / "claude").write_text("#!/bin/sh\ncat > /dev/null; exit 137\n")
        self.learn(preset="ROUND=1")
        rows = [json.loads(x) for x in self.read("ledger.jsonl").splitlines()]
        self.assertEqual([(r["role"], r["cost_usd"], r["subtype"]) for r in rows], [("learn-writer", 1, "no-result")])
        self.assertEqual([json.loads(x)["cost_usd"] for x in self.read("daily.jsonl").splitlines()], [1])

    def test_a_launch_stopped_at_the_daily_cap_leaves_the_draft_to_the_next(self) -> None:
        # audit3 F3: launch 1 ends at the daily cap, so learn makes no call; launch 2 in the same run directory, with
        # room in the budget, still drafts the run's one ticket. An API-billed run: only it has a daily budget.
        self.put("round-1.judge.json", {"verdict": "pass", "backlog": ["the gate ran serially"]})
        self.put("daily.jsonl", json.dumps({"date": "x", "cost_usd": 0}) + "\n")
        self.learn(preset="ROUND=1", daily="0.5", ANTHROPIC_API_KEY="sk-ant-test")
        self.assertEqual(self.claude_calls(), [])
        self.replies({"repo": "distbench", "title": "t", "source_line": "x", "body": "# F00: t\n"})
        self.learn(preset="ROUND=1")
        calls = self.claude_calls()
        self.assertEqual(len(calls), 2)  # the writer and the review of its draft
        self.assertIn("the gate ran serially", calls[0]["prompt"])
        self.assertEqual(json.loads(self.read("learn/draft.json"))["title"], "t")

    def test_learn_drafts_reviews_and_verifies_once(self) -> None:
        self.put("round-1.judge.json", {"verdict": "pass", "backlog": []})
        self.put("round-1.review.json", review(("high", "kept bug")))
        self.put("round-1.findings.json", [{"id": "reviewer-0", "source": "reviewer", "severity": "high",
                                            "file": "src/a.py", "line": 3, "claim": "kept bug Fix: fix kept bug"}])
        self.put("round-1.verify.json", {"sha": self.sha, "findings": [verdict("reviewer-0", "CONFIRMED")]})
        draft = "# F00: Fix the kept bug\n\nBrief: fix it\n"
        self.replies({"repo": "distbench", "title": "Fix the kept bug", "source_line": "x", "body": draft},
                     review(("high", "the done check passes today"), ("low", "wording")),
                     {"findings": [verdict("reviewer-0", "CONFIRMED"), verdict("codex-0", "REJECTED", "ls", "a.txt")]})
        (self.fake / "codex-reply.1").write_text("Two findings.\n- [high] docs/x.md:4 the path does not exist\n"
                                                 "- [low] docs/x.md:9 wording\n")
        self.bash('learn_run stuck "the same checks failed twice"', preset="ROUND=1")
        followups = self.read("followups.md").splitlines()
        self.assertEqual(followups[0], "- factory [stuck] -:0 the same checks failed twice")
        self.assertIn("- reviewer [high] src/a.py:3 kept bug Fix: fix kept bug", followups)
        learn = self.run_dir / "learn"
        self.assertEqual((learn / "draft.md").read_text(), draft + "\n")
        self.assertEqual(json.loads((learn / "draft.json").read_text())["repo"], "distbench")
        findings = json.loads((learn / "findings.json").read_text())
        self.assertEqual([(f["id"], f["severity"]) for f in findings],
                         [("reviewer-0", "high"), ("reviewer-1", "low"), ("codex-0", "high"), ("codex-1", "low")])
        ver = json.loads((learn / "verify.json").read_text())
        self.assertEqual({v["id"]: v["verdict"] for v in ver["findings"]}, {"reviewer-0": "CONFIRMED", "codex-0": "REJECTED"})
        roles = [json.loads(x)["role"] for x in self.read("ledger.jsonl").splitlines()]
        self.assertEqual(roles, ["learn-writer", "learn-review", "learn-review", "verifier"])
        self.assertTrue([a for a in self.alerts() if "learn drafted a distbench ticket" in a and "draft.md" in a],
                        self.alerts())
        # A second call in the same run directory drafts nothing more.
        self.bash("learn_run", preset="ROUND=1")
        self.assertEqual(len(self.claude_calls()), 3)

    def test_a_fable_reviewer_runs_at_high(self) -> None:
        # audit3 C5: Samyak's rule is Fable always at high (~/.claude/rules/pstack-models.md); with no
        # FACTORY_REVIEWER_EFFORT, a Fable reviewer (graders and learn) must not get the Opus default xhigh.
        self.put("round-1.judge.json", {"verdict": "pass", "backlog": ["the gate ran serially"]})
        self.replies({"repo": "distbench", "title": "t", "source_line": "x", "body": "# F00: t\n"}, review())
        env = {k: v for k, v in os.environ.items() if k != "FACTORY_REVIEWER_EFFORT"}
        with unittest.mock.patch.dict(os.environ, env, clear=True):
            proc = self.bash('echo "graders: $(grader_model reviewer) $(grader_effort reviewer)"; learn_run',
                             preset="ROUND=1", FACTORY_REVIEWER_MODEL="claude-fable-5-2")
        self.assertIn("graders: claude-fable-5-2 high", proc.stdout, proc.stderr)
        review_call = self.claude_calls()[1]["argv"]
        self.assertEqual((review_call[review_call.index("--model") + 1], review_call[review_call.index("--effort") + 1]),
                         ("claude-fable-5-2", "high"))

    def test_a_file_tickets_alert_and_learn_brief_name_the_target(self) -> None:
        # A file ticket has no REPO and no issue (the F103 proof's alert went out with project "" and run "F103-...").
        target = self.top / "target"
        target.mkdir()
        git("init", "-q", cwd=target)
        git("remote", "add", "origin", "git@github.com:Acme/Widget.git", cwd=target)
        proc = self.bash(f"TARGET='{target}'\n"
                         'alert() { printf "%s\\n" "$@" > "$RUN/alert-args"; }\n'
                         'review_alert "the draft waits"; learn_brief Writer "$TARGET" "$RUN/learn"', REPO="")
        args = self.read("alert-args").splitlines()
        self.assertEqual(args[args.index("--project") + 1], "widget", proc.stderr)
        self.assertEqual(args[args.index("--run") + 1], "ticket W1")
        self.assertIn("`widget`", proc.stdout)
        self.assertNotIn("<target-name>", proc.stdout)

    def test_a_usage_limit_past_max_hours_in_learn_gives_up_the_call_not_the_exit(self) -> None:
        # learn_run runs inside finish; a limit_wait finish there would replace the run's exit (pr-opened) with
        # stopped-environment.
        self.put("limit.json", {"type": "result", "is_error": True, "result": "You hit your limit · resets 3am (UTC)"})
        body = ('limit_switch() { return 1; }; finish() { echo "FINISH $1"; exit 9; }; echo 0 > "$RUN/launched"\n'
                'MAX_HOURS=1 REVIEW_NO_FINISH={} limit_wait "$RUN/limit.json"; echo "rc=$?"')
        learn = self.bash(body.replace("{}", "1"))
        self.assertIn("rc=1", learn.stdout, learn.stderr)
        self.assertNotIn("FINISH", learn.stdout)
        loop = self.bash(body.replace("{}", ""))
        self.assertIn("FINISH stopped-environment", loop.stdout, loop.stderr)


if __name__ == "__main__":
    unittest.main()
