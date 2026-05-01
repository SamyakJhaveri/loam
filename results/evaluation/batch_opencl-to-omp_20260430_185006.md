# Eval Batch: opencl-to-omp — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 36

## azure-gpt-5.3-codex
**24/36 PASS (66%)** | FAILURES=12 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| bfs | L1 | ✓ PASS | 0.001× | wall_time | 14091 |
| bfs | L2 | ✓ PASS | 0.002× | wall_time | 14059 |
| bfs | L3 | ✓ PASS | 0.001× | wall_time | 14061 |
| bfs | L4 | ✓ PASS | 0.002× | wall_time | 14015 |
| cfd | L1 | ✓ PASS | 0.933× | wall_time | 26314 |
| cfd | L2 | ✗ BUILD_FAIL | — | None | 26687 |
| cfd | L3 | ✓ PASS | 0.931× | wall_time | 26504 |
| cfd | L4 | ✓ PASS | 0.900× | wall_time | 26660 |
| hotspot3d | L1 | ✓ PASS | 1.011× | wall_time | 13074 |
| hotspot3d | L2 | ✓ PASS | 1.016× | wall_time | 12243 |
| hotspot3d | L3 | ✓ PASS | 1.024× | wall_time | 11597 |
| hotspot3d | L4 | ✓ PASS | 1.018× | wall_time | 12815 |
| lud | L1 | ✓ PASS | 1.000× | wall_time | 14984 |
| lud | L2 | ✓ PASS | 1.000× | wall_time | 15648 |
| lud | L3 | ✓ PASS | 1.000× | wall_time | 14825 |
| lud | L4 | ✓ PASS | 1.000× | wall_time | 15926 |
| mixbench | L1 | ✗ BUILD_FAIL | — | None | 15888 |
| mixbench | L2 | ✗ BUILD_FAIL | — | None | 14838 |
| mixbench | L3 | ✓ PASS | 3.170× | wall_time | 13722 |
| mixbench | L4 | ✗ BUILD_FAIL | — | None | 15289 |
| nw | L1 | ✗ RUN_FAIL | — | None | 14568 |
| nw | L2 | ✗ RUN_FAIL | — | None | 15320 |
| nw | L3 | ✗ RUN_FAIL | — | None | 14978 |
| nw | L4 | ✗ RUN_FAIL | — | None | 14785 |
| particlefilter | L1 | ✓ PASS | 0.875× | wall_time | 37435 |
| particlefilter | L2 | ✓ PASS | 1.000× | wall_time | 37513 |
| particlefilter | L3 | ✓ PASS | 1.400× | wall_time | 37612 |
| particlefilter | L4 | ✓ PASS | 1.000× | wall_time | 37080 |
| rsbench | L1 | ✗ BUILD_FAIL | — | None | 30051 |
| rsbench | L2 | ✗ BUILD_FAIL | — | None | 29699 |
| rsbench | L3 | ✗ BUILD_FAIL | — | None | 29521 |
| rsbench | L4 | ✗ BUILD_FAIL | — | None | 26676 |
| srad | L1 | ✓ PASS | 0.462× | wall_time | 22344 |
| srad | L2 | ✓ PASS | 0.353× | wall_time | 20371 |
| srad | L3 | ✓ PASS | 0.353× | wall_time | 20158 |
| srad | L4 | ✓ PASS | 0.429× | wall_time | 22618 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.3-codex |
|--------|-------|---|
| bfs | L1 | ✓ PASS |
| bfs | L2 | ✓ PASS |
| bfs | L3 | ✓ PASS |
| bfs | L4 | ✓ PASS |
| cfd | L1 | ✓ PASS |
| cfd | L2 | ✗ BUILD_FAIL |
| cfd | L3 | ✓ PASS |
| cfd | L4 | ✓ PASS |
| hotspot3d | L1 | ✓ PASS |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✓ PASS |
| lud | L1 | ✓ PASS |
| lud | L2 | ✓ PASS |
| lud | L3 | ✓ PASS |
| lud | L4 | ✓ PASS |
| mixbench | L1 | ✗ BUILD_FAIL |
| mixbench | L2 | ✗ BUILD_FAIL |
| mixbench | L3 | ✓ PASS |
| mixbench | L4 | ✗ BUILD_FAIL |
| nw | L1 | ✗ RUN_FAIL |
| nw | L2 | ✗ RUN_FAIL |
| nw | L3 | ✗ RUN_FAIL |
| nw | L4 | ✗ RUN_FAIL |
| particlefilter | L1 | ✓ PASS |
| particlefilter | L2 | ✓ PASS |
| particlefilter | L3 | ✓ PASS |
| particlefilter | L4 | ✓ PASS |
| rsbench | L1 | ✗ BUILD_FAIL |
| rsbench | L2 | ✗ BUILD_FAIL |
| rsbench | L3 | ✗ BUILD_FAIL |
| rsbench | L4 | ✗ BUILD_FAIL |
| srad | L1 | ✓ PASS |
| srad | L2 | ✓ PASS |
| srad | L3 | ✓ PASS |
| srad | L4 | ✓ PASS |
