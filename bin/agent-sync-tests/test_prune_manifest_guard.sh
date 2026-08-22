#!/usr/bin/env bash
# test_prune_manifest_guard.sh
# Codex High H2: a folded prune must carry an explicit 'travels' manifest verdict.
# A retired hub file whose verdict is stays/rework/unclassified - or ANY file when
# there is no manifest at all - must never be offered for deletion; only a
# 'travels' file is. Fail closed, matching bin/agent-sync-prune.sh.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

STAYS="skills/staysdir/SKILL.md"
REWORK="skills/reworkdir/SKILL.md"
NOROW="skills/norowdir/SKILL.md"
TRAVELS="skills/travelsdir/SKILL.md"

# Hub: four retired files (project source gone for all), all previously synced.
for rel in "$STAYS" "$REWORK" "$NOROW" "$TRAVELS"; do
  mkdir -p "$HUB_SETUP/$(dirname "$rel")"
  echo "hub $rel" > "$HUB_SETUP/$rel"
done
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: a committed manifest classifying three of the four; norow has no row.
mkdir -p "$TMP/proj/.claude/reference"
MAN="$TMP/proj/.claude/reference/portability-manifest.tsv"
printf 'skills/staysdir\t-\tstays\nskills/reworkdir\t-\trework\nskills/travelsdir\t-\ttravels\n' > "$MAN"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# All four were synced in a prior session; project source is gone for all.
{
  echo "session=1"
  echo "synced:$STAYS:1"
  echo "synced:$REWORK:1"
  echo "synced:$NOROW:1"
  echo "synced:$TRAVELS:1"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"

# --- Leg 1: manifest present. Only the travels file may be offered. ---
set +e
out=$(printf 'n\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: leg1 scan exit $rc"; echo "$out"; exit 1; fi

for rel in "$STAYS" "$REWORK" "$NOROW"; do
  if echo "$out" | grep -q "Delete $rel from hub?"; then
    echo "FAIL: non-travels file offered for deletion: $rel"; echo "$out"; exit 1
  fi
done
if ! echo "$out" | grep -q "Delete $TRAVELS from hub?"; then
  echo "FAIL: travels file was not offered for deletion"; echo "$out"; exit 1
fi
for rel in "$STAYS" "$REWORK" "$NOROW" "$TRAVELS"; do
  if [ ! -f "$HUB_SETUP/$rel" ]; then
    echo "FAIL: hub copy vanished in leg1: $rel"; echo "$out"; exit 1
  fi
done

# --- Leg 2: no manifest at all. Every file is withheld (fail closed). ---
rm -f "$MAN"
(cd "$TMP/proj" && git -c user.email=t@t -c user.name=t commit -q -am "drop manifest")
set +e
out2=$(printf 'n\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: leg2 scan exit $rc2"; echo "$out2"; exit 1; fi
for rel in "$STAYS" "$REWORK" "$NOROW" "$TRAVELS"; do
  if echo "$out2" | grep -q "Delete $rel from hub?"; then
    echo "FAIL: a file was offered with no manifest present: $rel"; echo "$out2"; exit 1
  fi
  if [ ! -f "$HUB_SETUP/$rel" ]; then
    echo "FAIL: hub copy vanished in leg2: $rel"; echo "$out2"; exit 1
  fi
done

echo "PASS: test_prune_manifest_guard"
