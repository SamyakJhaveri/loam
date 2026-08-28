#!/usr/bin/env bash
# test_manifest_guard.sh
# Verifies the portability-manifest guard (2026-08-02):
#   - 'travels' paths are offered
#   - 'stays' and 'rework' paths are withheld
#   - paths with no manifest verdict are withheld (fail closed)
#   - with NO manifest present, everything is offered (fail open, other projects)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

build_hub() {
  local hub="$1"
  rm -rf "$hub"
  mkdir -p "$hub/cultivation/marketplace/sam-cc-setup"
  (cd "$hub" && git init -q && git commit -q --allow-empty \
    -c user.email=t@t -c user.name=t -m init 2>/dev/null || \
    git -c user.email=t@t -c user.name=t commit -q --allow-empty -m init)
}

build_proj() {
  local proj="$1" with_manifest="$2"
  rm -rf "$proj"
  mkdir -p "$proj/.claude/skills/goes" "$proj/.claude/skills/homebody" \
           "$proj/.claude/hooks" "$proj/.claude/plans"
  echo "g" > "$proj/.claude/skills/goes/SKILL.md"
  echo "h" > "$proj/.claude/skills/homebody/SKILL.md"
  echo "r" > "$proj/.claude/hooks/needs-work.sh"
  echo "p" > "$proj/.claude/plans/scratch.md"
  if [ "$with_manifest" = yes ]; then
    mkdir -p "$proj/.claude/reference"
    printf 'path\tkind\tverdict\treason\n' > "$proj/.claude/reference/portability-manifest.tsv"
    printf 'skills/goes\tskill\ttravels\tok\n' >> "$proj/.claude/reference/portability-manifest.tsv"
    printf 'skills/homebody\tskill\tstays\tlocal\n' >> "$proj/.claude/reference/portability-manifest.tsv"
    printf 'hooks/needs-work.sh\thook\trework\thardcoded\n' >> "$proj/.claude/reference/portability-manifest.tsv"
    # plans/scratch.md deliberately has NO row (unclassified)
  fi
  (cd "$proj" && git init -q && git add -A && \
    git -c user.email=t@t -c user.name=t commit -q -m init)
}

# RUN A: manifest present — only 'travels' offered
build_hub "$TMP/hub"; build_proj "$TMP/proj" yes
cd "$TMP/proj"
out=$(printf 'n\nn\nn\nn\nn\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1 || true)
echo "$out" | grep -q "skills/goes" || { echo "FAIL: travels path not offered"; exit 1; }
echo "$out" | grep -q "skills/homebody" && { echo "FAIL: stays path was offered"; exit 1; }
echo "$out" | grep -q "needs-work.sh" && { echo "FAIL: rework path was offered"; exit 1; }
echo "$out" | grep -q "plans/scratch.md" && { echo "FAIL: unclassified path was offered (must fail closed)"; exit 1; }
echo "$out" | grep -q "manifest guard:" || { echo "FAIL: guard summary line missing"; exit 1; }

# RUN B: no manifest — everything offered (unchanged legacy behavior)
build_hub "$TMP/hub2"; build_proj "$TMP/proj2" no
cd "$TMP/proj2"
out=$(printf 'n\nn\nn\nn\nn\n' | SAM_CC_HUB_REPO="$TMP/hub2" bash "$SYNC_SH" 2>&1 || true)
for p in "skills/goes" "skills/homebody" "hooks/needs-work.sh" "plans/scratch.md"; do
  echo "$out" | grep -q "$p" || { echo "FAIL: $p not offered when no manifest exists"; exit 1; }
done
echo "$out" | grep -q "manifest guard:" && { echo "FAIL: guard summary printed without a manifest"; exit 1; }

echo "PASS test_manifest_guard.sh"
