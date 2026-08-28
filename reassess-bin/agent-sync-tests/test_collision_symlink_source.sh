#!/usr/bin/env bash
# test_collision_symlink_source.sh
# CI-p1 Codex High: a tracked project SYMLINK colliding with a hub directory is
# never offered as an Add (installing would follow the link and promote its
# target's bytes). Expect: loud skip warning, no rsync error, clean exit.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/link.md"

mkdir -p "$HUB_SETUP/$REL"
echo inner > "$HUB_SETUP/$REL/inner.txt"
echo seed  > "$HUB_SETUP/seed.md"
(cd "$TMP/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills"
echo seed > "$TMP/proj/.claude/seed.md"
echo "target outside claude" > "$TMP/proj/target.txt"
ln -s ../../target.txt "$TMP/proj/.claude/$REL"
# Round-2 High: a DANGLING tracked symlink must take the same skip path.
REL2="skills/dangling.md"
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/$REL2"
echo inner2 > "$TMP/hub/cultivation/marketplace/sam-cc-setup/$REL2/inner.txt"
ln -s ./no-such-target "$TMP/proj/.claude/$REL2"
(cd "$TMP/hub" && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m add-rel2)
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"
set +e
out=$(printf '' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi
if [ "$(echo "$out" | grep -cF "project source is a symlink colliding with a hub directory")" -ne 2 ]; then
  echo "FAIL: expected the skip warning for BOTH the live and the dangling symlink"; echo "$out"; exit 1; fi
if echo "$out" | grep -qF "Add $REL"; then
  echo "FAIL: symlink source was offered as an Add"; echo "$out"; exit 1; fi
if echo "$out" | grep -qF "rsync dry-run failed"; then
  echo "FAIL: rsync saw the collision"; echo "$out"; exit 1; fi
if [ -f "$STATE" ] && grep -qF "$REL" "$STATE"; then
  echo "FAIL: ledger mentions the symlink collision path"; cat "$STATE"; exit 1; fi
if [ ! -f "$HUB_SETUP/$REL/inner.txt" ]; then echo "FAIL: hub directory damaged"; exit 1; fi
echo "PASS: test_collision_symlink_source"
