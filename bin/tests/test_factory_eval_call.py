"""`bin/factory eval` replays the production grader call: the same flags and values, the budget aside.

Sources bin/factory (FACTORY_SOURCED=1) and runs the real call_json, then the real run_eval, with a fake `claude`
on PATH that records its arguments, so no model is called; once for the judge, at high, and once for the
reviewer, at xhigh (Samyak 2026-10-30). `bin/factory graders-check` holds each grader file to its own role's effort.
"""

from __future__ import annotations

import json
import os
import re
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, os, sys
sys.stdin.read()
with open(os.environ["ARGS_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
schema = sys.argv[sys.argv.index("--json-schema") + 1]
if "findings" in schema:
    reply = json.dumps({"verdict": "merge", "findings": []})
else:
    reply = json.dumps({"verdict": "pass", "rows": {"correct": "pass", "verified": "pass", "honest": "pass"}, "fixes": []})
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": reply}))
"""


def flags(argv: list[str]) -> dict[str, str | None]:
    """{flag: value}; --settings maps to the file's text, since the loop reads a frozen copy, and the budget goes."""
    out: dict[str, str | None] = {}
    i = 0
    while i < len(argv):
        value = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("-") else None
        out[argv[i]] = value
        i += 1 if value is None else 2
    if out.get("--settings"):
        out["--settings"] = pathlib.Path(out["--settings"]).read_text()
    out.pop("--max-budget-usd", None)
    return out


# call_json's stem for each role, as run_judge and run_review pass it; the expected verdict each eval case keeps.
ROLES = {"judge": ("judge", "high", "pass"), "reviewer": ("review", "xhigh", "merge")}


class EvalCallTests(unittest.TestCase):
    def call_args(self, role: str) -> tuple[dict[str, str | None], dict[str, str | None]]:
        """The flags of call_json's call for role, then of run_eval's replay of it."""
        stem, _, verdict = ROLES[role]
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = pathlib.Path(tmp_dir.name)
        fake = tmp / "bin/claude"
        fake.parent.mkdir()
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        run = tmp / "run"
        (run / "frozen").mkdir(parents=True)
        # freeze's copies of the two files the loop's call reads.
        shutil.copy(ROOT / "bin/factory.d/role-settings.json", run / "frozen/role-settings.json")
        shutil.copy(ROOT / f"bin/factory.d/{role}.schema.json", run / f"frozen/{role}.schema.json")
        (run / "prompt.md").write_text("## Ticket\n")
        case = tmp / f"evals/{role}/c1"
        case.mkdir(parents=True)
        (case / "prompt.md").write_text("## Ticket\n")
        (case / "expected.json").write_text(json.dumps({"verdict": verdict}))
        log = tmp / "args.jsonl"
        # IS_FILE=1 keeps notify from alerting if a call path ever reaches finish.
        script = (f"IS_FILE=1; RUN='{run}'; WORKTREE='{run}'; LEDGER=\"$RUN/ledger.jsonl\"; DAILY=\"$RUN/daily.jsonl\"; KEY=t\n"
                  'touch "$LEDGER" "$DAILY"; date -u +%s > "$RUN/launched"\n'
                  f'call_json 1 {stem} {role} "$RUN/prompt.md" "$RUN/frozen/{role}.schema.json" || exit 1\n'
                  f"EVALS_DIR='{tmp / 'evals'}'; GRADERS_DIR='{AGENTS}'; run_eval {role}\n")
        env = {k: v for k, v in os.environ.items() if k not in ("EVAL_EFFORT", "FACTORY_GRADER_MODEL")}
        env.update(PATH=f"{fake.parent}:{os.environ['PATH']}", ARGS_LOG=str(log), FACTORY_SOURCED="1",
                   FACTORY_RUNS_ROOT=str(tmp / "runs"))
        # $0 is bin/factory, as for `bin/factory eval`, so schema_for and the settings path resolve from bin/.
        proc = subprocess.run(["bash", "-c", '. "$0"\n' + script, "bin/factory"], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)
        lines = log.read_text().splitlines() if log.exists() else []
        self.assertEqual(len(lines), 2, proc.stdout + proc.stderr)
        production, replay = (flags(json.loads(x)) for x in lines)
        return production, replay

    def test_eval_makes_the_production_grader_call(self) -> None:
        for role, (_, effort, _) in ROLES.items():
            with self.subTest(role=role):
                production, replay = self.call_args(role)
                self.assertEqual(production["--effort"], effort, f"the loop's {role} call")
                differ = sorted(k for k in production.keys() | replay.keys() if replay.get(k) != production.get(k))
                self.assertEqual(differ, [], f"run_eval's flags that differ from call_json's for the {role}; effort "
                                             f"{replay.get('--effort')} against {production.get('--effort')}")


class GradersCheckTests(unittest.TestCase):
    def check(self, efforts: dict[str, str]) -> subprocess.CompletedProcess[str]:
        """graders-check over copies of the checkout's grader files, with each named role's effort set."""
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        agents = pathlib.Path(tmp_dir.name)
        for role in ROLES:
            text = (AGENTS / f"{role}.md").read_text()
            if role in efforts:
                text = re.sub(r"(?m)^effort: .*$", f"effort: {efforts[role]}", text, count=1)
            (agents / f"{role}.md").write_text(text)
        env = {k: v for k, v in os.environ.items() if k != "FACTORY_GRADER_MODEL"}
        return subprocess.run(["bin/factory", "graders-check", "--agents-dir", str(agents)], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)

    def test_checkout_files_pass(self) -> None:
        proc = self.check({})
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_each_file_is_held_to_its_own_roles_effort(self) -> None:
        # Each file at the other role's effort: only that file drifts.
        for role, other in (("reviewer", "judge"), ("judge", "reviewer")):
            with self.subTest(role=role):
                proc = self.check({role: ROLES[other][1]})
                self.assertNotEqual(proc.returncode, 0, proc.stdout)
                self.assertIn(f"DRIFT {role}", proc.stdout)
                self.assertNotIn(f"DRIFT {other}", proc.stdout)


if __name__ == "__main__":
    unittest.main()
