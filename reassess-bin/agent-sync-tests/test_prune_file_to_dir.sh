#!/usr/bin/env bash
# test_prune_file_to_dir.sh
# M6 (file->dir half): consider_prune must test -f, not -e, on the PROJECT side.
# A path that was a synced FILE but became a DIRECTORY in the project must have its
# stale hub FILE OFFERED for prune - the project directory must not shield it.
# RED (scan.sh:784 `-e`): the project dir satisfies -e, so consider_prune returns
# before appending the candidate and the "Delete ..." prompt never appears.
# GREEN (`-f`): no regular project file at the path, so the stale hub file is offered.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

REL="skills/x/S.md"
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"

# Hub: a regular FILE at skills/x/S.md, committed.
mkdir -p "$HUB_SETUP/skills/x"
echo "hub content" > "$HUB_SETUP/$REL"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: skills/x/S.md is now a DIRECTORY (the file became a dir) holding one
# child, so the project has NO regular file at skills/x/S.md. The manifest lists
# skills/x/S.md as a travels row (eligible for the prune fold-in); the child
# skills/x/S.md/child.md matches that same travels row via manifest_verdict's
# dirname walk (longest-prefix), so it is offered as a travels ADD and declined by
# the stdin n - no install runs, so no mkdir wedge is reached.
mkdir -p "$TMP/proj/.claude/skills/x/S.md"
echo "child body" > "$TMP/proj/.claude/skills/x/S.md/child.md"
mkdir -p "$TMP/proj/.claude/reference"
printf 'path\tkind\tverdict\treason\trequires\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
printf '%s\tfile\ttravels\tretired\t\n' "$REL" >> "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Seed the ledger so consider_prune enumerates skills/x/S.md via the synced:* loop.
# Legacy-unprefixed synced: is R5-adopted as this project's -> STATE_DECISIONS.
{
  echo "session=3"
  echo "synced:$REL:3"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"
# Decline everything: the RED is purely whether the Delete prompt appears.
set +e
out=$(printf 'n\nn\nn\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
cd - >/dev/null

# Sanity: the scan completed cleanly (declining is a clean exit).
if [ "$rc" -ne 0 ]; then
  echo "FAIL: scan exit $rc"; echo "$out"; exit 1
fi

# The fix: the stale hub FILE is now offered for prune despite the project dir.
if ! echo "$out" | grep -qF "Delete $REL from hub?"; then
  echo "FAIL: stale hub file was not offered for prune (project dir shielded it via -e)"
  echo "$out"; exit 1
fi

# Declined -> hub file kept (nothing deleted).
if [ ! -f "$HUB_SETUP/$REL" ]; then
  echo "FAIL: hub file was deleted despite declining the prune"
  echo "$out"; exit 1
fi

echo "PASS: test_prune_file_to_dir"
