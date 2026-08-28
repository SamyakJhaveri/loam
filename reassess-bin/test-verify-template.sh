#!/usr/bin/env bash
# Test: verify-template.sh exits 0 on a clean template, exits 1 if bootstrap is broken.
set -euo pipefail
cd "$(dirname "$0")/.."
EXPECTED_RENDERS=("Copier render (default)" "Copier render (research)")
LOGFILE=$(mktemp)
trap 'rm -f "$LOGFILE"' EXIT

bash bin/verify-template.sh > "$LOGFILE" 2>&1 || { cat "$LOGFILE"; exit 1; }

for r in "${EXPECTED_RENDERS[@]}"; do
  grep -q "OK: $r" "$LOGFILE" || { echo "FAIL: '$r' not verified"; exit 1; }
done
echo "PASS"
