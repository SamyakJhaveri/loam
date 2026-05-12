#!/usr/bin/env bash
# Test: verify-template.sh exits 0 on a clean template, exits 1 if bootstrap is broken.
set -euo pipefail
cd "$(dirname "$0")/.."
EXPECTED_FLAVORS=(research software-eng)
LOGFILE=$(mktemp)
trap 'rm -f "$LOGFILE"' EXIT

bash bin/verify-template.sh > "$LOGFILE" 2>&1 || { cat "$LOGFILE"; exit 1; }

for f in "${EXPECTED_FLAVORS[@]}"; do
  grep -q "OK: flavor $f" "$LOGFILE" || { echo "FAIL: flavor $f not verified"; exit 1; }
done
echo "PASS"
