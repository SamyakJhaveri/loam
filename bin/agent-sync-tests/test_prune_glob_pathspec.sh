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

# Run scan: y = delete the a[1].md candidate, n = do not commit (inspect index).
set +e
output=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion rc: the scan succeeded.
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "output: $output"; exit 1; fi

# Assertion 1: only a[1].md is named at a prompt (a1.md is never offered).
if ! echo "$output" | grep -qF "Delete $GLOB from hub?"; then
  echo "FAIL: no Delete prompt for $GLOB"; echo "output: $output"; exit 1
fi

STAGED=$(git -C "$TMP/hub" diff --cached --name-status)

# Assertion 2: the offered file a[1].md is staged as deleted.
if ! printf '%s\n' "$STAGED" | awk -F'\t' -v p="$REL_PFX/$GLOB" '$1=="D" && $2==p {f=1} END{exit !f}'; then
  echo "FAIL: a[1].md not staged as deleted"; echo "$STAGED"; exit 1
fi

# Assertion 3 (the RED): the never-offered sibling a1.md must NOT appear in the
# staged changes at all, must still exist, and must still be tracked at HEAD.
# Pre-fix the bare wildmatch pathspec sweeps it into the deletion.
if printf '%s\n' "$STAGED" | awk -F'\t' -v p="$REL_PFX/$SIBLING" '$2==p{f=1} END{exit !f}'; then
  echo "FAIL: hub-only sibling a1.md was swept into the staged changes (bare glob pathspec)"
  echo "$STAGED"; exit 1
fi
if [ ! -f "$HUB_SETUP/$SIBLING" ]; then
  echo "FAIL: hub-only sibling a1.md was removed from the working tree"; exit 1
fi
if ! git -C "$TMP/hub" cat-file -e "HEAD:$REL_PFX/$SIBLING" 2>/dev/null; then
  echo "FAIL: hub-only sibling a1.md no longer at HEAD"; exit 1
fi

echo "PASS: test_prune_glob_pathspec"
