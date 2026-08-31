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
import textwrap
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

POLICY_SCRIPT = BIN_DIR.parent / "seed/.codex/hooks/pre-tool-policy.py"
POLICY_DENIAL = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Force pushes are blocked by repository policy."
        ),
    }
}
GOOD_CODEX_HOOKS = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "^Bash$",
                "hooks": [
                    {
                        "type": "command",
                        "command": (
                            'python3 "$(git rev-parse --show-toplevel)/.codex/'
                            'hooks/pre-tool-policy.py"'
                        ),
                        "timeout": 10,
                        "statusMessage": "Checking Git push policy",
                    }
                ],
            }
        ]
    }
}
GOOD_CODEX_CONFIG = """\
default_permissions = "project-workspace"

[features]
hooks = true
multi_agent = true

[agents]
max_concurrent_threads_per_session = 6

[permissions.project-workspace]
description = "Workspace editing with project secret-file denies."
extends = ":workspace"

[permissions.project-workspace.filesystem.":workspace_roots"]
".env" = "deny"
".env*" = "deny"
".env.*" = "deny"
".envrc" = "deny"
".envrc.*" = "deny"
"**/.env" = "deny"
"**/.env*" = "deny"
"**/.env.*" = "deny"
"**/.envrc" = "deny"
"**/.envrc.*" = "deny"
"""
GOOD_CODEX_POLICY = """\
#!/usr/bin/env python3
import json
import sys

payload = json.load(sys.stdin)
command = payload["tool_input"]["command"]
if command == "git push --force origin main":
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Force pushes are blocked by repository policy."
        }
    }))
"""


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
        canonical_hook = "#!/bin/sh\nexit 0\n"
        self.write(
            self.source,
            "seed/.claude/hooks/concurrent-checkout-guard.sh",
            canonical_hook,
        )
        self.write(
            self.source,
            (
                "cultivation/marketplace/sam-cc-setup/hooks/"
                "concurrent-checkout-guard.sh"
            ),
            canonical_hook,
        )
        self.write(
            self.source,
            "seed/.claude/hooks/ruff-after-edit.sh",
            GOOD_RUFF_ADAPTER,
        )
        self.write(
            self.source,
            "cultivation/marketplace/.claude-plugin/marketplace.json",
            json.dumps({"plugins": []}),
        )

        rendered_contents = {
            "AGENTS.md": GOOD_AGENT_PROSE,
            "CLAUDE.md": GOOD_CLAUDE_PROSE,
            ".claude/settings.json": json.dumps(GOOD_CLAUDE_SETTINGS),
            ".claude/hooks/ruff-after-edit.sh": GOOD_RUFF_ADAPTER,
            ".codex/config.toml": GOOD_CODEX_CONFIG,
            ".codex/hooks.json": json.dumps(GOOD_CODEX_HOOKS),
            ".codex/hooks/pre-tool-policy.py": GOOD_CODEX_POLICY,
            ".codex/rules/default.rules": (
                BIN_DIR.parent / "seed/.codex/rules/default.rules"
            ).read_text(encoding="utf-8"),
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

    def test_concurrent_checkout_distribution_mirror_must_match_canonical(
        self,
    ) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            (
                "cultivation/marketplace/sam-cc-setup/hooks/"
                "concurrent-checkout-guard.sh"
            ),
            "different hook\n",
        )

        rendered = self.rendered_violations()

        self.assertTrue(
            any("FAIL [distribution-mirrors]" in item for item in rendered)
        )
        self.assertTrue(any("concurrent-checkout-guard.sh" in item for item in rendered))

    def test_concurrent_checkout_distribution_mirror_requires_both_files(
        self,
    ) -> None:
        self.build_good_fixture()
        paths = (
            "seed/.claude/hooks/concurrent-checkout-guard.sh",
            (
                "cultivation/marketplace/sam-cc-setup/hooks/"
                "concurrent-checkout-guard.sh"
            ),
        )
        for missing in paths:
            with self.subTest(missing=missing):
                (self.source / missing).unlink()

                rendered = self.rendered_violations()

                self.assertTrue(
                    any("FAIL [distribution-mirrors]" in item for item in rendered)
                )
                self.assertTrue(any(missing in item for item in rendered))
                self.write(self.source, missing, "#!/bin/sh\nexit 0\n")

    def test_missing_required_rendered_paths_are_reported(self) -> None:
        self.build_good_fixture()
        missing = ".codex/hooks.json"
        (self.rendered / missing).unlink()

        rendered = self.rendered_violations()

        self.assertTrue(any("FAIL [topology]" in item for item in rendered))
        self.assertTrue(any(missing in item for item in rendered))

    def test_required_rendered_files_reject_wrong_kinds_and_symlinks(self) -> None:
        self.build_good_fixture()
        cases = (
            ("directory", ".codex/config.toml", "directory"),
            ("external symlink", "AGENTS.md", "external-file"),
            (
                "internal symlink",
                ".claude/settings.local.json.template",
                "CLAUDE.md",
            ),
            (
                "symlink to directory",
                ".codex/rules/default.rules",
                ".codex",
            ),
        )
        for label, relative_path, target_name in cases:
            with self.subTest(label=label):
                path = self.rendered / relative_path
                original = path.read_bytes()
                original_mode = path.stat().st_mode
                path.unlink()
                if label == "directory":
                    path.mkdir()
                elif label == "external symlink":
                    outside = self.write(self.rendered.parent, target_name)
                    path.symlink_to(outside)
                else:
                    path.symlink_to(self.rendered / target_name)

                failures = self.rendered_violations()
                if path.is_symlink():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()
                path.write_bytes(original)
                path.chmod(original_mode)
                self.assertIn(
                    "FAIL [topology]: required rendered path must be a direct "
                    f"regular file inside rendered root: {relative_path}",
                    failures,
                )

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

    def test_workflow_conditional_gate_is_inert(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            ".github/workflows/test.yml",
            "jobs:\n"
            "  verify:\n"
            "    steps:\n"
            "      - name: Conditional gate\n"
            "        if: false\n"
            "        run: bin/verify-template.sh\n",
        )

        self.assertIn(
            "FAIL [release-callers]: .github/workflows/test.yml must call "
            "bin/verify-template.sh",
            self.rendered_violations(),
        )

    def test_workflow_failure_ignored_gate_is_inert(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            ".github/workflows/release.yml",
            "jobs:\n"
            "  release:\n"
            "    steps:\n"
            "      - name: Ignored gate\n"
            "        run: bin/verify-template.sh\n"
            "        continue-on-error: true\n"
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

    def test_release_script_conditional_gate_is_inert(self) -> None:
        self.build_good_fixture()
        for indentation in ("  ", ""):
            with self.subTest(indentation=repr(indentation)):
                self.write(
                    self.source,
                    "bin/release.sh",
                    "if false; then\n"
                    f'{indentation}bash "$SELF_DIR/verify-template.sh" || '
                    'die "verification failed"\n'
                    "fi\n"
                    'echo "$VERSION" > VERSION\n',
                )

                self.assertIn(
                    'FAIL [release-callers]: bin/release.sh must call bash '
                    '"$SELF_DIR/verify-template.sh"',
                    self.rendered_violations(),
                )

    def test_release_script_uncalled_function_gate_is_inert(self) -> None:
        self.build_good_fixture()
        for indentation in ("  ", ""):
            with self.subTest(indentation=repr(indentation)):
                self.write(
                    self.source,
                    "bin/release.sh",
                    "verify_only() {\n"
                    f'{indentation}bash "$SELF_DIR/verify-template.sh" || '
                    'die "verification failed"\n'
                    "}\n"
                    'echo "$VERSION" > VERSION\n',
                )

                self.assertIn(
                    'FAIL [release-callers]: bin/release.sh must call bash '
                    '"$SELF_DIR/verify-template.sh"',
                    self.rendered_violations(),
                )

    def test_release_script_compound_gate_is_inert(self) -> None:
        self.build_good_fixture()
        wrappers = (
            ("while false; do", "done"),
            ("for value in none; do", "done"),
            ("case value in", "esac"),
            ("{", "}"),
            ("(", ")"),
        )
        for opener, closer in wrappers:
            with self.subTest(opener=opener):
                self.write(
                    self.source,
                    "bin/release.sh",
                    f"{opener}\n"
                    'bash "$SELF_DIR/verify-template.sh" || '
                    'die "verification failed"\n'
                    f"{closer}\n"
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

    def test_marketplace_discovers_string_sources_and_parses_hooks(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "cultivation/marketplace/.claude-plugin/marketplace.json",
            json.dumps(
                {
                    "plugins": [
                        {"name": "local-one", "source": "./local-one"},
                        {
                            "name": "remote-one",
                            "source": {
                                "source": "git-subdir",
                                "url": "https://example.invalid/repo.git",
                            },
                        },
                    ]
                }
            ),
        )
        self.write(self.source, "cultivation/marketplace/local-one/README.md")
        self.write(
            self.source,
            "cultivation/marketplace/local-one/hooks/hooks.json",
            json.dumps({"hooks": {}}),
        )

        self.assertEqual((), contract.verify_contract(self.source, self.rendered))

    def test_marketplace_rejects_local_source_outside_root(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "cultivation/marketplace/.claude-plugin/marketplace.json",
            json.dumps({"plugins": [{"source": "../outside"}]}),
        )
        (self.source / "cultivation/outside").mkdir(parents=True)

        rendered = self.rendered_violations()

        self.assertTrue(any("FAIL [marketplace]" in item for item in rendered))
        self.assertTrue(any("escapes marketplace root" in item for item in rendered))

    def test_marketplace_rejects_symlinked_local_source_outside_root(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "cultivation/marketplace/.claude-plugin/marketplace.json",
            json.dumps({"plugins": [{"source": "./linked"}]}),
        )
        outside = self.source / "outside-plugin"
        outside.mkdir()
        (self.source / "cultivation/marketplace/linked").symlink_to(
            outside,
            target_is_directory=True,
        )

        rendered = self.rendered_violations()

        self.assertTrue(any("FAIL [marketplace]" in item for item in rendered))
        self.assertTrue(any("escapes marketplace root" in item for item in rendered))

    def test_marketplace_reports_missing_local_root(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "cultivation/marketplace/.claude-plugin/marketplace.json",
            json.dumps({"plugins": [{"source": "./missing-plugin"}]}),
        )

        rendered = self.rendered_violations()

        self.assertTrue(any("FAIL [marketplace]" in item for item in rendered))
        self.assertTrue(any("missing local plugin root" in item for item in rendered))

    def test_marketplace_reports_invalid_local_hook_json(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "cultivation/marketplace/.claude-plugin/marketplace.json",
            json.dumps({"plugins": [{"source": "./local-one"}]}),
        )
        self.write(
            self.source,
            "cultivation/marketplace/local-one/hooks/hooks.json",
            "{not-json\n",
        )

        rendered = self.rendered_violations()

        self.assertTrue(any("FAIL [marketplace]" in item for item in rendered))
        self.assertTrue(any("hooks/hooks.json" in item for item in rendered))

    def test_cli_lists_valid_local_marketplace_roots(self) -> None:
        self.build_good_fixture()
        self.write(
            self.source,
            "cultivation/marketplace/.claude-plugin/marketplace.json",
            json.dumps(
                {
                    "plugins": [
                        {"source": "./local-one"},
                        {"source": {"source": "git-subdir"}},
                    ]
                }
            ),
        )
        self.write(self.source, "cultivation/marketplace/local-one/README.md")
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            try:
                exit_code = contract.main(
                    [
                        "--source-root",
                        str(self.source),
                        "--list-local-plugin-roots",
                    ]
                )
            except SystemExit as error:
                exit_code = error.code

        self.assertEqual(0, exit_code)
        self.assertEqual("cultivation/marketplace/local-one\n", output.getvalue())

    def run_wrapper(
        self,
        *,
        with_claude: bool = True,
        with_codex: bool = True,
        claude_fails: bool = False,
        codex_wrong_decision: bool = False,
    ) -> tuple[subprocess.CompletedProcess[str], str]:
        fake_bin = pathlib.Path(self.temp_dir.name) / "fake-bin"
        fake_bin.mkdir(exist_ok=True)
        tool_log = pathlib.Path(self.temp_dir.name) / "tool.log"

        def fake_tool(name: str, content: str) -> None:
            path = self.write(fake_bin, name, content)
            self.make_executable(path)

        fake_tool(
            "python3",
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                if [[ "$1" == "-m" && "$2" == "unittest" ]]; then
                  echo "fake contract unit tests: OK"
                  exit 0
                fi
                if [[ "$1" == *rendered_harness_contract.py ]] && [[ " $* " == *" --rendered-root "* ]]; then
                  echo "checker $*" >> "$FAKE_TOOL_LOG"
                  exit 0
                fi
                if [[ "$1" == "-m" && "$2" == "json.tool" ]]; then
                  echo "json-tool $3" >> "$FAKE_TOOL_LOG"
                fi
                exec "$REAL_PYTHON" "$@"
                """
            ),
        )
        fake_tool(
            "copier",
            textwrap.dedent(
                """\
                #!/usr/bin/env bash
                for destination; do :; done
                mkdir -p "$destination"
                echo "copier $*" >> "$FAKE_TOOL_LOG"
                """
            ),
        )
        if with_claude:
            fake_tool(
                "claude",
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    printf 'claude' >> "$FAKE_TOOL_LOG"
                    printf ' <%s>' "$@" >> "$FAKE_TOOL_LOG"
                    printf '\n' >> "$FAKE_TOOL_LOG"
                    [[ "$FAKE_CLAUDE_FAILS" == 1 ]] && exit 7
                    exit 0
                    """
                ),
            )
        if with_codex:
            fake_tool(
                "codex",
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    printf 'codex' >> "$FAKE_TOOL_LOG"
                    printf ' <%s>' "$@" >> "$FAKE_TOOL_LOG"
                    printf '\n' >> "$FAKE_TOOL_LOG"
                    decision=prompt
                    [[ " $* " == *" --force "* ]] && decision=forbidden
                    [[ " $* " == *" --force-with-lease "* ]] && decision=forbidden
                    [[ "$FAKE_CODEX_WRONG" == 1 ]] && decision=allow
                    printf '{"decision":"%s"}\n' "$decision"
                    """
                ),
            )

        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{fake_bin}:/usr/bin:/bin",
                "REAL_PYTHON": sys.executable,
                "FAKE_TOOL_LOG": str(tool_log),
                "FAKE_CLAUDE_FAILS": "1" if claude_fails else "0",
                "FAKE_CODEX_WRONG": "1" if codex_wrong_decision else "0",
            }
        )
        process = subprocess.run(
            ["bash", str(BIN_DIR / "verify-template.sh")],
            cwd=BIN_DIR.parent,
            env=environment,
            text=True,
            capture_output=True,
            timeout=30,
            check=False,
        )
        log = tool_log.read_text(encoding="utf-8") if tool_log.exists() else ""
        return process, log

    def test_wrapper_runs_required_stages_in_order(self) -> None:
        process, log = self.run_wrapper()
        markers = (
            "contract unit tests",
            "Copier scratch render from HEAD",
            "rendered harness contract",
            "Claude native validation",
            "Codex native policy probes",
            "skill frontmatter names",
            "verify-template: PASSED",
        )

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        positions = tuple(process.stdout.index(marker) for marker in markers)
        self.assertEqual(tuple(sorted(positions)), positions)
        self.assertIn("<plugin> <validate> <seed/.claude>", log)
        self.assertNotIn("<plugin> <validate> <--strict> <seed/.claude>", log)
        self.assertIn(
            "<plugin> <validate> <--strict> <seed/.agents/skills>",
            log,
        )
        self.assertIn(
            "<plugin> <validate> <--strict> <cultivation/marketplace>",
            log,
        )
        self.assertNotIn("<hooks>", log)
        self.assertIn(
            "<execpolicy> <check> <--rules> <seed/.codex/rules/default.rules> "
            "<--> <git> <push> <origin> <main>",
            log,
        )
        self.assertIn(
            "<execpolicy> <check> <--rules> <seed/.codex/rules/default.rules> "
            "<--> <git> <push> <--force> <origin> <main>",
            log,
        )
        self.assertIn(
            "<execpolicy> <check> <--rules> <seed/.codex/rules/default.rules> "
            "<--> <git> <push> <--force-with-lease> <origin> <main>",
            log,
        )

    def test_wrapper_reports_missing_native_tools_as_visible_skips(self) -> None:
        process, _ = self.run_wrapper(with_claude=False, with_codex=False)

        self.assertEqual(0, process.returncode, process.stdout + process.stderr)
        self.assertIn("SKIPPED: claude CLI not found", process.stdout)
        self.assertIn("SKIPPED: codex CLI not found", process.stdout)

    def test_wrapper_accumulates_native_failures(self) -> None:
        for label, arguments in (
            ("claude", {"claude_fails": True}),
            ("codex", {"codex_wrong_decision": True}),
        ):
            with self.subTest(tool=label):
                process, _ = self.run_wrapper(**arguments)

                self.assertEqual(1, process.returncode)
                self.assertIn("verify-template: FAILED", process.stdout)
                self.assertIn("skill frontmatter names", process.stdout)

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

    def test_source_ruff_adapter_proves_nested_file_path_access(self) -> None:
        source_adapter = (
            BIN_DIR.parent / "seed/.claude/hooks/ruff-after-edit.sh"
        ).read_text(encoding="utf-8")

        self.assertTrue(contract._ruff_reads_nested_file_path(source_adapter))

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
            "import json, os, pathlib, sys\n"
            "pathlib.Path(os.environ['RUFF_CAPTURE']).write_text("
            "json.dumps(sys.argv[1:]), encoding='utf-8')\n"
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
        self.assertEqual(
            ["check", "--fix", "--", "src/example.py"],
            json.loads(capture.read_text()),
        )

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
        self.assertEqual(
            ["check", "--fix", "--", "src/example.py"],
            json.loads(capture.read_text()),
        )

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

    def policy_payload(self, command: str) -> str:
        return json.dumps(
            {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": command},
                "future_field": "accepted",
            }
        )

    def run_policy(self, payload: str) -> subprocess.CompletedProcess[str]:
        self.assertTrue(POLICY_SCRIPT.is_file(), f"missing {POLICY_SCRIPT}")
        return subprocess.run(
            [sys.executable, str(POLICY_SCRIPT)],
            input=payload,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_policy_process_denies_literal_force_push_forms(self) -> None:
        commands = (
            "git push --force origin main",
            "git push origin main --force",
            "git push --force=true origin main",
            "git push --force-with-lease origin main",
            "git push --force-with-lease=main:abc origin main",
            "git push --force-with-l origin main",
            "git push -f origin main",
            "git push -vf origin main",
            "git push origin +main",
            "git push -o --dry-run --force origin main",
            "git push --push-o --dry-run --force origin main",
            "git push --dry-run --no-dry-run --force origin main",
            "git -C repo push --force origin main",
            "git -c user.name=test push --force origin main",
            "git --git-dir=.git push --force origin main",
            "git --git-dir .git push --force origin main",
            "git --work-tree=. push --force origin main",
            "git --namespace=team push --force origin main",
            "git --no-pager push --force origin main",
            "git -P push --force origin main",
            "git --no-lazy-fetch push --force origin main",
            "command -- git push --force origin main",
            "env MODE=test git push --force origin main",
            "/usr/bin/env -i MODE=test git push --force origin main",
            "MODE=test git push --force origin main",
            "echo safe; git push --force origin main",
            "echo safe & git push --force origin main",
            "echo safe && git push --force origin main",
            "echo safe || git push --force origin main",
            "echo safe | git push --force origin main",
            "echo safe |& git push --force origin main",
            "echo safe\ngit push --force origin main",
            "echo safe # ignored\ngit push --force origin main",
            "echo value#text; git push --force origin main",
            "true\r#word; git push --force origin main",
            "echo ${value#prefix}; git push --force origin main",
            "if true; then git push --force origin main; fi",
            "git push \\\n--force origin main",
            "git push \\\r\n--force origin main",
            "'g''it' 'pu''sh' '--for''ce' origin main",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_denies_active_mirror_pushes(self) -> None:
        commands = (
            "git push --mirror origin",
            "git push --mir origin",
            "git push --no-mirror --mirror origin",
            "git push --mirror --no-mirror --mirror origin",
            "git push --dry-run --no-dry-run --mirror origin",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_allows_cancelled_or_dry_run_mirror_pushes(self) -> None:
        commands = (
            "git push --mirror --no-mirror origin",
            "git push --mirror --dry-run origin",
            "git push --mirror --no-dry-run --dry-run origin",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual("", process.stdout)
                self.assertEqual("", process.stderr)

    def test_policy_process_allows_out_of_scope_shell_forms(self) -> None:
        commands = (
            "",
            "git push origin main",
            "git push --dry-run --force origin main",
            "git push -o --force origin main",
            "git push --push-option --force origin main",
            "git push --push-o --force origin main",
            "git push --force --no-force origin main",
            "git push +definitely-not-a-repo main",
            "git help push --force",
            "echo safe",
            "printf '%s' '--force git push'",
            "echo safe # git push --force origin main",
            "printf '%s' 'x; git push --force origin main'",
            "g push --force origin main",
            "git publish --force origin main",
            "$GIT push --force origin main",
            "sh -c 'git push --force origin main'",
            "echo \"$(git push --force origin main)\"",
            "printf '%s' 'git push --force origin main'",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual("", process.stdout)
                self.assertEqual("", process.stderr)

    def test_policy_process_blocks_malformed_envelopes(self) -> None:
        malformed = (
            ("empty input", ""),
            ("invalid JSON", "{not json"),
            ("array", "[]"),
            ("string", '"value"'),
            ("number", "7"),
            ("Boolean", "true"),
            ("null", "null"),
            (
                "wrong event",
                json.dumps(
                    {
                        "hook_event_name": "PostToolUse",
                        "tool_name": "Bash",
                        "tool_input": {"command": "echo safe"},
                    }
                ),
            ),
            (
                "wrong tool",
                json.dumps(
                    {
                        "hook_event_name": "PreToolUse",
                        "tool_name": "Read",
                        "tool_input": {"command": "echo safe"},
                    }
                ),
            ),
            (
                "missing tool input",
                json.dumps(
                    {"hook_event_name": "PreToolUse", "tool_name": "Bash"}
                ),
            ),
            (
                "non-object tool input",
                json.dumps(
                    {
                        "hook_event_name": "PreToolUse",
                        "tool_name": "Bash",
                        "tool_input": [],
                    }
                ),
            ),
            (
                "missing command",
                json.dumps(
                    {
                        "hook_event_name": "PreToolUse",
                        "tool_name": "Bash",
                        "tool_input": {},
                    }
                ),
            ),
            (
                "non-string command",
                json.dumps(
                    {
                        "hook_event_name": "PreToolUse",
                        "tool_name": "Bash",
                        "tool_input": {"command": 7},
                    }
                ),
            ),
        )
        for label, payload in malformed:
            with self.subTest(label=label):
                process = self.run_policy(payload)

                self.assertEqual(2, process.returncode)
                self.assertEqual("", process.stdout)
                self.assertTrue(process.stderr.startswith("pre-tool-policy: "))
                self.assertLessEqual(len(process.stderr.strip()), 160)

    def test_policy_process_blocks_unparseable_shell_text(self) -> None:
        process = self.run_policy(self.policy_payload("git push 'unterminated"))

        self.assertEqual(2, process.returncode)
        self.assertEqual("", process.stdout)
        self.assertTrue(process.stderr.startswith("pre-tool-policy: "))

    def test_policy_process_denies_force_push_after_reserved_prefixes(self) -> None:
        commands = (
            "! git push --force origin main",
            "if git push --force origin main; then :; fi",
            "if false; then :; elif git push --force origin main; then :; fi",
            "while git push --force origin main; do break; done",
            "until git push --force origin main; do break; done",
            "if true; then git push --force origin main; fi",
            "while true; do git push --force origin main; break; done",
            "if false; then :; else git push --force origin main; fi",
            "time git push --force origin main",
            "time -p git push --force origin main",
            "time -p -- git push --force origin main",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_blocks_invalid_shell_grammar(self) -> None:
        commands = (
            "echo safe &&& echo ok",
            "echo safe ||| echo ok",
            "echo safe |",
            "if true; then echo safe",
            "while true; do echo safe",
            "(echo safe",
            "case value in value) echo safe",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(2, process.returncode)
                self.assertEqual("", process.stdout)
                self.assertTrue(process.stderr.startswith("pre-tool-policy: "))
                self.assertLessEqual(len(process.stderr.strip()), 160)

    def test_policy_process_allows_terminal_push_help(self) -> None:
        for command in (
            "git push -h --force origin main",
            "git push --help --force origin main",
        ):
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual("", process.stdout)
                self.assertEqual("", process.stderr)

    def test_policy_process_denies_force_push_in_function_definitions(self) -> None:
        functions = (
            "deploy() {\n  git push --force origin main\n}\n",
            "deploy()\n{\n  git push --force origin main\n}\n",
            "function deploy {\n  git push --force origin main\n}\n",
            "function deploy\n{\n  git push --force origin main\n}\n",
            (
                "deploy() {\n"
                "  printf '%s' '}'\n"
                "  git push --force origin main\n"
                "}\n"
            ),
        )
        for command in functions:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_denies_push_after_function_definition(self) -> None:
        commands = (
            (
                "deploy() {\n"
                "  git push --force origin main\n"
                "}\n"
                "git push --force origin main\n"
            ),
            (
                "deploy() {\n"
                "  printf '%s' '{'\n"
                "}\n"
                "git push --force origin main\n"
            ),
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_finds_git_after_wrappers_and_assignments(self) -> None:
        commands = (
            "command -- time git push --force origin main",
            "env time git push --force origin main",
            "/usr/bin/env -i time git push --force origin main",
            "MODE=check time git push --force origin main",
            "MODE+=check git push --force origin main",
            "MODE+=check time git push --force origin main",
            "MODE[0]=check git push --force origin main",
            "MODE[0]=check time git push --force origin main",
            "command -p git push --force origin main",
            "command -p -p git push --force origin main",
            "command -pp git push --force origin main",
            "env - git push --force origin main",
            "/usr/bin/env - git push --force origin main",
            "env -uMODE git push --force origin main",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_allows_safe_wrapper_analogs(self) -> None:
        commands = (
            "command -- time git --version",
            "env time git --version",
            "/usr/bin/env -i time git --version",
            "MODE=check time git --version",
            "command -p git --version",
            "env - git --version",
            "/usr/bin/env - git --version",
            "env -uMODE git --version",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual("", process.stdout)
                self.assertEqual("", process.stderr)

    def test_policy_process_denies_force_tokens_exposed_by_heredocs(self) -> None:
        commands = (
            (
                "deploy() {\n"
                "  cat <<EOF\n"
                "}\n"
                "EOF\n"
                "  git push --force origin main\n"
                "}\n"
            ),
            "cat <<EOF\ngit push --force origin main\nEOF\n",
            "cat <<'EOF'\ngit push --force origin main\nEOF\n",
            "cat <<$'EOF'\ngit push --force origin main\nEOF\n",
            "cat <<$\"EOF\"\ngit push --force origin main\nEOF\n",
            "cat <<$'E\\x4fF'\ngit push --force origin main\nEOF\n",
            "cat <<-EOF\n\tgit push --force origin main\n\tEOF\n",
            (
                "cat <<ONE <<'TWO'\n"
                "git push --force origin main\n"
                "ONE\n"
                "}\n"
                "TWO\n"
            ),
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_conservatively_denies_literal_git_sequences(self) -> None:
        commands = (
            "env A-B=value git push --force origin main",
            "env A-B= git push --force origin main",
            "cat <<$'E\\x4fF'\ngit push --force origin main\nEOF\n",
            (
                "cat <<$'E\\x4fF'\n"
                "safe\n"
                "EOF\n"
                "git push --force origin main\n"
            ),
            "{ git push --force origin main; }",
            "case x in x)git push --force origin main;;esac",
            (
                "deploy() {\n"
                "  printf '%s' '{' '}'\n"
                "  git push --force origin main\n"
                "}\n"
            ),
            (
                "deploy() {\n"
                "  echo {\n"
                "}\n"
                "git push --force origin main\n"
            ),
            (
                "deploy() {\n"
                "  echo }\n"
                "  git push --force origin main\n"
                "}\n"
            ),
            "cat <<''\ngit push --force origin main\n\n",
            "command -- if git push --force origin main",
            "command if git push --force origin main",
            "command -v git push --force origin main",
            "command -V git push --force origin main",
            "echo $(git push --force origin main)",
            "git 2>/dev/null push --force origin main",
            "git </dev/null push --force origin main",
            "git <<EOF push --force origin main\nEOF\n",
            "git >|/dev/null push --force origin main",
            "git <<- EOF push --force origin main\nEOF\n",
            "$'git' push --force origin main",
            "git $'push' --force origin main",
            "git push $'--force' origin main",
            "$''git push --force origin main",
            "$'\\547'it push --force origin main",
            "git $'\\560'ush --force origin main",
            (
                "git push $'\\455\\455\\546\\557\\562\\543\\545' "
                "origin main"
            ),
            '$"git" push --force origin main',
            'git $"push" --force origin main',
            'git push $"--force" origin main',
            '$"g"it push --force origin main',
            '$""git push --force origin main',
            "git {fd}>/dev/null push --force origin main",
            "git <<';' push --force origin main\n;\n",
            "printf '%s' ';' git push --force origin main",
            "printf '%s' \\; git push --force origin main",
            r'''printf '%s' "\";" git push --force origin main''',
            "printf '%s' 'line one\nline two' git push --force origin main",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_allows_safe_conservative_analogs(self) -> None:
        commands = (
            "env A-B=value git --version",
            "env A-B= git --version",
            "cat <<$'E\\x4fF'\ngit --version\nEOF\n",
            "{ git --version; }",
            "case x in x)git --version;;esac",
            "deploy() { printf '%s' '{' '}'; git --version; }",
            "cat <<''\ngit --version\n\n",
            "command -- if git --version",
            "command if git --version",
            "git 2>/dev/null --version",
            "git </dev/null --version",
            "$'git' --version",
            "git $'--version'",
            "$''git --version",
            "$'\\547'it --version",
            "git $'\\455\\455\\566\\545\\562\\563\\551\\557\\556'",
            "$'\\0147'it push --force origin main",
            '$"git" --version',
            "printf '%s' $'\\U00110000'",
            "git {fd}>/dev/null --version",
            "git <<';' --version\n;\n",
            "printf '%s' 'git push --force origin main'",
            "printf %s 'git\\\n' push --force origin main",
            "echo safe # git push --force origin main",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual("", process.stdout)
                self.assertEqual("", process.stderr)

    def test_policy_process_denies_nul_terminated_ansi_c_fragments(self) -> None:
        commands = (
            "g$'\\0'it p$'\\0'ush --f$'\\0'orce origin main",
            "$'\\0'git push --force origin main",
            "$'\\000'git push --force origin main",
            "$'\\x00'git push --force origin main",
            "$'\\u0000'git push --force origin main",
            "$'\\U00000000'git push --force origin main",
            "g$'\\c@'it p$'\\c@'ush --f$'\\c@'orce origin main",
            "$'\\c@'git push --force origin main",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_allows_safe_nul_terminated_ansi_c_fragments(
        self,
    ) -> None:
        commands = (
            "$'\\0'git --version",
            "$'g\\0it' push --force origin main",
            "$'\\c@'git --version",
            "$'g\\c@it' push --force origin main",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual("", process.stdout)
                self.assertEqual("", process.stderr)

    def test_policy_process_denies_force_pushes_rebuilt_by_byte_rules(
        self,
    ) -> None:
        commands = (
            "g\u0000it push --force origin main",
            "g$'\\cࠁ'it p$'\\cࠁ'ush --f$'\\cࠁ'orce origin main",
            "$'\\cࠁ'git push --force origin main",
            "$\u0000'git' push --force origin main",
            '$\u0000"git" push --force origin main',
            "g\\\u0000it push --force origin main",
            "git push --f\\\u0000orce origin main",
            "g\\\u0000\nit push --force origin main",
            "g\\\u0000\r\nit push --force origin main",
            "g$'\\\u0000x69't push --force origin main",
            "g$'\\\u0000c@discard'it push --force origin main",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_policy_process_allows_safe_byte_rule_analogs(self) -> None:
        commands = (
            "\u0000git --version",
            "xg\u0000it push --force origin main",
            "g$'\\cĀ'it push --force origin main",
            "$\u0000'git' --version",
            "xg\\\u0000it push --force origin main",
            "g$'\\\u0000cĀ'it push --force origin main",
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual("", process.stdout)
                self.assertEqual("", process.stderr)

    def test_policy_process_finds_force_push_after_compound_text(self) -> None:
        commands = (
            (
                "deploy() {\n"
                "  cat <<EOF\n"
                "{\n"
                "EOF\n"
                "}\n"
                "git push --force origin main\n"
            ),
            (
                "cat <<EOF\n"
                "git push --force origin main\n"
                "EOF\n"
                "git push --force origin main\n"
            ),
            (
                "printf '%s' 'literal\n"
                "<<EOF\n"
                "literal'\n"
                "git push --force origin main\n"
                "EOF\n"
            ),
            (
                "printf '%s' \"literal\n"
                "<<EOF\n"
                "literal\"\n"
                "git push --force origin main\n"
                "EOF\n"
            ),
            ": $((1 << 2))\ngit push --force origin main\n2\n",
            "((1 << 2))\ngit push --force origin main\n2\n",
            ": ${v:-<<2}\ngit push --force origin main\n2}\n",
            ": ${v//<</2}\ngit push --force origin main\n/2}\n",
            ": $[1 << 2]\ngit push --force origin main\n2]\n",
            (
                "cat <<$'E\\x4fF'\n"
                "safe\n"
                "EOF\n"
                "git push --force origin main\n"
            ),
            (
                ": ${v:-$(cat <<EOF\n"
                "f() {\n"
                "{\n"
                "EOF\n"
                ")}\n"
                "git push --force origin main\n"
            ),
            (
                ": $(( $(cat <<EOF >/dev/null\n"
                "f() {\n"
                "{\n"
                "EOF\n"
                "echo 1) ))\n"
                "git push --force origin main\n"
            ),
        )
        for command in commands:
            with self.subTest(command=command):
                process = self.run_policy(self.policy_payload(command))

                self.assertEqual(0, process.returncode, process.stderr)
                self.assertNotEqual("", process.stdout)
                self.assertEqual(POLICY_DENIAL, json.loads(process.stdout))
                self.assertEqual("", process.stderr)

    def test_codex_hook_wiring_is_exact_and_synchronous(self) -> None:
        hooks_path = BIN_DIR.parent / "seed/.codex/hooks.json"
        self.assertTrue(hooks_path.is_file(), f"missing {hooks_path}")

        self.assertEqual(
            GOOD_CODEX_HOOKS,
            json.loads(hooks_path.read_text(encoding="utf-8")),
        )

    def test_codex_hook_wiring_rejects_async_handlers(self) -> None:
        self.build_good_fixture()
        hooks = json.loads(json.dumps(GOOD_CODEX_HOOKS))
        hooks["hooks"]["PreToolUse"][0]["hooks"][0]["async"] = True
        self.write(self.rendered, ".codex/hooks.json", json.dumps(hooks))

        self.assertTrue(
            any("FAIL [codex-hooks]" in item for item in self.rendered_violations())
        )

    def test_exact_hook_command_runs_from_nested_git_directory(self) -> None:
        hooks_path = BIN_DIR.parent / "seed/.codex/hooks.json"
        self.assertTrue(hooks_path.is_file(), f"missing {hooks_path}")
        self.assertTrue(POLICY_SCRIPT.is_file(), f"missing {POLICY_SCRIPT}")
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
        command = hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        with tempfile.TemporaryDirectory() as temp_dir:
            root = pathlib.Path(temp_dir)
            init = subprocess.run(
                ["git", "init", str(root)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, init.returncode, init.stderr)
            hook = root / ".codex/hooks/pre-tool-policy.py"
            hook.parent.mkdir(parents=True)
            hook.write_text(POLICY_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
            nested = root / "one/two"
            nested.mkdir(parents=True)

            for force, expected_stdout in ((False, ""), (True, POLICY_DENIAL)):
                with self.subTest(force=force):
                    payload = self.policy_payload(
                        "git push --force origin main"
                        if force
                        else "git push origin main"
                    )
                    process = subprocess.run(
                        command,
                        shell=True,
                        cwd=nested,
                        input=payload,
                        text=True,
                        capture_output=True,
                        check=False,
                    )

                    self.assertEqual(0, process.returncode, process.stderr)
                    if force:
                        self.assertEqual(expected_stdout, json.loads(process.stdout))
                    else:
                        self.assertEqual(expected_stdout, process.stdout)
                    self.assertEqual("", process.stderr)

    def test_codex_contract_accepts_bounded_config_hooks_and_rules(self) -> None:
        self.build_good_fixture()

        self.assertEqual((), contract.verify_contract(self.source, self.rendered))

    def test_codex_config_rejects_unknown_root_keys_and_inline_hooks(self) -> None:
        self.build_good_fixture()
        for label, content in (
            (
                "unknown root",
                GOOD_CODEX_CONFIG.replace(
                    "\n[features]",
                    "\nunknown_owned_key = true\n\n[features]",
                    1,
                ),
            ),
            ("inline hooks", GOOD_CODEX_CONFIG + '\n[hooks]\nPreToolUse = []\n'),
        ):
            with self.subTest(label=label):
                self.write(
                    self.rendered,
                    ".codex/config.toml",
                    content,
                )

                self.assertTrue(
                    any(
                        "FAIL [codex-config]" in item
                        for item in self.rendered_violations()
                    )
                )

    def test_codex_config_requires_feature_and_agent_contract(self) -> None:
        self.build_good_fixture()
        mutations = (
            ("hooks disabled", "hooks = true", "hooks = false"),
            ("multi-agent disabled", "multi_agent = true", "multi_agent = false"),
            (
                "Boolean agent limit",
                "max_concurrent_threads_per_session = 6",
                "max_concurrent_threads_per_session = true",
            ),
            (
                "zero agent limit",
                "max_concurrent_threads_per_session = 6",
                "max_concurrent_threads_per_session = 0",
            ),
            (
                "wrong default profile",
                'default_permissions = "project-workspace"',
                'default_permissions = ":workspace"',
            ),
            ("wrong profile base", 'extends = ":workspace"', 'extends = ":read-only"'),
        )
        for label, old, new in mutations:
            with self.subTest(label=label):
                self.write(
                    self.rendered,
                    ".codex/config.toml",
                    GOOD_CODEX_CONFIG.replace(old, new, 1),
                )

                self.assertTrue(
                    any(
                        "FAIL [codex-config]" in item
                        for item in self.rendered_violations()
                    )
                )

    def test_codex_config_requires_every_secret_deny_pattern(self) -> None:
        self.build_good_fixture()
        patterns = (
            ".env",
            ".env*",
            ".env.*",
            ".envrc",
            ".envrc.*",
            "**/.env",
            "**/.env*",
            "**/.env.*",
            "**/.envrc",
            "**/.envrc.*",
        )
        for pattern in patterns:
            with self.subTest(pattern=pattern):
                line = f'"{pattern}" = "deny"\n'
                self.write(
                    self.rendered,
                    ".codex/config.toml",
                    GOOD_CODEX_CONFIG.replace(line, "", 1),
                )

                self.assertTrue(
                    any(
                        "FAIL [codex-config]" in item
                        for item in self.rendered_violations()
                    )
                )

    def test_codex_rules_reject_non_declarative_syntax(self) -> None:
        self.build_good_fixture()
        invalid_rules = (
            "import os\n",
            "value = 1\n",
            'prefix_rule(["git"], decision="allow", justification="x", match=[])\n',
            textwrap.dedent(
                """\
                prefix_rule(
                    pattern=["git"],
                    decision="allow",
                    decision="prompt",
                    justification="x",
                    match=[],
                )
                """
            ),
            'prefix_rule(pattern=["git"], decision="allow", justification="x", match=[], extra=true)\n',
            'prefix_rule(pattern=make_pattern(), decision="allow", justification="x", match=[])\n',
            'other_rule(pattern=["git"], decision="allow", justification="x", match=[])\n',
        )
        for content in invalid_rules:
            with self.subTest(content=content):
                self.write(self.rendered, ".codex/rules/default.rules", content)

                self.assertTrue(
                    any(
                        "FAIL [codex-rules]" in item
                        for item in self.rendered_violations()
                    )
                )

    def test_codex_rules_require_literal_fields(self) -> None:
        self.build_good_fixture()
        base = textwrap.dedent(
            """\
            prefix_rule(
                pattern=["git"],
                decision="allow",
                justification="x",
                match=[],
            )
            """
        )
        mutations = (
            ("missing pattern", "pattern=[\"git\"],\n", ""),
            ("missing decision", 'decision="allow",\n', ""),
            ("missing justification", 'justification="x",\n', ""),
            ("missing match", "match=[],\n", ""),
        )
        for label, old, new in mutations:
            with self.subTest(label=label):
                self.write(
                    self.rendered,
                    ".codex/rules/default.rules",
                    base.replace(old, new, 1),
                )

                self.assertTrue(
                    any(
                        "FAIL [codex-rules]" in item
                        for item in self.rendered_violations()
                    )
                )

    def test_codex_rules_reject_values_outside_native_grammar(self) -> None:
        self.build_good_fixture()
        original = (
            self.rendered / ".codex/rules/default.rules"
        ).read_text(encoding="utf-8")
        invalid_rules = (
            'prefix_rule(pattern=["x"], decision="deny", '
            'justification="x", match=[])\n',
            'prefix_rule(pattern=["x"], decision=[], '
            'justification="x", match=[])\n',
            'prefix_rule(pattern=["x", 1], decision="allow", '
            'justification="x", match=[])\n',
            'prefix_rule(pattern=["x", ["y", 1]], decision="allow", '
            'justification="x", match=[])\n',
            'prefix_rule(pattern=["x"], decision="allow", '
            'justification="x", match=[1])\n',
            'prefix_rule(pattern=["x"], decision="allow", '
            'justification="x", match=[["x", 1]])\n',
            'prefix_rule(pattern=[], decision="allow", '
            'justification="x", match=[])\n',
            'prefix_rule(pattern=["x", []], decision="allow", '
            'justification="x", match=[])\n',
        )
        for invalid_rule in invalid_rules:
            with self.subTest(invalid_rule=invalid_rule):
                self.write(
                    self.rendered,
                    ".codex/rules/default.rules",
                    original + invalid_rule,
                )

                try:
                    violations = self.rendered_violations()
                except (TypeError, ValueError) as error:
                    self.fail(f"literal grammar validation raised {error!r}")
                self.assertTrue(
                    any(
                        "FAIL [codex-rules]" in item
                        for item in violations
                    )
                )

    def test_codex_rules_require_every_policy_family(self) -> None:
        self.build_good_fixture()
        required_patterns = (
            '["cat", "ls", "grep", "rg", "head", "tail", "sed", "echo", "wc", "mkdir"]',
            '["git", ["status", "log", "diff"]]',
            '["rm", "-rf"]',
            '["rm", "-fr"]',
            '["git", "push", "--force"]',
            '["git", "push", "--force-with-lease"]',
            '["git", "reset", "--hard"]',
            '["git", "push"]',
        )
        original = (self.rendered / ".codex/rules/default.rules")
        rules = original.read_text(encoding="utf-8")
        for pattern in required_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, rules)
                self.write(
                    self.rendered,
                    ".codex/rules/default.rules",
                    rules.replace(pattern, '["removed"]', 1),
                )

                self.assertTrue(
                    any(
                        "FAIL [codex-rules]" in item
                        for item in self.rendered_violations()
                    )
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
