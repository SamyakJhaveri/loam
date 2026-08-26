#!/usr/bin/env bash
# test_decline_rolls_back_sync.sh
# H2 (sync side): the ledger ratchets before the commit decision - synced:/base:
# are written at install, and the EXIT trap persists them, so declining the
# commit (and the rsync-vs-worktree compare) silently swallows the approved sync:
# next scan sees project==worktree, offers nothing, and the ledger claims synced.
# A declined commit must ROLL BACK the hub to its pre-scan state and leave the
# ledger byte-identical, so the next scan re-offers the add.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
ADD="skills/x/new.md"

# Hub: a committed placeholder + git identity (no add ever commits here in run 1).
mkdir -p "$HUB_SETUP"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)

# Project: one new file under a 'travels' row.
mkdir -p "$TMP/proj/.claude/skills/x" "$TMP/proj/.claude/reference"
echo "brand new" > "$TMP/proj/.claude/$ADD"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"

# Run 1: approve the add (y), DECLINE the commit (n).
set +e
out1=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc1=$?
set -e

if [ "$rc1" -ne 0 ]; then echo "FAIL: run 1 exit $rc1"; echo "$out1"; exit 1; fi

# Assertion 1 (RED): no synced: record was written for the declined add.
if grep -q "synced:$ADD" "$STATE" 2>/dev/null; then
  echo "FAIL: declined add left a synced: record in the ledger"; cat "$STATE"; exit 1
fi

# Assertion 2 (RED): the installed hub file was rolled back (removed).
if [ -e "$HUB_SETUP/$ADD" ]; then
  echo "FAIL: declined add left the installed file in the hub (no rollback)"; exit 1
fi

# Assertion 3: the hub index is clean (no staged residue -> next scan not wedged).
if [ -n "$(git -C "$TMP/hub" diff --cached --name-only)" ]; then
  echo "FAIL: hub index has staged residue after decline"; git -C "$TMP/hub" diff --cached --name-only; exit 1
fi

# Assertion 4: the decline names the rollback.
if ! echo "$out1" | grep -qiF "restored"; then
  echo "FAIL: decline message did not report the rollback"; echo "$out1"; exit 1
fi

# Run 2 (RED, the swallow): the add must be re-offered, proving nothing was lost.
set +e
out2=$(printf 'd\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: run 2 exit $rc2"; echo "$out2"; exit 1; fi
if ! echo "$out2" | grep -qF "Add $ADD to hub?"; then
  echo "FAIL: the add was NOT re-offered on the next scan (silently swallowed)"; echo "$out2"; exit 1
fi

echo "PASS: test_decline_rolls_back_sync"
