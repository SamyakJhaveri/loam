#!/usr/bin/env bash
# test_base_missing_blob.sh
# A base: record whose blob was pruned from the hub object store (git gc) must be
# treated as NO base: the changed candidate falls back to the legacy overwrite
# "Update" prompt, never a three-way "Merge". Regression lock on R2/R3.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/foo/SKILL.md"

mkdir -p "$HUB_SETUP/skills/foo"
echo "hub content" > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/foo"
echo "project content different" > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# A base: line whose sha is a valid 40-hex string that is NOT in the object store.
BOGUS="deaddeaddeaddeaddeaddeaddeaddeaddeaddead"
{
  echo "session=1"
  echo "base:$REL:$BOGUS"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"
HUB_FILE="$HUB_SETUP/$REL"

set +e
output=$(printf '\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion 1: exit 0 (graceful fallback, no crash).
if [ "$rc" -ne 0 ]; then
  echo "FAIL: scan exit $rc (missing-blob base should fall back gracefully)"
  echo "output: $output"; exit 1
fi

# Assertion 2: the legacy Update prompt, not a Merge.
if ! echo "$output" | grep -q "Update $REL to hub"; then
  echo "FAIL: no legacy 'Update' prompt for a missing-blob base"
  echo "output: $output"; exit 1
fi
if echo "$output" | grep -qE "Merge $REL|clean three-way merge"; then
  echo "FAIL: took the Merge path despite a missing base blob"
  echo "output: $output"; exit 1
fi

# Assertion 3: hub copy unchanged (defer installed nothing).
if [ "$(cat "$HUB_FILE")" != "hub content" ]; then
  echo "FAIL: hub copy changed on defer"; cat "$HUB_FILE"; exit 1
fi

echo "PASS: test_base_missing_blob"
