#!/usr/bin/env bash
# test_binary_merge_fallback.sh
# M4 (group 10): a changed binary asset with a recorded base routes into the merge
# regime; git merge-file returns 255 on binary input. The old code treated EVERY
# 255 as an operational error and skipped forever, so the update could never be
# delivered. GREEN: a binary 255 (both inputs readable) falls through to the
# legacy overwrite prompt; on y the hub copy is overwritten and the base
# re-recorded. The operational-error skip (unreadable input) is preserved by
# test_merge_error_skips.sh (re-run separately).
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/x/asset.bin"
mkdir -p "$HUB_SETUP/skills/x"

# Three distinct binary blobs (NUL bytes make them binary to git merge-file).
printf 'BIN\x00\x01\x02hub\x00\xff'     > "$HUB_SETUP/$REL"
printf 'BIN\x00\x01\x02base\x00\xff'    > "$TMP/base.bin"
(cd "$TMP/hub" && git init -q && git config core.fileMode true && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills/x"
printf 'BIN\x00\x01\x02project\x00\xff' > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Record a base blob (base != project so Critical-1 does not suppress; base blob
# present so the merge regime is entered -> merge-file 255 on binary input).
BASE_SHA=$(git -C "$TMP/hub" hash-object -w "$TMP/base.bin")
{ echo "session=3"; echo "base:$REL:$BASE_SHA"; } > "$TMP/hub/.sync-state"

PROJ_SHA=$(git -C "$TMP/hub" hash-object "$TMP/proj/.claude/$REL")

cd "$TMP/proj"
set +e
out=$(printf 'y\ny\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion 1: the scan completes cleanly.
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# Assertion 2: the binary 255 was NOT reported as a plain skip.
if echo "$out" | grep -q "Merge error $REL: git merge-file failed (exit 255); skipped"; then
  echo "FAIL: a binary change was skipped as an operational error (M4 not fixed)"; echo "$out"; exit 1
fi

# Assertion 3: it was offered as an overwrite (the fallthrough prompt appeared).
if ! echo "$out" | grep -q "Update $REL to hub?"; then
  echo "FAIL: the binary change was not offered a full overwrite"; echo "$out"; exit 1
fi

# Assertion 4 (the RED->GREEN flip): the hub copy now equals the project bytes.
if ! cmp -s "$HUB_SETUP/$REL" "$TMP/proj/.claude/$REL"; then
  echo "FAIL: the binary overwrite did not reach the hub copy"; exit 1
fi

# Assertion 5: the base was re-recorded to the new project blob (R2).
if ! grep -qE "^base:[^$T]*${T}$REL:$PROJ_SHA\$" "$TMP/hub/.sync-state"; then
  echo "FAIL: base not re-recorded to the project blob after overwrite"; cat "$TMP/hub/.sync-state"; exit 1
fi

echo "PASS: test_binary_merge_fallback"
