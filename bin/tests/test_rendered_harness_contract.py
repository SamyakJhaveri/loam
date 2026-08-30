from __future__ import annotations

import contextlib
import io
import pathlib
import stat
import sys
import tempfile
import unittest


BIN_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN_DIR))

import rendered_harness_contract as contract


REQUIRED_SOURCE_PATHS = (
    "copier.yml",
    "bin/verify-template.sh",
    "bin/rendered_harness_contract.py",
    "bin/tests/test_rendered_harness_contract.py",
    ".github/workflows/test.yml",
    ".github/workflows/release.yml",
    "bin/release.sh",
)

REQUIRED_RENDERED_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agents/skills/catchup/SKILL.md",
    ".claude/settings.json",
    ".claude/settings.local.json.template",
    ".claude/hooks/bash-audit-log.sh",
    ".claude/hooks/concurrent-checkout-guard.sh",
    ".claude/hooks/ruff-after-edit.sh",
    ".claude/hooks/stop-verify-gate.sh",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/hooks/pre-tool-policy.py",
    ".codex/rules/default.rules",
)

FORBIDDEN_RENDERED_PATHS = (
    ".mcp.json",
    ".claude/agents",
    ".claude/rules",
    ".claude/hooks/post-compact-recovery.sh",
    ".claude/skills/reassess-template-sync",
    ".agents/skills/agent-team",
    ".codex/reassess-hooks.json",
    ".codex/agents",
    ".codex/mcp",
    "_research",
)


class RenderedHarnessContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        root = pathlib.Path(self.temp_dir.name)
        self.source = root / "source"
        self.rendered = root / "rendered"
        self.source.mkdir()
        self.rendered.mkdir()

    def write(
        self,
        root: pathlib.Path,
        relative_path: str,
        content: str = "fixture\n",
    ) -> pathlib.Path:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def make_executable(self, path: pathlib.Path) -> None:
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def build_good_fixture(self) -> None:
        source_contents = {
            ".github/workflows/test.yml": "run: bin/verify-template.sh\n",
            ".github/workflows/release.yml": (
                "run: bin/verify-template.sh\n"
                "uses: softprops/action-gh-release@v2\n"
            ),
            "bin/release.sh": (
                'bash "$SELF_DIR/verify-template.sh"\n'
                'echo "$VERSION" > VERSION\n'
            ),
        }
        for relative_path in REQUIRED_SOURCE_PATHS:
            path = self.write(
                self.source,
                relative_path,
                source_contents.get(relative_path, "fixture\n"),
            )
            if relative_path.endswith(".sh"):
                self.make_executable(path)

        for relative_path in REQUIRED_RENDERED_PATHS:
            path = self.write(self.rendered, relative_path)
            if "/hooks/" in relative_path:
                self.make_executable(path)

        catchup_link = self.rendered / ".claude/skills/catchup"
        catchup_link.parent.mkdir(parents=True, exist_ok=True)
        catchup_link.symlink_to("../../.agents/skills/catchup", target_is_directory=True)

    def rendered_violations(self) -> tuple[str, ...]:
        return tuple(
            violation.render()
            for violation in contract.verify_contract(self.source, self.rendered)
        )

    def test_known_good_fixture_has_no_violations(self) -> None:
        self.build_good_fixture()

        self.assertEqual((), contract.verify_contract(self.source, self.rendered))

    def test_missing_required_rendered_paths_are_reported(self) -> None:
        self.build_good_fixture()
        missing = ".codex/hooks.json"
        (self.rendered / missing).unlink()

        rendered = self.rendered_violations()

        self.assertTrue(any("FAIL [topology]" in item for item in rendered))
        self.assertTrue(any(missing in item for item in rendered))

    def test_missing_required_source_paths_are_reported(self) -> None:
        self.build_good_fixture()
        missing = "copier.yml"
        (self.source / missing).unlink()

        rendered = self.rendered_violations()

        self.assertTrue(any("FAIL [topology]" in item for item in rendered))
        self.assertTrue(any(missing in item for item in rendered))

    def test_forbidden_rendered_paths_are_reported(self) -> None:
        self.build_good_fixture()
        forbidden = ".claude/rules"
        (self.rendered / forbidden).mkdir(parents=True)

        rendered = self.rendered_violations()

        self.assertTrue(any("FAIL [topology]" in item for item in rendered))
        self.assertTrue(any(forbidden in item for item in rendered))

    def test_multiple_areas_are_reported_in_one_run(self) -> None:
        self.build_good_fixture()
        (self.rendered / "AGENTS.md").unlink()
        self.write(
            self.source,
            ".github/workflows/test.yml",
            "run: a-different-command\n",
        )

        violations = contract.verify_contract(self.source, self.rendered)

        self.assertEqual({"release-callers", "topology"}, {v.area for v in violations})

    def test_pull_request_workflow_calls_public_gate(self) -> None:
        self.build_good_fixture()
        workflow = ".github/workflows/test.yml"
        self.write(self.source, workflow, "run: a-different-command\n")

        rendered = self.rendered_violations()

        self.assertTrue(any(workflow in item for item in rendered))
        self.assertTrue(any("bin/verify-template.sh" in item for item in rendered))

    def test_release_workflow_runs_gate_before_publish(self) -> None:
        self.build_good_fixture()
        workflow = ".github/workflows/release.yml"
        self.write(
            self.source,
            workflow,
            "uses: softprops/action-gh-release@v2\n"
            "run: bin/verify-template.sh\n",
        )

        rendered = self.rendered_violations()

        self.assertTrue(any(workflow in item for item in rendered))
        self.assertTrue(any("before" in item for item in rendered))

    def test_release_script_runs_gate_before_version_write(self) -> None:
        self.build_good_fixture()
        release_script = "bin/release.sh"
        self.write(
            self.source,
            release_script,
            'echo "$VERSION" > VERSION\n'
            'bash "$SELF_DIR/verify-template.sh"\n',
        )

        rendered = self.rendered_violations()

        self.assertTrue(any(release_script in item for item in rendered))
        self.assertTrue(any("before" in item for item in rendered))

    def test_release_caller_failures_accumulate(self) -> None:
        self.build_good_fixture()
        self.write(self.source, ".github/workflows/test.yml", "missing gate\n")
        self.write(self.source, ".github/workflows/release.yml", "missing markers\n")
        self.write(self.source, "bin/release.sh", "missing markers\n")

        failures = [
            violation
            for violation in contract.verify_contract(self.source, self.rendered)
            if violation.area == "release-callers"
        ]

        self.assertEqual(3, len(failures))
        self.assertEqual(
            {
                ".github/workflows/test.yml",
                ".github/workflows/release.yml",
                "bin/release.sh",
            },
            {
                path
                for path in (
                    ".github/workflows/test.yml",
                    ".github/workflows/release.yml",
                    "bin/release.sh",
                )
                if any(path in violation.detail for violation in failures)
            },
        )

    def test_cli_prints_violations_and_returns_nonzero(self) -> None:
        self.build_good_fixture()
        missing = ".codex/config.toml"
        (self.rendered / missing).unlink()
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            exit_code = contract.main(
                [
                    "--source-root",
                    str(self.source),
                    "--rendered-root",
                    str(self.rendered),
                ]
            )

        self.assertEqual(1, exit_code)
        self.assertIn("FAIL [topology]", output.getvalue())
        self.assertIn(missing, output.getvalue())


if __name__ == "__main__":
    unittest.main()
