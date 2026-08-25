#!/usr/bin/env bash
# test_git_dir_excluded_bootstrap.sh
# H6 (group 6, bootstrap layer): --bootstrap-bases must not walk a nested .git and
# must not record a base for any .git/... path. The bootstrap find is pruned at
# .git and candidate_ok rejects a .git component, so a vendored repo present in
# both trees records bases only for the legit files.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
STATE="$TMP/hub/.sync-state"

# Hub: committed placeholder + identity, then PLANT the same vendored tree on disk
# (bootstrap checks [ -f ] on disk, not tracked-ness).
mkdir -p "$HUB_SETUP/vendored/.git"
echo "placeholder" > "$HUB_SETUP/.keep"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)
printf 'ref: refs/heads/main\n' > "$HUB_SETUP/vendored/.git/HEAD"
printf 'tool body\n' > "$HUB_SETUP/vendored/tool.md"
printf 'keep body\n' > "$HUB_SETUP/keep.md"

# Project: the same set under .claude/.
mkdir -p "$TMP/proj/.claude/vendored/.git"
printf 'ref: refs/heads/main\n' > "$TMP/proj/.claude/vendored/.git/HEAD"
printf 'tool body\n' > "$TMP/proj/.claude/vendored/tool.md"
printf 'keep body\n' > "$TMP/proj/.claude/keep.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"

set +e
out=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: bootstrap exit $rc"; echo "$out"; exit 1; fi

# Assertion 1 (RED): no base recorded for any .git/... path.
if grep -qE "^base:vendored/\.git/" "$STATE" 2>/dev/null; then
  echo "FAIL: bootstrap recorded a base for a .git path"; grep "\.git" "$STATE"; exit 1
fi
if grep -qF ".git/" "$STATE" 2>/dev/null; then
  echo "FAIL: a .git path leaked into the ledger"; cat "$STATE"; exit 1
fi

# Assertion 2: bases WERE recorded for the legit files.
for rel in keep.md vendored/tool.md; do
  if ! grep -qE "^base:$rel:" "$STATE" 2>/dev/null; then
    echo "FAIL: no base recorded for the legit file $rel"; cat "$STATE"; exit 1
  fi
done

echo "PASS: test_git_dir_excluded_bootstrap"
