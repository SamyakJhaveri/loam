#!/usr/bin/env bash
# test_bootstrap_warns_on_differing_base.sh
# Group 8 warning (lead REVISED ruling + advisor note): bootstrap STILL records a
# base for a differing-content path (M1's cmp is messaging-only, it never gates
# the record), and prints one loud warning naming every differing path it based.
# The warning fires on BOTH the fresh compute_base record AND the C1 dead-base
# re-record. A converged path is based and NOT named.
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HUB_SETUP/skills/conv" "$HUB_SETUP/skills/drift" "$HUB_SETUP/skills/dead"
echo "same content"  > "$HUB_SETUP/skills/conv/S.md"
echo "hub version"   > "$HUB_SETUP/skills/drift/S.md"
echo "hub dead"      > "$HUB_SETUP/skills/dead/S.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/conv" "$TMP/proj/.claude/skills/drift" "$TMP/proj/.claude/skills/dead"
echo "same content"    > "$TMP/proj/.claude/skills/conv/S.md"
echo "project version" > "$TMP/proj/.claude/skills/drift/S.md"
echo "project dead"    > "$TMP/proj/.claude/skills/dead/S.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

STATE="$TMP/hub/.sync-state"
# skills/dead has a well-formed but ABSENT base sha, forcing the C1 re-record path.
BOGUS="deaddeaddeaddeaddeaddeaddeaddeaddeaddead"
{
  echo "session=1"
  echo "base:skills/dead/S.md:$BOGUS"
} > "$STATE"

cd "$TMP/proj"
set +e
out=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: bootstrap exit $rc"; echo "$out"; exit 1; fi

# Assertion 1: the differing paths are STILL based (M1 never gates on content).
for rel in skills/drift/S.md skills/dead/S.md skills/conv/S.md; do
  want=$(git hash-object "$TMP/proj/.claude/$rel")
  if ! grep -qE "^base:[^$T]*${T}$rel:$want\$" "$STATE"; then
    echo "FAIL: differing/converged path $rel was not based to the project sha"; cat "$STATE"; exit 1
  fi
done

# Assertion 2: the dead base was re-recorded (C1), not left stale.
if grep -q "$BOGUS" "$STATE"; then
  echo "FAIL: the dead base sha was not re-recorded"; cat "$STATE"; exit 1
fi

# Assertion 3 (the RED->GREEN flip): a loud warning names BOTH differing paths
# it based - the fresh-record one AND the C1 re-record one.
if ! echo "$out" | grep -q "differs: skills/drift/S.md"; then
  echo "FAIL: warning did not name the fresh-record differing path"; echo "$out"; exit 1
fi
if ! echo "$out" | grep -q "differs: skills/dead/S.md"; then
  echo "FAIL: warning did not name the C1 re-record differing path"; echo "$out"; exit 1
fi

# Assertion 4: the converged path is based but NOT named in the warning.
if echo "$out" | grep -q "differs: skills/conv/S.md"; then
  echo "FAIL: warning falsely named a converged path"; echo "$out"; exit 1
fi

# Assertion 5: the summary line is byte-identical in form (3 recorded, 0 present).
if ! echo "$out" | grep -q "bootstrap: 3 bases recorded, 0 already present"; then
  echo "FAIL: summary line changed"; echo "$out"; exit 1
fi

echo "PASS: test_bootstrap_warns_on_differing_base"
