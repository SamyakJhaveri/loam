#!/usr/bin/env bash
# Launch the memory MCP server with a repo-rooted persistence file.

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export MEMORY_FILE_PATH="$ROOT/.claude-memory/knowledge-graph.json"

if [ "${CODEX_MCP_MEMORY_PRINT_ENV:-}" = "1" ]; then
    printf '%s\n' "$MEMORY_FILE_PATH"
    exit 0
fi

exec npx -y @modelcontextprotocol/server-memory "$@"
