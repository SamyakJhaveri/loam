#!/usr/bin/env bash
# pre-commit-gate.sh
#
# PreToolUse hook — blocks `git commit` unless post-session validation has passed.
#
# Mechanism:
#   - Reads hook event JSON from stdin (Claude Code hook protocol)
#   - Extracts the bash command being run
#   - Only acts on commands containing "git commit"
#   - Checks for .validation_passed sentinel file in project root
#   - Sentinel must exist, be < 30 min old, and not be stale (files unchanged since)
#
# Exit codes (Claude Code hook protocol):
#   0 = allow the command
#   2 = BLOCK the command (stderr shown to Claude as error)
#
# Written by: post-session validation loop
# Pattern from: Trail of Bits claude-code-config, disler/claude-code-hooks-mastery

set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
SENTINEL="$PROJECT_ROOT/.validation_passed"

# Detect OS once — reused in steps 4 and 5
if [ "$(uname)" = "Linux" ]; then
    IS_LINUX=1
else
    IS_LINUX=0
fi

# ── 1. Read and parse the hook event JSON ────────────────────────────────────
INPUT=$(cat)

COMMAND=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    # Claude Code sends tool_input as the top-level or nested object
    ti = d.get('tool_input', d)
    print(ti.get('command', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null || echo "")

# ── 2. Only gate on git commit commands ──────────────────────────────────────
if ! echo "$COMMAND" | grep -qE '^\s*git\s+commit'; then
    exit 0
fi

# ── 3. Check sentinel exists ─────────────────────────────────────────────────
if [ ! -f "$SENTINEL" ]; then
    echo "" >&2
    echo "╔══════════════════════════════════════════════════════════════╗" >&2
    echo "║  BLOCKED: Post-session validation has not been run.         ║" >&2
    echo "║                                                              ║" >&2
    echo "║  Run /validate before committing.                           ║" >&2
    echo "║  This gate enforces the validation loop protocol.           ║" >&2
    echo "║                                                              ║" >&2
    echo "║  Quick check (Wave 1 only, ~30s): /validate quick           ║" >&2
    echo "║  Full check (all waves, ~3min):   /validate                 ║" >&2
    echo "╚══════════════════════════════════════════════════════════════╝" >&2
    echo "" >&2
    exit 2
fi

# ── 4. Check sentinel is not stale (< 30 minutes old) ────────────────────────
if [ "$IS_LINUX" = "1" ]; then
    SENTINEL_MTIME=$(stat -c %Y "$SENTINEL" 2>/dev/null || echo "0")
else
    # macOS
    SENTINEL_MTIME=$(stat -f %m "$SENTINEL" 2>/dev/null || echo "0")
fi

NOW=$(date +%s)
AGE=$(( NOW - SENTINEL_MTIME ))
MAX_AGE=1800  # 30 minutes

if [ "$AGE" -gt "$MAX_AGE" ]; then
    echo "" >&2
    echo "╔══════════════════════════════════════════════════════════════╗" >&2
    echo "║  BLOCKED: Validation sentinel is stale.                     ║" >&2
    echo "║  Age: ${AGE}s  Limit: ${MAX_AGE}s                                   ║" >&2
    echo "║                                                              ║" >&2
    echo "║  Re-run /validate — files may have changed since last run.  ║" >&2
    echo "╚══════════════════════════════════════════════════════════════╝" >&2
    echo "" >&2
    exit 2
fi

# ── 4b. Check that at least 3 validation waves were run (not just quick) ────────
# Three waves per .claude/rules/validation-loop.md: 1=Deterministic 2=Rule-based 3=Probabilistic.
# Fail-open: if waves_passed field is missing, skip this check (backward compat).
WAVES=$(grep '^waves_passed=' "$SENTINEL" 2>/dev/null | cut -d= -f2 | tr -d ' ')
if [ -n "$WAVES" ] && [ "$WAVES" -lt 3 ] 2>/dev/null; then
    echo "" >&2
    echo "╔══════════════════════════════════════════════════════════════╗" >&2
    echo "║  BLOCKED: Only ${WAVES}/3 required validation waves passed.       ║" >&2
    echo "║                                                              ║" >&2
    echo "║  /validate quick is not sufficient for committing.          ║" >&2
    echo "║  Run full /validate (all 3 waves) before committing.         ║" >&2
    echo "╚══════════════════════════════════════════════════════════════╝" >&2
    echo "" >&2
    exit 2
fi

# ── 5. Check sentinel is not outdated by new file changes ─────────────────────
# Find the most recently modified tracked file in the diff
NEWEST_MTIME=$(git -C "$PROJECT_ROOT" diff --name-only HEAD 2>/dev/null | while read -r f; do
    FULL="$PROJECT_ROOT/$f"
    if [ -f "$FULL" ]; then
        if [ "$IS_LINUX" = "1" ]; then
            stat -c %Y "$FULL" 2>/dev/null
        else
            stat -f %m "$FULL" 2>/dev/null
        fi
    fi
done | sort -rn | head -1)

if [ -n "$NEWEST_MTIME" ] && [ "$NEWEST_MTIME" -gt "$SENTINEL_MTIME" ]; then
    echo "" >&2
    echo "╔══════════════════════════════════════════════════════════════╗" >&2
    echo "║  BLOCKED: Files changed after validation passed.            ║" >&2
    echo "║                                                              ║" >&2
    echo "║  Re-run /validate to cover the latest changes.              ║" >&2
    echo "║  Quick re-check: /validate fix                              ║" >&2
    echo "╚══════════════════════════════════════════════════════════════╝" >&2
    echo "" >&2
    exit 2
fi

# ── 6. All checks passed — allow the commit ───────────────────────────────────
echo "✓ Validation sentinel OK (age: ${AGE}s, max: ${MAX_AGE}s). Commit allowed." >&2
exit 0
