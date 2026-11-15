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
import re
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

# What Claude Code injects was measured for Fable 5.2 only (the fable-prompting skill, "Never paste these").
if re.search(r"fable-5[-.]2", model.lower()):
    injected = (
        "Do not paste the finishing block (in the first claude -p request) or the "
        "silent-turn reminder (in the Claude Code bundle); Claude Code sends Fable "
        "5.2 both. Interactive sessions were not "
        "captured. The first request had no Signal-intent or one-line-update "
        "text; quote it from the guide if needed. "
    )
else:
    injected = (
        "What Claude Code injects for this Fable version was not measured; check "
        "the request before pasting guide text. "
    )

print(
    "Fable session. Ask one question before acting only if a reading of the "
    "request would change the architecture; otherwise act.\n"
    "Judgment rules this harness does not inject:\n"
    "- A benign request stays benign. Do not refuse work that only sounds "
    "sensitive.\n"
    "In a session prompt for another session use five headings: Goal and why; "
    "Constraints; Done check per task; Session conduct; Target model and effort. "
    "A worker brief, its report and a handoff note use the seven headings in "
    "docs/WORKERS.md instead. "
    + injected
    + "The `fable-prompting` skill is the long form."
)
' 2>/dev/null || exit 0
