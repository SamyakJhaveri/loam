#!/usr/bin/env bash
# test_never_persists.sh
# Verifies that "never" suppresses prompts forever (until state cleared).
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Hub
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo"
echo "foo" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project
mkdir -p "$TMP/proj/.claude/skills/foo" "$TMP/proj/.claude/skills/bar"
echo "foo" > "$TMP/proj/.claude/skills/foo/SKILL.md"
echo "bar" > "$TMP/proj/.claude/skills/bar/SKILL.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"

# Run 1: user says "n" (never)
set +e
printf 'n\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" >/dev/null 2>&1
set -e
if ! grep -qE "^never:[^$T]*${T}skills/bar/SKILL.md\$" "$TMP/hub/.sync-state"; then
  echo "FAIL (Run 1): never entry missing"
  echo "state file:"; cat "$TMP/hub/.sync-state"
  exit 1
fi

# Run 2 + Run 3 + Run 4: bar should never re-prompt
for i in 2 3 4; do
  set +e
  output=$(printf 'n\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
  set -e
  if echo "$output" | grep -q 'Add skills/bar/SKILL.md to hub'; then
    echo "FAIL (Run $i): bar prompted despite never decision"
    exit 1
  fi
done

# bar should never have been synced
if [ -f "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md" ]; then
  echo "FAIL: bar synced despite never"
  exit 1
fi

echo "PASS: test_never_persists"
