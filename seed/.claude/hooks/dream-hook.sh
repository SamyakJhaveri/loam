#!/usr/bin/env bash
# dream-hook.sh — Stop hook: notifies user if memory consolidation is due.
# Always exits 0 to never block session close.
#
# Checks if 24+ hours have passed since last .last-dream timestamp.
# Notify-only — memory consolidation requires user judgment.

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
LOCAL_PATHS="$PROJECT_ROOT/.claude/.local-paths"
MEMORY_DIR="$(grep '^MEMORY_DIR=' "$LOCAL_PATHS" 2>/dev/null | cut -d= -f2)"
if [ -z "$MEMORY_DIR" ]; then
    PROJ_KEY="$(echo "$PROJECT_ROOT" | tr '/_' '--')"
    MEMORY_DIR="$HOME/.claude/projects/$PROJ_KEY/memory"
fi
LAST_DREAM="$MEMORY_DIR/.last-dream"

SHOULD_DREAM=false

if [ ! -f "$LAST_DREAM" ]; then
    SHOULD_DREAM=true
else
    LAST_TS=$(head -1 "$LAST_DREAM")
    LAST_EPOCH=$(python3 -c "from datetime import datetime; print(int(datetime.fromisoformat('$LAST_TS'.replace('Z','+00:00')).timestamp()))" 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    HOURS_SINCE=$(( (NOW_EPOCH - LAST_EPOCH) / 3600 ))
    if [ "$HOURS_SINCE" -ge 24 ]; then
        SHOULD_DREAM=true
    fi
fi

if [ "$SHOULD_DREAM" = true ]; then
    echo "Memory consolidation due — run /dream when convenient."
fi

exit 0
