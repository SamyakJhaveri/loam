#!/usr/bin/env bash
# fable-session-brief.sh - print a short prompting brief when the session model is Fable.
#
# Those are the only two events that reveal the model: SessionStart carries an
# optional `model`, PostModelSwitch carries `to_model`. Plain stdout on either
# event is added to Claude's context. No state is kept; an absent field means
# unknown, and unknown means silent.
#
# Triggered by: SessionStart (startup|resume|clear|compact|fork) and PostModelSwitch
# Exit codes:
#   0 = always (advisory, never blocks)

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

model = None
for field in ("to_model", "model"):
    value = payload.get(field)
    if isinstance(value, str) and value:
        model = value
        break

if model is None or "fable" not in model.lower():
    sys.exit(0)

print(
    "Fable 5.1 session. On a rough request, restate goal, constraints, and done "
    "check in three lines before acting; ask one question only if a reading would "
    "change the architecture. When writing a handoff or plan for another session, "
    "give it five headings: Goal and why; Constraints; Done check per task; "
    "Session conduct; Target model and effort. Do not paste the autonomy block, "
    "the Delivering work block, the progress-updates line, or the batching nudge; "
    "Claude Code already injects all four. Prefer targeted edits over whole-file "
    "rewrites. When the deliverable is prose, remove all mannered prose."
)
' 2>/dev/null || exit 0
