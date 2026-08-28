#!/usr/bin/env bash
# test_scan_skips_gitignored.sh
# 8b Item 2 (rsync/scan enumeration path): the additive diff is computed by rsync
# over the .claude tree, which walks the filesystem - so a project file that is
# .gitignored (untracked) would be offered as an add and promoted into the hub.
# The hub mirrors COMMITTED project state, so the scan must enumerate git-tracked
# files only: a gitignored project file must never be offered or committed, and
# the skip must surface as a one-line stderr summary count (N>0 only, silent at
# N==0). Both directions tested in one file.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
REL_PFX="cultivation/marketplace/sam-cc-setup"
SUMMARY="gitignored project file(s) (not git-tracked"

mk_hub() {  # $1 = hub root
  mkdir -p "$1/$REL_PFX/skills/x"
  printf '.sync-state\n' > "$1/.gitignore"
  echo "keep" > "$1/$REL_PFX/keep.md"
  (cd "$1" && git init -q && git config user.email t@t && git config user.name t \
    && git add -A && git commit -q -m init)
}

# ---------- Direction A: a gitignored file present -> filtered + counted --------
TMPA="$(mktemp -d)"
trap 'rm -rf "$TMPA" "${TMPB:-}"' EXIT
mk_hub "$TMPA/hub"
# Project: one TRACKED new file and one GITIGNORED (untracked) file under .claude.
# The gitignore lives at the PROJECT ROOT (outside .claude) so it is not synced; a
# bare `ignored.md` pattern matches the file at any depth.
mkdir -p "$TMPA/proj/.claude/skills/x"
echo "tracked"  > "$TMPA/proj/.claude/skills/x/tracked.md"
printf 'ignored.md\n' > "$TMPA/proj/.gitignore"
echo "gitignored" > "$TMPA/proj/.claude/skills/x/ignored.md"
(cd "$TMPA/proj" && git init -q \
  && git -c user.email=t@t -c user.name=t add -A \
  && git -c user.email=t@t -c user.name=t commit -q -m init)
# Sanity: the gitignored file really is untracked, else the test is meaningless.
if git -C "$TMPA/proj" ls-files --error-unmatch .claude/skills/x/ignored.md >/dev/null 2>&1; then
  echo "FIXTURE-BUG: ignored.md is tracked"; exit 1
fi

cd "$TMPA/proj"
# stdin 'y\ny\n': approve the first offered add, then answer the next prompt y.
# Pre-fix (2 adds): y=ignored, y=tracked, EOF -> commit Y, push EOF -> N (both land).
# Post-fix (ignored filtered, 1 add): y=tracked, y=commit, push EOF -> N.
set +e
outA=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMPA/hub" bash "$SYNC_SH" 2>&1)
rcA=$?
set -e
if [ "$rcA" -ne 0 ]; then echo "FAIL(A): scan exit $rcA"; echo "$outA"; exit 1; fi

TRACKED=$(git -C "$TMPA/hub" ls-tree -r --name-only HEAD)
# The tracked file must still be promoted (no over-filtering).
if ! printf '%s\n' "$TRACKED" | grep -qxF "$REL_PFX/skills/x/tracked.md"; then
  echo "FAIL(A): the git-tracked add did not commit"; echo "$TRACKED"; echo "$outA"; exit 1
fi
# The RED assertion: the gitignored file must NEVER reach the hub.
if printf '%s\n' "$TRACKED" | grep -qxF "$REL_PFX/skills/x/ignored.md"; then
  echo "FAIL(A): a gitignored project file was promoted into the hub"; echo "$TRACKED"; exit 1
fi
# It must never be offered as an add prompt.
if echo "$outA" | grep -qF "Add skills/x/ignored.md to hub?"; then
  echo "FAIL(A): gitignored file was offered as an add"; echo "$outA"; exit 1
fi
# The skip must surface as the stderr summary count (N>0).
if ! echo "$outA" | grep -qF "$SUMMARY"; then
  echo "FAIL(A): no stderr summary count for the skipped gitignored file"; echo "$outA"; exit 1
fi

# ---------- Direction B: no gitignored file -> summary silent (N==0) ------------
TMPB="$(mktemp -d)"
mk_hub "$TMPB/hub"
mkdir -p "$TMPB/proj/.claude/skills/x"
echo "tracked" > "$TMPB/proj/.claude/skills/x/tracked.md"
(cd "$TMPB/proj" && git init -q \
  && git -c user.email=t@t -c user.name=t add -A \
  && git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMPB/proj"
set +e
outB=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMPB/hub" bash "$SYNC_SH" 2>&1)
rcB=$?
set -e
if [ "$rcB" -ne 0 ]; then echo "FAIL(B): scan exit $rcB"; echo "$outB"; exit 1; fi
if ! git -C "$TMPB/hub" ls-tree -r --name-only HEAD | grep -qxF "$REL_PFX/skills/x/tracked.md"; then
  echo "FAIL(B): the tracked add did not commit"; echo "$outB"; exit 1
fi
# Silence at N==0: the summary line must NOT appear.
if echo "$outB" | grep -qF "$SUMMARY"; then
  echo "FAIL(B): summary count printed when nothing was skipped"; echo "$outB"; exit 1
fi

echo "PASS: test_scan_skips_gitignored"
