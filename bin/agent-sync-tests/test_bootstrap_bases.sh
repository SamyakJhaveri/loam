#!/usr/bin/env bash
# test_bootstrap_bases.sh
# --bootstrap-bases records a base for every path present in BOTH project and
# hub, using the PROJECT blob sha, without prompting, copying, editing any file
# but .sync-state, or bumping the session counter. It is idempotent.
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

# Two shared paths (one identical, one differing), one hub-only, one project-only.
mkdir -p "$HUB_SETUP/skills/same" "$HUB_SETUP/skills/diff" "$HUB_SETUP/skills/hubonly"
echo "shared identical" > "$HUB_SETUP/skills/same/SKILL.md"
echo "hub version"      > "$HUB_SETUP/skills/diff/SKILL.md"
echo "hub only"         > "$HUB_SETUP/skills/hubonly/SKILL.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/same" "$TMP/proj/.claude/skills/diff" "$TMP/proj/.claude/skills/projonly"
echo "shared identical" > "$TMP/proj/.claude/skills/same/SKILL.md"
echo "project version"  > "$TMP/proj/.claude/skills/diff/SKILL.md"
echo "project only"     > "$TMP/proj/.claude/skills/projonly/SKILL.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Pre-seed a session counter so "unchanged" is testable.
echo "session=5" > "$TMP/hub/.sync-state"

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"

# First run.
set +e
out1=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1)
rc1=$?
set -e

if [ "$rc1" -ne 0 ]; then echo "FAIL: bootstrap exit $rc1"; echo "$out1"; exit 1; fi

nbase=$(grep -c '^base:' "$STATE" || true)
if [ "$nbase" -ne 2 ]; then echo "FAIL: expected 2 base lines, got $nbase"; cat "$STATE"; exit 1; fi

for rel in skills/same/SKILL.md skills/diff/SKILL.md; do
  want=$(git hash-object "$TMP/proj/.claude/$rel")
  if ! grep -qE "^base:[^$T]*${T}$rel:$want\$" "$STATE"; then
    echo "FAIL: base for $rel not project sha $want"; cat "$STATE"; exit 1
  fi
done

if grep -qE "^base:[^$T]*${T}skills/(hubonly|projonly)/" "$STATE"; then
  echo "FAIL: a non-shared path got a base"; cat "$STATE"; exit 1
fi

if echo "$out1" | grep -q 'to hub?'; then echo "FAIL: bootstrap emitted a sync prompt"; echo "$out1"; exit 1; fi

if ! grep -qE "^session:[^$T]*${T}5\$" "$STATE"; then echo "FAIL: session counter changed"; cat "$STATE"; exit 1; fi

dirty=$(git -C "$TMP/hub" status --porcelain | grep -v -E ' \.sync-state$' || true)
if [ -n "$dirty" ]; then echo "FAIL: hub tree dirty beyond .sync-state:"; echo "$dirty"; exit 1; fi

if ! echo "$out1" | grep -q 'bootstrap: 2 bases recorded, 0 already present'; then
  echo "FAIL: wrong first-run report: $out1"; exit 1
fi

# Second run: idempotent.
set +e
out2=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: 2nd bootstrap exit $rc2"; echo "$out2"; exit 1; fi
nbase2=$(grep -c '^base:' "$STATE" || true)
if [ "$nbase2" -ne 2 ]; then echo "FAIL: 2nd run base count $nbase2 != 2"; cat "$STATE"; exit 1; fi
if ! echo "$out2" | grep -q 'bootstrap: 0 bases recorded, 2 already present'; then
  echo "FAIL: 2nd-run report not idempotent: $out2"; exit 1
fi

echo "PASS: test_bootstrap_bases"
