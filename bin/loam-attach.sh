#!/usr/bin/env bash
# loam-attach.sh - attach the Loam Claude harness to an existing directory.
#
# Copies the seed Claude settings and hook scripts into <dir>/.claude/ (foreign
# hooks already in <dir>/.claude/hooks/ are kept), appends the harness .gitignore
# lines, and writes <dir>/.claude/settings.local.json that registers this
# checkout's cultivation/marketplace and enables the sam-cc-setup plugin. Works
# whether or not <dir> is a git repo.
#
# This is the third Loam distribution mechanism, alongside Copier (forward) and
# the plugin marketplace (reverse); see docs/SYNC.md.
#
# Usage:
#   bin/loam-attach.sh <dir>
#   bin/loam-attach.sh <dir> --force   # overwrite the seed-named harness files
#
# Refuses if <dir>/.claude/settings.json exists or <dir>/.claude/hooks/ is a
# directory, unless --force. --force overwrites only the seed-named files
# (settings.json and the seed hook scripts); foreign hooks in
# <dir>/.claude/hooks/ and an existing <dir>/.claude/settings.local.json (a
# plugin marketplace or a Bash(*) grant could live there) are always kept.
#
# The marketplace path baked into settings.local.json is this checkout's
# absolute path. For a lasting attach, run this from the canonical checkout, not
# a throwaway worktree, so the path survives the worktree's teardown.
#
# Exit codes:
#   0  attached
#   1  usage error, missing target, existing harness (settings.json or hooks/)
#      without --force, or missing seed settings

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck disable=SC2034
LIB_PREFIX="loam-attach"
# shellcheck source=bin/lib.sh
. "$ROOT/bin/lib.sh"

usage() {
  cat >&2 <<'USAGE'
usage: bin/loam-attach.sh <dir> [--force]

Attach the Loam Claude harness (settings.json, hooks/, settings.local.json,
.gitignore lines) to an existing directory.

  --force   overwrite the seed-named files (settings.json and the seed hook
            scripts); foreign hooks and an existing settings.local.json stay
USAGE
}

FORCE=0
TARGET=""
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    -h|--help) usage; exit 0 ;;
    -*) usage; die "unknown option: $arg" ;;
    *) [ -z "$TARGET" ] || { usage; die "one target only"; }; TARGET="$arg" ;;
  esac
done
[ -n "$TARGET" ] || { usage; die "missing <dir>"; }
[ -d "$TARGET" ] || die "target is not a directory: $TARGET"

DST="$(cd "$TARGET" && pwd)"
SEED="$ROOT/seed/.claude"
MKT="$ROOT/cultivation/marketplace"
[ -f "$SEED/settings.json" ] || die "seed Claude settings not found: $SEED/settings.json"
[ -d "$SEED/hooks" ] || die "seed Claude hooks not found: $SEED/hooks"
[ -d "$MKT" ] || die "marketplace not found: $MKT"

# Refuse to clobber an existing harness unless --force. Key on the hooks
# directory too, not just settings.json: the hook copy below would overwrite the
# seed-named scripts there.
if { [ -e "$DST/.claude/settings.json" ] || [ -d "$DST/.claude/hooks" ]; } && [ "$FORCE" -eq 0 ]; then
  die "$DST/.claude already has a harness (settings.json or hooks/); re-run with --force to overwrite the seed-named files"
fi

mkdir -p "$DST/.claude"

# settings.json: verbatim copy of the seed file.
cp "$SEED/settings.json" "$DST/.claude/settings.json"

# hooks/: copy the seed hook scripts over the target. Any foreign hook already
# in <dir>/.claude/hooks/ survives; only the seed-named *.sh files are replaced.
mkdir -p "$DST/.claude/hooks"
cp "$SEED/hooks/"*.sh "$DST/.claude/hooks/"
for f in "$SEED/hooks/"*.sh; do
  chmod +x "$DST/.claude/hooks/${f##*/}"
done

# settings.local.json: register this checkout's marketplace and enable the
# plugin. Never overwrite an existing one, even with --force: it can hold a
# marketplace registration or a Bash(*) grant, and JSON carries no marker
# comment to prove this script wrote it.
SLJ="$DST/.claude/settings.local.json"
if [ -e "$SLJ" ]; then
  SLJ_STATUS="left in place (pre-existing, not overwritten)"
  warn "$SLJ already exists; left in place (not overwritten, even with --force)"
else
  python3 - "$SLJ" "$MKT" <<'PY'
import json, sys
out, mkt = sys.argv[1], sys.argv[2]
data = {
    "extraKnownMarketplaces": {
        "seed-skills": {"source": {"source": "directory", "path": mkt}}
    },
    "enabledPlugins": {"sam-cc-setup@seed-skills": True},
}
with open(out, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
PY
  SLJ_STATUS="written"
fi

# .gitignore: append the harness ignore lines once, keyed by a marker line.
GI="$DST/.gitignore"
MARKER="# Loam harness (added by loam-attach.sh)"
if [ -f "$GI" ] && grep -qxF "$MARKER" "$GI"; then
  GI_STATUS="ignore lines already present"
else
  # If the file has content and no trailing newline, start on a fresh line so
  # the marker does not glue onto the last pattern.
  if [ -s "$GI" ] && [ -n "$(tail -c 1 "$GI")" ]; then
    printf '\n' >> "$GI"
  fi
  {
    printf '%s\n' "$MARKER"
    printf '%s\n' \
      ".codex_review_done" \
      ".claude/audit.log" \
      ".claude/worktrees/" \
      ".claude/codex-reviews/" \
      ".claude/settings.local.json" \
      ".validation_passed" \
      ".superpowers/" \
      "/HANDOFF.md" \
      "*.log" \
      "logs/"
  } >> "$GI"
  GI_STATUS="ignore lines appended"
fi

HOOK_COUNT="$(find "$SEED/hooks" -maxdepth 1 -name '*.sh' -type f | wc -l | tr -d ' ')"

ok "attached Loam harness to $DST"
info "settings.json:        copied"
info "hooks/:               $HOOK_COUNT scripts copied"
info "settings.local.json:  $SLJ_STATUS"
info ".gitignore:           $GI_STATUS"
if ! git -C "$DST" rev-parse --git-dir >/dev/null 2>&1; then
  info "note: $DST is not a git repo; hooks that need git stay quiet until 'git init'"
fi
