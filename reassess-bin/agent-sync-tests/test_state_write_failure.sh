#!/usr/bin/env bash
T=$(printf '\t')   # ledger project-id delimiter (M3)
# test_state_write_failure.sh
# Codex pass 2 Critical C4: a failed .sync-state / refs/agent-sync/bases write
# must stop the scan before it commits, so files are never committed with their
# synced:/base: ledger records lost.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
ERR="Error: could not persist .sync-state or refs/agent-sync/bases; hub left uncommitted"

# ---- Leg 1: the .sync-state write fails (hub root not writable, so the temp
# file cannot be created). Skipped as root, which ignores directory modes. ----
if [ "$(id -u)" -eq 0 ]; then echo "SKIP(1): running as root, directory modes not enforced"; else
T1="$(mktemp -d)"
H1="$T1/hub"; HS1="$H1/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HS1/skills/keep"; echo keep > "$HS1/skills/keep/SKILL.md"
(cd "$H1" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
mkdir -p "$T1/proj/.claude/skills/new"; echo new > "$T1/proj/.claude/skills/new/SKILL.md"
(cd "$T1/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
chmod 555 "$H1"   # block the state temp-file creation in the hub root
CB=$(git -C "$H1" rev-list --count HEAD)
cd "$T1/proj"
set +e; out1=$(printf 'y\n\n' | SAM_CC_HUB_REPO="$H1" bash "$SYNC_SH" 2>&1); rc1=$?; set -e
if [ "$rc1" -eq 0 ]; then echo "FAIL(1): scan exited 0; expected abort on state-write failure"; echo "$out1"; chmod 755 "$H1"; rm -rf "$T1"; exit 1; fi
if ! echo "$out1" | grep -qF "$ERR"; then echo "FAIL(1): missing persist-failure Error line"; echo "$out1"; chmod 755 "$H1"; rm -rf "$T1"; exit 1; fi
if [ "$(git -C "$H1" rev-list --count HEAD)" != "$CB" ]; then echo "FAIL(1): hub committed despite state-write failure"; chmod 755 "$H1"; rm -rf "$T1"; exit 1; fi
if [ ! -f "$HS1/skills/new/SKILL.md" ]; then echo "FAIL(1): new file not installed into hub working tree"; chmod 755 "$H1"; rm -rf "$T1"; exit 1; fi
chmod 755 "$H1"; rm -rf "$T1"
fi

# ---- Leg 2: the refs/agent-sync/bases update fails (a file blocks the ref dir) ----
T2="$(mktemp -d)"
H2="$T2/hub"; HS2="$H2/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HS2/skills/foo"; echo shared > "$HS2/skills/foo/SKILL.md"
(cd "$H2" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
mkdir -p "$T2/proj/.claude/skills/foo"; echo shared > "$T2/proj/.claude/skills/foo/SKILL.md"
(cd "$T2/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
mkdir -p "$H2/.git/refs"; printf 'blocker\n' > "$H2/.git/refs/agent-sync"   # block the ref dir
cd "$T2/proj"
set +e; out2=$(SAM_CC_HUB_REPO="$H2" bash "$SYNC_SH" --bootstrap-bases 2>&1); rc2=$?; set -e
if [ "$rc2" -eq 0 ]; then echo "FAIL(2): bootstrap exited 0; expected abort on ref-update failure"; echo "$out2"; rm -rf "$T2"; exit 1; fi
if ! echo "$out2" | grep -qF "$ERR"; then echo "FAIL(2): missing persist-failure Error line"; echo "$out2"; rm -rf "$T2"; exit 1; fi
rm -rf "$T2"

# ---- Leg 3 (Codex pass 3 Critical): a planted symlink at the old predictable
# temp path .sync-state.tmp must never be followed; the state goes through a
# mktemp name and the victim file is untouched. ----
T3="$(mktemp -d)"
H3="$T3/hub"; HS3="$H3/cultivation/marketplace/sam-cc-setup"
mkdir -p "$HS3/skills/keep"; echo keep > "$HS3/skills/keep/SKILL.md"
(cd "$H3" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
mkdir -p "$T3/proj/.claude/skills/keep"; echo keep > "$T3/proj/.claude/skills/keep/SKILL.md"
(cd "$T3/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
echo victim > "$T3/victim.txt"
ln -s "$T3/victim.txt" "$H3/.sync-state.tmp"
cd "$T3/proj"
# The planted symlink is an untracked hub file, so answer y to the dirty-hub prompt.
set +e; out3=$(printf 'y\n' | SAM_CC_HUB_REPO="$H3" bash "$SYNC_SH" 2>&1); rc3=$?; set -e
if [ "$rc3" -ne 0 ]; then echo "FAIL(3): scan exit $rc3"; echo "$out3"; rm -rf "$T3"; exit 1; fi
if [ "$(cat "$T3/victim.txt")" != "victim" ]; then echo "FAIL(3): state write followed the planted .sync-state.tmp symlink and overwrote the victim"; rm -rf "$T3"; exit 1; fi
if [ -L "$H3/.sync-state" ]; then echo "FAIL(3): .sync-state became a symlink (the planted temp was renamed into place)"; rm -rf "$T3"; exit 1; fi
if ! grep -qE "^session:[^$T]*${T}1\$" "$H3/.sync-state"; then echo "FAIL(3): state not written"; rm -rf "$T3"; exit 1; fi
rm -rf "$T3"

echo "PASS: test_state_write_failure"
