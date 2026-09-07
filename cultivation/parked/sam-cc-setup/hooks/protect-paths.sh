#!/usr/bin/env bash
# protect-paths.sh - deny writes/deletes to a repo-declared protected path set
#
# Triggered by: PreToolUse on Edit|Write|Bash
# Config:      .claude/protected-paths.txt (one glob per line, '#' comments)
# Dormant:     exits 0 immediately when the config is absent
#
# All matching logic lives in protect_paths.py (testable without a hook harness).
# Exit codes: 0 = allow, 2 = BLOCK. Fail-open on infrastructure errors: a bug
# here must never brick every Edit/Write/Bash in the session.

set -uo pipefail
trap 'exit 0' ERR

ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
ROOT="${ROOT%/}"                      # a trailing slash here can disarm path matching
CONFIG="$ROOT/.claude/protected-paths.txt"
[ -f "$CONFIG" ] || exit 0

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

VERDICT=$(python3 "$HERE/protect_paths.py" --config "$CONFIG" --root "$ROOT" 2>/dev/null)

case "$VERDICT" in
  block*)
    REASON="${VERDICT#block}"
    REASON="${REASON#$'\t'}"
    echo "BLOCKED: ${REASON:-path is protected}" >&2
    echo "Protected paths are declared in .claude/protected-paths.txt." >&2
    echo "If this change is intended, remove or adjust the matching line there first." >&2
    exit 2
    ;;
esac

exit 0
