#!/usr/bin/env bash
# test_install_dir_target.sh
# Codex High H4: install_file must refuse a directory at the destination path.
# mv -f moving a temp file INTO an existing directory returns 0, which would
# record a phantom install and leave a .sync-install.* file in the hub.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
REL="skills/x/SKILL.md"

# Hub: a DIRECTORY at skills/x/SKILL.md (with a file inside), plus a seed file.
mkdir -p "$HUB_SETUP/$REL"
echo inner > "$HUB_SETUP/$REL/inner.txt"
echo seed  > "$HUB_SETUP/seed.md"
(cd "$TMP/hub" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

# Project: a regular FILE at skills/x/SKILL.md (an add).
mkdir -p "$TMP/proj/.claude/skills/x"
echo "project file" > "$TMP/proj/.claude/$REL"
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
STATE="$TMP/hub/.sync-state"
set +e
out=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -eq 0 ]; then echo "FAIL: scan exited 0; expected a non-zero install abort"; echo "$out"; exit 1; fi
if ! echo "$out" | grep -qF "Error: install failed for $REL (destination is a directory)"; then
  echo "FAIL: missing the directory-destination error message"; echo "$out"; exit 1; fi
if find "$TMP/hub" -name '.sync-install.*' | grep -q .; then
  echo "FAIL: leftover .sync-install.* under hub"; find "$TMP/hub" -name '.sync-install.*'; exit 1; fi
if [ -f "$STATE" ] && grep -qE "^(synced|base):$REL:" "$STATE"; then
  echo "FAIL: phantom ledger record for $REL"; cat "$STATE"; exit 1; fi
if [ ! -d "$HUB_SETUP/$REL" ] || [ ! -f "$HUB_SETUP/$REL/inner.txt" ]; then
  echo "FAIL: hub directory at $REL was damaged"; exit 1; fi

echo "PASS: test_install_dir_target"
