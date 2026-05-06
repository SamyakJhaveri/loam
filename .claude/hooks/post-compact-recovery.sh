#!/usr/bin/env bash
# Post-compact context recovery — re-injects critical project facts after /compact
#
# Triggered by: PostToolUse on Compact
# Purpose: After context compression, key facts (KNOWN_FAIL list, paths, spec counts)
#          are lost. This hook re-injects them so Claude doesn't hallucinate stale data.
#
# Exit codes:
#   0 = always (advisory hook, never blocks)

set -euo pipefail

# Consume stdin (PostToolUse hooks receive JSON on stdin; prevent SIGPIPE)
cat > /dev/null

echo "=== CONTEXT RECOVERY ===" >&2
echo "KNOWN_FAIL: kmeans-cuda, mummergpu-cuda, mummergpu-omp, hybridsort-cuda, nn-opencl, kmeans-opencl, hecbench-stencil1d-omp_target, hecbench-scan-omp_target" >&2
echo "Rodinia: 60 specs (54 PASS + 6 KNOWN_FAIL)" >&2
echo "XSBench: 4 specs (4 PASS)" >&2
NVCC_PATH="$(which nvcc 2>/dev/null || echo 'nvcc not found')"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
echo "CUDA: $NVCC_PATH" >&2
echo "Project: $PROJECT_ROOT" >&2
# Dynamic: count result files for active campaigns
for model_dir in "$PROJECT_ROOT"/results/evaluation/*/; do
  if [ -d "$model_dir" ]; then
    model=$(basename "$model_dir")
    count=$(find "$model_dir" -name "*.json" -type f 2>/dev/null | wc -l)
    echo "Results/$model: $count files" >&2
  fi
done
echo "========================" >&2
exit 0
