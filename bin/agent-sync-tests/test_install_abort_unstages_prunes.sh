#!/usr/bin/env bash
# test_install_abort_unstages_prunes.sh
# CI-p1 round-3 High 2: approve the collision Add, approve ONE child prune, defer
# the other. The install aborts (directory still non-empty). The staged prune
# deletion must be restored so the NEXT scan is not wedged by the staged-index
# guard, and the restored prune re-offers.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

mkdir -p "$HUB_SETUP/foo"
echo keep > "$HUB_SETUP/keep.md"
echo a > "$HUB_SETUP/foo/a.md"
echo b > "$HUB_SETUP/foo/b.md"
(cd "$TMP/hub" && git init -q && git config user.email t@t && git config user.name t && git add -A && git commit -q -m init)

mkdir -p "$TMP/proj/.claude/reference"
echo keep > "$TMP/proj/.claude/keep.md"
echo file-foo > "$TMP/proj/.claude/foo"
printf 'foo\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

{ echo "session=3"; echo "synced:foo/a.md:1"; echo "synced:foo/b.md:1"; } > "$TMP/hub/.sync-state"

cd "$TMP/proj"
set +e
out=$(printf 'y\ny\nd\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -eq 0 ]; then echo "FAIL: run 1 exited 0; expected the install abort"; echo "$out"; exit 1; fi
if ! echo "$out" | grep -qF "restored 1 staged prune deletion"; then
  echo "FAIL: missing the staged-prune restore message"; echo "$out"; exit 1; fi
if ! git -C "$TMP/hub" diff --cached --quiet; then
  echo "FAIL: hub index still has staged changes after the abort"; git -C "$TMP/hub" status --short; exit 1; fi
if [ ! -f "$HUB_SETUP/foo/a.md" ]; then echo "FAIL: pruned a.md was not restored"; exit 1; fi

set +e
out2=$(printf 'n\nn\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: run 2 exit $rc2 (expected a clean second scan)"; echo "$out2"; exit 1; fi
if echo "$out2" | grep -qF "hub index has staged changes"; then
  echo "FAIL: run 2 wedged on the staged-index guard"; echo "$out2"; exit 1; fi
if ! echo "$out2" | grep -qF "foo/a.md"; then
  echo "FAIL: restored prune did not re-offer on run 2"; echo "$out2"; exit 1; fi
echo "PASS: test_install_abort_unstages_prunes"
