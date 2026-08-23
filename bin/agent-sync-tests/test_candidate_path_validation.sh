#!/usr/bin/env bash
# test_candidate_path_validation.sh
# Codex p5 High (item 6, reshaped): rsync itemizes a control char in a filename as
# `\#ooo` (both GNU and BSD rsync), so an LF-in-name cannot split the itemize line -
# but the captured string (`skills/a\#012b.md`) names no real file. The scan must
# reject any candidate failing state_path_ok OR bearing a `\#ooo` escape, warn, and
# never prompt/hash/install/record it; a normal file alongside it is still offered.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

H="$TMP/hub"; HS="$H/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HS/skills"
echo keep > "$HS/skills/keep.md"
(cd "$H" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills"
echo keep   > "$TMP/proj/.claude/skills/keep.md"      # identical -> no diff
echo normal > "$TMP/proj/.claude/skills/normal.md"    # a clean add
lf=$(printf 'a\nb')
printf 'x' > "$TMP/proj/.claude/skills/${lf}.md"      # LF-in-name add (rsync -> a\#012b.md)
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
set +e
out=$(printf 'n\nn\n' | SAM_CC_HUB_REPO="$H" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi
# The escaped candidate is refused with the warning, never offered.
if ! echo "$out" | grep -qF 'ignoring unsafe candidate path: skills/a\#012b.md'; then
  echo "FAIL: no unsafe-candidate warning for the escaped name"; echo "$out"; exit 1; fi
if echo "$out" | grep -qF 'skills/a\#012b.md to hub?'; then
  echo "FAIL: the escaped candidate was offered"; echo "$out"; exit 1; fi
# The normal file IS still offered.
if ! echo "$out" | grep -qF 'Add skills/normal.md to hub?'; then
  echo "FAIL: the normal candidate was not offered"; echo "$out"; exit 1; fi
# Nothing for the escaped/LF name was installed into the hub.
if find "$HS" -name '*b.md' | grep -q .; then
  echo "FAIL: an escaped/LF-named file reached the hub"; find "$HS"; exit 1; fi

echo "PASS: test_candidate_path_validation"
