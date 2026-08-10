#!/usr/bin/env bash
# test_excluded_files_skipped.sh
# Verifies sync.sh excludes audit.log + settings.local.json from sync.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

# Hub: foo committed
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo"
echo "foo" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md"
(cd "$TMP/hub" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: foo (matches), bar (new), audit.log (excluded), settings.local.json (excluded)
mkdir -p "$TMP/proj/.claude/skills/foo" "$TMP/proj/.claude/skills/bar"
echo "foo" > "$TMP/proj/.claude/skills/foo/SKILL.md"
echo "bar" > "$TMP/proj/.claude/skills/bar/SKILL.md"
echo "secret bash log" > "$TMP/proj/.claude/audit.log"
echo "{\"local\":\"settings\"}" > "$TMP/proj/.claude/settings.local.json"
(cd "$TMP/proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Sync — approve bar, decline commit
cd "$TMP/proj"
set +e
output=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

if [ "$rc" -ne 0 ]; then
  echo "FAIL: exit $rc"; echo "output: $output"; exit 1
fi

# Assertion 1: bar synced (positive control)
if [ ! -f "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md" ]; then
  echo "FAIL: bar not synced"; exit 1
fi

# Assertion 2: audit.log NOT in hub
if [ -e "$TMP/hub/cultivation/marketplace/sam-cc-setup/audit.log" ]; then
  echo "FAIL: audit.log leaked into hub despite exclusion"; exit 1
fi

# Assertion 3: settings.local.json NOT in hub
if [ -e "$TMP/hub/cultivation/marketplace/sam-cc-setup/settings.local.json" ]; then
  echo "FAIL: settings.local.json leaked into hub despite exclusion"; exit 1
fi

# Assertion 4: output never mentions excluded files
if echo "$output" | grep -q 'audit.log'; then
  echo "FAIL: output mentions audit.log (excluded — should not appear in any prompt or summary)"
  echo "output: $output"
  exit 1
fi
if echo "$output" | grep -q 'settings.local.json'; then
  echo "FAIL: output mentions settings.local.json"; exit 1
fi

echo "PASS: test_excluded_files_skipped"
