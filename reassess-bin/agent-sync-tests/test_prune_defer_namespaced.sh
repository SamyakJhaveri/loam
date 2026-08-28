#!/usr/bin/env bash
# test_prune_defer_namespaced.sh
# M2: the prune prompt's d (default) overwrites synced:N with defer:ask_at in the
# single decision slot. A base-less synced record then loses its only route into
# prune candidacy (enumeration walks synced:* and base: records), so the promised
# re-ask after the defer expires never happens - the retired file lingers forever.
# Prune decisions must be namespaced (prune-defer:) so the synced: slot survives.
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

mkdir -p "$TMP/proj/.claude/reference"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# gone.md is synced with NO base: record (base-less) -> its only candidacy route
# is the synced:* enumeration.
{ echo "session=3"; echo "synced:$GONE:1"; } > "$TMP/hub/.sync-state"

cd "$TMP/proj"

# Run 1 (session 4): prune offers gone.md; answer d = defer (SAM_CC_DEFER_SESSIONS=1
# -> ask_at = 5).
set +e
out1=$(printf 'd\n' | SAM_CC_HUB_REPO="$TMP/hub" SAM_CC_DEFER_SESSIONS=1 bash "$SYNC_SH" 2>&1)
rc1=$?
set -e
if [ "$rc1" -ne 0 ]; then echo "FAIL: run 1 exit $rc1"; echo "$out1"; exit 1; fi
if ! echo "$out1" | grep -qF "Delete $GONE from hub?"; then
  echo "FAIL: run 1 did not offer the prune"; echo "$out1"; exit 1
fi

# Run 2 (session 5): the defer has expired (ask_at 5), so the prune must be
# re-offered. Pre-fix the synced: slot was overwritten by defer: and the base-less
# path drops out of both enumeration routes, so it is never re-offered.
set +e
out2=$(printf 'd\n' | SAM_CC_HUB_REPO="$TMP/hub" SAM_CC_DEFER_SESSIONS=1 bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: run 2 exit $rc2"; echo "$out2"; exit 1; fi
if ! echo "$out2" | grep -qF "Delete $GONE from hub?"; then
  echo "FAIL: the prune was NOT re-offered after the defer expired (base-less record lost)"; echo "$out2"; exit 1
fi

echo "PASS: test_prune_defer_namespaced"
