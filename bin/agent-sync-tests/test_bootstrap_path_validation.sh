#!/usr/bin/env bash
# test_bootstrap_path_validation.sh
# Codex p6 High (item 8): the bootstrap loop read `find` output by newline, so a
# project file whose name contains a newline was split into two bogus rels (silently
# dropped), and `rel` was never validated. Now bootstrap reads `find -print0` and runs
# candidate_ok on each rel: a newline-named file is refused atomically with a warning
# and never hashed or recorded, while a normal shared file still gets its base.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

H="$TMP/hub"; HS="$H/cultivation/marketplace/sam-cc-setup"
lf=$(printf 'a\nb')
mkdir -p "$HS/skills"
echo shared > "$HS/skills/normal.md"
printf 'x' > "$HS/skills/${lf}.md"   # a shared file with a newline in its name
(cd "$H" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj/.claude/skills"
echo shared > "$TMP/proj/.claude/skills/normal.md"
printf 'x' > "$TMP/proj/.claude/skills/${lf}.md"
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
set +e
out=$(SAM_CC_HUB_REPO="$H" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
rc=$?
set -e
STATE="$H/.sync-state"

if [ "$rc" -ne 0 ]; then echo "FAIL: bootstrap exit $rc"; echo "$out"; exit 1; fi
# The newline-named candidate is refused with the warning (its name starts "skills/a").
if ! echo "$out" | grep -qF 'ignoring unsafe candidate path: skills/a'; then
  echo "FAIL: no unsafe-candidate warning for the newline-named file"; echo "$out"; exit 1; fi
# Exactly one base recorded, and it is the normal shared file.
nbase=$(grep -c '^base:' "$STATE")
if [ "$nbase" -ne 1 ]; then echo "FAIL: expected exactly 1 base, got $nbase"; cat -v "$STATE"; exit 1; fi
if ! grep -q '^base:skills/normal.md:' "$STATE"; then echo "FAIL: normal.md base not recorded"; cat -v "$STATE"; exit 1; fi
# No base line other than the normal file (no split-fragment or newline-key base).
if grep -a '^base:' "$STATE" | grep -vq '^base:skills/normal.md:'; then
  echo "FAIL: a malformed base line was recorded"; cat -v "$STATE"; exit 1; fi

echo "PASS: test_bootstrap_path_validation"
