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
VENV="$PROJECT_ROOT/env_parbench/bin/activate"

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

# Activate venv for test commands
if [ -f "$VENV" ]; then
    # shellcheck disable=SC1090
    source "$VENV"
fi

# Route to appropriate test based on file path
if echo "$FILE_PATH" | grep -q "c_augmentation/"; then
    echo "[post-edit-test] Running augmentation transform tests..."
    timeout 30 python3 -m pytest "$PROJECT_ROOT/c_augmentation/test_transforms.py" -x -q --tb=line 2>&1 | tail -5 || true

elif echo "$FILE_PATH" | grep -q "harness/"; then
    echo "[post-edit-test] Smoke-testing harness import..."
    timeout 30 python3 -m harness --help >/dev/null 2>&1 && echo "[post-edit-test] harness import OK" || echo "[post-edit-test] WARNING: harness import failed"

elif echo "$FILE_PATH" | grep -q "scripts/evaluation/"; then
    echo "[post-edit-test] Smoke-testing evaluation module import..."
    timeout 30 python3 -c "
import importlib, sys
sys.path.insert(0, '$PROJECT_ROOT')
importlib.import_module('scripts.evaluation.llm_evaluate')
print('[post-edit-test] llm_evaluate import OK')
" 2>&1 || echo "[post-edit-test] WARNING: llm_evaluate import failed"

elif echo "$FILE_PATH" | grep -q "specs/"; then
    echo "[post-edit-test] Validating spec schema..."
    timeout 30 python3 "$PROJECT_ROOT/scripts/validate_schema.py" --spec "$FILE_PATH" 2>&1 | tail -5 || true

else
    # No test needed for other files
    exit 0
fi

exit 0
