#!/usr/bin/env bash
# test_claude_status_failure_refused.sh
# H4 (Codex round 1): the :86 uncommitted-.claude guard discards `git status`'s
# exit code - `[ -n "$(git status ... 2>/dev/null)" ]`. If git status FAILS, the
# substitution yields "" and -n "" reads the tree as CLEAN, so the guard fails
# OPEN and the scan proceeds on an unverified tree. This is the guard Item 2's
# tracked-only safety argument rests on, so it must fail CLOSED: refuse on ANY
# nonzero git-status exit, with a message DISTINCT from the "uncommitted changes"
# one.
#
# Failure is induced deterministically by CORRUPTING the project's index:
# `git rev-parse --show-toplevel` (:19) never reads the index and resolve-claude
# (:74) is filesystem-only, so :86's `git status` is the first index read and it
# exits 128. The tripwire covers BOTH the scan and --bootstrap-bases paths (the
# guard is not gated on bootstrap).
#
# RED note: the CURRENT engine also has an ls-files tracked-set guard (Item 2,
# ~:578) that fails closed on the same corrupt index, so the pre-fix run still
# exits nonzero - but with the Item 2 "could not list git-tracked files" message,
# NOT the H4 "could not check" one, proving :86 fell through (failed open). This
# test asserts the H4 message IS present AND the Item 2 ls-files message is ABSENT
# (early refusal at :86), so it fails for exactly that reason pre-fix.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
H4_MSG="could not check the project's .claude for uncommitted changes"
ITEM2_MSG="could not list git-tracked files"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Hub: committed plugin tree.
mkdir -p "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/x"
echo "keep" > "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/x/keep.md"
(cd "$TMP/hub" && git init -q \
  && git -c user.email=t@t -c user.name=t add -A \
  && git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: .claude committed, then CORRUPT the index so git status fails.
mkdir -p "$TMP/proj/.claude/skills/x"
echo "committed" > "$TMP/proj/.claude/skills/x/tracked.md"
(cd "$TMP/proj" && git init -q \
  && git -c user.email=t@t -c user.name=t add -A \
  && git -c user.email=t@t -c user.name=t commit -q -m init)
printf 'garbage-not-an-index' > "$TMP/proj/.git/index"

# Sanity: rev-parse still works, status is genuinely broken.
if ! git -C "$TMP/proj" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "FIXTURE-BUG: rev-parse should still succeed with a corrupt index"; exit 1
fi
if git -C "$TMP/proj" status --porcelain >/dev/null 2>&1; then
  echo "FIXTURE-BUG: git status should fail on the corrupt index"; exit 1
fi

cd "$TMP/proj"

assert_h4_refusal() {  # $1 = label, $2... = scan args
  local label="$1"; shift
  set +e
  local out rc
  out=$(SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" "$@" 2>&1)
  rc=$?
  set -e
  # Must refuse (nonzero) - true both pre and post fix, but the reason differs.
  if [ "$rc" -eq 0 ]; then
    echo "FAIL($label): scan exit 0; a failed .claude status must be refused"; echo "$out"; exit 1
  fi
  # The RED: it must refuse AT :86 with the H4 message, not fall through to the
  # Item 2 ls-files guard.
  if ! echo "$out" | grep -qF "$H4_MSG"; then
    echo "FAIL($label): :86 failed open - no H4 'could not check' message (fell through)"; echo "$out"; exit 1
  fi
  if echo "$out" | grep -qF "$ITEM2_MSG"; then
    echo "FAIL($label): refusal came from the Item 2 ls-files guard, not :86 (fell through)"; echo "$out"; exit 1
  fi
  # The corrupted project must never reach the hub.
  if git -C "$TMP/hub" ls-tree -r --name-only HEAD | grep -qF 'tracked.md'; then
    echo "FAIL($label): a file was promoted despite the status failure"; exit 1
  fi
}

assert_h4_refusal "scan"
assert_h4_refusal "bootstrap" --bootstrap-bases

echo "PASS: test_claude_status_failure_refused"
