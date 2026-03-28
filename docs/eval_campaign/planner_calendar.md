# Evaluation Campaign — Execution Calendar

**Created:** 2026-03-28
**Deadline:** April 8, 2026 (SC26 submission)
**Total Missing Tasks:** 1,152 of 1,530

---

## Infrastructure Summary

### CLI Reference (from `run_eval_batch.py`)

```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite <suite>              # rodinia | xsbench (ALWAYS pass to avoid cross-suite collisions)
  --direction <src-to-tgt>     # e.g. cuda-to-opencl
  --models <model1> [model2..] # space-separated model IDs
  --kernels <k1> [k2..]       # optional: restrict to specific kernels
  --augment-levels <0> [1..]   # default [0]; use "1 2 3 4" for augmented
  --max-retries <N>            # default 1 (zero-shot); use 3 for production
  --resume                     # default ON; skips existing non-ERROR/non-EXTRACTION_FAIL results
  --project-root <path>        # ALWAYS pass explicitly
  -v                           # verbose
```

### Key Behaviors
- `--resume` (default: True) skips tasks with existing PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL results
- `--resume` retries ERROR and EXTRACTION_FAIL results automatically
- Results written to: `results/evaluation/{model}/{src_id}-to-{tgt_id}[-L{n}].json`
- All models use same model IDs: `claude-sonnet-4-6`, `gemini-2.5-flash-lite`, `groq-llama-3.3-70b-versatile`

### Batch Script Pattern (from existing scripts)
- Self-launching tmux sessions for SSH-safe execution
- Pre-flight checks: API keys (ANTHROPIC_API_KEY, GEMINI_API_KEY, GROQ_API_KEY), GPU, venv
- `set +e` around python calls (non-zero exit = some failures, not script abort)
- Completeness check after each pass
- Analysis regeneration at end

---

## Eligible Kernel Lists (Verified from Specs on Disk)

### cuda-to-opencl / opencl-to-cuda (17 kernels each)
Both CUDA and OpenCL specs exist. Excludes: hybridsort (KNOWN_FAIL), kmeans (KNOWN_FAIL), nn (KNOWN_FAIL).
Includes dwt2d and gaussian (have CUDA+OpenCL specs, no OMP spec).

```
backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster
```

### omp-to-opencl / opencl-to-omp (15 kernels each)
Both OMP and OpenCL specs exist. Excludes: kmeans (KNOWN_FAIL), nn (KNOWN_FAIL).
No dwt2d/gaussian (no OMP specs for these).

```
backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster
```

### omp-to-cuda (16 kernels — L0 complete, needs L1-L4)
Both OMP and CUDA specs exist. Excludes: kmeans (KNOWN_FAIL), mummergpu (KNOWN_FAIL).

```
backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster
```

---

## Phase 0: Canary Test (~15 min)

**Goal:** Verify OpenCL build environment works end-to-end before committing to 1,152 tasks.

### Step 0a: Verify OpenCL specs build/run/verify natively
```bash
source env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Test 3 diverse OpenCL specs (simple, stencil, graph)
python3 -m harness -v verify specs/rodinia-bfs-opencl.json
python3 -m harness -v verify specs/rodinia-hotspot-opencl.json
python3 -m harness -v verify specs/rodinia-backprop-opencl.json
```

**Expected:** All 3 PASS. If any fail, OpenCL toolchain needs fixing before proceeding.

### Step 0b: Single end-to-end LLM translation
```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-opencl \
  --models claude-sonnet-4-6 \
  --kernels bfs \
  --augment-levels 0 \
  --max-retries 3 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v
```

**Expected:** 1 task completes (PASS, BUILD_FAIL, or VERIFY_FAIL — any deterministic outcome is acceptable). If ERROR or EXTRACTION_FAIL, investigate LLM prompt/extraction issues before scaling.

### Step 0c: Verify all 3 models can connect
```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-opencl \
  --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
  --kernels bfs \
  --augment-levels 0 \
  --max-retries 3 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v
```

**Expected:** 3 tasks complete. Verifies all API keys are valid and models respond.

**GO/NO-GO gate:** All 3 models produce deterministic results. Proceed to Phase 1.

---

## Phase 1: L0 Baselines for 4 New OpenCL Directions (192 tasks)

**Goal:** Establish L0 pass rates for all 4 OpenCL-involving directions.

### Task Breakdown

| Direction | Kernels | × Models | = Tasks |
|-----------|---------|----------|---------|
| cuda-to-opencl L0 | 17 | 3 | 51 |
| opencl-to-cuda L0 | 17 | 3 | 51 |
| omp-to-opencl L0 | 15 | 3 | 45 |
| opencl-to-omp L0 | 15 | 3 | 45 |
| **Total** | | | **192** |

### Batch Script: `scripts/batch/run_phase1_opencl_l0.sh`

```bash
#!/usr/bin/env bash
# Phase 1: L0 baselines for all 4 OpenCL directions
# 192 tasks: (17+17+15+15) kernels × 3 models × L0
# Estimated: ~4.8 hours wall-clock (192 tasks × 90s avg)
# Split into 4 sequential passes (one per direction)

set -euo pipefail

PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
SESSION="eval_phase1"
LOGFILE="$PROJECT_ROOT/results/evaluation/phase1_opencl_l0.log"

# ── If NOT in tmux, launch self in tmux ─────────────────────────────────────
if [[ -z "${TMUX:-}" ]]; then
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    mkdir -p "$(dirname "$LOGFILE")"
    tmux new-session -d -s "$SESSION" -x 220 -y 50 \
        "bash \"$0\" --inside-tmux 2>&1 | tee \"$LOGFILE\"; echo ''; echo '=== PHASE 1 FINISHED ==='; read -r -p 'Press Enter to close...'"
    echo "Launched tmux session '$SESSION'. Attach with: tmux attach -t $SESSION"
    exit 0
fi

trap 'echo ""; echo "INTERRUPTED at $(date -Iseconds)"; exit 130' INT TERM

echo "============================================================"
echo " Phase 1: OpenCL L0 Baselines — $(date)"
echo "============================================================"

source "$PROJECT_ROOT/env_parbench/bin/activate"

# Pre-flight
for VAR in ANTHROPIC_API_KEY GEMINI_API_KEY GROQ_API_KEY; do
    if [ -z "${!VAR:-}" ]; then echo "FATAL: $VAR not set"; exit 1; fi
done

MODELS="claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile"
MAX_RETRIES=3
START_TIME=$(date +%s)

cd "$PROJECT_ROOT"

# ── Direction 1: cuda-to-opencl (51 tasks) ──────────────────────────────────
echo ""
echo "=== Direction 1/4: cuda-to-opencl (17 kernels × 3 models = 51 tasks) ==="
echo "Started: $(date -Iseconds)"

set +e
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction cuda-to-opencl \
    --models $MODELS \
    --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 \
    --max-retries $MAX_RETRIES \
    --project-root "$PROJECT_ROOT" \
    --resume -v
D1_EXIT=$?
set -e
echo "cuda-to-opencl finished: exit=$D1_EXIT at $(date -Iseconds)"

# ── Direction 2: opencl-to-cuda (51 tasks) ──────────────────────────────────
echo ""
echo "=== Direction 2/4: opencl-to-cuda (17 kernels × 3 models = 51 tasks) ==="
echo "Started: $(date -Iseconds)"

set +e
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction opencl-to-cuda \
    --models $MODELS \
    --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 \
    --max-retries $MAX_RETRIES \
    --project-root "$PROJECT_ROOT" \
    --resume -v
D2_EXIT=$?
set -e
echo "opencl-to-cuda finished: exit=$D2_EXIT at $(date -Iseconds)"

# ── Direction 3: omp-to-opencl (45 tasks) ───────────────────────────────────
echo ""
echo "=== Direction 3/4: omp-to-opencl (15 kernels × 3 models = 45 tasks) ==="
echo "Started: $(date -Iseconds)"

set +e
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction omp-to-opencl \
    --models $MODELS \
    --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 \
    --max-retries $MAX_RETRIES \
    --project-root "$PROJECT_ROOT" \
    --resume -v
D3_EXIT=$?
set -e
echo "omp-to-opencl finished: exit=$D3_EXIT at $(date -Iseconds)"

# ── Direction 4: opencl-to-omp (45 tasks) ───────────────────────────────────
echo ""
echo "=== Direction 4/4: opencl-to-omp (15 kernels × 3 models = 45 tasks) ==="
echo "Started: $(date -Iseconds)"

set +e
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction opencl-to-omp \
    --models $MODELS \
    --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 \
    --max-retries $MAX_RETRIES \
    --project-root "$PROJECT_ROOT" \
    --resume -v
D4_EXIT=$?
set -e
echo "opencl-to-omp finished: exit=$D4_EXIT at $(date -Iseconds)"

# ── Completeness check ──────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo " PHASE 1 COMPLETENESS CHECK"
echo "============================================================"

for DIR in cuda-to-opencl opencl-to-cuda omp-to-opencl opencl-to-omp; do
    echo "Direction: $DIR"
    for MODEL in claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile; do
        COUNT=$(ls "$PROJECT_ROOT/results/evaluation/$MODEL"/rodinia-*-${DIR//-to-*}-to-rodinia-*-${DIR/*-to-/}.json 2>/dev/null | wc -l || echo 0)
        echo "  $MODEL: $COUNT files"
    done
done

END_TIME=$(date +%s)
ELAPSED=$(( (END_TIME - START_TIME) / 60 ))
echo ""
echo "Phase 1 total elapsed: ${ELAPSED} minutes"
echo "Exit codes: D1=$D1_EXIT D2=$D2_EXIT D3=$D3_EXIT D4=$D4_EXIT"
```

### Time & Cost Estimate

| Resource | Calculation | Estimate |
|----------|-------------|----------|
| Wall-clock | 192 tasks × 90s = 17,280s | ~4.8 hours |
| Claude API | 51 tasks × $0.045 | $2.30 |
| Gemini API | 51 tasks × $0.001 | $0.05 |
| Groq API | 51 tasks × $0.005 | $0.26 |
| **Total cost** | | **~$2.60** |

**With resume:** If interrupted and restarted, only unfinished tasks run. Safe to re-execute.

---

## Phase 2: L1-L4 Augmentation Expansion (960 tasks)

**Goal:** Fill all augmented-level gaps across 5 directions.

### Task Breakdown

| Direction | Kernels | × Models | × Levels | = Tasks |
|-----------|---------|----------|----------|---------|
| omp-to-cuda L1-L4 | 16 | 3 | 4 | 192 |
| cuda-to-opencl L1-L4 | 17 | 3 | 4 | 204 |
| opencl-to-cuda L1-L4 | 17 | 3 | 4 | 204 |
| omp-to-opencl L1-L4 | 15 | 3 | 4 | 180 |
| opencl-to-omp L1-L4 | 15 | 3 | 4 | 180 |
| **Total** | | | | **960** |

### Execution Strategy

Split into 2 tmux windows to allow some parallelism:
- **Window 0:** omp-to-cuda + cuda-to-opencl (396 tasks)
- **Window 1:** opencl-to-cuda + omp-to-opencl + opencl-to-omp (564 tasks)

Each direction runs L1+L2 then L3+L4 (2 passes, matching existing batch pattern).

### Batch Script: `scripts/batch/run_phase2_augmented.sh`

```bash
#!/usr/bin/env bash
# Phase 2: L1-L4 augmented evaluations for 5 directions
# 960 tasks total, split into 2 tmux windows
# Estimated: ~12 hours wall-clock per window (sequential)

set -euo pipefail

PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
SESSION="eval_phase2"
LOGDIR="$PROJECT_ROOT/results/evaluation"

if [[ -z "${TMUX:-}" ]]; then
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    mkdir -p "$LOGDIR"
    tmux new-session -d -s "$SESSION" -n win0 -x 220 -y 50
    tmux send-keys -t "$SESSION":win0 "bash \"$0\" --window0 2>&1 | tee $LOGDIR/phase2_win0.log" C-m
    tmux new-window -t "$SESSION" -n win1
    tmux send-keys -t "$SESSION":win1 "bash \"$0\" --window1 2>&1 | tee $LOGDIR/phase2_win1.log" C-m
    echo "Launched tmux session '$SESSION' with 2 windows."
    echo "  Attach: tmux attach -t $SESSION"
    echo "  Switch: Ctrl-B 0 / Ctrl-B 1"
    exit 0
fi

source "$PROJECT_ROOT/env_parbench/bin/activate"
for VAR in ANTHROPIC_API_KEY GEMINI_API_KEY GROQ_API_KEY; do
    if [ -z "${!VAR:-}" ]; then echo "FATAL: $VAR not set"; exit 1; fi
done

MODELS="claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile"
MAX_RETRIES=3

cd "$PROJECT_ROOT"

# ── Window 0: omp-to-cuda + cuda-to-opencl (396 tasks) ─────────────────────
if [[ "${1:-}" == "--window0" ]]; then
    echo "=== Window 0: omp-to-cuda L1-L4 + cuda-to-opencl L1-L4 ==="
    echo "Started: $(date -Iseconds)"

    # omp-to-cuda L1+L2 (96 tasks)
    echo "--- omp-to-cuda L1+L2 (16 × 3 × 2 = 96 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction omp-to-cuda \
        --models $MODELS \
        --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
        --augment-levels 1 2 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    # omp-to-cuda L3+L4 (96 tasks)
    echo "--- omp-to-cuda L3+L4 (16 × 3 × 2 = 96 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction omp-to-cuda \
        --models $MODELS \
        --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
        --augment-levels 3 4 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    # cuda-to-opencl L1+L2 (102 tasks)
    echo "--- cuda-to-opencl L1+L2 (17 × 3 × 2 = 102 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction cuda-to-opencl \
        --models $MODELS \
        --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
        --augment-levels 1 2 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    # cuda-to-opencl L3+L4 (102 tasks)
    echo "--- cuda-to-opencl L3+L4 (17 × 3 × 2 = 102 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction cuda-to-opencl \
        --models $MODELS \
        --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
        --augment-levels 3 4 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    echo "=== Window 0 COMPLETE at $(date -Iseconds) ==="
    exit 0
fi

# ── Window 1: opencl-to-cuda + omp-to-opencl + opencl-to-omp (564 tasks) ───
if [[ "${1:-}" == "--window1" ]]; then
    echo "=== Window 1: opencl-to-cuda + omp-to-opencl + opencl-to-omp L1-L4 ==="
    echo "Started: $(date -Iseconds)"

    # opencl-to-cuda L1+L2 (102 tasks)
    echo "--- opencl-to-cuda L1+L2 (17 × 3 × 2 = 102 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction opencl-to-cuda \
        --models $MODELS \
        --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
        --augment-levels 1 2 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    # opencl-to-cuda L3+L4 (102 tasks)
    echo "--- opencl-to-cuda L3+L4 (17 × 3 × 2 = 102 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction opencl-to-cuda \
        --models $MODELS \
        --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
        --augment-levels 3 4 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    # omp-to-opencl L1+L2 (90 tasks)
    echo "--- omp-to-opencl L1+L2 (15 × 3 × 2 = 90 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction omp-to-opencl \
        --models $MODELS \
        --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
        --augment-levels 1 2 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    # omp-to-opencl L3+L4 (90 tasks)
    echo "--- omp-to-opencl L3+L4 (15 × 3 × 2 = 90 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction omp-to-opencl \
        --models $MODELS \
        --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
        --augment-levels 3 4 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    # opencl-to-omp L1+L2 (90 tasks)
    echo "--- opencl-to-omp L1+L2 (15 × 3 × 2 = 90 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction opencl-to-omp \
        --models $MODELS \
        --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
        --augment-levels 1 2 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    # opencl-to-omp L3+L4 (90 tasks)
    echo "--- opencl-to-omp L3+L4 (15 × 3 × 2 = 90 tasks) ---"
    set +e
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction opencl-to-omp \
        --models $MODELS \
        --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
        --augment-levels 3 4 \
        --max-retries $MAX_RETRIES \
        --project-root "$PROJECT_ROOT" \
        --resume -v
    set -e

    echo "=== Window 1 COMPLETE at $(date -Iseconds) ==="
    exit 0
fi

echo "Usage: $0 (auto-launches tmux) or $0 --window0|--window1 (run one window)"
```

### Time & Cost Estimate

| Resource | Per Window | Total |
|----------|-----------|-------|
| Wall-clock (Window 0, 396 tasks) | 396 × 90s = 9.9h | |
| Wall-clock (Window 1, 564 tasks) | 564 × 90s = 14.1h | |
| **Effective wall-clock (parallel)** | | **~14.1 hours** |
| Claude API | 320 tasks × $0.045 | $14.40 |
| Gemini API | 320 tasks × $0.001 | $0.32 |
| Groq API | 320 tasks × $0.005 | $1.60 |
| **Total cost** | | **~$16.32** |

**Note:** 320 = 960 / 3 models; each model evaluates 1/3 of total tasks.

---

## Phase 3: EXTRACTION_FAIL Retries + Statistical Analysis (~23 tasks + analysis)

**Goal:** Recover transient failures and run comprehensive analysis.

### Step 3a: EXTRACTION_FAIL retry pass

`--resume` already retries EXTRACTION_FAIL automatically. Re-running any Phase 1/2 batch
script will retry these. For targeted retry:

```bash
source env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Re-run all Phase 1 directions (only EXTRACTION_FAIL and ERROR will retry)
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction cuda-to-opencl \
    --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
    --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 1 2 3 4 \
    --max-retries 3 \
    --project-root /home/samyak/Desktop/parbench_sam \
    --resume -v

# Repeat for other directions...
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction opencl-to-cuda \
    --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
    --kernels backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 1 2 3 4 \
    --max-retries 3 \
    --project-root /home/samyak/Desktop/parbench_sam \
    --resume -v

python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction omp-to-opencl \
    --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
    --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 1 2 3 4 \
    --max-retries 3 \
    --project-root /home/samyak/Desktop/parbench_sam \
    --resume -v

python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction opencl-to-omp \
    --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
    --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 1 2 3 4 \
    --max-retries 3 \
    --project-root /home/samyak/Desktop/parbench_sam \
    --resume -v

python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction omp-to-cuda \
    --models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
    --kernels backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster \
    --augment-levels 0 1 2 3 4 \
    --max-retries 3 \
    --project-root /home/samyak/Desktop/parbench_sam \
    --resume -v
```

### Step 3b: Run comprehensive analysis
```bash
python3 scripts/evaluation/analyze_eval.py \
    --project-root /home/samyak/Desktop/parbench_sam \
    --write-dashboard \
    --show-gaps \
    --expected-models claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile \
    --expected-directions cuda-to-omp omp-to-cuda cuda-to-opencl opencl-to-cuda omp-to-opencl opencl-to-omp \
    --expected-levels 0 1 2 3 4
```

### Step 3c: Completeness audit
```bash
python3 -c "
import json, glob, os

BASE = '/home/samyak/Desktop/parbench_sam/results/evaluation'
models = ['claude-sonnet-4-6', 'gemini-2.5-flash-lite', 'groq-llama-3.3-70b-versatile']
directions = {
    'cuda-to-omp':    {'kernels': 17, 'levels': [0,1,2,3,4]},
    'omp-to-cuda':    {'kernels': 16, 'levels': [0,1,2,3,4]},
    'cuda-to-opencl': {'kernels': 17, 'levels': [0,1,2,3,4]},
    'opencl-to-cuda': {'kernels': 17, 'levels': [0,1,2,3,4]},
    'omp-to-opencl':  {'kernels': 15, 'levels': [0,1,2,3,4]},
    'opencl-to-omp':  {'kernels': 15, 'levels': [0,1,2,3,4]},
}

total_expected = 0
total_found = 0
total_pass = 0
total_extraction_fail = 0

for direction, info in directions.items():
    src_api, tgt_api = direction.split('-to-')
    for model in models:
        for level in info['levels']:
            tag = f'-L{level}' if level > 0 else ''
            pattern = f'{BASE}/{model}/rodinia-*-{src_api}-to-rodinia-*-{tgt_api}{tag}.json'
            files = glob.glob(pattern)
            expected = info['kernels']
            total_expected += expected
            total_found += len(files)
            for f in files:
                try:
                    r = json.loads(open(f).read())
                    if r.get('overall_status') == 'PASS':
                        total_pass += 1
                    elif r.get('overall_status') == 'EXTRACTION_FAIL':
                        total_extraction_fail += 1
                except:
                    pass

print(f'Total expected: {total_expected}')
print(f'Total found:    {total_found}')
print(f'Total PASS:     {total_pass}')
print(f'EXTRACTION_FAIL: {total_extraction_fail}')
print(f'Coverage:       {100*total_found/total_expected:.1f}%')
"
```

### Time & Cost Estimate
- ~23 retries × 90s = ~35 min wall-clock
- Analysis scripts: ~5 min
- **Total: ~40 min, ~$0.50**

---

## Phase 4: Third Benchmark (Parboil) — GO/NO-GO after Phase 2

**Depends on:** Phase 2 completion + Implementor's `add_parboil_suite()` code
**Decision point:** If Phase 2 reveals systematic OpenCL failures, fixing those takes priority.

This phase is designed but NOT scheduled. The team lead will issue GO/NO-GO based on:
1. Phase 2 pass rates (if <10% overall, OpenCL pipeline needs debugging first)
2. Time remaining vs. paper writing deadline
3. Parboil source availability and spec generation readiness

If GO: estimated 6-8 hours for Parboil L0 across all directions + 3 models.

---

## Phase 5: Pass@k Pilot — GO/NO-GO after Phase 3

**Depends on:** Statistician's framework, Phase 3 results
**Decision point:** Only if Phase 3 shows >20% overall pass rate (otherwise Pass@k adds noise).

Pilot: 3 kernels × 3 models × 5 repetitions × 1 direction = 45 tasks.
Full: Would require `temperature>0` API calls, separate result directories.

---

## Timeline Mapping

### Calendar (March 28 - April 8)

```
Day 11 (Mar 28, Sat) — TODAY
  [x] Canary test: Phase 0 (15 min)
  [x] Launch Phase 1 batch script in tmux

Day 12 (Mar 29, Sun)
  [ ] Phase 1 completes (~4.8h from launch)
  [ ] Review Phase 1 results, sanity check pass rates
  [ ] Launch Phase 2 batch script (2 tmux windows)

Day 13 (Mar 30, Mon)
  [ ] Phase 2 running (Window 1 may still be executing)
  [ ] Begin paper data table drafting with Phase 1 L0 results

Day 14 (Mar 31, Tue)
  [ ] Phase 2 completes (~14h from launch)
  [ ] Phase 3: EXTRACTION_FAIL retries + analysis
  [ ] GO/NO-GO decision on Phase 4 (Parboil)

Day 15 (Apr 1, Wed) — EVAL EXECUTION DEADLINE
  [ ] All eval data frozen
  [ ] Final analysis run: eval_summary.json + eval_summary.md
  [ ] Dashboard refresh: generate_viz_data.py
  [ ] GO/NO-GO on Pass@k pilot

Day 16 (Apr 2, Thu) — LATEX TRANSFER BEGINS
  [ ] Data tables → LaTeX
  [ ] Figures generated from eval_summary data

Day 17 (Apr 3, Fri)
  [ ] Paper sections S5 (Methodology) + S6 (Results) drafted

Day 18 (Apr 4, Sat) — PAPER WRITING BEGINS
  [ ] Full draft assembly

Day 19-20 (Apr 5-6, Sun-Mon)
  [ ] Paper revision, related work integration

Day 21 (Apr 7, Tue)
  [ ] Final review, camera-ready prep

Day 22 (Apr 8, Wed) — SC26 SUBMISSION DEADLINE
```

### Critical Path

```
Phase 0 (15 min) → Phase 1 (4.8h) → Phase 2 (14h) → Phase 3 (40 min) → Analysis
                                                                           ↓
                                                              Paper data tables ready
```

**Total execution time:** ~20 hours wall-clock (with 2-window parallelism in Phase 2)
**Total estimated cost:** ~$19.50 across all 3 model APIs
**Buffer:** 1.5 days between eval completion (Mar 31) and deadline (Apr 1)

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| OpenCL build failures | Phase 0 canary catches before 192 tasks |
| API rate limits | Sequential per-model execution; `--resume` recovers |
| SSH disconnect | tmux sessions persist across disconnects |
| Phase 2 runs long | Window 0 (396 tasks) finishes first; can start analysis on its data |
| Groq token limits | myocyte/heartwall may EXTRACTION_FAIL for groq; expected, not blocking |
| Power outage / GPU crash | `--resume` makes all phases restartable from any point |

---

## Quick Reference: Copy-Paste Commands

### Launch Phase 0 (canary)
```bash
source env_parbench/bin/activate && cd /home/samyak/Desktop/parbench_sam
python3 -m harness -v verify specs/rodinia-bfs-opencl.json
python3 -m harness -v verify specs/rodinia-hotspot-opencl.json
python3 -m harness -v verify specs/rodinia-backprop-opencl.json
```

### Launch Phase 1
```bash
bash scripts/batch/run_phase1_opencl_l0.sh
```

### Launch Phase 2
```bash
bash scripts/batch/run_phase2_augmented.sh
```

### Monitor progress
```bash
tmux attach -t eval_phase1   # or eval_phase2
# Ctrl-B D to detach
```

### Quick completeness check (any time)
```bash
for d in cuda-to-opencl opencl-to-cuda omp-to-opencl opencl-to-omp; do
  echo "=== $d ===";
  for m in claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile; do
    src=${d%%-to-*}; tgt=${d##*-to-};
    l0=$(ls results/evaluation/$m/rodinia-*-${src}-to-rodinia-*-${tgt}.json 2>/dev/null | wc -l);
    aug=$(ls results/evaluation/$m/rodinia-*-${src}-to-rodinia-*-${tgt}-L*.json 2>/dev/null | wc -l);
    echo "  $m: L0=$l0 L1-L4=$aug";
  done;
done
```
