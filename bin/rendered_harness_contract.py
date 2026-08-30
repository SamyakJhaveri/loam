#!/usr/bin/env python3
"""Verify the contract shared by Loam's source and rendered harness."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
import shlex
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
    ".claude/hooks/post-compact-recovery.sh",
    ".claude/skills/reassess-template-sync",
    ".agents/skills/agent-team",
    ".codex/reassess-hooks.json",
    ".codex/agents",
    ".codex/mcp",
    "_research",
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
        if not _path_exists(rendered_root / relative_path):
            violations.append(
                Violation("topology", f"missing required rendered path: {relative_path}")
            )

    for relative_path in FORBIDDEN_RENDERED_PATHS:
        if _path_exists(rendered_root / relative_path):
            violations.append(
                Violation("topology", f"forbidden rendered path exists: {relative_path}")
            )


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


def _release_gate_position(content: str | None, marker: str) -> int:
    marker_words = _shell_words(marker)
    for line_number, line in _active_shell_lines(content):
        words = _shell_words(line)
        if (
            words[: len(marker_words)] == marker_words
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


def _workflow_step_values(
    content: str | None,
    key: str,
) -> tuple[tuple[int, str], ...]:
    if content is None:
        return ()
    values: list[tuple[int, str]] = []
    steps_indent: int | None = None
    list_indent: int | None = None
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
            value = _mapping_value(stripped[2:].lstrip(), key)
        elif indent == list_indent + 2:
            value = _mapping_value(stripped, key)
        else:
            value = None
        if value is not None:
            values.append((line_number, value))
    return tuple(values)


def _workflow_run_position(content: str | None, marker: str) -> int:
    marker_words = _shell_words(marker)
    for line_number, value in _workflow_step_values(content, "run"):
        words = _shell_words(value)
        if words == marker_words:
            return line_number
    return -1


def _workflow_uses_position(content: str | None, marker: str) -> int:
    for line_number, value in _workflow_step_values(content, "uses"):
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


def verify_contract(
    source_root: pathlib.Path,
    rendered_root: pathlib.Path,
) -> tuple[Violation, ...]:
    violations: list[Violation] = []
    _check_topology(source_root, rendered_root, violations)
    _check_release_callers(source_root, violations)
    return tuple(sorted(violations))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=pathlib.Path)
    parser.add_argument("--rendered-root", required=True, type=pathlib.Path)
    arguments = parser.parse_args(argv)

    violations = verify_contract(arguments.source_root, arguments.rendered_root)
    for violation in violations:
        print(violation.render())
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
