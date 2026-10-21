#!/usr/bin/env bash
# post-compact-reinject.sh
#
# SessionStart hook, matcher: compact.
# Purpose: after a compaction the task is easily lost, so point Claude back at the
# handoff note (format in docs/WORKERS.md). Stdout is added to the context.
#
# Exit codes: 0 = always (advisory)

set -uo pipefail

# Drain stdin so the caller's pipe never blocks; the payload is not needed.
cat >/dev/null 2>&1 || true

# A project rendered with memory=false has no memory hooks, and keeps its handoff in HANDOFF.md.
if [ -f "$(dirname "$0")/mem-recall.sh" ]; then
  echo "After compaction: re-read the handoff, .loam/memory/handoff/<repo>.md, or the newest file in .loam/memory/handoff/<repo>/archive/ if this session claimed it at startup (format: docs/WORKERS.md). Compare its Written at hash with git rev-parse HEAD before claiming any result; the repository state wins."
else
  echo "After compaction: re-read the handoff, HANDOFF.md at the repo root, if it exists (format: docs/WORKERS.md). Compare its Written at hash with git rev-parse HEAD before claiming any result; the repository state wins."
fi
exit 0
