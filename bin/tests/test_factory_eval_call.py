"""`bin/factory eval` replays the production grader call: the same flags and values, the budget aside (#505).

Sources bin/factory (FACTORY_SOURCED=1) and runs a real freeze and call_json, then the real run_eval, on a fixture user
tier (CLAUDE_CONFIG_DIR) with a fake `claude` on PATH that records its arguments, its environment and its settings,
so no model is called. Both grader calls disable user, project and local settings (`--setting-sources ''`) and read
the same settings bytes: role-settings.json with the read fence, plus the user tier's env without its account token
or config dir, never its hooks or allow rules. Each runs under a private config dir, since the fence still lets it read
CLAUDE.md, rules, skills, plugins, agents and commands, and gets the live user-tier token in its own environment, so a
retry after an account switch gets the new token and the supervisor keeps its own. model-eval regrades a Claude cell
when that user-tier file changes.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
TOKEN = "CLAUDE_CODE_OAUTH_TOKEN"  # by name, so no token assignment appears for the merge secret grep
# What the fence still lets a call read in its config dir (probed on Claude Code 2.1.312).
FENCE_ALLOWED = {"CLAUDE.md", "rules", "skills", "plugins", "agents", "commands"}

# Records each call; with FAKE_SWITCH (the user tier's settings file), the first -p call switches the user tier's
# token, as bin/claude-account does, and replies with no JSON, so call_json retries.
FAKE_CLAUDE = """#!/usr/bin/env python3
import json, os, shutil, sys
a = sys.argv[1:]
if "-p" not in a:
    print(os.environ.get("FAKE_VERSION", "2.1.312") + " (Claude Code)"); sys.exit(0)
sys.stdin.read()
d = os.path.join(os.environ["ARGS_DIR"], str(os.getpid()))
c = os.environ.get("CLAUDE_CONFIG_DIR", "")
json.dump({"argv": a, "token": os.environ.get("CLAUDE_CODE_OAUTH_TOKEN", ""), "cfg": c,
           "mode": os.stat(c).st_mode & 0o777 if os.path.isdir(c) else None,
           "ls": sorted(os.listdir(c)) if c and os.path.isdir(c) else None}, open(d + ".json", "w"))
shutil.copy(a[a.index("--settings") + 1], d + ".settings")
f = os.environ.get("FAKE_SWITCH", "")
if f and not os.path.exists(f + ".done"):
    open(f + ".done", "w").close()
    s = json.load(open(f)); s["env"]["CLAUDE_CODE_OAUTH_TOKEN"] = "fixture-token-2"; json.dump(s, open(f, "w"))
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": "not json"}))
    sys.exit(0)
r = json.dumps({"verdict": "pass", "rows": {"correct": "pass", "verified": "pass", "honest": "pass"}, "fixes": []})
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": r,
                  "modelUsage": {"m": {}}}))
"""

USER = {"env": {"FIXTURE_USER_ENV": "u", TOKEN: "fixture-token", "CLAUDE_CONFIG_DIR": "/operator/config",
                "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "0"}, "permissions": {"allow": ["Read(*)"]},
        "hooks": {"UserPromptSubmit": [{"hooks": [{"type": "command", "command": "true"}]}]}}


def flags(argv: list[str], settings: str) -> dict[str, str | None]:
    """{flag: value}; --settings maps to the file's text as the call read it, and the budget goes."""
    out: dict[str, str | None] = {}
    i = 0
    while i < len(argv):
        value = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("-") else None
        out[argv[i]] = value
        i += 1 if value is None else 2
    out["--settings"] = settings
    out.pop("--max-budget-usd", None)
    return out


class EvalCallTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.tmp = tmp = pathlib.Path(tmp_dir.name)
        fake = tmp / "bin/claude"
        fake.parent.mkdir()
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        # Observe env's argv too: Claude's argv alone misses a token passed by its launcher.
        self.wrapper_log = tmp / "env-argv.jsonl"
        wrapper = fake.parent / "env"
        wrapper.write_text("#!/usr/bin/env python3\nimport json, os, sys\n"
                           f"with open({str(self.wrapper_log)!r}, 'a') as f:\n"
                           "    f.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                           f"os.execv({shutil.which('env')!r}, ['env', *sys.argv[1:]])\n")
        wrapper.chmod(0o755)
        self.cfg = tmp / "cfg"
        (self.cfg / "rules").mkdir(parents=True)
        (self.cfg / "settings.json").write_text(json.dumps(USER))
        (self.cfg / "CLAUDE.md").write_text("operator memory\n")
        (self.cfg / "rules/r.md").write_text("operator rule\n")
        case = tmp / "evals/judge/c1"
        case.mkdir(parents=True)
        (case / "prompt.md").write_text("## Ticket\n")
        (case / "expected.json").write_text('{"verdict": "pass"}')
        env = {k: v for k, v in os.environ.items()
               if not k.startswith("FACTORY_") and k not in ("EVAL_EFFORT", "EVAL_OUT", "RUN", "LOG",
                                                            "CLAUDE_SETTINGS_FILE", "FAKE_SWITCH", "FAKE_VERSION", TOKEN)}
        env.update(PATH=f"{fake.parent}:{os.environ['PATH']}", FACTORY_ROOT=str(ROOT), CLAUDE_CONFIG_DIR=str(self.cfg),
                   FACTORY_RUNS_ROOT=str(tmp / "runs"))
        self.env = env

    def calls(self, args_dir: pathlib.Path) -> list[tuple[dict, str]]:
        """Each -p call's record and the settings text it read, in call order."""
        recs = sorted(args_dir.glob("*.json"), key=lambda p: p.stat().st_mtime_ns)
        calls = [(json.loads(p.read_text()), p.with_suffix(".settings").read_text()) for p in recs]
        for rec, _ in calls:
            self.assert_no_token_on_argv(rec["argv"])
        if self.wrapper_log.exists():
            for line in self.wrapper_log.read_text().splitlines():
                self.assert_no_token_on_argv(json.loads(line))
        return calls

    def assert_no_token_on_argv(self, argv: list[str]) -> None:
        for arg in argv:
            self.assertNotIn(TOKEN, arg)
            self.assertNotIn("fixture-token", arg)
            self.assertNotIn("launch-token", arg)

    def production(self, switch: bool, config_mode: int | None = None
                   ) -> tuple[subprocess.CompletedProcess[str], list[tuple[dict, str]], pathlib.Path]:
        """A real freeze and call_json on a fixture worktree; returns the calls and the run dir."""
        tmp = self.tmp
        run, main, wt, args = tmp / "run", tmp / "main", tmp / "wt", tmp / "pargs"
        for d in (run / "frozen", run / "tasks", run / "worker", args):
            d.mkdir(parents=True)
        if config_mode is not None:
            (run / "grader-config").mkdir()
            (run / "grader-config").chmod(config_mode)
        (run / "prompt.md").write_text("## Ticket\n")
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "init", "-q", "-b", "main", str(main)], check=True)
        subprocess.run([*git, "-C", str(main), "commit", "-q", "--allow-empty", "-m", "base"], check=True)
        subprocess.run(["git", "-C", str(main), "worktree", "add", "-q", "-b", "factory/t", str(wt)], check=True)
        script = (f"RUN='{run}'; WORKTREE='{wt}'; LOG=\"$RUN/factory.log\"; LEDGER=\"$RUN/ledger.jsonl\"; "
                  f"DAILY=\"$RUN/daily.jsonl\"; DECISIONS=\"$RUN/worker/decisions.md\"; GRADERS_DIR='{AGENTS}'; "
                  "IS_FILE=1; KEY=t; BODY=x\n"
                  'touch "$LEDGER" "$DAILY"; date -u +%s > "$RUN/launched"\n'
                  'freeze || exit 1\n'
                  'call_json 1 judge judge "$RUN/prompt.md" "$RUN/frozen/judge.schema.json" || exit 1\n'
                  f'echo "after:${{{TOKEN}-unset}}"; echo "grader_effort:$GRADER_EFFORT"')
        env = {**self.env, "ARGS_DIR": str(args), "FACTORY_SOURCED": "1", TOKEN: "launch-token"}
        if switch:
            env["FAKE_SWITCH"] = str(self.cfg / "settings.json")
        # $0 is bin/factory, as for `bin/factory eval`, so schema_for and the settings path resolve from bin/.
        proc = subprocess.run(["bash", "-c", '. "$0"\n' + script, "bin/factory"], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)
        self.assertIn("grader_effort:", proc.stdout, proc.stderr)
        return proc, self.calls(args), run

    def replay(self, switch: bool = False, version: str = "2.1.312"
               ) -> tuple[subprocess.CompletedProcess[str], list[tuple[dict, str]]]:
        args = self.tmp / "eargs"
        args.mkdir()
        env = {**self.env, "ARGS_DIR": str(args), "FAKE_VERSION": version}
        if switch:
            env["FAKE_SWITCH"] = str(self.cfg / "settings.json")
        proc = subprocess.run(["bin/factory", "eval", "judge", "--evals-dir", str(self.tmp / "evals")],
                              cwd=ROOT, env=env, capture_output=True, text=True, check=False)
        return proc, self.calls(args)

    def assert_fenced(self, rec: dict, settings: str) -> None:
        argv = rec["argv"]
        self.assertEqual(argv[argv.index("--setting-sources") + 1], "")
        # A config dir of the call's own, never the operator's, holding nothing the fence lets a call read.
        self.assertTrue(rec["cfg"])
        self.assertNotEqual(os.path.realpath(rec["cfg"]), os.path.realpath(self.cfg))
        self.assertIsNotNone(rec["ls"], "the grader config directory must exist at launch")
        self.assertEqual(rec["mode"], 0o700)
        self.assertEqual(set(rec["ls"]) & FENCE_ALLOWED, set())
        s = json.loads(settings)
        self.assertIs(s["permissions"]["blockReadsOutsideWorkingDirectories"], True)
        self.assertIn("Read(.env*)", s["permissions"]["deny"])
        self.assertNotIn("allow", s["permissions"])
        self.assertNotIn("hooks", s)
        self.assertNotIn("claudeMdExcludes", s)
        self.assertEqual(s["env"]["FIXTURE_USER_ENV"], "u")
        self.assertEqual(s["env"]["CLAUDE_CODE_DISABLE_AUTO_MEMORY"], "1")
        self.assertNotIn(TOKEN, s["env"])
        self.assertNotIn("CLAUDE_CONFIG_DIR", s["env"])

    def test_eval_makes_the_production_grader_call(self) -> None:
        proc, production, run = self.production(switch=False)
        replay_proc, replay = self.replay()
        self.assertEqual(replay_proc.returncode, 0, replay_proc.stdout + replay_proc.stderr)
        self.assertEqual(len(production), 1, proc.stderr)
        self.assertEqual(len(replay), 1)
        frozen = run / "frozen/role-settings.json"
        self.assertEqual(frozen.stat().st_mode & 0o077, 0)  # it holds the user tier's env, which may hold a secret
        self.assertEqual(production[0][1], frozen.read_text())
        for rec, settings in (production[0], replay[0]):
            self.assert_fenced(rec, settings)
            self.assertEqual(rec["token"], "fixture-token")
        grader_effort = proc.stdout.rsplit("grader_effort:", 1)[1].strip()
        prod, rep = (flags(rec["argv"], settings) for rec, settings in (production[0], replay[0]))
        self.assertEqual(prod["--effort"], grader_effort)
        differ = sorted(k for k in prod.keys() | rep.keys() if rep.get(k) != prod.get(k))
        self.assertEqual(differ, [], f"run_eval's flags that differ from call_json's; effort "
                                     f"{rep.get('--effort')} against GRADER_EFFORT {grader_effort}")

    def test_a_retry_gets_the_token_switched_in_after_the_first_attempt(self) -> None:
        proc, production, run = self.production(switch=True)
        self.assertEqual([rec["token"] for rec, _ in production], ["fixture-token", "fixture-token-2"], proc.stderr)
        self.assertEqual(json.loads((run / "round-1.judge.json").read_text())["verdict"], "pass")
        self.assertIn("after:launch-token", proc.stdout)  # the supervisor's own token is left alone
        for rec, settings in production:
            self.assert_fenced(rec, settings)

    def test_eval_retry_gets_the_token_switched_in_after_the_first_attempt(self) -> None:
        proc, replay = self.replay(switch=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual([rec["token"] for rec, _ in replay], ["fixture-token", "fixture-token-2"])
        for rec, settings in replay:
            self.assert_fenced(rec, settings)

    def test_eval_refuses_an_unsupported_claude_before_any_grader_call(self) -> None:
        proc, replay = self.replay(version="2.1.256")
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("the factory needs Claude Code 2.1.257+", proc.stderr)
        self.assertEqual(replay, [])

    def test_production_repairs_an_existing_config_directory_mode(self) -> None:
        proc, production, _ = self.production(switch=False, config_mode=0o755)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(len(production), 1)
        self.assert_fenced(*production[0])

    def test_model_eval_regrades_when_the_user_tier_changes(self) -> None:
        args, home = self.tmp / "margs", self.tmp / "home"
        args.mkdir()
        home.mkdir()
        env = {**self.env, "HOME": str(home), "ARGS_DIR": str(args), "MODEL_EVAL_OUT": str(self.tmp / "mout"),
               "MODEL_EVAL_SET": str(self.tmp / "evals"), "MODEL_EVAL_GRADERS": "judge", "MODEL_EVAL_REPEATS": "1"}

        def model_eval() -> None:
            subprocess.run(["bin/factory.d/model-eval", "m"], cwd=ROOT, env=env, capture_output=True, text=True,
                           check=False)

        model_eval()
        self.assertEqual(len(list((self.tmp / "mout").rglob("*.key"))), 1)
        model_eval()
        self.assertEqual(len(self.calls(args)), 1)  # unchanged: the keyed reply is reused
        user = json.loads((self.cfg / "settings.json").read_text())
        user["env"]["FIXTURE_USER_ENV"] = "u2"
        (self.cfg / "settings.json").write_text(json.dumps(user))
        model_eval()
        self.assertEqual(len(self.calls(args)), 2)


if __name__ == "__main__":
    unittest.main()
