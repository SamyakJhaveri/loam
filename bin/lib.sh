#!/usr/bin/env bash
# lib.sh — shared helpers for bin/ scripts. Source, don't execute.

# Colored output — set LIB_PREFIX before sourcing to customize.
LIB_PREFIX="${LIB_PREFIX:-loam}"

die()  { printf '%s: %s\n' "$LIB_PREFIX" "$*" >&2; exit 1; }
info() { printf '\033[36m[%s]\033[0m %s\n' "$LIB_PREFIX" "$*"; }
warn() { printf '\033[33m[%s]\033[0m %s\n' "$LIB_PREFIX" "$*"; }
ok()   { printf '\033[32m[%s]\033[0m   %s\n' "$LIB_PREFIX" "$*"; }

# Plain output (verify-template.sh style)
fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "OK: $*"; }

# Extract YAML frontmatter (between first and second --- delimiters).
extract_frontmatter() {
  awk 'BEGIN{n=0} /^---$/{n++; if(n==1){next} if(n==2){exit}} n==1{print}' "$1"
}
