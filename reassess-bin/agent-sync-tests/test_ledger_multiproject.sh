#!/usr/bin/env bash
# test_ledger_multiproject.sh
# M3 (group 11): a scan by project B must PRESERVE project A's ledger records
# verbatim (never adopt or drop them). GREEN on the per-project engine; its RED is
# the demonstrate-by-removal mutation (drop RETAINED_LINES) shown to the critic,
# never committed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HUB_SETUP"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

SHA_C=$(printf 'A base c\n' | git -C "$TMP/hub" hash-object -w --stdin)
A_ID="/some/other/projA"   # another project's identity (literal; retained verbatim)
TAB=$'\t'
# Project A's records (all four types), already project-keyed in the ledger.
A_NEVER="never:${A_ID}${TAB}skills/a/S.md"
A_DEFER="defer:${A_ID}${TAB}skills/b/S.md:5"
A_SYNCED="synced:${A_ID}${TAB}skills/d/S.md:2"
A_BASE="base:${A_ID}${TAB}skills/c/S.md:${SHA_C}"
A_PNEVER="prune-never:${A_ID}${TAB}skills/e/S.md"
{
  echo "session:${A_ID}${TAB}4"
  echo "$A_NEVER"; echo "$A_DEFER"; echo "$A_SYNCED"; echo "$A_BASE"; echo "$A_PNEVER"
} > "$TMP/hub/.sync-state"

# Project B: a different project; a no-op scan (empty .claude) so it just re-writes.
mkdir -p "$TMP/projB/.claude"
(cd "$TMP/projB" && git init -q && \
  git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init)

set +e
out=$(cd "$TMP/projB" && printf '\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: project B scan exit $rc"; echo "$out"; exit 1; fi

# Every one of project A's records must survive verbatim.
for rec in "$A_NEVER" "$A_DEFER" "$A_SYNCED" "$A_BASE" "$A_PNEVER" "session:${A_ID}${TAB}4"; do
  if ! grep -qF -- "$rec" "$TMP/hub/.sync-state"; then
    echo "FAIL: project A record dropped by project B's run: $rec"; echo "--- ledger ---"; cat "$TMP/hub/.sync-state"; exit 1
  fi
done

# A's base blob stays reachable after gc (retained sha fed into the bases tree).
git -C "$TMP/hub" gc --prune=now -q
if [ "$(git -C "$TMP/hub" cat-file -t "$SHA_C" 2>/dev/null)" != blob ]; then
  echo "FAIL: project A's base blob pruned after B's run + gc"; exit 1
fi

echo "PASS: test_ledger_multiproject"
