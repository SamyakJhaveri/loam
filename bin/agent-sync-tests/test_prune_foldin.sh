#!/usr/bin/env bash
# test_prune_foldin.sh
# Hub files whose project source is gone are offered for deletion by the same
# scan (prune fold-in), for BOTH a synced: record and a base:-only record. On y
# each is git-rm'd (staged deletion) and its ledger record dropped.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
GONE="skills/gone/SKILL.md"     # carries a synced: record
BONLY="skills/bonly/SKILL.md"   # carries a base: record only

# Hub: two retired files (gone, bonly) plus a shared unchanged file (keep).
mkdir -p "$HUB_SETUP/skills/gone" "$HUB_SETUP/skills/bonly"
echo "keep"  > "$HUB_SETUP/keep.md"
echo "gone"  > "$HUB_SETUP/$GONE"
echo "bonly" > "$HUB_SETUP/$BONLY"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: has keep (identical, no change), lacks gone and bonly. A manifest
# marks both retired paths 'travels' so the folded prune (H2) still offers them.
mkdir -p "$TMP/proj/.claude/reference"
echo "keep" > "$TMP/proj/.claude/keep.md"
printf 'skills/gone\t-\ttravels\nskills/bonly\t-\ttravels\n' \
  > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# gone was synced in a prior session; bonly has a base: record only.
BONLY_SHA=$(printf 'bonly\n' | git -C "$TMP/hub" hash-object -w --stdin)
{
  echo "session=1"
  echo "synced:$GONE:1"
  echo "base:$BONLY:$BONLY_SHA"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"

# Run scan: y = delete each candidate, then commit (EOF defaults commit=Y,
# push=N). H2 group 3: a declined commit now rolls the prune back, so the
# deletions land only after a commit - this run commits.
set +e
output=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion rc: the scan succeeded.
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "output: $output"; exit 1; fi

# Assertion 1: both deletions were offered (synced: and base:-only candidates).
for rel in "$GONE" "$BONLY"; do
  if ! echo "$output" | grep -q "Delete $rel from hub?"; then
    echo "FAIL: no Delete prompt for $rel"; echo "output: $output"; exit 1
  fi
done

# Assertion 2: both hub files are gone, committed as deletions (absent from HEAD),
# records dropped (the pending prune-unset is applied after the commit succeeds).
for rel in "$GONE" "$BONLY"; do
  if [ -f "$HUB_SETUP/$rel" ]; then
    echo "FAIL: hub file still present after y: $rel"; echo "output: $output"; exit 1
  fi
  if git -C "$TMP/hub" cat-file -e "HEAD:cultivation/marketplace/sam-cc-setup/$rel" 2>/dev/null; then
    echo "FAIL: deletion not committed in hub (still at HEAD): $rel"; exit 1
  fi
  if grep -q "$rel" "$STATE"; then
    echo "FAIL: record for $rel still in .sync-state"; cat "$STATE"; exit 1
  fi
done

# Assertion 3 (control): the shared unchanged file is untouched.
if [ ! -f "$HUB_SETUP/keep.md" ]; then
  echo "FAIL: keep.md was removed"; exit 1
fi

echo "PASS: test_prune_foldin"
