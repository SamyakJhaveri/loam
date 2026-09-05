#!/usr/bin/env python3
"""Check the Loam seed's Claude/Codex capability bill of materials.

Fail-closed: any manifest error, drift between agent-parity.toml and the seed
capability tree, or missing shared-skill symlink is a non-zero exit. This is the
check-only descendant of distbench's apply/check/report/catalog tool; Loam ships
only the gate.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from pathlib import Path
from typing import Any


MANIFEST = "agent-parity.toml"
CAPABILITY_NAME = re.compile(r"[a-z0-9][a-z0-9-]*")


class ParityError(RuntimeError):
    """A fail-closed manifest or ownership error."""


def _safe_name(name: str) -> str:
    if not CAPABILITY_NAME.fullmatch(name):
        raise ParityError(f"invalid capability name: {name!r}")
    return name


def _repo_path(root: Path, relative: str) -> Path:
    raw = Path(relative)
    if raw.is_absolute():
        raise ParityError(f"path escapes repository: {relative}")
    candidate = root / raw
    resolved_root = root.resolve()
    resolved = candidate.resolve(strict=False)
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise ParityError(f"path escapes repository: {relative}")
    return candidate


def _load(root: Path) -> dict[str, Any]:
    path = root / MANIFEST
    if not path.is_file():
        raise ParityError(f"missing manifest: {path}")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ParityError("agent-parity.toml must declare schema_version = 1")
    return data


def _names(entries: list[Any]) -> list[str]:
    return [entry if isinstance(entry, str) else entry["name"] for entry in entries]


def _skill_names(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {item.name for item in root.iterdir() if (item / "SKILL.md").is_file()}


def _file_set(root: Path, directory: str, suffix: str = "") -> set[str]:
    base = root / directory
    if not base.is_dir():
        return set()
    return {
        path.relative_to(root).as_posix()
        for path in base.iterdir()
        if path.is_file() and (not suffix or path.name.endswith(suffix))
    }


def _duplicates(groups: dict[str, list[str]]) -> list[str]:
    seen: dict[str, str] = {}
    errors: list[str] = []
    for disposition, names in groups.items():
        for name in names:
            if name in seen:
                errors.append(
                    f"{name!r} is classified as both {seen[name]} and {disposition}"
                )
            else:
                seen[name] = disposition
    return errors


def _compare(label: str, actual: set[str], declared: set[str]) -> list[str]:
    errors: list[str] = []
    missing = sorted(actual - declared)
    stale = sorted(declared - actual)
    if missing:
        errors.append(f"{label} unclassified: {', '.join(missing)}")
    if stale:
        errors.append(f"{label} declared but absent: {', '.join(stale)}")
    return errors


def check(root: Path, data: dict[str, Any] | None = None) -> list[str]:
    data = data or _load(root)
    errors: list[str] = []

    skills = data["skills"]
    skill_groups = {
        "shared": list(skills["shared"]),
        "native_adapter": list(skills["native_adapter"]),
        "native_codex": list(skills["native_codex"]),
        "unsupported": _names(skills["unsupported"]),
    }
    for section in ("skills", "workflows"):
        for entry in data[section]["unsupported"]:
            if not str(entry.get("fallback", "")).strip():
                errors.append(
                    f"unsupported capability needs a fallback: {entry.get('name', entry.get('source', 'unknown'))}"
                )
    errors.extend(_duplicates(skill_groups))
    claude_declared = set(
        skill_groups["shared"]
        + skill_groups["native_adapter"]
        + skill_groups["unsupported"]
    )
    workflow_skill_adapters = {
        Path(item["codex"]).parent.name
        for item in data["workflows"]["native_adapter"]
        if Path(item["codex"]).name == "SKILL.md"
        and Path(item["codex"]).parent.parent.as_posix() == ".agents/skills"
    }
    codex_declared = set(
        skill_groups["shared"]
        + skill_groups["native_adapter"]
        + skill_groups["native_codex"]
    ) | workflow_skill_adapters
    errors.extend(
        _compare(
            "Claude skill",
            _skill_names(root / ".claude" / "skills"),
            claude_declared,
        )
    )
    errors.extend(
        _compare(
            "Codex skill",
            _skill_names(root / ".agents" / "skills"),
            codex_declared,
        )
    )

    # Shared skills: the canonical directory is .agents/skills/<name> (real
    # files, read by both Claude and Codex); .claude/skills/<name> is a relative
    # symlink into it. This is the reverse of distbench, where .claude/skills was
    # canonical, so source and target are swapped from the upstream check.
    for name in skill_groups["shared"]:
        _safe_name(name)
        try:
            source = _repo_path(root, f".agents/skills/{name}")
        except ParityError:
            errors.append(f"shared source escapes repository: {name}")
            continue
        target = _repo_path(root, f".claude/skills/{name}")
        if not target.is_symlink():
            errors.append(f"shared skill is not a symlink: {target.relative_to(root)}")
            continue
        raw_target = os.readlink(target)
        if Path(raw_target).is_absolute():
            errors.append(f"shared skill link is absolute: {target.relative_to(root)}")
        try:
            if target.resolve(strict=True) != source.resolve(strict=True):
                errors.append(f"shared skill link points elsewhere: {target.relative_to(root)}")
        except FileNotFoundError:
            errors.append(f"shared skill link is broken: {target.relative_to(root)}")

    agents = data["agents"]
    claude_agents = {
        Path(path).stem for path in _file_set(root, ".claude/agents", ".md")
    }
    codex_agents = {
        Path(path).stem for path in _file_set(root, ".codex/agents", ".toml")
    }
    agent_adapters = set(agents["native_adapter"])
    agent_native = set(agents["native_codex"])
    errors.extend(
        _duplicates(
            {"native_adapter": list(agent_adapters), "native_codex": list(agent_native)}
        )
    )
    errors.extend(_compare("Claude agent", claude_agents, agent_adapters))
    errors.extend(_compare("Codex agent", codex_agents, agent_adapters | agent_native))
    for name in sorted(agent_adapters):
        wrapper = root / ".codex" / "agents" / f"{name}.toml"
        canonical = f".claude/agents/{name}.md"
        if wrapper.is_file() and canonical not in wrapper.read_text(encoding="utf-8"):
            errors.append(f"Codex agent does not name canonical source: {wrapper.relative_to(root)}")

    hooks = data["hooks"]
    hook_adapters = dict(hooks["native_adapter"])
    hook_unsupported = dict(hooks["unsupported"])
    hook_native = dict(hooks["native_codex"])
    unsupported_hook_files = {
        path for path in hook_unsupported if path.startswith(".claude/hooks/")
    }
    errors.extend(
        _compare(
            "Claude hook",
            _file_set(root, ".claude/hooks"),
            set(hook_adapters) | unsupported_hook_files,
        )
    )
    codex_hook_targets = {
        value for value in hook_adapters.values() if value.startswith(".codex/hooks/")
    }
    errors.extend(
        _compare(
            "Codex hook",
            _file_set(root, ".codex/hooks"),
            codex_hook_targets | set(hook_native.values()),
        )
    )

    workflows = data["workflows"]
    workflow_adapters = list(workflows["native_adapter"])
    workflow_unsupported = list(workflows["unsupported"])
    workflow_sources = {item["source"] for item in workflow_adapters}
    workflow_sources.update(item["source"] for item in workflow_unsupported)
    errors.extend(
        _compare(
            "Claude workflow",
            _file_set(root, ".claude/workflows", ".js"),
            workflow_sources,
        )
    )
    for item in workflow_adapters:
        if not _repo_path(root, item["codex"]).is_file():
            errors.append(f"workflow adapter is missing: {item['codex']}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check",))
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "seed",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        data = _load(root)
        issues = check(root, data)
        if issues:
            print("parity check failed:", file=sys.stderr)
            for issue in issues:
                print(f"- {issue}", file=sys.stderr)
            return 1
        print("parity check passed")
    except (OSError, KeyError, ParityError, tomllib.TOMLDecodeError) as exc:
        print(f"parity check failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
