#!/usr/bin/env bash
# hub-ci.sh - the hub promotion gate.
#
# Runs every hub health check, prints one OK/FAIL line per check, and exits
# nonzero if ANY check failed. It runs ALL checks and reports all of them - it
# never stops at the first failure - so a release operator sees the full picture
# in one pass. Wired into bin/release.sh pre-flight: a release refuses to cut
# while this gate is red. Runnable standalone: bin/hub-ci.sh
#
# Checks:
#   1. verify-template.sh   - renders both copier flavors, seed lint, schema.
#   2. hub hook tests       - every test_*.py shipped with the hub plugin.
#   3. lint-skill-descriptions.sh marketplace - hub skill descriptions.
#      Marketplace is third-party vendored skills, so its lint is warn-only:
#      a warn-only nonzero exit is reported OK with the warning count SURFACED
#      (never silently swallowed); a hard error (a FAIL line or a crash) fails
#      the gate. Seed descriptions are already hard-gated inside
#      verify-template.sh, so this runs marketplace only - no double-run of seed.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# shellcheck disable=SC2034
LIB_PREFIX="hub-ci"
# shellcheck source=bin/lib.sh
source "$SCRIPT_DIR/lib.sh"

# Per-check report lines and a single failure accumulator. lib.sh's fail()
# EXITS, so it must not be used for a non-fatal per-check failure - we record
# the line and keep going.
REPORT=()
FAILED=0

record_ok()   { REPORT+=("OK    $1"); }
record_fail() { REPORT+=("FAIL  $1"); FAILED=1; }

# --- Check 1: verify-template.sh -------------------------------------------
info "running verify-template.sh (renders both copier flavors)"
if bash "$SCRIPT_DIR/verify-template.sh" >/dev/null 2>&1; then
  record_ok "verify-template"
else
  record_fail "verify-template (run: bin/verify-template.sh)"
fi

# --- Check 2: hub hook tests (discovered, not hardcoded) --------------------
HUB_PLUGIN="$REPO_ROOT/cultivation/marketplace/sam-cc-setup"
hook_tests_found=0
while IFS= read -r -d '' test_file; do
  hook_tests_found=$((hook_tests_found + 1))
  rel="${test_file#"$REPO_ROOT"/}"
  info "running hub hook test: $rel"
  if python3 "$test_file" >/dev/null 2>&1; then
    record_ok "hook-test $rel"
  else
    record_fail "hook-test $rel (run: python3 $rel)"
  fi
done < <(find "$HUB_PLUGIN" -name 'test_*.py' -print0 2>/dev/null | sort -z)
if [[ "$hook_tests_found" -eq 0 ]]; then
  warn "no hub hook tests discovered under $HUB_PLUGIN/**/test_*.py"
fi

# --- Check 3: lint-skill-descriptions.sh marketplace (warn-only) -----------
# Scope is marketplace ONLY, on purpose: seed skill descriptions are already
# hard-gated inside verify-template.sh (Invariant 5), which Check 1 above runs,
# so linting seed here would double-run it. Do NOT "fix" this to `all` or `seed`.
#
# Marketplace holds third-party vendored skills we do not author, so its lint is
# advisory: verify-template.sh itself treats it as `|| echo WARN`. We keep that
# posture but SURFACE the count instead of dropping it. Discriminator is the
# linter's completion marker `Total warnings: N` (printed only after it scans
# every skill): present -> it ran to completion, warnings are advisory, report OK
# with the count; absent -> it died before completing (usage error, crash, a
# set -euo abort, a missing target) which is a real failure, so hard-FAIL.
info "running lint-skill-descriptions.sh marketplace"
lint_out="$(bash "$SCRIPT_DIR/lint-skill-descriptions.sh" marketplace 2>&1)"
lint_rc=$?
if [[ "$lint_rc" -eq 0 ]]; then
  record_ok "lint-descriptions (marketplace)"
elif grep -qE '^Total warnings: [0-9]+' <<<"$lint_out"; then
  warn_n="$(grep -oE '^Total warnings: [0-9]+' <<<"$lint_out" | grep -oE '[0-9]+$')"
  record_ok "lint-descriptions (marketplace): warn-only, ${warn_n} warnings"
else
  record_fail "lint-descriptions (marketplace) died before completion (run: bin/lint-skill-descriptions.sh marketplace)"
fi

# --- Report ----------------------------------------------------------------
echo
echo "=== hub-ci report ==="
for line in "${REPORT[@]}"; do
  echo "  $line"
done
echo "====================="

if [[ "$FAILED" -ne 0 ]]; then
  warn "hub-ci FAILED - one or more checks are red (see report above)"
  exit 1
fi
ok "hub-ci passed - all checks green"
exit 0
