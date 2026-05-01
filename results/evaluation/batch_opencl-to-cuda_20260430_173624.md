# Eval Batch: opencl-to-cuda — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 20

## azure-gpt-5.3-codex
**13/20 PASS (65%)** | FAILURES=7 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| cfd | L1 | ✓ PASS | — | wall_time | 41028 |
| cfd | L2 | ✓ PASS | — | wall_time | 41583 |
| cfd | L3 | ✓ PASS | — | wall_time | 41233 |
| cfd | L4 | ✓ PASS | — | wall_time | 41690 |
| mixbench | L1 | ✓ PASS | 15.528× | wall_time | 15092 |
| mixbench | L2 | ✓ PASS | 15.306× | wall_time | 15806 |
| mixbench | L3 | ✗ BUILD_FAIL | — | None | 15382 |
| mixbench | L4 | ✓ PASS | 15.369× | wall_time | 15209 |
| particlefilter | L1 | ✗ RUN_FAIL | — | None | 44134 |
| particlefilter | L2 | ✓ PASS | 0.574× | wall_time | 43619 |
| particlefilter | L3 | ✗ RUN_FAIL | — | None | 45290 |
| particlefilter | L4 | ✗ RUN_FAIL | — | None | 45077 |
| rsbench | L1 | ✓ PASS | 0.961× | wall_time | 30731 |
| rsbench | L2 | ✗ BUILD_FAIL | — | None | 31274 |
| rsbench | L3 | ✓ PASS | 0.962× | wall_time | 30816 |
| rsbench | L4 | ✗ BUILD_FAIL | — | None | 27924 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 30756 |
| xsbench | L2 | ✓ PASS | 1.189× | wall_time | 31862 |
| xsbench | L3 | ✓ PASS | 1.186× | wall_time | 32531 |
| xsbench | L4 | ✓ PASS | 1.405× | wall_time | 34006 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.3-codex |
|--------|-------|---|
| cfd | L1 | ✓ PASS |
| cfd | L2 | ✓ PASS |
| cfd | L3 | ✓ PASS |
| cfd | L4 | ✓ PASS |
| mixbench | L1 | ✓ PASS |
| mixbench | L2 | ✓ PASS |
| mixbench | L3 | ✗ BUILD_FAIL |
| mixbench | L4 | ✓ PASS |
| particlefilter | L1 | ✗ RUN_FAIL |
| particlefilter | L2 | ✓ PASS |
| particlefilter | L3 | ✗ RUN_FAIL |
| particlefilter | L4 | ✗ RUN_FAIL |
| rsbench | L1 | ✓ PASS |
| rsbench | L2 | ✗ BUILD_FAIL |
| rsbench | L3 | ✓ PASS |
| rsbench | L4 | ✗ BUILD_FAIL |
| xsbench | L1 | ✗ BUILD_FAIL |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
