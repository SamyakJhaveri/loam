#!/usr/bin/env bash
# test_hub_ci_strict_tooling.sh  (Codex C1)
# hub-ci is the RELEASE gate, so it must be STRICT: verify-template.sh SKIPs
# (prints "SKIP: ..." and still exits 0 / "ALL OK") when shellcheck or copier are
# absent - reasonable for a hand dev-run, but on a fresh clone or CI box it means
# the render/lint checks never ran. A gate that records OK for a check that was
# skipped would let release.sh push untested. hub-ci must detect a `^SKIP:` line
# in verify-template's output and fail the gate, surfacing which check skipped.
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

# --- NEGATIVE: verify-template SKIPPED a check -> gate must FAIL --------------
build '#!/usr/bin/env bash
echo "SKIP: copier not installed; skipping render tests"
echo "ALL OK"
exit 0'
run
if [ "$rc" -eq 0 ]; then
  echo "FAIL: hub-ci exited 0 although verify-template SKIPPED a check"; echo "$out"; exit 1
fi
if ! grep -qi 'skip' <<<"$out"; then
  echo "FAIL: report does not surface the skipped check"; echo "$out"; exit 1
fi

# --- POSITIVE: verify-template ran fully (no SKIP) -> gate green -------------
build '#!/usr/bin/env bash
echo "ALL OK"
exit 0'
run
if [ "$rc" -ne 0 ]; then
  echo "FAIL: hub-ci failed although verify-template ran clean (no SKIP)"; echo "$out"; exit 1
fi

echo "PASS test_hub_ci_strict_tooling.sh"
