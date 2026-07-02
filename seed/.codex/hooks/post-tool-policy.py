#!/usr/bin/env python3
"""Codex PostToolUse advisory hook for this project."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def project_root() -> Path:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.DEVNULL
        )
        return Path(out.strip())
    except Exception:
        return Path.cwd()


ROOT = project_root()


def validation_sentinel() -> Path:
    override = os.environ.get("CODEX_VALIDATION_SENTINEL")
    return Path(override) if override else ROOT / ".validation_passed"


def review_sentinel() -> Path:
    override = os.environ.get("CODEX_REVIEW_SENTINEL")
    return Path(override) if override else ROOT / ".codex_review_done"


def load_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def tool_input(payload: dict) -> dict:
    value = payload.get("tool_input", payload.get("input", payload))
    return value if isinstance(value, dict) else {}


def rel_path(path: str) -> str:
    if not path:
        return ""
    p = Path(path)
    try:
        if p.is_absolute():
            path = str(p.resolve().relative_to(ROOT.resolve()))
    except Exception:
        path = str(p)
    path = path.replace("\\", "/")
    return path[2:] if path.startswith("./") else path


def patch_paths(patch: str) -> list[str]:
    paths: list[str] = []
    for line in patch.splitlines():
        for prefix in ("*** Add File: ", "*** Update File: ", "*** Delete File: ", "*** Move to: "):
            if line.startswith(prefix):
                paths.append(rel_path(line[len(prefix) :].strip()))
    return paths


def changed_paths(payload: dict) -> list[str]:
    inputs = tool_input(payload)
    paths = []
    file_path = inputs.get("file_path") or inputs.get("path")
    if file_path:
        paths.append(rel_path(str(file_path)))
    patch = str(inputs.get("patch") or payload.get("patch") or "")
    paths.extend(patch_paths(patch))
    return sorted({path for path in paths if path})


def cleanup_sentinels(paths: list[str]) -> None:
    if not paths:
        return

    sentinels = [validation_sentinel(), review_sentinel()]
    sentinel_paths = {rel_path(str(sentinel)) for sentinel in sentinels}
    if all(path in sentinel_paths for path in paths):
        return

    for sentinel in sentinels:
        if sentinel.exists():
            sentinel.unlink()
            print(f"sentinel-cleanup: {sentinel.name} deleted after file edit", file=sys.stderr)


def run_ruff(paths: list[str]) -> None:
    py_files = [str(ROOT / path) for path in paths if path.endswith(".py") and (ROOT / path).is_file()]
    if not py_files:
        return
    print("[post-tool-policy] Running advisory ruff check...", file=sys.stderr)
    subprocess.run(["python3", "-m", "ruff", "check", *py_files], check=False)


def run_smoke_tests(paths: list[str]) -> None:
    if not any(path.endswith(".py") for path in paths):
        return
    tests = ROOT / "tests"
    if not tests.is_dir():
        return
    print("[post-tool-policy] Running Python smoke tests...", file=sys.stderr)
    cmd = ["python3", "-m", "pytest", str(tests), "-x", "-q", "--tb=line"]
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=8, check=False)
    except Exception as exc:
        print(f"[post-tool-policy] smoke test skipped: {exc}", file=sys.stderr)
        return
    lines = (proc.stdout + proc.stderr).splitlines()
    for line in lines[-5:]:
        print(line, file=sys.stderr)


def main() -> int:
    paths = changed_paths(load_payload())
    cleanup_sentinels(paths)
    run_ruff(paths)
    run_smoke_tests(paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
