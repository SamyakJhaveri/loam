# Eval Batch: opencl-to-omp — 2026-04-26
**Date:** 2026-04-26  |  **Tasks:** 42

## azure-gpt-5.4
**6/14 PASS (42%)** | FAILURES=8 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| bfs | ✓ PASS | 0.002× | wall_time | 17953 |
| bptree | ✗ VERIFY_FAIL | 0.961× | wall_time | 32023 |
| cfd | ✓ PASS | 0.932× | wall_time | 29128 |
| heartwall | ✗ BUILD_FAIL | — | None | 64912 |
| hotspot | ✗ VERIFY_FAIL | 0.784× | wall_time | 13094 |
| hotspot3d | ✓ PASS | 1.001× | wall_time | 16004 |
| lavamd | ✗ BUILD_FAIL | — | None | 11794 |
| lud | ✓ PASS | 0.133× | wall_time | 15884 |
| myocyte | ✗ BUILD_FAIL | — | None | 56021 |
| nw | ✗ RUN_FAIL | — | None | 19515 |
| particlefilter | ✓ PASS | 1.000× | wall_time | 41412 |
| pathfinder | ✗ BUILD_FAIL | — | None | 12568 |
| srad | ✓ PASS | 0.286× | wall_time | 24725 |
| streamcluster | ✗ VERIFY_FAIL | 0.959× | wall_time | 34318 |

## Cross-Model Summary

| Kernel | azure-gpt-5.4 |
|--------|---|
| bfs | ✓ PASS |
| bptree | ✗ VERIFY_FAIL |
| cfd | ✓ PASS |
| heartwall | ✗ BUILD_FAIL |
| hotspot | ✗ VERIFY_FAIL |
| hotspot3d | ✓ PASS |
| lavamd | ✗ BUILD_FAIL |
| lud | ✓ PASS |
| myocyte | ✗ BUILD_FAIL |
| nw | ✗ RUN_FAIL |
| particlefilter | ✓ PASS |
| pathfinder | ✗ BUILD_FAIL |
| srad | ✓ PASS |
| streamcluster | ✗ VERIFY_FAIL |
