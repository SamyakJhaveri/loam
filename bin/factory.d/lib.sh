#!/usr/bin/env bash
# bin/factory.d/lib.sh - the prelude a ticket's done-checks block is sourced after.
# Source it; do not run it. The block is run from the worktree root.
set -uo pipefail

n_pass=0
n_fail=0

pass() { echo "PASS $1"; n_pass=$((n_pass + 1)); }
fail() { echo "FAIL $1: ${2:-}"; n_fail=$((n_fail + 1)); }
guard() { "$@"; }   # a regression guard: runs CMD and returns its status; allowed to pass on main

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
