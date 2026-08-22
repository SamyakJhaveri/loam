#!/usr/bin/env bash
# test_merge_error_skips.sh
# An operational git merge-file failure (exit 255, e.g. an unreadable hub copy)
# must be reported as a "Merge error ...; skipped" and NOT treated as a content
# conflict offering a destructive overwrite. Codex High 2.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'chmod -R u+rwx "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/foo/SKILL.md"

BASE="$TMP/base.txt"
printf 'base\n' > "$BASE"

mkdir -p "$HUB_SETUP/skills/foo"
printf 'hub\n' > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/foo"
printf 'project\n' > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Valid base blob (project != base, so Critical 1 does not filter it).
BASE_SHA=$(git -C "$TMP/hub" hash-object -w "$BASE")
{ echo "session=1"; echo "base:$REL:$BASE_SHA"; } > "$TMP/hub/.sync-state"

HUB_FILE="$HUB_SETUP/$REL"
# Make the hub copy unreadable so git merge-file fails with exit 255. chmod 000
# also makes git report the hub tree modified, so the scan's hub-dirty guard
# warns first; answer 'y' to continue past it, then reach the merge branch.
chmod 000 "$HUB_FILE"

cd "$TMP/proj"
set +e
out=$(printf 'y\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
chmod 644 "$HUB_FILE"

# Assertion 1: exit 0 (skipped safely, no crash).
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# Assertion 2: reported as a merge error and skipped.
if ! echo "$out" | grep -q "Merge error $REL: git merge-file failed (exit 255); skipped"; then
  echo "FAIL: no 'Merge error ... exit 255 ... skipped' line"; echo "$out"; exit 1
fi

# Assertion 3: NOT treated as a conflict / not offered an overwrite.
if echo "$out" | grep -qE "Conflict $REL|Update $REL to hub\?|Merge $REL to hub\?"; then
  echo "FAIL: an operational error was offered as a conflict/overwrite"; echo "$out"; exit 1
fi

# Assertion 4: hub copy unchanged.
if [ "$(cat "$HUB_FILE")" != "hub" ]; then
  echo "FAIL: hub copy changed on a merge error"; cat "$HUB_FILE"; exit 1
fi

echo "PASS: test_merge_error_skips"
