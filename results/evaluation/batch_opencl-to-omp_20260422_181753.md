# Eval Batch: opencl-to-omp — 2026-04-22
**Date:** 2026-04-22  |  **Tasks:** 16

## together-qwen-3.5-397b-a17b
**6/16 PASS (37%)** | FAILURES=10 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| hotspot3d | L1 | ✗ BUILD_FAIL | — | None | 14288 |
| hotspot3d | L2 | ✓ PASS | 1.006× | wall_time | 21377 |
| hotspot3d | L3 | ✓ PASS | 1.019× | wall_time | 16375 |
| hotspot3d | L4 | ✗ BUILD_FAIL | — | None | 13834 |
| lud | L1 | ✓ PASS | 0.800× | wall_time | 27191 |
| lud | L2 | ✓ PASS | 4.000× | wall_time | 24355 |
| lud | L3 | ✗ RUN_FAIL | — | None | 23159 |
| lud | L4 | ✗ RUN_FAIL | — | None | 15471 |
| particlefilter | L1 | ✗ BUILD_FAIL | — | None | 40498 |
| particlefilter | L2 | ✗ BUILD_FAIL | — | None | 39870 |
| particlefilter | L3 | ✗ BUILD_FAIL | — | None | 46048 |
| particlefilter | L4 | ✓ PASS | 1.000× | wall_time | 40610 |
| srad | L1 | ✓ PASS | 1.500× | wall_time | 30237 |
| srad | L2 | ✗ BUILD_FAIL | — | None | 29954 |
| srad | L3 | ✗ BUILD_FAIL | — | None | 20190 |
| srad | L4 | ✗ BUILD_FAIL | — | None | 20730 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| hotspot3d | L1 | ✗ BUILD_FAIL |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✗ BUILD_FAIL |
| lud | L1 | ✓ PASS |
| lud | L2 | ✓ PASS |
| lud | L3 | ✗ RUN_FAIL |
| lud | L4 | ✗ RUN_FAIL |
| particlefilter | L1 | ✗ BUILD_FAIL |
| particlefilter | L2 | ✗ BUILD_FAIL |
| particlefilter | L3 | ✗ BUILD_FAIL |
| particlefilter | L4 | ✓ PASS |
| srad | L1 | ✓ PASS |
| srad | L2 | ✗ BUILD_FAIL |
| srad | L3 | ✗ BUILD_FAIL |
| srad | L4 | ✗ BUILD_FAIL |
