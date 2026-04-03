#!/usr/bin/env bash
# Run missing L0-L4 primary campaign batches for non-Rodinia suites.
# Usage: bash scripts/batch/run_qwen_missing_batches.sh [hecbench|small|all]
set -euo pipefail

PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
source "$PROJECT_ROOT/env_parbench/bin/activate"
cd "$PROJECT_ROOT"

MODEL="together-qwen-3.5-397b-a17b"
COMMON_ARGS="--models $MODEL --augment-levels 0 1 2 3 4 --max-retries 3 --temperature 0.0 --num-samples 1 --resume -v --project-root $PROJECT_ROOT"
MODE="${1:-all}"
FAILED=()

run_batch() {
    local SUITE="$1" DIR="$2"
    shift 2
    local EXTRA=("$@")
    echo "============================================================"
    echo " $SUITE: $DIR $(date -Iseconds)"
    echo "============================================================"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite "$SUITE" --direction "$DIR" $COMMON_ARGS "${EXTRA[@]}"
    local rc=$?
    set -e
    if [ "$rc" -ne 0 ]; then
        echo "  WARNING: $SUITE $DIR failed (exit $rc)"
        FAILED+=("$SUITE:$DIR")
    fi
}

# -- Small suites (XSBench + RSBench + mixbench = 90 tasks) ---------------
if [ "$MODE" = "small" ] || [ "$MODE" = "all" ]; then
    for SUITE in xsbench rsbench mixbench; do
        for DIR in cuda-to-omp omp-to-cuda cuda-to-opencl opencl-to-cuda omp-to-opencl opencl-to-omp; do
            run_batch "$SUITE" "$DIR"
        done
    done
fi

# -- HeCBench (4 directions, kernel-filtered = ~140 tasks) ----------------
if [ "$MODE" = "hecbench" ] || [ "$MODE" = "all" ]; then
    run_batch hecbench cuda-to-omp --kernels stencil1d heat2d floydwarshall scan iso2dfd
    run_batch hecbench omp-to-cuda --kernels stencil1d heat2d floydwarshall scan iso2dfd
    run_batch hecbench cuda-to-omp_target --kernels heat2d floydwarshall page-rank jacobi nqueen md convolution1d iso2dfd
    run_batch hecbench omp_target-to-cuda --kernels stencil1d heat2d floydwarshall page-rank scan jacobi nqueen md convolution1d iso2dfd
fi

# -- Summary ---------------------------------------------------------------
echo ""
echo "============================================================"
echo " COMPLETE -- $(date -Iseconds)"
echo " Failed batches: ${#FAILED[@]}"
for b in "${FAILED[@]}"; do echo "   $b"; done
echo "============================================================"
