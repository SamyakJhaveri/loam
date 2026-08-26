#!/usr/bin/env bash
# test_state_file_shape.sh
# Codex p5 Critical (item 5): a .sync-state that is a DIRECTORY or a SYMLINK (to a
# directory) is not a valid ledger. The old write_state did `mv -f "$tmp"
# "$STATE_FILE"`, which moves the temp INTO a directory target (or through a
# symlink-to-dir) and returns 0 - leaving no readable ledger yet letting a commit
# proceed, and (for a symlink) writing OUTSIDE the hub. The scan must refuse both
# shapes and exit 1, writing nothing outside and committing nothing.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mk_pair() {  # $1=root: a hub + project already in sync (one shared file, no diff)
  local root="$1" hs="$1/hub/cultivation/marketplace/sam-cc-setup"
  mkdir -p "$hs/skills/keep"; echo keep > "$hs/skills/keep/SKILL.md"
  (cd "$root/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
  mkdir -p "$root/proj/.claude/skills/keep"; echo keep > "$root/proj/.claude/skills/keep/SKILL.md"
  (cd "$root/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
}

# ---- Leg A: .sync-state is a DIRECTORY ----
A="$TMP/A"; mk_pair "$A"
mkdir "$A/hub/.sync-state"   # a directory where the ledger should be a regular file
HEAD_A=$(git -C "$A/hub" rev-parse HEAD)
cd "$A/proj"
set +e; outA=$(printf 'n\n' | SAM_CC_HUB_REPO="$A/hub" bash "$SYNC_SH" 2>&1); rcA=$?; set -e
if [ "$rcA" -ne 1 ]; then echo "FAIL(A): expected exit 1, got $rcA"; echo "$outA"; exit 1; fi
if ! echo "$outA" | grep -qF "not a regular file"; then echo "FAIL(A): no shape Error"; echo "$outA"; exit 1; fi
if [ -n "$(find "$A/hub/.sync-state" -type f 2>/dev/null)" ]; then
  echo "FAIL(A): a temp ledger was moved into the .sync-state directory"; find "$A/hub/.sync-state"; exit 1; fi
if [ "$(git -C "$A/hub" rev-parse HEAD)" != "$HEAD_A" ]; then echo "FAIL(A): hub HEAD advanced"; exit 1; fi

# ---- Leg B: .sync-state is a SYMLINK to an outside directory ----
B="$TMP/B"; mk_pair "$B"
mkdir -p "$TMP/outsideB"
ln -s "$TMP/outsideB" "$B/hub/.sync-state"   # symlink -> external directory
HEAD_B=$(git -C "$B/hub" rev-parse HEAD)
cd "$B/proj"
set +e; outB=$(printf 'n\n' | SAM_CC_HUB_REPO="$B/hub" bash "$SYNC_SH" 2>&1); rcB=$?; set -e
if [ "$rcB" -ne 1 ]; then echo "FAIL(B): expected exit 1, got $rcB"; echo "$outB"; exit 1; fi
if ! echo "$outB" | grep -qF "not a regular file"; then echo "FAIL(B): no shape Error"; echo "$outB"; exit 1; fi
if [ -n "$(find "$TMP/outsideB" -type f 2>/dev/null)" ]; then
  echo "FAIL(B): a temp ledger was written into the outside directory via the symlink"; find "$TMP/outsideB"; exit 1; fi
if [ "$(git -C "$B/hub" rev-parse HEAD)" != "$HEAD_B" ]; then echo "FAIL(B): hub HEAD advanced"; exit 1; fi

echo "PASS: test_state_file_shape"
