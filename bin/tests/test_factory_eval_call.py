"""`bin/factory eval` replays the production grader call: the same flags and values, the budget aside.

Sources bin/factory (FACTORY_SOURCED=1) and runs the real call_json, then the real run_eval, with a fake `claude`
on PATH that records its arguments, so no model is called.
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

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, os, sys
sys.stdin.read()
with open(os.environ["ARGS_LOG"], "a") as f:
    f.write(json.dumps(sys.argv[1:]) + "\\n")
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


class EvalCallTests(unittest.TestCase):
    def test_eval_makes_the_production_grader_call(self) -> None:
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
        shutil.copy(ROOT / "bin/factory.d/judge.schema.json", run / "frozen/judge.schema.json")
        (run / "prompt.md").write_text("## Ticket\n")
        case = tmp / "evals/judge/c1"
        case.mkdir(parents=True)
        (case / "prompt.md").write_text("## Ticket\n")
        (case / "expected.json").write_text('{"verdict": "pass"}')
        log = tmp / "args.jsonl"
        script = (f"RUN='{run}'; WORKTREE='{run}'; LEDGER=\"$RUN/ledger.jsonl\"; DAILY=\"$RUN/daily.jsonl\"; KEY=t\n"
                  'touch "$LEDGER" "$DAILY"; date -u +%s > "$RUN/launched"\n'
                  'call_json 1 judge judge "$RUN/prompt.md" "$RUN/frozen/judge.schema.json" || exit 1\n'
                  f"EVALS_DIR='{tmp / 'evals'}'; GRADERS_DIR='{AGENTS}'; run_eval judge\n"
                  'echo "grader_effort:$GRADER_EFFORT"')
        env = {k: v for k, v in os.environ.items() if k not in ("EVAL_EFFORT", "FACTORY_GRADER_MODEL")}
        env.update(PATH=f"{fake.parent}:{os.environ['PATH']}", ARGS_LOG=str(log), FACTORY_SOURCED="1",
                   FACTORY_RUNS_ROOT=str(tmp / "runs"))
        # $0 is bin/factory, as for `bin/factory eval`, so schema_for and the settings path resolve from bin/.
        proc = subprocess.run(["bash", "-c", '. "$0"\n' + script, "bin/factory"], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)
        self.assertIn("grader_effort:", proc.stdout, proc.stderr)
        grader_effort = proc.stdout.rsplit("grader_effort:", 1)[1].strip()
        production, replay = (flags(json.loads(x)) for x in log.read_text().splitlines())
        self.assertEqual(production["--effort"], grader_effort)
        differ = sorted(k for k in production.keys() | replay.keys() if replay.get(k) != production.get(k))
        self.assertEqual(differ, [], f"run_eval's flags that differ from call_json's; effort "
                                     f"{replay.get('--effort')} against GRADER_EFFORT {grader_effort}")


if __name__ == "__main__":
    unittest.main()
