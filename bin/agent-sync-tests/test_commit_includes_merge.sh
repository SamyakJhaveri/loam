#!/usr/bin/env bash
# test_commit_includes_merge.sh
# M9 (a): the commit+push stage had no test asserting the COMMIT CONTENTS include
# approved merge results or changes - dropping MERGED_PATHS/APPROVED_CHANGES from the
# staging loop (scan.sh:1434) passed the whole suite, so a regression would push
# commits silently missing merged content. This asserts the committed tree (HEAD, and
# the pushed remote) actually carries both a three-way MERGE result and a plain CHANGE.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
MREL="skills/merge/SKILL.md"      # three-way merge path
CREL="skills/change/SKILL.md"     # plain change path

# Base ancestor for the merge path.
BASE="$TMP/base.txt"
printf 'alpha\nbeta\ngamma\ndelta\n' > "$BASE"

# Hub: merge path = base + hub-only generalization on line 1; change path = old body.
mkdir -p "$HUB_SETUP/skills/merge" "$HUB_SETUP/skills/change"
printf 'alpha GENERALIZED\nbeta\ngamma\ndelta\n' > "$HUB_SETUP/$MREL"
echo "old change body" > "$HUB_SETUP/$CREL"
git init -q --bare "$TMP/remote.git"
(cd "$TMP/hub" && git -c init.defaultBranch=main init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init && \
  git remote add origin "$TMP/remote.git" && git push -q -u origin main)

# Project: merge path = base + project edit on the last line; change path = new body.
mkdir -p "$TMP/proj/.claude/skills/merge" "$TMP/proj/.claude/skills/change"
printf 'alpha\nbeta\ngamma\ndelta PROJECTEDIT\n' > "$TMP/proj/.claude/$MREL"
echo "new change body" > "$TMP/proj/.claude/$CREL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Record the merge base blob + ledger.
BASE_SHA=$(git -C "$TMP/hub" hash-object -w "$BASE")
{ echo "session=1"; echo "base:$MREL:$BASE_SHA"; } > "$TMP/hub/.sync-state"

cd "$TMP/proj"
# Prompts: accept the merge (y), approve the change (y), commit (default Y = empty),
# push (y). Order of add/change/merge prompts is rsync-driven; y to all covers it.
set +e
out=$(printf 'y\ny\n\ny\n' | \
  SAM_CC_HUB_REPO="$TMP/hub" \
  GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=t@t \
  GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=t@t \
  bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

HUBREL="cultivation/marketplace/sam-cc-setup"
EXPECT_MERGE=$(printf 'alpha GENERALIZED\nbeta\ngamma\ndelta PROJECTEDIT\n')

# The committed tree at HEAD must carry the MERGE result (not just the worktree).
GOT_MERGE=$(git -C "$TMP/hub" show "HEAD:$HUBREL/$MREL" 2>/dev/null || true)
if [ "$GOT_MERGE" != "$EXPECT_MERGE" ]; then
  echo "FAIL: committed HEAD lacks the merge result for $MREL (MERGED_PATHS not staged?)"
  echo "--- got ---"; printf '%s\n' "$GOT_MERGE"; exit 1
fi
# The committed tree must carry the plain CHANGE too.
GOT_CHANGE=$(git -C "$TMP/hub" show "HEAD:$HUBREL/$CREL" 2>/dev/null || true)
if [ "$GOT_CHANGE" != "new change body" ]; then
  echo "FAIL: committed HEAD lacks the changed content for $CREL (APPROVED_CHANGES not staged?)"
  echo "--- got ---"; printf '%s\n' "$GOT_CHANGE"; exit 1
fi
# The push delivered that commit to the remote.
if [ "$(git -C "$TMP/remote.git" rev-parse main)" != "$(git -C "$TMP/hub" rev-parse HEAD)" ]; then
  echo "FAIL: remote main did not receive the commit"; exit 1
fi
# And the merge result is reachable in the remote's committed tree.
GOT_REMOTE=$(git -C "$TMP/remote.git" show "main:$HUBREL/$MREL" 2>/dev/null || true)
if [ "$GOT_REMOTE" != "$EXPECT_MERGE" ]; then
  echo "FAIL: pushed remote tree lacks the merge result for $MREL"; exit 1
fi

echo "PASS: test_commit_includes_merge"
