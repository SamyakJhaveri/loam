#!/usr/bin/env bash
# post-edit-test.sh
#
# PostToolUse hook — runs lightweight tests after edits based on which file was changed.
#
# Triggered by: PostToolUse on Edit|Write tools
# Always exits 0 (advisory only — never blocks edits)

set -euo pipefail

# Read hook payload from stdin (Claude Code hook protocol — do NOT use
# CLAUDE_TOOL_INPUT env var, it is not populated; see GitHub #9567)
PAYLOAD="$(cat)"

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0

# Extract file_path from tool input JSON
FILE_PATH=$(printf '%s' "$PAYLOAD" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input', d)
    print(ti.get('file_path', ''))
except Exception:
    print('')
" 2>/dev/null)

# No file path — nothing to test
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Run pytest if the edited file is Python and a tests/ directory exists
if echo "$FILE_PATH" | grep -qE '\.py$'; then
    if [ -d "$PROJECT_ROOT/tests" ]; then
        # Try common venv locations
        for VENV_PATH in "$PROJECT_ROOT/.venv/bin/activate" "$PROJECT_ROOT/venv/bin/activate" "$PROJECT_ROOT/env/bin/activate"; do
            if [ -f "$VENV_PATH" ]; then
                # shellcheck disable=SC1090
                source "$VENV_PATH"
                break
            fi
        done
        echo "[post-edit-test] Running tests..."
        # timeout 8s — must be under the 10s outer hook timeout in settings.json
        timeout 8 python3 -m pytest "$PROJECT_ROOT/tests/" -x -q --tb=line 2>&1 | tail -5 || true
    fi
fi

exit 0
