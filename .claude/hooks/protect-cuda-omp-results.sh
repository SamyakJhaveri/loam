#!/usr/bin/env bash
# protect-cuda-omp-results.sh
#
# PreToolUse hook on Bash — protects Phase 3 (and later) evaluation results
# from accidental deletion, modification, or overwrite.
#
# SCOPE (current — retargeted 2026-04-20):
#   Protects result files under `results/phase3/` and any `results/phaseN/`
#   path (N >= 3). Pre-Phase-3 data at `results/evaluation/` was purged
#   2026-04-20 per user directive (Qwen 3.5 397B + GPT-4.1-mini campaigns
#   decommissioned; evaluation re-runs for NeurIPS 2026 from a clean slate
#   with azure-gpt-5.4 + together-qwen-3.5-397b-a17b canonical + ablation).
#   This hook now protects the future data; it will no longer fire on
#   `results/evaluation/` paths.
#
# BLOCKS:
#   1. rm/git rm targeting Phase 3 result files matching *cuda*omp* or *omp*cuda*
#   2. run_eval_batch.py with cuda-to-omp or omp-to-cuda direction WITHOUT --resume
#      (applies regardless of output dir — preserves resume semantics)
#   3. Warn on llm_evaluate.py single-run for cuda↔omp pairs
#
# WHY: Phase 3 canonical + L0-conditional ablation results represent
# expensive LLM API calls (~$848 recomputed budget, awaiting fresh Gal
# sign-off). Once the runs complete, results are immutable per the
# same inviolable rule that applied to the pre-Phase-3 data.
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

# ── Check 1: rm/git rm targeting Phase 3+ CUDA↔OMP result files ────────────
# Matches any rm command that could hit result files with cuda+omp in the name
# inside a results/phase{3..9}/ path.

if echo "$CMD" | grep -qE '\brm\b' && echo "$CMD" | grep -qE 'results/phase[3-9]'; then
    if echo "$CMD" | grep -qiE '(cuda.*omp|omp.*cuda)'; then
        echo "BLOCKED: Cannot delete Phase 3+ CUDA↔OMP evaluation results." >&2
        echo "  Command: $CMD" >&2
        echo "  These results are IMMUTABLE — they represent expensive LLM API calls." >&2
        echo "  If you must re-run, use --resume to skip existing results." >&2
        exit 2
    fi
    if echo "$CMD" | grep -qE '\*\.(json|txt)'; then
        echo "BLOCKED: Wildcard rm in results/phaseN/ could delete CUDA↔OMP results." >&2
        echo "  Command: $CMD" >&2
        echo "  Use specific file patterns that exclude *cuda*omp* and *omp*cuda* files." >&2
        exit 2
    fi
fi

# ── Check 2: run_eval_batch.py without --resume for CUDA↔OMP directions ────
# Applies regardless of output dir — preserves resume semantics to prevent
# accidental overwrite when a Phase 3 run is paused and resumed.

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

if echo "$CMD" | grep -qE 'llm_evaluate\.py'; then
    HAS_CUDA=$(echo "$CMD" | grep -oE '\-\-source\s+\S*cuda\S*|\-\-target\s+\S*cuda\S*' | head -1)
    HAS_OMP=$(echo "$CMD" | grep -oE '\-\-source\s+\S*omp\S*|\-\-target\s+\S*omp\S*' | head -1)
    if [ -n "$HAS_CUDA" ] && [ -n "$HAS_OMP" ]; then
        echo "WARNING: Running CUDA↔OMP translation via llm_evaluate.py." >&2
        echo "  Phase 3+ CUDA↔OMP results are IMMUTABLE once produced." >&2
        echo "  Verify the output path does not collide with existing Phase 3 results." >&2
        exit 0
    fi
fi

exit 0
