#!/usr/bin/env bash
# Run full harness pipeline (build → run → verify) for all 40 new OMP kernels
# Skip: convolution3d (no OMP dir), convolutionseparable (no Makefile.aomp, Batch 1), simplespmv (no Makefile.aomp, Batch 1)

set -euo pipefail

PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
LOG_DIR="$PROJECT_ROOT/results/phase3/omp_batch_logs"
SUMMARY="$LOG_DIR/_summary.tsv"

cd "$PROJECT_ROOT"
source env_parbench/bin/activate

mkdir -p "$LOG_DIR"

# 40 OMP kernels (Batch 2 + Batch 3, excluding convolution3d which has no OMP dir)
KERNELS=(
  # Batch 2 (20)
  babelstream backprop ccsd-trpdrv deredundancy feynman-kac
  fpc ga keccaktreehash laplace3d lulesh
  maxpool3d md5hash pathfinder pso rmsnorm
  secp256k1 softmax-online thomas tissue tsp
  # Batch 3 (19, excluding convolution3d — no OMP dir)
  bezier-surface crc64 floydwarshall gaussian
  geglu heat2d iso2dfd jenkins-hash knn
  mandelbrot mis murmurhash3 myocyte nw
  perplexity popcount sobol stencil1d triad
)

TOTAL=${#KERNELS[@]}

# Header for summary TSV
echo -e "#\tKernel\tBuild\tBuild_Time\tRun\tRun_Time\tRun_Exit\tVerify\tVerify_Strategy\tStdout_First5" > "$SUMMARY"

echo "========================================"
echo "Starting OMP harness run: $TOTAL kernels"
echo "Time: $(date -Iseconds)"
echo "========================================"

IDX=0
PASS_COUNT=0
FAIL_COUNT=0
BUILD_FAIL=0
RUN_FAIL=0

for KERNEL in "${KERNELS[@]}"; do
  IDX=$((IDX + 1))
  SPEC="specs/hecbench-${KERNEL}-omp.json"
  LOGFILE="$LOG_DIR/${KERNEL}.log"
  JSONFILE="$LOG_DIR/${KERNEL}.json"

  echo ""
  echo "[$IDX/$TOTAL] Running: $KERNEL ..."
  echo "  Spec: $SPEC"
  echo "  Log:  $LOGFILE"
  echo "  Time: $(date -Iseconds)"

  set +e
  OUTPUT=$(python -m harness --json -v verify "$SPEC" --config correctness 2>&1)
  EXIT_CODE=$?
  set -e

  echo "$OUTPUT" > "$LOGFILE"

  JSON_BLOCK=$(echo "$OUTPUT" | sed -n '/^{/,/^}/p')
  if [ -n "$JSON_BLOCK" ]; then
    echo "$JSON_BLOCK" > "$JSONFILE"
  fi

  SUMMARY_LINE=$(echo "$OUTPUT" | grep '^\[hecbench-' | head -1)

  BUILD_STATUS=$(echo "$SUMMARY_LINE" | grep -oP 'BUILD: \K\w+' || echo "UNKNOWN")
  BUILD_TIME=$(echo "$SUMMARY_LINE" | grep -oP 'BUILD: \w+ \(\K[0-9.]+' || echo "0")
  RUN_STATUS=$(echo "$SUMMARY_LINE" | grep -oP 'RUN\([^)]+\): \K\w+' || echo "UNKNOWN")
  RUN_TIME=$(echo "$SUMMARY_LINE" | grep -oP 'RUN\([^)]+\): \w+ \(\K[0-9.]+' || echo "0")
  VERIFY_STATUS=$(echo "$SUMMARY_LINE" | grep -oP 'VERIFY: \K\w+' || echo "UNKNOWN")
  VERIFY_STRATEGY=$(echo "$SUMMARY_LINE" | grep -oP 'VERIFY: \w+ \(\K[^)]+' || echo "unknown")

  RUN_EXIT=$(echo "$JSON_BLOCK" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('runs',{}).get('correctness',{}).get('exit_code','?'))" 2>/dev/null || echo "?")

  STDOUT_FIRST5=$(echo "$JSON_BLOCK" | python3 -c "
import sys, json
d = json.load(sys.stdin)
stdout = d.get('runs',{}).get('correctness',{}).get('stdout','')
lines = stdout.strip().split('\n')[:5]
print(' | '.join(lines))
" 2>/dev/null || echo "(no stdout)")

  echo -e "${IDX}\t${KERNEL}\t${BUILD_STATUS}\t${BUILD_TIME}s\t${RUN_STATUS}\t${RUN_TIME}s\t${RUN_EXIT}\t${VERIFY_STATUS}\t${VERIFY_STRATEGY}\t${STDOUT_FIRST5}" >> "$SUMMARY"

  if [ "$VERIFY_STATUS" = "PASS" ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
    echo "  ✅ PASS (build=${BUILD_TIME}s, run=${RUN_TIME}s, verify=${VERIFY_STRATEGY})"
  elif [ "$BUILD_STATUS" != "PASS" ]; then
    BUILD_FAIL=$((BUILD_FAIL + 1))
    echo "  🚫 BUILD FAIL (${BUILD_STATUS})"
  elif [ "$RUN_STATUS" != "PASS" ]; then
    RUN_FAIL=$((RUN_FAIL + 1))
    echo "  ❌ RUN ${RUN_STATUS} (exit=${RUN_EXIT}, ${RUN_TIME}s)"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo "  ❌ VERIFY ${VERIFY_STATUS} (strategy=${VERIFY_STRATEGY})"
  fi
done

echo ""
echo "========================================"
echo "DONE: $(date -Iseconds)"
echo "  Total:  $TOTAL"
echo "  PASS:   $PASS_COUNT"
echo "  BUILD_FAIL: $BUILD_FAIL"
echo "  RUN_FAIL: $RUN_FAIL"
echo "  VERIFY_FAIL: $FAIL_COUNT"
echo "  Summary: $SUMMARY"
echo "========================================"

echo "COMPLETED $(date -Iseconds) PASS=$PASS_COUNT BUILD_FAIL=$BUILD_FAIL RUN_FAIL=$RUN_FAIL VERIFY_FAIL=$FAIL_COUNT TOTAL=$TOTAL" > "$LOG_DIR/_done.marker"
