#!/usr/bin/env bash
# Thin wrapper - the canonical scan engine lives in the hub repo as bin/agent-sync-scan.sh,
# behind the bin/agent-sync.sh dispatcher.
# Behavior contract: env SAM_CC_HUB_REPO / SAM_CC_DEFER_SESSIONS, no positional args,
# refuses on dirty project .claude/, fail-closed manifest guard, .sync-state ledger in the hub.
set -euo pipefail
HUB="${SAM_CC_HUB_REPO:-$HOME/Desktop/loam}"
ENGINE="${SAM_CC_ENGINE:-$HUB/bin/agent-sync.sh}"
[ -f "$ENGINE" ] || { echo "sync-to-hub: canonical engine not found at $ENGINE (set SAM_CC_HUB_REPO or SAM_CC_ENGINE)" >&2; exit 1; }
if [ "${1:-}" = "--prune" ]; then
  shift
  exec bash "$ENGINE" prune "$@"
fi
exec bash "$ENGINE" scan "$@"
