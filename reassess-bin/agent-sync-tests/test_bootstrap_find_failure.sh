#!/usr/bin/env bash
# test_bootstrap_find_failure.sh
# M8-b (group 8): a find enumeration failure (an unreadable subtree under
# .claude) must ABORT re-runnably (rc!=0, an error naming the failure), not
# record only the readable subset and exit 0. The old `done < <(find ...)`
# never checked the process-substitution exit status.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
# The unreadable subdir must be restored before rm -rf can clean the tree.
trap 'chmod -R u+rwx "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HUB_SETUP/skills/readable" "$HUB_SETUP/skills/blocked"
echo "hub readable" > "$HUB_SETUP/skills/readable/S.md"
echo "hub blocked"  > "$HUB_SETUP/skills/blocked/S.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/readable" "$TMP/proj/.claude/skills/blocked"
echo "proj readable" > "$TMP/proj/.claude/skills/readable/S.md"
echo "proj blocked"  > "$TMP/proj/.claude/skills/blocked/S.md"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Make one subtree unreadable so find errors mid-enumeration.
chmod 000 "$TMP/proj/.claude/skills/blocked"

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"
set +e
out=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
rc=$?
set -e
chmod -R u+rwx "$TMP/proj/.claude/skills/blocked" 2>/dev/null || true

# Assertion 1 (the RED->GREEN flip): an enumeration failure aborts non-zero.
if [ "$rc" -eq 0 ]; then
  echo "FAIL: bootstrap exited 0 despite a find enumeration failure (partial bootstrap)"; echo "$out"; exit 1
fi

# Assertion 2: it did NOT falsely claim to have recorded the readable subset.
if echo "$out" | grep -q 'bases recorded'; then
  echo "FAIL: bootstrap printed a success report despite the enumeration failure"; echo "$out"; exit 1
fi

# Assertion 3: no partial base was persisted for the readable subtree.
if [ -f "$STATE" ] && grep -q '^base:' "$STATE"; then
  echo "FAIL: a partial base was persisted on the abort"; cat "$STATE"; exit 1
fi

echo "PASS: test_bootstrap_find_failure"
