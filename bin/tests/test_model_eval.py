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
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODEL_EVAL = ROOT / "bin/factory.d/model-eval"
AGENTS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
CREDENTIALS = ("CODEX_API_KEY", "OPENAI_API_KEY", "CODEX_ACCESS_TOKEN", "OPENAI_FEDERATION_RULE_ID",
               "OPENAI_IDENTITY_TOKEN_FILE", "OPENAI_WORKLOAD_IDENTITY_CONTEXT")

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
# STUB_FAIL_AFTER=n: every call after the n-th is an API error, as bin/factory eval saves no reply for.
err = len(open(os.environ["STUB_LOG"]).readlines()) > int(os.environ.get("STUB_FAIL_AFTER") or 1 << 30)
if err:
    reply = "API Error: 500"
print(json.dumps({"type": "result", "is_error": err, "total_cost_usd": 0, "result": reply, "modelUsage": {served: {}}}))
"""

FAKE_CODEX = """#!/usr/bin/env python3
import json, os, sys
a = sys.argv[1:]
g = lambda f: a[a.index(f) + 1] if f in a else ""
if "mcp" in a:
    if os.environ.get("STUB_SEEN"):
        json.dump({"argv": a, "home": os.environ.get("CODEX_HOME"), "env": sorted(os.environ), "cwd": os.getcwd()},
                  open(os.environ["STUB_SEEN"] + ".mcp", "w"))
    print(os.environ.get("STUB_MCP_REPLY", '[{"name":"mcp.consensus.app"}]'))
    sys.exit(0)
sys.stdin.read()
""" + REPLIES + """
with open(os.environ["STUB_LOG"], "a") as f:
    f.write("codex %s\\n" % g("-m"))
if os.environ.get("STUB_SEEN"):
    import pathlib
    home = os.environ.get("CODEX_HOME", "")
    files = sorted(str(p.relative_to(home)) for p in pathlib.Path(home).rglob("*")) if home else []
    tree = sorted(str(p) for p in pathlib.Path(".").rglob("*") if p.name in ("evals", "cases", "expected.json")
                  or str(p) == "bin/factory")
    json.dump({"argv": a, "tree": tree, "home": home, "files": files, "env": sorted(os.environ), "cwd": os.getcwd()},
              open(os.environ["STUB_SEEN"], "w"))
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
        self.stub = stub
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.log = self.tmp / "calls"
        self.log.touch()
        self.out = self.tmp / "out"
        self.fhome = self.tmp / "factory-codex-home"
        self.fhome.mkdir()
        (self.fhome / "auth.json").write_text("{}\n")
        self.env = {**os.environ, "PATH": f"{stub}:{os.environ['PATH']}", "HOME": str(self.home),
                    "STUB_LOG": str(self.log), "MODEL_EVAL_SET": str(self.tmp / "set"),
                    "MODEL_EVAL_OUT": str(self.out), "MODEL_EVAL_REPEATS": "1", "MODEL_EVAL_GRADERS_DIR": str(AGENTS),
                    "FACTORY_CODEX_HOME": str(self.fhome)}
        for k in ("STUB_VERSION", "STUB_SERVED", "STUB_BAD", "STUB_FAIL_AFTER", "EVAL_OUT", "MODEL_EVAL_EFFORTS", "MODEL_EVAL_SEED",
                  "FACTORY_ROOT", "CODEX_HOME"):
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

    def test_codex_cell_runs_in_the_evals_free_export_under_the_factory_home(self) -> None:
        # The answer keys stay out of the cell's tree, as for a Claude cell, and the operator's ~/.codex
        # AGENTS.md and rules stay out of its home (#490, #543).
        self.case("judge", "k1", {"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]})
        (self.home / ".codex/rules").mkdir(parents=True)
        (self.home / ".codex/AGENTS.md").write_text("Ask only when the task is ambiguous.\n")
        (self.home / ".codex/rules/default.rules").write_text("")
        (self.home / ".codex/auth.json").write_text("{}\n")
        skill = self.home / ".agents/skills/personal-audit/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: personal-audit\ndescription: operator skill\n---\nOPERATOR BODY\n")
        seen = self.tmp / "seen.json"
        r = self.run_me("codex:x", MODEL_EVAL_GRADERS="judge", STUB_SEEN=str(seen),
                        **{k: "operator-credential" for k in CREDENTIALS})
        self.assertEqual(r.returncode, 0, r.stderr)
        s = json.loads(seen.read_text())
        self.assertEqual(s["tree"], ["bin/factory"])  # the export, with no evals/ and no expected.json in it
        self.assertEqual(s["home"], str(self.fhome))
        self.assertEqual(s["files"], ["auth.json"])
        self.assertIn("--skip-git-repo-check", s["argv"])
        pairs = [s["argv"][i:i + 2] for i in range(len(s["argv"]) - 1)]
        self.assertIn(["-c", "skills.include_instructions=false"], pairs)
        probe = json.loads(pathlib.Path(str(seen) + ".mcp").read_text())
        self.assertEqual(probe["cwd"], s["cwd"])
        self.assertEqual(probe["home"], str(self.fhome))
        self.assertEqual(set(probe["env"]) & set(CREDENTIALS), set())
        probe_pairs = [probe["argv"][i:i + 2] for i in range(len(probe["argv"]) - 1)]
        for key in ("features.plugins", "features.remote_plugin", "features.apps", "features.skill_mcp_dependency_install"):
            for argv in (pairs, probe_pairs):
                self.assertIn(["-c", f"{key}=false"], argv)
        mcp = [tomllib.loads(v)["mcp_servers"] for k, v in pairs if k == "-c" and v.startswith("mcp_servers=")]
        self.assertEqual(mcp, [{"mcp.consensus.app": {"enabled": False}}])
        # The operator's skill is disabled by path, so a `$personal-audit` in a case prompt cannot load it.
        rules = [tomllib.loads("v = " + v.removeprefix("skills.config="))["v"] for k, v in pairs
                 if k == "-c" and v.startswith("skills.config=")]
        self.assertEqual(rules, [[{"path": str(skill), "enabled": False}]])
        self.assertEqual(set(s["env"]) & set(CREDENTIALS), set())  # each would outrank the factory's own login

    def test_codex_cell_with_an_invalid_mcp_list_makes_no_model_call(self) -> None:
        self.case("judge", "k1", {"verdict": "pass"})
        r = self.run_me("codex:x", MODEL_EVAL_GRADERS="judge", STUB_MCP_REPLY="not json")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("codex_mcp_off", r.stderr)
        self.assertEqual(self.calls(), [])

    def test_codex_cell_export_drops_a_custom_set_outside_evals(self) -> None:
        # A committed set outside evals/ (MODEL_EVAL_SET=cases) is removed from the export too.
        proj = self.tmp / "proj"
        d = proj / "cases" / "judge" / "k1"
        d.mkdir(parents=True)
        (d / "prompt.md").write_text("## Ticket\nk1\n")
        (d / "expected.json").write_text(json.dumps({"verdict": "fail", "defect_class": "logic-bug",
                                                     "failing_rows": ["correct"]}))
        (proj / "bin").mkdir()
        (proj / "bin/factory").write_text("")
        for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"]):
            subprocess.run(["git", *args], cwd=proj, check=True, capture_output=True)
        seen = self.tmp / "seen.json"
        r = self.run_me("codex:x", MODEL_EVAL_GRADERS="judge", MODEL_EVAL_SET=str(proj / "cases"),
                        FACTORY_ROOT=str(proj), STUB_SEEN=str(seen))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(seen.read_text())["tree"], ["bin/factory"])

    def test_codex_cell_without_the_factory_login_makes_no_call(self) -> None:
        self.case("judge", "k1", {"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]})
        (self.home / ".codex").mkdir()
        (self.home / ".codex/auth.json").write_text("{}\n")  # the operator's login is never a fallback
        for auth in (None, '{"tokens": {}}"}\n'):  # missing, or left corrupt by a concurrent token refresh
            with self.subTest(auth=auth):
                if auth is None:
                    (self.fhome / "auth.json").unlink()
                else:
                    (self.fhome / "auth.json").write_text(auth)
                r = self.run_me("codex:x", MODEL_EVAL_GRADERS="judge")
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("no factory Codex login", r.stderr)
                self.assertEqual(self.calls(), [])

    def test_codex_cell_finds_codex_where_the_factory_does(self) -> None:
        # Codex is not on the non-interactive PATH (#41); bin/factory prepends ~/.local/bin, and so must the eval.
        self.case("judge", "k1", {"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]})
        (self.home / ".local/bin").mkdir(parents=True)
        (self.stub / "codex").rename(self.home / ".local/bin/codex")
        path = ":".join(d for d in self.env["PATH"].split(":") if not (pathlib.Path(d) / "codex").exists())
        r = self.run_me("codex:x", MODEL_EVAL_GRADERS="judge", PATH=path)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.calls(), ["codex x"])

    def test_codex_cell_key_follows_the_factory_home_config(self) -> None:
        # A Codex cell runs on the factory's config.toml, never the operator's, so only the former re-grades it.
        self.case("judge", "k1", {"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]})
        env = {"MODEL_EVAL_GRADERS": "judge"}
        self.assertEqual(self.run_me("codex:x", **env).returncode, 0)
        self.assertEqual(self.calls(), ["codex x"])
        (self.home / ".codex").mkdir()
        (self.home / ".codex/config.toml").write_text('model = "operator-model"\n')
        self.assertEqual(self.run_me("codex:x", **env).returncode, 0)
        self.assertEqual(self.calls(), [], "the operator's Codex config does not reach a Codex cell")
        (self.fhome / "config.toml").write_text('model = "factory-model"\n')
        self.assertEqual(self.run_me("codex:x", **env).returncode, 0)
        self.assertEqual(self.calls(), ["codex x"], "a factory config change re-grades the Codex cell")

    def test_codex_runs_in_the_export_without_the_answer_keys(self) -> None:
        # model-eval runs from the checkout, whose evals/ holds every expected.json, and a Codex grader reads
        # the directory it runs in, so it gets the export a Claude cell's bin/factory eval reads.
        self.judge_cases()
        seen = self.tmp / "cwd"
        # A Claude cell first, so its copied cases (each with an expected.json) exist while the Codex cell runs.
        r = self.run_me("m1", "codex:x", MODEL_EVAL_GRADERS="judge", STUB_CWD=str(seen))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(seen.read_text().splitlines(), ["evals=False factory=True cd=True keys=0"] * 2)

    def test_a_case_whose_diff_does_not_apply_is_recorded_once(self) -> None:
        # Its tree cannot be built, so no grader reads a half-built tree; the case still shows in the table, as a
        # failed reply, and a rerun with nothing changed does not try it again.
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        d = self.tmp / "set" / "judge" / "k1"
        d.mkdir(parents=True)
        fence = "~~~~~~~~~~~~ evidence"
        diff = "diff --git a/no-such-file b/no-such-file\n--- a/no-such-file\n+++ b/no-such-file\n@@ -1 +1 @@\n-old\n+new"
        (d / "prompt.md").write_text(f"## Ticket\n\n## Diff ({head[:8]}...HEAD)\n\n{fence}\n{diff}\n{fence}\n")
        (d / "expected.json").write_text(json.dumps({"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]}))
        for m in ("m1", "codex:x"):
            r = self.run_me(m, MODEL_EVAL_GRADERS="judge")
            self.assertEqual(r.returncode, 0, r.stderr)
            reply = json.loads((self.out / f"replies/{m}@high/r1/judge-k1.json").read_text())
            self.assertTrue(reply["is_error"] and reply["result"].startswith("TREE "), reply)
            self.assertEqual(self.table(r.stdout).get(("judge", f"{m}@high", "infra")), "1", r.stdout)
            again = self.run_me(m, MODEL_EVAL_GRADERS="judge")
            self.assertNotIn("1 of 1 cases", again.stderr, "an unchanged TREE failure was graded again")
        self.assertEqual(self.calls(), [], "no grader call read a half-built tree")

    def test_a_case_whose_recorded_base_is_missing_is_retried(self) -> None:
        # An unfetched tree_base is the checkout's state, not the case's: the case fails as TREE, never grades in
        # HEAD, and gets no reuse key, so the next run tries it again.
        d = self.tmp / "set" / "judge" / "k1"
        d.mkdir(parents=True)
        (d / "prompt.md").write_text("## Ticket\n\n## Diff (main...HEAD)\n")
        (d / "expected.json").write_text(json.dumps({"verdict": "pass", "tree_base": "f" * 40}))
        for m in ("m1", "codex:x"):
            r = self.run_me(m, MODEL_EVAL_GRADERS="judge")
            self.assertEqual(r.returncode, 0, r.stderr)
            reply = json.loads((self.out / f"replies/{m}@high/r1/judge-k1.json").read_text())
            self.assertTrue(reply["is_error"] and reply["result"].startswith("TREE tree_base "), reply)
            self.assertFalse((self.out / f"replies/{m}@high/r1/judge-k1.key").exists())
            again = self.run_me(m, MODEL_EVAL_GRADERS="judge")
            self.assertIn("1 of 1 cases", again.stderr, "a TREE failure of the environment was not retried")
        self.assertEqual(self.calls(), [], "no grader call graded the case in HEAD")

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

    def test_a_repeat_whose_calls_all_failed_counts_as_infra(self) -> None:
        self.case("judge", "k1", {"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]})
        (self.tmp / "set/reviewer").mkdir()
        r = self.run_me("m1", MODEL_EVAL_GRADERS="judge reviewer", MODEL_EVAL_REPEATS="2", STUB_FAIL_AFTER="1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.calls()), 2)
        saved = [k for k in ("r1", "r2") if (self.out / f"replies/m1@high/{k}/judge-k1.json").exists()]
        self.assertEqual(len(saved), 1, saved)
        t = self.table(r.stdout)
        self.assertEqual((t[("judge", "m1@high", "infra")], t[("judge", "m1@high", "n:infra")]), ("1", "2"))
        self.assertEqual(t[("judge", "m1@high", "n:recall:logic-bug")], "2")
        self.assertEqual(t[("judge", "m1@high", "recall:logic-bug")], "0.50")
        self.assertEqual(t[("judge", "m1@high", "agreement")], "0.00")

    def test_a_grader_with_no_case_gets_no_row(self) -> None:
        self.case("judge", "k1", {"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]})
        (self.tmp / "set/reviewer").mkdir()
        reply = {"type": "result", "is_error": False, "total_cost_usd": 0,
                 "result": json.dumps({"verdict": "fail", "rows": {"correct": "fail"}})}
        for k in ("r1", "r2"):
            d = self.out / "m1" / k
            d.mkdir(parents=True)
            for g in ("judge", "reviewer"):
                (d / f"fingerprint-{g}.txt").write_text("model m1\n")
        (self.out / "m1/r1/judge-k1.json").write_text(json.dumps(reply))
        r = subprocess.run([sys.executable, str(ROOT / "bin/factory.d/eval_score.py"), str(self.tmp / "set"),
                            str(self.out)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        graders = {k[0] for k in self.table(r.stdout)}
        self.assertEqual(graders, {"judge"})
        self.assertEqual(self.table(r.stdout)[("judge", "m1", "infra")], "1")

    def test_a_bare_eval_out_root_scores_only_repeats_with_replies(self) -> None:
        self.case("judge", "k1", {"verdict": "fail", "defect_class": "logic-bug", "failing_rows": ["correct"]})
        self.case("reviewer", "k1", {"verdict": "merge"})
        reply = {"type": "result", "is_error": False, "total_cost_usd": 0,
                 "result": json.dumps({"verdict": "fail", "rows": {"correct": "fail"}})}
        (self.out / "m1/r1").mkdir(parents=True)
        (self.out / "m1/r2").mkdir(parents=True)
        (self.out / "m1/r1/judge-k1.json").write_text(json.dumps(reply))
        for k in ("r1", "r2"):  # the shared fingerprint names no grader, so it counts no repeat
            (self.out / "m1" / k / "fingerprint.txt").write_text("model m1\n")
        r = subprocess.run([sys.executable, str(ROOT / "bin/factory.d/eval_score.py"), str(self.tmp / "set"),
                            str(self.out)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.table(r.stdout)[("judge", "m1", "n:infra")], "1")
        self.assertNotIn("reviewer", {k[0] for k in self.table(r.stdout)})

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
