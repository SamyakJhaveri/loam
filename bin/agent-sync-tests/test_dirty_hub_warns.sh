#!/usr/bin/env bash
# test_dirty_hub_warns.sh
# Verifies sync.sh warns and aborts (default-no) when hub has uncommitted changes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

# Build ephemeral hub with a clean .claude-equivalent then dirty it
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo"
cd "$TMP/hub" && git init -q
echo "hub skill v1" > cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md
git add -A && git -c user.email=t@t -c user.name=t commit -q -m init
echo "WIP not yet committed" > wip.txt   # dirty hub working tree
cd - >/dev/null

# Build ephemeral project — clean
mkdir -p "$TMP/proj/.claude/skills/bar"
cd "$TMP/proj" && git init -q
echo "project skill" > .claude/skills/bar/SKILL.md
git add -A && git -c user.email=t@t -c user.name=t commit -q -m init

# Invoke sync.sh with empty stdin (default-no should abort)
set +e
output=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" </dev/null 2>&1)
rc=$?
set -e

# Assertion 1: prompt text mentions hub dirty AND continuation
if ! echo "$output" | grep -qi 'Hub has uncommitted'; then
  echo "FAIL: output missing 'Hub has uncommitted' warning"
  echo "output was: $output"
  exit 1
fi
if ! echo "$output" | grep -qi 'Continue'; then
  echo "FAIL: output missing 'Continue' prompt"
  echo "output was: $output"
  exit 1
fi

# Assertion 2: default-no aborts → non-zero exit
if [ "$rc" -eq 0 ]; then
  echo "FAIL: sync.sh exit 0 (default-no should abort with non-zero)"
  exit 1
fi

# Assertion 3: hub working tree still has only the WIP it started with — project's bar skill NOT propagated
if [ -e "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md" ]; then
  echo "FAIL: project's bar skill leaked into hub despite default-no"
  exit 1
fi

echo "PASS: test_dirty_hub_warns"
