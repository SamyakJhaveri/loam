# Eval Batch: opencl-to-omp — 2026-03-31
**Date:** 2026-03-31  |  **Tasks:** 85

## together-qwen-3.5-397b-a17b
**35/85 PASS (41%)** | FAILURES=50 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| backprop | L0 | ✗ BUILD_FAIL | — | None | 66129 |
| backprop | L1 | ✗ VERIFY_FAIL | 16.000× | wall_time | 49133 |
| backprop | L2 | ✗ BUILD_FAIL | — | None | 65561 |
| backprop | L3 | ✗ BUILD_FAIL | — | None | 66128 |
| backprop | L4 | ✗ BUILD_FAIL | — | None | 78978 |
| bfs | L0 | ✓ PASS | 0.002× | wall_time | 15296 |
| bfs | L1 | ✗ BUILD_FAIL | — | None | 51636 |
| bfs | L2 | ✓ PASS | 0.002× | wall_time | 15125 |
| bfs | L3 | ✓ PASS | 0.002× | wall_time | 15152 |
| bfs | L4 | ✓ PASS | 0.002× | wall_time | 15396 |
| bptree | L0 | ✗ VERIFY_FAIL | 0.655× | wall_time | 105171 |
| bptree | L1 | ✗ BUILD_FAIL | — | None | 94071 |
| bptree | L2 | ✗ VERIFY_FAIL | 0.988× | wall_time | 101307 |
| bptree | L3 | ✗ BUILD_FAIL | — | None | 102229 |
| bptree | L4 | ✗ BUILD_FAIL | — | None | 100234 |
| cfd | L0 | ✓ PASS | 1.026× | wall_time | 99708 |
| cfd | L1 | ✗ RUN_FAIL | — | None | 101784 |
| cfd | L2 | ✓ PASS | 0.972× | wall_time | 27511 |
| cfd | L3 | ✓ PASS | 1.020× | wall_time | 61492 |
| cfd | L4 | ✓ PASS | 1.020× | wall_time | 61579 |
| heartwall | L0 | ✗ BUILD_FAIL | — | None | 221310 |
| heartwall | L1 | ✗ BUILD_FAIL | — | None | 228484 |
| heartwall | L2 | ✗ RUN_FAIL | — | None | 223013 |
| heartwall | L3 | ✗ BUILD_FAIL | — | None | 219429 |
| heartwall | L4 | ✗ BUILD_FAIL | — | None | 222471 |
| hotspot | L0 | ✓ PASS | 0.742× | wall_time | 22923 |
| hotspot | L1 | ✓ PASS | 0.622× | wall_time | 23112 |
| hotspot | L2 | ✓ PASS | 0.784× | wall_time | 22568 |
| hotspot | L3 | ✓ PASS | 0.775× | wall_time | 22565 |
| hotspot | L4 | ✓ PASS | 0.767× | wall_time | 22541 |
| hotspot3d | L0 | ✓ PASS | 1.015× | wall_time | 76089 |
| hotspot3d | L1 | ✓ PASS | 1.022× | wall_time | 68543 |
| hotspot3d | L2 | ✗ BUILD_FAIL | — | None | 74209 |
| hotspot3d | L3 | ✓ PASS | 0.998× | wall_time | 11213 |
| hotspot3d | L4 | ✗ BUILD_FAIL | — | None | 56891 |
| kmeans | L0 | ✗ BUILD_FAIL | — | None | 101694 |
| kmeans | L1 | ✗ BUILD_FAIL | — | None | 101881 |
| kmeans | L2 | ✗ BUILD_FAIL | — | None | 98680 |
| kmeans | L3 | ✗ BUILD_FAIL | — | None | 114092 |
| kmeans | L4 | ✗ BUILD_FAIL | — | None | 105436 |
| lavamd | L0 | ✗ VERIFY_FAIL | 0.000× | wall_time | 39611 |
| lavamd | L1 | ✗ BUILD_FAIL | — | None | 44971 |
| lavamd | L2 | ✗ BUILD_FAIL | — | None | 45420 |
| lavamd | L3 | ✗ VERIFY_FAIL | 0.010× | wall_time | 40406 |
| lavamd | L4 | ✗ VERIFY_FAIL | 0.011× | wall_time | 39579 |
| lud | L0 | ✓ PASS | 2.000× | wall_time | 15059 |
| lud | L1 | ✓ PASS | 0.667× | wall_time | 14735 |
| lud | L2 | ✓ PASS | 1.000× | wall_time | 14523 |
| lud | L3 | ✓ PASS | 2.000× | wall_time | 14306 |
| lud | L4 | ✓ PASS | 2.000× | wall_time | 14298 |
| myocyte | L0 | ✗ BUILD_FAIL | — | None | 285563 |
| myocyte | L1 | ✗ BUILD_FAIL | — | None | 286461 |
| myocyte | L2 | ✗ BUILD_FAIL | — | None | 285003 |
| myocyte | L3 | ✗ BUILD_FAIL | — | None | 294432 |
| myocyte | L4 | ✗ BUILD_FAIL | — | None | 289989 |
| nn | L0 | ✗ VERIFY_FAIL | 1.778× | wall_time | 57891 |
| nn | L1 | ✗ VERIFY_FAIL | 2.000× | wall_time | 57977 |
| nn | L2 | ✗ VERIFY_FAIL | 1.778× | wall_time | 58310 |
| nn | L3 | ✗ VERIFY_FAIL | 1.600× | wall_time | 59591 |
| nn | L4 | ✗ VERIFY_FAIL | 1.333× | wall_time | 58253 |
| nw | L0 | ✓ PASS | 0.833× | wall_time | 15042 |
| nw | L1 | ✓ PASS | 0.882× | wall_time | 16796 |
| nw | L2 | ✓ PASS | 0.833× | wall_time | 15771 |
| nw | L3 | ✓ PASS | 0.025× | wall_time | 70782 |
| nw | L4 | ✓ PASS | 0.833× | wall_time | 62229 |
| particlefilter | L0 | ✓ PASS | 1.000× | wall_time | 87301 |
| particlefilter | L1 | ✓ PASS | 1.000× | wall_time | 85450 |
| particlefilter | L2 | ✓ PASS | 1.000× | wall_time | 85446 |
| particlefilter | L3 | ✓ PASS | 1.000× | wall_time | 84930 |
| particlefilter | L4 | ✓ PASS | 1.000× | wall_time | 39381 |
| pathfinder | L0 | ✗ BUILD_FAIL | — | None | 40119 |
| pathfinder | L1 | ✗ BUILD_FAIL | — | None | 48587 |
| pathfinder | L2 | ✗ VERIFY_FAIL | 0.002× | wall_time | 45257 |
| pathfinder | L3 | ✗ VERIFY_FAIL | 0.014× | wall_time | 37197 |
| pathfinder | L4 | ✗ VERIFY_FAIL | 0.008× | wall_time | 45703 |
| srad | L0 | ✗ RUN_FAIL | — | None | 77672 |
| srad | L1 | ✓ PASS | 1.500× | wall_time | 22335 |
| srad | L2 | ✓ PASS | 1.500× | wall_time | 50580 |
| srad | L3 | ✓ PASS | 1.500× | wall_time | 45697 |
| srad | L4 | ✗ VERIFY_FAIL | 0.071× | wall_time | 76938 |
| streamcluster | L0 | ✗ VERIFY_FAIL | 3.062× | wall_time | 121946 |
| streamcluster | L1 | ✗ VERIFY_FAIL | 0.115× | wall_time | 125799 |
| streamcluster | L2 | ✗ VERIFY_FAIL | 4.001× | wall_time | 129510 |
| streamcluster | L3 | ✗ VERIFY_FAIL | 0.260× | wall_time | 126893 |
| streamcluster | L4 | ✓ PASS | 29.228× | wall_time | 117426 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| backprop | L0 | ✗ BUILD_FAIL |
| backprop | L1 | ✗ VERIFY_FAIL |
| backprop | L2 | ✗ BUILD_FAIL |
| backprop | L3 | ✗ BUILD_FAIL |
| backprop | L4 | ✗ BUILD_FAIL |
| bfs | L0 | ✓ PASS |
| bfs | L1 | ✗ BUILD_FAIL |
| bfs | L2 | ✓ PASS |
| bfs | L3 | ✓ PASS |
| bfs | L4 | ✓ PASS |
| bptree | L0 | ✗ VERIFY_FAIL |
| bptree | L1 | ✗ BUILD_FAIL |
| bptree | L2 | ✗ VERIFY_FAIL |
| bptree | L3 | ✗ BUILD_FAIL |
| bptree | L4 | ✗ BUILD_FAIL |
| cfd | L0 | ✓ PASS |
| cfd | L1 | ✗ RUN_FAIL |
| cfd | L2 | ✓ PASS |
| cfd | L3 | ✓ PASS |
| cfd | L4 | ✓ PASS |
| heartwall | L0 | ✗ BUILD_FAIL |
| heartwall | L1 | ✗ BUILD_FAIL |
| heartwall | L2 | ✗ RUN_FAIL |
| heartwall | L3 | ✗ BUILD_FAIL |
| heartwall | L4 | ✗ BUILD_FAIL |
| hotspot | L0 | ✓ PASS |
| hotspot | L1 | ✓ PASS |
| hotspot | L2 | ✓ PASS |
| hotspot | L3 | ✓ PASS |
| hotspot | L4 | ✓ PASS |
| hotspot3d | L0 | ✓ PASS |
| hotspot3d | L1 | ✓ PASS |
| hotspot3d | L2 | ✗ BUILD_FAIL |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✗ BUILD_FAIL |
| kmeans | L0 | ✗ BUILD_FAIL |
| kmeans | L1 | ✗ BUILD_FAIL |
| kmeans | L2 | ✗ BUILD_FAIL |
| kmeans | L3 | ✗ BUILD_FAIL |
| kmeans | L4 | ✗ BUILD_FAIL |
| lavamd | L0 | ✗ VERIFY_FAIL |
| lavamd | L1 | ✗ BUILD_FAIL |
| lavamd | L2 | ✗ BUILD_FAIL |
| lavamd | L3 | ✗ VERIFY_FAIL |
| lavamd | L4 | ✗ VERIFY_FAIL |
| lud | L0 | ✓ PASS |
| lud | L1 | ✓ PASS |
| lud | L2 | ✓ PASS |
| lud | L3 | ✓ PASS |
| lud | L4 | ✓ PASS |
| myocyte | L0 | ✗ BUILD_FAIL |
| myocyte | L1 | ✗ BUILD_FAIL |
| myocyte | L2 | ✗ BUILD_FAIL |
| myocyte | L3 | ✗ BUILD_FAIL |
| myocyte | L4 | ✗ BUILD_FAIL |
| nn | L0 | ✗ VERIFY_FAIL |
| nn | L1 | ✗ VERIFY_FAIL |
| nn | L2 | ✗ VERIFY_FAIL |
| nn | L3 | ✗ VERIFY_FAIL |
| nn | L4 | ✗ VERIFY_FAIL |
| nw | L0 | ✓ PASS |
| nw | L1 | ✓ PASS |
| nw | L2 | ✓ PASS |
| nw | L3 | ✓ PASS |
| nw | L4 | ✓ PASS |
| particlefilter | L0 | ✓ PASS |
| particlefilter | L1 | ✓ PASS |
| particlefilter | L2 | ✓ PASS |
| particlefilter | L3 | ✓ PASS |
| particlefilter | L4 | ✓ PASS |
| pathfinder | L0 | ✗ BUILD_FAIL |
| pathfinder | L1 | ✗ BUILD_FAIL |
| pathfinder | L2 | ✗ VERIFY_FAIL |
| pathfinder | L3 | ✗ VERIFY_FAIL |
| pathfinder | L4 | ✗ VERIFY_FAIL |
| srad | L0 | ✗ RUN_FAIL |
| srad | L1 | ✓ PASS |
| srad | L2 | ✓ PASS |
| srad | L3 | ✓ PASS |
| srad | L4 | ✗ VERIFY_FAIL |
| streamcluster | L0 | ✗ VERIFY_FAIL |
| streamcluster | L1 | ✗ VERIFY_FAIL |
| streamcluster | L2 | ✗ VERIFY_FAIL |
| streamcluster | L3 | ✗ VERIFY_FAIL |
| streamcluster | L4 | ✓ PASS |
