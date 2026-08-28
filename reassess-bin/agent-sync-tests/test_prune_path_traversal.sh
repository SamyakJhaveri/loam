#!/usr/bin/env bash
# test_prune_path_traversal.sh
# CX-1 (Critical): bin/agent-sync-prune.sh built hub_path/src_path and the git rm
# pathspec directly from an untrusted manifest-row path. A 'travels' row whose path
# escapes the plugin root (../../../AGENTS.md) resolves hub_path to the HUB ROOT's
# AGENTS.md and, on y, `git rm -- :(literal).../../../AGENTS.md` stages that
# unrelated file's deletion - a file the y/N prompt never named. The fix validates
# the row path (reject absolute / . / .. / CR / LF) before building any fs path or
# pathspec, so the row is withheld.
#   RED (unmodified engine): the hub-root AGENTS.md is staged for deletion.
#   GREEN (fixed engine): the row is withheld, nothing is staged, AGENTS.md intact.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PRUNE_SH="$SCRIPT_DIR/../agent-sync-prune.sh"
HP="cultivation/marketplace/sam-cc-setup"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Hub: a hub-root AGENTS.md (the escape target) + a normal plugin file.
mkdir -p "$TMP/hub/$HP"
echo "HUB ROOT - must never be pruned by a plugin manifest row" > "$TMP/hub/AGENTS.md"
echo "keep" > "$TMP/hub/$HP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: a single 'travels' row whose path escapes the plugin root. No project
# source exists for it (it resolves outside .claude), so the "source gone" gate
# passes and the row reaches the deletion path.
mkdir -p "$TMP/proj/.claude/reference"
{ printf 'path\tkind\tverdict\treason\trequires\n'
  printf '../../../AGENTS.md\tfile\ttravels\tretired\t\n'; } \
  > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
set +e
out=$(printf 'y\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$PRUNE_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -ne 0 ]; then echo "FAIL: prune exit $rc"; echo "$out"; exit 1; fi

# Assertion 1 (RED->GREEN flip): the hub-root AGENTS.md must NOT be staged for deletion.
if git -C "$TMP/hub" diff --cached --name-status | grep -qE '^D[[:space:]]+AGENTS\.md$'; then
  echo "FAIL: hub-root AGENTS.md was staged for deletion by a traversal manifest row"
  git -C "$TMP/hub" diff --cached --name-status; echo "$out"; exit 1
fi

# Assertion 2: nothing at all was staged.
if ! git -C "$TMP/hub" diff --cached --quiet; then
  echo "FAIL: a traversal manifest row staged a change"
  git -C "$TMP/hub" diff --cached --name-status; exit 1
fi

# Assertion 3: the hub-root file is intact in the worktree and HEAD.
if [ ! -e "$TMP/hub/AGENTS.md" ]; then
  echo "FAIL: hub-root AGENTS.md was removed from the worktree"; exit 1
fi
if ! git -C "$TMP/hub" cat-file -e "HEAD:AGENTS.md" 2>/dev/null; then
  echo "FAIL: hub-root AGENTS.md missing from HEAD"; exit 1
fi

# Assertion 4: the row was withheld with a clear notice.
if ! echo "$out" | grep -qiF "unsafe manifest path"; then
  echo "FAIL: no 'unsafe manifest path' withhold notice for the traversal row"; echo "$out"; exit 1
fi

echo "PASS: test_prune_path_traversal"
