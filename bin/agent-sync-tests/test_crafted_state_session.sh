#!/usr/bin/env bash
T=$(printf '\t')   # ledger project-id delimiter (M3)
# test_crafted_state_session.sh
# Codex Critical C3: the session= value and a defer counter from .sync-state
# reach bash arithmetic - $((PRIOR_SESSION+1)) (line 141) and
# [ "$CURRENT_SESSION" -lt "$ask_at" ] (line 312). A non-decimal counter is
# always wrong; on older bash (<=5.2, incl. Linux CI) an array-subscript command
# substitution there EXECUTES. The fix validates decimal-only, warns, and drops.
#
# Leg 2 platform note (session=a[$(touch M)]):
#   - Linux bash <=5.2 (CI): current code EXECUTES the smuggled touch (marker created).
#   - macOS bash 5.3.15 (here): current code ABORTS at the arithmetic under set -u
#     (a: unbound variable), rc != 0.
#   Both are RED vs current code; after the fix the value is rejected at parse and
#   never reaches arithmetic (rc 0, no marker) on either platform.
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

# ---- Leg 1: non-decimal session + defer counter (reproducible everywhere) ----
T1="$(mktemp -d)"
mk_repo_pair "$T1"
{ echo 'session=7*7'; echo 'defer:skills/x/SKILL.md:0x41'; } > "$T1/hub/.sync-state"
S1="$T1/hub/.sync-state"
cd "$T1/proj"
set +e; out1=$(printf 'n\n' | SAM_CC_HUB_REPO="$T1/hub" bash "$SYNC_SH" 2>&1); rc1=$?; set -e
if [ "$rc1" -ne 0 ]; then echo "FAIL(1): scan exit $rc1"; echo "$out1"; rm -rf "$T1"; exit 1; fi
if ! echo "$out1" | grep -qF "warning: ignoring malformed .sync-state session: 7*7"; then
  echo "FAIL(1): no malformed-session warning"; echo "$out1"; rm -rf "$T1"; exit 1; fi
if ! echo "$out1" | grep -qF "warning: ignoring malformed .sync-state key: skills/x/SKILL.md"; then
  echo "FAIL(1): no malformed-key warning for the defer record"; echo "$out1"; rm -rf "$T1"; exit 1; fi
if ! grep -qE "^session:[^$T]*${T}1\$" "$S1"; then echo "FAIL(1): session not reset to 1 (current writes 50)"; cat "$S1"; rm -rf "$T1"; exit 1; fi
if grep -q 'defer:' "$S1"; then echo "FAIL(1): malformed defer record persisted"; cat "$S1"; rm -rf "$T1"; exit 1; fi
rm -rf "$T1"

# ---- Leg 2: array-subscript injection (platform-dependent RED) ----
T2="$(mktemp -d)"
mk_repo_pair "$T2"
MARK="$T2/pwned"
# The $(...) must stay LITERAL in the .sync-state file (that is the payload).
# shellcheck disable=SC2016
printf 'session=a[$(touch "%s")]\n' "$MARK" > "$T2/hub/.sync-state"
S2="$T2/hub/.sync-state"
cd "$T2/proj"
set +e; out2=$(printf 'n\n' | SAM_CC_HUB_REPO="$T2/hub" bash "$SYNC_SH" 2>&1); rc2=$?; set -e
if [ "$rc2" -ne 0 ]; then echo "FAIL(2): fixed scan must not abort on a crafted session (rc $rc2)"; echo "$out2"; rm -rf "$T2"; exit 1; fi
if [ -e "$MARK" ]; then echo "FAIL(2): session injection executed (marker created)"; echo "$out2"; rm -rf "$T2"; exit 1; fi
if ! echo "$out2" | grep -qF "warning: ignoring malformed .sync-state session:"; then
  echo "FAIL(2): no malformed-session warning"; echo "$out2"; rm -rf "$T2"; exit 1; fi
if ! grep -qE "^session:[^$T]*${T}1\$" "$S2"; then echo "FAIL(2): session not reset to 1"; cat "$S2"; rm -rf "$T2"; exit 1; fi
rm -rf "$T2"

echo "PASS: test_crafted_state_session"
