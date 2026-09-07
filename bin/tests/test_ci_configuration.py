#!/usr/bin/env python3
"""Contract tests for the two CI workflows and pinned deps."""

from __future__ import annotations

import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TEST = ROOT / ".github/workflows/test.yml"
RELEASE = ROOT / ".github/workflows/release.yml"
PY = ROOT / ".github/ci/python-requirements.txt"
NPM = ROOT / ".github/ci/npm-packages.txt"


class CIConfig(unittest.TestCase):
    def test_python_pins(self):
        self.assertEqual(
            ["copier==9.16.0", "ruff==0.15.20", "pytest==8.4.2", "pytest-xdist==3.8.0"],
            PY.read_text().split(),
        )

    def test_npm_pins(self):
        self.assertEqual(
            ["@anthropic-ai/claude-code@2.1.258", "@openai/codex@0.153.2"],
            NPM.read_text().split(),
        )

    def test_test_workflow_runs_check_on_push_and_pr(self):
        w = TEST.read_text()
        self.assertIn("push:", w)
        self.assertIn("pull_request:", w)
        self.assertIn("  verify:", w)  # job name = ruleset status context
        self.assertIn("run: bin/check", w)
        self.assertIn("run: python3 -m pip install -r .github/ci/python-requirements.txt", w)
        self.assertIn("cache-dependency-path: .github/ci/python-requirements.txt", w)
        self.assertNotIn("verify-template", w)

    def test_release_workflow_publishes_only(self):
        w = RELEASE.read_text()
        self.assertIn("tags:", w)
        self.assertIn("softprops/action-gh-release@v2", w)
        self.assertNotIn("verify-template", w)
        self.assertNotIn("bin/check", w)  # release does not re-run the gate


if __name__ == "__main__":
    unittest.main()
