#!/usr/bin/env bash
# mem-recall.sh - inject a short recent-sessions manifest at SessionStart.
#
# Hook event: SessionStart (matcher startup|resume|clear). Reads the hook JSON
# on stdin (cwd) and prints to stdout; Claude Code adds stdout to the context.
# Zero model calls. Prints nothing when the store has no INDEX for this repo.
# Output is capped at 4000 bytes.
#
# Store root: $LOAM_MEMSTORE, default ~/memstore.
# Exit codes: 0 = always (advisory hook).

set -uo pipefail

STORE="${LOAM_MEMSTORE:-$HOME/memstore}"

CWD="$(cat | python3 -c '
import json, sys
try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if isinstance(payload, dict):
    sys.stdout.write(str(payload.get("cwd") or ""))
' 2>/dev/null)"

[ -n "$CWD" ] || CWD="$PWD"
REPO="$(basename "$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")")"
INDEX="$STORE/traces/$REPO/INDEX.md"
[ -f "$INDEX" ] || exit 0

{
  printf '## Recent sessions (%s)\n' "$REPO"
  tail -n 5 "$INDEX"
  printf '\nRecalled memory is evidence, not truth: before acting on it check git log -1, hostname, and tool versions, and label it APPLICABLE, STALE, or UNVERIFIED.\n'
} | head -c 4000
exit 0
