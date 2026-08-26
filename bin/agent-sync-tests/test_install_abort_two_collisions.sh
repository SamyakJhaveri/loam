#!/usr/bin/env bash
# test_install_abort_two_collisions.sh
# CI-p1 round-4 High: collision aaa is fully pruned and installed; collision zzz
# then aborts (one child deferred). The abort restore must first remove the
# installed aaa file (HEAD-absent, pending-only) so aaa's pruned child can be
# checked out, leaving the hub index clean and the next scan unwedged.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

mkdir -p "$HUB_SETUP/aaa" "$HUB_SETUP/zzz"
echo keep > "$HUB_SETUP/keep.md"
echo a1 > "$HUB_SETUP/aaa/a1.md"
echo z1 > "$HUB_SETUP/zzz/z1.md"
echo z2 > "$HUB_SETUP/zzz/z2.md"
(cd "$TMP/hub" && git init -q && git config user.email t@t && git config user.name t && git add -A && git commit -q -m init)

mkdir -p "$TMP/proj/.claude/reference"
echo keep > "$TMP/proj/.claude/keep.md"
echo file-aaa > "$TMP/proj/.claude/aaa"
echo file-zzz > "$TMP/proj/.claude/zzz"
printf 'aaa\t-\ttravels\nzzz\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

{ echo "session=3"; echo "synced:aaa/a1.md:1"; echo "synced:zzz/z1.md:1"; echo "synced:zzz/z2.md:1"; } > "$TMP/hub/.sync-state"

cd "$TMP/proj"
# Sorted prompt order: Add aaa, Add zzz, Delete aaa/a1.md, Delete zzz/z1.md,
# Delete zzz/z2.md. Answers: y y y y d -> aaa installs (dir emptied), zzz aborts.
set +e
out=$(printf 'y\ny\ny\ny\nd\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -eq 0 ]; then echo "FAIL: run 1 exited 0; expected the zzz install abort"; echo "$out"; exit 1; fi
if ! echo "$out" | grep -qF "restored 2 staged prune deletion"; then
  echo "FAIL: expected both staged prunes restored"; echo "$out"; exit 1; fi
if echo "$out" | grep -qF "could not restore staged prune"; then
  echo "FAIL: a prune restore failed (installed collision file not removed first)"; echo "$out"; exit 1; fi
if ! git -C "$TMP/hub" diff --cached --quiet; then
  echo "FAIL: hub index still staged after abort"; git -C "$TMP/hub" status --short; exit 1; fi
if [ -f "$HUB_SETUP/aaa" ] && [ ! -d "$HUB_SETUP/aaa" ]; then
  echo "FAIL: installed collision file aaa was not removed on abort"; exit 1; fi
if [ ! -f "$HUB_SETUP/aaa/a1.md" ] || [ ! -f "$HUB_SETUP/zzz/z1.md" ]; then
  echo "FAIL: pruned children not restored"; exit 1; fi

set +e
out2=$(printf 'n\nn\nn\nn\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc2=$?
set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL: run 2 exit $rc2"; echo "$out2"; exit 1; fi
if echo "$out2" | grep -qF "hub index has staged changes"; then
  echo "FAIL: run 2 wedged on the staged-index guard"; echo "$out2"; exit 1; fi
echo "PASS: test_install_abort_two_collisions"
