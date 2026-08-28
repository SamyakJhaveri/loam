#!/usr/bin/env bash
# test_prune_untracked_hub_copy.sh
# H5 (untracked copy): a retired hub file that is present on disk but UNTRACKED in
# git (e.g. left by an earlier interrupted run), carrying a synced: ledger record,
# must be plain-rm'd on an approved prune AND its ledger record cleaned - not
# "skipped (not tracked)" with the record left behind, which re-offers the same
# Delete prompt every session forever. The next scan must NOT re-offer it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
GONE="skills/x/gone.md"
STATE="$TMP/hub/.sync-state"

# Hub: only keep.md is committed; git identity set.
mkdir -p "$HUB_SETUP/skills/x"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)
# Plant an UNTRACKED retired file (present on disk, never committed).
echo "gonebody" > "$HUB_SETUP/$GONE"

# Project: lacks gone.md; manifest marks skills/x travels.
mkdir -p "$TMP/proj/.claude/reference"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

{ echo "session=3"; echo "synced:$GONE:1"; } > "$STATE"

cd "$TMP/proj"

# Run 1: y = continue past the hub-dirty warning (the untracked file makes the
# tree dirty), y = delete gone.md.
set +e
out1=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc1=$?
set -e
if [ "$rc1" -ne 0 ]; then echo "FAIL: run 1 exit $rc1"; echo "$out1"; exit 1; fi

# Assertion 1 (RED): the untracked file was actually removed (not skipped).
if [ -e "$HUB_SETUP/$GONE" ]; then
  echo "FAIL: untracked retired copy still present after approved prune"; echo "$out1"; exit 1
fi

# Assertion 2 (RED): no "not tracked in hub" skip message; instead a per-rm
# message names the removed untracked path (R2(i) amendment: one message per rm).
if echo "$out1" | grep -qiF "not tracked in hub"; then
  echo "FAIL: prune skipped the untracked copy with no rm fallback"; echo "$out1"; exit 1
fi
if ! echo "$out1" | grep -qF "$GONE" || ! echo "$out1" | grep -qiE "untracked"; then
  echo "FAIL: no per-rm message naming the removed untracked copy"; echo "$out1"; exit 1
fi

# Assertion 3 (RED): the ledger record was cleaned.
if grep -q "$GONE" "$STATE"; then
  echo "FAIL: synced: record for the untracked copy survived (will re-offer forever)"; cat "$STATE"; exit 1
fi

# Run 2 (RED): the prune must NOT be re-offered (record + file both gone).
set +e
out2=$(printf 'd\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: run 2 exit $rc2"; echo "$out2"; exit 1; fi
if echo "$out2" | grep -qF "Delete $GONE from hub?"; then
  echo "FAIL: the untracked prune was re-offered on the next scan (no cleanup)"; echo "$out2"; exit 1
fi

echo "PASS: test_prune_untracked_hub_copy"
