#!/usr/bin/env bash
# test_prune_foldin.sh
# A hub file whose project source is gone, and which carries a synced: record,
# is offered for deletion by the same scan (prune fold-in). On y it is git-rm'd
# (staged deletion) and its ledger record is dropped.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
GONE="skills/gone/SKILL.md"

# Hub: a retired file (gone) plus a shared unchanged file (keep).
mkdir -p "$HUB_SETUP/skills/gone"
echo "keep" > "$HUB_SETUP/keep.md"
echo "gone" > "$HUB_SETUP/$GONE"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: has keep (identical, no change), lacks gone.
mkdir -p "$TMP/proj/.claude"
echo "keep" > "$TMP/proj/.claude/keep.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# gone was synced in a prior session.
{
  echo "session=1"
  echo "synced:$GONE:1"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"
HUB_GONE="$HUB_SETUP/$GONE"

# Run scan: y = delete gone, n = do not commit.
set +e
output=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion 1: the deletion was offered.
if ! echo "$output" | grep -q "Delete $GONE from hub?"; then
  echo "FAIL: no Delete prompt for $GONE"; echo "rc=$rc"; echo "output: $output"; exit 1
fi

# Assertion 2: the hub file is gone.
if [ -f "$HUB_GONE" ]; then
  echo "FAIL: hub file still present after y"; echo "output: $output"; exit 1
fi

# Assertion 3: git shows it staged as deleted (D).
if ! git -C "$TMP/hub" status --porcelain | grep -qE "^D.*$GONE"; then
  echo "FAIL: deletion not staged (D) in hub"
  git -C "$TMP/hub" status --porcelain; exit 1
fi

# Assertion 4: the ledger record was dropped.
if grep -q "$GONE" "$STATE"; then
  echo "FAIL: record for $GONE still in .sync-state"; cat "$STATE"; exit 1
fi

# Assertion 5 (control): the shared unchanged file is untouched.
if [ ! -f "$HUB_SETUP/keep.md" ]; then
  echo "FAIL: keep.md was removed"; exit 1
fi

echo "PASS: test_prune_foldin"
