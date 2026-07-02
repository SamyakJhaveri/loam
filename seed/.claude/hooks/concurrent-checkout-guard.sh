#!/usr/bin/env bash
# concurrent-checkout-guard.sh
#
# PreToolUse hook on Bash|Edit|Write.
#
# Guards against the documented Codex+Claude same-checkout race
# (memory: concurrent-codex-claude-checkout-race). Two harnesses sharing ONE
# working tree collide on .git/index.lock, producing:
#   fatal: Unable to create '.git/index.lock': File exists
# plus mystery files and clobbered .validation_passed sentinels.
#
# Design: reuse git's OWN index.lock as the single-writer mutex — no new lock
# machinery, no SessionStart wiring. The lock git already maintains is exactly
# the contention signal we need.
#
# Behavior:
#   - Resolves THIS worktree's git dir (worktree-aware) so .worktrees/* siblings
#     never false-positive on each other — the race is two harnesses in the SAME
#     tree, which share one git dir.
#   - Bash: only gates git index-writing subcommands; read-only git (status/log)
#     and non-git commands pass untouched.
#   - FRESH lock (age < THRESHOLD s) → another writer is live → BLOCK (exit 2).
#   - STALE lock (>= THRESHOLD s) → likely a crashed git process, not a live
#     race → ALLOW + advise cleanup (avoids a leftover lock deadlocking forever).
#
# Exit codes (Claude Code hook protocol): 0 = allow, 2 = BLOCK (stderr → Claude).

set -euo pipefail

INPUT=$(cat)

TOOL_NAME=$(python3 -c "
import sys, json
try:
    print(json.loads(sys.stdin.read()).get('tool_name', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null || echo "")

# Resolve this worktree's git dir (absolute, worktree-aware). Not a repo → nothing to guard.
GIT_DIR=$(git rev-parse --absolute-git-dir 2>/dev/null || echo "")
[ -z "$GIT_DIR" ] && exit 0
LOCK="$GIT_DIR/index.lock"

# For Bash, only act on git commands that take the index lock.
if [ "$TOOL_NAME" = "Bash" ] || [ -z "$TOOL_NAME" ]; then
    CMD=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read()); ti = d.get('tool_input', d)
    print(ti.get('command', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null || echo "")
    if ! echo "$CMD" | grep -qE '\bgit\b[^|;&]*\b(commit|add|rm|mv|merge|rebase|reset|restore|checkout|switch|stash|cherry-pick|pull|am|apply|revert)\b'; then
        exit 0
    fi
fi

# No lock → no contention.
[ -f "$LOCK" ] || exit 0

# Lock present — fresh (live writer) or stale (crash leftover)?
if [ "$(uname)" = "Linux" ]; then
    LOCK_MTIME=$(stat -c %Y "$LOCK" 2>/dev/null || echo 0)
else
    LOCK_MTIME=$(stat -f %m "$LOCK" 2>/dev/null || echo 0)
fi
NOW=$(date +%s)
AGE=$(( NOW - LOCK_MTIME ))
THRESHOLD=30

if [ "$AGE" -lt "$THRESHOLD" ]; then
    echo "" >&2
    echo "BLOCKED: another writer holds this checkout's git index (index.lock age ${AGE}s)." >&2
    echo "  A second agent (a concurrent Codex or Claude session) is mid-write in the SAME working tree." >&2
    echo "  Treat one checkout as single-writer. Wait for the other session to finish, then retry." >&2
    echo "  Lock: $LOCK" >&2
    echo "" >&2
    exit 2
fi

# Stale lock: advise, do not block (git would otherwise error on its own anyway).
echo "NOTE: stale git index.lock found (age ${AGE}s) — likely a crashed git process, not a live race." >&2
echo "  If no other agent is active in this checkout, clear it: rm '$LOCK'" >&2
exit 0
