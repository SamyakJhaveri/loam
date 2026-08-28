#!/usr/bin/env bash
# test_hub_ci_lint_failopen.sh  (Codex H2)
# The marketplace-lint check must require the "Total warnings: N" completion
# marker in BOTH exit branches. Ruling A1 hardened only the nonzero branch; the
# rc==0 branch recorded OK with no marker check, so a linter that exits 0 without
# scanning anything passed the gate (fail-open).
#   legA: hub-ci vs a stub linter that exits 0 with NO marker -> gate must FAIL.
#   legB: the ROOT cause - the REAL lint-skill-descriptions.sh on a missing
#         marketplace dir must exit nonzero WITHOUT the marker (not "Total
#         warnings: 0" exit 0), so hub-ci's marker rule can catch it.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT

# ---- legA: hub-ci must fail-CLOSED on a marker-less rc==0 linter ------------
mkdir -p "$TMP/bin" "$TMP/cultivation/marketplace/sam-cc-setup/hooks"
cp "$REAL_BIN/hub-ci.sh" "$TMP/bin/hub-ci.sh"
cp "$REAL_BIN/lib.sh"    "$TMP/bin/lib.sh"
printf '#!/usr/bin/env bash\necho "ALL OK"\nexit 0\n' > "$TMP/bin/verify-template.sh"
# Stub linter: exits 0 but prints NO "Total warnings" marker (never scanned).
printf '#!/usr/bin/env bash\necho "nothing to do"\nexit 0\n' > "$TMP/bin/lint-skill-descriptions.sh"
printf 'import sys\nsys.exit(0)\n' > "$TMP/cultivation/marketplace/sam-cc-setup/hooks/test_ok.py"
chmod +x "$TMP/bin/"*.sh
# hub-ci discovers git-TRACKED hook tests: index the fixture first (setup only).
git -C "$TMP" init -q 2>/dev/null || true
git -C "$TMP" add -A
set +e; out="$(bash "$TMP/bin/hub-ci.sh" 2>&1)"; rc=$?; set -e
if [ "$rc" -eq 0 ]; then
  echo "FAIL legA: hub-ci exited 0 on a marker-less rc==0 linter (fail-open)"; echo "$out"; exit 1
fi
if ! grep -qi 'lint-descriptions' <<<"$out"; then
  echo "FAIL legA: lint check not reported"; echo "$out"; exit 1
fi

# ---- legB: real linter must not fail-open on a missing marketplace dir ------
mkdir -p "$TMP/b/bin"
cp "$REAL_BIN/lint-skill-descriptions.sh" "$TMP/b/bin/lint-skill-descriptions.sh"
cp "$REAL_BIN/lib.sh"                      "$TMP/b/bin/lib.sh"
chmod +x "$TMP/b/bin/lint-skill-descriptions.sh"
# NOTE: no $TMP/b/cultivation/marketplace dir exists -> the marketplace scan target is absent.
set +e; lout="$(bash "$TMP/b/bin/lint-skill-descriptions.sh" marketplace 2>&1)"; lrc=$?; set -e
if [ "$lrc" -eq 0 ]; then
  echo "FAIL legB: linter exited 0 with the marketplace dir missing (fail-open)"; echo "$lout"; exit 1
fi
if grep -qE '^Total warnings: [0-9]+' <<<"$lout"; then
  echo "FAIL legB: linter printed a completion marker though it scanned nothing"; echo "$lout"; exit 1
fi

echo "PASS test_hub_ci_lint_failopen.sh"
