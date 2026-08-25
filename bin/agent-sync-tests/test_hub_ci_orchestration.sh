#!/usr/bin/env bash
# test_hub_ci_orchestration.sh
# hub-ci.sh is the hub promotion gate. Two orchestration invariants that a naive
# "run the checks" script gets wrong:
#   (1) it must run EVERY check and report each, never stopping at the first
#       failure, so one broken check cannot mask the state of the others; and
#   (2) a broken hub must make the gate exit nonzero AND the report must name
#       the failing check.
# This test drives hub-ci against a FAST fake repo root (stubbed
# verify-template.sh + lint-skill-descriptions.sh, a real-shaped hub-plugin
# hooks dir) so it never pays the ~52s copier render. The real hub passing the
# real hub-ci is a separate acceptance run, not this unit test.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"   # bin/
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- Build a fake repo root: bin/ + hub plugin hooks dir --------------------
mkdir -p "$TMP/bin" "$TMP/cultivation/marketplace/sam-cc-setup/hooks"
cp "$REAL_BIN/hub-ci.sh" "$TMP/bin/hub-ci.sh"
cp "$REAL_BIN/lib.sh"    "$TMP/bin/lib.sh"
# Stub the two heavy sub-scripts so orchestration is tested in isolation.
printf '#!/usr/bin/env bash\nexit 0\n'            > "$TMP/bin/verify-template.sh"
printf '#!/usr/bin/env bash\necho "ALL OK"\nexit 0\n' > "$TMP/bin/lint-skill-descriptions.sh"
chmod +x "$TMP/bin/"*.sh

HOOKS="$TMP/cultivation/marketplace/sam-cc-setup/hooks"

run_hubci() {
  # Echoes combined output; sets global rc.
  set +e
  out="$(bash "$TMP/bin/hub-ci.sh" 2>&1)"
  rc=$?
  set -e
}

# --- Case A: a broken hub hook test -> gate FAILS, names it, runs all -------
printf 'import sys\nsys.exit(1)\n' > "$HOOKS/test_broken.py"
run_hubci

if [ "$rc" -eq 0 ]; then
  echo "FAIL: hub-ci exited 0 with a broken hub hook test present"; echo "$out"; exit 1
fi
if ! grep -q 'test_broken.py' <<<"$out"; then
  echo "FAIL: report does not name the failing hook test test_broken.py"; echo "$out"; exit 1
fi
# Ran ALL checks, no early stop: verify-template (check 1, before the failure)
# AND lint-descriptions (check 3, after the failure) both reported.
if ! grep -q 'verify-template' <<<"$out"; then
  echo "FAIL: verify-template check line missing (check 1 not reported)"; echo "$out"; exit 1
fi
if ! grep -q 'lint-descriptions' <<<"$out"; then
  echo "FAIL: lint-descriptions check line missing (gate stopped before check 3)"; echo "$out"; exit 1
fi

# --- Case B: the hook test now passes -> gate is green, exit 0 --------------
rm -f "$HOOKS/test_broken.py"
printf 'import sys\nsys.exit(0)\n' > "$HOOKS/test_ok.py"
run_hubci

if [ "$rc" -ne 0 ]; then
  echo "FAIL: hub-ci exited $rc on a healthy fake hub (expected 0)"; echo "$out"; exit 1
fi
if grep -q '^  FAIL' <<<"$out"; then
  echo "FAIL: a check reported FAIL on a healthy fake hub"; echo "$out"; exit 1
fi
if ! grep -q 'test_ok.py' <<<"$out"; then
  echo "FAIL: the passing hook test was not discovered/reported"; echo "$out"; exit 1
fi

echo "PASS test_hub_ci_orchestration.sh"
