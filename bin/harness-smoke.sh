#!/usr/bin/env bash
# Smoke the same intended source snapshot used by the full verification gate.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if python3 "$ROOT/bin/verification_snapshot.py" --root "$ROOT" -- \
    bash bin/harness-smoke-stages.sh "$@"; then
  echo "harness-smoke: PASS"
else
  echo "harness-smoke: FAIL"
  exit 1
fi
