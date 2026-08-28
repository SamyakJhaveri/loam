#!/usr/bin/env bash
# test_prune_standalone.sh
# L1 + L5: the standalone bin/agent-sync-prune.sh had ZERO coverage (it read
# /dev/tty, so it was untestable) and ignored the manifest verdict column while
# deleting directory rows recursively. This exercises the hardened prune.sh:
#   Leg A - verdict gate: only a 'travels' row is offered; stays/rework/unclassified
#           are withheld (matching the scan fold-in).
#   Leg B - directory-row safety: a directory row enumerates every tracked hub file
#           it would delete BEFORE the y/N, so nothing is removed unnamed.
#   Leg C - :(literal) lock (group-1 flag): deleting a glob-named row (a[1].md) must
#           not sweep a hub-only sibling (a1.md).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PRUNE_SH="$SCRIPT_DIR/../agent-sync-prune.sh"
HP="cultivation/marketplace/sam-cc-setup"

# ---- Leg A: verdict gate ----
A="$(mktemp -d)"
trap 'rm -rf "$A" "${B:-}" "${C:-}"' EXIT
mkdir -p "$A/hub/$HP/skills/staysdir" "$A/hub/$HP/skills/travelsdir"
echo "s" > "$A/hub/$HP/skills/staysdir/S.md"
echo "t" > "$A/hub/$HP/skills/travelsdir/S.md"
(cd "$A/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
mkdir -p "$A/proj/.claude/reference"
{ printf 'path\tkind\tverdict\treason\trequires\n'
  printf 'skills/staysdir/S.md\tfile\tstays\tkeep\t\n'
  printf 'skills/travelsdir/S.md\tfile\ttravels\tretired\t\n'; } > "$A/proj/.claude/reference/portability-manifest.tsv"
(cd "$A/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
# Both project sources gone (never created under .claude/skills). EOF stdin -> kept.
cd "$A/proj"
set +e
outA=$(printf '' | SAM_CC_HUB_REPO="$A/hub" bash "$PRUNE_SH" 2>&1)
rcA=$?
set -e
cd - >/dev/null
if [ "$rcA" -ne 0 ]; then echo "FAIL(A): prune exit $rcA"; echo "$outA"; exit 1; fi
if ! echo "$outA" | grep -qF "Hub file with no project source: sam-cc-setup/skills/travelsdir/S.md"; then
  echo "FAIL(A): the travels row was not offered"; echo "$outA"; exit 1; fi
if echo "$outA" | grep -qF "Hub file with no project source: sam-cc-setup/skills/staysdir/S.md"; then
  echo "FAIL(A): a stays row was offered (verdict gate missing)"; echo "$outA"; exit 1; fi
if ! echo "$outA" | grep -qF "prune withheld"; then
  echo "FAIL(A): no withheld notice for the non-travels row"; echo "$outA"; exit 1; fi
# EOF -> nothing deleted.
if ! git -C "$A/hub" diff --cached --quiet; then echo "FAIL(A): something was staged for deletion on EOF"; git -C "$A/hub" diff --cached --name-status; exit 1; fi

# ---- Leg B: directory-row enumeration ----
B="$(mktemp -d)"
mkdir -p "$B/hub/$HP/skills/tooldir"
echo "a" > "$B/hub/$HP/skills/tooldir/a.md"
echo "hub-only, no manifest row" > "$B/hub/$HP/skills/tooldir/HUBONLY.md"
(cd "$B/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
mkdir -p "$B/proj/.claude/reference"
{ printf 'path\tkind\tverdict\treason\trequires\n'
  printf 'skills/tooldir\tdir\ttravels\tretired\t\n'; } > "$B/proj/.claude/reference/portability-manifest.tsv"
(cd "$B/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$B/proj"
set +e
outB=$(printf 'y\n' | SAM_CC_HUB_REPO="$B/hub" bash "$PRUNE_SH" 2>&1)
rcB=$?
set -e
cd - >/dev/null
if [ "$rcB" -ne 0 ]; then echo "FAIL(B): prune exit $rcB"; echo "$outB"; exit 1; fi
if ! echo "$outB" | grep -qF "NOTE: this is a DIRECTORY"; then
  echo "FAIL(B): directory row was not flagged/enumerated"; echo "$outB"; exit 1; fi
# Every tracked hub file under the dir is named BEFORE deletion - incl. the hub-only one.
if ! echo "$outB" | grep -qF "skills/tooldir/HUBONLY.md"; then
  echo "FAIL(B): the hub-only file inside the directory was not named before deletion"; echo "$outB"; exit 1; fi
if ! echo "$outB" | grep -qF "skills/tooldir/a.md"; then
  echo "FAIL(B): a tracked file inside the directory was not enumerated"; echo "$outB"; exit 1; fi
# The stdin 'y' actually took effect (proves the stdin read): the dir is staged deleted.
if ! git -C "$B/hub" diff --cached --name-status | grep -qF "$HP/skills/tooldir/HUBONLY.md"; then
  echo "FAIL(B): approved directory prune did not stage the deletion"; git -C "$B/hub" diff --cached --name-status; exit 1; fi

# ---- Leg C: :(literal) lock - a glob-named row must not sweep a sibling ----
C="$(mktemp -d)"
mkdir -p "$C/hub/$HP"
echo "bracket" > "$C/hub/$HP/a[1].md"
echo "sibling" > "$C/hub/$HP/a1.md"           # hub-only, no manifest row
(cd "$C/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
mkdir -p "$C/proj/.claude/reference"
{ printf 'path\tkind\tverdict\treason\trequires\n'
  printf 'a[1].md\tfile\ttravels\tretired\t\n'; } > "$C/proj/.claude/reference/portability-manifest.tsv"
(cd "$C/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
cd "$C/proj"
set +e
outC=$(printf 'y\n' | SAM_CC_HUB_REPO="$C/hub" bash "$PRUNE_SH" 2>&1)
rcC=$?
set -e
cd - >/dev/null
if [ "$rcC" -ne 0 ]; then echo "FAIL(C): prune exit $rcC"; echo "$outC"; exit 1; fi
STAGED=$(git -C "$C/hub" diff --cached --name-status)
if ! echo "$STAGED" | grep -qF "D	$HP/a[1].md"; then
  echo "FAIL(C): a[1].md was not staged for deletion (stdin read not taking effect?)"; echo "$STAGED"; echo "$outC"; exit 1; fi
if echo "$STAGED" | grep -qF "D	$HP/a1.md"; then
  echo "FAIL(C): the sibling a1.md was swept into the deletion (:(literal) not honored)"; echo "$STAGED"; exit 1; fi
if ! git -C "$C/hub" cat-file -e "HEAD:$HP/a1.md" 2>/dev/null; then
  echo "FAIL(C): a1.md missing from HEAD"; exit 1; fi

echo "PASS: test_prune_standalone"
