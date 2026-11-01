"""bin/factory.d/model-eval: a Codex cell gets a strict schema, reuse keys cover the harness, each grader's
fingerprint describes its own replies, an unparseable reply is retried, and an off-model serve stops the grid.

Runs the real model-eval and bin/factory eval with a fake `claude` and `codex` on PATH and a fake HOME, so no
model is called. The fake codex refuses a non-strict --output-schema, as the API does (400, "additionalProperties
is required to be supplied and to be false").
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODEL_EVAL = ROOT / "bin/factory.d/model-eval"
AGENTS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"

# The reply each grader gives in both fakes; the fake codex adds a null for every optional field.
REPLIES = """
REPLIES = {
    "judge": {"verdict": "fail", "rows": {"correct": "fail", "verified": "pass", "honest": "pass"}, "fixes": []},
    "reviewer": {"verdict": "fix", "findings": [{"severity": "high", "file": "a.py", "defect": "d", "fix": "f"}]},
    "lean-critic": {"verdict": "fix", "findings": [{"severity": "high", "file": "a.py", "defect": "d", "fix": "f"}]},
}
def grader_of(schema):
    props = schema.get("properties", {})
    return "judge" if "rows" in props else "lean-critic" if "rules" in props else "reviewer"
"""

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]
g = lambda f: a[a.index(f) + 1] if f in a else ""
if "--version" in a:
    print(os.environ.get("STUB_VERSION", "1.0.0") + " (Claude Code)")
    sys.exit(0)
sys.stdin.read()
""" + REPLIES + """
with open(os.environ["STUB_LOG"], "a") as f:
    f.write("call %s\\n" % g("--model"))
reply = "no verdict here" if os.environ.get("STUB_BAD") else json.dumps(REPLIES[grader_of(json.loads(g("--json-schema")))])
served = os.environ.get("STUB_SERVED") or g("--model")
print(json.dumps({"type": "result", "is_error": False, "total_cost_usd": 0, "result": reply, "modelUsage": {served: {}}}))
"""

FAKE_CODEX = """#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]
g = lambda f: a[a.index(f) + 1] if f in a else ""
sys.stdin.read()
""" + REPLIES + """
with open(os.environ["STUB_LOG"], "a") as f:
    f.write("codex %s\\n" % g("-m"))
if os.environ.get("STUB_CWD"):
    with open(os.environ["STUB_CWD"], "a") as f:
        import glob
        keys = glob.glob("../**/expected.json", recursive=True) + glob.glob("**/expected.json", recursive=True)
        f.write("evals=%s factory=%s cd=%s keys=%d\\n" % (os.path.isdir("evals"), os.path.isfile("bin/factory"),
                                                os.path.realpath(g("-C") or ".") == os.path.realpath("."), len(keys)))
def strict(node):
    if not isinstance(node, dict):
        return True
    if node.get("type") == "object" or "properties" in node:
        if node.get("additionalProperties") is not False or set(node.get("required", [])) != set(node.get("properties", {})):
            return False
    kids = list(node.get("properties", {}).values()) + node.get("anyOf", []) + [node.get("items")]
    return all(strict(k) for k in kids)
schema = json.load(open(g("--output-schema")))
if not strict(schema):
    print("400 Invalid schema: 'additionalProperties' is required to be supplied and to be false", file=sys.stderr)
    sys.exit(1)
grader = grader_of(schema)
reply = json.loads(json.dumps(REPLIES[grader]))
reply[{"judge": "backlog", "reviewer": "unverified", "lean-critic": "rules"}[grader]] = None
for x in reply.get("findings", []):
    x["line"] = None
open(g("-o"), "w").write(json.dumps(reply))
"""


def load_model_eval():
    loader = importlib.machinery.SourceFileLoader("model_eval", str(MODEL_EVAL))
    spec = importlib.util.spec_from_loader("model_eval", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def assert_strict(test, node, where):
    if isinstance(node, list):
        for i, x in enumerate(node):
            assert_strict(test, x, f"{where}[{i}]")
        return
    if not isinstance(node, dict):
        return
    if node.get("type") == "object" or "properties" in node or "required" in node:
        test.assertIs(node.get("additionalProperties"), False, where)
        test.assertEqual(set(node.get("required", [])), set(node.get("properties", {})), where)
    for k, v in node.items():
        assert_strict(test, v, f"{where}.{k}")


class ModelEvalTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.tmp = pathlib.Path(tmp_dir.name)
        stub = self.tmp / "stub"
        stub.mkdir()
        for name, text in (("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX)):
            (stub / name).write_text(text)
            (stub / name).chmod(0o755)
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.log = self.tmp / "calls"
        self.log.touch()
        self.out = self.tmp / "out"
        self.env = {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "HOME": str(self.home),
                    "STUB_LOG": str(self.log), "MODEL_EVAL_SET": str(self.tmp / "set"),
                    "MODEL_EVAL_OUT": str(self.out), "MODEL_EVAL_REPEATS": "1", "MODEL_EVAL_GRADERS_DIR": str(AGENTS)}
        for k in ("STUB_VERSION", "STUB_SERVED", "STUB_BAD", "EVAL_OUT", "MODEL_EVAL_EFFORTS", "MODEL_EVAL_SEED"):
            self.env.pop(k, None)

    def case(self, grader: str, name: str, exp: dict) -> None:
        d = self.tmp / "set" / grader / name
        d.mkdir(parents=True)
        (d / "prompt.md").write_text(f"## Ticket\n{name}\n")
        (d / "expected.json").write_text(json.dumps(exp))

    def judge_cases(self) -> None:
        for name in ("k1", "k2"):
            self.case("judge", name, {"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]})

    def run_me(self, *models: str, **env: str) -> subprocess.CompletedProcess:
        self.log.write_text("")
        return subprocess.run([str(MODEL_EVAL), *models], cwd=ROOT, env={**self.env, **env},
                              capture_output=True, text=True, timeout=300)

    def calls(self) -> list[str]:
        return self.log.read_text().splitlines()

    def table(self, text: str) -> dict:
        return {tuple(r[:3]): r[3] for r in (ln.split("\t") for ln in text.splitlines()) if len(r) >= 4}

    def test_codex_schema_is_strict_for_every_grader(self) -> None:
        me = load_model_eval()
        for g in ("judge", "reviewer", "lean-critic"):
            assert_strict(self, me.strict_schema(json.loads((ROOT / f"bin/factory.d/{g}.schema.json").read_text())), g)

    def test_codex_reply_with_nulls_scores_like_claude(self) -> None:
        self.case("judge", "k1", {"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]})
        for g in ("reviewer", "lean-critic"):
            self.case(g, "k1", {"verdict": "fix", "defect_class": "logic-bug", "defect_file": "a.py"})
        r = self.run_me("m1", "codex:x")
        self.assertEqual(r.returncode, 0, r.stderr)
        t = self.table(r.stdout)
        for g in ("judge", "reviewer", "lean-critic"):
            for metric in ("recall:logic-bug", "infra"):
                self.assertEqual(t.get((g, "codex:x@high", metric)), t.get((g, "m1@high", metric)), (g, metric))
            self.assertEqual(t.get((g, "codex:x@high", "recall:logic-bug")), "1.00", g)
            self.assertEqual(t.get((g, "codex:x@high", "infra")), "0", g)

    def test_codex_runs_in_the_export_without_the_answer_keys(self) -> None:
        # model-eval runs from the checkout, whose evals/ holds every expected.json, and a Codex grader reads
        # the directory it runs in, so it gets the export a Claude cell's bin/factory eval reads.
        self.judge_cases()
        seen = self.tmp / "cwd"
        # A Claude cell first, so its copied cases (each with an expected.json) exist while the Codex cell runs.
        r = self.run_me("m1", "codex:x", MODEL_EVAL_GRADERS="judge", STUB_CWD=str(seen))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(seen.read_text().splitlines(), ["evals=False factory=True cd=True keys=0"] * 2)

    def test_harness_change_regrades_every_reply(self) -> None:
        self.judge_cases()
        drift = self.home / ".claude/config-drift.sh"
        drift.parent.mkdir()
        drift.write_text('#!/bin/sh\ncat "$HOME/drift"\n')
        drift.chmod(0o755)
        (self.home / "drift").write_text("d1\n")
        env = {"MODEL_EVAL_GRADERS": "judge"}
        self.assertEqual(self.run_me("m1", **env, STUB_VERSION="1").returncode, 0)
        self.assertEqual(len(self.calls()), 2)
        self.assertEqual(self.run_me("m1", **env, STUB_VERSION="1").returncode, 0)
        self.assertEqual(self.calls(), [], "an unchanged harness reuses every reply")
        self.assertEqual(self.run_me("m1", **env, STUB_VERSION="2").returncode, 0)
        self.assertEqual(len(self.calls()), 2, "a Claude Code update re-grades every case")
        fp = (self.out / "replies/m1@high/r1/fingerprint-judge.txt").read_text()
        self.assertIn("claude-version 2 (Claude Code)\n", fp)
        (self.home / "drift").write_text("d2\n")
        self.assertEqual(self.run_me("m1", **env, STUB_VERSION="2").returncode, 0)
        self.assertEqual(len(self.calls()), 2, "a config change re-grades every case")
        # config-drift.sh prints setting names only, so a changed value must reach the key some other way.
        (self.home / ".claude/settings.json").write_text('{"permissions": {"deny": ["Read(secret.txt)"]}}\n')
        self.assertEqual(self.run_me("m1", **env, STUB_VERSION="2").returncode, 0)
        self.assertEqual(len(self.calls()), 2)
        (self.home / ".claude/settings.json").write_text('{"permissions": {"deny": ["Read(*)"]}}\n')
        self.assertEqual(self.run_me("m1", **env, STUB_VERSION="2").returncode, 0)
        self.assertEqual(len(self.calls()), 2, "a changed setting value re-grades every case")

    def test_each_graders_fingerprint_describes_its_own_replies(self) -> None:
        self.judge_cases()
        self.case("reviewer", "k1", {"verdict": "merge"})
        self.assertEqual(self.run_me("m1", "m2", MODEL_EVAL_GRADERS="judge", STUB_VERSION="1").returncode, 0)
        # A second grader on one model under a new Claude Code leaves the judge's config where its replies ran.
        self.assertEqual(self.run_me("m2", MODEL_EVAL_GRADERS="reviewer", STUB_VERSION="2").returncode, 0)

        def moved():
            r = subprocess.run([sys.executable, str(ROOT / "bin/factory.d/eval_score.py"), str(self.tmp / "set"),
                                str(self.out / "replies")], capture_output=True, text=True)
            return self.table(r.stdout).get(("judge", "m1@high~m2@high", "moved"))

        self.assertEqual(moved(), "model")
        # A partial retry under the new version re-grades all of m2's judge cases, so its fingerprint fits them.
        (self.out / "replies/m2@high/r1/judge-k1.json").unlink()
        self.assertEqual(self.run_me("m2", MODEL_EVAL_GRADERS="judge", STUB_VERSION="2").returncode, 0)
        self.assertEqual(len(self.calls()), 2)
        self.assertEqual(moved(), "descriptive: claude-version,model")

    def test_unparseable_reply_gets_no_key_and_is_retried(self) -> None:
        self.judge_cases()
        self.run_me("m1", MODEL_EVAL_GRADERS="judge", STUB_BAD="1")
        cell = self.out / "replies/m1@high/r1"
        self.assertTrue((cell / "judge-k1.json").is_file())
        self.assertEqual(sorted(cell.glob("*.key")), [])
        self.assertEqual(self.run_me("m1", MODEL_EVAL_GRADERS="judge").returncode, 0)
        self.assertEqual(len(self.calls()), 2)
        self.assertEqual(len(list(cell.glob("*.key"))), 2)

    def test_off_model_serve_stops_after_the_first_cell(self) -> None:
        self.judge_cases()
        r = self.run_me("m1", "m2", MODEL_EVAL_GRADERS="judge", STUB_SERVED="claude-haiku-4-5")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertIn("served by claude-haiku-4-5", r.stderr)
        self.assertNotIn("wilson", r.stdout.lower())
        self.assertEqual(len(set(self.calls())), 1, f"a second cell was paid for: {self.calls()}")
