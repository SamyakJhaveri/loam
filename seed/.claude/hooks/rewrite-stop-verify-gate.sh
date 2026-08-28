#!/usr/bin/env bash
# stop-verify-gate.sh — Stop hook: deterministic turn-end verification gate.
#
# Implements the best-practices "deterministic gate" rung
# (https://code.claude.com/docs/en/best-practices → "Give Claude a way to verify
# its work"): runs fast Layer-1 checks on CHANGED files and blocks the turn from
# ending until they pass. Complements (does NOT replace) the commit-time
# pre-commit-gate.sh — this is the fast signal, /validate stays the full one.
#
# Triggered by: Stop
# Blocks by:    exit 2 with evidence on stderr (Claude Code auto-overrides after
#               8 consecutive blocks). No-ops (exit 0) when nothing relevant changed.
# Protocol:     reads the JSON envelope on stdin — NOT env vars (see known-issues.md
#               "hooks receive JSON on stdin, not env vars").
#
# Deliberately EXCLUDES mypy/pytest: too slow for every turn-end and already
# covered by /validate (Wave 2) and the post-edit-test.sh PostToolUse hook.

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
PY=$(printf '%s\n' "$CHANGED" | grep -E '\.py$' | while read -r f; do [ -f "$f" ] && echo "$f"; done)
if [ -n "$PY" ]; then
    if ! OUT=$(printf '%s\n' "$PY" | xargs python3 -m ruff check 2>&1); then
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
        echo "(Fast deterministic checks on changed files only; not the full /validate."
        echo " Run /validate before commit. To bypass intentionally, disable the Stop hook in .claude/settings.json.)"
    } >&2
    exit 2
fi

exit 0
