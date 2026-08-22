#!/usr/bin/env bash
# test_crafted_state_path.sh
# (named ...state_path, not ...state_key: .gitignore's *_key* secret pattern
#  would otherwise swallow this file so git add silently no-ops it.)
# Codex High H1: a crafted .sync-state key (path traversal, absolute path) is
# rejected at parse time by state_path_ok - each prints a warning, is dropped
# from the ledger, is never offered for prune, and is not re-emitted by the next
# write_state - so it can never drive a git-rm outside the plugin root.
#
# Leg A: a CONTRIVED manifest row marks the traversal prefix 'travels' purely to
#   bypass the item-3 (H2) prune gate; against the pre-fix engine that lets the
#   crafted key reach an approved prune that git-rm's hub/README.md OUTSIDE the
#   plugin tree (the real H1 deletion). state_path_ok blocks it at the parse layer.
# Leg B: the brief's no-manifest case - item-3's gate already withholds the
#   unclassified candidate, so the visible gap is the missing warnings and the
#   crafted keys persisting in the rewritten .sync-state.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

TRAV="../../../README.md"   # resolves to the hub ROOT from the plugin dir

# ---- Leg A: contrived 'travels' manifest -> real deletion RED against pre-fix --
HUBA="$TMP/hubA"; SETUPA="$HUBA/cultivation/marketplace/sam-cc-setup"
mkdir -p "$SETUPA/skills/foo"
echo "top secret readme" > "$HUBA/README.md"
echo "foo" > "$SETUPA/skills/foo/SKILL.md"
(cd "$HUBA" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/projA/.claude/skills/foo" "$TMP/projA/.claude/reference"
echo "foo" > "$TMP/projA/.claude/skills/foo/SKILL.md"
# CONTRIVED row: nobody would classify '..' as travels; it exists ONLY to bypass
# the item-3 prune gate so the pre-fix deletion is observable. state_path_ok must
# block the traversal key regardless of any such manifest.
printf '..\t-\ttravels\n' > "$TMP/projA/.claude/reference/portability-manifest.tsv"
(cd "$TMP/projA" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

{ echo "session=1"; echo "synced:$TRAV:1"; } > "$HUBA/.sync-state"

cd "$TMP/projA"
set +e
outA=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$HUBA" bash "$SYNC_SH" 2>&1)
rcA=$?
set -e
if [ "$rcA" -ne 0 ]; then echo "FAIL(A): scan exit $rcA"; echo "$outA"; exit 1; fi
# The file OUTSIDE the plugin tree is intact (the whole point of H1).
if [ ! -f "$HUBA/README.md" ]; then echo "FAIL(A): hub/README.md deleted outside the plugin tree"; echo "$outA"; exit 1; fi
if git -C "$HUBA" status --porcelain | grep -qE '^D.*README\.md'; then
  echo "FAIL(A): hub/README.md staged as deleted"; git -C "$HUBA" status --porcelain; exit 1; fi
if echo "$outA" | grep -q "Delete $TRAV from hub?"; then
  echo "FAIL(A): crafted key offered for deletion despite the travels manifest"; echo "$outA"; exit 1; fi
if ! echo "$outA" | grep -qF "warning: ignoring malformed .sync-state key: $TRAV"; then
  echo "FAIL(A): no malformed-key warning for $TRAV"; echo "$outA"; exit 1; fi
if grep -qF "$TRAV" "$HUBA/.sync-state"; then echo "FAIL(A): traversal key persisted"; cat "$HUBA/.sync-state"; exit 1; fi

# ---- Leg B: brief's no-manifest defense-in-depth case ----
HUBB="$TMP/hubB"; SETUPB="$HUBB/cultivation/marketplace/sam-cc-setup"
mkdir -p "$SETUPB/skills/foo"
echo "top secret readme" > "$HUBB/README.md"
echo "foo" > "$SETUPB/skills/foo/SKILL.md"
(cd "$HUBB" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/projB/.claude/skills/foo"
echo "foo" > "$TMP/projB/.claude/skills/foo/SKILL.md"
(cd "$TMP/projB" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

{ echo "session=1"; echo "synced:$TRAV:1"; echo "never:/etc/passwd"; } > "$HUBB/.sync-state"

cd "$TMP/projB"
set +e
outB=$(printf 'n\n' | SAM_CC_HUB_REPO="$HUBB" bash "$SYNC_SH" 2>&1)
rcB=$?
set -e
if [ "$rcB" -ne 0 ]; then echo "FAIL(B): scan exit $rcB"; echo "$outB"; exit 1; fi
if echo "$outB" | grep -q "Delete $TRAV from hub?"; then
  echo "FAIL(B): crafted key offered for deletion"; echo "$outB"; exit 1; fi
if [ ! -f "$HUBB/README.md" ]; then echo "FAIL(B): hub/README.md deleted"; echo "$outB"; exit 1; fi
if git -C "$HUBB" status --porcelain | grep -qE '^D.*README\.md'; then
  echo "FAIL(B): hub/README.md staged as deleted"; git -C "$HUBB" status --porcelain; exit 1; fi
for key in "$TRAV" "/etc/passwd"; do
  if ! echo "$outB" | grep -qF "warning: ignoring malformed .sync-state key: $key"; then
    echo "FAIL(B): no malformed-key warning for $key"; echo "$outB"; exit 1; fi
done
if grep -qF "$TRAV" "$HUBB/.sync-state"; then echo "FAIL(B): traversal key persisted"; cat "$HUBB/.sync-state"; exit 1; fi
if grep -qF "/etc/passwd" "$HUBB/.sync-state"; then echo "FAIL(B): absolute key persisted"; cat "$HUBB/.sync-state"; exit 1; fi

echo "PASS: test_crafted_state_path"
