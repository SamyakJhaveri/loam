#!/usr/bin/env bash
# test_hub_ci_marketplace_lint.sh
# hub-ci treats the marketplace skill-description linter as warn-only, because
# those skills are third-party and vendored. But "warn-only" must not collapse
# into a blind `|| echo WARN` that swallows a linter that actually crashed. The
# discriminator is the linter's completion marker `Total warnings: N`:
#   - marker present  -> the linter scanned every skill; warnings are advisory,
#                        so hub-ci reports OK AND surfaces the count.
#   - marker absent    -> the linter died before completing (usage error, crash,
#                        set -euo abort, missing target); hub-ci HARD-FAILS.
# Both branches are exercised here against a STUBBED linter (mktemp), never the
# real vendored marketplace tree.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"   # bin/
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/bin" "$TMP/cultivation/marketplace/sam-cc-setup/hooks"
cp "$REAL_BIN/hub-ci.sh" "$TMP/bin/hub-ci.sh"
cp "$REAL_BIN/lib.sh"    "$TMP/bin/lib.sh"
# verify-template and the hub hook test both pass, so Check 3 is isolated.
printf '#!/usr/bin/env bash\necho \"ALL OK\"\nexit 0\n' > "$TMP/bin/verify-template.sh"
printf 'import sys\nsys.exit(0)\n'      > "$TMP/cultivation/marketplace/sam-cc-setup/hooks/test_ok.py"
LINT="$TMP/bin/lint-skill-descriptions.sh"

run_hubci() {
  set +e
  out="$(bash "$TMP/bin/hub-ci.sh" 2>&1)"
  rc=$?
  set -e
}

# --- Leg 1: warn-only (marker present) -> OK, count surfaced ----------------
# Stub reproduces the real linter's WARN>0 signature: WARN lines, the completion
# marker, and exit 1.
cat > "$LINT" <<'STUB'
#!/usr/bin/env bash
echo "WARN [alpha]: missing conditional language"
echo "WARN [beta]: description under 30 chars"
echo ""
echo "Total warnings: 2"
exit 1
STUB
chmod +x "$LINT"
run_hubci

if [ "$rc" -ne 0 ]; then
  echo "FAIL leg1: hub-ci exited $rc on warn-only marketplace lint (expected 0)"; echo "$out"; exit 1
fi
# The lint line must report OK, not FAIL...
if grep -qE '^  FAIL  lint-descriptions' <<<"$out"; then
  echo "FAIL leg1: warn-only lint was reported FAIL"; echo "$out"; exit 1
fi
# ...and it must SURFACE the count (this is what makes it not-silent).
if ! grep -E 'lint-descriptions .*marketplace' <<<"$out" | grep -q '2'; then
  echo "FAIL leg1: warn count '2' not surfaced in the lint report line"; echo "$out"; exit 1
fi

# --- Leg 2: linter died early (NO marker) -> HARD FAIL ----------------------
# Stub reproduces the real usage-error / crash signature: an error to stderr,
# nonzero exit, and NO `Total warnings:` completion marker.
cat > "$LINT" <<'STUB'
#!/usr/bin/env bash
echo "lint-skill-descriptions: cannot read target dir" >&2
exit 1
STUB
chmod +x "$LINT"
run_hubci

if [ "$rc" -eq 0 ]; then
  echo "FAIL leg2: hub-ci exited 0 though the linter died before its completion marker"; echo "$out"; exit 1
fi
if ! grep -qE '^  FAIL  lint-descriptions' <<<"$out"; then
  echo "FAIL leg2: early-death lint was not reported FAIL"; echo "$out"; exit 1
fi

echo "PASS test_hub_ci_marketplace_lint.sh"
