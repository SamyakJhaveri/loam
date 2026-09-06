#!/usr/bin/env bash
# Canonical validation entry point. Complete content-bound checks mint a
# .validation_passed JSON receipt. Stage the intended changes before running.
set -uo pipefail
HOOK_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || exit 1
exec python3 "$HOOK_DIR/../../.agents/lib/validation.py" run --label "${1:-validate-skill}"
