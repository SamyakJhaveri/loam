#!/usr/bin/env bash
# file-ownership.sh
#
# PreToolUse hook — enforces file ownership during agent team sessions.
#
# Osmani principle: One file, one owner — prevent concurrent edits in agent teams.
# When multiple teammates work in parallel, uncoordinated edits to the same file
# create overwrite conflicts. This hook blocks edits to files already claimed by
# another agent, forcing edits to be routed to the file's owner.
#
# Triggered by: PreToolUse on Edit|Write tools
# Exit 2 = BLOCK (file owned by another agent)
# Exit 0 = ALLOW (no team session, unowned, or owned by this agent)

set -euo pipefail

INPUT=$(cat)

PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
OWNERS_FILE="$PROJECT_ROOT/.file-owners.json"
TEAMS_DIR="$HOME/.claude/teams"
OWNERSHIP_TTL_SECONDS=7200  # 2 hours

# Extract file_path from tool input (try CLAUDE_TOOL_INPUT env var first, fall back to stdin)
FILE_PATH=$(python3 -c "
import sys, json, os
try:
    raw = os.environ.get('CLAUDE_TOOL_INPUT', '')
    if raw:
        d = json.loads(raw)
    else:
        d = json.loads(sys.stdin.read())
        d = d.get('tool_input', d)
    print(d.get('file_path', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

# No file path — nothing to check
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Check if a team session is active (config modified in last 2 hours)
TEAM_ACTIVE=false
if [ -d "$TEAMS_DIR" ]; then
    # Look for any team config file modified in the last 2 hours
    RECENT_TEAMS=$(find "$TEAMS_DIR" -name "config.json" -mmin -120 2>/dev/null | head -1)
    if [ -n "$RECENT_TEAMS" ]; then
        TEAM_ACTIVE=true
    fi
fi

# No active team session — no enforcement needed
if [ "$TEAM_ACTIVE" = "false" ]; then
    exit 0
fi

# Determine current agent identity. Use PPID as a stable identifier within a session,
# since there's no CLAUDE_AGENT_NAME env var. Also try to extract from the tool input
# or session context.
AGENT_ID="${CLAUDE_AGENT_NAME:-agent_${PPID}}"

# Run the ownership check/claim in Python for atomic JSON operations
python3 -c "
import json, os, sys
from datetime import datetime, timezone

owners_file = '$OWNERS_FILE'
file_path = '$FILE_PATH'
agent_id = '$AGENT_ID'
ttl = $OWNERSHIP_TTL_SECONDS

# Load existing ownership data
owners = {}
if os.path.exists(owners_file):
    try:
        with open(owners_file) as f:
            owners = json.load(f)
    except (json.JSONDecodeError, IOError):
        owners = {}

now = datetime.now(timezone.utc)

# Clean up expired entries while we're here
expired = []
for path, info in owners.items():
    try:
        ts = datetime.fromisoformat(info['timestamp'])
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        if (now - ts).total_seconds() > ttl:
            expired.append(path)
    except (KeyError, ValueError):
        expired.append(path)
for path in expired:
    del owners[path]

# Check ownership of requested file
if file_path in owners:
    owner_info = owners[file_path]
    owner = owner_info.get('owner', '')
    if owner != agent_id:
        # File owned by someone else — BLOCK (stdout shown to Claude)
        print(f'BLOCKED: File {os.path.basename(file_path)} is owned by teammate \"{owner}\". Route this edit to them.')
        # Save cleaned owners
        with open(owners_file, 'w') as f:
            json.dump(owners, f, indent=2)
        sys.exit(2)

# Claim ownership (or refresh timestamp if already ours)
owners[file_path] = {
    'owner': agent_id,
    'timestamp': now.isoformat()
}

with open(owners_file, 'w') as f:
    json.dump(owners, f, indent=2)

sys.exit(0)
" || exit $?
