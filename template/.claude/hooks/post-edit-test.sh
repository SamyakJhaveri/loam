#!/usr/bin/env bash
# post-edit-test.sh
#
# PostToolUse hook — runs lightweight tests after edits based on which file was changed.
#
# Osmani principle: Continuous verification — move testing earlier, not just pre-commit.
# Instead of waiting for /validate or pre-commit, this hook gives Claude immediate
# feedback when edits break tests, enabling faster iteration loops.
#
# Triggered by: PostToolUse on Edit|Write tools
# Always exits 0 (advisory only — never blocks edits)

set -euo pipefail

# Consume stdin to prevent SIGPIPE
cat > /dev/null

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0

# Try common venv locations
for VENV_PATH in "$PROJECT_ROOT/.venv/bin/activate" "$PROJECT_ROOT/venv/bin/activate" "$PROJECT_ROOT/env/bin/activate"; do
    if [ -f "$VENV_PATH" ]; then
        # shellcheck disable=SC1090
        source "$VENV_PATH"
        break
    fi
done

# Extract file_path from tool input
FILE_PATH=$(python3 -c "
import sys, json, os
try:
    d = json.loads(os.environ.get('CLAUDE_TOOL_INPUT', '{}'))
    print(d.get('file_path', ''))
except Exception:
    print('')
" 2>/dev/null)

# No file path — nothing to test
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Run pytest if the edited file is a Python file and a tests/ directory exists
if echo "$FILE_PATH" | grep -qE '\.py$'; then
    if [ -d "$PROJECT_ROOT/tests" ]; then
        echo "[post-edit-test] Running tests..."
        timeout 30 python3 -m pytest "$PROJECT_ROOT/tests/" -x -q --tb=line 2>&1 | tail -5 || true
    fi
fi

exit 0
