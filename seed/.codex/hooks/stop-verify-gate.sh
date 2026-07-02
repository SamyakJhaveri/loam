#!/usr/bin/env bash
# Codex Stop hook: fast deterministic turn-end verification on changed files.

set -uo pipefail

PAYLOAD="$(cat)"

ACTIVE=$(printf '%s' "$PAYLOAD" | python3 -c "import sys, json
try:
    print(str(json.load(sys.stdin).get('stop_hook_active', False)).lower())
except Exception:
    print('false')" 2>/dev/null)
[ "$ACTIVE" = "true" ] && exit 0

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$ROOT" || exit 0

CHANGED=$( { git diff --name-only HEAD; git ls-files --others --exclude-standard; } 2>/dev/null)
[ -z "$CHANGED" ] && exit 0

FAIL=""

DC=$(git diff --check HEAD 2>&1) || true
[ -n "$DC" ] && FAIL="${FAIL}\n[git diff --check]\n${DC}\n"

PY=$(printf '%s\n' "$CHANGED" | grep -E '\.py$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)
if [ -n "$PY" ]; then
    if ! OUT=$(printf '%s\n' "$PY" | xargs python3 -m ruff check 2>&1); then
        FAIL="${FAIL}\n[ruff check]\n${OUT}\n"
    fi
fi

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
        echo "Turn-end verification gate FAILED; fix these before ending the turn:"
        printf '%b\n' "$FAIL"
        echo "(Fast deterministic checks only. Run /validate before commit.)"
    } >&2
    exit 2
fi

exit 0
