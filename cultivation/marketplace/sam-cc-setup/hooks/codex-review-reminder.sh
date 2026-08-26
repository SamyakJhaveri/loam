#!/usr/bin/env bash
# codex-review-reminder.sh
#
# PreToolUse (Bash) hook - advisory reminder to run a Codex review before committing.
# Fires at most ONCE PER SESSION, only on a `git commit`, and never blocks (always exit 0).
#
# It checks for a `.codex_review_done` sentinel at the project root: if that file is
# missing or stale (>30 min), it emits a one-time reminder via hookSpecificOutput JSON.
# A session-scoped marker (keyed on session_id, falling back to a daily marker when the
# payload omits it) suppresses every reminder after the first, so a session with many
# commits gets one nudge, not one per commit. Staying silent for the rest of the session
# is deliberate: the hook is advisory, and not nagging twice does not weaken any review
# policy the project sets elsewhere.
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

SESSION_ID=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    print(d.get('session_id', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null || echo "")

# Once-per-session gate. A missing session_id (older protocol version or a malformed
# payload) falls back to a once-per-day-PER-REPO marker rather than firing on every
# call (a global daily marker would let one repo's reminder suppress every other's).
if [ -n "$SESSION_ID" ]; then
    SHOWN_MARKER="${TMPDIR:-/tmp}/.codex_review_reminder_shown_${SESSION_ID}"
else
    REPO_KEY=$(git rev-parse --show-toplevel 2>/dev/null | cksum | cut -d' ' -f1)
    SHOWN_MARKER="${TMPDIR:-/tmp}/.codex_review_reminder_shown_${REPO_KEY:-norepo}_$(date -u +%Y-%m-%d)"
fi

if [ -f "$SHOWN_MARKER" ]; then
    exit 0
fi

# Match `git commit` at the start of the command or after a `;`/`&`/`|` separator,
# tolerating one `-C <path>` between `git` and `commit`. Conservative by design: a miss
# costs one un-shown advisory reminder, a false positive nags on an unrelated command.
if ! grep -qE '(^|[;&|[:space:]])git([[:space:]]+-C[[:space:]]+[^[:space:]]+)?[[:space:]]+commit([[:space:]]|$)' <<< "$COMMAND"; then
    exit 0
fi

# Resolve the repo the commit targets: honor a `git -C <path> commit`, else the cwd.
CPATH=$(sed -nE 's/.*(^|[;&|[:space:]])git[[:space:]]+-C[[:space:]]+([^[:space:]]+)[[:space:]]+commit.*/\2/p' <<< "$COMMAND" | head -1)
PROJECT_ROOT="$(git ${CPATH:+-C "$CPATH"} rev-parse --show-toplevel 2>/dev/null)" || exit 0
SENTINEL="$PROJECT_ROOT/.codex_review_done"
REMINDER_JSON='{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Codex review reminder: You have not run a Codex review in this session. Before committing, consider running:\n\n  /codex-review\n\nAfter the review completes, write the sentinel from the project root: touch .codex_review_done\nTo skip this reminder, touch .codex_review_done from the project root."}}'

if [ ! -f "$SENTINEL" ]; then
    echo "$REMINDER_JSON"
    touch "$SHOWN_MARKER" 2>/dev/null || true
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
    touch "$SHOWN_MARKER" 2>/dev/null || true
fi

exit 0
