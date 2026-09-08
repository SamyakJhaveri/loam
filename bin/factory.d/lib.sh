#!/usr/bin/env bash
# bin/factory.d/lib.sh - the prelude a ticket's done-checks block is sourced after.
# Source it; do not run it. The block is run from the worktree root.
set -uo pipefail

n_pass=0
n_fail=0

pass() { echo "PASS $1"; n_pass=$((n_pass + 1)); }
fail() { echo "FAIL $1: $2"; n_fail=$((n_fail + 1)); }
guard() { "$@"; }   # a regression guard: runs CMD and returns its status; allowed to pass on main
