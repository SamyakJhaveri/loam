#!/usr/bin/env bash
# stop-verify-gate.sh - Stop hook: deterministic turn-end verification gate.
# Fast checks on CHANGED files only: git diff --check, ruff on .py, bash -n on .sh.
# Blocks the turn with exit 2 + evidence on stderr; no-ops when nothing changed.
# Reads the JSON envelope on stdin (hooks get JSON on stdin, not env vars).
# Deliberately excludes slow checks (mypy/pytest) - this is the fast signal only.

set -uo pipefail   # no -e: collect all failures, don't abort on the first

PAYLOAD="$(cat)"

# Loop guard: if we're already inside a stop-hook continuation, pass.
ACTIVE=$(printf '%s' "$PAYLOAD" | python3 -c "import sys, json
try:
    print(str(json.load(sys.stdin).get('stop_hook_active', False)).lower())
except Exception:
    print('false')" 2>/dev/null)
[ "$ACTIVE" = "true" ] && exit 0

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0

# Changed = tracked diffs vs HEAD + untracked (excluding gitignored).
CHANGED=$( { git diff --name-only HEAD; git ls-files --others --exclude-standard; } 2>/dev/null)
[ -z "$CHANGED" ] && exit 0   # docs/conversation turn with no file changes → pass

FAIL=""

# 1. Whitespace errors / leftover conflict markers (instant).
DC=$(git diff --check HEAD 2>&1) || true
[ -n "$DC" ] && FAIL="${FAIL}\n[git diff --check]\n${DC}\n"

# 2. Ruff on changed, still-present Python files (fast).
# uv/brew installs ship ruff as a PATH binary, not an importable module, so
# probe the module first and fall back to the binary before giving up.
PY=$(printf '%s\n' "$CHANGED" | grep -E '\.py$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)
if [ -n "$PY" ]; then
    RUFF=""
    if python3 -m ruff --version >/dev/null 2>&1; then
        RUFF="python3 -m ruff"
    elif command -v ruff >/dev/null 2>&1; then
        RUFF="ruff"
    fi
    if [ -z "$RUFF" ]; then
        # A project without ruff gets a visible note, not a misleading block.
        echo "NOTE: ruff unavailable; the stop gate skipped its ruff leg." >&2
    elif ! OUT=$(printf '%s\n' "$PY" | xargs $RUFF check 2>&1); then
        FAIL="${FAIL}\n[ruff check]\n${OUT}\n"
    fi
fi

# 3. Shell syntax on changed, still-present .sh files (instant).
SH=$(printf '%s\n' "$CHANGED" | grep -E '\.sh$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)
if [ -n "$SH" ]; then
    while read -r f; do
        [ -z "$f" ] && continue
        if ! ERR=$(bash -n "$f" 2>&1); then
            FAIL="${FAIL}\n[bash -n] ${f}:\n${ERR}\n"
        fi
    done <<< "$SH"
fi

if [ -n "$FAIL" ]; then
    {
        echo "Turn-end verification gate FAILED — fix these before ending the turn:"
        printf '%b\n' "$FAIL"
        echo "(Fast deterministic checks on changed files only."
        echo " To bypass intentionally, disable the Stop hook in .claude/settings.json.)"
    } >&2
    exit 2
fi

exit 0
