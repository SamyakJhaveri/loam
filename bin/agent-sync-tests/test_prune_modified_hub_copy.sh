#!/usr/bin/env bash
# test_prune_modified_hub_copy.sh
# H5 (modified tracked copy): a retired hub file that is tracked but has UNSTAGED
# local edits (a state the hub-dirty warning lets the user continue into) must be
# REFUSED-AND-WARNED on an approved prune - not crash the run with git rm's
# "has local modifications" under set -e, and NOT force-removed (git rm -f would
# let a declined commit's rollback checkout-HEAD destroy the local WIP, reopening
# the decline-path data loss group 3 closed). The file and its record are kept and
# the prune re-offers until the user resolves the hub WIP.
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
echo "orig" > "$HUB_SETUP/$GONE"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)
# Give the tracked retired file an UNSTAGED local modification.
echo "LOCAL WIP EDIT" >> "$HUB_SETUP/$GONE"

# Project: lacks gone.md; manifest marks skills/x travels so the fold-in offers it.
mkdir -p "$TMP/proj/.claude/reference"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

{ echo "session=3"; echo "synced:$GONE:1"; } > "$TMP/hub/.sync-state"

cd "$TMP/proj"

# stdin: y = continue past the hub-dirty warning, y = approve the prune. Nothing
# reaches the hub (the modified copy is refused), so the commit prompt is never
# reached ("nothing to commit" exit).
set +e
out=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion rc (RED): no crash. Pre-fix plain git rm exits 1 "has local
# modifications" and set -e aborts the run.
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc (git rm crash on modified copy?)"; echo "$out"; exit 1; fi

# Assertion 1 (RED): the git-rm "local modifications" failure never surfaced.
if echo "$out" | grep -qiF "local modifications"; then
  echo "FAIL: git rm hit the modified copy (not refused before rm)"; echo "$out"; exit 1
fi

# Assertion 2 (RED): a warning names the skipped path and its local edits.
if ! echo "$out" | grep -qF "$GONE" || ! echo "$out" | grep -qiE "local edit|has local"; then
  echo "FAIL: no refuse-and-warn message for the modified copy"; echo "$out"; exit 1
fi

# Assertion 3: the file is KEPT (not removed - refuse, no force).
if [ ! -e "$HUB_SETUP/$GONE" ]; then
  echo "FAIL: modified retired copy was removed (force-rm?) - WIP would be at risk"; echo "$out"; exit 1
fi
if ! git -C "$TMP/hub" cat-file -e "HEAD:$REL_PFX/$GONE" 2>/dev/null; then
  echo "FAIL: modified retired copy no longer tracked at HEAD"; exit 1
fi
# The local WIP edit is intact (nothing touched it).
if ! grep -qF "LOCAL WIP EDIT" "$HUB_SETUP/$GONE"; then
  echo "FAIL: the local WIP edit was lost"; cat "$HUB_SETUP/$GONE"; exit 1
fi

# Assertion 4: the ledger record survives (so the prune re-offers next run).
if ! grep -qE "synced:[^$T]*${T}$GONE" "$TMP/hub/.sync-state"; then
  echo "FAIL: record for $GONE was dropped despite the refusal"; cat "$TMP/hub/.sync-state"; exit 1
fi

# Assertion 5: the hub index is clean (nothing staged - no wedge).
if [ -n "$(git -C "$TMP/hub" diff --cached --name-only)" ]; then
  echo "FAIL: hub index has staged changes after a refused prune (wedge)"; exit 1
fi

echo "PASS: test_prune_modified_hub_copy"
