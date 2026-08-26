#!/usr/bin/env bash
# test_untracked_dest_refused.sh
# Codex round-2 High (scan.sh drop_dirty_approved): the CX-3 dirty check used only
# `git diff`, which ignores UNTRACKED files - so an existing untracked hub file at
# an approved change path was silently overwritten, and a decline/commit-failure
# rollback then UNLINKED it (absent from HEAD), destroying pre-scan work. The
# filter must refuse an existing untracked destination like any other pre-scan WIP.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
P="skills/x/wip.md"

# Hub: a committed placeholder, plus an UNTRACKED file at the candidate path
# (pre-scan work the user has not committed).
mkdir -p "$HUB_SETUP/skills/x"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)
echo "precious untracked WIP" > "$HUB_SETUP/$P"
echo "session=3" > "$TMP/hub/.sync-state"

# Project: a differing copy of the same path under a travels row -> rsync sees a
# CHANGE (worktree comparison), git sees an untracked destination.
mkdir -p "$TMP/proj/.claude/skills/x" "$TMP/proj/.claude/reference"
echo "project version" > "$TMP/proj/.claude/$P"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"

# Continue past the dirty-hub warning (y), approve the change (y). Bounded input:
# `yes |` would take SIGPIPE (141) under pipefail when the scan exits first.
set +e
out=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# 1 (RED flip): the untracked pre-scan file survives with its content intact.
if [ ! -e "$HUB_SETUP/$P" ] || [ "$(cat "$HUB_SETUP/$P")" != "precious untracked WIP" ]; then
  echo "FAIL: the untracked hub destination was overwritten or destroyed"
  ls -la "$HUB_SETUP/skills/x" || true; echo "$out"; exit 1
fi
# 2: the skip is announced as an untracked-destination refusal.
if ! echo "$out" | grep -qi "UNTRACKED in the hub"; then
  echo "FAIL: no untracked-destination skip message"; echo "$out"; exit 1
fi
# 3: nothing was staged or committed for the path.
if git -C "$TMP/hub" diff --cached --name-only | grep -q "wip.md"; then
  echo "FAIL: the untracked destination was staged"; exit 1
fi
# 4: no synced: record for the refused path.
if grep -Eq "^synced:.*[[:space:]]$P:" "$TMP/hub/.sync-state" 2>/dev/null; then
  echo "FAIL: a synced: record was written for the refused path"; exit 1
fi
# 5: the scan itself did not crash (rc 0: nothing approved survives the filter).
if [ "$rc" -ne 0 ]; then
  echo "FAIL: scan exited $rc"; echo "$out"; exit 1
fi

echo "PASS: test_untracked_dest_refused"
