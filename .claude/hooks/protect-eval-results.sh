#!/usr/bin/env bash
# protect-eval-results.sh
#
# PreToolUse hook on Bash — protects ALL evaluation results from accidental
# deletion. Covers results/evaluation/ (where Phase 3 data lands).
#
# BLOCKS:
#   1. rm targeting any file under results/evaluation/
#   2. run_eval_batch.py without --resume
#
# ALLOWS:
#   - Read-only operations (cat, head, ls, grep, etc.)
#   - New file creation (eval pipeline writes new results)
#   - Edit/Write blocked separately by result-immutability.sh
#
# Exit codes:
#   0 = allow
#   2 = BLOCK

set -euo pipefail

INPUT=$(cat)

CMD=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('command', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

# Block rm commands targeting results/evaluation/
if echo "$CMD" | grep -qE '\brm\b.*results/evaluation/'; then
  echo "BLOCKED: Cannot delete files in results/evaluation/" >&2
  echo "Phase 3 evaluation results are protected. Ask Samyak before deleting." >&2
  exit 2
fi

# Block shell redirects that would overwrite result files
if echo "$CMD" | grep -qE '>\s*results/evaluation/.*\.json'; then
  echo "BLOCKED: Cannot overwrite result files via redirect in results/evaluation/" >&2
  exit 2
fi

# Block eval batch without --resume
if echo "$CMD" | grep -qE 'run_eval_batch\.py' && ! echo "$CMD" | grep -qE '\-\-resume'; then
  echo "BLOCKED: run_eval_batch.py must include --resume to protect existing results" >&2
  exit 2
fi

exit 0
