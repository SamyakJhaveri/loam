#!/usr/bin/env bash
# test_bootstrap_skips_gitignored.sh
# 8b Item 2 (bootstrap enumeration path): --bootstrap-bases enumerates project
# files with `find` over the .claude tree, which walks the filesystem - so a
# .gitignored (untracked) project file present in both trees would get a base
# record. The scan must enumerate git-tracked files only: a gitignored project
# file must never receive a base, and the skip must surface as a one-line stderr
# summary count (N>0 only, silent at N==0). Both directions tested.
set -euo pipefail
T=$(printf '\t')   # ledger project-id delimiter (M3)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
SUMMARY="gitignored project file(s) not based"

mk_hub() {  # $1 = hub root; both files present so both are "shared" for bootstrap
  mkdir -p "$1/cultivation/marketplace/sam-cc-setup/skills/x"
  echo "tracked"    > "$1/cultivation/marketplace/sam-cc-setup/skills/x/tracked.md"
  echo "gitignored" > "$1/cultivation/marketplace/sam-cc-setup/skills/x/ignored.md"
  (cd "$1" && git init -q \
    && git -c user.email=t@t -c user.name=t add -A \
    && git -c user.email=t@t -c user.name=t commit -q -m init)
}

# ---------- Direction A: gitignored shared file -> not based + counted ----------
TMPA="$(mktemp -d)"
trap 'rm -rf "$TMPA" "${TMPB:-}"' EXIT
mk_hub "$TMPA/hub"
STATEA="$TMPA/hub/.sync-state"
mkdir -p "$TMPA/proj/.claude/skills/x"
echo "tracked"    > "$TMPA/proj/.claude/skills/x/tracked.md"
printf 'ignored.md\n' > "$TMPA/proj/.gitignore"
echo "gitignored" > "$TMPA/proj/.claude/skills/x/ignored.md"
(cd "$TMPA/proj" && git init -q \
  && git -c user.email=t@t -c user.name=t add -A \
  && git -c user.email=t@t -c user.name=t commit -q -m init)
if git -C "$TMPA/proj" ls-files --error-unmatch .claude/skills/x/ignored.md >/dev/null 2>&1; then
  echo "FIXTURE-BUG: ignored.md is tracked"; exit 1
fi
echo "session=5" > "$STATEA"

cd "$TMPA/proj"
set +e
outA=$(SAM_CC_HUB_REPO="$TMPA/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1)
rcA=$?
set -e
if [ "$rcA" -ne 0 ]; then echo "FAIL(A): bootstrap exit $rcA"; echo "$outA"; exit 1; fi
# The git-tracked shared file must get a base (no over-filtering).
want=$(git hash-object "$TMPA/proj/.claude/skills/x/tracked.md")
if ! grep -qE "^base:[^$T]*${T}skills/x/tracked.md:$want\$" "$STATEA"; then
  echo "FAIL(A): tracked.md did not get a base"; cat "$STATEA"; echo "$outA"; exit 1
fi
# The RED assertion: the gitignored shared file must NOT get a base.
if grep -qE "^base:[^$T]*${T}skills/x/ignored.md:" "$STATEA"; then
  echo "FAIL(A): a gitignored project file received a base record"; cat "$STATEA"; exit 1
fi
# The skip must surface as the stderr summary count (N>0).
if ! echo "$outA" | grep -qF "$SUMMARY"; then
  echo "FAIL(A): no stderr summary count for the skipped gitignored file"; echo "$outA"; exit 1
fi

# ---------- Direction B: no gitignored file -> summary silent (N==0) ------------
TMPB="$(mktemp -d)"
mk_hub "$TMPB/hub"
STATEB="$TMPB/hub/.sync-state"
# Remove the hub-only ignored.md so both trees share only tracked.md (no skip).
rm -f "$TMPB/hub/cultivation/marketplace/sam-cc-setup/skills/x/ignored.md"
(cd "$TMPB/hub" && git -c user.email=t@t -c user.name=t commit -q -am "drop ignored" >/dev/null 2>&1)
mkdir -p "$TMPB/proj/.claude/skills/x"
echo "tracked" > "$TMPB/proj/.claude/skills/x/tracked.md"
(cd "$TMPB/proj" && git init -q \
  && git -c user.email=t@t -c user.name=t add -A \
  && git -c user.email=t@t -c user.name=t commit -q -m init)
echo "session=5" > "$STATEB"

cd "$TMPB/proj"
set +e
outB=$(SAM_CC_HUB_REPO="$TMPB/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1)
rcB=$?
set -e
if [ "$rcB" -ne 0 ]; then echo "FAIL(B): bootstrap exit $rcB"; echo "$outB"; exit 1; fi
wantB=$(git hash-object "$TMPB/proj/.claude/skills/x/tracked.md")
if ! grep -qE "^base:[^$T]*${T}skills/x/tracked.md:$wantB\$" "$STATEB"; then
  echo "FAIL(B): tracked.md did not get a base"; cat "$STATEB"; echo "$outB"; exit 1
fi
# Silence at N==0: the summary line must NOT appear.
if echo "$outB" | grep -qF "$SUMMARY"; then
  echo "FAIL(B): summary count printed when nothing was skipped"; echo "$outB"; exit 1
fi

echo "PASS: test_bootstrap_skips_gitignored"
