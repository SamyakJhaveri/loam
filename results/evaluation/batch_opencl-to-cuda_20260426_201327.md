# Eval Batch: opencl-to-cuda — 2026-04-26
**Date:** 2026-04-26  |  **Tasks:** 20

## azure-gpt-5.4
**15/20 PASS (75%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| cfd | L1 | ✓ PASS | — | wall_time | 45542 |
| cfd | L2 | ✓ PASS | — | wall_time | 46069 |
| cfd | L3 | ✓ PASS | — | wall_time | 44658 |
| cfd | L4 | ✓ PASS | — | wall_time | 44592 |
| mixbench | L1 | ✗ BUILD_FAIL | — | None | 19724 |
| mixbench | L2 | ✗ BUILD_FAIL | — | None | 21997 |
| mixbench | L3 | ✗ BUILD_FAIL | — | None | 21278 |
| mixbench | L4 | ✓ PASS | 14.634× | wall_time | 20012 |
| particlefilter | L1 | ✓ PASS | 0.628× | wall_time | 44881 |
| particlefilter | L2 | ✗ BUILD_FAIL | — | None | 59997 |
| particlefilter | L3 | ✓ PASS | 0.633× | wall_time | 46100 |
| particlefilter | L4 | ✓ PASS | 0.624× | wall_time | 60332 |
| rsbench | L1 | ✓ PASS | 0.973× | wall_time | 32609 |
| rsbench | L2 | ✓ PASS | 0.975× | wall_time | 32436 |
| rsbench | L3 | ✗ BUILD_FAIL | — | None | 36979 |
| rsbench | L4 | ✓ PASS | 0.974× | wall_time | 32178 |
| xsbench | L1 | ✓ PASS | 1.388× | wall_time | 36753 |
| xsbench | L2 | ✓ PASS | 1.376× | wall_time | 35663 |
| xsbench | L3 | ✓ PASS | 1.177× | wall_time | 35303 |
| xsbench | L4 | ✓ PASS | 1.183× | wall_time | 34529 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.4 |
|--------|-------|---|
| cfd | L1 | ✓ PASS |
| cfd | L2 | ✓ PASS |
| cfd | L3 | ✓ PASS |
| cfd | L4 | ✓ PASS |
| mixbench | L1 | ✗ BUILD_FAIL |
| mixbench | L2 | ✗ BUILD_FAIL |
| mixbench | L3 | ✗ BUILD_FAIL |
| mixbench | L4 | ✓ PASS |
| particlefilter | L1 | ✓ PASS |
| particlefilter | L2 | ✗ BUILD_FAIL |
| particlefilter | L3 | ✓ PASS |
| particlefilter | L4 | ✓ PASS |
| rsbench | L1 | ✓ PASS |
| rsbench | L2 | ✓ PASS |
| rsbench | L3 | ✗ BUILD_FAIL |
| rsbench | L4 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
