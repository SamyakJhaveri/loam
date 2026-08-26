#!/usr/bin/env bash
# test_upgrading_reminder.sh
# Wave 3 (8b Item 1): a soft provenance reminder. Every promoted change is meant
# to get one UPGRADING.md line (WHAT changed, WHY). At the commit step the scan
# must print a reminder when cultivation/marketplace/UPGRADING.md was NOT touched
# in this batch, and stay SILENT when it was. It is a reminder only: it never
# gates, never changes the exit code, never suppresses the commit.
# Two directions in one file:
#   A) UPGRADING.md untouched -> commit succeeds AND the reminder is printed.
#   B) UPGRADING.md touched   -> commit succeeds AND the reminder is absent.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
REL_PFX="cultivation/marketplace/sam-cc-setup"
REMINDER="UPGRADING.md was not updated in this batch"

# mk_hub <hubroot>: a committed hub with the plugin tree, a committed UPGRADING.md
# sibling, git identity, and a .gitignore for .sync-state.
mk_hub() {
  local hub="$1"
  mkdir -p "$hub/$REL_PFX/skills/x" "$hub/cultivation/marketplace"
  printf '.sync-state\n' > "$hub/.gitignore"
  echo "keep" > "$hub/$REL_PFX/keep.md"
  printf '# Upgrading\n\n(history)\n' > "$hub/cultivation/marketplace/UPGRADING.md"
  (cd "$hub" && git init -q && git config user.email t@t && git config user.name t \
    && git add -A && git commit -q -m init)
}

# mk_proj <projroot>: a committed project with one NEW .claude file to promote.
mk_proj() {
  local proj="$1"
  mkdir -p "$proj/.claude/skills/x"
  echo "new content" > "$proj/.claude/skills/x/new.md"
  (cd "$proj" && git init -q \
    && git -c user.email=t@t -c user.name=t add -A \
    && git -c user.email=t@t -c user.name=t commit -q -m init)
}

# ---------- Direction A: UPGRADING.md untouched -> reminder present ----------
TMPA="$(mktemp -d)"
trap 'rm -rf "$TMPA" "${TMPB:-}"' EXIT
mk_hub "$TMPA/hub"
mk_proj "$TMPA/proj"

cd "$TMPA/proj"
# stdin 'y\ny': approve the one offered add, then Y at the commit prompt; EOF
# drives the push prompt to its default N.
set +e
outA=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMPA/hub" bash "$SYNC_SH" 2>&1)
rcA=$?
set -e

if [ "$rcA" -ne 0 ]; then
  echo "FAIL(A): scan exit $rcA (expected a clean commit)"; echo "$outA"; exit 1
fi
if ! git -C "$TMPA/hub" ls-tree -r --name-only HEAD | grep -qxF "$REL_PFX/skills/x/new.md"; then
  echo "FAIL(A): the promoted add did not commit"; echo "$outA"; exit 1
fi
# The RED assertion: the reminder must fire when UPGRADING.md was not touched.
if ! echo "$outA" | grep -qF "$REMINDER"; then
  echo "FAIL(A): expected the UPGRADING.md reminder, none printed"; echo "$outA"; exit 1
fi

# ---------- Direction B: UPGRADING.md touched -> reminder absent ----------
TMPB="$(mktemp -d)"
mk_hub "$TMPB/hub"
mk_proj "$TMPB/proj"
# Touch UPGRADING.md in the hub worktree (unstaged) BEFORE the run. The scan's
# dirty-hub prompt warns and continues on our 'y'.
printf '\n- new.md: added (why: test)\n' >> "$TMPB/hub/cultivation/marketplace/UPGRADING.md"

cd "$TMPB/proj"
# stdin: 'y' past the dirty-hub warning, 'y' to approve the add, 'y' to commit;
# EOF -> push default N.
set +e
outB=$(printf 'y\ny\ny\n' | SAM_CC_HUB_REPO="$TMPB/hub" bash "$SYNC_SH" 2>&1)
rcB=$?
set -e

if [ "$rcB" -ne 0 ]; then
  echo "FAIL(B): scan exit $rcB (expected a clean commit)"; echo "$outB"; exit 1
fi
if ! git -C "$TMPB/hub" ls-tree -r --name-only HEAD | grep -qxF "$REL_PFX/skills/x/new.md"; then
  echo "FAIL(B): the promoted add did not commit"; echo "$outB"; exit 1
fi
# The silent-direction assertion: no reminder when UPGRADING.md was touched.
if echo "$outB" | grep -qF "$REMINDER"; then
  echo "FAIL(B): reminder fired even though UPGRADING.md was touched"; echo "$outB"; exit 1
fi

echo "PASS: test_upgrading_reminder"
