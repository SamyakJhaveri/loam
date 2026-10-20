"""Each judge backlog item files exactly one needs-triage issue, even when its text spans several lines.

`bin/factory` is sourced (FACTORY_SOURCED=1) and file_backlog is called directly. FACTORY_GH points at a
fake `gh` that records its arguments and body. No network.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PR_URL = "https://github.com/acme/widget/pull/9"

FAKE_GH = """#!/usr/bin/env python3
import json, sys
with open(%r, "a") as f:
    f.write(json.dumps({"args": sys.argv[1:], "body": sys.stdin.read()}) + "\\n")
"""


class FileBacklogTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.run_dir = pathlib.Path(tmp.name)
        self.gh_log = self.run_dir / "gh-calls.jsonl"
        self.gh = self.run_dir / "gh"
        self.gh.write_text(FAKE_GH % str(self.gh_log))
        self.gh.chmod(0o755)

    def file_backlog(self, backlog: list[str]) -> list[dict]:
        """Run file_backlog on a judge reply holding `backlog`; return the gh issue-create calls."""
        judge = self.run_dir / "round-1.judge.json"
        judge.write_text(json.dumps({"verdict": "pass", "rows": {}, "backlog": backlog}))
        proc = subprocess.run(
            ["bash", "-c", f". bin/factory\nfile_backlog '{judge}' 7 '{PR_URL}'"],
            cwd=ROOT, capture_output=True, text=True, check=False,
            env={**os.environ, "FACTORY_SOURCED": "1", "FACTORY_GH": str(self.gh), "REPO": "acme/widget",
                 "RUN": str(self.run_dir), "LOG": str(self.run_dir / "factory.log")},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        calls = [json.loads(x) for x in self.gh_log.read_text().splitlines()] if self.gh_log.exists() else []
        return [c for c in calls if c["args"][:2] == ["issue", "create"]]

    def title(self, call: dict) -> str:
        return call["args"][call["args"].index("--title") + 1]

    def test_multi_line_item_files_one_issue(self) -> None:
        issues = self.file_backlog(["Widget leaks a handle.  \n\n  Close it in teardown.", "Rename foo."])
        self.assertEqual([self.title(c) for c in issues], ["Widget leaks a handle. Close it in teardown.", "Rename foo."])
        self.assertIn("\n\nWidget leaks a handle. Close it in teardown.\n", issues[0]["body"])

    def test_multi_line_item_is_filed_once_per_run(self) -> None:
        item = ["Widget leaks a handle.\nClose it in teardown."]
        self.assertEqual(len(self.file_backlog(item)), 1)
        self.assertEqual(len(self.file_backlog(item)), 1)  # the second call files nothing new


if __name__ == "__main__":
    unittest.main()
