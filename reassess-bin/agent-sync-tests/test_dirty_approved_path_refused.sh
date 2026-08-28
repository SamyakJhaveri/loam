#!/usr/bin/env bash
# test_dirty_approved_path_refused.sh
# CX-3 (High): if the user continues past the global dirty-hub warning and an
# APPROVED path's hub copy carries PRE-SCAN uncommitted edits, the engine installs
# over that WIP; declining the commit then runs rollback_path -> `checkout HEAD`,
# which restores HEAD and DESTROYS the pre-scan WIP while the decline message
# claims "hub restored". The fix refuses a dirty approved path per-path (warn +
# skip, like the group-5 modified-prune guard) so it is never installed or rolled
# back, and the WIP survives both the skip and a mixed-batch decline.
#   RED (unmodified engine): the change installs over S.md, decline `checkout HEAD`
#      wipes the PRE-SCAN WIP line.
#   GREEN: S.md is warned + skipped, WIP intact; the clean add is installed then
#      rolled back on decline; index clean.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
CHG="skills/x/S.md"
ADD="skills/x/new.md"

# Hub: a committed change-target file (no base record -> legacy overwrite regime).
mkdir -p "$HUB_SETUP/skills/x"
printf 'hub original\n' > "$HUB_SETUP/$CHG"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)
echo "session=3" > "$TMP/hub/.sync-state"

# Project: a differing S.md (=> offered as a change) + a brand-new add, both travels.
mkdir -p "$TMP/proj/.claude/skills/x" "$TMP/proj/.claude/reference"
printf 'project version\n' > "$TMP/proj/.claude/$CHG"
printf 'brand new\n'       > "$TMP/proj/.claude/$ADD"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Pre-scan: dirty the hub change-target with uncommitted WIP.
printf 'PRE-SCAN WIP\n' >> "$HUB_SETUP/$CHG"

# Sanity: the WIP is present and the hub file is dirty vs HEAD.
if ! grep -q "PRE-SCAN WIP" "$HUB_SETUP/$CHG"; then echo "FIXTURE BUG: WIP not written"; exit 1; fi
if git -C "$TMP/hub" diff --quiet -- "cultivation/marketplace/sam-cc-setup/$CHG"; then
  echo "FIXTURE BUG: hub change-target is not dirty vs HEAD"; exit 1
fi

cd "$TMP/proj"
# stdin: y (continue past dirty-hub warning), y (approve the add), y (approve the
# change), n (decline the commit).
set +e
out=$(printf 'y\ny\ny\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# Non-vacuous: the change path was genuinely in play (offered).
if ! echo "$out" | grep -qF "$CHG"; then
  echo "FAIL: the change path $CHG was never surfaced (test would be vacuous)"; echo "$out"; exit 1
fi

# Assertion 1 (RED->GREEN flip): the pre-scan WIP on the dirty approved path survives.
if ! grep -q "PRE-SCAN WIP" "$HUB_SETUP/$CHG"; then
  echo "FAIL: pre-scan WIP on the approved path was DESTROYED (installed-over + checkout HEAD)"
  echo "--- hub $CHG now ---"; cat "$HUB_SETUP/$CHG"; echo "--- out ---"; echo "$out"; exit 1
fi

# Assertion 2: the dirty path was warned + skipped (never installed).
if ! echo "$out" | grep -qiF "skipped ($CHG has uncommitted edits"; then
  echo "FAIL: no per-path skip warning for the dirty approved path"; echo "$out"; exit 1
fi

# Assertion 3: content is exactly the pre-scan state (hub original + WIP), i.e. the
# project version was never installed over it.
if grep -q "project version" "$HUB_SETUP/$CHG"; then
  echo "FAIL: the project version was installed over a dirty approved path"; cat "$HUB_SETUP/$CHG"; exit 1
fi

# Assertion 4: the clean add was rolled back on decline (mixed-batch decline works).
if [ -e "$HUB_SETUP/$ADD" ]; then
  echo "FAIL: the clean add was not rolled back on decline"; exit 1
fi

# Assertion 5: the hub index is clean (no staged residue -> next scan not wedged).
if [ -n "$(git -C "$TMP/hub" diff --cached --name-only)" ]; then
  echo "FAIL: hub index has staged residue after decline"; git -C "$TMP/hub" diff --cached --name-only; exit 1
fi

# Assertion 6: the decline reported the rollback.
if ! echo "$out" | grep -qiF "restored"; then
  echo "FAIL: decline message did not report the rollback"; echo "$out"; exit 1
fi

echo "PASS: test_dirty_approved_path_refused"
