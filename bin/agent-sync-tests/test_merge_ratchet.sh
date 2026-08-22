#!/usr/bin/env bash
# test_merge_ratchet.sh
# The ratchet fix: a hub-only generalization and an unrelated project edit both
# survive a sync when a three-way merge base is recorded. The point of Wave 1.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/foo/SKILL.md"

# Base ancestor (four lines so a line-1 and a last-line edit never collide).
BASE="$TMP/base.txt"
printf 'alpha\nbeta\ngamma\ndelta\n' > "$BASE"

# Hub copy = base + a hub-only generalization on line 1.
mkdir -p "$HUB_SETUP/skills/foo"
printf 'alpha GENERALIZED\nbeta\ngamma\ndelta\n' > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project copy = base + an unrelated project edit on the last line.
mkdir -p "$TMP/proj/.claude/skills/foo"
printf 'alpha\nbeta\ngamma\ndelta PROJECTEDIT\n' > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Record the base blob in the hub object store and the base ledger in .sync-state.
BASE_SHA=$(git -C "$TMP/hub" hash-object -w "$BASE")
{
  echo "session=1"
  echo "base:$REL:$BASE_SHA"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"

# Run scan: y = accept the merge, n = do not commit.
set +e
output=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

HUB_FILE="$HUB_SETUP/$REL"

# Assertion 0: the clean-merge path was taken (not legacy overwrite, not conflict).
if ! echo "$output" | grep -q 'clean three-way merge'; then
  echo "FAIL: clean three-way merge header not shown"
  echo "rc=$rc"; echo "output: $output"; exit 1
fi

# Assertion 1: hub copy carries BOTH the generalization and the new project edit.
if ! grep -q 'GENERALIZED' "$HUB_FILE"; then
  echo "FAIL: hub copy lost the hub-only generalization"; cat "$HUB_FILE"; exit 1
fi
if ! grep -q 'PROJECTEDIT' "$HUB_FILE"; then
  echo "FAIL: hub copy did not gain the project edit"; cat "$HUB_FILE"; exit 1
fi

# Assertion 2: no conflict markers in the merged hub copy.
if grep -q '<<<<<<<' "$HUB_FILE"; then
  echo "FAIL: hub copy contains conflict markers"; cat "$HUB_FILE"; exit 1
fi

# Assertion 3: a fresh base: line records the project content as the new base.
EXPECT_SHA=$(git hash-object "$TMP/proj/.claude/$REL")
if ! grep -qE "^base:$REL:$EXPECT_SHA\$" "$TMP/hub/.sync-state"; then
  echo "FAIL: .sync-state missing fresh base line for project content ($EXPECT_SHA)"
  echo "state file:"; cat "$TMP/hub/.sync-state"; exit 1
fi

echo "PASS: test_merge_ratchet"
