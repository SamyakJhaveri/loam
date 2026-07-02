#!/usr/bin/env bash
# _apply_research_overlay.sh — merge research flavor assets into .claude/.
# Called by Copier _tasks when is_research=true. Deleted after bootstrap.
set -euo pipefail

echo '[copier] Applying research flavor...'

# 1. Copy overlay directories into .claude/
cp -R _research/agents/* .claude/agents/ 2>/dev/null || true
cp -R _research/skills/* .claude/skills/ 2>/dev/null || true
cp -R _research/hooks/*  .claude/hooks/  2>/dev/null || true
cp -R _research/rules/*  .claude/rules/  2>/dev/null || true
mkdir -p .codex/agents 2>/dev/null || true
cp -R _research/.codex/agents/* .codex/agents/ 2>/dev/null || true
cp _research/seed-docs/* . 2>/dev/null || true

# 2. Deep-merge research hook registrations into settings.json
python3 _copier_merge_hooks.py _research/settings-hooks.json .claude/settings.json 2>/dev/null || true

# 3. Remove the generic result-immutability hook (superseded by research protect-results.sh)
python3 -c "
import json

path = '.claude/settings.json'
with open(path) as f:
    settings = json.load(f)

for entry in settings.get('hooks', {}).get('PreToolUse', []):
    entry['hooks'] = [
        h for h in entry.get('hooks', [])
        if 'result-immutability.sh' not in h.get('command', '')
    ]

with open(path, 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')
" 2>/dev/null || true

rm -f .claude/hooks/result-immutability.sh

# 4. Clean up overlay directory
rm -rf _research

echo '[copier] Research flavor applied.'
