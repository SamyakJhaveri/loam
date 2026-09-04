#!/usr/bin/env bash
# bash-length-advisory.sh
#
# PreToolUse hook on Bash.
# Purpose: when a command is very long, suggest splitting it into steps so each
# result stays readable. Advisory only; never blocks.
# Length is the character count of the command, not a separator count: the
# design rejected separator counting: 6 percent false positives on 4,271 real commands.
#
# Exit codes: 0 = always (advisory)

set -uo pipefail

PAYLOAD="$(cat)"

printf '%s' "$PAYLOAD" | python3 -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
except (json.JSONDecodeError, OSError):
    sys.exit(0)
if not isinstance(payload, dict):
    sys.exit(0)

tool_input = payload.get("tool_input")
command = tool_input.get("command") if isinstance(tool_input, dict) else None
if not isinstance(command, str):
    sys.exit(0)

n = len(command)
if n <= 400:
    sys.exit(0)

msg = "Long command (%d chars). Split it into steps so each result is readable." % n
print(json.dumps(
    {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": msg}},
    separators=(",", ":"),
))
' 2>/dev/null || exit 0
