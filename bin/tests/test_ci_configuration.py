#!/usr/bin/env python3
"""Contract tests for the two CI workflows."""

from __future__ import annotations

import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TEST = ROOT / ".github/workflows/test.yml"
RELEASE = ROOT / ".github/workflows/release.yml"


class CIConfig(unittest.TestCase):
    def test_test_workflow_runs_check_on_push_and_pr(self):
        w = TEST.read_text()
        self.assertIn("push:\n    branches: [main]", w)
        self.assertIn("pull_request:\n    branches: [main]", w)
        self.assertIn("  verify:", w)  # job id = a status check main's ruleset requires
        # Exact step block: a commented-out or renamed step must fail here.
        self.assertIn("- name: Run check\n        run: bin/check", w)
        self.assertIn("run: python3 -m pip install -r .github/ci/python-requirements.txt", w)
        self.assertIn("cache-dependency-path: .github/ci/python-requirements.txt", w)
        # bin/check is the only repo script CI runs: no retired checker may come back.
        self.assertEqual(1, w.count("run: bin/"))

    def test_verify_job_has_no_inert_gate(self):
        """An `if:` or `continue-on-error:` in the verify job would make check advisory."""
        w = TEST.read_text()
        job = w[w.index("  verify:"):w.index("  stub-sweep:")]
        self.assertNotIn("continue-on-error:", job)
        self.assertNotIn("if:", job)

    def test_verify_job_fetches_main(self):
        """bin/plugin_versions.py diffs against origin/main; a shallow checkout would skip its bump rule."""
        w = TEST.read_text()
        job = w[w.index("  verify:"):w.index("  stub-sweep:")]
        self.assertIn("- uses: actions/checkout@v4\n        with:\n          fetch-depth: 0", job)

    def test_stub_sweep_job_runs_the_sweep(self):
        """verify-loam's stub sweep runs on every push and PR; a dropped step or a gate would let a break pass."""
        w = TEST.read_text()
        job = w[w.index("  stub-sweep:"):w.index("  factory-macos:")]
        self.assertIn("- name: Run verify-loam stub sweep\n        run: .claude/skills/verify-loam/control-loam sweep", job)
        self.assertNotIn("continue-on-error:", job)
        self.assertNotIn("if:", job)

    def test_release_workflow_publishes_only(self):
        w = RELEASE.read_text()
        self.assertIn("tags:", w)
        self.assertIn("softprops/action-gh-release@v2", w)
        self.assertNotIn("run: bin/", w)  # release runs no repo script
        self.assertNotIn("bin/check", w)  # release does not re-run the gate


if __name__ == "__main__":
    unittest.main()
