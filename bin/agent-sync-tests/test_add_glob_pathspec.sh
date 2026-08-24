#!/usr/bin/env bash
# test_add_glob_pathspec.sh
# H1, second consequence (site c): the scoped `git add` that stages an approved
# sync uses a bare pathspec, so adding a glob-named project file (x[1].md) also
# wildmatches and stages an unrelated dirty hub WIP sibling (x1.md), sweeping it
# into the sync commit and defeating the no-contamination guarantee. The staging
# add must use `:(literal)` so only the approved file is committed.
# (Finding M9: the commit/staging path has no negative coverage, so a regression
# here would pass the rest of the suite - this test closes that gap for site c.)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL_PFX="cultivation/marketplace/sam-cc-setup"
GLOB="x[1].md"     # approved project ADD (glob-named)
WIP="x1.md"        # untracked hub WIP sibling; must NOT be swept into the commit

# Hub: a committed placeholder, git identity configured (the sync makes a real
# commit here), plus an UNTRACKED WIP sibling planted after init.
mkdir -p "$HUB_SETUP"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)
echo "HUB WIP - must not be committed" > "$HUB_SETUP/$WIP"

# Project: one new glob-named file marked 'travels', so it is an approved add.
mkdir -p "$TMP/proj/.claude/reference"
echo "add me" > "$TMP/proj/.claude/$GLOB"
printf 'x[1].md\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"

# stdin: y = continue past the hub-dirty warning (untracked WIP present);
#        y = approve the add; y = commit; n = do not push.
set +e
output=$(printf 'y\ny\ny\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "output: $output"; exit 1; fi

TRACKED=$(git -C "$TMP/hub" ls-tree -r --name-only HEAD)

# Assertion 1: the approved add reached the commit.
if ! printf '%s\n' "$TRACKED" | grep -qxF "$REL_PFX/$GLOB"; then
  echo "FAIL: approved add x[1].md not committed"; echo "$TRACKED"; echo "output: $output"; exit 1
fi

# Assertion 2 (the RED): the untracked hub WIP sibling x1.md must NOT have been
# swept into the commit. Pre-fix the bare git-add pathspec wildmatches and stages
# it, so it lands in HEAD.
if printf '%s\n' "$TRACKED" | grep -qxF "$REL_PFX/$WIP"; then
  echo "FAIL: untracked hub WIP x1.md was swept into the sync commit (bare add pathspec)"
  echo "$TRACKED"; exit 1
fi

# Assertion 3: x1.md still exists on disk and is still untracked (uncommitted WIP).
if [ ! -f "$HUB_SETUP/$WIP" ]; then
  echo "FAIL: hub WIP x1.md vanished from the working tree"; exit 1
fi

echo "PASS: test_add_glob_pathspec"
