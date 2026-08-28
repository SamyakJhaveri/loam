#!/usr/bin/env bash
# test_merge_ratchet.sh
# The ratchet fix: a hub-only generalization and an unrelated project edit both
# survive a sync when a three-way merge base is recorded. The point of Wave 1.
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/foo/SKILL.md"

# Base ancestor (four lines so a line-1 and a last-line edit never collide).
BASE="$TMP/base.txt"
printf 'alpha\nbeta\ngamma\ndelta\n' > "$BASE"

# Hub copy = base + a hub-only generalization on line 1.
mkdir -p "$HUB_SETUP/skills/foo"
printf 'alpha GENERALIZED\nbeta\ngamma\ndelta\n' > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project copy = base + an unrelated project edit on the last line. Marked +x so
# the merged result must arrive executable (H3: the merged temp's mode is set
# from the project file via stat before install_file's cp -p - GNU stat -c must
# run before BSD stat -f, else the mode is a multi-line dump and chmod no-ops).
mkdir -p "$TMP/proj/.claude/skills/foo"
printf 'alpha\nbeta\ngamma\ndelta PROJECTEDIT\n' > "$TMP/proj/.claude/$REL"
chmod 755 "$TMP/proj/.claude/$REL"
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

# Run scan: y = accept the merge, then commit (EOF defaults commit=Y, push=N).
# H2 group 3: a declined commit now rolls the merge back, so the merged content
# and the advanced base: land only after a commit - this run commits.
set +e
output=$(printf 'y\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

HUB_FILE="$HUB_SETUP/$REL"

# Assertion rc: the scan succeeded.
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "output: $output"; exit 1; fi

# Assertion 0: the clean-merge path was taken (not legacy overwrite, not conflict).
if ! echo "$output" | grep -q 'clean three-way merge'; then
  echo "FAIL: clean three-way merge header not shown"
  echo "rc=$rc"; echo "output: $output"; exit 1
fi

# Assertion 1: the hub copy is EXACTLY the expected merge - the hub-only
# generalization on line 1 and the project edit on the last line, in order,
# nothing duplicated or reordered (a token grep would miss such corruption; a
# conflict marker would also fail this compare).
EXPECT="$TMP/expected.txt"
printf 'alpha GENERALIZED\nbeta\ngamma\ndelta PROJECTEDIT\n' > "$EXPECT"
if ! cmp -s "$EXPECT" "$HUB_FILE"; then
  echo "FAIL: hub copy is not the exact expected merge"
  echo "--- expected ---"; cat "$EXPECT"; echo "--- got ---"; cat "$HUB_FILE"; exit 1
fi

# Assertion 2 (+x leg, H3): the merged result carries the project file's +x bit.
# On macOS (BSD stat) both stat orders yield the mode, so this stays green; it
# locks the GNU-stat-first ordering for Linux CI, where the wrong order no-ops
# the chmod and the merged file would land 0600.
if [ ! -x "$HUB_FILE" ]; then
  echo "FAIL: merged hub copy lost the project's executable bit"
  ls -l "$HUB_FILE"; exit 1
fi

# Assertion 3: a fresh base: line records the project content as the new base.
EXPECT_SHA=$(git hash-object "$TMP/proj/.claude/$REL")
if ! grep -qE "^base:[^$T]*${T}$REL:$EXPECT_SHA\$" "$TMP/hub/.sync-state"; then
  echo "FAIL: .sync-state missing fresh base line for project content ($EXPECT_SHA)"
  echo "state file:"; cat "$TMP/hub/.sync-state"; exit 1
fi

echo "PASS: test_merge_ratchet"
