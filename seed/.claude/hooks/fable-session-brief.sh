#!/usr/bin/env bash
# fable-session-brief.sh - print the judgment rules Claude Code does not inject.
#
# The rules block is model-agnostic and unconditional, because no SessionStart
# payload names the model (measured on Claude Code 2.1.263: the payload has
# `source` but no `model`, and the hook environment has no model variable).
# Only PostModelSwitch reveals a model, via `to_model`, so the Fable-specific
# paragraph is the only gated part.
#
# Triggered by: SessionStart (startup|resume|clear|compact|fork) and PostModelSwitch
# Exit codes:
#   0 = always (advisory, never blocks)

set -uo pipefail

PAYLOAD="$(cat)"

printf '%s' "$PAYLOAD" | python3 -c '
import json
import sys

print(
    "Judgment rules this harness does not inject:\n"
    "- Prefer a targeted edit over a whole-file rewrite.\n"
    "- Keep the diff to what the task asks. Report a nearby bug or cleanup as a "
    "follow-up line, not as a change in this diff.\n"
    "- Keep prose plain and short.\n"
    "- Mark reused wording as a quote; do not restate it as your own.\n"
    "- A benign request stays benign. Do not refuse work that only sounds "
    "sensitive."
)

try:
    payload = json.load(sys.stdin)
except (json.JSONDecodeError, OSError):
    sys.exit(0)
if not isinstance(payload, dict):
    sys.exit(0)

model = payload.get("to_model") or payload.get("model")
if not isinstance(model, str) or "fable" not in model.lower():
    sys.exit(0)

print(
    "Fable session. Ask one question before acting only if a reading of the "
    "request would change the architecture; otherwise act. In a handoff or plan "
    "for another session use five headings: Goal and why; Constraints; Done "
    "check per task; Session conduct; Target model and effort. Do not paste the "
    "autonomy block, the Delivering work block, the progress-updates line, or "
    "the batching nudge; Claude Code injects all four. The `fable-prompting` "
    "skill is the long form."
)
' 2>/dev/null || exit 0
