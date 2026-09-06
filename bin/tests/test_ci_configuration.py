#!/usr/bin/env python3
"""Contract tests for bounded, reproducible CI dependency setup."""

from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
TEST_WORKFLOW = ROOT / ".github/workflows/test.yml"
RELEASE_WORKFLOW = ROOT / ".github/workflows/release.yml"
PYTHON_PINS = ROOT / ".github/ci/python-requirements.txt"
NPM_PINS = ROOT / ".github/ci/npm-packages.txt"


class CIConfigurationTest(unittest.TestCase):
    def workflow(self, path: pathlib.Path) -> str:
        self.assertTrue(path.is_file(), f"missing workflow: {path}")
        return path.read_text(encoding="utf-8")

    def pin_lines(self, path: pathlib.Path) -> list[str]:
        self.assertTrue(path.is_file(), f"missing dependency pin file: {path}")
        return path.read_text(encoding="utf-8").splitlines()

    def test_ci_dependency_versions_are_exact(self) -> None:
        self.assertEqual(
            ["copier==9.16.0", "ruff==0.15.20"],
            self.pin_lines(PYTHON_PINS),
        )
        self.assertEqual(
            [
                "@anthropic-ai/claude-code@2.1.258",
                "@openai/codex@0.153.2",
            ],
            self.pin_lines(NPM_PINS),
        )

    def test_pull_request_runs_cancel_only_obsolete_runs(self) -> None:
        workflow = self.workflow(TEST_WORKFLOW)

        self.assertIn("group: test-${{ github.event.pull_request.number }}", workflow)
        self.assertIn("cancel-in-progress: true", workflow)
        self.assertIn(
            "  verify:\n    runs-on: ubuntu-latest\n    timeout-minutes: 15",
            workflow,
        )
        self.assertNotIn("continue-on-error:", workflow)

    def test_release_runs_are_independent_and_time_bounded(self) -> None:
        workflow = self.workflow(RELEASE_WORKFLOW)

        self.assertNotIn("\nconcurrency:", workflow)
        self.assertNotIn("cancel-in-progress:", workflow)
        self.assertIn(
            "  release:\n    runs-on: ubuntu-latest\n    timeout-minutes: 15",
            workflow,
        )
        self.assertNotIn("continue-on-error:", workflow)

        gate = workflow.index("run: bin/verify-template.sh")
        publish = workflow.index("uses: softprops/action-gh-release@v2")
        self.assertLess(gate, publish)

    def test_workflows_use_pin_files_and_download_caches(self) -> None:
        python_setup = (
            "uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.12'\n"
            "          cache: 'pip'\n"
            "          cache-dependency-path: .github/ci/python-requirements.txt"
        )
        npm_cache = (
            "uses: actions/cache@v4\n"
            "        with:\n"
            "          path: ~/.npm\n"
            "          key: ${{ runner.os }}-npm-${{ "
            "hashFiles('.github/ci/npm-packages.txt') }}"
        )

        for path in (TEST_WORKFLOW, RELEASE_WORKFLOW):
            with self.subTest(path=path):
                workflow = self.workflow(path)
                self.assertIn(python_setup, workflow)
                self.assertIn(
                    "run: python3 -m pip install -r "
                    ".github/ci/python-requirements.txt",
                    workflow,
                )
                self.assertIn(npm_cache, workflow)
                self.assertIn(
                    "run: xargs npm install -g < .github/ci/npm-packages.txt",
                    workflow,
                )
                self.assertNotIn("pip install copier ruff", workflow)
                self.assertNotIn(
                    "npm install -g @anthropic-ai/claude-code @openai/codex",
                    workflow,
                )


if __name__ == "__main__":
    unittest.main()
