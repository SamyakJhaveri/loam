#!/usr/bin/env python3
"""Verify the contract shared by Loam's source and rendered harness."""

from __future__ import annotations

import argparse
import ast
import dataclasses
import json
import os
import pathlib
import shlex
import stat
import subprocess
import sys
import tomllib
from collections.abc import Sequence


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
    ".claude/skills/catchup",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/hooks/pre-tool-policy.py",
    ".codex/rules/default.rules",
)

FORBIDDEN_RENDERED_PATHS = (
    ".mcp.json",
    ".claude/agents",
    ".claude/rules",
    ".claude/stale-counts.json",
    ".claude/codex-reviews",
    ".claude/hooks/post-compact-recovery.sh",
    ".claude/skills/reassess-template-sync",
    ".agents/skills/agent-team",
    ".codex/reassess-hooks.json",
    ".codex/agents",
    ".codex/mcp",
    "_research",
)

# The rendered .claude/settings.json must not pin a model. A template cannot
# know the right model for a given user or machine; any pinned string ages out
# within weeks of a new release; and the local settings template used to
# override the pin anyway, so the pin was dead weight. The user's global default
# decides the model instead.

CLAUDE_HOOK_ROUTES = {
    "PreToolUse": (
        ("Bash", ".claude/hooks/bash-audit-log.sh"),
        ("Bash|Edit|Write", ".claude/hooks/concurrent-checkout-guard.sh"),
    ),
    "PostToolUse": (("Edit|Write", ".claude/hooks/ruff-after-edit.sh"),),
    "Stop": ((None, ".claude/hooks/stop-verify-gate.sh"),),
}

CODEX_HOOKS = {
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

CODEX_POLICY_DENIAL = {
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": (
            "Force pushes are blocked by repository policy."
        ),
    }
}

CODEX_SECRET_DENIES = {
    ".env": "deny",
    ".env*": "deny",
    ".env.*": "deny",
    ".envrc": "deny",
    ".envrc.*": "deny",
    "**/.env": "deny",
    "**/.env*": "deny",
    "**/.env.*": "deny",
    "**/.envrc": "deny",
    "**/.envrc.*": "deny",
}

CODEX_REQUIRED_RULES = (
    (
        [["cat", "ls", "grep", "rg", "head", "tail", "echo", "wc", "mkdir"]],
        "allow",
    ),
    (["git", ["status", "log", "diff"]], "allow"),
    (["rm", "-rf"], "forbidden"),
    (["rm", "-fr"], "forbidden"),
    (["git", "push", "--force"], "forbidden"),
    (["git", "push", "--force-with-lease"], "forbidden"),
    (["git", "reset", "--hard"], "forbidden"),
    (["git", "push"], "prompt"),
)

PROSE_ROUTE_REFERENCES = (
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

PROSE_ROUTE_TARGETS = (
    ("CLAUDE.md", "AGENTS.md"),
    ("AGENTS.md", ".codex"),
    ("AGENTS.md", ".agents/skills"),
    ("CLAUDE.md", ".claude/hooks/stop-verify-gate.sh"),
    ("CLAUDE.md", ".agents/skills/catchup/SKILL.md"),
    ("CLAUDE.md", ".claude/hooks/bash-audit-log.sh"),
    ("CLAUDE.md", ".claude/hooks/concurrent-checkout-guard.sh"),
    ("CLAUDE.md", ".claude/hooks/ruff-after-edit.sh"),
)

MARKETPLACE_MANIFEST = "cultivation/marketplace/.claude-plugin/marketplace.json"

DISTRIBUTION_MIRRORS = (
    (
        "seed/.claude/hooks/concurrent-checkout-guard.sh",
        (
            "cultivation/marketplace/sam-cc-setup/hooks/"
            "concurrent-checkout-guard.sh"
        ),
    ),
)


@dataclasses.dataclass(frozen=True, order=True)
class Violation:
    area: str
    detail: str

    def render(self) -> str:
        return f"FAIL [{self.area}]: {self.detail}"


def _path_exists(path: pathlib.Path) -> bool:
    return path.exists() or path.is_symlink()


def _check_topology(
    source_root: pathlib.Path,
    rendered_root: pathlib.Path,
    violations: list[Violation],
) -> None:
    for relative_path in REQUIRED_SOURCE_PATHS:
        if not _path_exists(source_root / relative_path):
            violations.append(
                Violation("topology", f"missing required source path: {relative_path}")
            )

    for relative_path in REQUIRED_RENDERED_PATHS:
        path = rendered_root / relative_path
        if not _path_exists(path):
            violations.append(
                Violation("topology", f"missing required rendered path: {relative_path}")
            )
        elif relative_path != ".claude/skills/catchup" and (
            path.is_symlink()
            or not _is_regular_file_inside_root(path, rendered_root)
        ):
            violations.append(
                Violation(
                    "topology",
                    "required rendered path must be a direct regular file "
                    f"inside rendered root: {relative_path}",
                )
            )

    for relative_path in FORBIDDEN_RENDERED_PATHS:
        if _path_exists(rendered_root / relative_path):
            violations.append(
                Violation("topology", f"forbidden rendered path exists: {relative_path}")
            )


def _check_distribution_mirrors(
    source_root: pathlib.Path,
    violations: list[Violation],
) -> None:
    for canonical_relative, mirror_relative in DISTRIBUTION_MIRRORS:
        paths = (
            ("canonical", canonical_relative, source_root / canonical_relative),
            ("mirror", mirror_relative, source_root / mirror_relative),
        )
        readable: dict[str, bytes] = {}
        for role, relative_path, path in paths:
            if not _path_exists(path):
                violations.append(
                    Violation(
                        "distribution-mirrors",
                        f"missing {role} file: {relative_path}",
                    )
                )
                continue
            if path.is_symlink() or not path.is_file():
                violations.append(
                    Violation(
                        "distribution-mirrors",
                        f"{role} must be a direct regular file: {relative_path}",
                    )
                )
                continue
            execute_bits = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            if not path.stat().st_mode & execute_bits:
                violations.append(
                    Violation(
                        "distribution-mirrors",
                        f"{role} must be executable: {relative_path}",
                    )
                )
            try:
                readable[role] = path.read_bytes()
            except OSError:
                violations.append(
                    Violation(
                        "distribution-mirrors",
                        f"{role} must be readable: {relative_path}",
                    )
                )

        if (
            readable.get("canonical") is not None
            and readable.get("mirror") is not None
            and readable["canonical"] != readable["mirror"]
        ):
            violations.append(
                Violation(
                    "distribution-mirrors",
                    f"{mirror_relative} must be byte-identical to {canonical_relative}",
                )
            )


def _check_marketplace(
    source_root: pathlib.Path,
    violations: list[Violation],
) -> tuple[pathlib.Path, ...]:
    manifest_path = source_root / MARKETPLACE_MANIFEST
    content = _read_text(manifest_path)
    if content is None:
        violations.append(
            Violation("marketplace", f"{MARKETPLACE_MANIFEST} must be readable")
        )
        return ()
    try:
        manifest = json.loads(content)
    except json.JSONDecodeError as error:
        violations.append(
            Violation(
                "marketplace",
                f"{MARKETPLACE_MANIFEST} must contain valid JSON: {error.msg}",
            )
        )
        return ()
    if not isinstance(manifest, dict):
        violations.append(
            Violation(
                "marketplace",
                f"{MARKETPLACE_MANIFEST} must contain a JSON object",
            )
        )
        return ()
    plugins = manifest.get("plugins")
    if not isinstance(plugins, list):
        violations.append(
            Violation(
                "marketplace",
                f"{MARKETPLACE_MANIFEST} plugins must be a JSON array",
            )
        )
        return ()

    marketplace_root = manifest_path.parents[1].resolve()
    local_roots: list[pathlib.Path] = []
    for index, plugin in enumerate(plugins):
        if not isinstance(plugin, dict):
            violations.append(
                Violation(
                    "marketplace",
                    f"plugin entry {index} must be a JSON object",
                )
            )
            continue
        source = plugin.get("source")
        if not isinstance(source, str):
            continue
        if not source or "\n" in source or "\r" in source:
            violations.append(
                Violation(
                    "marketplace",
                    f"plugin entry {index} has an invalid local source",
                )
            )
            continue

        candidate = marketplace_root / source
        try:
            resolved = candidate.resolve()
            resolved.relative_to(marketplace_root)
        except (OSError, RuntimeError, ValueError):
            violations.append(
                Violation(
                    "marketplace",
                    f"local source escapes marketplace root: {source}",
                )
            )
            continue
        if not resolved.is_dir():
            violations.append(
                Violation(
                    "marketplace",
                    f"missing local plugin root: {source}",
                )
            )
            continue

        local_roots.append(resolved)
        hooks_path = resolved / "hooks/hooks.json"
        if not _path_exists(hooks_path):
            continue
        hooks_content = _read_text(hooks_path)
        relative_hooks = hooks_path.relative_to(source_root.resolve()).as_posix()
        if hooks_content is None:
            violations.append(
                Violation("marketplace", f"{relative_hooks} must be readable")
            )
            continue
        try:
            hooks = json.loads(hooks_content)
        except json.JSONDecodeError as error:
            violations.append(
                Violation(
                    "marketplace",
                    f"{relative_hooks} must contain valid JSON: {error.msg}",
                )
            )
            continue
        if not isinstance(hooks, dict):
            violations.append(
                Violation(
                    "marketplace",
                    f"{relative_hooks} must contain a JSON object",
                )
            )

    return tuple(sorted(set(local_roots)))


def _read_text(path: pathlib.Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None


def _shell_words(command: str) -> tuple[str, ...]:
    try:
        return tuple(shlex.split(command, comments=True, posix=True))
    except ValueError:
        return ()


def _shell_tokens(command: str) -> tuple[str, ...]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|<>")
        return tuple(lexer)
    except ValueError:
        return ()


def _heredoc_delimiters(command: str) -> tuple[tuple[str, bool], ...]:
    tokens = _shell_tokens(command)
    delimiters: list[tuple[str, bool]] = []
    for index, token in enumerate(tokens[:-1]):
        if token != "<<":
            continue
        delimiter = tokens[index + 1]
        strip_tabs = delimiter.startswith("-")
        if strip_tabs:
            delimiter = delimiter[1:]
        if delimiter:
            delimiters.append((delimiter, strip_tabs))
    return tuple(delimiters)


def _active_shell_lines(content: str | None) -> tuple[tuple[int, str], ...]:
    if content is None:
        return ()
    active_lines: list[tuple[int, str]] = []
    pending_heredocs: list[tuple[str, bool]] = []
    for line_number, line in enumerate(content.splitlines()):
        if pending_heredocs:
            delimiter, strip_tabs = pending_heredocs[0]
            candidate = line.lstrip("\t") if strip_tabs else line
            if candidate == delimiter:
                pending_heredocs.pop(0)
            continue
        active_lines.append((line_number, line))
        pending_heredocs.extend(_heredoc_delimiters(line))
    return tuple(active_lines)


def _shell_command_position(content: str | None, marker: str) -> int:
    marker_words = _shell_words(marker)
    for line_number, line in _active_shell_lines(content):
        words = _shell_words(line)
        if words[: len(marker_words)] == marker_words:
            return line_number
    return -1


def _declares_shell_function(line: str) -> bool:
    words = _shell_words(line)
    if not words:
        return False
    if words[0] == "function":
        return len(words) >= 2
    if words[0].endswith(("()", "(){")):
        return True
    return len(words) >= 2 and words[1] == "()"


def _release_block_boundary(words: tuple[str, ...]) -> int:
    if not words:
        return 0
    first = words[0]
    if first in {"if", "for", "while", "until", "select", "case", "{", "("}:
        return 1
    if first in {"fi", "done", "esac", "}", ")"}:
        return -1
    return 0


def _release_gate_position(content: str | None, marker: str) -> int:
    marker_words = _shell_words(marker)
    function_declared = False
    block_depth = 0
    for line_number, line in _active_shell_lines(content):
        function_declared = function_declared or _declares_shell_function(line)
        words = _shell_words(line)
        boundary = _release_block_boundary(words)
        if boundary < 0:
            if block_depth == 0:
                return -1
            block_depth -= 1
        elif boundary > 0 and not _declares_shell_function(line):
            block_depth += 1
        if line != line.lstrip():
            continue
        if (
            not function_declared
            and block_depth == 0
            and words[: len(marker_words)] == marker_words
            and words[len(marker_words) : len(marker_words) + 2] == ("||", "die")
            and len(words) == len(marker_words) + 3
        ):
            return line_number
    return -1


def _mapping_value(text: str, key: str) -> str | None:
    if text.startswith("#"):
        return None
    prefix = f"{key}:"
    if not text.startswith(prefix):
        return None
    return text[len(prefix) :].strip()


def _workflow_steps(
    content: str | None,
) -> tuple[tuple[int, dict[str, str]], ...]:
    if content is None:
        return ()
    steps: list[tuple[int, dict[str, str]]] = []
    steps_indent: int | None = None
    list_indent: int | None = None
    current_line: int | None = None
    current: dict[str, str] = {}

    def finish_step() -> None:
        nonlocal current_line, current
        if current_line is not None:
            steps.append((current_line, current))
        current_line = None
        current = {}

    def record_field(text: str) -> None:
        for key in ("run", "uses", "if", "continue-on-error"):
            value = _mapping_value(text, key)
            if value is not None:
                current[key] = value if key not in current else "\0duplicate"
                return

    for line_number, line in enumerate(content.splitlines()):
        stripped = line.lstrip(" ")
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(stripped)

        if steps_indent is None:
            if stripped == "steps:" or stripped.startswith("steps: #"):
                steps_indent = indent
            continue

        if indent <= steps_indent:
            finish_step()
            steps_indent = None
            list_indent = None
            if stripped == "steps:" or stripped.startswith("steps: #"):
                steps_indent = indent
            continue

        if list_indent is None:
            if not stripped.startswith("- "):
                continue
            list_indent = indent

        if indent == list_indent and stripped.startswith("- "):
            finish_step()
            current_line = line_number
            record_field(stripped[2:].lstrip())
        elif indent == list_indent + 2:
            record_field(stripped)
    finish_step()
    return tuple(steps)


def _workflow_gate_is_unconditional(step: dict[str, str]) -> bool:
    return "if" not in step and step.get("continue-on-error", "false") == "false"


def _workflow_run_position(content: str | None, marker: str) -> int:
    marker_words = _shell_words(marker)
    for line_number, step in _workflow_steps(content):
        value = step.get("run")
        if value is None or not _workflow_gate_is_unconditional(step):
            continue
        words = _shell_words(value)
        if words == marker_words:
            return line_number
    return -1


def _workflow_uses_position(content: str | None, marker: str) -> int:
    for line_number, step in _workflow_steps(content):
        value = step.get("uses")
        if value is None:
            continue
        if value == marker or value.startswith(f"{marker}@"):
            return line_number
    return -1


def _check_marker_positions(
    relative_path: str,
    first_marker: str,
    second_marker: str | None,
    first_position: int,
    second_position: int | None,
    violations: list[Violation],
) -> None:
    if first_position < 0:
        detail = f"{relative_path} must call {first_marker}"
    elif second_marker is not None and second_position is not None:
        if second_position < 0:
            detail = f"{relative_path} must contain ordering marker {second_marker}"
        elif first_position > second_position:
            detail = (
                f"{relative_path} must run {first_marker} before {second_marker}"
            )
        else:
            return
    else:
        return

    violations.append(Violation("release-callers", detail))


def _check_release_callers(
    source_root: pathlib.Path,
    violations: list[Violation],
) -> None:
    test_workflow = _read_text(source_root / ".github/workflows/test.yml")
    _check_marker_positions(
        ".github/workflows/test.yml",
        "bin/verify-template.sh",
        None,
        _workflow_run_position(test_workflow, "bin/verify-template.sh"),
        None,
        violations,
    )

    release_workflow = _read_text(source_root / ".github/workflows/release.yml")
    _check_marker_positions(
        ".github/workflows/release.yml",
        "bin/verify-template.sh",
        "softprops/action-gh-release",
        _workflow_run_position(release_workflow, "bin/verify-template.sh"),
        _workflow_uses_position(release_workflow, "softprops/action-gh-release"),
        violations,
    )

    release_script = _read_text(source_root / "bin/release.sh")
    _check_marker_positions(
        "bin/release.sh",
        'bash "$SELF_DIR/verify-template.sh"',
        'echo "$VERSION" > VERSION',
        _release_gate_position(
            release_script, 'bash "$SELF_DIR/verify-template.sh"'
        ),
        _shell_command_position(release_script, 'echo "$VERSION" > VERSION'),
        violations,
    )


def _check_symlinks(
    rendered_root: pathlib.Path,
    violations: list[Violation],
) -> None:
    relative_path = ".claude/skills/catchup"
    link = rendered_root / relative_path
    if not link.is_symlink():
        violations.append(Violation("symlinks", f"{relative_path} must be a symlink"))
        return

    try:
        raw_target = os.readlink(link)
        root = rendered_root.resolve()
        resolved_target = link.resolve()
    except (OSError, RuntimeError) as error:
        violations.append(
            Violation("symlinks", f"cannot resolve {relative_path}: {error}")
        )
        return

    try:
        resolved_target.relative_to(root)
    except ValueError:
        violations.append(
            Violation(
                "symlinks",
                f"{relative_path} resolves outside rendered root: {raw_target}",
            )
        )
        return

    expected_target = (rendered_root / ".agents/skills/catchup").resolve()
    if resolved_target != expected_target:
        violations.append(
            Violation(
                "symlinks",
                f"{relative_path} must resolve to .agents/skills/catchup; "
                f"found {raw_target}",
            )
        )
        return

    if not (resolved_target / "SKILL.md").is_file():
        violations.append(
            Violation(
                "symlinks",
                f"{relative_path} target must contain SKILL.md",
            )
        )


def _read_claude_settings(
    rendered_root: pathlib.Path,
    violations: list[Violation],
) -> dict[str, object] | None:
    settings_path = rendered_root / ".claude/settings.json"
    content = _read_text(settings_path)
    if content is None:
        violations.append(
            Violation("claude-hooks", ".claude/settings.json must be readable")
        )
        return None
    try:
        settings = json.loads(content)
    except json.JSONDecodeError as error:
        violations.append(
            Violation(
                "claude-hooks",
                f".claude/settings.json must contain valid JSON: {error.msg}",
            )
        )
        return None
    if not isinstance(settings, dict):
        violations.append(
            Violation(
                "claude-hooks",
                ".claude/settings.json must contain a JSON object",
            )
        )
        return None
    return settings


def _command_script_targets(command: str) -> tuple[str, ...]:
    targets: list[str] = []
    for word in _shell_words(command):
        normalized = word[2:] if word.startswith("./") else word
        if normalized.startswith((".claude/", ".codex/")) and normalized.endswith(
            (".sh", ".py")
        ):
            targets.append(normalized)
    return tuple(targets)


def _is_regular_file_inside_root(
    path: pathlib.Path,
    root: pathlib.Path,
) -> bool:
    try:
        resolved_path = path.resolve(strict=True)
        resolved_path.relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return False
    return resolved_path.is_file()


def _is_get_assignment(
    statement: ast.stmt,
    target_name: str,
    receiver_name: str,
    key: str,
) -> bool:
    if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
        return False
    target = statement.targets[0]
    call = statement.value
    if isinstance(call, ast.IfExp):
        call = call.body
    return (
        isinstance(target, ast.Name)
        and target.id == target_name
        and isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and call.func.attr == "get"
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == receiver_name
        and len(call.args) == 1
        and isinstance(call.args[0], ast.Constant)
        and call.args[0].value == key
    )


def _ruff_reads_nested_file_path(content: str | None) -> bool:
    if content is None:
        return False
    prefix = "python3 -c '\n"
    suffix = "\n' 2>/dev/null"
    start = content.find(prefix)
    if start < 0:
        return False
    start += len(prefix)
    end = content.find(suffix, start)
    if end < 0:
        return False
    try:
        tree = ast.parse(content[start:end])
    except SyntaxError:
        return False
    return any(
        _is_get_assignment(statement, "tool_input", "payload", "tool_input")
        for statement in ast.walk(tree)
    ) and any(
        _is_get_assignment(statement, "file_path", "tool_input", "file_path")
        for statement in ast.walk(tree)
    )


def _check_claude_model(
    rendered_root: pathlib.Path,
    violations: list[Violation],
) -> None:
    settings = _read_claude_settings(rendered_root, violations)
    if settings is None:
        return
    if "model" in settings:
        violations.append(
            Violation(
                "claude-model",
                ".claude/settings.json must not pin a model; the user's "
                "global default decides",
            )
        )


def _check_claude_hooks(
    source_root: pathlib.Path,
    rendered_root: pathlib.Path,
    violations: list[Violation],
) -> tuple[str, ...]:
    settings = _read_claude_settings(rendered_root, violations)
    if settings is None:
        return ()

    hooks = settings.get("hooks")
    if not isinstance(hooks, dict):
        violations.append(
            Violation("claude-hooks", "settings hooks must be a JSON object")
        )
        return ()

    expected_events = set(CLAUDE_HOOK_ROUTES)
    actual_events = set(hooks)
    if actual_events != expected_events:
        violations.append(
            Violation(
                "claude-hooks",
                "owned events must equal PreToolUse, PostToolUse, and Stop; "
                f"found {', '.join(sorted(actual_events)) or 'none'}",
            )
        )

    actual_routes: list[tuple[str, str | None, str]] = []
    script_targets: set[str] = set()
    for event in sorted(expected_events):
        routes = hooks.get(event)
        if not isinstance(routes, list):
            violations.append(
                Violation("claude-hooks", f"{event} routes must be a JSON array")
            )
            continue
        for route_index, route in enumerate(routes):
            if not isinstance(route, dict):
                violations.append(
                    Violation(
                        "claude-hooks",
                        f"{event} route {route_index} must be a JSON object",
                    )
                )
                continue
            matcher = route.get("matcher")
            handlers = route.get("hooks")
            if not isinstance(handlers, list) or not handlers:
                violations.append(
                    Violation(
                        "claude-hooks",
                        f"{event} route {route_index} must contain command handlers",
                    )
                )
                continue
            for handler_index, handler in enumerate(handlers):
                if (
                    not isinstance(handler, dict)
                    or handler.get("type") != "command"
                    or not isinstance(handler.get("command"), str)
                    or not handler["command"]
                ):
                    violations.append(
                        Violation(
                            "claude-hooks",
                            f"{event} route {route_index} handler {handler_index} "
                            "must be a command handler",
                        )
                    )
                    continue
                command = handler["command"]
                actual_routes.append((event, matcher, command))
                script_targets.update(_command_script_targets(command))
                if "ruff" in command and command != ".claude/hooks/ruff-after-edit.sh":
                    violations.append(
                        Violation(
                            "claude-hooks",
                            "inline Ruff command is forbidden; route through "
                            ".claude/hooks/ruff-after-edit.sh",
                        )
                    )

    expected_routes = [
        (event, matcher, command)
        for event, routes in CLAUDE_HOOK_ROUTES.items()
        for matcher, command in routes
    ]
    expected_matchers = sorted(
        (event, matcher)
        for event, routes in CLAUDE_HOOK_ROUTES.items()
        for matcher, _ in routes
    )
    actual_matchers = sorted(
        ((event, matcher) for event, matcher, _ in actual_routes),
        key=repr,
    )
    if actual_matchers != sorted(expected_matchers, key=repr):
        violations.append(
            Violation("claude-hooks", "owned matchers do not equal design values")
        )
    if sorted(actual_routes, key=repr) != sorted(expected_routes, key=repr):
        violations.append(
            Violation(
                "claude-hooks",
                "owned command routes must include .claude/hooks/ruff-after-edit.sh",
            )
        )

    for relative_path in sorted(script_targets):
        path = rendered_root / relative_path
        if not _path_exists(path):
            violations.append(
                Violation(
                    "claude-hooks",
                    f"repository script target does not exist: {relative_path}",
                )
            )
        elif not _is_regular_file_inside_root(path, rendered_root):
            violations.append(
                Violation(
                    "claude-hooks",
                    "repository script target must be a regular file inside "
                    f"rendered root: {relative_path}",
                )
            )
        elif _read_text(path) is None:
            violations.append(
                Violation(
                    "claude-hooks",
                    f"repository script target must be readable: {relative_path}",
                )
            )

    ruff_content = _read_text(rendered_root / ".claude/hooks/ruff-after-edit.sh")
    source_ruff_content = _read_text(
        source_root / "seed/.claude/hooks/ruff-after-edit.sh"
    )
    if source_ruff_content is None:
        violations.append(
            Violation("claude-hooks", "source ruff-after-edit.sh must be readable")
        )
    elif ruff_content is not None and ruff_content != source_ruff_content:
        violations.append(
            Violation(
                "claude-hooks",
                "rendered ruff-after-edit.sh must match the tested source adapter",
            )
        )
    if ruff_content is not None and not _ruff_reads_nested_file_path(ruff_content):
        violations.append(
            Violation(
                "claude-hooks",
                "ruff-after-edit.sh must read tool_input.file_path",
            )
        )

    return tuple(sorted(script_targets))


def _read_json_object(
    path: pathlib.Path,
    area: str,
    violations: list[Violation],
) -> dict[str, object] | None:
    if not _path_exists(path):
        return None
    content = _read_text(path)
    if content is None:
        violations.append(Violation(area, f"{path.name} must be readable"))
        return None
    try:
        value = json.loads(content)
    except json.JSONDecodeError as error:
        violations.append(
            Violation(area, f"{path.name} must contain valid JSON: {error.msg}")
        )
        return None
    if not isinstance(value, dict):
        violations.append(Violation(area, f"{path.name} must contain a JSON object"))
        return None
    return value


def _policy_envelope(command: str) -> str:
    return json.dumps(
        {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
        }
    )


def _run_codex_policy_probe(
    policy_path: pathlib.Path,
    command: str,
    violations: list[Violation],
) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            [sys.executable, str(policy_path)],
            input=_policy_envelope(command),
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        violations.append(
            Violation("codex-hooks", f"policy process could not run: {error}")
        )
        return None


def _check_codex_hooks(
    rendered_root: pathlib.Path,
    violations: list[Violation],
) -> tuple[str, ...]:
    hooks = _read_json_object(
        rendered_root / ".codex/hooks.json",
        "codex-hooks",
        violations,
    )
    if hooks is not None and hooks != CODEX_HOOKS:
        violations.append(
            Violation(
                "codex-hooks",
                ".codex/hooks.json must contain the exact synchronous Bash policy route",
            )
        )

    relative_path = ".codex/hooks/pre-tool-policy.py"
    policy_path = rendered_root / relative_path
    if not _is_regular_file_inside_root(policy_path, rendered_root):
        violations.append(
            Violation(
                "codex-hooks",
                f"policy process must be a regular file inside rendered root: {relative_path}",
            )
        )
        return ()

    normal = _run_codex_policy_probe(policy_path, "git push origin main", violations)
    if normal is not None and (
        normal.returncode != 0 or normal.stdout != "" or normal.stderr != ""
    ):
        violations.append(
            Violation("codex-hooks", "policy process must allow a normal Git push silently")
        )

    force = _run_codex_policy_probe(
        policy_path,
        "git push --force origin main",
        violations,
    )
    if force is not None:
        try:
            decision = json.loads(force.stdout)
        except json.JSONDecodeError:
            decision = None
        if (
            force.returncode != 0
            or force.stderr != ""
            or decision != CODEX_POLICY_DENIAL
        ):
            violations.append(
                Violation(
                    "codex-hooks",
                    "policy process must deny a direct force push with the design result",
                )
            )
    return (relative_path,)


def _check_codex_config(
    rendered_root: pathlib.Path,
    violations: list[Violation],
) -> None:
    relative_path = ".codex/config.toml"
    path = rendered_root / relative_path
    if not _path_exists(path):
        return
    content = _read_text(path)
    if content is None:
        violations.append(Violation("codex-config", f"{relative_path} must be readable"))
        return
    try:
        config = tomllib.loads(content)
    except tomllib.TOMLDecodeError as error:
        violations.append(
            Violation("codex-config", f"{relative_path} must contain valid TOML: {error}")
        )
        return

    if set(config) != {"default_permissions", "features", "agents", "permissions"}:
        violations.append(
            Violation(
                "codex-config",
                "root keys must equal default_permissions, features, agents, and permissions",
            )
        )
    if config.get("default_permissions") != "project-workspace":
        violations.append(
            Violation("codex-config", "default_permissions must be project-workspace")
        )

    features = config.get("features")
    if features != {"hooks": True, "multi_agent": True}:
        violations.append(
            Violation(
                "codex-config",
                "features must enable only hooks and multi_agent",
            )
        )

    agents = config.get("agents")
    limit = (
        agents.get("max_concurrent_threads_per_session")
        if isinstance(agents, dict)
        else None
    )
    if not isinstance(agents, dict) or set(agents) != {
        "max_concurrent_threads_per_session"
    }:
        violations.append(
            Violation("codex-config", "agents must contain only the concurrency limit")
        )
    if type(limit) is not int or limit <= 0:
        violations.append(
            Violation("codex-config", "agent concurrency limit must be a positive integer")
        )

    expected_profile = {
        "description": "Workspace editing with project secret-file denies.",
        "extends": ":workspace",
        "filesystem": {":workspace_roots": CODEX_SECRET_DENIES},
    }
    if config.get("permissions") != {"project-workspace": expected_profile}:
        violations.append(
            Violation(
                "codex-config",
                "permissions must equal the bounded project-workspace profile",
            )
        )


def _literal_prefix_rules(
    content: str,
    violations: list[Violation],
) -> tuple[dict[str, object], ...] | None:
    try:
        tree = ast.parse(content)
    except SyntaxError as error:
        violations.append(
            Violation("codex-rules", f"default.rules must parse as expressions: {error.msg}")
        )
        return None

    rules: list[dict[str, object]] = []
    required_keywords = {"pattern", "decision", "justification", "match"}
    for statement in tree.body:
        if not (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Call)
            and isinstance(statement.value.func, ast.Name)
            and statement.value.func.id == "prefix_rule"
        ):
            violations.append(
                Violation("codex-rules", "default.rules may contain only prefix_rule calls")
            )
            return None
        call = statement.value
        if call.args:
            violations.append(
                Violation("codex-rules", "prefix_rule does not accept positional arguments")
            )
            return None
        names = [keyword.arg for keyword in call.keywords]
        if None in names or len(names) != len(set(names)) or set(names) != required_keywords:
            violations.append(
                Violation(
                    "codex-rules",
                    "prefix_rule keywords must equal pattern, decision, justification, and match",
                )
            )
            return None
        values: dict[str, object] = {}
        try:
            for keyword in call.keywords:
                assert keyword.arg is not None
                values[keyword.arg] = ast.literal_eval(keyword.value)
        except (ValueError, TypeError):
            violations.append(
                Violation("codex-rules", "prefix_rule values must be literals")
            )
            return None
        pattern = values["pattern"]
        decision = values["decision"]
        justification = values["justification"]
        examples = values["match"]
        pattern_is_valid = (
            isinstance(pattern, list)
            and bool(pattern)
            and all(
                isinstance(element, str)
                or (
                    isinstance(element, list)
                    and bool(element)
                    and all(isinstance(option, str) for option in element)
                )
                for element in pattern
            )
        )
        examples_are_valid = isinstance(examples, list) and all(
            (isinstance(example, str) and bool(example))
            or (
                isinstance(example, list)
                and bool(example)
                and all(isinstance(token, str) for token in example)
            )
            for example in examples
        )
        if (
            not pattern_is_valid
            or not isinstance(decision, str)
            or decision not in {"allow", "prompt", "forbidden"}
            or not isinstance(justification, str)
            or not justification
            or not examples_are_valid
        ):
            violations.append(
                Violation(
                    "codex-rules",
                    "prefix_rule literal fields do not match native grammar",
                )
            )
            return None
        rules.append(values)
    return tuple(rules)


def _check_codex_rules(
    rendered_root: pathlib.Path,
    violations: list[Violation],
) -> None:
    relative_path = ".codex/rules/default.rules"
    path = rendered_root / relative_path
    if not _path_exists(path):
        return
    content = _read_text(path)
    if content is None:
        violations.append(Violation("codex-rules", f"{relative_path} must be readable"))
        return
    rules = _literal_prefix_rules(content, violations)
    if rules is None:
        return
    for pattern, decision in CODEX_REQUIRED_RULES:
        if not any(
            rule["pattern"] == pattern and rule["decision"] == decision
            for rule in rules
        ):
            violations.append(
                Violation(
                    "codex-rules",
                    f"missing required {decision} rule for pattern {pattern!r}",
                )
            )


def _check_prose_routes(
    rendered_root: pathlib.Path,
    violations: list[Violation],
) -> None:
    documents = {
        document: _read_text(rendered_root / document)
        for document, _ in PROSE_ROUTE_REFERENCES
    }
    for document, reference in PROSE_ROUTE_REFERENCES:
        content = documents[document]
        if content is None or reference not in content:
            violations.append(
                Violation(
                    "prose-routes",
                    f"{document} must reference {reference}",
                )
            )

    for document, target in PROSE_ROUTE_TARGETS:
        if not _path_exists(rendered_root / target):
            violations.append(
                Violation(
                    "prose-routes",
                    f"{document} route target does not exist: {target}",
                )
            )

    claude_content = documents.get("CLAUDE.md")
    if claude_content is not None and any(
        "`docs/`" in line and "Add rows here" in line
        for line in claude_content.splitlines()
    ):
        violations.append(
            Violation(
                "prose-routes",
                "CLAUDE.md contains unresolved docs/ placeholder",
            )
        )


def _check_executable_modes(
    rendered_root: pathlib.Path,
    script_targets: Sequence[str],
    violations: list[Violation],
) -> None:
    execute_bits = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    for relative_path in script_targets:
        path = rendered_root / relative_path
        try:
            mode = path.stat().st_mode
        except OSError:
            continue
        if not mode & execute_bits:
            violations.append(
                Violation(
                    "executable-modes",
                    f"repository script is not executable: {relative_path}",
                )
            )

def verify_contract(
    source_root: pathlib.Path,
    rendered_root: pathlib.Path,
) -> tuple[Violation, ...]:
    violations: list[Violation] = []
    _check_topology(source_root, rendered_root, violations)
    _check_distribution_mirrors(source_root, violations)
    _check_marketplace(source_root, violations)
    _check_release_callers(source_root, violations)
    _check_symlinks(rendered_root, violations)
    _check_claude_model(rendered_root, violations)
    claude_script_targets = _check_claude_hooks(
        source_root, rendered_root, violations
    )
    codex_script_targets = _check_codex_hooks(rendered_root, violations)
    _check_codex_config(rendered_root, violations)
    _check_codex_rules(rendered_root, violations)
    _check_prose_routes(rendered_root, violations)
    _check_executable_modes(
        rendered_root,
        claude_script_targets + codex_script_targets,
        violations,
    )
    return tuple(sorted(violations))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=pathlib.Path)
    parser.add_argument("--rendered-root", type=pathlib.Path)
    parser.add_argument("--list-local-plugin-roots", action="store_true")
    arguments = parser.parse_args(argv)

    if arguments.list_local_plugin_roots:
        violations: list[Violation] = []
        roots = _check_marketplace(arguments.source_root, violations)
        for violation in sorted(violations):
            print(violation.render())
        if violations:
            return 1
        source_root = arguments.source_root.resolve()
        for root in roots:
            print(root.relative_to(source_root).as_posix())
        return 0

    if arguments.rendered_root is None:
        parser.error("--rendered-root is required unless listing local plugin roots")

    violations = verify_contract(arguments.source_root, arguments.rendered_root)
    for violation in violations:
        print(violation.render())
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
