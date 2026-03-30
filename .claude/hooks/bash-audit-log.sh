#!/usr/bin/env bash
# Bash audit log — appends every Bash command to timestamped log
#
# Triggered by: PreToolUse on Bash
# Purpose: Experiment reproducibility — every shell command is logged with timestamp
#          so eval runs, build commands, and debug sessions can be replayed later.
#
# Exit codes:
#   0 = always (logging hook, never blocks)

set -euo pipefail

# Consume stdin (PreToolUse hooks receive JSON on stdin; prevent SIGPIPE)
cat > /dev/null

LOG="/home/samyak/Desktop/parbench_sam/.claude/audit.log"
echo "$(date -Iseconds) | ${CLAUDE_TOOL_INPUT:-unknown}" >> "$LOG"
exit 0
