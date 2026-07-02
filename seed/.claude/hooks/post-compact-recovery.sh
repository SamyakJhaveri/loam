#!/usr/bin/env bash
# Post-compact context recovery — re-injects critical project facts after /compact
#
# Triggered by: PostToolUse on Compact
# Purpose: After context compression, key facts (project root, known issues, structure)
#          are lost. This hook re-injects them so Claude doesn't hallucinate stale data.
#
# Exit codes:
#   0 = always (advisory hook, never blocks)

set -euo pipefail

# Consume stdin (PostToolUse hooks receive JSON on stdin; prevent SIGPIPE)
cat > /dev/null

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0

echo "=== CONTEXT RECOVERY ===" >&2
echo "Project: $PROJECT_ROOT" >&2
echo "Branch: $(git -C "$PROJECT_ROOT" branch --show-current 2>/dev/null || echo 'detached')" >&2

# Show known issues if file exists
if [ -f "$PROJECT_ROOT/.claude/rules/known-issues.md" ]; then
    ISSUE_COUNT=$(grep -c '^\s*-' "$PROJECT_ROOT/.claude/rules/known-issues.md" 2>/dev/null || echo "0")
    echo "Known issues: $ISSUE_COUNT entries (see .claude/rules/known-issues.md)" >&2
fi

# Dynamic: count files in key directories
for dir in results tests src; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        count=$(find "$PROJECT_ROOT/$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
        echo "$dir/: $count files" >&2
    fi
done

echo "========================" >&2
exit 0
