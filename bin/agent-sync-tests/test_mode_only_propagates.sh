#!/usr/bin/env bash
# test_mode_only_propagates.sh
# M5 (group 9): a mode-only difference (project hook 755, hub copy 644, identical
# bytes) is currently invisible - rsync itemizes it as `.f...p...` and the CHANGES
# grep drops it, so the scan reports "No changes" and the hub hook stays a dead
# 644. GREEN: the scan detects it, offers it, and on y chmods the hub copy to 755
# and commits, so the +x propagates.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Portable octal mode of a file (GNU stat -c, then BSD stat -f).
mode_of() { stat -c '%a' "$1" 2>/dev/null || stat -f '%Lp' "$1" 2>/dev/null; }

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/x/h.sh"
mkdir -p "$HUB_SETUP/skills/x"
printf '#!/bin/sh\necho hook\n' > "$HUB_SETUP/$REL"
chmod 644 "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && git config core.fileMode true && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
echo "session=3" > "$TMP/hub/.sync-state"

mkdir -p "$TMP/proj/.claude/skills/x"
printf '#!/bin/sh\necho hook\n' > "$TMP/proj/.claude/$REL"   # identical bytes
chmod 755 "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Sanity: the hub copy starts at 644 and the bytes are identical.
if [ "$(mode_of "$HUB_SETUP/$REL")" != "644" ]; then
  echo "FIXTURE BUG: hub copy not 644"; exit 1
fi
if ! cmp -s "$HUB_SETUP/$REL" "$TMP/proj/.claude/$REL"; then
  echo "FIXTURE BUG: bytes differ (should be a mode-only diff)"; exit 1
fi

cd "$TMP/proj"
set +e
out=$(printf 'y\ny\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion 1: the scan completes cleanly.
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# Assertion 2: the scan did NOT report the mode diff as "No changes".
if echo "$out" | grep -q "No changes"; then
  echo "FAIL: a mode-only diff was reported as 'No changes' (M5)"; echo "$out"; exit 1
fi

# Assertion 3 (the RED->GREEN flip): the hub copy mode propagated to 755.
if [ "$(mode_of "$HUB_SETUP/$REL")" != "755" ]; then
  echo "FAIL: hub copy mode did not propagate (still $(mode_of "$HUB_SETUP/$REL"), want 755)"; echo "$out"; exit 1
fi

# Assertion 4: the mode change is committed (HEAD carries it at 100755).
head_mode=$(git -C "$TMP/hub" ls-tree HEAD -- "cultivation/marketplace/sam-cc-setup/$REL" | awk '{print $1}')
if [ "$head_mode" != "100755" ]; then
  echo "FAIL: committed tree mode is $head_mode, want 100755"; echo "$out"; exit 1
fi

# Assertion 5: the bytes are unchanged (a mode-only sync must not alter content).
if ! cmp -s "$HUB_SETUP/$REL" "$TMP/proj/.claude/$REL"; then
  echo "FAIL: a mode-only sync changed the bytes"; exit 1
fi

echo "PASS: test_mode_only_propagates"
