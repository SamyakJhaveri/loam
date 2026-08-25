#!/usr/bin/env bash
# test_decline_rolls_back_prune.sh
# H2 (prune side): the prune git rm stages a deletion and drops the ledger record
# before the commit decision, so declining leaves the deletion staged (next scan
# wedges on the C2 staged-index guard) with the record already gone (the restored
# file becomes a permanent orphan the fold-in can never offer again). A declined
# commit must ROLL BACK the deletion (restore the file, clean index) and keep the
# ledger record, so the next scan re-offers the prune.
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL_PFX="cultivation/marketplace/sam-cc-setup"
GONE="skills/x/gone.md"

# Hub: a committed retired file + placeholder, git identity.
mkdir -p "$HUB_SETUP/skills/x"
echo "keep" > "$HUB_SETUP/keep.md"
echo "gone" > "$HUB_SETUP/$GONE"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)

# Project: lacks gone.md; a manifest marks skills/x 'travels' so the fold-in
# offers the retired file for deletion.
mkdir -p "$TMP/proj/.claude/reference"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# gone.md was synced in a prior session -> a prune candidate this run.
{
  echo "session=3"
  echo "synced:$GONE:1"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"

# Run 1: approve the prune (y), DECLINE the commit (n).
set +e
out1=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc1=$?
set -e

if [ "$rc1" -ne 0 ]; then echo "FAIL: run 1 exit $rc1"; echo "$out1"; exit 1; fi

# Assertion 1 (RED): the deletion was rolled back - gone.md is present and tracked.
if [ ! -e "$HUB_SETUP/$GONE" ]; then
  echo "FAIL: declined prune left the hub file deleted (no rollback)"; exit 1
fi
if ! git -C "$TMP/hub" cat-file -e "HEAD:$REL_PFX/$GONE" 2>/dev/null; then
  echo "FAIL: gone.md no longer tracked at HEAD after decline"; exit 1
fi

# Assertion 2 (RED): the hub index is clean (no staged deletion -> next scan not wedged).
if [ -n "$(git -C "$TMP/hub" diff --cached --name-only)" ]; then
  echo "FAIL: hub index has a staged deletion after decline (wedge)"; git -C "$TMP/hub" diff --cached --name-only; exit 1
fi

# Assertion 3 (RED): the ledger record survives (not erased before the commit).
if ! grep -qE "synced:[^$T]*${T}$GONE" "$STATE" 2>/dev/null; then
  echo "FAIL: declined prune erased the ledger record (orphan)"; cat "$STATE"; exit 1
fi

# Assertion 4: the decline names the rollback.
if ! echo "$out1" | grep -qiF "restored"; then
  echo "FAIL: decline message did not report the rollback"; echo "$out1"; exit 1
fi

# Run 2 (RED, the orphan): the prune must be re-offered, proving nothing was lost.
set +e
out2=$(printf 'd\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: run 2 exit $rc2"; echo "$out2"; exit 1; fi
if ! echo "$out2" | grep -qF "Delete $GONE from hub?"; then
  echo "FAIL: the prune was NOT re-offered on the next scan (orphaned)"; echo "$out2"; exit 1
fi

echo "PASS: test_decline_rolls_back_prune"
