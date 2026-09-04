#!/usr/bin/env bash
# Bash audit log - append every finished Bash command, with its exit code, to a
# timestamped log so eval runs, build commands, and debug sessions can be
# replayed later (experiment reproducibility).
#
# Triggered by: PostToolUse and PostToolUseFailure on Bash (both events route
# here). PostToolUse carries tool_response.exit_code; PostToolUseFailure carries
# the failure text in "error".
#
# Project root comes from the payload "cwd" field, NOT CLAUDE_PROJECT_DIR:
# under `claude --worktree` only cwd carries the worktree path. Falls back to
# `git rev-parse --show-toplevel`, then exits 0 if neither resolves.
#
# Exit codes:
#   0 = always (logging hook, never blocks)

set -uo pipefail

PAYLOAD="$(cat)"

# Project root: cwd field first (see header), then git toplevel, else give up.
ROOT="$(printf '%s' "$PAYLOAD" | python3 -c '
import sys, json
try:
    print(json.load(sys.stdin).get("cwd") or "")
except Exception:
    print("")' 2>/dev/null)"
[ -n "$ROOT" ] || ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || true
[ -n "$ROOT" ] || exit 0

# Exit code + command in one parse. PostToolUse -> tool_response.exit_code (else
# "?"); PostToolUseFailure -> first integer after "exit code" (case-insensitive)
# in "error", else "fail"; malformed JSON -> "?" / "unparseable". Fields are
# NUL-separated so a multi-line or empty command survives intact.
EXIT=""; COMMAND=""
{ IFS= read -r -d '' EXIT; IFS= read -r -d '' COMMAND; } < <(printf '%s' "$PAYLOAD" | python3 -c '
import sys, json, re
try:
    d = json.load(sys.stdin)
except Exception:
    sys.stdout.write("?\x00unparseable\x00"); sys.exit(0)
ti = d.get("tool_input")
cmd = ti.get("command", "") if isinstance(ti, dict) else ""
if d.get("hook_event_name") == "PostToolUseFailure":
    m = re.search(r"exit code\D*(\d+)", str(d.get("error", "")), re.I)
    code = m.group(1) if m else "fail"
else:
    tr = d.get("tool_response")
    code = tr.get("exit_code", "?") if isinstance(tr, dict) else "?"
sys.stdout.write("%s\x00%s\x00" % (code, cmd))
' 2>/dev/null)
# Empty EXIT means python produced nothing (e.g. unavailable); treat as unparseable.
[ -n "$EXIT" ] || { EXIT="?"; COMMAND="unparseable"; }

# Experiment name from the environment; "-" when unset or empty.
EXP="-"
[ -n "${EXPERIMENT_ACTIVE:-}" ] && EXP="$EXPERIMENT_ACTIVE"

LINE="$(date -Iseconds) | exit=$EXIT | $EXP | $COMMAND"

# Always log to the project's .claude/audit.log when that directory exists.
[ -d "$ROOT/.claude" ] && printf '%s\n' "$LINE" >> "$ROOT/.claude/audit.log"

# When an experiment is active and its folder exists, mirror the line into the
# experiment's per-day command log. Session 6 owns the run-folder layout and may
# re-point this path.
if [ -n "${EXPERIMENT_ACTIVE:-}" ] && [ -d "$ROOT/experiments/$EXP" ]; then
    DIR="$ROOT/experiments/$EXP/logs/commands"
    mkdir -p "$DIR" 2>/dev/null && printf '%s\n' "$LINE" >> "$DIR/$(date -u +%F).log"
fi

exit 0
