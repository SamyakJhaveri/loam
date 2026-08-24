#!/usr/bin/env bash
# test_defer_expires.sh
# Verifies that after the defer threshold (default 4 sessions), the file is
# re-prompted on the next sync run.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Hub
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo"
echo "foo" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
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

# Run 1: defer bar with SAM_CC_DEFER_SESSIONS=2 (so 2 sessions later, ask again)
set +e
printf '\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" SAM_CC_DEFER_SESSIONS=2 \
  bash "$SYNC_SH" >/dev/null 2>&1
set -e
# Confirm state recorded with ask_again=3 (current session 1 + 2 = 3)
if ! grep -qE '^defer:skills/bar/SKILL.md:3$' "$TMP/hub/.sync-state"; then
  echo "FAIL (Run 1): defer entry missing or wrong threshold"
  echo "state file:"; cat "$TMP/hub/.sync-state"
  exit 1
fi

# Run 2: still under threshold (session 2). bar should NOT prompt.
set +e
output2=$(printf 'n\n' | SAM_CC_HUB_REPO="$TMP/hub" SAM_CC_DEFER_SESSIONS=2 \
  bash "$SYNC_SH" 2>&1)
set -e
if echo "$output2" | grep -q 'Add skills/bar/SKILL.md to hub'; then
  echo "FAIL (Run 2): bar prompted at session 2 (still under threshold)"
  exit 1
fi

# Run 3: session 3 — defer expired. bar SHOULD prompt; user says y and commits
# (EOF defaults commit=Y, push=N). H2 group 3: the approved add lands post-commit.
set +e
output3=$(printf 'y\n' | SAM_CC_HUB_REPO="$TMP/hub" SAM_CC_DEFER_SESSIONS=2 \
  bash "$SYNC_SH" 2>&1)
set -e
if ! echo "$output3" | grep -q 'Add skills/bar/SKILL.md to hub'; then
  echo "FAIL (Run 3): bar NOT prompted at session 3 (defer should have expired)"
  echo "output: $output3"
  echo "state file:"; cat "$TMP/hub/.sync-state"
  exit 1
fi
# bar should now be synced
if [ ! -f "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md" ]; then
  echo "FAIL (Run 3): bar not synced despite y answer at expiration"
  exit 1
fi

echo "PASS: test_defer_expires"
