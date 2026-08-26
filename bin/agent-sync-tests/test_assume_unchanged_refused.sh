#!/usr/bin/env bash
# test_assume_unchanged_refused.sh
# H5 (Codex round 1): `git ls-files` membership proves a path is TRACKED, not that
# its worktree bytes are COMMITTED. A tracked file marked --assume-unchanged (a
# lowercase ls-files -v tag) or skip-worktree (S) is HIDDEN from `git status`, so
# the :86 guard does not refuse, yet its worktree bytes can differ from the index -
# and the scan would promote / base those UNCOMMITTED bytes. The engine must refuse
# fail-closed when any entry under .claude carries a non-`H` ls-files tag.
#
# Covers BOTH paths: the scan path (RED shows the divergent bytes actually PROMOTED
# into the hub) and the --bootstrap-bases path (RED shows the divergent bytes BASED
# in .sync-state). The guard runs before the bootstrap block, so one fix covers both.
set -euo pipefail
T=$(printf '\t')

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
REL_PFX="cultivation/marketplace/sam-cc-setup"
HUBFILE_REL="$REL_PFX/skills/x/tracked.md"

# mk_fixture <root>: hub with tracked.md="v1" committed; project with tracked.md
# committed "v1" then worktree diverged to "v2 divergent" and --assume-unchanged.
mk_fixture() {
  local root="$1"
  mkdir -p "$root/hub/$REL_PFX/skills/x"
  printf 'v1\n' > "$root/hub/$HUBFILE_REL"
  (cd "$root/hub" && git init -q \
    && git -c user.email=t@t -c user.name=t add -A \
    && git -c user.email=t@t -c user.name=t commit -q -m init)
  mkdir -p "$root/proj/.claude/skills/x"
  printf 'v1\n' > "$root/proj/.claude/skills/x/tracked.md"
  (cd "$root/proj" && git init -q \
    && git -c user.email=t@t -c user.name=t add -A \
    && git -c user.email=t@t -c user.name=t commit -q -m init)
  printf 'v2 divergent\n' > "$root/proj/.claude/skills/x/tracked.md"
  git -C "$root/proj" update-index --assume-unchanged .claude/skills/x/tracked.md
  # Sanity: status hides the change (the hole) AND ls-files -v tags it lowercase.
  if [ -n "$(git -C "$root/proj" status --porcelain -- ':(literal).claude')" ]; then
    echo "FIXTURE-BUG: assume-unchanged should hide the change from status"; exit 1
  fi
  if ! git -C "$root/proj" ls-files -v -- ':(literal).claude' | grep -q '^[a-z] '; then
    echo "FIXTURE-BUG: expected a lowercase assume-unchanged ls-files tag"; exit 1
  fi
}

# ---------- Scan path: divergent bytes must NOT be promoted ----------
A="$(mktemp -d)"
trap 'rm -rf "$A" "${B:-}"' EXIT
mk_fixture "$A"
cd "$A/proj"
set +e
outA=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$A/hub" bash "$SYNC_SH" 2>&1)
rcA=$?
set -e
HUB_NOW=$(git -C "$A/hub" show "HEAD:$HUBFILE_REL" 2>/dev/null || cat "$A/hub/$HUBFILE_REL")
# The RED (the HARM): the divergent uncommitted bytes must NOT reach the hub.
if printf '%s' "$HUB_NOW" | grep -q 'v2 divergent'; then
  echo "FAIL(scan): assume-unchanged worktree bytes (uncommitted) were promoted into the hub"; echo "rc=$rcA"; echo "$outA"; exit 1
fi
if [ "$rcA" -eq 0 ]; then
  echo "FAIL(scan): scan exit 0; an assume-unchanged .claude file must be refused"; echo "$outA"; exit 1
fi
if ! echo "$outA" | grep -qiE 'assume-unchanged|skip-worktree'; then
  echo "FAIL(scan): refusal did not name assume-unchanged/skip-worktree"; echo "$outA"; exit 1
fi

# ---------- Bootstrap path: divergent bytes must NOT be based ----------
B="$(mktemp -d)"
mk_fixture "$B"
echo "session=5" > "$B/hub/.sync-state"
cd "$B/proj"
set +e
outB=$(SAM_CC_HUB_REPO="$B/hub" bash "$SYNC_SH" --bootstrap-bases 2>&1)
rcB=$?
set -e
# The RED (the HARM): no base for the divergent file may be recorded.
if grep -qE "^base:[^$T]*${T}skills/x/tracked.md:" "$B/hub/.sync-state"; then
  echo "FAIL(bootstrap): a base was recorded for the assume-unchanged file"; cat "$B/hub/.sync-state"; echo "$outB"; exit 1
fi
if [ "$rcB" -eq 0 ]; then
  echo "FAIL(bootstrap): --bootstrap-bases exit 0; must refuse an assume-unchanged .claude file"; echo "$outB"; exit 1
fi
if ! echo "$outB" | grep -qiE 'assume-unchanged|skip-worktree'; then
  echo "FAIL(bootstrap): refusal did not name assume-unchanged/skip-worktree"; echo "$outB"; exit 1
fi

echo "PASS: test_assume_unchanged_refused"
