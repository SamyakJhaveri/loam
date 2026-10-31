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
# Each pass-over marker line CMD prints (bin/check's `SKIPPED: <step>`) is also copied to fd 9, the block's own
# stdout (the checks file), so `guard bin/check >/dev/null` cannot hide a step that did not run from status
# --criteria. CMD's output goes through a temp file, so the copy lands before the next line the block prints.
exec 9>&1
guard() {
  local out rc
  [ -n "${LOAM_HOOK:-}" ] && [ "${1:-}" = bin/check ] && return 0
  { [ /dev/fd/1 -ef /dev/fd/9 ] || ! out=$(mktemp 2> /dev/null); } && { "$@"; return; }
  "$@" > "$out"
  rc=$?
  cat "$out"
  grep -a '^SKIPPED:' "$out" >&9
  rm -f "$out"
  return "$rc"
}
# predict NAME CMD...: CMD exits 0 exactly when base shows the failure check NAME predicts (CONTRACT.md, Done checks).
# round_zero runs CMD itself, and checks.sh carries no predict line; this no-op serves a block that sources lib.sh.
predict() { return 0; }

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
