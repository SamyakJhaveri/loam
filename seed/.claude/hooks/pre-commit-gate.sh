#!/usr/bin/env bash
# Shared command parsing and receipt checks; 0 allows, 2 blocks the tool call.
set -uo pipefail
HOOK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || exit 2
python3 "$HOOK_DIR/../../.agents/lib/validation.py" pre-commit
RESULT=$?
if [ "$RESULT" -ne 0 ]; then exit 2; fi
exit 0
