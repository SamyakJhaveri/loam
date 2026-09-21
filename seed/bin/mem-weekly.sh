#!/usr/bin/env bash
# mem-weekly.sh - weekly maintenance for the memory store (run from cron).
#
# Commits the store as a git baseline, then regenerates a recurring-errors
# report from the captured traces. Zero model calls. The cron line is documented
# in seed/docs/HARNESS.md; this ticket does not install it.
#
# Store root: $LOAM_MEMSTORE, default ~/memstore.
# Usage: mem-weekly.sh

set -uo pipefail

STORE="${LOAM_MEMSTORE:-$HOME/memstore}"
mkdir -p "$STORE" || exit 0
cd "$STORE" || exit 0

# The baseline holds reports and native-memory caches only. Traces stay out of git so
# that deleting a trace file forgets it (HARNESS.md, Accepted risks); a git history of
# transcripts would keep a pasted secret after the file is gone.
[ -d .git ] || git init -q 2>/dev/null
printf 'traces/\n.throttle/\n' > .gitignore
git add -A 2>/dev/null \
  && git -c user.name=memstore -c user.email=memstore@localhost \
       commit -qm "weekly $(date +%F)" 2>/dev/null || true

mkdir -p reports
grep -rohE 'Error: .{0,60}|RuntimeError.{0,60}|Traceback.{0,60}' traces/ 2>/dev/null \
  | sort | uniq -c | sort -rn | head -20 > reports/recurring-errors.md

# Capture, retrieval, and application counts, so the weekly report says whether
# the memory layer is used, not only which errors recur. Plain grep over traces/.
traces=$(ls traces/*/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
sessions="n/a"
CLAUDE_PROJECTS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"
CODEX_SESSIONS="${CODEX_HOME:-$HOME/.codex}/sessions"
if [ -d "$CLAUDE_PROJECTS" ] || [ -d "$CODEX_SESSIONS" ]; then
  claude_n=0; codex_n=0
  [ -d "$CLAUDE_PROJECTS" ] && claude_n=$(ls "$CLAUDE_PROJECTS"/*/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
  [ -d "$CODEX_SESSIONS" ] && codex_n=$(find "$CODEX_SESSIONS" -type f -name 'rollout-*.jsonl' 2>/dev/null | wc -l | tr -d ' ')
  sessions=$((claude_n + codex_n))
fi
retrieval=$(grep -rc -e memsearch traces/ 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}')
application=$(grep -rcE 'APPLICABLE|STALE|UNVERIFIED' traces/ 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}')
{
  printf 'capture %s traces, %s sessions seen\n' "$traces" "$sessions"
  printf 'retrieval %s\n' "$retrieval"
  printf 'application %s\n' "$application"
} > reports/counts.md
exit 0
