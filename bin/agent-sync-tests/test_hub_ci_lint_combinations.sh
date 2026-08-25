#!/usr/bin/env bash
# test_hub_ci_lint_combinations.sh  (Codex H9)
# Check 3 must validate the linter's (exit code, warning count) CONTRACT, not just
# the presence of the marker. The linter exits 0 iff count==0 and exits 1 iff
# count>0. hub-ci must accept ONLY those two combinations; every other pairing is
# a contract violation (a linter that exited 0 while reporting 5, or exited 1 while
# reporting 0) and must fail the gate.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

build() { # $1 = lint count line ; $2 = lint exit code
  rm -rf "${TMP:?}/bin" "${TMP:?}/cultivation"
  mkdir -p "$TMP/bin" "$TMP/cultivation/marketplace/sam-cc-setup/hooks"
  cp "$REAL_BIN/hub-ci.sh" "$TMP/bin/hub-ci.sh"
  cp "$REAL_BIN/lib.sh"    "$TMP/bin/lib.sh"
  printf '#!/usr/bin/env bash\necho "ALL OK"\nexit 0\n' > "$TMP/bin/verify-template.sh"
  printf '#!/usr/bin/env bash\necho "%s"\nexit %s\n' "$1" "$2" > "$TMP/bin/lint-skill-descriptions.sh"
  printf 'import sys\nsys.exit(0)\n' > "$TMP/cultivation/marketplace/sam-cc-setup/hooks/test_ok.py"
  chmod +x "$TMP/bin/"*.sh
}
run() { set +e; out="$(bash "$TMP/bin/hub-ci.sh" 2>&1)"; rc=$?; set -e; }

# Invalid combo 1: exit 0 but count>0 -> FAIL
build "Total warnings: 5" 0; run
if [ "$rc" -eq 0 ]; then echo "FAIL combo(rc0,count5): hub-ci accepted exit 0 with 5 warnings"; echo "$out"; exit 1; fi

# Invalid combo 2: exit 1 but count==0 -> FAIL
build "Total warnings: 0" 1; run
if [ "$rc" -eq 0 ]; then echo "FAIL combo(rc1,count0): hub-ci accepted exit 1 with 0 warnings"; echo "$out"; exit 1; fi

# Valid combo A: exit 0, count 0 -> OK
build "Total warnings: 0" 0; run
if [ "$rc" -ne 0 ]; then echo "FAIL combo(rc0,count0): hub-ci rejected a clean linter run"; echo "$out"; exit 1; fi

# Valid combo B: exit 1, count 5 -> OK (warn-only)
build "Total warnings: 5" 1; run
if [ "$rc" -ne 0 ]; then echo "FAIL combo(rc1,count5): hub-ci rejected a valid warn-only run"; echo "$out"; exit 1; fi
grep -q '5 warnings' <<<"$out" || { echo "FAIL combo(rc1,count5): warn count 5 not surfaced"; echo "$out"; exit 1; }

echo "PASS test_hub_ci_lint_combinations.sh"
