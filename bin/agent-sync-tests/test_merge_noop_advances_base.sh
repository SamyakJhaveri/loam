#!/usr/bin/env bash
# test_merge_noop_advances_base.sh
# A clean three-way merge whose output is byte-identical to the hub copy (the
# project independently made the same edit the hub already had) must NOT be
# offered: the base advances to the project's content, nothing is installed,
# prompted, or committed, and the hub copy is untouched. Codex Critical 2.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/foo/SKILL.md"

# base (ancestor), hub (generalized line1 + changed line5), project (only the
# same line5 change) -> separate hunks, so the merge is clean and merged == hub.
BASE="$TMP/base.txt"
printf 'L1\nL2\nL3\nL4\nL5\n' > "$BASE"

mkdir -p "$HUB_SETUP/skills/foo"
printf 'L1-GEN\nL2\nL3\nL4\nL5-HUBB\n' > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/foo"
printf 'L1\nL2\nL3\nL4\nL5-HUBB\n' > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Record the base blob and the base ledger line.
BASE_SHA=$(git -C "$TMP/hub" hash-object -w "$BASE")
{
  echo "session=1"
  echo "base:$REL:$BASE_SHA"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"
HUB_FILE="$HUB_SETUP/$REL"
HUB_BEFORE="$(cat "$HUB_FILE")"

set +e
out=$(printf '\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion 1: exit 0.
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# Assertion 2: no prompt for the path (a no-op is not offered).
if echo "$out" | grep -qE "Merge $REL|Update $REL|$REL to hub\?"; then
  echo "FAIL: no-op merge was offered"; echo "$out"; exit 1
fi

# Assertion 3: hub copy unchanged.
if [ "$(cat "$HUB_FILE")" != "$HUB_BEFORE" ]; then
  echo "FAIL: hub copy changed on a no-op merge"; cat "$HUB_FILE"; exit 1
fi

# Assertion 4: base advanced to the project content.
WANT=$(git hash-object "$TMP/proj/.claude/$REL")
if ! grep -qE "^base:$REL:$WANT\$" "$TMP/hub/.sync-state"; then
  echo "FAIL: base not advanced to project content ($WANT)"; cat "$TMP/hub/.sync-state"; exit 1
fi

echo "PASS: test_merge_noop_advances_base"
