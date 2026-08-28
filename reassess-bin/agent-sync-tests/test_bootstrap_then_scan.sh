#!/usr/bin/env bash
# test_bootstrap_then_scan.sh
# After --bootstrap-bases records a base for a shared file that differs between
# hub (generalized) and project, a following scan must NOT re-offer it: the
# project is unchanged vs the recorded base, so the only delta is the hub's own
# generalization. Regression lock on Codex Critical 1 (Task-1b no-op bug).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/diff/SKILL.md"

# Shared file, generalized differently in the hub.
mkdir -p "$HUB_SETUP/skills/diff"
echo "hub version" > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/diff"
echo "project version" > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"

# 1) bootstrap records base = hash-object(project) for the shared path.
set +e
bout=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
brc=$?
set -e
if [ "$brc" -ne 0 ]; then echo "FAIL: bootstrap exit $brc"; echo "$bout"; exit 1; fi

# 2) scan: the path must NOT be offered (project unchanged vs base).
set +e
out=$(printf '\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi
if echo "$out" | grep -qE "Merge $REL|Update $REL|$REL to hub\?"; then
  echo "FAIL: scan re-offered an unchanged-since-base path"; echo "$out"; exit 1
fi
if ! echo "$out" | grep -q "0 changed files to ask about"; then
  echo "FAIL: path not counted as suppressed"; echo "$out"; exit 1
fi
if [ "$(cat "$HUB_SETUP/$REL")" != "hub version" ]; then
  echo "FAIL: hub copy changed"; cat "$HUB_SETUP/$REL"; exit 1
fi

echo "PASS: test_bootstrap_then_scan"
