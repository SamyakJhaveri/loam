#!/usr/bin/env bash
# test_untracked_nonignored_refused.sh
# 8b Item 2 TRIPWIRE. The tracked-only enumeration filter is safe ONLY because the
# :86 uncommitted-.claude guard already REFUSES the whole run when a NON-ignored
# file under .claude is uncommitted: `git status --porcelain` reports it as `??`,
# so the run aborts upstream and the filter never sees it. Thus within the
# reachable state space "tracked-only" == "exclude gitignored" and the filter
# cannot silently drop a legitimately-new project file.
# This test LOCKS that guard. It asserts refusal on BOTH the normal scan path AND
# the --bootstrap-bases path (:86 is shared and not gated on bootstrap). If :86 is
# ever loosened, this fails and the filter's safety argument must be revisited.
# (The existing test_uncommitted_project_refused.sh covers only a MODIFIED tracked
# file, i.e. ` M`, not the untracked `??` case - hence this focused test.)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Hub: committed plugin tree.
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/x"
echo "keep" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/x/keep.md"
(cd "$TMP/hub" && git init -q \
  && git -c user.email=t@t -c user.name=t add -A \
  && git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: .claude committed, then add an UNTRACKED, NON-ignored new file under it.
# No .gitignore, so the file is a plain `??` untracked path.
mkdir -p "$TMP/proj/.claude/skills/x"
echo "committed" > "$TMP/proj/.claude/skills/x/tracked.md"
(cd "$TMP/proj" && git init -q \
  && git -c user.email=t@t -c user.name=t add -A \
  && git -c user.email=t@t -c user.name=t commit -q -m init)
echo "brand new, not ignored" > "$TMP/proj/.claude/skills/x/newfile.md"

# Sanity: the new file is genuinely untracked AND not ignored (a `??` in porcelain).
cd "$TMP/proj"
porc=$(git status --porcelain -- ":(literal).claude")
if ! printf '%s\n' "$porc" | grep -qE '^\?\? .*newfile\.md$'; then
  echo "FIXTURE-BUG: newfile.md is not an untracked ?? path"; echo "$porc"; exit 1
fi
if git check-ignore -q .claude/skills/x/newfile.md; then
  echo "FIXTURE-BUG: newfile.md is gitignored; the test must use a NON-ignored file"; exit 1
fi

assert_refused() {  # $1 = label, $2... = scan args
  local label="$1"; shift
  set +e
  local out rc
  out=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" "$@" 2>&1 >/dev/null)
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then
    echo "FAIL($label): scan exit 0; an untracked non-ignored .claude file must be refused"; echo "$out"; exit 1
  fi
  if ! echo "$out" | grep -qi 'uncommitted'; then
    echo "FAIL($label): refusal did not mention 'uncommitted'"; echo "$out"; exit 1
  fi
  # The new file must never reach the hub.
  if git -C "$TMP/hub" ls-tree -r --name-only HEAD | grep -qF 'newfile.md'; then
    echo "FAIL($label): the untracked file reached the hub"; exit 1
  fi
}

assert_refused "scan"
assert_refused "bootstrap" --bootstrap-bases

echo "PASS: test_untracked_nonignored_refused"
