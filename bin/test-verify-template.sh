#!/usr/bin/env bash
# Test: verify-template.sh exits 0 on a clean template, exits 1 if bootstrap is broken.
set -euo pipefail
EXPECTED_FLAVORS=(research software-eng ml hpc)

bash bin/verify-template.sh > /tmp/verify-out.log 2>&1 || { cat /tmp/verify-out.log; exit 1; }

for f in "${EXPECTED_FLAVORS[@]}"; do
  grep -q "OK: flavor $f" /tmp/verify-out.log || { echo "FAIL: flavor $f not verified"; exit 1; }
done
echo "PASS"
