# Eval Batch: opencl-to-omp — 2026-04-21
**Date:** 2026-04-21  |  **Tasks:** 51

## together-qwen-3.5-397b-a17b
**3/17 PASS (17%)** | FAILURES=14 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| backprop | ✗ BUILD_FAIL | — | None | 15958 |
| bfs | ✗ BUILD_FAIL | — | None | 15290 |
| bptree | ✗ RUN_FAIL | — | None | 38553 |
| cfd | ✗ BUILD_FAIL | — | None | 27736 |
| heartwall | ✗ BUILD_FAIL | — | None | 72209 |
| hotspot | ✗ BUILD_FAIL | — | None | 14907 |
| hotspot3d | ✓ PASS | 1.003× | wall_time | 14265 |
| kmeans | ✗ BUILD_FAIL | — | None | 36747 |
| lavamd | ✗ BUILD_FAIL | — | None | 12733 |
| lud | ✗ RUN_FAIL | — | None | 25971 |
| myocyte | ✗ BUILD_FAIL | — | None | 70777 |
| nn | ✗ BUILD_FAIL | — | None | 26507 |
| nw | ✗ BUILD_FAIL | — | None | 15429 |
| particlefilter | ✓ PASS | 1.167× | wall_time | 44864 |
| pathfinder | ✗ BUILD_FAIL | — | None | 18535 |
| srad | ✓ PASS | 2.000× | wall_time | 26569 |
| streamcluster | ✗ BUILD_FAIL | — | None | 31431 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✗ BUILD_FAIL |
| bfs | ✗ BUILD_FAIL |
| bptree | ✗ RUN_FAIL |
| cfd | ✗ BUILD_FAIL |
| heartwall | ✗ BUILD_FAIL |
| hotspot | ✗ BUILD_FAIL |
| hotspot3d | ✓ PASS |
| kmeans | ✗ BUILD_FAIL |
| lavamd | ✗ BUILD_FAIL |
| lud | ✗ RUN_FAIL |
| myocyte | ✗ BUILD_FAIL |
| nn | ✗ BUILD_FAIL |
| nw | ✗ BUILD_FAIL |
| particlefilter | ✓ PASS |
| pathfinder | ✗ BUILD_FAIL |
| srad | ✓ PASS |
| streamcluster | ✗ BUILD_FAIL |
