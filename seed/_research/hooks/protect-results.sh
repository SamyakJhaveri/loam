#!/usr/bin/env bash
# protect-results.sh — Research flavor hook
#
# Merged from protect-eval-results.sh + result-immutability.sh.
# Protects result files from accidental deletion or overwriting.
#
# PreToolUse hook on Bash|Edit|Write
#
# BLOCKS:
#   1. rm targeting any file under results/
#   2. Shell redirects overwriting existing result JSONs
#   3. Edit/Write to existing result JSON files
#
# ALLOWS:
#   - Read-only operations (cat, head, ls, grep, etc.)
#   - New file creation (pipeline writes new results)
#
# Exit codes:
#   0 = allow
#   2 = BLOCK

set -euo pipefail

INPUT=$(cat)

# Detect which tool is being used
TOOL_NAME="${CLAUDE_TOOL_NAME:-}"

# --- Bash command checks ---
if [ "$TOOL_NAME" = "Bash" ] || [ -z "$TOOL_NAME" ]; then
  CMD=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('command', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

  # Block rm commands targeting results/
  if echo "$CMD" | grep -qE '\brm\b.*results/'; then
    echo "BLOCKED: Cannot delete files in results/" >&2
    echo "Result files are immutable. Use --resume to skip existing." >&2
    exit 2
  fi

  # Block shell redirects that would overwrite result files
  if echo "$CMD" | grep -qE '>\s*results/.*\.json'; then
    echo "BLOCKED: Cannot overwrite result files via redirect" >&2
    exit 2
  fi
fi

# --- Edit/Write checks ---
if [ "$TOOL_NAME" = "Edit" ] || [ "$TOOL_NAME" = "Write" ]; then
  FILE=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('file_path', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

  if [ -n "$FILE" ] && echo "$FILE" | grep -qE 'results/.*\.json$'; then
    if [ -f "$FILE" ]; then
      echo "BLOCKED: Cannot overwrite existing result file: $FILE" >&2
      echo "Result files are immutable once written." >&2
      exit 2
    fi
  fi
fi

exit 0
