#!/usr/bin/env bash
# test_symlinked_claude_retarget.sh
# CX-2 (High): the M7 commit-check resolves the .claude symlink and statuses only
# the RESOLVED TARGET. So an UNCOMMITTED RETARGET of the .claude symlink itself -
# pointed at a different, clean, committed in-repo tree - is invisible: the target
# it now names is clean, the symlink-blob change is never statused, and the scan
# proceeds to sync a tree the project has not committed to. The fix statuses BOTH
# the literal `.claude` path AND the resolved target (:(literal) pathspecs), so the
# uncommitted symlink retarget is seen and the scan refuses.
#   RED (statuses only the resolved target): the retarget passes, scan proceeds.
#   GREEN: the uncommitted symlink retarget is refused.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Hub.
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HUB_SETUP"; echo keep > "$HUB_SETUP/keep.md"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
echo "session=1" > "$TMP/hub/.sync-state"

# Project: two clean committed .claude trees, .claude -> seed/.claude committed.
mkdir -p "$TMP/proj/seed/.claude/skills/x" "$TMP/proj/seed2/.claude/skills/x"
echo "committed A" > "$TMP/proj/seed/.claude/skills/x/S.md"
echo "committed B (a DIFFERENT tree the project never chose to sync)" \
  > "$TMP/proj/seed2/.claude/skills/x/S.md"
(cd "$TMP/proj" && ln -s seed/.claude .claude && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Sanity: .claude is a symlink and the tree is clean at commit time.
[ -L "$TMP/proj/.claude" ] || { echo "FIXTURE BUG: .claude is not a symlink"; exit 1; }
if [ -n "$(git -C "$TMP/proj" status --porcelain)" ]; then
  echo "FIXTURE BUG: project not clean at commit time"; git -C "$TMP/proj" status --porcelain; exit 1
fi

# Now RETARGET the symlink to the OTHER clean committed tree, WITHOUT committing.
# The new target (seed2/.claude) is itself clean/committed; only the symlink blob
# is uncommitted.
rm "$TMP/proj/.claude"
ln -s seed2/.claude "$TMP/proj/.claude"

# Sanity: the retarget is the ONLY uncommitted change and its target is clean.
if [ -z "$(git -C "$TMP/proj" status --porcelain -- .claude)" ]; then
  echo "FIXTURE BUG: the symlink retarget did not register as uncommitted"; exit 1
fi
if [ -n "$(git -C "$TMP/proj" status --porcelain -- seed2/.claude)" ]; then
  echo "FIXTURE BUG: the retarget target seed2/.claude is not clean"; exit 1
fi

cd "$TMP/proj"
set +e
out=$(printf 'n\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Assertion (RED->GREEN flip): the scan must REFUSE the uncommitted symlink retarget.
if ! echo "$out" | grep -qi "uncommitted changes"; then
  echo "FAIL: an uncommitted .claude retarget to a clean tree was NOT refused (CX-2 bypass)"
  echo "rc=$rc"; echo "$out"; exit 1
fi
if [ "$rc" -eq 0 ]; then
  echo "FAIL: scan exited 0 despite an uncommitted .claude symlink retarget"; echo "$out"; exit 1
fi

echo "PASS: test_symlinked_claude_retarget"
