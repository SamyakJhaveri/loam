#!/usr/bin/env bash
# verify-template.sh - thin verification wrapper for the Loam template.
# Check 1: scratch copier render from HEAD (the one genuinely custom check).
# Check 2: `claude plugin validate` over the real (non-symlinked) asset dirs,
#          plus a one-line semantic grep the native validator lacks
#          (frontmatter that parses but carries no `name:`).
# Check 2 SKIPs visibly when the claude CLI is absent (e.g. CI).
# Evidence on failure, no silent caps.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

# ---------- Check 1: scratch render ----------
echo "== check 1: copier scratch render (from HEAD) =="
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
if ! command -v copier >/dev/null 2>&1 && ! command -v uvx >/dev/null 2>&1; then
  echo "FAIL: neither copier nor uvx found; cannot render."
  exit 1
fi
COPIER=(copier)
command -v copier >/dev/null 2>&1 || COPIER=(uvx copier)

if "${COPIER[@]}" copy --trust --defaults --vcs-ref=HEAD \
    --data project_name=verifyproj --data github_repo= \
    "$ROOT" "$TMP/render" >"$TMP/render.log" 2>&1; then
  echo "render: OK"
else
  echo "FAIL: copier render failed. Log tail:"
  tail -20 "$TMP/render.log"
  FAIL=1
fi

if [ -d "$TMP/render" ]; then
  # The shared catchup skill must arrive as a symlink that resolves.
  LINK="$TMP/render/.claude/skills/catchup"
  if [ -L "$LINK" ] && [ -f "$LINK/SKILL.md" ]; then
    echo "catchup symlink: OK ($(readlink "$LINK"))"
  else
    echo "FAIL: $LINK is not a resolving symlink to the shared catchup skill."
    FAIL=1
  fi
  # Rendered settings.json must be valid JSON.
  if python3 -m json.tool "$TMP/render/.claude/settings.json" >/dev/null 2>&1; then
    echo "settings.json: OK"
  else
    echo "FAIL: rendered .claude/settings.json is not valid JSON."
    FAIL=1
  fi
fi

# ---------- Check 2: claude plugin validate + name grep ----------
echo "== check 2: claude plugin validate =="
if command -v claude >/dev/null 2>&1; then
  # Name the REAL directories: the tool refuses a symlinked .claude and does
  # not follow symlinks inside a named directory.
  for DIR in seed/.claude seed/.agents/skills cultivation/marketplace/*/; do
    [ -e "$DIR" ] || continue
    if claude plugin validate "$DIR" >"$TMP/validate.log" 2>&1; then
      echo "validate $DIR: OK"
    else
      echo "FAIL: claude plugin validate $DIR:"
      tail -10 "$TMP/validate.log"
      FAIL=1
    fi
  done
else
  echo "SKIPPED: claude CLI not found - plugin validation did NOT run (CI runs only check 1)."
fi

# Semantic gap the native validator has: frontmatter that parses but lacks name:.
while IFS= read -r SKILL; do
  if ! awk '/^---$/{n++} n==1 && /^name:/{found=1} END{exit !found}' "$SKILL"; then
    echo "FAIL: $SKILL frontmatter has no name: field."
    FAIL=1
  fi
done < <(find seed cultivation/marketplace -name SKILL.md -not -path '*/node_modules/*' 2>/dev/null)

echo
if [ "$FAIL" -ne 0 ]; then
  echo "verify-template: FAILED"
  exit 1
fi
echo "verify-template: PASSED"
