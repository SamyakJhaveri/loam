#!/usr/bin/env bash
# test_commit_failure_rolls_back.sh
# CX-5 (High): a hub `git commit` FAILURE (distinct from a user decline) - e.g. a
# rejecting pre-commit hook - left the approved paths STAGED in the hub index with
# their synced:/base: records never promoted. The next scan then wedges at the C2
# staged-index guard, and a manual commit has no matching ledger records. The fix
# catches the commit failure, runs the same scoped rollback the decline path uses
# (worktree + index for this run's paths), leaves the ledger unpromoted, and exits
# non-zero with recovery guidance.
#   RED (unmodified engine): set -e aborts on the failed commit, leaving the staged
#      add as residue in the index.
#   GREEN: index clean, add rolled back, no synced: record, non-zero exit with
#      guidance; a follow-up scan (hook removed) re-offers and commits cleanly.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
ADD="skills/x/new.md"
CHG="skills/x/exist.md"

# Hub: committed placeholder + a HEAD-present file (the CHANGE leg: rollback must
# checkout HEAD to unstage AND restore it, per the critic's GREEN conditions) +
# a pre-commit hook that REJECTS every commit.
mkdir -p "$HUB_SETUP/skills/x"
echo "keep" > "$HUB_SETUP/keep.md"
echo "hub version" > "$HUB_SETUP/$CHG"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)
echo "session=3" > "$TMP/hub/.sync-state"
HOOK="$TMP/hub/.git/hooks/pre-commit"
printf '#!/bin/sh\necho "pre-commit hook: rejecting" >&2\nexit 1\n' > "$HOOK"
chmod +x "$HOOK"

# Project: one new file (HEAD-absent ADD) + one differing copy of the hub file
# (HEAD-present CHANGE, no base record -> legacy overwrite prompt), both under a
# 'travels' row - a mixed batch, so the failure rollback exercises both classes.
mkdir -p "$TMP/proj/.claude/skills/x" "$TMP/proj/.claude/reference"
echo "brand new" > "$TMP/proj/.claude/$ADD"
echo "project version" > "$TMP/proj/.claude/$CHG"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"

# Run 1: approve the add (y) and the change (y), APPROVE the commit (y) - which
# the hook rejects.
set +e
out1=$(printf 'y\ny\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc1=$?
set -e

# Assertion 1: the scan exits non-zero on the commit failure.
if [ "$rc1" -eq 0 ]; then echo "FAIL: scan exited 0 despite the commit failing"; echo "$out1"; exit 1; fi

# Assertion 2 (RED->GREEN flip): the hub index is CLEAN - no staged residue.
if [ -n "$(git -C "$TMP/hub" diff --cached --name-only)" ]; then
  echo "FAIL: hub index has staged residue after the commit failure (next scan will wedge)"
  git -C "$TMP/hub" diff --cached --name-only; echo "$out1"; exit 1
fi

# Assertion 3: the installed add was rolled back (removed from the worktree).
if [ -e "$HUB_SETUP/$ADD" ]; then
  echo "FAIL: the add was not rolled back after the commit failure"; exit 1
fi

# Assertion 3b (CHANGE leg): the HEAD-present file was restored to its HEAD
# content, proving checkout HEAD unstaged AND restored it.
if [ "$(cat "$HUB_SETUP/$CHG")" != "hub version" ]; then
  echo "FAIL: the change was not restored to HEAD content after the commit failure"
  cat "$HUB_SETUP/$CHG"; exit 1
fi

# Assertion 4: no synced: record was promoted (ledger left unpromoted).
# (group 11 format: synced:<projid>\t<path>:N)
if grep -Eq "^synced:.*[[:space:]]($ADD|$CHG):" "$STATE" 2>/dev/null; then
  echo "FAIL: a synced: record was promoted despite the commit failing"; cat "$STATE"; exit 1
fi

# Assertion 5: recovery guidance surfaced.
if ! echo "$out1" | grep -qiE "commit failed|rolled back"; then
  echo "FAIL: no recovery guidance on the commit failure"; echo "$out1"; exit 1
fi

# Run 2: remove the failing hook; a fresh scan must NOT be wedged (clean index),
# must re-offer both paths, and must commit them cleanly with synced records.
rm -f "$HOOK"
set +e
out2=$(printf 'y\ny\ny\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: run 2 exit $rc2 (wedged?)"; echo "$out2"; exit 1; fi
if echo "$out2" | grep -qi "hub index has staged changes"; then
  echo "FAIL: run 2 wedged at the C2 staged-index guard (residue not cleaned)"; echo "$out2"; exit 1
fi
if ! echo "$out2" | grep -qF "Add $ADD to hub?"; then
  echo "FAIL: run 2 did not re-offer the add (silently lost)"; echo "$out2"; exit 1
fi
if ! grep -Eq "^synced:.*[[:space:]]$ADD:" "$STATE" 2>/dev/null; then
  echo "FAIL: run 2 committed the add but did not promote a synced: record"; cat "$STATE"; exit 1
fi
if ! grep -Eq "^synced:.*[[:space:]]$CHG:" "$STATE" 2>/dev/null; then
  echo "FAIL: run 2 committed the change but did not promote its synced: record"; cat "$STATE"; exit 1
fi
if [ "$(cat "$HUB_SETUP/$CHG")" != "project version" ]; then
  echo "FAIL: run 2 did not deliver the change content"; exit 1
fi

echo "PASS: test_commit_failure_rolls_back"
