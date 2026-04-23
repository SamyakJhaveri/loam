# Eval Batch: cuda-to-opencl — 2026-04-21
**Date:** 2026-04-21  |  **Tasks:** 60

## together-qwen-3.5-397b-a17b
**1/20 PASS (5%)** | FAILURES=19 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| backprop | ✗ VERIFY_FAIL | 0.006× | wall_time | 17342 |
| bfs | ✗ RUN_FAIL | — | None | 15458 |
| bptree | ✗ RUN_FAIL | — | None | 14852 |
| cfd | ✗ VERIFY_FAIL | — | wall_time | 40592 |
| dwt2d | ✗ RUN_FAIL | — | None | 40073 |
| gaussian | ✗ RUN_FAIL | — | None | 15285 |
| heartwall | ✗ RUN_FAIL | — | None | 45363 |
| hotspot | ✓ PASS | 0.562× | wall_time | 13322 |
| hotspot3d | ✗ RUN_FAIL | — | None | 11808 |
| hybridsort | ✗ RUN_FAIL | — | None | 34541 |
| kmeans | ✗ VERIFY_FAIL | 2.966× | wall_time | 31113 |
| lavamd | ✗ RUN_FAIL | — | None | 12106 |
| lud | ✗ RUN_FAIL | — | None | 15266 |
| myocyte | ✗ RUN_FAIL | — | None | 72564 |
| nn | ✗ RUN_FAIL | — | None | 14930 |
| nw | ✗ RUN_FAIL | — | None | 14824 |
| particlefilter | ✗ VERIFY_FAIL | 0.453× | wall_time | 30728 |
| pathfinder | ✗ RUN_FAIL | — | None | 7551 |
| srad | ✗ RUN_FAIL | — | None | 17951 |
| streamcluster | ✗ RUN_FAIL | — | None | 23287 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✗ VERIFY_FAIL |
| bfs | ✗ RUN_FAIL |
| bptree | ✗ RUN_FAIL |
| cfd | ✗ VERIFY_FAIL |
| dwt2d | ✗ RUN_FAIL |
| gaussian | ✗ RUN_FAIL |
| heartwall | ✗ RUN_FAIL |
| hotspot | ✓ PASS |
| hotspot3d | ✗ RUN_FAIL |
| hybridsort | ✗ RUN_FAIL |
| kmeans | ✗ VERIFY_FAIL |
| lavamd | ✗ RUN_FAIL |
| lud | ✗ RUN_FAIL |
| myocyte | ✗ RUN_FAIL |
| nn | ✗ RUN_FAIL |
| nw | ✗ RUN_FAIL |
| particlefilter | ✗ VERIFY_FAIL |
| pathfinder | ✗ RUN_FAIL |
| srad | ✗ RUN_FAIL |
| streamcluster | ✗ RUN_FAIL |
