#!/usr/bin/env bash
# mem-recall.sh - inject a short memory manifest at SessionStart.
#
# Hook event: SessionStart (matcher startup|resume|clear). Reads the hook JSON
# on stdin (cwd) and prints to stdout; Claude Code adds stdout to the context.
# Zero model calls. Prints nothing when the store has no INDEX for this repo.
#
# The manifest names what it loaded (recent sessions, hint bullets, handoff), the
# last INDEX lines, what exists but was not loaded and the one command to reach
# it, and the four trust labels every recalled item must carry (layers 3 and 5 of
# docs/research/memory-design-v2-2026-09-21.md). Output is capped at 4000 bytes.
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

# Key by the origin remote so recall reads the same directory mem-capture writes
# across the factory's per-worktree checkouts. Fall back to the toplevel basename
# with no origin, then to the cwd basename with no git.
repo_key() {
  local dir="$1" url top
  url="$(git -C "$dir" remote get-url origin 2>/dev/null)"
  if [ -n "$url" ]; then
    url="${url%/}"; url="${url%.git}"
    basename "$url"
    return
  fi
  top="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)"
  [ -n "$top" ] && { basename "$top"; return; }
  basename "$dir"
}

REPO="$(repo_key "$CWD")"
INDEX="$STORE/traces/$REPO/INDEX.md"
[ -f "$INDEX" ] || exit 0

INDEX_LINES="$(tail -n 5 "$INDEX")"
N_SESS="$(printf '%s\n' "$INDEX_LINES" | grep -c .)"

TRACES_DIR="$STORE/traces/$REPO"
TRACES_COUNT="$(find "$TRACES_DIR" -type f \( -name '*.jsonl' -o -name '*.jsonl.gz' \) 2>/dev/null | wc -l | tr -d ' ')"

# The newest note's first three hint bullets, when MEM-03 has written notes here.
NOTES_DIR="$STORE/notes/$REPO"
NOTES_COUNT=0
HINT_BULLETS=""
HINT_N=0
if [ -d "$NOTES_DIR" ]; then
  NOTES_COUNT="$(find "$NOTES_DIR" -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  NEWEST="$(ls -t "$NOTES_DIR"/*.md 2>/dev/null | head -1)"
  if [ -n "$NEWEST" ]; then
    HINT_BULLETS="$(awk '
      tolower($0) ~ /hint/ { inhint=1; next }
      inhint && /^#/ { inhint=0 }
      inhint && /^[[:space:]]*[-*] / && c<3 { print; c++ }
    ' "$NEWEST")"
    HINT_N="$(printf '%s\n' "$HINT_BULLETS" | grep -c .)"
  fi
fi

{
  printf '## Memory (%s)\n' "$REPO"
  printf 'Loaded: %s recent sessions, %s hint bullets, 0 handoff\n' "$N_SESS" "$HINT_N"
  printf '%s\n' "$INDEX_LINES"
  [ -n "$HINT_BULLETS" ] && printf '%s\n' "$HINT_BULLETS"
  printf 'Not loaded: %s notes, %s traces under .loam/memory; reach them with memsearch <pattern> or mem-inspect <session>; do not grep the raw traces.\n' "$NOTES_COUNT" "$TRACES_COUNT"
  printf 'Label every recalled item before acting on it: supported (the trace shows it), contradicts (the current repo or host disagrees), near-match (similar task, different conditions), insufficient (not enough to act); check git log -1, hostname, and tool versions first.\n'
} | head -c 4000
exit 0
