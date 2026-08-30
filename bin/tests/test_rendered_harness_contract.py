from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest


BIN_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BIN_DIR))

import rendered_harness_contract as contract  # noqa: E402


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

CLAUDE_HOOK_PATHS = (
    ".claude/hooks/bash-audit-log.sh",
    ".claude/hooks/concurrent-checkout-guard.sh",
    ".claude/hooks/ruff-after-edit.sh",
    ".claude/hooks/stop-verify-gate.sh",
)

GOOD_CLAUDE_SETTINGS = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": ".claude/hooks/bash-audit-log.sh",
                    }
                ],
            },
            {
                "matcher": "Bash|Edit|Write",
                "hooks": [
                    {
                        "type": "command",
                        "command": ".claude/hooks/concurrent-checkout-guard.sh",
                    }
                ],
            },
        ],
        "PostToolUse": [
            {
                "matcher": "Edit|Write",
                "hooks": [
                    {
                        "type": "command",
                        "command": ".claude/hooks/ruff-after-edit.sh",
                    }
                ],
            }
        ],
        "Stop": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": ".claude/hooks/stop-verify-gate.sh",
                    }
                ]
            }
        ],
    }
}

GOOD_CLAUDE_PROSE = """# CLAUDE.md

@AGENTS.md

- Stop hook: `.claude/hooks/stop-verify-gate.sh`.
- `/catchup` lives in `.agents/skills/`.
- Hooks: `bash-audit-log.sh`, `concurrent-checkout-guard.sh`, and `ruff-after-edit.sh`.

| Resource | Use when |
| --- | --- |
| `/plan-review <path>` (sam-cc-setup plugin, if installed) | Reviewing a plan |
| `scaffold-context` skill (sam-cc-setup plugin, if installed) | Writing context |
"""

GOOD_AGENT_PROSE = """# AGENTS.md

The `.codex/` layer contains Codex configuration.
Codex-side skills live in `.agents/skills/`.
"""

GOOD_RUFF_ADAPTER = (
    "python3 -c '\n"
    "payload = {}\n"
    'tool_input = payload.get("tool_input")\n'
    'file_path = tool_input.get("file_path")'
    "\n' 2>/dev/null\n"
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
            ".github/workflows/test.yml": (
                "jobs:\n"
                "  verify:\n"
                "    steps:\n"
                "      - run: bin/verify-template.sh\n"
            ),
            ".github/workflows/release.yml": (
                "jobs:\n"
                "  release:\n"
                "    steps:\n"
                "      - run: bin/verify-template.sh\n"
                "      - uses: softprops/action-gh-release@v2\n"
            ),
            "bin/release.sh": (
                'bash "$SELF_DIR/verify-template.sh" || die "verification failed"\n'
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
        self.write(
            self.source,
            "seed/.claude/hooks/ruff-after-edit.sh",
            GOOD_RUFF_ADAPTER,
        )

        rendered_contents = {
            "AGENTS.md": GOOD_AGENT_PROSE,
            "CLAUDE.md": GOOD_CLAUDE_PROSE,
            ".claude/settings.json": json.dumps(GOOD_CLAUDE_SETTINGS),
            ".claude/hooks/ruff-after-edit.sh": GOOD_RUFF_ADAPTER,
        }
        for relative_path in REQUIRED_RENDERED_PATHS:
            path = self.write(
                self.rendered,
                relative_path,
                rendered_contents.get(relative_path, "fixture\n"),
            )
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
            "jobs:\n"
            "  verify:\n"
            "    steps:\n"
            "      - run: a-different-command\n",
        )

        violations = contract.verify_contract(self.source, self.rendered)

        self.assertEqual(
            {"prose-routes", "release-callers", "topology"},
            {v.area for v in violations},
        )

    def test_pull_request_workflow_calls_public_gate(self) -> None:
        self.build_good_fixture()
        workflow = ".github/workflows/test.yml"
        self.write(
            self.source,
            workflow,
            "jobs:\n"
            "  verify:\n"
            "    steps:\n"
            "      - run: a-different-command\n",
        )

        rendered = self.rendered_violations()

        self.assertTrue(any(workflow in item for item in rendered))
        self.assertTrue(any("bin/verify-template.sh" in item for item in rendered))

    def test_release_workflow_runs_gate_before_publish(self) -> None:
        self.build_good_fixture()
        workflow = ".github/workflows/release.yml"
        self.write(
            self.source,
            workflow,
            "jobs:\n"
            "  release:\n"
            "    steps:\n"
            "      - uses: softprops/action-gh-release@v2\n"
            "      - run: bin/verify-template.sh\n",
        )

        rendered = self.rendered_violations()

        self.assertTrue(any(workflow in item for item in rendered))
        self.assertTrue(any("before" in item for item in rendered))

    def test_commented_workflow_gate_is_inert(self) -> None:
        self.build_good_fixture()
        workflow = ".github/workflows/release.yml"
        self.write(
            self.source,
            workflow,
            "jobs:\n"
            "  release:\n"
            "    steps:\n"
            "      # - run: bin/verify-template.sh\n"
            "      - uses: softprops/action-gh-release@v2\n",
        )

        self.assertIn(
            "FAIL [release-callers]: .github/workflows/release.yml must call "
            "bin/verify-template.sh",
            self.rendered_violations(),
        )

    def test_echoed_workflow_gate_is_inert(self) -> None:
        self.build_good_fixture()
        workflow = ".github/workflows/release.yml"
        self.write(
            self.source,
            workflow,
            "jobs:\n"
            "  release:\n"
            "    steps:\n"
            "      - run: echo bin/verify-template.sh\n"
            "      - uses: softprops/action-gh-release@v2\n",
        )

        self.assertIn(
            "FAIL [release-callers]: .github/workflows/release.yml must call "
            "bin/verify-template.sh",
            self.rendered_violations(),
        )

    def test_inert_workflow_duplicate_does_not_hide_late_gate(self) -> None:
        self.build_good_fixture()
        workflow = ".github/workflows/release.yml"
        self.write(
            self.source,
            workflow,
            "jobs:\n"
            "  release:\n"
            "    steps:\n"
            "      - run: echo bin/verify-template.sh\n"
            "      - uses: softprops/action-gh-release@v2\n"
            "      - run: bin/verify-template.sh\n",
        )

        self.assertIn(
            "FAIL [release-callers]: .github/workflows/release.yml must run "
            "bin/verify-template.sh before softprops/action-gh-release",
            self.rendered_violations(),
        )

    def test_workflow_env_run_is_inert(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            ".github/workflows/release.yml",
            "jobs:\n"
            "  release:\n"
            "    steps:\n"
            "      - name: Inert environment value\n"
            "        env:\n"
            "          run: bin/verify-template.sh\n"
            "      - uses: softprops/action-gh-release@v2\n"
            "      - run: bin/verify-template.sh\n",
        )

        self.assertIn(
            "FAIL [release-callers]: .github/workflows/release.yml must run "
            "bin/verify-template.sh before softprops/action-gh-release",
            self.rendered_violations(),
        )

    def test_workflow_env_uses_is_inert(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            ".github/workflows/release.yml",
            "jobs:\n"
            "  release:\n"
            "    steps:\n"
            "      - name: Inert environment value\n"
            "        env:\n"
            "          uses: softprops/action-gh-release@v2\n"
            "      - run: bin/verify-template.sh\n"
            "      - uses: softprops/action-gh-release@v2\n",
        )

        self.assertEqual((), contract.verify_contract(self.source, self.rendered))

    def test_workflow_gate_cannot_suppress_failure(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            ".github/workflows/release.yml",
            "jobs:\n"
            "  release:\n"
            "    steps:\n"
            "      - run: bin/verify-template.sh || true\n"
            "      - uses: softprops/action-gh-release@v2\n",
        )

        self.assertIn(
            "FAIL [release-callers]: .github/workflows/release.yml must call "
            "bin/verify-template.sh",
            self.rendered_violations(),
        )

    def test_release_script_runs_gate_before_version_write(self) -> None:
        self.build_good_fixture()
        release_script = "bin/release.sh"
        self.write(
            self.source,
            release_script,
            'echo "$VERSION" > VERSION\n'
            'bash "$SELF_DIR/verify-template.sh" || die "verification failed"\n',
        )

        rendered = self.rendered_violations()

        self.assertTrue(any(release_script in item for item in rendered))
        self.assertTrue(any("before" in item for item in rendered))

    def test_commented_release_script_gate_is_inert(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "bin/release.sh",
            '# bash "$SELF_DIR/verify-template.sh"\n'
            'echo "$VERSION" > VERSION\n',
        )

        self.assertIn(
            'FAIL [release-callers]: bin/release.sh must call bash '
            '"$SELF_DIR/verify-template.sh"',
            self.rendered_violations(),
        )

    def test_echoed_release_script_gate_is_inert(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "bin/release.sh",
            "echo 'bash \"$SELF_DIR/verify-template.sh\"'\n"
            'echo "$VERSION" > VERSION\n',
        )

        self.assertIn(
            'FAIL [release-callers]: bin/release.sh must call bash '
            '"$SELF_DIR/verify-template.sh"',
            self.rendered_violations(),
        )

    def test_inert_release_script_duplicate_does_not_hide_late_gate(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "bin/release.sh",
            "echo 'bash \"$SELF_DIR/verify-template.sh\"'\n"
            'echo "$VERSION" > VERSION\n'
            'bash "$SELF_DIR/verify-template.sh" || die "verification failed"\n',
        )

        self.assertIn(
            'FAIL [release-callers]: bin/release.sh must run bash '
            '"$SELF_DIR/verify-template.sh" before echo "$VERSION" > VERSION',
            self.rendered_violations(),
        )

    def test_release_script_gate_cannot_suppress_failure(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "bin/release.sh",
            'bash "$SELF_DIR/verify-template.sh" || true\n'
            'echo "$VERSION" > VERSION\n',
        )

        self.assertIn(
            'FAIL [release-callers]: bin/release.sh must call bash '
            '"$SELF_DIR/verify-template.sh"',
            self.rendered_violations(),
        )

    def test_heredoc_gate_markers_are_inert(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "bin/release.sh",
            "cat <<UNQUOTED\n"
            'bash "$SELF_DIR/verify-template.sh"\n'
            "UNQUOTED\n"
            "cat <<'QUOTED'\n"
            'bash "$SELF_DIR/verify-template.sh"\n'
            "QUOTED\n"
            'echo "$VERSION" > VERSION\n'
            'bash "$SELF_DIR/verify-template.sh" || die "verification failed"\n',
        )

        self.assertIn(
            'FAIL [release-callers]: bin/release.sh must run bash '
            '"$SELF_DIR/verify-template.sh" before echo "$VERSION" > VERSION',
            self.rendered_violations(),
        )

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

    def test_catchup_must_be_a_symlink(self) -> None:
        self.build_good_fixture()
        catchup = self.rendered / ".claude/skills/catchup"
        catchup.unlink()
        catchup.mkdir()

        self.assertIn(
            "FAIL [symlinks]: .claude/skills/catchup must be a symlink",
            self.rendered_violations(),
        )

    def test_catchup_must_resolve_to_shared_skill(self) -> None:
        self.build_good_fixture()
        wrong_target = self.rendered / ".agents/skills/wrong"
        self.write(wrong_target, "SKILL.md")
        catchup = self.rendered / ".claude/skills/catchup"
        catchup.unlink()
        catchup.symlink_to("../../.agents/skills/wrong", target_is_directory=True)

        failures = self.rendered_violations()

        self.assertTrue(any("FAIL [symlinks]" in item for item in failures))
        self.assertTrue(any(".agents/skills/catchup" in item for item in failures))

    def test_catchup_target_must_contain_skill_file(self) -> None:
        self.build_good_fixture()
        (self.rendered / ".agents/skills/catchup/SKILL.md").unlink()

        self.assertIn(
            "FAIL [symlinks]: .claude/skills/catchup target must contain SKILL.md",
            self.rendered_violations(),
        )

    def test_catchup_target_cannot_escape_rendered_root(self) -> None:
        self.build_good_fixture()
        outside = self.rendered.parent / "outside-skill"
        self.write(outside, "SKILL.md")
        catchup = self.rendered / ".claude/skills/catchup"
        catchup.unlink()
        catchup.symlink_to(outside, target_is_directory=True)

        failures = self.rendered_violations()

        self.assertTrue(any("FAIL [symlinks]" in item for item in failures))
        self.assertTrue(any("outside rendered root" in item for item in failures))

    def test_claude_settings_must_be_an_object(self) -> None:
        self.build_good_fixture()
        self.write(self.rendered, ".claude/settings.json", "[]\n")

        self.assertIn(
            "FAIL [claude-hooks]: .claude/settings.json must contain a JSON object",
            self.rendered_violations(),
        )

    def test_claude_settings_must_be_valid_json(self) -> None:
        self.build_good_fixture()
        self.write(self.rendered, ".claude/settings.json", "{not json\n")

        failures = self.rendered_violations()

        self.assertTrue(any("FAIL [claude-hooks]" in item for item in failures))
        self.assertTrue(any("valid JSON" in item for item in failures))

    def test_claude_settings_owned_events_are_exact(self) -> None:
        self.build_good_fixture()
        for event, mutation in (
            ("SessionStart", "add"),
            ("Stop", "remove"),
        ):
            with self.subTest(event=event, mutation=mutation):
                settings = json.loads(json.dumps(GOOD_CLAUDE_SETTINGS))
                if mutation == "add":
                    settings["hooks"][event] = []
                else:
                    del settings["hooks"][event]
                self.write(
                    self.rendered,
                    ".claude/settings.json",
                    json.dumps(settings),
                )

                failures = self.rendered_violations()

                self.assertTrue(
                    any("FAIL [claude-hooks]" in item for item in failures)
                )
                self.assertTrue(any("owned events" in item for item in failures))

    def test_claude_settings_owned_matchers_are_exact(self) -> None:
        self.build_good_fixture()
        settings = json.loads(json.dumps(GOOD_CLAUDE_SETTINGS))
        settings["hooks"]["PostToolUse"][0]["matcher"] = "Write|Edit"
        self.write(self.rendered, ".claude/settings.json", json.dumps(settings))

        failures = self.rendered_violations()

        self.assertTrue(any("FAIL [claude-hooks]" in item for item in failures))
        self.assertTrue(any("owned matchers" in item for item in failures))

    def test_every_owned_handler_must_be_a_command_handler(self) -> None:
        self.build_good_fixture()
        settings = json.loads(json.dumps(GOOD_CLAUDE_SETTINGS))
        settings["hooks"]["Stop"][0]["hooks"][0]["type"] = "prompt"
        self.write(self.rendered, ".claude/settings.json", json.dumps(settings))

        failures = self.rendered_violations()

        self.assertTrue(any("FAIL [claude-hooks]" in item for item in failures))
        self.assertTrue(any("command handler" in item for item in failures))

    def test_every_claude_repository_script_target_must_exist(self) -> None:
        self.build_good_fixture()
        missing = ".claude/hooks/bash-audit-log.sh"
        (self.rendered / missing).unlink()

        self.assertIn(
            f"FAIL [claude-hooks]: repository script target does not exist: {missing}",
            self.rendered_violations(),
        )

    def test_claude_repository_script_target_must_stay_inside_rendered_root(self) -> None:
        self.build_good_fixture()
        relative_path = ".claude/hooks/bash-audit-log.sh"
        outside = self.write(self.rendered.parent, "outside-hook.sh", "exit 0\n")
        self.make_executable(outside)
        target = self.rendered / relative_path
        target.unlink()
        target.symlink_to(outside)

        self.assertIn(
            f"FAIL [claude-hooks]: repository script target must be a regular "
            f"file inside rendered root: {relative_path}",
            self.rendered_violations(),
        )

    def test_claude_repository_script_target_must_be_a_regular_file(self) -> None:
        self.build_good_fixture()
        relative_path = ".claude/hooks/bash-audit-log.sh"
        target = self.rendered / relative_path
        target.unlink()
        target.mkdir()

        self.assertIn(
            f"FAIL [claude-hooks]: repository script target must be a regular "
            f"file inside rendered root: {relative_path}",
            self.rendered_violations(),
        )

    def test_claude_repository_script_target_must_be_readable(self) -> None:
        self.build_good_fixture()
        relative_path = ".claude/hooks/ruff-after-edit.sh"
        target = self.rendered / relative_path
        target.chmod(stat.S_IXUSR)

        self.assertIn(
            f"FAIL [claude-hooks]: repository script target must be readable: "
            f"{relative_path}",
            self.rendered_violations(),
        )

    def test_inline_ruff_command_is_rejected(self) -> None:
        self.build_good_fixture()
        settings = json.loads(json.dumps(GOOD_CLAUDE_SETTINGS))
        settings["hooks"]["PostToolUse"][0]["hooks"][0]["command"] = (
            "python3 -m ruff check --fix example.py || true"
        )
        self.write(self.rendered, ".claude/settings.json", json.dumps(settings))

        failures = self.rendered_violations()

        self.assertTrue(any("FAIL [claude-hooks]" in item for item in failures))
        self.assertTrue(any("inline Ruff command" in item for item in failures))

    def test_ruff_route_must_use_the_adapter(self) -> None:
        self.build_good_fixture()
        settings = json.loads(json.dumps(GOOD_CLAUDE_SETTINGS))
        settings["hooks"]["PostToolUse"][0]["hooks"][0]["command"] = "true"
        self.write(self.rendered, ".claude/settings.json", json.dumps(settings))

        failures = self.rendered_violations()

        self.assertTrue(any("FAIL [claude-hooks]" in item for item in failures))
        self.assertTrue(any("ruff-after-edit.sh" in item for item in failures))

    def test_ruff_route_must_read_nested_file_path(self) -> None:
        self.build_good_fixture()
        self.write(
            self.rendered,
            ".claude/hooks/ruff-after-edit.sh",
            "# should read tool_input.file_path\n"
            'file_path = payload.get("file_path")\n',
        )
        self.make_executable(self.rendered / ".claude/hooks/ruff-after-edit.sh")

        failures = self.rendered_violations()

        self.assertTrue(any("FAIL [claude-hooks]" in item for item in failures))
        self.assertTrue(any("tool_input.file_path" in item for item in failures))

    def test_ruff_route_comments_do_not_prove_nested_file_path_access(self) -> None:
        self.build_good_fixture()
        self.write(
            self.rendered,
            ".claude/hooks/ruff-after-edit.sh",
            "#!/usr/bin/env bash\n"
            '# payload.get("tool_input")\n'
            '# tool_input.get("file_path")\n'
            "exit 0\n",
        )
        self.make_executable(self.rendered / ".claude/hooks/ruff-after-edit.sh")

        self.assertIn(
            "FAIL [claude-hooks]: ruff-after-edit.sh must read "
            "tool_input.file_path",
            self.rendered_violations(),
        )

    def test_rendered_ruff_adapter_must_match_tested_source(self) -> None:
        self.build_good_fixture()
        self.write(
            self.rendered,
            ".claude/hooks/ruff-after-edit.sh",
            GOOD_RUFF_ADAPTER.replace(
                "payload = {}\n",
                "payload = {}\nraise SystemExit(0)\n",
            ),
        )
        self.make_executable(self.rendered / ".claude/hooks/ruff-after-edit.sh")

        self.assertIn(
            "FAIL [claude-hooks]: rendered ruff-after-edit.sh must match the "
            "tested source adapter",
            self.rendered_violations(),
        )

    def run_ruff_hook(
        self,
        payload: str,
        *,
        fake_exit: int = 0,
    ) -> tuple[subprocess.CompletedProcess[str], pathlib.Path]:
        fake_root = pathlib.Path(self.temp_dir.name) / "fake-pythonpath"
        ruff_package = fake_root / "ruff"
        ruff_package.mkdir(parents=True, exist_ok=True)
        self.write(ruff_package, "__init__.py", "")
        self.write(
            ruff_package,
            "__main__.py",
            "import os, pathlib, sys\n"
            "pathlib.Path(os.environ['RUFF_CAPTURE']).write_text("
            "' '.join(sys.argv[1:]), encoding='utf-8')\n"
            "raise SystemExit(int(os.environ.get('RUFF_FAKE_EXIT', '0')))\n",
        )
        capture = pathlib.Path(self.temp_dir.name) / "ruff-capture"
        environment = os.environ.copy()
        environment.update(
            {
                "PYTHONPATH": str(fake_root),
                "RUFF_CAPTURE": str(capture),
                "RUFF_FAKE_EXIT": str(fake_exit),
            }
        )
        process = subprocess.run(
            ["bash", str(BIN_DIR.parent / "seed/.claude/hooks/ruff-after-edit.sh")],
            input=payload,
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        return process, capture

    def test_ruff_hook_fixes_only_nested_python_file_path(self) -> None:
        payload = json.dumps({"tool_input": {"file_path": "src/example.py"}})

        process, capture = self.run_ruff_hook(payload)

        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual("check --fix -- src/example.py", capture.read_text())

    def test_ruff_hook_ignores_irrelevant_payloads(self) -> None:
        for label, payload in (
            ("non-python", json.dumps({"tool_input": {"file_path": "README.md"}})),
            ("missing", json.dumps({"tool_input": {}})),
            ("non-string", json.dumps({"tool_input": {"file_path": 7}})),
            ("malformed", "{not json"),
        ):
            with self.subTest(label=label):
                process, capture = self.run_ruff_hook(payload)

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertFalse(capture.exists())

    def test_ruff_hook_is_non_blocking_when_ruff_fails(self) -> None:
        payload = json.dumps({"tool_input": {"file_path": "src/example.py"}})

        process, capture = self.run_ruff_hook(payload, fake_exit=23)

        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual("check --fix -- src/example.py", capture.read_text())

    def test_every_required_prose_reference_is_enforced(self) -> None:
        self.build_good_fixture()
        references = (
            ("CLAUDE.md", "@AGENTS.md"),
            ("AGENTS.md", ".codex/"),
            ("AGENTS.md", ".agents/skills/"),
            ("CLAUDE.md", ".claude/hooks/stop-verify-gate.sh"),
            ("CLAUDE.md", "/catchup"),
            ("CLAUDE.md", ".agents/skills/"),
            ("CLAUDE.md", "bash-audit-log.sh"),
            ("CLAUDE.md", "concurrent-checkout-guard.sh"),
            ("CLAUDE.md", "ruff-after-edit.sh"),
        )
        original = {
            document: (self.rendered / document).read_text(encoding="utf-8")
            for document, _ in references
        }
        for document, reference in references:
            with self.subTest(document=document, reference=reference):
                self.write(
                    self.rendered,
                    document,
                    original[document].replace(reference, "REMOVED", 1),
                )

                failures = self.rendered_violations()
                self.write(self.rendered, document, original[document])
                self.assertIn(
                    f"FAIL [prose-routes]: {document} must reference {reference}",
                    failures,
                )

    def test_required_prose_route_targets_are_enforced(self) -> None:
        self.build_good_fixture()
        targets = (
            ("CLAUDE.md", "AGENTS.md"),
            ("AGENTS.md", ".codex"),
            ("AGENTS.md", ".agents/skills"),
            ("CLAUDE.md", ".claude/hooks/stop-verify-gate.sh"),
            ("CLAUDE.md", ".agents/skills/catchup/SKILL.md"),
            ("CLAUDE.md", ".claude/hooks/bash-audit-log.sh"),
            ("CLAUDE.md", ".claude/hooks/concurrent-checkout-guard.sh"),
            ("CLAUDE.md", ".claude/hooks/ruff-after-edit.sh"),
        )
        for document, target in targets:
            with self.subTest(document=document, target=target):
                path = self.rendered / target
                parked = self.rendered / f"{target}.parked"
                path.rename(parked)

                failures = self.rendered_violations()
                parked.rename(path)
                self.assertIn(
                    f"FAIL [prose-routes]: {document} route target does not exist: "
                    f"{target}",
                    failures,
                )

    def test_optional_plugin_routes_do_not_require_targets(self) -> None:
        self.build_good_fixture()

        failures = [
            item for item in self.rendered_violations() if "prose-routes" in item
        ]

        self.assertEqual([], failures)

    def test_unresolved_docs_placeholder_is_rejected(self) -> None:
        self.build_good_fixture()
        self.write(
            self.rendered,
            "CLAUDE.md",
            GOOD_CLAUDE_PROSE + "| `docs/` | (Add rows here) |\n",
        )

        self.assertIn(
            "FAIL [prose-routes]: CLAUDE.md contains unresolved docs/ placeholder",
            self.rendered_violations(),
        )

    def test_every_rendered_claude_hook_must_be_executable(self) -> None:
        self.build_good_fixture()
        for relative_path in CLAUDE_HOOK_PATHS:
            with self.subTest(path=relative_path):
                path = self.rendered / relative_path
                original_mode = path.stat().st_mode
                path.chmod(
                    original_mode
                    & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                )

                failures = self.rendered_violations()
                path.chmod(original_mode)
                self.assertIn(
                    f"FAIL [executable-modes]: repository script is not "
                    f"executable: {relative_path}",
                    failures,
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
        self.assertEqual(
            "FAIL [topology]: missing required rendered path: "
            ".codex/config.toml\n",
            output.getvalue(),
        )

    def test_cli_returns_zero_for_clean_fixture(self) -> None:
        self.build_good_fixture()
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

        self.assertEqual(0, exit_code)
        self.assertEqual("", output.getvalue())


if __name__ == "__main__":
    unittest.main()
