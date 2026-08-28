#!/usr/bin/env bash
# test_prune_dir_to_file.sh
# M6 dir->file half (group 5): the hub has a DIRECTORY at a synced path whose
# children are retired (project source gone), and the project now has a FILE at
# that same path. Approving the child prunes AND the file add in one run must
# git-rm the children (emptying and removing the hub directory) BEFORE the file
# is installed, so the add lands instead of dying on "destination is a directory".
# Requires prune git-rms to run before installs.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL_PFX="cultivation/marketplace/sam-cc-setup"

# Hub: a DIRECTORY foo/ with two retired children, plus a shared keep file.
mkdir -p "$HUB_SETUP/foo"
echo "keep" > "$HUB_SETUP/keep.md"
echo "a"    > "$HUB_SETUP/foo/a.md"
echo "b"    > "$HUB_SETUP/foo/b.md"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)

# Project: foo is now a FILE (so foo/a.md and foo/b.md sources are gone), keep is
# identical. Manifest row foo=travels covers the add foo AND, by longest-prefix,
# the child prunes foo/a.md and foo/b.md.
mkdir -p "$TMP/proj/.claude/reference"
echo "keep"    > "$TMP/proj/.claude/keep.md"
echo "file-foo" > "$TMP/proj/.claude/foo"
printf 'foo\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Both children were synced in a prior session -> prune candidates this run.
{
  echo "session=3"
  echo "synced:foo/a.md:1"
  echo "synced:foo/b.md:1"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"

# stdin: y = add foo, y = delete a.md, y = delete b.md; EOF then commits (Y) and
# declines the push (N).
set +e
out=$(printf 'y\ny\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion rc: the run completed (pre-fix it aborts rc=1 on the dir install).
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# Assertion 1 (RED): no directory-destination install failure.
if echo "$out" | grep -qF "destination is a directory"; then
  echo "FAIL: install hit a directory at foo (prune did not run before install)"; echo "$out"; exit 1
fi

# Assertion 2 (RED): foo is committed as a FILE at HEAD.
foo_type=$(git -C "$TMP/hub" cat-file -t "HEAD:$REL_PFX/foo" 2>/dev/null || echo none)
if [ "$foo_type" != blob ]; then
  echo "FAIL: foo is not a committed file blob at HEAD (got: $foo_type)"; echo "$out"; exit 1
fi
if [ "$(git -C "$TMP/hub" cat-file -p "HEAD:$REL_PFX/foo")" != "file-foo" ]; then
  echo "FAIL: foo file content wrong at HEAD"; exit 1
fi

# Assertion 3: the retired children are gone from HEAD (pruned + committed).
for child in foo/a.md foo/b.md; do
  if git -C "$TMP/hub" cat-file -e "HEAD:$REL_PFX/$child" 2>/dev/null; then
    echo "FAIL: retired child still at HEAD: $child"; exit 1
  fi
done

# Assertion 4 (control): the shared unchanged file survives.
if [ ! -f "$HUB_SETUP/keep.md" ]; then echo "FAIL: keep.md removed"; exit 1; fi

echo "PASS: test_prune_dir_to_file"
