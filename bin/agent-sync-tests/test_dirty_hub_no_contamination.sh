#!/usr/bin/env bash
# test_dirty_hub_no_contamination.sh
# REGRESSION: when user continues through the dirty-hub warning, the sync
# commit must contain ONLY the approved synced files — never unrelated WIP.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Bare remote so commit/push works in test
git init -q --bare "$TMP/remote.git"

# Hub: foo committed + WIP file (uncommitted, simulating user mid-edit)
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo"
echo "foo" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md"
(cd "$TMP/hub" && \
  git -c init.defaultBranch=main init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init && \
  git remote add origin "$TMP/remote.git" && \
  git push -q -u origin main)

# Add WIP — uncommitted hub work that must NOT end up in the sync commit
echo "secret WIP that should not be committed" > "$TMP/hub/wip-document.md"

# Project: foo (matches), bar (new addition to sync)
mkdir -p "$TMP/proj/.claude/skills/foo" "$TMP/proj/.claude/skills/bar"
echo "foo" > "$TMP/proj/.claude/skills/foo/SKILL.md"
echo "bar" > "$TMP/proj/.claude/skills/bar/SKILL.md"
(cd "$TMP/proj" && \
  git -c init.defaultBranch=main init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Run sync — answer Y to "Continue?" (proceed through dirty-hub),
# y to bar add, default-Y to commit prompt
cd "$TMP/proj"
set +e
output=$(printf 'y\ny\n\n' | \
  SAM_CC_HUB_REPO="$TMP/hub" \
  GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=t@t \
  GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=t@t \
  bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

if [ "$rc" -ne 0 ]; then
  echo "FAIL: exit $rc"; echo "output: $output"; exit 1
fi

# Assertion 1: sync commit exists
HEAD_FILES=$(git -C "$TMP/hub" show --name-only --pretty=format: HEAD | grep -v '^$')

# Assertion 2: bar/SKILL.md is in the commit
if ! echo "$HEAD_FILES" | grep -q '^cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md$'; then
  echo "FAIL: bar/SKILL.md not in sync commit"
  echo "files in HEAD: $HEAD_FILES"
  exit 1
fi

# Assertion 3 (the BLOCKER fix): wip-document.md must NOT be in the commit
if echo "$HEAD_FILES" | grep -q '^wip-document.md$'; then
  echo "FAIL: wip-document.md was swept into the sync commit (git add -A contamination)"
  echo "files in HEAD: $HEAD_FILES"
  exit 1
fi

# Assertion 4: WIP file still present in working tree (untouched)
if [ ! -f "$TMP/hub/wip-document.md" ]; then
  echo "FAIL: wip-document.md was removed/stashed"
  exit 1
fi

echo "PASS: test_dirty_hub_no_contamination"
