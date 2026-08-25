#!/usr/bin/env bash
# test_uncommitted_project_refused.sh
# Verifies sync.sh refuses to run when project's .claude/ has uncommitted changes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Build ephemeral hub
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills"
cd "$TMP/hub" && git init -q && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
cd - >/dev/null

# Build ephemeral project with .claude committed, then dirty it
mkdir -p "$TMP/proj/.claude/skills/foo"
cd "$TMP/proj" && git init -q
echo "skill v1" > .claude/skills/foo/SKILL.md
git add -A && git -c user.email=t@t -c user.name=t commit -q -m init
echo "skill v2 (uncommitted)" > .claude/skills/foo/SKILL.md  # dirty .claude/

# Invoke sync.sh — should refuse
set +e
stderr=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1 >/dev/null)
rc=$?
set -e

# Assertions
if [ "$rc" -eq 0 ]; then
  echo "FAIL: sync.sh exit code 0 (should be non-zero)"
  exit 1
fi
if ! echo "$stderr" | grep -qi 'uncommitted'; then
  echo "FAIL: stderr does not mention 'uncommitted'"
  echo "stderr was: $stderr"
  exit 1
fi
# Hub working tree must be untouched
cd "$TMP/hub"
if [ -n "$(git status --porcelain)" ]; then
  echo "FAIL: hub working tree was modified despite refusal"
  exit 1
fi
echo "PASS: test_uncommitted_project_refused"
