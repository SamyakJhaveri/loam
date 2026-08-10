#!/usr/bin/env bash
# Canonical dual-host sync engine - single home for both promotion directions.
#   scan    - bulk interactive project->hub sync: owns the .sync-state defer ledger,
#             the fail-closed portability-manifest guard, and the transitive
#             requires-closure check (validated against the hub's committed HEAD).
#   promote - per-path project->template promotion (delegates to template-sync.sh;
#             commits under the caller's git identity; pushes only with --push).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
sub="${1:-}"; shift 2>/dev/null || true
case "$sub" in
  scan)    exec bash "$here/agent-sync-scan.sh" "$@";;
  promote) exec bash "$here/template-sync.sh" promote "$@";;
  *) echo "usage: agent-sync.sh {scan|promote [--push]}" >&2; exit 1;;
esac
