#!/usr/bin/env bash
# test_addition.sh
# Verifies opt-in per-file addition flow: 'y' applies, empty (default-defer) does not.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap "rm -rf '$TMP'" EXIT

# Helper: build a fresh hub with foo skill committed
build_hub() {
  local hub="$1"
  rm -rf "$hub"
  mkdir -p "$hub/cultivation/marketplace/sam-cc-setup/skills/foo"
  echo "foo content" > "$hub/cultivation/marketplace/sam-cc-setup/skills/foo/SKILL.md"
  (cd "$hub" && git init -q && git add -A && \
    git -c user.email=t@t -c user.name=t commit -q -m init)
}

# Build project once: foo (matches hub) + bar (new)
mkdir -p "$TMP/proj/.claude/skills/foo" "$TMP/proj/.claude/skills/bar"
echo "foo content" > "$TMP/proj/.claude/skills/foo/SKILL.md"
echo "bar content" > "$TMP/proj/.claude/skills/bar/SKILL.md"
(cd "$TMP/proj" && git init -q && git add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

# RUN A: user approves bar addition (y), declines commit (n)
build_hub "$TMP/hub"
cd "$TMP/proj"
set +e
output_a=$(printf 'y\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc_a=$?
set -e
cd - >/dev/null

if [ "$rc_a" -ne 0 ]; then
  echo "FAIL (Run A): exit $rc_a"
  echo "output: $output_a"
  exit 1
fi
if [ ! -f "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md" ]; then
  echo "FAIL (Run A): bar/SKILL.md missing in hub after approved addition"
  echo "output: $output_a"
  exit 1
fi
got=$(cat "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md")
if [ "$got" != "bar content" ]; then
  echo "FAIL (Run A): bar content mismatch — got '$got'"
  exit 1
fi

# RUN B: user defers bar addition (empty), declines commit (n)
build_hub "$TMP/hub"
cd "$TMP/proj"
set +e
output_b=$(printf '\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc_b=$?
set -e
cd - >/dev/null

if [ "$rc_b" -ne 0 ]; then
  echo "FAIL (Run B): exit $rc_b"
  echo "output: $output_b"
  exit 1
fi
if [ -f "$TMP/hub/cultivation/marketplace/sam-cc-setup/skills/bar/SKILL.md" ]; then
  echo "FAIL (Run B): bar/SKILL.md present in hub despite default-defer"
  echo "output: $output_b"
  exit 1
fi

echo "PASS: test_addition (sync-now + default-defer)"
