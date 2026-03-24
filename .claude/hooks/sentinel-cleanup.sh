#!/usr/bin/env bash
# sentinel-cleanup.sh
#
# PostToolUse hook — deletes .validation_passed sentinel when any file is edited/written.
#
# Rationale: If Claude makes any change after validation, the sentinel is invalidated.
# This forces re-validation before the next commit.
#
# Triggered by: PostToolUse on Edit|Write tools
# Side effect: .validation_passed is silently deleted if it exists
#
# Exit codes:
#   0 = always (this hook is advisory, never blocks)

set -euo pipefail

# Consume stdin (PostToolUse hooks receive JSON on stdin; prevent SIGPIPE)
cat > /dev/null

PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
SENTINEL="$PROJECT_ROOT/.validation_passed"

# Only delete if it exists (silent no-op otherwise)
if [ -f "$SENTINEL" ]; then
    rm -f "$SENTINEL"
    # Brief note to stderr (visible in Claude Code hook output, not shown to user)
    echo "sentinel-cleanup: .validation_passed deleted (file edited after validation)" >&2
fi

exit 0
