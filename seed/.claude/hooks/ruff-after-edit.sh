#!/usr/bin/env bash
# Run Ruff's safe auto-fixes after Claude edits or writes a Python file.
# Claude hook input arrives as one JSON object on standard input.

set -uo pipefail

FILE="$(python3 -c '
import json
import sys

try:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input") if isinstance(payload, dict) else None
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if isinstance(file_path, str):
        print(file_path, end="")
except (json.JSONDecodeError, OSError):
    pass
' 2>/dev/null)" || FILE=""

case "$FILE" in
    *.py) python3 -m ruff check --fix -- "$FILE" >/dev/null 2>&1 || true ;;
esac

exit 0
