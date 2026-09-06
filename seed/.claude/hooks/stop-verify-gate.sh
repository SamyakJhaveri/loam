#!/usr/bin/env bash
# Shared turn-end checks; Python owns payload parsing and safe path handling.
set -uo pipefail
HOOK_DIR="${BASH_SOURCE[0]%/*}"
python3 "$HOOK_DIR/../../.agents/lib/stop_verify.py"
status=$?
if [ "$status" -ne 0 ]; then
    echo 'Stop verification did not complete successfully.' >&2
    exit 2
fi
