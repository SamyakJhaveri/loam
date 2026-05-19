#!/usr/bin/env bash
# Test: bash-audit-log.sh logs the real command from stdin JSON
set -euo pipefail
tmpdir=$(mktemp -d)
cd "$tmpdir"
git init -q
mkdir -p .claude

INPUT='{"tool_name":"Bash","tool_input":{"command":"ls -la /tmp"}}'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "$INPUT" | "$SCRIPT_DIR/bash-audit-log.sh"

grep -q "ls -la /tmp" .claude/audit.log || { echo "FAIL: command not logged"; exit 1; }
! grep -q "| unknown" .claude/audit.log || { echo "FAIL: still logging 'unknown'"; exit 1; }
echo "PASS"
rm -rf "$tmpdir"
