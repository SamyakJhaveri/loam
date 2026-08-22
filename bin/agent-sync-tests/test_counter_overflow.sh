#!/usr/bin/env bash
# test_counter_overflow.sh
# Codex pass 2 High H5: bound the decimal counters. The session= value and a
# defer ask_at accept only 1-9 digits below 900000000; a longer value overflows
# Bash arithmetic (9999999999999999999 wraps negative). SAM_CC_DEFER_SESSIONS is
# validated at startup.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"

mk_repo_pair() {  # $1 = root; a hub + project already in sync (no changes)
  local root="$1" hub_setup="$1/hub/cultivation/marketplace/sam-cc-setup"
  mkdir -p "$hub_setup/skills/keep"; echo keep > "$hub_setup/skills/keep/SKILL.md"
  (cd "$root/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
  mkdir -p "$root/proj/.claude/skills/keep"; echo keep > "$root/proj/.claude/skills/keep/SKILL.md"
  (cd "$root/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
}

# ---- Leg 1: over-long session + defer counters are rejected ----
T1="$(mktemp -d)"
mk_repo_pair "$T1"
{ echo 'session=9999999999999999999'; echo 'defer:skills/x/SKILL.md:99999999999999999999'; } > "$T1/hub/.sync-state"
S1="$T1/hub/.sync-state"
cd "$T1/proj"
set +e; out1=$(printf 'n\n' | SAM_CC_HUB_REPO="$T1/hub" bash "$SYNC_SH" 2>&1); rc1=$?; set -e
if [ "$rc1" -ne 0 ]; then echo "FAIL(1): scan exit $rc1"; echo "$out1"; rm -rf "$T1"; exit 1; fi
if ! echo "$out1" | grep -qF "warning: ignoring malformed .sync-state session: 9999999999999999999"; then
  echo "FAIL(1): no over-long session warning"; echo "$out1"; rm -rf "$T1"; exit 1; fi
if ! echo "$out1" | grep -qF "warning: ignoring malformed .sync-state key: skills/x/SKILL.md"; then
  echo "FAIL(1): no over-long defer-counter warning"; echo "$out1"; rm -rf "$T1"; exit 1; fi
if ! grep -qx 'session=1' "$S1"; then echo "FAIL(1): session not reset to 1"; cat "$S1"; rm -rf "$T1"; exit 1; fi
if grep -q 'defer:' "$S1"; then echo "FAIL(1): over-long defer record persisted"; cat "$S1"; rm -rf "$T1"; exit 1; fi
rm -rf "$T1"

# ---- Leg 1b: a session at the ceiling (999999999, 9 digits) is malformed too ----
T1b="$(mktemp -d)"
mk_repo_pair "$T1b"
echo 'session=999999999' > "$T1b/hub/.sync-state"
cd "$T1b/proj"
set +e; o1b=$(printf 'n\n' | SAM_CC_HUB_REPO="$T1b/hub" bash "$SYNC_SH" 2>&1); r1b=$?; set -e
if [ "$r1b" -ne 0 ]; then echo "FAIL(1b): scan exit $r1b"; echo "$o1b"; rm -rf "$T1b"; exit 1; fi
if ! echo "$o1b" | grep -qF "warning: ignoring malformed .sync-state session: 999999999"; then
  echo "FAIL(1b): a session at the ceiling was accepted"; echo "$o1b"; rm -rf "$T1b"; exit 1; fi
if ! grep -qx 'session=1' "$T1b/hub/.sync-state"; then echo "FAIL(1b): session not reset to 1"; rm -rf "$T1b"; exit 1; fi
rm -rf "$T1b"

# ---- Leg 2: SAM_CC_DEFER_SESSIONS is validated at startup ----
T2="$(mktemp -d)"
mk_repo_pair "$T2"
cd "$T2/proj"
DERR="Error: SAM_CC_DEFER_SESSIONS must be a decimal number of 1 to 6 digits"
set +e; o2a=$(SAM_CC_DEFER_SESSIONS=99999999999999999999 SAM_CC_HUB_REPO="$T2/hub" bash "$SYNC_SH" 2>&1); r2a=$?; set -e
if [ "$r2a" -eq 0 ]; then echo "FAIL(2a): over-long SAM_CC_DEFER_SESSIONS accepted"; echo "$o2a"; rm -rf "$T2"; exit 1; fi
if ! echo "$o2a" | grep -qF "$DERR"; then echo "FAIL(2a): missing SAM_CC_DEFER_SESSIONS Error"; echo "$o2a"; rm -rf "$T2"; exit 1; fi
set +e; o2b=$(SAM_CC_DEFER_SESSIONS=abc SAM_CC_HUB_REPO="$T2/hub" bash "$SYNC_SH" 2>&1); r2b=$?; set -e
if [ "$r2b" -eq 0 ]; then echo "FAIL(2b): non-decimal SAM_CC_DEFER_SESSIONS accepted"; echo "$o2b"; rm -rf "$T2"; exit 1; fi
if ! echo "$o2b" | grep -qF "$DERR"; then echo "FAIL(2b): missing SAM_CC_DEFER_SESSIONS Error for abc"; echo "$o2b"; rm -rf "$T2"; exit 1; fi
set +e; o2c=$(SAM_CC_DEFER_SESSIONS=1234567 SAM_CC_HUB_REPO="$T2/hub" bash "$SYNC_SH" 2>&1); r2c=$?; set -e
if [ "$r2c" -eq 0 ]; then echo "FAIL(2c): 7-digit SAM_CC_DEFER_SESSIONS accepted"; echo "$o2c"; rm -rf "$T2"; exit 1; fi
rm -rf "$T2"

echo "PASS: test_counter_overflow"
