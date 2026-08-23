#!/usr/bin/env bash
# test_base_record_failure.sh
# Codex pass-4 High (item 2): a failed `hash-object -w` must NOT be swallowed. The
# base is computed BEFORE install; a compute failure fails the item, so no synced:
# line is ever written without a matching base: (a later scan would resolve that by
# a destructive overwrite).
#
# Injection (root-safe, deterministic, per-blob): compute the target blob's sha with
# `git hash-object FILE` (no -w) and plant a REGULAR FILE at .git/objects/${sha:0:2}.
# git must create/enter that 2-hex directory to write the loose object; a regular
# file there makes the write fail ("unable to create temporary file: Not a
# directory") - and mkdir-over-a-file fails even for root, so there is no chmod
# root-bypass and no sha-prefix lottery. Only that one blob fails; every other object
# write (different prefix) still works, so git add / commit run normally for them.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

poison() {  # $1=hub repo root, $2=absolute path to the project file whose write must fail
  local hub="$1" file="$2" sha pdir
  sha=$(git -C "$hub" hash-object "$file")
  pdir="$hub/.git/objects/${sha:0:2}"
  if [ -e "$pdir" ]; then echo "PROBE-BUG: poison prefix ${sha:0:2} already exists in $hub"; exit 1; fi
  printf 'x' > "$pdir"
  # Precondition: the exact write the scan will attempt MUST now fail.
  if git -C "$hub" hash-object -w "$file" >/dev/null 2>&1; then
    echo "PROBE-BUG: injection did not take for $file"; exit 1; fi
}

# ---- Leg 1: main install path - a two-file batch; earlier item records, later fails ----
H="$TMP/hub"; HS="$H/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HS/skills/keep"
echo "keepcontent" > "$HS/skills/keep/SKILL.md"
(cd "$H" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
HEAD_BEFORE=$(git -C "$H" rev-parse HEAD)

mkdir -p "$TMP/proj/.claude/skills/keep" "$TMP/proj/.claude/skills/aaa" "$TMP/proj/.claude/skills/zzz"
echo "keepcontent"       > "$TMP/proj/.claude/skills/keep/SKILL.md"   # identical -> no diff
echo "aaa-novel-content" > "$TMP/proj/.claude/skills/aaa/SKILL.md"    # add, not poisoned
echo "zzz-novel-content" > "$TMP/proj/.claude/skills/zzz/SKILL.md"    # add, poisoned
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

# Poison ONLY skills/zzz's blob; skills/aaa (rsync-ordered first) must still record.
poison "$H" "$TMP/proj/.claude/skills/zzz/SKILL.md"

STATE="$H/.sync-state"
cd "$TMP/proj"
set +e
out=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$H" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# Sanity only (both engines exit non-zero: post-fix aborts at zzz; pre-fix at git add).
if [ "$rc" -eq 0 ]; then echo "FAIL(1): scan exited 0; expected a non-zero fail-closed abort"; echo "$out"; exit 1; fi
# Earlier item genuinely recorded IN THIS BATCH (resolves option A): aaa installed + synced: + base:.
if [ ! -e "$HS/skills/aaa/SKILL.md" ]; then echo "FAIL(1): earlier item skills/aaa was not installed"; echo "$out"; exit 1; fi
if ! grep -qE "^synced:skills/aaa/SKILL.md:" "$STATE"; then echo "FAIL(1): earlier item skills/aaa has no synced: record"; cat "$STATE"; exit 1; fi
if ! grep -qE "^base:skills/aaa/SKILL.md:" "$STATE"; then echo "FAIL(1): earlier item skills/aaa has no base: record"; cat "$STATE"; exit 1; fi
# Discriminator 1 (install): pre-fix installs zzz before the swallowed failure.
if [ -e "$HS/skills/zzz" ]; then echo "FAIL(1): skills/zzz was installed despite the failure"; exit 1; fi
# Discriminator 2 (ledger - the exact regression): pre-fix writes synced:zzz with no base:zzz.
if grep -qE "^synced:skills/zzz/SKILL.md:" "$STATE"; then echo "FAIL(1): synced: written for the failed path (base-less synced regression)"; cat "$STATE"; exit 1; fi
if grep -qE "^base:skills/zzz/SKILL.md:" "$STATE"; then echo "FAIL(1): base: written for the failed path"; cat "$STATE"; exit 1; fi
# Discriminator 3 (Error text): post-fix aborts BEFORE install; pre-fix never prints this.
if ! echo "$out" | grep -qF "aborting before install of skills/zzz/SKILL.md"; then echo "FAIL(1): no pre-install abort Error for skills/zzz"; echo "$out"; exit 1; fi
if ! echo "$out" | grep -qF "hash-object failed for skills/zzz/SKILL.md"; then echo "FAIL(1): no hash-object failure Error for skills/zzz"; echo "$out"; exit 1; fi
# No commit was made.
if [ "$(git -C "$H" rev-parse HEAD)" != "$HEAD_BEFORE" ]; then echo "FAIL(1): hub HEAD advanced (a commit was made)"; exit 1; fi

# ---- Leg 2: bootstrap fails closed on a compute failure ----
H2="$TMP/hub2"; HS2="$H2/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HS2/skills/shared"
echo "hubversion" > "$HS2/skills/shared/SKILL.md"
(cd "$H2" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

mkdir -p "$TMP/proj2/.claude/skills/shared"
echo "projversion" > "$TMP/proj2/.claude/skills/shared/SKILL.md"   # differs -> a write is needed
(cd "$TMP/proj2" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

STATE2="$H2/.sync-state"
echo "session=5" > "$STATE2"
poison "$H2" "$TMP/proj2/.claude/skills/shared/SKILL.md"
cd "$TMP/proj2"
set +e
out2=$(SAM_CC_HUB_REPO="$H2" bash "$SYNC_SH" --bootstrap-bases 2>&1 </dev/null)
rc2=$?
set -e

# Bootstrap makes no other object write, so exit code DOES discriminate here:
# pre-fix exits 0 (inflated count), post-fix exits 1 (fail closed).
if [ "$rc2" -ne 1 ]; then echo "FAIL(2): expected exit 1, got $rc2"; echo "$out2"; exit 1; fi
if ! echo "$out2" | grep -qF "hash-object failed for skills/shared/SKILL.md"; then echo "FAIL(2): no hash-object failure Error for skills/shared"; echo "$out2"; exit 1; fi
if ! echo "$out2" | grep -qF "bootstrap aborted"; then echo "FAIL(2): no bootstrap-aborted Error"; echo "$out2"; exit 1; fi
if echo "$out2" | grep -q 'bootstrap:'; then echo "FAIL(2): a success report was printed on failure"; echo "$out2"; exit 1; fi
if ! grep -qx 'session=5' "$STATE2"; then echo "FAIL(2): session not pinned to PRIOR"; cat "$STATE2"; exit 1; fi
if grep -qE "^base:skills/shared/SKILL.md:" "$STATE2"; then echo "FAIL(2): base recorded for the failed path"; cat "$STATE2"; exit 1; fi

echo "PASS: test_base_record_failure"
