# Eval Batch: opencl-to-omp — 2026-03-31
**Date:** 2026-03-31  |  **Tasks:** 51

## together-qwen-3.5-397b-a17b
**4/17 PASS (23%)** | FAILURES=13 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| backprop | ✗ BUILD_FAIL | — | None | 16944 |
| bfs | ✓ PASS | 0.002× | wall_time | 16082 |
| bptree | ✗ BUILD_FAIL | — | None | 31232 |
| cfd | ✗ BUILD_FAIL | — | None | 27075 |
| heartwall | ✗ BUILD_FAIL | — | None | 57979 |
| hotspot | ✗ VERIFY_FAIL | 0.750× | wall_time | 9776 |
| hotspot3d | ✓ PASS | 1.027× | wall_time | 11386 |
| kmeans | ✗ BUILD_FAIL | — | None | 31103 |
| lavamd | ✗ VERIFY_FAIL | 0.012× | wall_time | 12018 |
| lud | ✓ PASS | 2.000× | wall_time | 14307 |
| myocyte | ✗ BUILD_FAIL | — | None | 70992 |
| nn | ✗ VERIFY_FAIL | 16.000× | wall_time | 17580 |
| nw | ✗ BUILD_FAIL | — | None | 14321 |
| particlefilter | ✓ PASS | 1.000× | wall_time | 39675 |
| pathfinder | ✗ BUILD_FAIL | — | None | 10176 |
| srad | ✗ BUILD_FAIL | — | None | 20348 |
| streamcluster | ✗ BUILD_FAIL | — | None | 32163 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✗ BUILD_FAIL |
| bfs | ✓ PASS |
| bptree | ✗ BUILD_FAIL |
| cfd | ✗ BUILD_FAIL |
| heartwall | ✗ BUILD_FAIL |
| hotspot | ✗ VERIFY_FAIL |
| hotspot3d | ✓ PASS |
| kmeans | ✗ BUILD_FAIL |
| lavamd | ✗ VERIFY_FAIL |
| lud | ✓ PASS |
| myocyte | ✗ BUILD_FAIL |
| nn | ✗ VERIFY_FAIL |
| nw | ✗ BUILD_FAIL |
| particlefilter | ✓ PASS |
| pathfinder | ✗ BUILD_FAIL |
| srad | ✗ BUILD_FAIL |
| streamcluster | ✗ BUILD_FAIL |
