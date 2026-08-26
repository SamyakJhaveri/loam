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
#      Marketplace is third-party vendored skills, so its lint is warn-only. The
#      linter's completion marker "Total warnings: N" is the discriminator: when
#      it is present the linter scanned every skill, so the warnings are advisory
#      and the check reports OK with the count SURFACED (never silently swallowed);
#      when it is absent the linter died before completing (usage error, crash,
#      set -euo abort, missing target), which hard-fails the gate. Seed
#      descriptions are already hard-gated inside verify-template.sh, so this runs
#      marketplace only - no double-run of seed.

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
# verify-template.sh SKIPS a check (prints a "SKIP:" line and still exits 0) when
# a tool it needs is absent - shellcheck, or copier/uvx for the render tests.
# That is a reasonable convenience for a hand dev-run, but hub-ci is the RELEASE
# gate: a check that was skipped is a check that did NOT run, so here a SKIP is a
# failure, not a pass. Capture the output (never discard it) and refuse on any
# `^SKIP:` line, naming it so the operator learns which dependency is missing.
info "running verify-template.sh (renders both copier flavors)"
vt_out="$(bash "$SCRIPT_DIR/verify-template.sh" 2>&1)"
vt_rc=$?
if [[ "$vt_rc" -ne 0 ]]; then
  record_fail "verify-template (run: bin/verify-template.sh)"
elif grep -q '^SKIP:' <<<"$vt_out"; then
  vt_skips="$(grep '^SKIP:' <<<"$vt_out" | tr '\n' ' ')"
  record_fail "verify-template SKIPPED a check (missing tool); strict release gate refuses: ${vt_skips}"
elif ! grep -qx 'ALL OK' <<<"$vt_out"; then
  # Same discipline as Check 3: require verify-template's own completion marker.
  # It prints "ALL OK" as its last line only after every invariant passed, so an
  # exit-0 run without it did not run to completion - do not record it green.
  record_fail "verify-template exited 0 without its 'ALL OK' completion marker (did not run to completion)"
else
  record_ok "verify-template"
fi

# --- Check 2: hub hook tests (git-TRACKED, not just on disk) ----------------
# hub-ci validates the live WORKTREE, but release.sh tags/pushes COMMITTED
# objects, so the gate must run only git-tracked tests: a gitignored or untracked
# test_*.py would run here yet never ship in the tag (and the mirror - the gate
# could pass on a test the tag omits). So discovery is by `git ls-files`, not a
# filesystem `find`, reusing the tracked-enumeration shape from
# bin/agent-sync-scan.sh (8b, 075e7ae). ls-files reads the index. Discovery must
# fail LOUD: a non-repo, an ls-files error, a missing dir, or zero tracked tests
# are all broken states, never a quiet pass. `find` cannot see trackedness, so
# it is gone. (The clean/smudge case - a filter rewriting content on checkout -
# is NOT covered here; that needs the isolated-HEAD checkout, a Ticket 9 residual.)
HUB_PLUGIN_REL="cultivation/marketplace/sam-cc-setup"
HUB_PLUGIN="$REPO_ROOT/$HUB_PLUGIN_REL"
if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  # A distinct, accurate message: tracked discovery is a NEW precondition, so a
  # missing repo must not surface as "no tests found" and send someone hunting.
  record_fail "hub-ci must run inside a git repository to validate tracked content, but $REPO_ROOT is not one"
elif [[ ! -d "$HUB_PLUGIN" ]]; then
  record_fail "hub plugin dir missing: $HUB_PLUGIN_REL (broken checkout)"
else
  hook_list="$(mktemp)"
  if git -C "$REPO_ROOT" ls-files -z -- ":(literal)$HUB_PLUGIN_REL" 2>/dev/null > "$hook_list"; then
    # Read the checked ls-files NUL stream DIRECTLY and filter by basename glob -
    # no `grep | sort` pipeline (whose `|| true` used to swallow a partial-pipeline
    # failure and let the gate pass on an INCOMPLETE tracked-test list, R5-H1).
    # ls-files output is already NUL-delimited and sorted, so this stays
    # deterministic and runs EVERY tracked test or fails the enclosing ls-files
    # check; there is no middle state.
    hook_tests_found=0
    while IFS= read -r -d '' rel; do
      case "${rel##*/}" in
        test_*.py) ;;
        *) continue ;;
      esac
      hook_tests_found=$((hook_tests_found + 1))
      info "running hub hook test: $rel"
      if python3 "$REPO_ROOT/$rel" >/dev/null 2>&1; then
        record_ok "hook-test $rel"
      else
        record_fail "hook-test $rel (run: python3 $rel)"
      fi
    done < "$hook_list"
    if [[ "$hook_tests_found" -eq 0 ]]; then
      record_fail "no git-tracked hub hook tests discovered under $HUB_PLUGIN_REL/**/test_*.py (broken checkout)"
    fi
  else
    record_fail "hub hook test discovery failed (git ls-files error under $HUB_PLUGIN_REL)"
  fi
  rm -f "$hook_list"
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
if ! grep -qE '^Total warnings: [0-9]+' <<<"$lint_out"; then
  # Require the completion marker on BOTH exit paths. A rc==0 WITHOUT the marker
  # is a linter that died before scanning (usage error, crash, set -euo abort,
  # missing target), not a clean pass - fail closed rather than fail open.
  record_fail "lint-descriptions (marketplace) died before completion (no 'Total warnings' marker; run: bin/lint-skill-descriptions.sh marketplace)"
else
  # Validate the linter's (exit code, count) CONTRACT, not just the marker: it
  # exits 0 iff count==0 and exits 1 iff count>0. Accept ONLY those two pairings;
  # any other (exit 0 with warnings, exit 1 with none, a crash after the marker)
  # is a contract violation, so fail the gate.
  lint_n="$(grep -oE '^Total warnings: [0-9]+' <<<"$lint_out" | grep -oE '[0-9]+$' | head -1)"
  if [[ "$lint_rc" -eq 0 && "$lint_n" -eq 0 ]]; then
    record_ok "lint-descriptions (marketplace): 0 warnings"
  elif [[ "$lint_rc" -eq 1 && "$lint_n" -gt 0 ]]; then
    record_ok "lint-descriptions (marketplace): warn-only, ${lint_n} warnings"
  else
    record_fail "lint-descriptions (marketplace) inconsistent result (exit ${lint_rc}, count ${lint_n}); refusing"
  fi
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
