# Eval Batch: opencl-to-omp — 2026-04-23
**Date:** 2026-04-23  |  **Tasks:** 16

## together-qwen-3.5-397b-a17b
**6/16 PASS (37%)** | FAILURES=10 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| hotspot3d | L1 | ✗ BUILD_FAIL | — | None | 21910 |
| hotspot3d | L2 | ✗ VERIFY_FAIL | 1.004× | wall_time | 12636 |
| hotspot3d | L3 | ✓ PASS | 0.985× | wall_time | 23849 |
| hotspot3d | L4 | ✓ PASS | 1.014× | wall_time | 19411 |
| lud | L1 | ✓ PASS | 0.800× | wall_time | 16785 |
| lud | L2 | ✗ RUN_FAIL | — | None | 21625 |
| lud | L3 | ✓ PASS | 2.000× | wall_time | 15516 |
| lud | L4 | ✗ RUN_FAIL | — | None | 19468 |
| particlefilter | L1 | ✗ BUILD_FAIL | — | None | 44629 |
| particlefilter | L2 | ✗ BUILD_FAIL | — | None | 40027 |
| particlefilter | L3 | ✓ PASS | 1.167× | wall_time | 46083 |
| particlefilter | L4 | ✗ BUILD_FAIL | — | None | 40062 |
| srad | L1 | ✓ PASS | 1.000× | wall_time | 23205 |
| srad | L2 | ✗ BUILD_FAIL | — | None | 22378 |
| srad | L3 | ✗ BUILD_FAIL | — | None | 21137 |
| srad | L4 | ✗ BUILD_FAIL | — | None | 21040 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| hotspot3d | L1 | ✗ BUILD_FAIL |
| hotspot3d | L2 | ✗ VERIFY_FAIL |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✓ PASS |
| lud | L1 | ✓ PASS |
| lud | L2 | ✗ RUN_FAIL |
| lud | L3 | ✓ PASS |
| lud | L4 | ✗ RUN_FAIL |
| particlefilter | L1 | ✗ BUILD_FAIL |
| particlefilter | L2 | ✗ BUILD_FAIL |
| particlefilter | L3 | ✓ PASS |
| particlefilter | L4 | ✗ BUILD_FAIL |
| srad | L1 | ✓ PASS |
| srad | L2 | ✗ BUILD_FAIL |
| srad | L3 | ✗ BUILD_FAIL |
| srad | L4 | ✗ BUILD_FAIL |
