"""`bin/factory eval` grades a frozen case in the tree its round saw: the base commit its Diff heading names, with the
Diff applied and evals/ removed, not the checkout's HEAD, which has moved on since the case was frozen.

Sources bin/factory (FACTORY_SOURCED=1) against a small git repository standing in for the checkout, and runs the
real run_eval with a fake `claude` that records what the grader would read in its working directory.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
AGENTS = ROOT / "cultivation/marketplace/sam-cc-setup/agents"
FENCE = "~~~~~~~~~~~~ evidence"

FAKE_CLAUDE = """#!/usr/bin/env python3
import json, os, sys
sys.stdin.read()
seen = {"a": open("a.txt").read().strip(), "evals": os.path.exists("evals")}
with open(os.environ["SEEN_LOG"], "a") as f:
    f.write(json.dumps(seen) + "\\n")
reply = json.dumps({"verdict": "pass", "rows": {"correct": "pass", "verified": "pass", "honest": "pass"}, "fixes": []})
print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "result": reply}))
"""


def git(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


class EvalTreeTests(unittest.TestCase):
    def test_case_grades_in_its_base_tree_with_its_diff_applied(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        tmp = pathlib.Path(tmp_dir.name)
        repo = tmp / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "t@example.com")
        git(repo, "config", "user.name", "t")
        (repo / "a.txt").write_text("one\n")
        (repo / "evals/judge/old").mkdir(parents=True)
        (repo / "evals/judge/old/expected.json").write_text('{"verdict": "pass"}\n')
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", "base")
        base = git(repo, "rev-parse", "HEAD")
        (repo / "a.txt").write_text("three\n")
        git(repo, "commit", "-qam", "main moves on")
        diff = "\n".join([" a.txt | 2 +-", " 1 file changed, 1 insertion(+), 1 deletion(-)", "",
                          "diff --git a/a.txt b/a.txt", "index 5626abf..f719efd 100644", "--- a/a.txt", "+++ b/a.txt",
                          "@@ -1 +1 @@", "-one", "+two"])
        evals = tmp / "evals"
        for name, heading in (("c1-based", f"## Diff ({base[:8]}...HEAD)"), ("c2-headless", "## Diff (main...HEAD)")):
            case = evals / "judge" / name
            case.mkdir(parents=True)
            (case / "prompt.md").write_text(f"## Ticket\n\n{heading}\n\n{FENCE}\n{diff}\n{FENCE}\n")
            (case / "expected.json").write_text('{"verdict": "pass"}\n')
        fake = tmp / "bin/claude"
        fake.parent.mkdir()
        fake.write_text(FAKE_CLAUDE)
        fake.chmod(0o755)
        seen = tmp / "seen.jsonl"
        env = {k: v for k, v in os.environ.items() if k not in ("EVAL_EFFORT", "EVAL_OUT", "FACTORY_LEDGER")}
        env.update(PATH=f"{fake.parent}:{os.environ['PATH']}", SEEN_LOG=str(seen), FACTORY_SOURCED="1",
                   FACTORY_ROOT=str(repo))
        script = f"EVALS_DIR='{evals}'; GRADERS_DIR='{AGENTS}'; run_eval judge"
        proc = subprocess.run(["bash", "-c", '. "$0"\n' + script, "bin/factory"], cwd=ROOT, env=env,
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        got = [json.loads(line) for line in seen.read_text().splitlines()]
        # c1 names its base: the grader reads base plus the case's diff, not HEAD's "three"; c2 names none: HEAD.
        self.assertEqual(got, [{"a": "two", "evals": False}, {"a": "three", "evals": False}])


if __name__ == "__main__":
    unittest.main()
