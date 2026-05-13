#!/usr/bin/env bash
# codex-review-reminder.sh
#
# PreToolUse hook — advisory reminder to run Codex review before committing.
#
# Checks for .codex_review_done sentinel file. If missing or stale (>30 min),
# outputs a reminder via hookSpecificOutput JSON. Never blocks (always exit 0).
#
# Exit codes:
#   0 = always (advisory hook, never blocks)

trap 'exit 0' ERR

INPUT=$(cat)
COMMAND=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('command', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null || echo "")

if ! echo "$COMMAND" | grep -qE '^\s*git\s+commit'; then
    exit 0
fi

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
SENTINEL="$PROJECT_ROOT/.codex_review_done"
REMINDER_JSON='{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Codex review reminder: You have not run a Codex review in this session. Before committing, consider running:\n\n  /codex:rescue review the uncommitted changes for correctness and regressions\n\nAfter the review completes, write the sentinel from the project root: touch .codex_review_done\nTo skip this reminder, touch .codex_review_done from the project root."}}'

if [ ! -f "$SENTINEL" ]; then
    echo "$REMINDER_JSON"
    exit 0
fi

if [ "$(uname)" = "Linux" ]; then
    SENTINEL_MTIME=$(stat -c %Y "$SENTINEL" 2>/dev/null || echo "0")
else
    SENTINEL_MTIME=$(stat -f %m "$SENTINEL" 2>/dev/null || echo "0")
fi

NOW=$(date +%s)
AGE=$(( NOW - SENTINEL_MTIME ))

if [ "$AGE" -gt 1800 ]; then
    echo "$REMINDER_JSON"
    exit 0
fi

exit 0
