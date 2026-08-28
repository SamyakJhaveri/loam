#!/usr/bin/env bash
# test_git_dir_excluded_scan.sh
# H6 (group 6): a nested .git under .claude/ (a vendored repo) must never be
# enumerated or offered for sync. In a manifest-less project (the documented
# default for other consumers) the scan currently offers .git internals as adds;
# installing them creates an embedded repo in the hub and the scoped git add then
# stages nothing across the nested-repo boundary. The scan must exclude .git while
# still offering the legit sibling files.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

# Hub: a committed placeholder + identity.
mkdir -p "$HUB_SETUP"
echo "placeholder" > "$HUB_SETUP/.keep"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)

# Project: MANIFEST-LESS, with a vendored repo under .claude/ (a nested .git dir
# plus a legit tracked file) and a top-level file. git ignores the .git dir's
# contents, so .claude commits clean.
mkdir -p "$TMP/proj/.claude/vendored/.git"
printf 'ref: refs/heads/main\n' > "$TMP/proj/.claude/vendored/.git/HEAD"
printf '[core]\n' > "$TMP/proj/.claude/vendored/.git/config"
printf 'tool body\n' > "$TMP/proj/.claude/vendored/tool.md"
printf 'keep body\n' > "$TMP/proj/.claude/keep.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"

# Defer every offer (d): nothing is installed; we only inspect what was ENUMERATED.
set +e
out=$(printf 'd\nd\nd\nd\nd\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# Assertion 1 (RED): no .git path is offered/enumerated.
if echo "$out" | grep -qF ".git/"; then
  echo "FAIL: a .git path was enumerated/offered by the scan"; echo "$out"; exit 1
fi
if echo "$out" | grep -qiE "Add +vendored/\.git"; then
  echo "FAIL: the scan offered a vendored/.git add"; echo "$out"; exit 1
fi

# Assertion 2: the legit sibling files ARE still offered.
if ! echo "$out" | grep -qF "Add keep.md to hub?"; then
  echo "FAIL: keep.md was not offered"; echo "$out"; exit 1
fi
if ! echo "$out" | grep -qF "Add vendored/tool.md to hub?"; then
  echo "FAIL: vendored/tool.md was not offered"; echo "$out"; exit 1
fi

echo "PASS: test_git_dir_excluded_scan"
