#!/usr/bin/env bash
# test_hub_gitignore_preflight.sh
# H3: nothing checks the hub's ignore rules before install. A hub-gitignored
# approved add (e.g. a 2026-* dated doc under a 'travels' row) is installed, then
# `git add` refuses it and set -e kills the script before the commit - so NO file
# in the batch commits, the non-ignored one is left staged, and every later scan
# wedges on the C2 staged-index guard. A check-ignore preflight must skip such a
# path BEFORE install so the rest of the batch commits cleanly.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL_PFX="cultivation/marketplace/sam-cc-setup"
IGN="skills/x/2026-notes.md"   # matches the hub .gitignore '2026-*'
PLAIN="skills/x/plain.md"      # not ignored; the batch companion that must commit

# Hub: a committed .gitignore (2026-*), a committed placeholder, git identity
# configured (a real commit happens), plugin dir present.
mkdir -p "$HUB_SETUP"
printf '2026-*\n.sync-state\n' > "$TMP/hub/.gitignore"
echo "keep" > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)

# Project: two new files under a 'travels' row; one is hub-gitignored.
mkdir -p "$TMP/proj/.claude/skills/x" "$TMP/proj/.claude/reference"
echo "dated"  > "$TMP/proj/.claude/$IGN"
echo "plain"  > "$TMP/proj/.claude/$PLAIN"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"

# stdin 'y\ny': approve every offered add and let EOF drive the trailing prompts.
# Pre-fix (2 adds offered): y=add 2026-notes, y=add plain, EOF -> commit default Y
#   -> git add refuses 2026-notes -> set -e aborts non-zero (no commit).
# Post-fix (2026-notes filtered, 1 add offered): y=add plain, y=commit,
#   EOF -> push default N -> clean commit, exit 0.
set +e
output=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion 1 (the RED): the scan succeeds. Pre-fix git add aborts the batch.
if [ "$rc" -ne 0 ]; then
  echo "FAIL: scan exit $rc (hub-gitignored add aborted the batch commit)"; echo "output: $output"; exit 1
fi

TRACKED=$(git -C "$TMP/hub" ls-tree -r --name-only HEAD)

# Assertion 2 (the RED): the non-ignored companion committed. Pre-fix nothing commits.
if ! printf '%s\n' "$TRACKED" | grep -qxF "$REL_PFX/$PLAIN"; then
  echo "FAIL: the non-ignored add plain.md did not commit"; echo "$TRACKED"; echo "output: $output"; exit 1
fi

# Assertion 3: the hub-gitignored file never entered the hub (not committed).
if printf '%s\n' "$TRACKED" | grep -qxF "$REL_PFX/$IGN"; then
  echo "FAIL: hub-gitignored file was committed"; echo "$TRACKED"; exit 1
fi

# Assertion 4: the skip was reported and named the offending path.
if ! echo "$output" | grep -qF "$IGN"; then
  echo "FAIL: no message naming the skipped hub-gitignored path"; echo "output: $output"; exit 1
fi

# Assertion 5: the hub index is clean after (no staged residue -> next scan is not wedged).
if [ -n "$(git -C "$TMP/hub" diff --cached --name-only)" ]; then
  echo "FAIL: hub index has staged residue after the run"; git -C "$TMP/hub" diff --cached --name-only; exit 1
fi

echo "PASS: test_hub_gitignore_preflight"
