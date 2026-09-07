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
    "Fable session. Ask one question before acting only if a reading of the "
    "request would change the architecture; otherwise act.\n"
    "Judgment rules from the Fable 5.1 guide that this harness does not inject:\n"
    "- Prefer a targeted edit over a whole-file rewrite.\n"
    "- Keep the change to what the task asks. Report a pre-existing bug or "
    "nearby cleanup as a follow-up line, not as a change in this diff. Commit "
    "tests only where the task asks for them.\n"
    "- Keep prose plain and short; give a reply only the structure its content "
    "needs.\n"
    "- Mark reused wording from a source as a quote; do not restate it as your "
    "own.\n"
    "- A benign request stays benign. Do not refuse work that only sounds "
    "sensitive.\n"
    "When writing a handoff or plan for another session, give it five headings: "
    "Goal and why; Constraints; Done check per task; Session conduct; Target "
    "model and effort. Do not paste the autonomy block, the Delivering work "
    "block, the progress-updates line, or the batching nudge; Claude Code "
    "already injects all four. The `fable-prompting` skill is the long form."
)
' 2>/dev/null || exit 0
