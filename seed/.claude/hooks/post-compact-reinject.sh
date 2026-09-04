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

echo "Post-compaction reminders: 1. Finish the whole task; do not stop early or ask permission for work already requested. 2. Keep changes to what the task asks; report pre-existing bugs as follow-ups. 3. Surgically edit files. 4. Batch independent tool calls. 5. Re-read HANDOFF.md if present and run the verify command it names before claiming anything."
exit 0
