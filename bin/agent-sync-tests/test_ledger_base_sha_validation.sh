#!/usr/bin/env bash
# test_ledger_base_sha_validation.sh
# L3: a ledger base: sha is never shape-validated. A 7-hex (abbreviated) sha resolves
# via cat-file (so base_blob_present passes) but `git update-index --index-info`
# rejects it, so write_state fails and EVERY run - including a no-change scan - exits
# 1; --bootstrap-bases counts the path "already present" and never re-records, so the
# designated repair fails at the same step.
# Fix: validate 40-hex at parse time (mirror compute_base) and drop a malformed base
# (warn); bootstrap then re-records it via its existing missing-base path.
# GREEN Leg 1: a no-op scan with a 7-hex base exits 0 (unwedged), warns, drops it.
# GREEN Leg 2: --bootstrap-bases re-records a valid 40-hex base for the path.
set -uo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

REL="skills/keep/S.md"

# ---- Leg 1: a no-op scan with a 7-hex base is no longer wedged ----
H1="$TMP/hub1"; HS1="$H1/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HS1/skills/keep"
echo "same body" > "$HS1/$REL"
(cd "$H1" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj1/.claude/skills/keep"
echo "same body" > "$TMP/proj1/.claude/$REL"   # identical -> genuine no-op
(cd "$TMP/proj1" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

# Make a REAL blob in the hub, then abbreviate its sha to 7 hex - it resolves via
# cat-file (base_blob_present true) but is rejected by update-index --index-info.
FULL=$(printf 'a real blob for the abbreviated base\n' | git -C "$H1" hash-object -w --stdin)
SHORT="${FULL:0:7}"
# Fixture sanity: the 7-hex prefix must resolve to a blob (else the RED mechanism is absent).
if [ "$(git -C "$H1" cat-file -t "$SHORT" 2>/dev/null)" != blob ]; then
  echo "FAIL(fixture): 7-hex prefix $SHORT does not resolve to a blob"; exit 1
fi
printf 'session=3\nbase:%s:%s\n' "$REL" "$SHORT" > "$H1/.sync-state"

cd "$TMP/proj1"
set +e
out=$(printf '' | SAM_CC_HUB_REPO="$H1" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

# GREEN: the run is unwedged (exit 0) - pre-fix it exits 1 (write_state rejects the short sha).
if [ "$rc" -ne 0 ]; then
  echo "FAIL(1): no-op scan with a 7-hex base exited $rc (still wedged - L3 not fixed)"
  echo "$out"; exit 1
fi
if ! echo "$out" | grep -q "No changes"; then
  echo "FAIL(1): expected the no-op 'No changes' path"; echo "$out"; exit 1
fi
# The malformed base is dropped (warned), so the rewritten ledger holds no base for REL.
if grep -qE "^base:[^$T]*${T}?$REL:" "$H1/.sync-state"; then
  echo "FAIL(1): malformed 7-hex base was retained instead of dropped"; cat "$H1/.sync-state"; exit 1
fi

# ---- Leg 2: --bootstrap-bases re-records a valid 40-hex base ----
H2="$TMP/hub2"; HS2="$H2/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HS2/skills/keep"
echo "same body" > "$HS2/$REL"
(cd "$H2" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj2/.claude/skills/keep"
echo "same body" > "$TMP/proj2/.claude/$REL"
(cd "$TMP/proj2" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

FULL2=$(printf 'another abbreviated base blob\n' | git -C "$H2" hash-object -w --stdin)
SHORT2="${FULL2:0:7}"
printf 'session=3\nbase:%s:%s\n' "$REL" "$SHORT2" > "$H2/.sync-state"

cd "$TMP/proj2"
set +e
out2=$(SAM_CC_HUB_REPO="$H2" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
rc2=$?
set -e
cd - >/dev/null

if [ "$rc2" -ne 0 ]; then
  echo "FAIL(2): bootstrap exited $rc2 (pre-fix wedges on the 7-hex base)"; echo "$out2"; exit 1
fi
# A fresh, valid 40-hex base for REL was re-recorded (the project content's blob sha).
EXPECT=$(git -C "$H2" hash-object "$TMP/proj2/.claude/$REL")
if ! grep -qE "^base:[^$T]*${T}$REL:$EXPECT\$" "$H2/.sync-state"; then
  echo "FAIL(2): bootstrap did not re-record a valid 40-hex base for $REL"
  echo "expected sha $EXPECT"; cat "$H2/.sync-state"; exit 1
fi

echo "PASS: test_ledger_base_sha_validation"
