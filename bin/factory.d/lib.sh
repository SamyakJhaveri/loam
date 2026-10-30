#!/usr/bin/env bash
# bin/factory.d/lib.sh - the prelude a ticket's done-checks block is sourced after.
# Source it; do not run it. The block is run from the worktree root.
set -uo pipefail

n_pass=0
n_fail=0

# A result starts on a fresh line: after a command's output with no trailing newline it would land
# mid-line, where the supervisor's ^PASS and ^FAIL reads miss it (#180).
pass() { printf '\nPASS %s\n' "$1"; n_pass=$((n_pass + 1)); }
fail() { printf '\nFAIL %s: %s\n' "$1" "${2:-}"; n_fail=$((n_fail + 1)); }
# guard: a regression guard; runs CMD and returns its status; allowed to pass on main.
# Under LOAM_HOOK (the worker's Stop hook) a guarded bin/check passes without running:
# it takes minutes per stop, and the supervisor's own check run is the one run per round (LOOP.md).
guard() { [ -n "${LOAM_HOOK:-}" ] && [ "${1:-}" = bin/check ] && return 0; "$@"; }
# predict NAME CMD...: CMD exits 0 exactly when base shows the failure check NAME predicts (CONTRACT.md, Done checks).
# Only round 0 sets FACTORY_ROUND0 and runs CMD; a non-zero exit prints the PREDICT-MISS line round_zero turns into
# ticket-defect. CMD's own output is dropped, so it cannot print a PASS line. Every other run prints nothing.
predict() {
  local name=$1 rc
  shift
  [ "${FACTORY_ROUND0:-}" = 1 ] || return 0
  "$@" > /dev/null 2>&1
  rc=$?
  [ "$rc" -eq 0 ] || printf '\nPREDICT-MISS %s exit %s\n' "$name" "$rc"
  return 0
}

# MEASURE prints one measured row for the supervisor to collect (CONTRACT.md, Rows measured).
MEASURE() { echo "MEASURE $1 ${2:-}"; }

check_clean() {
  local dirty
  dirty=$(git status --porcelain 2>/dev/null)
  if [ -z "$dirty" ]; then
    pass worktree-clean
  else
    fail worktree-dirty "$(printf '%s\n' "$dirty" | grep -c .) uncommitted paths: $(printf '%s\n' "$dirty" | head -n 3 | tr '\n' ' ')"
  fi
}

# render_into sets render_dir to a copier render of the checkout, or render_err with render_dir empty.
tmp_root=""
trap '[ -z "$tmp_root" ] || { chmod -R u+w "$tmp_root" 2>/dev/null; rm -r "$tmp_root" 2>/dev/null; }' EXIT
render_into() {
  local out rc
  render_dir=""; render_err=""
  tmp_root=$(mktemp -d 2>/dev/null)
  [ -d "${tmp_root:-}" ] || { render_err="could not create a temp directory"; return; }
  render_dir="$tmp_root/render"
  out=$(uvx copier copy --trust --defaults --vcs-ref HEAD -d project_name=check . "$render_dir" 2>&1)
  rc=$?
  [ "$rc" -eq 0 ] || { render_err="copier copy exit $rc; $(printf '%s' "$out" | tail -n 2 | tr '\n' ' ')"; render_dir=""; }
}
