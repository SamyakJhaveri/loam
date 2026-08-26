#!/usr/bin/env bash
# test_push_declined_remote_unchanged.sh
# M9 (b): no test answered N at the push prompt and asserted the remote did NOT
# advance, so an unconditional-push mutation passed the whole suite - and the push is
# the engine's only outward-facing action. This approves an add, COMMITS (Y), then
# DECLINES the push (n): the hub HEAD must advance (commit made) while the remote ref
# stays exactly where it was.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git init -q --bare "$TMP/remote.git"

# Hub: foo committed, origin set, initial push.
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo"
echo "foo" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md"
(cd "$TMP/hub" && git -c init.defaultBranch=main init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init && \
  git remote add origin "$TMP/remote.git" && git push -q -u origin main)
REMOTE_BEFORE=$(git -C "$TMP/remote.git" rev-parse main)
HUB_BEFORE=$(git -C "$TMP/hub" rev-parse HEAD)

# Project: foo + new bar.
mkdir -p "$TMP/proj/.claude/skills/foo" "$TMP/proj/.claude/skills/bar"
echo "foo" > "$TMP/proj/.claude/skills/foo/SKILL.md"
echo "bar" > "$TMP/proj/.claude/skills/bar/SKILL.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
# approve bar (y), commit (default Y = empty line), push DECLINE (n).
set +e
out=$(printf 'y\n\nn\n' | \
  SAM_CC_HUB_REPO="$TMP/hub" \
  GIT_AUTHOR_NAME=test GIT_AUTHOR_EMAIL=t@t \
  GIT_COMMITTER_NAME=test GIT_COMMITTER_EMAIL=t@t \
  bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# The commit WAS made locally (hub HEAD advanced).
if [ "$(git -C "$TMP/hub" rev-parse HEAD)" = "$HUB_BEFORE" ]; then
  echo "FAIL: hub HEAD unchanged - the commit was not made"; echo "$out"; exit 1
fi
# The push was DECLINED: the remote ref must be byte-identical to before.
REMOTE_AFTER=$(git -C "$TMP/remote.git" rev-parse main)
if [ "$REMOTE_AFTER" != "$REMOTE_BEFORE" ]; then
  echo "FAIL: remote main advanced ($REMOTE_BEFORE -> $REMOTE_AFTER) despite declining the push"
  echo "$out"; exit 1
fi
# And the user was told the commit is local.
if ! echo "$out" | grep -q "Commit kept local"; then
  echo "FAIL: missing the 'Commit kept local' notice on push decline"; echo "$out"; exit 1
fi

echo "PASS: test_push_declined_remote_unchanged"
