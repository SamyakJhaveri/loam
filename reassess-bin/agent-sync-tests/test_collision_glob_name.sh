#!/usr/bin/env bash
# test_collision_glob_name.sh
# CI-p1 Codex High: the collision exclude must be a LITERAL rsync filter. A hub
# directory at `skills/g[1].md` colliding with a project file must not exclude the
# unrelated sibling `skills/g1.md` from the walk, and neither rsync flavor may see
# the collision (no dry-run exit 23).
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

mkdir -p "$HUB_SETUP/skills/g[1].md"
echo inner > "$HUB_SETUP/skills/g[1].md/inner.txt"
echo seed  > "$HUB_SETUP/seed.md"
(cd "$TMP/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills"
echo "collision file" > "$TMP/proj/.claude/skills/g[1].md"
echo "sibling file"   > "$TMP/proj/.claude/skills/g1.md"
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
set +e
out=$(printf 'n\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if echo "$out" | grep -qF "rsync dry-run failed"; then
  echo "FAIL: rsync saw the collision (exclude not literal enough)"; echo "$out"; exit 1; fi
if ! echo "$out" | grep -qF "Add skills/g1.md"; then
  echo "FAIL: sibling g1.md was not offered (over-broad exclude swallowed it)"; echo "$out"; exit 1; fi
if ! echo "$out" | grep -qF "Add skills/g[1].md"; then
  echo "FAIL: the collision file itself was not offered"; echo "$out"; exit 1; fi
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc after two 'n' answers"; echo "$out"; exit 1; fi
echo "PASS: test_collision_glob_name"
