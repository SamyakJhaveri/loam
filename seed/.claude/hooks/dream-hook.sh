#!/usr/bin/env bash
# dream-hook.sh — Stop hook: notifies user if memory consolidation is due.
# Always exits 0 to never block session close.
#
# Design: Notify-only, not auto-spawn. Memory consolidation requires user
# judgment, so we print a reminder instead of auto-spawning `claude -p`
# in the background.

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"

if bash "$HOOK_DIR/should-dream.sh" 2>/dev/null; then
    echo "Memory consolidation due — run /dream when convenient."
fi

exit 0
