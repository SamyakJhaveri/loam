#!/usr/bin/env bash
# test_ledger_isolation.sh
# M3 (group 11): a decision recorded by project A must not suppress project B's
# sync of the SAME relative path. Two-step (per critic): A scans and answers 'n'
# (records a never: for skills/x/S.md), THEN B scans the same path.
#   RED (current shared-slot engine): A's never: is path-keyed, so B is SUPPRESSED.
#   GREEN (per-project engine): A's never: is A-scoped, so B is OFFERED.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/x/S.md"
mkdir -p "$HUB_SETUP"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && git config core.fileMode true && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
echo "session=1" > "$TMP/hub/.sync-state"

# Project A: has skills/x/S.md; scans and answers n -> records a never: for it.
mkdir -p "$TMP/projA/.claude/skills/x"
echo "A content" > "$TMP/projA/.claude/$REL"
(cd "$TMP/projA" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
( cd "$TMP/projA" && printf 'n\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" >/dev/null 2>&1 ) || true

# Sanity: A recorded a never: for the path (in whatever format the engine uses).
if ! grep -q "never:.*$REL" "$TMP/hub/.sync-state"; then
  echo "FIXTURE BUG: project A did not record a never: for $REL"; cat "$TMP/hub/.sync-state"; exit 1
fi

# Project B: a DIFFERENT project with the same relative path.
mkdir -p "$TMP/projB/.claude/skills/x"
echo "B content" > "$TMP/projB/.claude/$REL"
(cd "$TMP/projB" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
set +e
outB=$(cd "$TMP/projB" && printf 'd\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rcB=$?
set -e
if [ "$rcB" -ne 0 ]; then echo "FAIL: project B scan exit $rcB"; echo "$outB"; exit 1; fi

# Assertion (RED->GREEN flip): B must be OFFERED the add (A's never: is A-scoped).
if ! echo "$outB" | grep -q "Add $REL to hub?"; then
  echo "FAIL: project B was NOT offered $REL - project A's decision suppressed it (M3 shared slot)"; echo "$outB"; exit 1
fi
if echo "$outB" | grep -q "0 new files to ask about"; then
  echo "FAIL: project B saw 0 new files - A's decision cross-contaminated B"; echo "$outB"; exit 1
fi

# Session-isolation arm (M3): per-project counters. A scanned once (its counter is
# 2 = seeded 1 + 1); B scanned once from no prior (its counter is 1). Both must be
# present as INDEPENDENT per-project session lines - a shared counter would leave a
# single line. This also proves B's run cannot expire A's defer window: B never
# advances A's counter.
TAB=$(printf '\t')
A_ID=$(git -C "$TMP/projA" rev-parse --show-toplevel)
B_ID=$(git -C "$TMP/projB" rev-parse --show-toplevel)
STATE="$TMP/hub/.sync-state"
if ! grep -qF "session:$A_ID${TAB}2" "$STATE"; then
  echo "FAIL: project A's session counter (2) was altered by project B's run (per-project session broken)"; cat "$STATE"; exit 1
fi
if ! grep -qF "session:$B_ID${TAB}1" "$STATE"; then
  echo "FAIL: project B did not get its own independent session counter"; cat "$STATE"; exit 1
fi
# A's never: decision survived B's run verbatim (retained, never adopted).
if ! grep -qF "never:$A_ID${TAB}$REL" "$STATE"; then
  echo "FAIL: project A's never: record was dropped or adopted by project B"; cat "$STATE"; exit 1
fi

echo "PASS: test_ledger_isolation"
