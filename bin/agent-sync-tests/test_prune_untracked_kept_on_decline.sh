#!/usr/bin/env bash
# test_prune_untracked_kept_on_decline.sh
# R2(i) amendment (lead, 2026-08-24): an untracked-hub-copy prune is a state-only
# reconciliation (an untracked rm stages nothing, so it can never reach a commit).
# In a batch that ALSO carries a committable add, declining the commit must:
#   - roll back the add (group 3 rollback), AND
#   - KEEP the untracked cleanup (file removed, stale record cleared), because
#     there is no committed content to roll back for it, AND
#   - say so in the decline message.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL_PFX="cultivation/marketplace/sam-cc-setup"
UNTRACKED="skills/x/gone.md"     # untracked hub copy -> state-only prune
ADD="skills/y/new.md"            # committable add -> rolled back on decline
STATE="$TMP/hub/.sync-state"

# Hub: keep.md committed; git identity.
mkdir -p "$HUB_SETUP/skills/x"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)
# Plant an UNTRACKED retired file (present on disk, never committed).
echo "gonebody" > "$HUB_SETUP/$UNTRACKED"

# Project: has the add source, lacks gone.md. Manifest: both dirs travel.
mkdir -p "$TMP/proj/.claude/skills/y" "$TMP/proj/.claude/reference"
echo "newbody" > "$TMP/proj/.claude/$ADD"
printf 'skills/x\t-\ttravels\nskills/y\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

{ echo "session=3"; echo "synced:$UNTRACKED:1"; } > "$STATE"

cd "$TMP/proj"

# stdin: y = continue past the hub-dirty warning (the untracked file makes the
# tree dirty), y = approve the add, y = approve the untracked prune, n = DECLINE
# the commit. (Add prompt precedes the prune fold-in prompt.)
set +e
out=$(printf 'y\ny\ny\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# Assertion 1: the add was rolled back (not installed, not committed).
if [ -e "$HUB_SETUP/$ADD" ]; then
  echo "FAIL: declined add was not rolled back (still on disk)"; echo "$out"; exit 1
fi
if git -C "$TMP/hub" cat-file -e "HEAD:$REL_PFX/$ADD" 2>/dev/null; then
  echo "FAIL: declined add reached HEAD"; exit 1
fi

# Assertion 2 (the amendment): the untracked cleanup was KEPT despite the decline.
if [ -e "$HUB_SETUP/$UNTRACKED" ]; then
  echo "FAIL: untracked cleanup not applied/kept - file still present after the declined batch"; echo "$out"; exit 1
fi
if grep -qF "$UNTRACKED" "$STATE"; then
  echo "FAIL: untracked stale record survived (cleanup not kept)"; cat "$STATE"; exit 1
fi

# Assertion 3: the decline message states the untracked cleanup was kept.
if ! echo "$out" | grep -qiE "kept|removed"; then
  echo "FAIL: decline message did not report the kept untracked cleanup"; echo "$out"; exit 1
fi
# And it still reports the rollback of the committable part.
if ! echo "$out" | grep -qiF "restored"; then
  echo "FAIL: decline message did not report the hub rollback"; echo "$out"; exit 1
fi

# Assertion 4: the hub index is clean (no wedge).
if [ -n "$(git -C "$TMP/hub" diff --cached --name-only)" ]; then
  echo "FAIL: hub index dirty after decline (wedge)"; git -C "$TMP/hub" diff --cached --name-only; exit 1
fi

echo "PASS: test_prune_untracked_kept_on_decline"
