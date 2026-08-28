#!/usr/bin/env bash
# test_symlinked_claude_guard.sh
# M7 (group 12): when a project's .claude is a SYMLINK (loam's own layout
# .claude -> seed/.claude), the commit-check `git status --porcelain .claude`
# statuses only the symlink blob, so an UNCOMMITTED file under seed/.claude is
# invisible and the guard passes - then rsync's trailing-slash follow would
# promote the uncommitted bytes. The fix resolves the symlink and statuses the
# TARGET, so the dirty file is seen and the scan refuses.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Hub.
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HUB_SETUP"; echo keep > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
echo "session=1" > "$TMP/hub/.sync-state"

# Project with .claude -> seed/.claude (the committed symlink layout).
mkdir -p "$TMP/proj/seed/.claude/skills/x"
echo "committed" > "$TMP/proj/seed/.claude/skills/x/S.md"
(cd "$TMP/proj" && ln -s seed/.claude .claude && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Sanity: .claude is a symlink and the tree is clean at commit time.
[ -L "$TMP/proj/.claude" ] || { echo "FIXTURE BUG: .claude is not a symlink"; exit 1; }

# Now dirty a file UNDER the symlink target (uncommitted).
echo "UNCOMMITTED EDIT" >> "$TMP/proj/seed/.claude/skills/x/S.md"

cd "$TMP/proj"
set +e
out=$(printf 'n\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion (RED->GREEN flip): the scan must REFUSE - the uncommitted edit under
# the symlink target must be seen. RED (statuses the symlink blob): not refused.
if ! echo "$out" | grep -qi "uncommitted changes"; then
  echo "FAIL: symlinked .claude with a dirty target was NOT refused (M7 bypass)"; echo "rc=$rc"; echo "$out"; exit 1
fi
if [ "$rc" -eq 0 ]; then
  echo "FAIL: scan exited 0 despite an uncommitted edit under the .claude symlink target"; echo "$out"; exit 1
fi

echo "PASS: test_symlinked_claude_guard"
