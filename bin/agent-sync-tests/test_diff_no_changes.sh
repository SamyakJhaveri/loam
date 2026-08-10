#!/usr/bin/env bash
# test_diff_no_changes.sh
# Verifies sync.sh reports "no changes" and makes no commit when project and hub are identical.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

# Build identical content in both project and hub
mkdir -p "$TMP/proj/.claude/skills/foo" "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo"

# Project side
cd "$TMP/proj" && git init -q
echo "shared content" > .claude/skills/foo/SKILL.md
git add -A && git -c user.email=t@t -c user.name=t commit -q -m init
cd - >/dev/null

# Hub side — identical content
cd "$TMP/hub" && git init -q
echo "shared content" > cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md
git add -A && git -c user.email=t@t -c user.name=t commit -q -m init
HUB_HEAD_BEFORE=$(git rev-parse HEAD)
cd - >/dev/null

# Run sync — should report no changes
cd "$TMP/proj"
set +e
output=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" </dev/null 2>&1)
rc=$?
set -e
cd - >/dev/null

# Assertion 1: output mentions "no changes" (case-insensitive)
if ! echo "$output" | grep -qi 'no changes'; then
  echo "FAIL: output missing 'no changes' message"
  echo "output was: $output"
  exit 1
fi

# Assertion 2: exit code 0
if [ "$rc" -ne 0 ]; then
  echo "FAIL: exit $rc, expected 0"
  exit 1
fi

# Assertion 3: hub HEAD unchanged (no commit was made)
HUB_HEAD_AFTER=$(git -C "$TMP/hub" rev-parse HEAD)
if [ "$HUB_HEAD_BEFORE" != "$HUB_HEAD_AFTER" ]; then
  echo "FAIL: hub HEAD changed from $HUB_HEAD_BEFORE to $HUB_HEAD_AFTER (no commit expected)"
  exit 1
fi

echo "PASS: test_diff_no_changes"
