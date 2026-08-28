#!/usr/bin/env bash
# test_install_partial_failure.sh
# Codex High H3 + H2 (group 3): adds/changes install per-item via install_file
# (temp file in the destination dir, atomic rename). A mid-batch install failure
# prints "Error: install failed for <path>" and aborts with exit 1. Under H2
# pending-quarantine (A1) the synced:/base: records are held in PENDING_* and only
# written after a successful commit, so a mid-batch abort leaves earlier items
# INSTALLED-BUT-UNRECORDED (not recorded), later items neither installed nor
# recorded, and no leftover .sync-install.* temp file. cp -p keeps the +x bit.
#
# Failure injection: the hub has a regular FILE at skills/b. This does NOT make
# the current bulk rsync fail - rsync -a recovers by DELETING the file and
# creating the directory, so it installs all three (a, b, c), records them, and
# exits 0 (a read-only directory is bypassed the same way: rsync -a resets the
# dir mode from the source and installs anyway). It is the FIXED install_file
# that fails at b: its `mkdir -p "$(dirname dst)"` cannot make a directory where
# a file exists, so b's install errors and the scan aborts with a installed and
# recorded, b and c neither installed nor recorded. So this test REDs against the
# current engine via the exit-0 assertion below and GREENs against the fix.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
A="skills/a/SKILL.md"
B="skills/b/SKILL.md"
C="skills/c/SKILL.md"

# Hub: one committed file plus a FILE at skills/b (the type-conflict obstacle for
# skills/b/SKILL.md); none of a/b/c's own files present.
mkdir -p "$HUB_SETUP/skills"
echo "seed" > "$HUB_SETUP/seed.md"
echo "i am a file, not a directory" > "$HUB_SETUP/skills/b"
(cd "$TMP/hub" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: three new files a < b < c. a is executable (+x leg).
mkdir -p "$TMP/proj/.claude/skills/a" "$TMP/proj/.claude/skills/b" "$TMP/proj/.claude/skills/c"
printf '#!/bin/sh\necho a\n' > "$TMP/proj/.claude/$A"; chmod 755 "$TMP/proj/.claude/$A"
echo "b content" > "$TMP/proj/.claude/$B"
echo "c content" > "$TMP/proj/.claude/$C"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"

# y/y/y: approve all three adds; the install loop fails on b before the commit prompt.
set +e
out=$(printf 'y\ny\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -eq 0 ]; then echo "FAIL: scan exited 0; expected a non-zero install abort"; echo "$out"; exit 1; fi

# The brief's mandated failure message printed for the failing item.
if ! echo "$out" | grep -q "Error: install failed for $B"; then
  echo "FAIL: missing mandated 'Error: install failed for $B' message"; echo "$out"; exit 1
fi

# a installed (install writes to the worktree) but NOT recorded: H2 pending-
# quarantine (A1) discards the pending synced:/base: on a mid-batch abort, so a is
# installed-but-unrecorded (surfaced by the dirty-hub warning, healed by --bootstrap-bases).
if [ ! -f "$HUB_SETUP/$A" ]; then echo "FAIL: a not installed"; echo "$out"; exit 1; fi
if grep -q "synced:$A:" "$STATE"; then echo "FAIL: a recorded synced: despite mid-batch abort (A1: expected installed-but-unrecorded)"; cat "$STATE"; exit 1; fi
if grep -q "base:$A:" "$STATE"; then echo "FAIL: a recorded base: despite mid-batch abort (A1: expected installed-but-unrecorded)"; cat "$STATE"; exit 1; fi

# +x leg: a arrived executable.
if [ ! -x "$HUB_SETUP/$A" ]; then echo "FAIL: a lost its executable bit"; exit 1; fi

# b and c neither recorded nor (for c) installed.
for rel in "$B" "$C"; do
  if grep -q "synced:$rel:" "$STATE"; then echo "FAIL: synced: record leaked for $rel"; cat "$STATE"; exit 1; fi
  if grep -q "base:$rel:" "$STATE"; then echo "FAIL: base: record leaked for $rel"; cat "$STATE"; exit 1; fi
done
if [ -f "$HUB_SETUP/$C" ]; then echo "FAIL: c was installed despite the earlier abort"; echo "$out"; exit 1; fi

# No leftover install temp file anywhere under the hub.
if find "$TMP/hub" -name '.sync-install.*' | grep -q .; then
  echo "FAIL: leftover .sync-install.* temp file under hub"; find "$TMP/hub" -name '.sync-install.*'; exit 1
fi

echo "PASS: test_install_partial_failure"
