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

# Codex pass-4 Medium (item 3): refuse - never roll over - when a DERIVED counter
# would cross the ceiling. Both CURRENT_SESSION (= session + 1) and the largest
# ask_at a defer could produce this run (= CURRENT_SESSION + DEFER_SESSIONS) are
# validated at derivation; a refusal leaves the ledger unchanged (A1).

# ---- Leg 3: session=899999999 refused (CURRENT_SESSION would be 900000000) ----
T3="$(mktemp -d)"; mk_repo_pair "$T3"
echo 'session=899999999' > "$T3/hub/.sync-state"
cd "$T3/proj"
set +e; o3=$(printf 'n\n' | SAM_CC_HUB_REPO="$T3/hub" bash "$SYNC_SH" 2>&1); r3=$?; set -e
if [ "$r3" -eq 0 ]; then echo "FAIL(3): session at ceiling-1 accepted (CURRENT would be 900000000)"; echo "$o3"; rm -rf "$T3"; exit 1; fi
if ! echo "$o3" | grep -qF "session counter at the ceiling"; then echo "FAIL(3): no ceiling Error"; echo "$o3"; rm -rf "$T3"; exit 1; fi
if ! grep -qx 'session=899999999' "$T3/hub/.sync-state"; then echo "FAIL(3): ledger advanced/rewritten despite refusal"; cat "$T3/hub/.sync-state"; rm -rf "$T3"; exit 1; fi
rm -rf "$T3"

# ---- Leg 4: session=899999998 + DEFER=2 refused (derived ask_at would be 900000001) ----
T4="$(mktemp -d)"; mk_repo_pair "$T4"
echo 'session=899999998' > "$T4/hub/.sync-state"
cd "$T4/proj"
set +e; o4=$(printf 'n\n' | SAM_CC_DEFER_SESSIONS=2 SAM_CC_HUB_REPO="$T4/hub" bash "$SYNC_SH" 2>&1); r4=$?; set -e
if [ "$r4" -eq 0 ]; then echo "FAIL(4): defer would derive ask_at 900000001 but the run was accepted"; echo "$o4"; rm -rf "$T4"; exit 1; fi
if ! echo "$o4" | grep -qF "session counter at the ceiling"; then echo "FAIL(4): no ceiling Error"; echo "$o4"; rm -rf "$T4"; exit 1; fi
if ! grep -qx 'session=899999998' "$T4/hub/.sync-state"; then echo "FAIL(4): ledger advanced despite refusal"; cat "$T4/hub/.sync-state"; rm -rf "$T4"; exit 1; fi
rm -rf "$T4"

# ---- Leg 5: session=899999997 + DEFER=1 proceeds; persists session=899999998 ----
T5="$(mktemp -d)"; mk_repo_pair "$T5"
echo 'session=899999997' > "$T5/hub/.sync-state"
cd "$T5/proj"
set +e; o5=$(printf 'n\n' | SAM_CC_DEFER_SESSIONS=1 SAM_CC_HUB_REPO="$T5/hub" bash "$SYNC_SH" 2>&1); r5=$?; set -e
if [ "$r5" -ne 0 ]; then echo "FAIL(5): valid near-ceiling session refused"; echo "$o5"; rm -rf "$T5"; exit 1; fi
if echo "$o5" | grep -qF "session counter at the ceiling"; then echo "FAIL(5): spurious ceiling Error on a valid session"; echo "$o5"; rm -rf "$T5"; exit 1; fi
if ! grep -qx 'session=899999998' "$T5/hub/.sync-state"; then echo "FAIL(5): session not advanced to 899999998"; cat "$T5/hub/.sync-state"; rm -rf "$T5"; exit 1; fi
rm -rf "$T5"

echo "PASS: test_counter_overflow"
