#!/usr/bin/env bash
# test_plugin_root_symlink.sh
# Codex pass 4 Critical (item 1): the normal scan's `mkdir -p "$HUB_PLUGIN"` runs
# BEFORE any symlink check, so a committed plugin-root ancestor symlink
# (cultivation -> ../outside) makes mkdir create marketplace/sam-cc-setup OUTSIDE
# the hub before approval. reject_symlink_path, called before the mkdir, must
# abort first so nothing is created behind the symlink and nothing commits.
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

H="$TMP/hub"
# Symlink target sits OUTSIDE the hub repo (sibling under $TMP), reached via
# `../outside` from $H/cultivation - the brief's escape shape.
mkdir -p "$H" "$TMP/outside"
echo "outside marker" > "$TMP/outside/marker.txt"
# cultivation is a committed symlink; NO real plugin tree exists behind it, so the
# normal scan's `mkdir -p "$HUB_PLUGIN"` is what would create dirs through it.
ln -s ../outside "$H/cultivation"
(cd "$H" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)
HEAD_BEFORE=$(git -C "$H" rev-parse HEAD)

# Project has one new file, so the scan has work to do.
mkdir -p "$TMP/proj/.claude/skills/x"
echo "project file" > "$TMP/proj/.claude/skills/x/SKILL.md"
(cd "$TMP/proj" && git init -q && git -c user.email=t@t -c user.name=t add -A && git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
set +e
out=$(printf 'n\n' | SAM_CC_HUB_REPO="$H" bash "$SYNC_SH" 2>&1)
rc=$?
set -e

# 1 (RED: pre-fix reaches mkdir then exits 0 on the defer/never): abort with exit 1.
if [ "$rc" -ne 1 ]; then echo "FAIL: expected exit 1, got $rc"; echo "$out"; exit 1; fi
# 2: the error names the symlinked component.
if ! echo "$out" | grep -qF "symlink in destination path: cultivation"; then
  echo "FAIL: missing/incorrect symlink Error (should name cultivation)"; echo "$out"; exit 1; fi
# 3 (the true RED): nothing created behind the symlink (pre-fix mkdir makes it).
if [ -e "$TMP/outside/marketplace" ]; then
  echo "FAIL: mkdir created dirs OUTSIDE the hub behind the symlink"; ls -R "$TMP/outside"; exit 1; fi
# 4: nothing committed / staged in the hub.
if [ "$(git -C "$H" rev-parse HEAD)" != "$HEAD_BEFORE" ]; then
  echo "FAIL: hub HEAD advanced (a commit was made)"; exit 1; fi
if [ -n "$(git -C "$H" diff --cached --name-only)" ]; then
  echo "FAIL: hub index has staged changes"; git -C "$H" diff --cached --name-only; exit 1; fi

echo "PASS: test_plugin_root_symlink"
