#!/usr/bin/env bash
# test_commit_push_path.sh
# Full happy path: approve addition + accept commit/push, verify commit on hub + push to remote.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

# Bare remote
git init -q --bare "$TMP/remote.git"

# Hub: foo committed, origin set, initial push
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo"
echo "foo" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md"
(cd "$TMP/hub" && \
  git -c init.defaultBranch=main init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init && \
  git remote add origin "$TMP/remote.git" && \
  git push -q -u origin main)
HUB_HEAD_BEFORE=$(git -C "$TMP/hub" rev-parse HEAD)

# Project: foo + new bar
mkdir -p "$TMP/proj/.claude/skills/foo" "$TMP/proj/.claude/skills/bar"
echo "foo" > "$TMP/proj/.claude/skills/foo/SKILL.md"
echo "bar" > "$TMP/proj/.claude/skills/bar/SKILL.md"
(cd "$TMP/proj" && \
  git -c init.defaultBranch=main init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Run sync — approve bar (y), accept default-Y commit+push (empty)
cd "$TMP/proj"
set +e
output=$(printf 'y\n\ny\n' | \
  SAM_CC_HUB_REPO="$TMP/hub" \
  GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=t@t \
  GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=t@t \
  bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

# Assertion 1: exit 0
if [ "$rc" -ne 0 ]; then
  echo "FAIL: exit $rc"
  echo "output: $output"
  exit 1
fi

# Assertion 2: hub HEAD changed (new commit)
HUB_HEAD_AFTER=$(git -C "$TMP/hub" rev-parse HEAD)
if [ "$HUB_HEAD_BEFORE" = "$HUB_HEAD_AFTER" ]; then
  echo "FAIL: hub HEAD unchanged — no commit was made"
  echo "output: $output"
  exit 1
fi

# Assertion 3: commit message format
COMMIT_MSG=$(git -C "$TMP/hub" log -1 --pretty=%B HEAD)
TODAY=$(date -u +%Y-%m-%d)
if ! echo "$COMMIT_MSG" | grep -q "sync: from proj on $TODAY"; then
  echo "FAIL: commit message wrong"
  echo "got: $COMMIT_MSG"
  exit 1
fi

# Assertion 4: remote received the push (bare repo's main matches hub's HEAD)
REMOTE_HEAD=$(git -C "$TMP/remote.git" rev-parse main)
if [ "$REMOTE_HEAD" != "$HUB_HEAD_AFTER" ]; then
  echo "FAIL: remote main ($REMOTE_HEAD) does not match hub HEAD ($HUB_HEAD_AFTER) — push did not happen"
  exit 1
fi

echo "PASS: test_commit_push_path"
