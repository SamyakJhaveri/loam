#!/usr/bin/env bash
# validate-experiment-config.sh — Research flavor hook
#
# PreToolUse hook on Write
#
# Validates that writes to experiments/runs/*/config.json contain
# all required reproducibility fields.
#
# Exit codes:
#   0 = allow (not a config.json write, or valid config)
#   2 = BLOCK (missing required fields or file already exists)

set -euo pipefail

INPUT=$(cat)
TOOL_NAME="${CLAUDE_TOOL_NAME:-}"

# Only check Write tool
if [ "$TOOL_NAME" != "Write" ]; then
  exit 0
fi

# Extract file_path from tool input
FILE=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('file_path', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

# Only check experiments/runs/*/config.json paths
if ! echo "$FILE" | grep -qE 'experiments/runs/[^/]+/config\.json$'; then
  exit 0
fi

# BLOCK if file already exists (append-only — no overwrites)
if [ -f "$FILE" ]; then
  echo "BLOCKED: config.json already exists at $FILE" >&2
  echo "Experiment runs are immutable. Create a new run instead." >&2
  exit 2
fi

# Extract content from tool input
CONTENT=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('content', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

# Validate required fields and formats
python3 -c "
import sys, json, re

content = sys.stdin.read()
try:
    config = json.loads(content)
except json.JSONDecodeError:
    print('BLOCKED: config.json is not valid JSON', file=sys.stderr)
    sys.exit(2)

required = ['schema_version', 'experiment_name', 'spec_version', 'timestamp', 'git_commit', 'config_hash', 'seed']
missing = [f for f in required if f not in config]
if missing:
    print(f'BLOCKED: config.json missing required fields: {missing}', file=sys.stderr)
    sys.exit(2)

sv = config.get('schema_version')
if not isinstance(sv, int) or sv < 1:
    print('BLOCKED: schema_version must be a positive integer', file=sys.stderr)
    sys.exit(2)

if not re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', str(config['timestamp'])):
    print('BLOCKED: timestamp must be ISO 8601 format', file=sys.stderr)
    sys.exit(2)

if not re.match(r'^[0-9a-f]{7,}$', str(config['git_commit'])):
    print('BLOCKED: git_commit must be hex string, 7+ characters', file=sys.stderr)
    sys.exit(2)

if not re.match(r'^v\d+$', str(config['spec_version'])):
    print('BLOCKED: spec_version must match pattern v<N> (e.g. v1, v2)', file=sys.stderr)
    sys.exit(2)
" <<< "$CONTENT"

exit 0
