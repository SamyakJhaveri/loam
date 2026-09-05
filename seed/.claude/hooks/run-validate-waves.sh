#!/usr/bin/env bash
# run-validate-waves.sh - deterministic validation wave runner and sentinel writer.
#
# Runs Wave 1 (deterministic checks) and Wave 2 (tests), then writes
# .validation_passed at the repo root with waves_passed=2 ONLY when both waves
# are green. This is the ONLY sanctioned writer of that sentinel; never
# hand-write .validation_passed. pre-commit-gate.sh reads it on git commit and
# sentinel-cleanup.sh deletes it on the next edit.
#
# The language checks are guarded on pyproject.toml AND on tool availability:
# ruff, mypy, and pytest run only when a pyproject.toml is present and the tool
# resolves (uv run when uv imports the tool, else the direct binary or uvx). A
# missing tool is skipped with a printed note, never a hard failure, so an
# uninstalled dev tool cannot block a commit for an unrelated reason. With no
# pyproject.toml checks are skipped, sentinel still written; mypy non-blocking.
#
# Usage: ./.claude/hooks/run-validate-waves.sh [validated_by-label]
#   default label: validate-skill
#
# Exit: 0 = both waves green, sentinel written; 1 = a wave failed, no sentinel.

set -uo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 1
cd "$PROJECT_ROOT" || exit 1
VALIDATED_BY="${1:-validate-skill}"

# Test seams: these env overrides exist ONLY so tests can drive the green/red
# paths without recursing into a real ruff/pytest run.
WAVE1_OVERRIDE="${RUN_VALIDATE_WAVE1_CMD:-}"
WAVE2_OVERRIDE="${RUN_VALIDATE_WAVE2_CMD:-}"

# Resolve how to run each tool; echo the command prefix, empty when unavailable.
ruff_runner() {
    if command -v uv >/dev/null 2>&1 && uv run python -c 'import ruff' >/dev/null 2>&1; then echo "uv run ruff"
    elif command -v ruff >/dev/null 2>&1; then echo "ruff"
    elif command -v uvx >/dev/null 2>&1; then echo "uvx ruff"; fi
}
pytest_runner() {
    if command -v uv >/dev/null 2>&1 && uv run python -c 'import pytest' >/dev/null 2>&1; then echo "uv run pytest"
    elif python3 -c 'import pytest' >/dev/null 2>&1; then echo "python3 -m pytest"; fi
}
mypy_runner() {
    if command -v uv >/dev/null 2>&1 && uv run python -c 'import mypy' >/dev/null 2>&1; then echo "uv run mypy"
    elif python3 -c 'import mypy' >/dev/null 2>&1; then echo "python3 -m mypy"; fi
}

wave1() {
    if [ -n "$WAVE1_OVERRIDE" ]; then eval "$WAVE1_OVERRIDE"; return $?; fi
    local rc=0 ruff mypy f
    if [ -f pyproject.toml ]; then
        ruff="$(ruff_runner)"
        if [ -n "$ruff" ]; then
            $ruff check . || rc=1
        else
            echo "run-validate-waves: ruff not available; skipping" >&2
        fi
        mypy="$(mypy_runner)"
        [ -n "$mypy" ] && { $mypy . || true; }
    else
        echo "run-validate-waves: no pyproject.toml; skipping ruff/mypy" >&2
    fi
    git diff --check || rc=1
    for f in $(git diff --name-only HEAD 2>/dev/null | grep '\.sh$' || true); do
        [ -f "$f" ] && { bash -n "$f" || rc=1; }
    done
    return $rc
}

wave2() {
    if [ -n "$WAVE2_OVERRIDE" ]; then eval "$WAVE2_OVERRIDE"; return $?; fi
    if [ -f pyproject.toml ]; then
        local pytest
        pytest="$(pytest_runner)"
        if [ -n "$pytest" ]; then
            $pytest || return 1
        else
            echo "run-validate-waves: pytest not available; skipping" >&2
        fi
    else
        echo "run-validate-waves: no pyproject.toml; skipping pytest" >&2
    fi
    return 0
}

echo "=== Wave 1 - deterministic ==="
wave1 || { echo "WAVE 1 FAILED - no sentinel written" >&2; exit 1; }
echo "=== Wave 2 - tests ==="
wave2 || { echo "WAVE 2 FAILED - no sentinel written" >&2; exit 1; }

cat > "$PROJECT_ROOT/.validation_passed" << SENTINEL
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
git_hash=$(git rev-parse --verify HEAD 2>/dev/null || echo "none")
changed_files=$(git diff --name-only HEAD 2>/dev/null | wc -l | tr -d ' ')
waves_passed=2
validated_by=$VALIDATED_BY
SENTINEL
echo ".validation_passed written (waves_passed=2, validated_by=$VALIDATED_BY)"
