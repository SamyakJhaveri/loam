#!/usr/bin/env bash
# run_eval_campaign.sh — Generic full eval campaign for any model
#
# Two modes:
#   PRIMARY (default):  790 tasks — 158 pairs × L0-L4, max_retries=3, temp=0.0
#   PASS@K:             158 tasks — 158 pairs × L0 only, 3 samples each, temp=0.7
#
# Self-launches in a detached tmux session so you can safely disconnect SSH.
#
# Usage:
#   bash scripts/batch/run_eval_campaign.sh <MODEL>                 # primary campaign
#   bash scripts/batch/run_eval_campaign.sh <MODEL> pass@k          # pass@k sweep
#   bash scripts/batch/run_eval_campaign.sh <MODEL> --attach        # attach to primary session
#   bash scripts/batch/run_eval_campaign.sh <MODEL> pass@k --attach # attach to pass@k session
#
# Examples:
#   bash scripts/batch/run_eval_campaign.sh together-qwen-3.5-397b-a17b
#   bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash pass@k
#
# Primary campaign:
#   Levels: L0-L4 (5 augmentation levels)
#   Max retries: 3 (iterative self-repair with error feedback)
#   Temperature: 0.0 (greedy/deterministic)
#   Samples: 1
#   Total: 158 L0 pairs × 5 levels = 790 tasks
#
# Pass@k sweep:
#   Levels: L0 only
#   Max retries: 1 (zero-shot, no repair)
#   Temperature: 0.7 (stochastic sampling)
#   Samples: 3 (independent samples per task)
#   Total: 158 L0 pairs × 3 samples = 474 tasks
#
# Suites: Rodinia (110 pairs, incl. KNOWN_FAIL) + XSBench (6) + RSBench (6) + mixbench (6) + HeCBench (30)
#   HeCBench: cuda<->omp (11, incl. iso2dfd dup) + cuda<->omp_target (19, excl. 2 KNOWN_FAIL targets)
#   Note: ~14 Rodinia tasks involve KNOWN_FAIL specs — runner handles these gracefully
#
# Results written to: results/evaluation/<MODEL>/
# Log file: results/evaluation/<MODEL_SHORT>_{campaign,passk}.log
# Done marker: results/evaluation/<MODEL_SHORT>_{campaign,passk}_done.marker

set -euo pipefail

PROJECT_ROOT="{{PROJECT_ROOT}}"

# ── Usage ────────────────────────────────────────────────────────────────────
usage() {
    echo "Usage: $0 <MODEL> [pass@k] [--attach]"
    echo ""
    echo "  MODEL     Model ID to evaluate. Examples:"
    echo "              together-qwen-3.5-397b-a17b"
    echo "              gemini-2.5-flash"
    echo ""
    echo "  pass@k    Run pass@k sweep instead of primary campaign:"
    echo "              L0 only, temperature=0.7, num_samples=3, max_retries=1"
    echo ""
    echo "  --attach  Attach to an existing tmux session for this model/mode"
    echo ""
    echo "The script auto-launches in a tmux session."
    echo "You can safely disconnect SSH — the session will keep running."
    exit 1
}

# ── Parse arguments ─────────────────────────────────────────────────────────
MODEL=""
MODE="primary"
ATTACH=false
INSIDE_TMUX=false

for arg in "$@"; do
    case "$arg" in
        --attach)      ATTACH=true ;;
        --inside-tmux) INSIDE_TMUX=true ;;
        --help|-h)     usage ;;
        pass@k)        MODE="passk" ;;
        -*)            echo "Unknown flag: $arg"; usage ;;
        *)
            if [ -z "$MODEL" ]; then
                MODEL="$arg"
            else
                echo "Unexpected argument: $arg"; usage
            fi
            ;;
    esac
done

if [ -z "$MODEL" ]; then
    usage
fi

# ── Derive names from MODEL and MODE ────────────────────────────────────────
MODEL_SHORT=$(echo "$MODEL" | sed 's/[^a-zA-Z0-9_-]/_/g' | cut -c1-30)

if [ "$MODE" = "passk" ]; then
    SESSION="${MODEL_SHORT}_passk"
    LOGFILE="$PROJECT_ROOT/results/evaluation/${MODEL_SHORT}_passk.log"
    DONE_MARKER="$PROJECT_ROOT/results/evaluation/${MODEL_SHORT}_passk_done.marker"
    MODE_DISPLAY="pass@k sweep"
else
    SESSION="${MODEL_SHORT}_campaign"
    LOGFILE="$PROJECT_ROOT/results/evaluation/${MODEL_SHORT}_campaign.log"
    DONE_MARKER="$PROJECT_ROOT/results/evaluation/${MODEL_SHORT}_campaign_done.marker"
    MODE_DISPLAY="primary campaign"
fi

# ── Mode-specific configuration ─────────────────────────────────────────────
if [ "$MODE" = "passk" ]; then
    AUGMENT_LEVELS="0"
    MAX_RETRIES=1
    TEMPERATURE=0.7
    NUM_SAMPLES=3
    EXPECTED_TASKS=474    # 158 pairs × 3 samples
else
    AUGMENT_LEVELS="0 1 2 3 4"
    MAX_RETRIES=3
    TEMPERATURE=0.0
    NUM_SAMPLES=1
    EXPECTED_TASKS=790    # 158 pairs × 5 levels
fi

# ── --attach mode ────────────────────────────────────────────────────────────
if $ATTACH; then
    exec tmux attach -t "$SESSION"
fi

# ── API key check function ──────────────────────────────────────────────────
check_api_key() {
    case "$MODEL" in
        together-*)
            if [ -z "${TOGETHER_API_KEY:-}" ]; then
                echo "  FATAL: TOGETHER_API_KEY is not set."
                echo "  Set it with:  export TOGETHER_API_KEY='your-key-here'"
                exit 1
            fi
            echo "  OK: TOGETHER_API_KEY is set"
            ;;
        gemini-*)
            if [ -z "${GEMINI_API_KEY:-}${GOOGLE_API_KEY:-}" ]; then
                echo "  FATAL: Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set."
                echo "  Set one with:  export GEMINI_API_KEY='your-key-here'"
                exit 1
            fi
            if [ -n "${GEMINI_API_KEY:-}" ]; then
                echo "  OK: GEMINI_API_KEY is set"
            else
                echo "  OK: GOOGLE_API_KEY is set"
            fi
            ;;
        claude-*)
            if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
                echo "  FATAL: ANTHROPIC_API_KEY is not set."
                echo "  Set it with:  export ANTHROPIC_API_KEY='your-key-here'"
                exit 1
            fi
            echo "  OK: ANTHROPIC_API_KEY is set"
            ;;
        azure-*)
            if [ -z "${AZURE_OPENAI_API_KEY:-}" ]; then
                echo "  FATAL: AZURE_OPENAI_API_KEY is not set."
                exit 1
            fi
            echo "  OK: AZURE_OPENAI_API_KEY is set"
            ;;
        groq-*)
            if [ -z "${GROQ_API_KEY:-}" ]; then
                echo "  FATAL: GROQ_API_KEY is not set."
                echo "  Set it with:  export GROQ_API_KEY='your-key-here'"
                exit 1
            fi
            echo "  OK: GROQ_API_KEY is set"
            ;;
        gpt-*|o1-*|o3-*|o4-*)
            if [ -z "${OPENAI_API_KEY:-}" ]; then
                echo "  FATAL: OPENAI_API_KEY is not set."
                exit 1
            fi
            echo "  OK: OPENAI_API_KEY is set"
            ;;
        *)
            echo "  WARNING: Unknown model prefix '$MODEL' — cannot verify API key."
            echo "  The pipeline will fail if the correct key is not set."
            ;;
    esac
}

# ── If we are NOT already inside tmux, launch ourselves in a new session ─────
if ! $INSIDE_TMUX; then
    # Check API key BEFORE launching tmux (fail fast with clear error)
    echo "--- Pre-launch API key check ---"
    check_api_key
    echo ""

    # Kill stale session if it exists
    tmux kill-session -t "$SESSION" 2>/dev/null || true

    # Ensure log directory exists
    mkdir -p "$(dirname "$LOGFILE")"

    # Build the inner command — pass MODEL, MODE, and --inside-tmux
    INNER_ARGS="\"$MODEL\""
    if [ "$MODE" = "passk" ]; then
        INNER_ARGS="\"$MODEL\" pass@k"
    fi

    # Create a new detached session that runs this script with --inside-tmux
    tmux new-session -d -s "$SESSION" -x 220 -y 50 \
        "bash \"$0\" $INNER_ARGS --inside-tmux 2>&1 | tee \"$LOGFILE\"; echo ''; echo '=== SESSION FINISHED ==='; read -r -p 'Press Enter to close...'"

    echo "Launched tmux session '$SESSION' ($MODE_DISPLAY)."
    echo ""
    echo "  Attach with:  tmux attach -t $SESSION"
    echo "  Log file:     $LOGFILE"
    echo ""
    echo "You can safely close this SSH connection — the session will keep running."
    exit 0
fi

# ── Inside tmux: do the real work ─────────────────────────────────────────────

# Trap SIGINT/SIGTERM for clean shutdown
trap 'echo ""; echo "INTERRUPTED at $(date -Iseconds)"; exit 130' INT TERM

echo "============================================================"
echo " $MODEL — ${MODE_DISPLAY^^}"
echo " $(date)"
echo " Repo: $PROJECT_ROOT"
echo "============================================================"
echo ""

# ── Activate venv ─────────────────────────────────────────────────────────────
source "$PROJECT_ROOT/env_parbench/bin/activate"
echo "[env] Python: $(python3 --version)"
echo ""

# ── Pre-flight: verify API key ───────────────────────────────────────────────
echo "--- Pre-flight checks ---"
check_api_key

# ── System info ───────────────────────────────────────────────────────────────
GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 || echo "N/A")
echo "  GPU: $GPU_NAME"
echo "  CUDA: $(nvcc --version 2>&1 | tail -1 || echo 'N/A')"
echo ""

# ── Configuration ─────────────────────────────────────────────────────────────
echo "Configuration:"
echo "  Mode: $MODE_DISPLAY"
echo "  Model: $MODEL"
echo "  Augment levels: $AUGMENT_LEVELS"
echo "  Max retries per task: $MAX_RETRIES"
echo "  Temperature: $TEMPERATURE"
echo "  Samples per task: $NUM_SAMPLES"
echo "  Total estimated tasks: $EXPECTED_TASKS"
echo ""

# ── Helper: run one suite+direction (with optional --kernels) ────────────────
run_batch() {
    local SUITE="$1"
    local DIR="$2"
    local BATCH_IDX="$3"
    local BATCH_TOTAL="$4"
    shift 4
    local KERNEL_ARGS=("$@")  # remaining args are kernel names (may be empty)

    echo "============================================================"
    echo " [Batch $BATCH_IDX/$BATCH_TOTAL] $SUITE: $DIR"
    if [ ${#KERNEL_ARGS[@]} -gt 0 ]; then
        echo "  Kernels: ${KERNEL_ARGS[*]}"
    fi
    echo "  Started: $(date -Iseconds)"
    echo "============================================================"

    local CMD=(python3 scripts/evaluation/run_eval_batch.py
        --suite "$SUITE"
        --direction "$DIR"
        --models $MODEL
        --augment-levels $AUGMENT_LEVELS
        --max-retries $MAX_RETRIES
        --temperature $TEMPERATURE
        --num-samples $NUM_SAMPLES
        --resume -v
        --project-root "$PROJECT_ROOT")

    if [ ${#KERNEL_ARGS[@]} -gt 0 ]; then
        CMD+=(--kernels "${KERNEL_ARGS[@]}")
    fi

    "${CMD[@]}"
    return $?
}

# ── HeCBench curated kernel lists ────────────────────────────────────────────
# 10 curated kernels for the SC26 paper narrative.
# HeCBench has 65+ kernels in manifest — MUST filter with --kernels.
#
# 5 kernels have cuda + omp (CPU OpenMP):
HECBENCH_OMP_KERNELS="stencil1d heat2d floydwarshall scan iso2dfd"
# 10 kernels have cuda + omp_target (GPU offload):
HECBENCH_OMP_TARGET_ALL="stencil1d heat2d floydwarshall page-rank scan jacobi nqueen md convolution1d iso2dfd"
# 8 kernels for cuda→omp_target (exclude stencil1d + scan: KNOWN_FAIL targets):
HECBENCH_OMP_TARGET_TARGETS="heat2d floydwarshall page-rank jacobi nqueen md convolution1d iso2dfd"

# ── Define all batches ───────────────────────────────────────────────────────
# Format: run_batch SUITE DIRECTION BATCH_IDX TOTAL [KERNEL1 KERNEL2 ...]
# Ordered: Rodinia first (largest), then smaller suites, HeCBench last
#
# Rodinia:   110 L0 task pairs (includes KNOWN_FAIL specs; ~14 extra vs ideal 96)
# XSBench:     6 L0 task pairs
# RSBench:     6 L0 task pairs
# mixbench:    6 L0 task pairs
# HeCBench:   30 L0 task pairs (includes iso2dfd manifest duplicate)
# ─────────────────────────────────────────────────────────
# 158 L0 pairs total
# Primary: × 5 levels × 1 sample = 790 tasks
# Pass@k:  × 1 level  × 3 samples = 474 tasks

TOTAL_BATCHES=28  # 6 rodinia + 6 xsbench + 6 rsbench + 6 mixbench + 4 hecbench = 28
BATCH_IDX=0
FAILED_BATCHES=()
FAILED_BATCH_CMDS=()
START_TIME=$(date +%s)

cd "$PROJECT_ROOT"

echo "Total batches: $TOTAL_BATCHES"
echo ""

run_and_track() {
    BATCH_IDX=$((BATCH_IDX + 1))
    local SUITE="$1"
    local DIR="$2"
    shift 2
    local KERNELS=("$@")

    set +e
    run_batch "$SUITE" "$DIR" "$BATCH_IDX" "$TOTAL_BATCHES" "${KERNELS[@]}"
    EXIT_CODE=$?
    set -e

    if [ "$EXIT_CODE" -ne 0 ]; then
        echo "  WARNING: $SUITE $DIR exited with code $EXIT_CODE — will retry in Pass 2"
        FAILED_BATCHES+=("$SUITE $DIR ${KERNELS[*]}")
    fi

    echo "  Completed: $(date -Iseconds)"
    echo ""
}

# ── Rodinia: 6 directions (96 L0 pairs) ─────────────────────────────────────
run_and_track rodinia cuda-to-omp
run_and_track rodinia omp-to-cuda
run_and_track rodinia cuda-to-opencl
run_and_track rodinia opencl-to-cuda
run_and_track rodinia omp-to-opencl
run_and_track rodinia opencl-to-omp

# ── XSBench: 6 directions (6 L0 pairs) ──────────────────────────────────────
run_and_track xsbench cuda-to-omp
run_and_track xsbench omp-to-cuda
run_and_track xsbench cuda-to-opencl
run_and_track xsbench opencl-to-cuda
run_and_track xsbench omp-to-opencl
run_and_track xsbench opencl-to-omp

# ── RSBench: 6 directions (6 L0 pairs) ──────────────────────────────────────
run_and_track rsbench cuda-to-omp
run_and_track rsbench omp-to-cuda
run_and_track rsbench cuda-to-opencl
run_and_track rsbench opencl-to-cuda
run_and_track rsbench omp-to-opencl
run_and_track rsbench opencl-to-omp

# ── mixbench: 6 directions (6 L0 pairs) ─────────────────────────────────────
run_and_track mixbench cuda-to-omp
run_and_track mixbench omp-to-cuda
run_and_track mixbench cuda-to-opencl
run_and_track mixbench opencl-to-cuda
run_and_track mixbench omp-to-opencl
run_and_track mixbench opencl-to-omp

# ── HeCBench: 4 directions (28 L0 pairs) ────────────────────────────────────
# cuda ↔ omp (CPU): 5 kernels with both APIs
run_and_track hecbench cuda-to-omp $HECBENCH_OMP_KERNELS
run_and_track hecbench omp-to-cuda $HECBENCH_OMP_KERNELS
# cuda → omp_target (GPU): 8 kernels (excludes stencil1d + scan KNOWN_FAIL targets)
run_and_track hecbench cuda-to-omp_target $HECBENCH_OMP_TARGET_TARGETS
# omp_target → cuda: all 10 kernels (KNOWN_FAIL specs are fine as sources)
run_and_track hecbench omp_target-to-cuda $HECBENCH_OMP_TARGET_ALL

# ── Pass 2: retry any failed batches ─────────────────────────────────────────
if [ "${#FAILED_BATCHES[@]}" -gt 0 ]; then
    echo "============================================================"
    echo " RETRY PASS: ${#FAILED_BATCHES[@]} batch(es) need retry"
    echo "============================================================"
    echo ""

    RETRY_STILL_FAILED=()
    for BATCH_ENTRY in "${FAILED_BATCHES[@]}"; do
        # Parse: "suite direction [kernel1 kernel2 ...]"
        read -r SUITE DIR KERNEL_STR <<< "$BATCH_ENTRY"
        read -r -a KERNEL_ARGS <<< "$KERNEL_STR"

        if [ ${#KERNEL_ARGS[@]} -gt 0 ]; then
            echo "--- Retrying: $SUITE $DIR (kernels: ${KERNEL_ARGS[*]}) ---"
        else
            echo "--- Retrying: $SUITE $DIR ---"
        fi
        set +e
        RETRY_CMD=(python3 scripts/evaluation/run_eval_batch.py
            --suite "$SUITE"
            --direction "$DIR"
            --models $MODEL
            --augment-levels $AUGMENT_LEVELS
            --max-retries $MAX_RETRIES
            --temperature $TEMPERATURE
            --num-samples $NUM_SAMPLES
            --resume -v
            --project-root "$PROJECT_ROOT")
        if [ ${#KERNEL_ARGS[@]} -gt 0 ]; then
            RETRY_CMD+=(--kernels "${KERNEL_ARGS[@]}")
        fi
        "${RETRY_CMD[@]}"
        EXIT_CODE=$?
        set -e
        if [ "$EXIT_CODE" -ne 0 ]; then
            echo "  FAIL: Still failing: $SUITE $DIR"
            RETRY_STILL_FAILED+=("$BATCH_ENTRY")
        else
            echo "  OK: Retry succeeded: $SUITE $DIR"
        fi
        echo ""
    done
    FAILED_BATCHES=("${RETRY_STILL_FAILED[@]}")
fi

# ── Completeness check ──────────────────────────────────────────────────────
echo "============================================================"
echo " COMPLETENESS CHECK"
echo "============================================================"

TOTAL_FILES=0
for SUITE in rodinia xsbench rsbench mixbench hecbench; do
    COUNT=$(ls "$PROJECT_ROOT/results/evaluation/$MODEL"/${SUITE}-*-to-${SUITE}-*.json 2>/dev/null | wc -l || echo 0)
    echo "  $SUITE: $COUNT files"
    TOTAL_FILES=$((TOTAL_FILES + COUNT))
done
echo "  Total: $TOTAL_FILES / $EXPECTED_TASKS expected"
echo ""

# ── Regenerate analysis ──────────────────────────────────────────────────────
echo "============================================================"
echo " REGENERATING ANALYSIS"
echo "============================================================"

set +e
python3 scripts/evaluation/analyze_eval.py \
    --project-root "$PROJECT_ROOT" \
    --write-dashboard
ANALYZE_EXIT=$?
set -e

if [ "$ANALYZE_EXIT" -ne 0 ]; then
    echo "  WARNING: analyze_eval.py exited with code $ANALYZE_EXIT"
fi
echo ""

# ── Summary ──────────────────────────────────────────────────────────────────
echo "============================================================"
echo " RESULTS SUMMARY"
echo "============================================================"
echo ""

python3 - "$MODEL" << 'PYEOF'
import json, glob, os, sys

MODEL = sys.argv[1]
BASE = "{{PROJECT_ROOT}}"
MODEL_DIR = f"{BASE}/results/evaluation/{MODEL}"

if not os.path.isdir(MODEL_DIR):
    print(f"  No results directory found: {MODEL_DIR}")
    exit(0)

files = glob.glob(f"{MODEL_DIR}/*.json")
results = []
for f in files:
    try:
        results.append(json.loads(open(f).read()))
    except:
        pass

# Status breakdown
status_counts = {}
for r in results:
    s = r.get("overall_status", "UNKNOWN")
    status_counts[s] = status_counts.get(s, 0) + 1

total = len(results)
passes = status_counts.get("PASS", 0)
pct = 100 * passes / total if total else 0

print(f"  Total results: {total}")
print(f"  PASS: {passes}/{total} ({pct:.1f}%)")
print()
print("  Status breakdown:")
for s, n in sorted(status_counts.items(), key=lambda x: -x[1]):
    print(f"    {s}: {n}")

# Per-suite breakdown
print()
print("  Per-suite breakdown:")
suite_counts = {}
for r in results:
    src = r.get("source_spec", "")
    suite = src.split("-")[0] if src else "unknown"
    if suite not in suite_counts:
        suite_counts[suite] = {"total": 0, "pass": 0}
    suite_counts[suite]["total"] += 1
    if r.get("overall_status") == "PASS":
        suite_counts[suite]["pass"] += 1

for suite in sorted(suite_counts):
    sc = suite_counts[suite]
    pct = 100 * sc["pass"] / sc["total"] if sc["total"] else 0
    print(f"    {suite}: {sc['pass']}/{sc['total']} PASS ({pct:.1f}%)")

# Per-direction L0 breakdown
print()
print("  Per-direction L0 breakdown:")
dir_counts = {}
for r in results:
    level = r.get("augment_level", 0)
    if level != 0:
        continue
    src = r.get("source_spec", "")
    tgt = r.get("target_spec", "")
    if not src or not tgt:
        continue
    src_api = src.rsplit("-", 1)[-1]
    tgt_api = tgt.rsplit("-", 1)[-1]
    direction = f"{src_api}-to-{tgt_api}"
    if direction not in dir_counts:
        dir_counts[direction] = {"total": 0, "pass": 0}
    dir_counts[direction]["total"] += 1
    if r.get("overall_status") == "PASS":
        dir_counts[direction]["pass"] += 1

for d in sorted(dir_counts):
    dc = dir_counts[d]
    pct = 100 * dc["pass"] / dc["total"] if dc["total"] else 0
    print(f"    {d}: {dc['pass']}/{dc['total']} PASS ({pct:.1f}%)")

PYEOF

# ── Write done marker ────────────────────────────────────────────────────────
END_TIME=$(date +%s)
ELAPSED=$(( (END_TIME - START_TIME) / 60 ))

{
    echo "COMPLETED $(date -Iseconds)"
    echo "MODEL=$MODEL"
    echo "MODE=$MODE_DISPLAY"
    echo "FILES=$TOTAL_FILES/$EXPECTED_TASKS"
    echo "ELAPSED=${ELAPSED}m"
    if [ "${#FAILED_BATCHES[@]}" -gt 0 ]; then
        echo "FAILED_BATCHES=${FAILED_BATCHES[*]}"
    else
        echo "FAILED_BATCHES=none"
    fi
} > "$DONE_MARKER"

# ── Final banner ─────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo " ${MODE_DISPLAY^^} COMPLETE — $(date)"
echo " Model: $MODEL"
echo " Total results: $TOTAL_FILES / $EXPECTED_TASKS"
echo " Elapsed: ${ELAPSED} minutes"
if [ "${#FAILED_BATCHES[@]}" -gt 0 ]; then
    echo " WARNING: Batches still failed after retry: ${FAILED_BATCHES[*]}"
    if [ "$MODE" = "passk" ]; then
        echo " Re-run:  bash scripts/batch/run_eval_campaign.sh $MODEL pass@k"
    else
        echo " Re-run:  bash scripts/batch/run_eval_campaign.sh $MODEL"
    fi
    echo " (--resume will skip completed tasks)"
else
    echo " All batches completed successfully."
fi
echo " Log:  $LOGFILE"
echo " Done: $DONE_MARKER"
echo "============================================================"
