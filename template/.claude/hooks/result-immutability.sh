#!/usr/bin/env bash
# result-immutability.sh — PreToolUse hook (Edit|Write)
# Blocks overwriting existing files in results/ directory.
# Rationale: experiment/research results should be append-only.
# Overwriting invalidates audit trails and reproducibility.
#
# Exit codes: 0 = allow, 2 = BLOCK

set -euo pipefail

PAYLOAD="$(cat)"

FILE_PATH="$(printf '%s' "$PAYLOAD" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', d)
    print(ti.get('file_path', ''))
except Exception:
    print('')
" 2>/dev/null || echo "")"

# Only block if file is under results/ AND already exists
if [ -n "$FILE_PATH" ] && echo "$FILE_PATH" | grep -q '/results/' && [ -f "$FILE_PATH" ]; then
    echo "BLOCKED: Cannot overwrite existing file in results/." >&2
    echo "Results are append-only. To add new results, use a new filename." >&2
    echo "To intentionally replace, delete the old file first (rm + confirm)." >&2
    exit 2
fi

exit 0
