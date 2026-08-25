#!/usr/bin/env bash
# test_merge_conflict.sh
# A recorded base plus hub and project editing the SAME line differently is a
# true conflict: scan must NOT auto-install, must surface "Conflict", and must
# default to defer, leaving the hub copy untouched.
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/foo/SKILL.md"

# Base ancestor.
BASE="$TMP/base.txt"
printf 'alpha\nbeta\ngamma\n' > "$BASE"

# Hub and project edit the SAME line (line 2) differently -> conflict.
mkdir -p "$HUB_SETUP/skills/foo"
printf 'alpha\nHUBEDIT\ngamma\n' > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/foo"
printf 'alpha\nPROJEDIT\ngamma\n' > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Record the base blob and the base ledger line.
BASE_SHA=$(git -C "$TMP/hub" hash-object -w "$BASE")
{
  echo "session=1"
  echo "base:$REL:$BASE_SHA"
} > "$TMP/hub/.sync-state"

# Snapshot the hub copy to prove it is untouched afterwards.
HUB_FILE="$HUB_SETUP/$REL"
cp "$HUB_FILE" "$TMP/hub_orig"

cd "$TMP/proj"

# Run scan: bare newline = defer. Nothing is approved, so scan exits before the
# commit prompt; one input line suffices.
set +e
output=$(printf '\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion rc: the scan succeeded.
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "output: $output"; exit 1; fi

# Assertion 1: a Conflict was surfaced (not a clean merge, not a bare Update).
if ! echo "$output" | grep -q 'Conflict'; then
  echo "FAIL: no Conflict header in output"
  echo "rc=$rc"; echo "output: $output"; exit 1
fi

# Assertion 1b: the fallback used the legacy overwrite prompt (R3), i.e. the
# "Update <path> to hub" prompt appears and the clean-merge "Merge <path> to hub"
# prompt does not.
if ! echo "$output" | grep -q "Update $REL to hub"; then
  echo "FAIL: conflict did not fall back to the legacy Update prompt"; echo "$output"; exit 1
fi
if echo "$output" | grep -q "Merge $REL to hub"; then
  echo "FAIL: a conflict was offered as a clean Merge"; echo "$output"; exit 1
fi

# Assertion 2: hub copy unchanged byte-for-byte (not auto-installed).
if ! cmp -s "$TMP/hub_orig" "$HUB_FILE"; then
  echo "FAIL: hub copy changed despite defer on a conflict"
  echo "expected:"; cat "$TMP/hub_orig"; echo "got:"; cat "$HUB_FILE"; exit 1
fi

# Assertion 3: a defer decision was recorded for the path.
if ! grep -qE "^defer:[^$T]*${T}$REL:[0-9]+\$" "$TMP/hub/.sync-state"; then
  echo "FAIL: no defer record for $REL"
  echo "state file:"; cat "$TMP/hub/.sync-state"; exit 1
fi

echo "PASS: test_merge_conflict"
