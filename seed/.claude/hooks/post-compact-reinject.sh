#!/usr/bin/env bash
# post-compact-reinject.sh
#
# SessionStart hook, matcher: compact.
# Purpose: after a compaction the working discipline is easily lost, so re-inject
# a short reminder list into Claude's context. Stdout is added to the context.
#
# Exit codes: 0 = always (advisory)

set -uo pipefail

# Drain stdin so the caller's pipe never blocks; the payload is not needed.
cat >/dev/null 2>&1 || true

echo "After compaction: re-read HANDOFF.md if it exists and run the verify command it names before claiming any result."
exit 0
