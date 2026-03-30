#!/usr/bin/env bash
# Result immutability — blocks Edit/Write to existing result JSON files
#
# Triggered by: PreToolUse on Edit|Write
# Purpose: Eval results are append-only (like manifest.jsonl). Overwriting an existing
#          result file invalidates the audit trail. Use --resume in run_eval_batch.py
#          to skip existing results instead of overwriting them.
#
# Exit codes:
#   0 = allow (file doesn't exist yet, or not a result file)
#   2 = BLOCK (existing result file would be overwritten)

set -euo pipefail

INPUT=$(cat)

FILE=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('file_path', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

if [ -n "$FILE" ] && echo "$FILE" | grep -qE 'results/evaluation/.*\.json$'; then
  if [ -f "$FILE" ]; then
    echo "BLOCKED: Cannot overwrite existing result file: $FILE" >&2
    echo "Use --resume in run_eval_batch.py to skip existing results." >&2
    exit 2
  fi
fi

exit 0
