#!/usr/bin/env bash
# lint-skill-descriptions.sh — check skill descriptions for quality issues
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
WARN=0

extract_frontmatter() {
  # Extract content between first and second --- delimiters only
  awk 'BEGIN{in_fm=0; count=0} /^---$/{count++; if(count==1){in_fm=1; next} if(count==2){exit}} in_fm{print}' "$1"
}

while IFS= read -r skill_file; do
  frontmatter=$(extract_frontmatter "$skill_file")
  name=$(echo "$frontmatter" | grep -m1 '^name:' | sed 's/name: *//' | tr -d '"' || true)
  if [ -z "$name" ]; then
    rel_path="${skill_file#"$ROOT"/}"
    echo "WARN [$rel_path]: could not parse name from frontmatter"
    WARN=$((WARN + 1))
    continue
  fi

  # Check 0: YAML frontmatter is valid (catches unquoted colons, bad indentation)
  if command -v python3 >/dev/null 2>&1; then
    if ! python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    content = f.read()
parts = content.split('---', 2)
if len(parts) >= 3:
    yaml.safe_load(parts[1])
" "$skill_file" 2>/dev/null; then
      echo "WARN [$name]: YAML frontmatter is not valid (parse error)"
      WARN=$((WARN + 1))
    fi
  fi

  # Extract description (handles both single-line and multi-line YAML)
  # Use awk to handle end-of-frontmatter correctly (sed '$d' strips the last
  # description line when description is the final key in frontmatter).
  desc=$(echo "$frontmatter" | awk '/^description:/{found=1; sub(/^description: */, ""); if($0 != "" && $0 != ">") print; next} found && /^[a-z]/{exit} found{print}' | sed 's/^  *//' | tr '\n' ' ' | sed 's/  */ /g')
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

  # Check 2: Auto-activate skills (auto-activate: true or unset) missing negative triggers
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
done < <(find "$ROOT/seed/.claude/skills" "$ROOT/seed/_research/skills" "$ROOT/cultivation/marketplace" -name "SKILL.md" 2>/dev/null | sort)

echo ""
echo "Total warnings: $WARN"
if [ "$WARN" -eq 0 ]; then
  echo "ALL OK"
else
  exit 1
fi
