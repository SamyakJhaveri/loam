#!/usr/bin/env bash
# Codex PostCompact hook. Emits a compact state reminder after context compaction.

set -euo pipefail
cat >/dev/null

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0

echo "=== CONTEXT RECOVERY ===" >&2
echo "Project: $PROJECT_ROOT" >&2
echo "Branch: $(git -C "$PROJECT_ROOT" branch --show-current 2>/dev/null || echo 'detached')" >&2

if [ -f "$PROJECT_ROOT/.claude/rules/known-issues.md" ]; then
    ISSUE_COUNT=$(grep -c '^\s*-' "$PROJECT_ROOT/.claude/rules/known-issues.md" 2>/dev/null || echo "0")
    echo "Known issues: $ISSUE_COUNT entries (see .claude/rules/known-issues.md)" >&2
fi

for dir in results tests src; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        count=$(find "$PROJECT_ROOT/$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
        echo "$dir/: $count files" >&2
    fi
done

echo "========================" >&2
