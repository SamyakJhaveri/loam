#!/usr/bin/env bash
# test_prune_never_namespaced.sh
# M2: prune decisions share the single sync decision slot. Answering 'n' (never
# delete - keep it) at a prune prompt stores never: in STATE_DECISIONS, which
# should_prompt reads as "never offer at all" - so a later project re-add of the
# same path with NEW content is suppressed forever. Prune decisions must be
# namespaced (prune-never:) so they never touch the synced: slot.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
GONE="skills/x/gone.md"

mkdir -p "$HUB_SETUP/skills/x"
echo "keep" > "$HUB_SETUP/keep.md"
echo "old"  > "$HUB_SETUP/$GONE"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)

# Project: initially lacks gone.md; manifest marks skills/x 'travels'.
mkdir -p "$TMP/proj/.claude/reference"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# gone.md was synced in a prior session -> a prune candidate.
{ echo "session=3"; echo "synced:$GONE:1"; } > "$TMP/hub/.sync-state"

cd "$TMP/proj"

# Run 1: prune offers gone.md; answer n = never delete (keep it).
set +e
out1=$(printf 'n\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc1=$?
set -e
if [ "$rc1" -ne 0 ]; then echo "FAIL: run 1 exit $rc1"; echo "$out1"; exit 1; fi
if ! echo "$out1" | grep -qF "Delete $GONE from hub?"; then
  echo "FAIL: run 1 did not offer the prune"; echo "$out1"; exit 1
fi

# The project RE-ADDS gone.md with NEW content.
mkdir -p "$TMP/proj/.claude/skills/x"
echo "brand new content" > "$TMP/proj/.claude/$GONE"
(cd "$TMP/proj" && git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m readd)

# Run 2: the changed gone.md must be OFFERED (not suppressed by a prune 'never').
set +e
out2=$(printf 'd\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: run 2 exit $rc2"; echo "$out2"; exit 1; fi

# The RED: pre-fix the prune 'never' lands in the sync slot and suppresses this.
if ! echo "$out2" | grep -qF "Update $GONE to hub?"; then
  echo "FAIL: the re-added gone.md was NOT offered (prune 'never' suppressed the sync slot)"; echo "$out2"; exit 1
fi

echo "PASS: test_prune_never_namespaced"
