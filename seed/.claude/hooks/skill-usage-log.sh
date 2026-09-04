#!/usr/bin/env bash
# skill-usage-log.sh - PreToolUse(Skill): append one line per Skill invocation.
# That log is the eval: which skills fire, how often. Appends to root/.claude/skill-usage.log.
#
# Triggered by: PreToolUse on Skill
# Exit codes:
#   0 = always (logging hook, never blocks)

set -uo pipefail

PAYLOAD="$(cat)"

ROOT="$(printf '%s' "$PAYLOAD" | python3 -c 'import sys, json
try:
    c = json.load(sys.stdin).get("cwd")
    print(c if isinstance(c, str) else "")
except Exception:
    print("")' 2>/dev/null)" || ROOT=""
if [ -z "$ROOT" ] || [ ! -d "$ROOT" ]; then
    ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
fi
[ -z "$ROOT" ] && exit 0
# Only log when .claude already exists; never create it.
[ -d "$ROOT/.claude" ] || exit 0

read -r NAME ARGS <<EOF
$(printf '%s' "$PAYLOAD" | python3 -c 'import sys, json
try:
    ti = json.load(sys.stdin).get("tool_input") or {}
    name = ti.get("skill") or "unknown"
    args = ti.get("args") or ""
    print(str(name).replace("\n", " "), str(args).replace("\n", " "))
except Exception:
    print("unparseable")' 2>/dev/null || printf 'unparseable')
EOF
[ -z "$NAME" ] && NAME="unparseable"

# No args means no trailing field, so the line never ends in a stray space.
if [ -n "${ARGS:-}" ]; then
    printf '%s %s %s\n' "$(date -Iseconds)" "$NAME" "$ARGS" >> "$ROOT/.claude/skill-usage.log"
else
    printf '%s %s\n' "$(date -Iseconds)" "$NAME" >> "$ROOT/.claude/skill-usage.log"
fi
exit 0
