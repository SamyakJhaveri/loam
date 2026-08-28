#!/usr/bin/env bash
# test_staged_hub_refused.sh
# Codex Critical C2: a normal scan must refuse to run when the hub index already
# has staged changes, because the final `git commit` has no pathspec and would
# sweep that pre-staged WIP (possibly a secret) into the sync commit. Fail closed
# before any prompt; leave the staged file exactly as it was.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

# Hub: foo committed.
mkdir -p "$HUB_SETUP/skills/foo"
echo "foo" > "$HUB_SETUP/skills/foo/SKILL.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Pre-stage an unrelated file in the hub index (never committed).
echo "secret token" > "$TMP/hub/wip-secret.md"
git -C "$TMP/hub" add wip-secret.md

# Project: adds bar.
mkdir -p "$TMP/proj/.claude/skills/bar"
echo "bar" > "$TMP/proj/.claude/skills/bar/SKILL.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
BEFORE=$(git -C "$TMP/hub" rev-list --count HEAD)

# Inputs y (add bar) / y (commit default) - a fixed scan never reads them.
set +e
out=$(printf 'y\ny\n\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion 1: fail-closed, non-zero exit.
if [ "$rc" -eq 0 ]; then
  echo "FAIL: scan exit 0 with a staged hub index (must refuse)"; echo "$out"; exit 1
fi

# Assertion 2: the error names the staged file and the word "staged".
if ! echo "$out" | grep -q 'staged'; then
  echo "FAIL: error does not mention 'staged'"; echo "$out"; exit 1
fi
if ! echo "$out" | grep -q 'wip-secret.md'; then
  echo "FAIL: error does not name wip-secret.md"; echo "$out"; exit 1
fi

# Assertion 3: no new commit was made.
AFTER=$(git -C "$TMP/hub" rev-list --count HEAD)
if [ "$AFTER" != "$BEFORE" ]; then
  echo "FAIL: hub HEAD advanced ($BEFORE -> $AFTER); a commit was made"; echo "$out"; exit 1
fi

# Assertion 4: bar was NOT installed into the hub.
if [ -e "$HUB_SETUP/skills/bar/SKILL.md" ]; then
  echo "FAIL: bar leaked into the hub despite the refusal"; exit 1
fi

# Assertion 5: wip-secret.md is still staged (not unstaged, not deleted).
if [ ! -f "$TMP/hub/wip-secret.md" ]; then
  echo "FAIL: wip-secret.md was removed"; exit 1
fi
if ! git -C "$TMP/hub" diff --cached --name-only | grep -q '^wip-secret.md$'; then
  echo "FAIL: wip-secret.md is no longer staged"; git -C "$TMP/hub" status --porcelain; exit 1
fi

echo "PASS: test_staged_hub_refused"
