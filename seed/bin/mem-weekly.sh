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

[ -d .git ] || git init -q 2>/dev/null
git add -A 2>/dev/null && git commit -qm "weekly $(date +%F)" 2>/dev/null || true

mkdir -p reports
grep -rohE 'Error: .{0,60}|RuntimeError.{0,60}|Traceback.{0,60}' traces/ 2>/dev/null \
  | sort | uniq -c | sort -rn | head -20 > reports/recurring-errors.md
exit 0
