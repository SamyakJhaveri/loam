#!/usr/bin/env bash
# lint-skill-descriptions.sh — check skill descriptions for quality issues
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
WARN=0

extract_frontmatter() {
  # Extract content between first and second --- delimiters
  sed -n '/^---$/,/^---$/p' "$1" | sed '1d;$d'
}

for skill_file in $(find "$ROOT/.claude/skills" "$ROOT/flavors" -name "SKILL.md" 2>/dev/null | sort); do
  frontmatter=$(extract_frontmatter "$skill_file")
  name=$(echo "$frontmatter" | grep -m1 '^name:' | sed 's/name: *//' | tr -d '"' || true)
  if [ -z "$name" ]; then
    rel_path="${skill_file#"$ROOT"/}"
    echo "WARN [$rel_path]: could not parse name from frontmatter"
    WARN=$((WARN + 1))
    continue
  fi

  # Extract description (handles both single-line and multi-line YAML)
  desc=$(echo "$frontmatter" | sed -n '/^description:/,/^[a-z]/p' | sed '$d' | sed 's/^description: *//' | sed 's/^  *//' | tr '\n' ' ' | sed 's/  */ /g')
  if [ -z "$desc" ]; then
    desc=$(echo "$frontmatter" | grep -m1 '^description:' | sed 's/description: *//' || true)
  fi

  # Check auto-activate status
  auto_activate=$(echo "$frontmatter" | grep -m1 'auto-activate:' | awk '{print $2}' || true)

  # Check 1: Missing conditional language
  if ! echo "$desc" | grep -qi "Use when\|Use ONLY when\|Use before\|Use after\|Use at\|Invoke when\|Use this"; then
    echo "WARN [$name]: missing 'Use when...' conditional language"
    WARN=$((WARN + 1))
  fi

  # Check 2: Auto-activate skills missing negative triggers (skip Tier 2 skills)
  if [ "$auto_activate" != "false" ]; then
    if ! echo "$desc" | grep -qi "NOT for\|Do NOT\|Do not use\|NOT when"; then
      echo "WARN [$name]: auto-activate skill missing 'NOT for...' negative trigger"
      WARN=$((WARN + 1))
    fi
  fi

  # Check 3: Description too short
  desc_len=${#desc}
  if [ "$desc_len" -lt 30 ]; then
    echo "WARN [$name]: description under 30 chars ($desc_len)"
    WARN=$((WARN + 1))
  fi
done

echo ""
echo "Total warnings: $WARN"
if [ "$WARN" -eq 0 ]; then
  echo "ALL OK"
else
  exit 1
fi
