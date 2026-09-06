#!/usr/bin/env bash
# Public gate: all stages use one frozen source tree; exit status is authoritative.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if python3 "$ROOT/bin/verification_snapshot.py" --root "$ROOT" -- \
    bash bin/verify-template-stages.sh; then
  echo "verify-template: PASSED"
else
  echo "verify-template: FAILED"
  exit 1
fi
