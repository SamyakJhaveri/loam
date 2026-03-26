#!/usr/bin/env bash
# should-dream.sh — Returns exit 0 if dream consolidation should run, exit 1 otherwise.
# Condition: 24+ hours since last .last-dream timestamp, OR no timestamp exists.
#
# Used by dream-hook.sh (Stop hook) to decide whether to notify the user.

MEMORY_DIR="$HOME/.claude/projects/-home-samyak-Desktop-parbench-sam/memory"
LAST_DREAM="$MEMORY_DIR/.last-dream"

# Never dreamed before — should run
if [ ! -f "$LAST_DREAM" ]; then
    exit 0
fi

LAST_TS=$(head -1 "$LAST_DREAM")
LAST_EPOCH=$(date -d "$LAST_TS" +%s 2>/dev/null || echo 0)
NOW_EPOCH=$(date +%s)
HOURS_SINCE=$(( (NOW_EPOCH - LAST_EPOCH) / 3600 ))

# 24+ hours elapsed — should run
if [ "$HOURS_SINCE" -ge 24 ]; then
    exit 0
fi

# Too soon
exit 1
