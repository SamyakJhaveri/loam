#!/usr/bin/env bash
# context-budget.sh
#
# PostToolUse hook — tracks Bash tool call count and prints context budget reminders.
#
# Osmani principle: Token budgeting with auto-pause at thresholds.
# Long sessions accumulate context silently. This hook provides periodic nudges
# to compact or split the task before context fills up and quality degrades.
#
# Triggered by: PostToolUse on Bash
# Always exits 0 (advisory only — never blocks)

set -euo pipefail

# Consume stdin to prevent SIGPIPE
cat > /dev/null

# Use a session-stable counter file. PPID is the Claude Code process (stable across
# tool calls within a session, unlike $$ which changes per hook invocation).
COUNTER_FILE="/tmp/parbench_context_counter_${PPID}"

# Initialize counter if missing
if [ ! -f "$COUNTER_FILE" ]; then
    echo "0" > "$COUNTER_FILE"
fi

# Increment
COUNT=$(cat "$COUNTER_FILE")
COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

# Print reminders at thresholds
case $COUNT in
    20)
        echo "[context-budget] 20 tool calls this session. Consider running /compact if context is getting large."
        ;;
    40)
        echo "[context-budget] 40 tool calls. Osmani's rule: compact at 50% context, split task at 75%."
        ;;
    60)
        echo "[context-budget] 60 tool calls. Recommend /compact now to preserve context quality."
        ;;
    80)
        echo "[context-budget] 80 tool calls. Strong recommendation: /compact or split into a new session."
        ;;
    100)
        echo "[context-budget] WARNING: 100+ tool calls. /compact or /clear strongly recommended to avoid context degradation."
        ;;
esac

# After 100, remind every 20 calls
if [ "$COUNT" -gt 100 ] && [ $(( COUNT % 20 )) -eq 0 ]; then
    echo "[context-budget] WARNING: ${COUNT} tool calls this session. /compact or /clear is overdue."
fi

exit 0
