#!/usr/bin/env bash
# test_install_symlink_ancestor.sh
# Codex pass 2 Critical C5: install_file must refuse a destination path that
# passes through a committed hub symlink ancestor, else an approved sync writes
# OUTSIDE the plugin tree.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
H="$TMP/hub"; HS="$H/cultivation/marketplace/sam-cc-setup"

# Hub: an outside/ dir with a marker, plus a committed symlink
# skills -> ../../../outside (from the plugin dir, resolves to $HUB/outside).
mkdir -p "$HS" "$H/outside"
echo marker > "$H/outside/marker.txt"
ln -s ../../../outside "$HS/skills"
(cd "$H" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

# Project adds skills/x/SKILL.md (its dest path passes through the symlink).
mkdir -p "$TMP/proj/.claude/skills/x"
echo "project file" > "$TMP/proj/.claude/skills/x/SKILL.md"
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
STATE="$H/.sync-state"
set +e
out=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$H" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

if [ "$rc" -eq 0 ]; then echo "FAIL: scan exited 0; expected abort on a symlink ancestor"; echo "$out"; exit 1; fi
if ! echo "$out" | grep -qF "symlink in destination path: skills"; then
  echo "FAIL: missing/incorrect symlink Error (should name skills)"; echo "$out"; exit 1; fi
if [ -e "$H/outside/x" ]; then echo "FAIL: wrote OUTSIDE the plugin tree ($H/outside/x)"; ls -R "$H/outside"; exit 1; fi
if [ -f "$STATE" ] && grep -qE "^(synced|base):skills/x/SKILL.md:" "$STATE"; then
  echo "FAIL: phantom ledger record for skills/x/SKILL.md"; cat "$STATE"; exit 1; fi
if find "$H" -name '.sync-install.*' | grep -q .; then
  echo "FAIL: leftover .sync-install.* under hub"; find "$H" -name '.sync-install.*'; exit 1; fi

echo "PASS: test_install_symlink_ancestor"
