#!/usr/bin/env bash
# Run full harness pipeline (build → run → verify) for all 60 Rodinia specs.

set -euo pipefail

PROJECT_ROOT="{{PROJECT_ROOT}}"
LOG_DIR="$PROJECT_ROOT/results/rodinia/logs"
SUMMARY="$LOG_DIR/_summary.tsv"

cd "$PROJECT_ROOT"
source env_parbench/bin/activate

mkdir -p "$LOG_DIR"

# All 60 Rodinia specs, sorted
SPECS=($(ls specs/rodinia-*.json | sort))
TOTAL=${#SPECS[@]}

# Header for summary TSV
echo -e "#\tSpec\tBuild\tBuild_Time\tRun\tRun_Time\tRun_Exit\tVerify\tVerify_Strategy\tStdout_First5" > "$SUMMARY"

echo "========================================"
echo "Starting Rodinia harness run: $TOTAL specs"
echo "Time: $(date -Iseconds)"
echo "========================================"

IDX=0
PASS_COUNT=0
FAIL_COUNT=0

for SPEC in "${SPECS[@]}"; do
  IDX=$((IDX + 1))
  BASENAME=$(basename "$SPEC" .json)
  LOGFILE="$LOG_DIR/${BASENAME}.log"
  JSONFILE="$LOG_DIR/${BASENAME}.json"

  echo ""
  echo "[$IDX/$TOTAL] Running: $BASENAME ..."
  echo "  Spec: $SPEC"
  echo "  Log:  $LOGFILE"
  echo "  Time: $(date -Iseconds)"

  # Run the full pipeline, capture output
  set +e
  OUTPUT=$(python3 -m harness --json -v verify "$SPEC" --config correctness 2>&1)
  EXIT_CODE=$?
  set -e

  # Save full log
  echo "$OUTPUT" > "$LOGFILE"

  # Extract JSON block (everything between first { and last })
  JSON_BLOCK=$(echo "$OUTPUT" | sed -n '/^{/,/^}/p')
  if [ -n "$JSON_BLOCK" ]; then
    echo "$JSON_BLOCK" > "$JSONFILE"
  fi

  # Parse results from the summary line: [rodinia-*] | BUILD: X | RUN: X | VERIFY: X
  SUMMARY_LINE=$(echo "$OUTPUT" | grep '^\[rodinia-' | head -1)

  # Extract build status and time
  BUILD_STATUS=$(echo "$SUMMARY_LINE" | grep -oP 'BUILD: \K\w+' || echo "UNKNOWN")
  BUILD_TIME=$(echo "$SUMMARY_LINE" | grep -oP 'BUILD: \w+ \(\K[0-9.]+' || echo "0")

  # Extract run status and time
  RUN_STATUS=$(echo "$SUMMARY_LINE" | grep -oP 'RUN\([^)]+\): \K\w+' || echo "UNKNOWN")
  RUN_TIME=$(echo "$SUMMARY_LINE" | grep -oP 'RUN\([^)]+\): \w+ \(\K[0-9.]+' || echo "0")

  # Extract verify status and strategy
  VERIFY_STATUS=$(echo "$SUMMARY_LINE" | grep -oP 'VERIFY: \K\w+' || echo "UNKNOWN")
  VERIFY_STRATEGY=$(echo "$SUMMARY_LINE" | grep -oP 'VERIFY: \w+ \(\K[^)]+' || echo "unknown")

  # Get run exit code from JSON
  RUN_EXIT=$(echo "$JSON_BLOCK" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('runs',{}).get('correctness',{}).get('exit_code','?'))" 2>/dev/null || echo "?")

  # Get first 5 lines of stdout from JSON
  STDOUT_FIRST5=$(echo "$JSON_BLOCK" | python3 -c "
import sys, json
d = json.load(sys.stdin)
stdout = d.get('runs',{}).get('correctness',{}).get('stdout','')
lines = stdout.strip().split('\n')[:5]
print(' | '.join(lines))
" 2>/dev/null || echo "(no stdout)")

  # Append to summary TSV
  echo -e "${IDX}\t${BASENAME}\t${BUILD_STATUS}\t${BUILD_TIME}s\t${RUN_STATUS}\t${RUN_TIME}s\t${RUN_EXIT}\t${VERIFY_STATUS}\t${VERIFY_STRATEGY}\t${STDOUT_FIRST5}" >> "$SUMMARY"

  if [ "$VERIFY_STATUS" = "PASS" ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
    echo "  PASS (build=${BUILD_TIME}s, run=${RUN_TIME}s, verify=${VERIFY_STRATEGY})"
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    echo "  FAIL: ${VERIFY_STATUS} (build=${BUILD_STATUS}, run=${RUN_STATUS}, verify=${VERIFY_STRATEGY})"
  fi
done

echo ""
echo "========================================"
echo "DONE: $(date -Iseconds)"
echo "  Total:  $TOTAL"
echo "  PASS:   $PASS_COUNT"
echo "  FAIL:   $FAIL_COUNT"
echo "  Summary: $SUMMARY"
echo "========================================"

# Write a completion marker
echo "COMPLETED $(date -Iseconds) PASS=$PASS_COUNT FAIL=$FAIL_COUNT TOTAL=$TOTAL" > "$LOG_DIR/_done.marker"
