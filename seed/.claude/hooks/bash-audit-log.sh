#!/usr/bin/env bash
# Bash audit log — appends every Bash command to timestamped log
#
# Triggered by: PreToolUse on Bash
# Purpose: Experiment reproducibility — every shell command is logged with timestamp so eval runs, build commands, and debug sessions can be replayed later.
#
# Exit codes:
#   0 = always (logging hook, never blocks)

set -euo pipefail

# Read stdin JSON (Claude Code passes hook payload as JSON on stdin)
PAYLOAD="$(cat)"

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
LOG="$PROJECT_ROOT/.claude/audit.log"
COMMAND="$(printf '%s' "$PAYLOAD" | python3 -c 'import sys, json; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command","unparseable"))' 2>/dev/null || echo "unparseable")"
echo "$(date -Iseconds) | $COMMAND" >> "$LOG"
exit 0
