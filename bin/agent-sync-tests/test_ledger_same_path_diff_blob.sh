#!/usr/bin/env bash
# test_ledger_same_path_diff_blob.sh
# M3 + C1 (group 11, lead-required): two projects with base records for the SAME
# relative path but DIFFERENT base blobs must BOTH stay gc-reachable. If the
# refs/agent-sync/bases tree were keyed by PATH, the two same-path bases would
# collide (update-index --index-info: one overwrites the other) and the dropped
# blob would be pruned by gc. Keying tree entries by BLOB SHA keeps both. This is
# a GREEN test on the per-project engine; its RED is the demonstrate-by-removal
# mutation (path-key the tree) shown to the critic, never committed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/x/S.md"
mkdir -p "$HUB_SETUP"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Two DISTINCT base blobs for the SAME path, hashed into the hub object store.
SHA_A=$(printf 'base blob for project A\n' | git -C "$TMP/hub" hash-object -w --stdin)
SHA_B=$(printf 'base blob for project B\n' | git -C "$TMP/hub" hash-object -w --stdin)
[ "$SHA_A" != "$SHA_B" ] || { echo "FIXTURE BUG: blobs identical"; exit 1; }

# Project A is the running project; project B is another project whose base record
# is present in the ledger (retained on A's run).
mkdir -p "$TMP/projA/.claude"
(cd "$TMP/projA" && git init -q && \
  git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init)
A_ID=$(git -C "$TMP/projA" rev-parse --show-toplevel)
B_ID="/some/other/projB"   # a literal other-project identity; retained verbatim
TAB=$'\t'
{
  echo "session=1"
  echo "base:${A_ID}${TAB}${REL}:${SHA_A}"
  echo "base:${B_ID}${TAB}${REL}:${SHA_B}"
} > "$TMP/hub/.sync-state"

# A no-op scan as project A: loads A's base, retains B's, rebuilds the bases ref.
set +e
out=$(cd "$TMP/projA" && printf '\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# gc every unreachable object.
git -C "$TMP/hub" gc --prune=now -q

# Assertion (the lead requirement): BOTH base blobs are still reachable.
if [ "$(git -C "$TMP/hub" cat-file -t "$SHA_A" 2>/dev/null)" != blob ]; then
  echo "FAIL: project A's base blob was pruned (bases tree dropped it)"; exit 1
fi
if [ "$(git -C "$TMP/hub" cat-file -t "$SHA_B" 2>/dev/null)" != blob ]; then
  echo "FAIL: project B's same-path base blob was pruned (tree keyed by path -> collision)"; exit 1
fi

# And B's ledger record survived A's run verbatim.
if ! grep -qF -- "base:${B_ID}${TAB}${REL}:${SHA_B}" "$TMP/hub/.sync-state"; then
  echo "FAIL: project B's base record was not retained through A's write_state"; cat "$TMP/hub/.sync-state"; exit 1
fi

echo "PASS: test_ledger_same_path_diff_blob"
