#!/usr/bin/env bash
# test_prune_glob_pathspec.sh
# H1 + git-rm half of L1: git treats a bare `git rm` path argument as a wildmatch
# pathspec, so pruning a retired hub file whose name contains a glob metachar
# (a[1].md) ALSO matches and stages the never-offered sibling a1.md (literal
# equality on a[1].md plus wildmatch [1]->'1' on a1.md). The prune git-rm must
# use the `:(literal)` pathspec prefix so only the offered file is deleted.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL_PFX="cultivation/marketplace/sam-cc-setup"
GLOB="a[1].md"     # retired, carries a synced: record - the ONLY offered path
SIBLING="a1.md"    # hub-only, never offered; the wildmatch victim to protect

# Hub: the retired glob-named file plus its hub-only sibling. Both committed.
mkdir -p "$HUB_SETUP"
echo "bracket" > "$HUB_SETUP/$GLOB"
echo "one"     > "$HUB_SETUP/$SIBLING"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: lacks both files (a[1].md is retired). A manifest marks a[1].md
# 'travels' so the folded prune (H2 gate) offers it. Nothing marks a1.md, and
# a1.md has no ledger record, so it is never a prune candidate.
mkdir -p "$TMP/proj/.claude/reference"
printf 'a[1].md\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# a[1].md was synced in a prior session -> a prune candidate this run.
{
  echo "session=3"
  echo "synced:$GLOB:1"
} > "$TMP/hub/.sync-state"

cd "$TMP/proj"

# Run scan: y = delete the a[1].md candidate, then commit (EOF defaults commit=Y,
# push=N). H2 group 3: a declined commit now rolls the prune back, so the deletion
# lands only after a commit - this run commits and we inspect HEAD.
set +e
output=$(printf 'y\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion rc: the scan succeeded.
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "output: $output"; exit 1; fi

# Assertion 1: only a[1].md is named at a prompt (a1.md is never offered).
if ! echo "$output" | grep -qF "Delete $GLOB from hub?"; then
  echo "FAIL: no Delete prompt for $GLOB"; echo "output: $output"; exit 1
fi

# Assertion 2: the offered file a[1].md was committed as a deletion (absent from HEAD).
if git -C "$TMP/hub" cat-file -e "HEAD:$REL_PFX/$GLOB" 2>/dev/null; then
  echo "FAIL: a[1].md still at HEAD (deletion not committed)"; exit 1
fi

# Assertion 3 (the H1 guarantee): the never-offered sibling a1.md must be
# untouched - still on disk and still tracked at HEAD. Pre-fix the bare wildmatch
# pathspec swept it into the deletion (committing would drop it from HEAD too);
# :(literal) confines the delete to a[1].md.
if [ ! -f "$HUB_SETUP/$SIBLING" ]; then
  echo "FAIL: hub-only sibling a1.md was removed from the working tree"; exit 1
fi
if ! git -C "$TMP/hub" cat-file -e "HEAD:$REL_PFX/$SIBLING" 2>/dev/null; then
  echo "FAIL: hub-only sibling a1.md no longer at HEAD (swept by the glob pathspec)"; exit 1
fi

echo "PASS: test_prune_glob_pathspec"
