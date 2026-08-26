#!/usr/bin/env bash
# test_commit_promotes_ledger.sh
# H2 pending-quarantine, the promotion path: synced:/base: are held in PENDING_*
# during install and written to the ledger ONLY after the hub commit succeeds. A
# committed add must land BOTH a synced: and a base: record; a committed change
# must ADVANCE base: to the new project blob. Guards a broken pending->STATE
# promotion, which would silently lose a record (R5).
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL_PFX="cultivation/marketplace/sam-cc-setup"
ADD="skills/x/new.md"

# Hub: committed placeholder + persistent identity (real commits happen here).
mkdir -p "$HUB_SETUP"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)

# Project: one new file under a 'travels' row.
mkdir -p "$TMP/proj/.claude/skills/x" "$TMP/proj/.claude/reference"
echo "v1" > "$TMP/proj/.claude/$ADD"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"

# Leg 1: approve the add, COMMIT (y), decline push (n).
set +e
out1=$(printf 'y\ny\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc1=$?
set -e
if [ "$rc1" -ne 0 ]; then echo "FAIL: leg 1 exit $rc1"; echo "$out1"; exit 1; fi

# Both records promoted into the ledger after the commit.
if ! grep -qE "^synced:[^$T]*${T}$ADD:" "$STATE"; then echo "FAIL: no synced: record after commit"; cat "$STATE"; exit 1; fi
if ! grep -qE "^base:[^$T]*${T}$ADD:" "$STATE"; then echo "FAIL: no base: record after commit"; cat "$STATE"; exit 1; fi
# The add reached HEAD.
if ! git -C "$TMP/hub" cat-file -e "HEAD:$REL_PFX/$ADD" 2>/dev/null; then
  echo "FAIL: committed add not at HEAD"; exit 1; fi

base1=$(grep -E "^base:[^$T]*${T}$ADD:" "$STATE" | head -1 | sed 's/^base:.*://')

# Leg 2: change the project file, commit it, sync + COMMIT the change.
echo "v2 changed" > "$TMP/proj/.claude/$ADD"
(cd "$TMP/proj" && git -c user.email=t@t -c user.name=t commit -q -am change)
set +e
out2=$(printf 'y\ny\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: leg 2 exit $rc2"; echo "$out2"; exit 1; fi

base2=$(grep -E "^base:[^$T]*${T}$ADD:" "$STATE" | head -1 | sed 's/^base:.*://')
expect=$(git -C "$TMP/hub" hash-object "$TMP/proj/.claude/$ADD")
if [ "$base2" = "$base1" ]; then echo "FAIL: base: did not advance after the committed change"; echo "base1=$base1 base2=$base2"; exit 1; fi
if [ "$base2" != "$expect" ]; then echo "FAIL: base: did not advance to the new project blob"; echo "base2=$base2 expect=$expect"; exit 1; fi

echo "PASS: test_commit_promotes_ledger"
