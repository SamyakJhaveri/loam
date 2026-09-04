#!/usr/bin/env bash
# write-rewrite-guard.sh
#
# PreToolUse hook on Write.
# Purpose: when Write targets an existing, sizeable file, nudge toward Edit so a
# small change does not rewrite the whole file. Advisory only; never blocks.
# Threshold is REWRITE_GUARD_LINES (default 80).
#
# Exit codes: 0 = always (advisory)

set -uo pipefail

PAYLOAD="$(cat)"

printf '%s' "$PAYLOAD" | python3 -c '
import json
import os
import sys

try:
    payload = json.load(sys.stdin)
except (json.JSONDecodeError, OSError):
    sys.exit(0)
if not isinstance(payload, dict):
    sys.exit(0)

tool_input = payload.get("tool_input")
file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
if not isinstance(file_path, str) or not file_path:
    sys.exit(0)

base = payload.get("cwd")
if not isinstance(base, str) or not base:
    base = os.getcwd()
resolved = file_path if os.path.isabs(file_path) else os.path.join(base, file_path)

try:
    with open(resolved, "r", encoding="utf-8", errors="replace") as handle:
        n = sum(1 for _ in handle)
except OSError:
    sys.exit(0)

try:
    threshold = int(os.environ.get("REWRITE_GUARD_LINES", "80"))
except ValueError:
    threshold = 80

if n < threshold:
    sys.exit(0)

msg = ("%s already exists with %d lines. Prefer Edit; use Write only if most "
       "of the file is changing." % (file_path, n))
print(json.dumps(
    {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": msg}},
    separators=(",", ":"),
))
' 2>/dev/null || exit 0
