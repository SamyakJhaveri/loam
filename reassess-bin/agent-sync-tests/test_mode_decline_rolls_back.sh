#!/usr/bin/env bash
# test_mode_decline_rolls_back.sh
# Group 9 left a gap the critic flagged for group 16: the mode-only COMMIT path is
# tested (test_mode_only_propagates) but the mode-DECLINE rollback leg is only covered
# by composition (APPROVED_MODES is in the decline rollback loop at scan.sh:1416).
# This locks it: approve a mode-only change (755 vs 644, identical bytes), then DECLINE
# the commit; the hub copy's mode must be restored to 644 and no commit made.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

REL="skills/x/h.sh"
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

mkdir -p "$HUB_SETUP/skills/x"
printf '#!/bin/sh\necho hi\n' > "$HUB_SETUP/$REL"
chmod 644 "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && git config core.fileMode true && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
HUB_HEAD_BEFORE=$(git -C "$TMP/hub" rev-parse HEAD)

# Project: identical bytes, mode 755.
mkdir -p "$TMP/proj/.claude/skills/x"
printf '#!/bin/sh\necho hi\n' > "$TMP/proj/.claude/$REL"
chmod 755 "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && git config core.fileMode true && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

echo "session=3" > "$TMP/hub/.sync-state"

# Fixture sanity: identical bytes, hub 644.
if ! cmp -s "$HUB_SETUP/$REL" "$TMP/proj/.claude/$REL"; then echo "FAIL(fixture): bytes differ"; exit 1; fi

cd "$TMP/proj"
# Sync the mode (y), then DECLINE the commit (n).
set +e
out=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# The mode prompt was shown (the leg is actually exercised).
if ! echo "$out" | grep -q "Sync mode of $REL"; then
  echo "FAIL: mode prompt not shown - fixture did not produce a mode-only diff"; echo "$out"; exit 1
fi
# Declined: the hub copy's mode is rolled back to 644 (checkout HEAD).
MODE=$(stat -c '%a' "$HUB_SETUP/$REL" 2>/dev/null || stat -f '%Lp' "$HUB_SETUP/$REL")
if [ "$MODE" != "644" ]; then
  echo "FAIL: hub mode not rolled back on decline (got $MODE, want 644)"; echo "$out"; exit 1
fi
# No commit made.
if [ "$(git -C "$TMP/hub" rev-parse HEAD)" != "$HUB_HEAD_BEFORE" ]; then
  echo "FAIL: hub HEAD advanced despite declining the commit"; exit 1
fi
# The decline notice printed.
if ! echo "$out" | grep -q "Declined - hub restored"; then
  echo "FAIL: missing decline-restore notice"; echo "$out"; exit 1
fi

echo "PASS: test_mode_decline_rolls_back"
