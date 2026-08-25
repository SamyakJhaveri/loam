#!/usr/bin/env bash
# test_hub_ci_verify_marker.sh  (Codex H8)
# Check 1 must require verify-template's own completion marker on the clean path,
# the same discipline Check 3 applies to the linter. verify-template.sh prints
# "ALL OK" as its last line only after every invariant passed; an exit-0 run with
# no "ALL OK" (a silent early return, a truncated run) must NOT be recorded green.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

build() { # $1 = verify-template body
  rm -rf "${TMP:?}/bin" "${TMP:?}/cultivation"
  mkdir -p "$TMP/bin" "$TMP/cultivation/marketplace/sam-cc-setup/hooks"
  cp "$REAL_BIN/hub-ci.sh" "$TMP/bin/hub-ci.sh"
  cp "$REAL_BIN/lib.sh"    "$TMP/bin/lib.sh"
  printf '%s\n' "$1" > "$TMP/bin/verify-template.sh"
  printf '#!/usr/bin/env bash\necho "Total warnings: 0"\necho "ALL OK"\nexit 0\n' > "$TMP/bin/lint-skill-descriptions.sh"
  printf 'import sys\nsys.exit(0)\n' > "$TMP/cultivation/marketplace/sam-cc-setup/hooks/test_ok.py"
  chmod +x "$TMP/bin/"*.sh
}
run() { set +e; out="$(bash "$TMP/bin/hub-ci.sh" 2>&1)"; rc=$?; set -e; }

# NEGATIVE: verify-template exits 0 but never printed ALL OK (and no SKIP) -> FAIL
build '#!/usr/bin/env bash
echo "some progress output"
exit 0'
run
if [ "$rc" -eq 0 ]; then echo "FAIL: hub-ci exited 0 though verify-template printed no ALL OK marker"; echo "$out"; exit 1; fi
if ! grep -qi 'verify-template' <<<"$out"; then echo "FAIL: verify-template not reported"; echo "$out"; exit 1; fi

# POSITIVE: verify-template printed ALL OK -> OK
build '#!/usr/bin/env bash
echo "ran everything"
echo "ALL OK"
exit 0'
run
if [ "$rc" -ne 0 ]; then echo "FAIL: hub-ci failed though verify-template printed ALL OK"; echo "$out"; exit 1; fi

echo "PASS test_hub_ci_verify_marker.sh"
