#!/bin/sh
# CORE-04 controller: the trusted operator entrypoint for admission and for
# installed diagnostics. It is dependency-free POSIX sh and part of the sealed
# payload.
#
# Trust boundary (SETUP.md): the operator runs this from a plain non-interactive
# terminal. The controller cannot protect its own first startup (native loader
# variables such as LD_PRELOAD or DYLD_INSERT_LIBRARIES, or the shell's own
# startup files); an already compromised parent is out of scope. Everything after
# the first line runs in a clean environment this script establishes.
#
# C1: sanitization is unconditional. Unless already invoked with --clean, the
# controller re-executes itself under `env -i` with a fixed PATH, carrying only
# the six proxy variables through as inert data for the admission bootstrap. The
# internal --clean flag is honored only when the environment is already exactly
# the clean set, so a caller cannot pass --clean to skip sanitization.

set -eu

# --- unconditional re-exec into a clean environment (C1) -------------------
if [ "${1-}" != '--clean' ]; then
  __loam_scratch=$(/usr/bin/mktemp -d "${TMPDIR:-/tmp}/loam-control.XXXXXXXX")
  exec /usr/bin/env -i \
    PATH=/usr/bin:/bin HOME="$__loam_scratch" TMPDIR="$__loam_scratch" LANG=C \
    __LOAM_PROXY_HTTP_PROXY="${HTTP_PROXY-}" \
    __LOAM_PROXY_HTTPS_PROXY="${HTTPS_PROXY-}" \
    __LOAM_PROXY_NO_PROXY="${NO_PROXY-}" \
    __LOAM_PROXY_http_proxy="${http_proxy-}" \
    __LOAM_PROXY_https_proxy="${https_proxy-}" \
    __LOAM_PROXY_no_proxy="${no_proxy-}" \
    /bin/sh "$0" --clean "$@"
fi
shift # remove --clean

# --- output helpers --------------------------------------------------------
json_escape() { printf '%s' "$1" | /usr/bin/sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }
emit_unavailable() {
  printf '{"status":"unavailable","diagnostic":"%s","detail":"%s"}\n' "$1" "$(json_escape "$2")"
  exit 1
}
usage_exit() {
  printf '{"status":"usage","detail":"%s"}\n' "$(json_escape "$1")"
  exit 2
}

# --- verify the clean environment (C1) -------------------------------------
# PATH must be exactly the fixed pair, and no variable outside the allowlist may
# be present. Enumeration is fail-closed: a value carrying a newline can only add
# a spurious name (which is refused), never hide a real one.
[ "$PATH" = '/usr/bin:/bin' ] || usage_exit 'refusing --clean: environment is not sanitized'
set -f
for __name in $(/usr/bin/env | /usr/bin/cut -d= -f1); do
  case "$__name" in
    PATH|HOME|TMPDIR|LANG|PWD|OLDPWD|SHLVL|_|__LOAM_PROXY_*) : ;;
    *) set +f; usage_exit 'refusing --clean: unexpected environment variable present' ;;
  esac
done
set +f

# --- platform helpers ------------------------------------------------------
__os=$(/usr/bin/uname -s)
__arch=$(/usr/bin/uname -m)
case "$__os" in
  Darwin) DIGEST_HASH='/usr/bin/shasum -a 256'; DIGEST_CHECK='/usr/bin/shasum -a 256 -c' ;;
  Linux) DIGEST_HASH='/usr/bin/sha256sum'; DIGEST_CHECK='/usr/bin/sha256sum -c' ;;
  *) usage_exit "unsupported platform: $__os" ;;
esac
case "$__os $__arch" in
  'Darwin arm64') PLATFORM_KEY='darwin-arm64' ;;
  'Linux x86_64') PLATFORM_KEY='linux-x64' ;;
  *) PLATFORM_KEY='' ;;
esac

is_absolute() { case "$1" in /*) return 0 ;; *) return 1 ;; esac; }
is_hex16() {
  [ "${#1}" -eq 16 ] || return 1
  case "$1" in *[!0-9a-f]*) return 1 ;; esac
  return 0
}

# --- selected.json parser (C1: validate the whole serialization) -----------
# The record is written by canonicalJson: sorted keys, two-space indent. Accept
# only that exact five-line shape, reject any trailing or duplicate content, and
# constrain both ids to the 16-hex grammar before use.
extract_snapshot_id() {
  __sel=$1
  [ -f "$__sel" ] || return 1
  [ "$(/usr/bin/grep -c '' "$__sel")" -eq 5 ] || return 1
  [ "$(/usr/bin/sed -n '1p' "$__sel")" = '{' ] || return 1
  /usr/bin/sed -n '2p' "$__sel" | /usr/bin/grep -Eq '^  "admissionId": "[0-9a-f]{16}",$' || return 1
  __id=$(/usr/bin/sed -n '3p' "$__sel" | /usr/bin/sed -n 's/^  "snapshotId": "\([0-9a-f]\{16\}\)",$/\1/p')
  [ -n "$__id" ] || return 1
  /usr/bin/sed -n '4p' "$__sel" | /usr/bin/grep -Eq '^  "version": 1$' || return 1
  [ "$(/usr/bin/sed -n '5p' "$__sel")" = '}' ] || return 1
  printf '%s' "$__id"
}

records_complete() {
  __root=$1; __id=$2
  [ -f "$__root/registry/admissions/$__id.json" ] || return 1
  [ -f "$__root/registry/runtimes/$__id.sha256" ] || return 1
  [ -f "$__root/registry/runtimes/$__id.json" ] || return 1
  return 0
}

# Resolve the control-root state (item 9 table). On any non-dispatch state it
# emits the diagnostic and exits 1. On dispatch it sets SELECTED_ID and returns.
resolve_state() {
  __root=$1
  { [ -n "$__root" ] && [ -d "$__root" ]; } || emit_unavailable control-root-missing "$__root"
  [ ! -e "$__root/registry/admit.lock" ] || emit_unavailable install-interrupted "lock $__root/registry/admit.lock"
  __rt="$__root/runtimes"
  __complete=''
  if [ -d "$__rt" ]; then
    for __e in "$__rt"/.staging-* "$__rt"/.tool-*; do
      [ -e "$__e" ] || continue
      emit_unavailable install-interrupted "staging $__e"
    done
    for __e in "$__rt"/*; do
      [ -e "$__e" ] || continue
      __base=${__e##*/}
      is_hex16 "$__base" || continue
      records_complete "$__root" "$__base" || emit_unavailable install-interrupted "unregistered $__base"
      __complete="$__complete $__base"
    done
  fi
  __sel="$__root/registry/selected.json"
  if [ -e "$__sel" ]; then
    __id=$(extract_snapshot_id "$__sel") || emit_unavailable install-interrupted 'selection'
    case " $__complete " in
      *" $__id "*) SELECTED_ID=$__id; return 0 ;;
      *) emit_unavailable install-interrupted 'selection' ;;
    esac
  fi
  if [ -n "$__complete" ]; then
    set -f; set -- $__complete; set +f
    emit_unavailable install-interrupted "unselected $1"
  fi
  emit_unavailable nothing-admitted 'no runtime has been admitted'
}

# Pre-dispatch integrity check (item 8): verify the recorded entrypoint set with
# the host digest tool, from the snapshot directory, before any snapshot code
# runs. The .sha256 file lists only relative paths inside the snapshot.
predispatch_check() {
  __root=$1; __id=$2
  __snap="$__root/runtimes/$__id"
  __sums="$__root/registry/runtimes/$__id.sha256"
  [ -f "$__sums" ] || emit_unavailable installed-file-altered "$__sums"
  ( cd "$__snap" && $DIGEST_CHECK "$__sums" ) >/dev/null 2>&1 || emit_unavailable installed-file-altered "$__snap"
}

# --- global flag parsing ---------------------------------------------------
TOOLCHAIN=''
CONTROL_ROOT=''
VERB=''
while [ $# -gt 0 ]; do
  case "$1" in
    --toolchain) [ $# -ge 2 ] || usage_exit 'missing value for --toolchain'; TOOLCHAIN=$2; shift 2 ;;
    --control-root) [ $# -ge 2 ] || usage_exit 'missing value for --control-root'; CONTROL_ROOT=$2; shift 2 ;;
    admit|status|doctor) VERB=$1; shift; break ;;
    --clean) usage_exit 'unexpected --clean' ;;
    *) usage_exit "unexpected argument: $1" ;;
  esac
done
[ -n "$VERB" ] || usage_exit 'missing verb'
# A present-but-relative control root is a usage error; an absent one is reported
# as control-root-missing by resolve_state (status/doctor) or below (admit).
if [ -n "$CONTROL_ROOT" ]; then is_absolute "$CONTROL_ROOT" || usage_exit '--control-root must be an absolute path'; fi

# --- admit -----------------------------------------------------------------
if [ "$VERB" = 'admit' ]; then
  is_absolute "$CONTROL_ROOT" || usage_exit 'admit requires an absolute --control-root'
  is_absolute "$TOOLCHAIN" || usage_exit 'admit requires an absolute --toolchain'
  TRUSTED=''
  RELEASE_IDENTITY=''
  set -- "$@" '__loam_end__'
  while [ "$1" != '__loam_end__' ]; do
    case "$1" in
      --trusted-source) [ $# -ge 2 ] || usage_exit 'missing value for --trusted-source'; TRUSTED=$2; shift 2 ;;
      --release-identity) [ $# -ge 2 ] || usage_exit 'missing value for --release-identity'; RELEASE_IDENTITY=$2; shift 2 ;;
      --protect-registry) usage_exit '--protect-registry is not allowed' ;;
      --protect-state|--protect-locks|--protect-credentials|--protect-sockets|--protect-callbacks)
        [ $# -ge 2 ] || usage_exit "missing value for $1"
        __flag=$1; __val=$2; shift 2; set -- "$@" "$__flag" "$__val" ;;
      *) usage_exit "unexpected admit argument: $1" ;;
    esac
  done
  shift # remove __loam_end__; remaining "$@" are the protect flags
  is_absolute "$TRUSTED" || usage_exit '--trusted-source must be an absolute path'
  { [ "${#RELEASE_IDENTITY}" -ge 1 ] && [ "${#RELEASE_IDENTITY}" -le 120 ]; } || usage_exit '--release-identity must be 1-120 characters'

  # Trusted-source shape guard (item 3): admit.js re-checks it authoritatively.
  __real=$(cd "$TRUSTED" 2>/dev/null && pwd -P) || emit_unavailable trusted-source-shape "$TRUSTED"
  case "$__real" in
    */seed/.loam/factory) : ;;
    *) emit_unavailable trusted-source-shape "$__real" ;;
  esac
  __repo=${__real%/seed/.loam/factory}
  for __sentinel in copier.yml VERSION bin/release.sh; do
    [ -e "$__repo/$__sentinel" ] || emit_unavailable trusted-source-shape "$__repo missing $__sentinel"
  done

  # Verify the toolchain node bytes against the trusted manifest BEFORE running
  # it (C1/R2). The manifest entry is a single fixed line.
  [ -n "$PLATFORM_KEY" ] || emit_unavailable runtime-digest-mismatch "$__os $__arch"
  __manifest="$__real/assets/runtime-manifest.json"
  [ -f "$__manifest" ] || emit_unavailable runtime-digest-mismatch "$__manifest"
  __expected=$(/usr/bin/grep -o "\"$PLATFORM_KEY\": { \"nodeSha256\": \"[0-9a-f]\{64\}\" }" "$__manifest" | /usr/bin/sed -n 's/.*"nodeSha256": "\([0-9a-f]\{64\}\)".*/\1/p')
  [ -n "$__expected" ] || emit_unavailable runtime-digest-mismatch "$__manifest has no $PLATFORM_KEY digest"
  [ -f "$TOOLCHAIN/bin/node" ] || emit_unavailable runtime-digest-mismatch "$TOOLCHAIN/bin/node"
  __actual=$($DIGEST_HASH "$TOOLCHAIN/bin/node" | /usr/bin/cut -d' ' -f1)
  [ "$__actual" = "$__expected" ] || emit_unavailable runtime-digest-mismatch "$TOOLCHAIN/bin/node"

  # Dispatch admit.js under a fresh clean environment. Proxy carriers are passed
  # through as data, only here; admit.ts drops the empty ones. Node's own JSON
  # output and exit code pass through.
  exec /usr/bin/env -i \
    HOME="$HOME" PATH="$TOOLCHAIN/bin" TMPDIR="$TMPDIR" LANG=C \
    HTTP_PROXY="$__LOAM_PROXY_HTTP_PROXY" HTTPS_PROXY="$__LOAM_PROXY_HTTPS_PROXY" NO_PROXY="$__LOAM_PROXY_NO_PROXY" \
    http_proxy="$__LOAM_PROXY_http_proxy" https_proxy="$__LOAM_PROXY_https_proxy" no_proxy="$__LOAM_PROXY_no_proxy" \
    "$TOOLCHAIN/bin/node" --no-global-search-paths "$__real/dist/src/installation/admit.js" \
    --trusted-source "$__real" --control-root "$CONTROL_ROOT" --toolchain "$TOOLCHAIN" --release-identity "$RELEASE_IDENTITY" "$@"
fi

# --- status / doctor -------------------------------------------------------
MODE=''
CHECKOUT=''
case "$VERB" in
  status) MODE='status'; [ $# -eq 0 ] || usage_exit 'status takes no further arguments' ;;
  doctor)
    MODE='doctor'
    if [ $# -gt 0 ]; then
      [ "$1" = '--checkout' ] && [ $# -eq 2 ] || usage_exit 'doctor accepts only --checkout <dir>'
      CHECKOUT=$2
      is_absolute "$CHECKOUT" || usage_exit '--checkout must be an absolute path'
    fi ;;
esac

SELECTED_ID=''
resolve_state "$CONTROL_ROOT"
predispatch_check "$CONTROL_ROOT" "$SELECTED_ID"
__snap="$CONTROL_ROOT/runtimes/$SELECTED_ID"
if [ -n "$CHECKOUT" ]; then
  exec /usr/bin/env -i HOME="$HOME" PATH="$__snap/bin" TMPDIR="$TMPDIR" LANG=C \
    "$__snap/bin/node" --no-global-search-paths "$__snap/payload/dist/src/commands/doctor.js" \
    --mode "$MODE" --control-root "$CONTROL_ROOT" --checkout "$CHECKOUT"
fi
exec /usr/bin/env -i HOME="$HOME" PATH="$__snap/bin" TMPDIR="$TMPDIR" LANG=C \
  "$__snap/bin/node" --no-global-search-paths "$__snap/payload/dist/src/commands/doctor.js" \
  --mode "$MODE" --control-root "$CONTROL_ROOT"
