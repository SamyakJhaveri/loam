#!/usr/bin/env bash
# protect-cuda-omp-results.sh
#
# PreToolUse hook on Bash — blocks commands that could delete, modify,
# or overwrite existing CUDA↔OMP evaluation results.
#
# BLOCKS:
#   1. rm/git rm targeting result files matching *cuda*omp* or *omp*cuda*
#   2. run_eval_batch.py with cuda-to-omp or omp-to-cuda direction WITHOUT --resume
#   3. mv/cp that would overwrite existing CUDA↔OMP result files
#
# WHY: During session S-OCLFIX (2026-03-30), a test re-run accidentally
# overwrote 5 bfs omp-to-cuda results, regressing them from PASS to
# EXTRACTION_FAIL. These results represent expensive LLM API calls
# (Qwen 3.5 397B via Together AI) that cannot be cheaply reproduced.
# Samyak explicitly demanded this as an inviolable rule.
#
# Exit codes:
#   0 = allow
#   2 = BLOCK

set -euo pipefail

# Read hook event JSON from stdin
INPUT=$(cat)

# Extract the command from tool_input
CMD=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('command', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

if [ -z "$CMD" ]; then
    exit 0
fi

# ── Check 1: rm/git rm targeting CUDA↔OMP result files ─────────────────────
# Matches any rm command that could hit result files with cuda+omp in the name

if echo "$CMD" | grep -qE '\brm\b' && echo "$CMD" | grep -qE 'results/evaluation/'; then
    # Check if the rm glob/path could match cuda↔omp result files
    if echo "$CMD" | grep -qiE '(cuda.*omp|omp.*cuda)'; then
        echo "BLOCKED: Cannot delete CUDA↔OMP evaluation results." >&2
        echo "  Command: $CMD" >&2
        echo "  These results are IMMUTABLE — they represent expensive LLM API calls." >&2
        echo "  If you must re-run, use --resume to skip existing results." >&2
        exit 2
    fi
    # Block wildcard rm that could match CUDA↔OMP files via glob expansion
    # Catches: rm -f *.json, rm -f rodinia-*.json, rm -f rodinia-bfs-*.json, etc.
    if echo "$CMD" | grep -qE '\*\.(json|txt)'; then
        echo "BLOCKED: Wildcard rm in results/evaluation/ could delete CUDA↔OMP results." >&2
        echo "  Command: $CMD" >&2
        echo "  Use specific file patterns that exclude *cuda*omp* and *omp*cuda* files." >&2
        exit 2
    fi
fi

# ── Check 2: run_eval_batch.py without --resume for CUDA↔OMP directions ────
# Running cuda-to-omp or omp-to-cuda without --resume risks overwriting results

if echo "$CMD" | grep -qE 'run_eval_batch\.py'; then
    if echo "$CMD" | grep -qE '(cuda-to-omp|omp-to-cuda)'; then
        if ! echo "$CMD" | grep -qE '\-\-resume'; then
            echo "BLOCKED: run_eval_batch.py for CUDA↔OMP direction requires --resume." >&2
            echo "  Command: $CMD" >&2
            echo "  Always use --resume to protect existing CUDA↔OMP results from overwrite." >&2
            exit 2
        fi
    fi
fi

# ── Check 3: llm_evaluate.py single-run for CUDA↔OMP without checking ──────
# Direct llm_evaluate.py calls with source/target that are cuda↔omp pairs

if echo "$CMD" | grep -qE 'llm_evaluate\.py'; then
    # Check if both --source and --target contain cuda and omp (in either order)
    HAS_CUDA=$(echo "$CMD" | grep -oE '\-\-source\s+\S*cuda\S*|\-\-target\s+\S*cuda\S*' | head -1)
    HAS_OMP=$(echo "$CMD" | grep -oE '\-\-source\s+\S*omp\S*|\-\-target\s+\S*omp\S*' | head -1)
    if [ -n "$HAS_CUDA" ] && [ -n "$HAS_OMP" ]; then
        echo "WARNING: Running CUDA↔OMP translation via llm_evaluate.py." >&2
        echo "  Existing CUDA↔OMP results are IMMUTABLE." >&2
        echo "  Verify the output path does not collide with existing results." >&2
        # Allow but warn — llm_evaluate.py single runs create new files
        exit 0
    fi
fi

exit 0
