#!/usr/bin/env bash
# =============================================================================
# Re-run ALL eval batches with corrected conjunction verification
# Created: 2026-03-27 (S-VERIFY follow-up)
#
# Why: 169 existing PASS results verified under disjunction semantics
# (exit_code only, stdout_pattern never checked). Must re-run with
# conjunction semantics where ALL strategies must pass.
#
# Run this script from the project root:
#   bash scripts/batch/rerun_conjunction_eval.sh
#
# It creates a tmux session "eval-rerun" with 2 windows:
#   Window 0 (cuda-to-omp): 18 kernels x 5 levels x 3 models = 270 tasks
#   Window 1 (omp-to-cuda + xsbench): 18 kernels x 1 level x 3 models +
#                                      12 dirs x 5 levels x 3 models = 234 tasks
# Total: ~504 tasks, estimated ~6-8 hours with parallelism
# =============================================================================

set -euo pipefail

PROJECT_ROOT="{{PROJECT_ROOT}}"
cd "$PROJECT_ROOT"

# --- Pre-flight checks -------------------------------------------------------
echo "=== Pre-flight checks ==="

# Venv
if ! python3 -c "import harness" 2>/dev/null; then
    echo "ERROR: harness not importable. Run: source env_parbench/bin/activate"
    exit 1
fi

# API keys
# Gemini uses GEMINI_API_KEY or GOOGLE_API_KEY (either works)
for key in ANTHROPIC_API_KEY GROQ_API_KEY; do
    if [ -z "${!key:-}" ]; then
        echo "ERROR: $key not set"
        exit 1
    fi
done
if [ -z "${GEMINI_API_KEY:-}" ] && [ -z "${GOOGLE_API_KEY:-}" ]; then
    echo "ERROR: Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set"
    exit 1
fi

# GPU
if ! nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null; then
    echo "ERROR: nvidia-smi failed — no GPU available"
    exit 1
fi

echo "Pre-flight OK"

# --- Archive old results ------------------------------------------------------
echo "=== Archiving old results ==="

ARCHIVE="$PROJECT_ROOT/results/evaluation_archive_pre_conjunction_20260327"
mkdir -p "$ARCHIVE"

MODELS="claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile"

for model in $MODELS; do
    if [ -d "results/evaluation/$model" ]; then
        cp -r "results/evaluation/$model" "$ARCHIVE/"
        echo "  Archived $model"
    fi
done

if [ -d "results/evaluation/azure-gpt-4.1" ]; then
    cp -r "results/evaluation/azure-gpt-4.1" "$ARCHIVE/"
    echo "  Archived azure-gpt-4.1"
fi

# Verify archive counts
echo "=== Verifying archive ==="
for model in $MODELS; do
    archived=$(find "$ARCHIVE/$model" -name '*.json' 2>/dev/null | wc -l)
    original=$(find "results/evaluation/$model" -name '*.json' 2>/dev/null | wc -l)
    echo "  $model: archived=$archived original=$original"
    if [ "$archived" -ne "$original" ]; then
        echo "ERROR: archive count mismatch for $model! Aborting."
        exit 1
    fi
done

# Clear active model directories
echo "=== Clearing active model directories ==="
for model in $MODELS; do
    rm -rf "results/evaluation/$model"
    mkdir -p "results/evaluation/$model"
done
rm -rf results/evaluation/azure-gpt-4.1

# Verify empty
for model in $MODELS; do
    remaining=$(find "results/evaluation/$model" -name '*.json' 2>/dev/null | wc -l)
    if [ "$remaining" -ne 0 ]; then
        echo "ERROR: $model directory not empty ($remaining files remain)!"
        exit 1
    fi
    echo "  $model: clean"
done

echo "=== Archive complete ==="

# --- Launch tmux session ------------------------------------------------------
# Kernel list (18 valid): excludes 3 phantom specs (gaussian, huffman, hybridsort)
# Includes 2 KNOWN_FAIL (kmeans, mummergpu) for failure taxonomy completeness
echo "=== Launching tmux session 'eval-rerun' ==="

# Kill existing session if present
tmux kill-session -t eval-rerun 2>/dev/null || true

tmux new-session -d -s eval-rerun -n cuda-to-omp

# Window 0: Rodinia cuda-to-omp (18 kernels x L0-L4 x 3 models, sequential)
tmux send-keys -t eval-rerun:cuda-to-omp \
  "cd $PROJECT_ROOT && source env_parbench/bin/activate" C-m

tmux send-keys -t eval-rerun:cuda-to-omp \
  'for model in claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile; do
  echo "=== Starting $model cuda-to-omp at $(date) ==="
  python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction cuda-to-omp \
    --models $model \
    --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud mummergpu myocyte nn nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 1 2 3 4 \
    --max-retries 2 --resume \
    --project-root {{PROJECT_ROOT}} -v \
    2>&1 | tee {{PROJECT_ROOT}}/results/evaluation/rerun_${model}_cuda-to-omp.log
  echo "=== Finished $model cuda-to-omp at $(date) ==="
done
echo "=== ALL cuda-to-omp COMPLETE at $(date) ==="' C-m

# Window 1: Rodinia omp-to-cuda + XSBench (sequential per direction per model)
tmux new-window -t eval-rerun -n omp-and-xsbench

tmux send-keys -t eval-rerun:omp-and-xsbench \
  "cd $PROJECT_ROOT && source env_parbench/bin/activate" C-m

tmux send-keys -t eval-rerun:omp-and-xsbench \
  'for model in claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile; do
  echo "=== Starting $model omp-to-cuda at $(date) ==="
  python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction omp-to-cuda \
    --models $model \
    --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud mummergpu myocyte nn nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 \
    --max-retries 2 --resume \
    --project-root {{PROJECT_ROOT}} -v \
    2>&1 | tee {{PROJECT_ROOT}}/results/evaluation/rerun_${model}_omp-to-cuda.log
  echo "=== Finished $model omp-to-cuda at $(date) ==="
done

for direction in cuda-to-omp omp-to-cuda cuda-to-opencl opencl-to-cuda omp-to-opencl opencl-to-omp cuda-to-omp_target omp-to-omp_target opencl-to-omp_target omp_target-to-cuda omp_target-to-omp omp_target-to-opencl; do
  for model in claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile; do
    echo "=== Starting $model xsbench $direction at $(date) ==="
    python3 scripts/evaluation/run_eval_batch.py \
      --suite xsbench --direction $direction \
      --models $model \
      --augment-levels 0 1 2 3 4 \
      --max-retries 2 --resume \
      --project-root {{PROJECT_ROOT}} -v \
      2>&1 | tee -a {{PROJECT_ROOT}}/results/evaluation/rerun_${model}_xsbench.log
    echo "=== Finished $model xsbench $direction at $(date) ==="
  done
done
echo "=== ALL omp-to-cuda + xsbench COMPLETE at $(date) ==="' C-m

echo ""
echo "=== tmux session 'eval-rerun' launched ==="
echo "  Window 0 (cuda-to-omp): 18 kernels x 5 levels x 3 models = 270 tasks"
echo "  Window 1 (omp-and-xsbench): 54 omp-to-cuda + 180 xsbench = 234 tasks"
echo ""
echo "Monitor with:  tmux attach -t eval-rerun"
echo "Detach with:   Ctrl-B D"
echo "Switch window: Ctrl-B 0 / Ctrl-B 1"
