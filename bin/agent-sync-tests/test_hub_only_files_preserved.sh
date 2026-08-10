#!/usr/bin/env bash
# test_hub_only_files_preserved.sh
# Verifies sync.sh leaves hub-only files untouched (no deletion path).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

# Hub has foo + gone (curated set). Project has foo (matches) + bar (new).
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo" \
         "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/gone"
echo "foo content" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md"
echo "gone content" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/gone/SKILL.md"
(cd "$TMP/hub" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/foo" "$TMP/proj/.claude/skills/bar"
echo "foo content" > "$TMP/proj/.claude/skills/foo/SKILL.md"
echo "bar content" > "$TMP/proj/.claude/skills/bar/SKILL.md"
(cd "$TMP/proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Sync — approve bar, decline commit
cd "$TMP/proj"
set +e
output=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

# Assertion 1: exit 0
if [ "$rc" -ne 0 ]; then
  echo "FAIL: exit $rc"; echo "output: $output"; exit 1
fi

# Assertion 2: hub-only 'gone' file still present
if [ ! -f "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/gone/SKILL.md" ]; then
  echo "FAIL: hub-only gone/SKILL.md was removed despite additive-only sync"
  echo "output: $output"
  exit 1
fi

# Assertion 3: bar got synced (positive control)
if [ ! -f "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md" ]; then
  echo "FAIL: project's bar/SKILL.md not synced"
  echo "output: $output"
  exit 1
fi

# Assertion 4: no deletion prompt in output
if echo "$output" | grep -qi 'delete .* from hub\|would be deleted'; then
  echo "FAIL: output contains a deletion prompt — sync should not offer to delete hub files"
  echo "output: $output"
  exit 1
fi

echo "PASS: test_hub_only_files_preserved"
