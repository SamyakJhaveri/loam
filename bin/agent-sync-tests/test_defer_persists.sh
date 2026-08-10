#!/usr/bin/env bash
# test_defer_persists.sh
# Verifies that a deferred file is silently skipped on a subsequent sync run
# (no prompt) until the defer threshold expires.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

# Hub: foo committed
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo"
echo "foo" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: foo (matches), bar (new)
mkdir -p "$TMP/proj/.claude/skills/foo" "$TMP/proj/.claude/skills/bar"
echo "foo" > "$TMP/proj/.claude/skills/foo/SKILL.md"
echo "bar" > "$TMP/proj/.claude/skills/bar/SKILL.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"

# Run 1: defer bar (empty input on prompt), decline commit
set +e
output1=$(printf '\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc1=$?
set -e
if [ "$rc1" -ne 0 ]; then
  echo "FAIL (Run 1): exit $rc1"; echo "output: $output1"; exit 1
fi
# Verify bar not synced
if [ -f "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md" ]; then
  echo "FAIL (Run 1): bar synced despite defer"; exit 1
fi
# Verify state file recorded the defer
if [ ! -f "$TMP/hub/.sync-state" ]; then
  echo "FAIL (Run 1): state file $TMP/hub/.sync-state not created"; exit 1
fi
if ! grep -q '^defer:skills/bar/SKILL.md:' "$TMP/hub/.sync-state"; then
  echo "FAIL (Run 1): defer entry missing for skills/bar/SKILL.md"
  echo "state file:"; cat "$TMP/hub/.sync-state"
  exit 1
fi

# Run 2: same diff, deferred file should NOT prompt this run
set +e
output2=$(printf 'n\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then
  echo "FAIL (Run 2): exit $rc2"; echo "output: $output2"; exit 1
fi
# bar should still not be synced
if [ -f "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md" ]; then
  echo "FAIL (Run 2): bar synced unexpectedly"; exit 1
fi
# Output should NOT contain a prompt about bar
if echo "$output2" | grep -q 'Add skills/bar/SKILL.md to hub'; then
  echo "FAIL (Run 2): bar was re-prompted despite active defer"
  echo "output: $output2"
  exit 1
fi

echo "PASS: test_defer_persists"
