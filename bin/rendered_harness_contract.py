#!/usr/bin/env python3
"""Verify the contract shared by Loam's source and rendered harness."""

from __future__ import annotations

import argparse
import dataclasses
import pathlib
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


def _check_marker_order(
    source_root: pathlib.Path,
    relative_path: str,
    first_marker: str,
    second_marker: str | None,
    violations: list[Violation],
) -> None:
    content = _read_text(source_root / relative_path)
    first_position = -1 if content is None else content.find(first_marker)
    second_position = (
        None
        if second_marker is None
        else -1
        if content is None
        else content.find(second_marker)
    )

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
    _check_marker_order(
        source_root,
        ".github/workflows/test.yml",
        "bin/verify-template.sh",
        None,
        violations,
    )
    _check_marker_order(
        source_root,
        ".github/workflows/release.yml",
        "bin/verify-template.sh",
        "softprops/action-gh-release",
        violations,
    )
    _check_marker_order(
        source_root,
        "bin/release.sh",
        'bash "$SELF_DIR/verify-template.sh"',
        'echo "$VERSION" > VERSION',
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
