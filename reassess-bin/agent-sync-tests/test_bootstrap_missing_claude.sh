#!/usr/bin/env bash
# test_bootstrap_missing_claude.sh
# M8-a (group 8): --bootstrap-bases with NO project .claude/ must ABORT
# re-runnably (rc!=0, an error naming the missing tree), not report
# "0 bases recorded" and exit 0 (the fail-open bug).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HUB_SETUP/skills/x"
echo "hub content" > "$HUB_SETUP/skills/x/S.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project dir is a git repo but has NO .claude/ (the wrong-cwd case).
mkdir -p "$TMP/proj"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init)

cd "$TMP/proj"
set +e
out=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
rc=$?
set -e

# Assertion 1 (the RED->GREEN flip): a missing project .claude aborts non-zero.
if [ "$rc" -eq 0 ]; then
  echo "FAIL: bootstrap with no project .claude exited 0 (fail-open)"; echo "$out"; exit 1
fi

# Assertion 2: the error names the missing project tree.
if ! echo "$out" | grep -qi 'claude'; then
  echo "FAIL: abort message does not name the missing .claude tree"; echo "$out"; exit 1
fi

# Assertion 3: it did NOT falsely claim success.
if echo "$out" | grep -q 'bases recorded'; then
  echo "FAIL: bootstrap printed a success report despite the missing tree"; echo "$out"; exit 1
fi

echo "PASS: test_bootstrap_missing_claude"
