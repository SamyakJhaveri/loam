#!/usr/bin/env bash
# superpowers-plan-location.sh — PreToolUse hook (Edit|Write)
# Blocks superpowers plan/spec writes under docs/superpowers/ and points the model
# at the project-root .superpowers/ directory instead.
#
# Why: superpowers v5.0.0+ defaults plan/spec output to docs/superpowers/plans|specs/.
# This project keeps docs/ human-curated and routes plugin scratch to .superpowers/
# (gitignored). The CLAUDE.md/AGENTS.md directive states this; this hook enforces it
# for fresh subagents that never read the directive at write-time.
#
# Exit codes: 0 = allow, 2 = BLOCK (stderr fed back to Claude)

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

if [ -n "$FILE_PATH" ] && echo "$FILE_PATH" | grep -qE '(^|/)docs/superpowers/'; then
    # shellcheck disable=SC2001  # sed is clearest here; paths won't contain '#'
    SUGGESTED="$(echo "$FILE_PATH" | sed 's#docs/superpowers/#.superpowers/#')"
    {
        echo "BLOCKED: this project writes superpowers plans/specs to '.superpowers/', not 'docs/superpowers/'."
        echo "Re-issue the Write to: $SUGGESTED"
        echo "(plans -> .superpowers/plans/, specs -> .superpowers/specs/. See CLAUDE.md 'Required Plugins'.)"
    } >&2
    exit 2
fi

exit 0
