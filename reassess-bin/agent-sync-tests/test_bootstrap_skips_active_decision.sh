#!/usr/bin/env bash
# test_bootstrap_skips_active_decision.sh
# M1 (group 8, decision-check ONLY): --bootstrap-bases must NOT record a base
# for a path carrying an active synced:/defer: decision - recording one cancels
# the decision (the next scan sees project==base and suppresses the offer
# forever). Bootstrap skips + warns per-path, leaves NO base, and the decision
# record survives. Two arms: a defer: path (the finding's named repro) and a
# synced: path (the synced-cancellation half the lead named explicitly).
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
DREL="skills/deferred/S.md"   # under an active defer
SREL="skills/synced/S.md"     # under an active synced
mkdir -p "$HUB_SETUP/skills/deferred" "$HUB_SETUP/skills/synced"
echo "hub deferred" > "$HUB_SETUP/$DREL"
echo "hub synced"   > "$HUB_SETUP/$SREL"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/deferred" "$TMP/proj/.claude/skills/synced"
echo "project deferred" > "$TMP/proj/.claude/$DREL"
echo "project synced"   > "$TMP/proj/.claude/$SREL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

STATE="$TMP/hub/.sync-state"
# Seed an EXPIRED defer (ask_at=2; the scan at session 4 would re-offer it) and a
# synced record. Both are the user's decision state that bootstrap must not cancel.
{
  echo "session=3"
  echo "defer:$DREL:2"
  echo "synced:$SREL:2"
} > "$STATE"

cd "$TMP/proj"
set +e
bout=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
brc=$?
set -e
if [ "$brc" -ne 0 ]; then echo "FAIL: bootstrap exit $brc"; echo "$bout"; exit 1; fi

# --- defer arm ---------------------------------------------------------------
# Assertion 1 (RED->GREEN flip): NO base recorded for the deferred path.
if grep -qE "^base:[^$T]*${T}$DREL:" "$STATE"; then
  echo "FAIL: bootstrap recorded a base for a path under an active defer (cancels it)"; cat "$STATE"; exit 1
fi
# Assertion 2: bootstrap announced the skip naming the defer reason.
if ! echo "$bout" | grep -q "bootstrap skipped ($DREL: an active defer decision"; then
  echo "FAIL: no defer skip message"; echo "$bout"; exit 1
fi
# Assertion 3: the defer record survived intact.
if ! grep -qE "^defer:[^$T]*${T}$DREL:2\$" "$STATE"; then
  echo "FAIL: the defer record was lost or altered by bootstrap"; cat "$STATE"; exit 1
fi

# --- synced arm --------------------------------------------------------------
# Assertion 4 (RED->GREEN flip): NO base recorded for the synced path.
if grep -qE "^base:[^$T]*${T}$SREL:" "$STATE"; then
  echo "FAIL: bootstrap recorded a base for a path under an active synced decision"; cat "$STATE"; exit 1
fi
# Assertion 5: bootstrap announced the skip naming the synced reason.
if ! echo "$bout" | grep -q "bootstrap skipped ($SREL: an active synced decision"; then
  echo "FAIL: no synced skip message"; echo "$bout"; exit 1
fi
# Assertion 6: the synced record survived intact.
if ! grep -qE "^synced:[^$T]*${T}$SREL:2\$" "$STATE"; then
  echo "FAIL: the synced record was lost or altered by bootstrap"; cat "$STATE"; exit 1
fi

# --- the defer is not permanently cancelled ----------------------------------
# Assertion 7: a follow-up scan re-offers the (expired) deferred change - with no
# base recorded there is nothing to suppress it.
set +e
sout=$(printf '\n\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
src=$?
set -e
if [ "$src" -ne 0 ]; then echo "FAIL: follow-up scan exit $src"; echo "$sout"; exit 1; fi
if ! echo "$sout" | grep -q "Update $DREL to hub?"; then
  echo "FAIL: follow-up scan did not re-offer the deferred change"; echo "$sout"; exit 1
fi

echo "PASS: test_bootstrap_skips_active_decision"
