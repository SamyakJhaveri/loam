# Eval Batch: cuda-to-opencl — 2026-03-30
**Date:** 2026-03-30  |  **Tasks:** 100

## together-qwen-3.5-397b-a17b
**15/100 PASS (15%)** | FAILURES=85 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| backprop | L0 | ✗ VERIFY_FAIL | 0.006× | wall_time | 52893 |
| backprop | L1 | ✓ PASS | 0.005× | wall_time | 34339 |
| backprop | L2 | ✗ VERIFY_FAIL | 0.006× | wall_time | 52815 |
| backprop | L3 | ✗ VERIFY_FAIL | 0.006× | wall_time | 52920 |
| backprop | L4 | ✗ VERIFY_FAIL | 0.006× | wall_time | 53013 |
| bfs | L0 | ✓ PASS | 0.852× | wall_time | 29546 |
| bfs | L1 | ✓ PASS | 0.836× | wall_time | 29534 |
| bfs | L2 | ✓ PASS | 0.826× | wall_time | 29565 |
| bfs | L3 | ✗ RUN_FAIL | — | None | 44811 |
| bfs | L4 | ✗ RUN_FAIL | — | None | 45130 |
| bptree | L0 | ✗ RUN_FAIL | — | None | 43128 |
| bptree | L1 | ✗ RUN_FAIL | — | None | 43068 |
| bptree | L2 | ✗ RUN_FAIL | — | None | 47584 |
| bptree | L3 | ✗ RUN_FAIL | — | None | 45320 |
| bptree | L4 | ✓ PASS | 0.654× | wall_time | 13700 |
| cfd | L0 | ✗ VERIFY_FAIL | — | wall_time | 124982 |
| cfd | L1 | ✗ VERIFY_FAIL | — | wall_time | 126901 |
| cfd | L2 | ✗ VERIFY_FAIL | — | wall_time | 128867 |
| cfd | L3 | ✗ VERIFY_FAIL | — | wall_time | 129208 |
| cfd | L4 | ✗ VERIFY_FAIL | — | wall_time | 142185 |
| dwt2d | L0 | ✗ RUN_FAIL | — | None | 171600 |
| dwt2d | L1 | ✗ RUN_FAIL | — | None | 167196 |
| dwt2d | L2 | ✗ RUN_FAIL | — | None | 195293 |
| dwt2d | L3 | ✗ RUN_FAIL | — | None | 164957 |
| dwt2d | L4 | ✗ RUN_FAIL | — | None | 167079 |
| gaussian | L0 | ✗ RUN_FAIL | — | None | 73063 |
| gaussian | L1 | ✗ RUN_FAIL | — | None | 70563 |
| gaussian | L2 | ✗ RUN_FAIL | — | None | 287465 |
| gaussian | L3 | ✗ RUN_FAIL | — | None | 71229 |
| gaussian | L4 | ✗ RUN_FAIL | — | None | 42181 |
| heartwall | L0 | ✗ RUN_FAIL | — | None | 160050 |
| heartwall | L1 | ✗ RUN_FAIL | — | None | 158022 |
| heartwall | L2 | ✗ RUN_FAIL | — | None | 159321 |
| heartwall | L3 | ✗ RUN_FAIL | — | None | 168103 |
| heartwall | L4 | ✗ RUN_FAIL | — | None | 160365 |
| hotspot | L0 | ✓ PASS | 0.591× | wall_time | 18959 |
| hotspot | L1 | ✓ PASS | 0.657× | wall_time | 18954 |
| hotspot | L2 | ✓ PASS | 0.558× | wall_time | 18957 |
| hotspot | L3 | ✓ PASS | 0.564× | wall_time | 8931 |
| hotspot | L4 | ✗ RUN_FAIL | — | None | 33734 |
| hotspot3d | L0 | ✓ PASS | 0.934× | wall_time | 8157 |
| hotspot3d | L1 | ✓ PASS | 0.895× | wall_time | 8161 |
| hotspot3d | L2 | ✓ PASS | 0.891× | wall_time | 8235 |
| hotspot3d | L3 | ✓ PASS | 0.932× | wall_time | 8170 |
| hotspot3d | L4 | ✓ PASS | 0.897× | wall_time | 8211 |
| hybridsort | L0 | ✗ RUN_FAIL | — | None | 109205 |
| hybridsort | L1 | ✗ RUN_FAIL | — | None | 120156 |
| hybridsort | L2 | ✗ RUN_FAIL | — | None | 109879 |
| hybridsort | L3 | ✗ RUN_FAIL | — | None | 125979 |
| hybridsort | L4 | ✗ RUN_FAIL | — | None | 110236 |
| kmeans | L0 | ✗ VERIFY_FAIL | 2.881× | wall_time | 89270 |
| kmeans | L1 | ✗ VERIFY_FAIL | 2.859× | wall_time | 85410 |
| kmeans | L2 | ✗ VERIFY_FAIL | 2.897× | wall_time | 85428 |
| kmeans | L3 | ✗ VERIFY_FAIL | 2.909× | wall_time | 85409 |
| kmeans | L4 | ✗ VERIFY_FAIL | 2.897× | wall_time | 91868 |
| lavamd | L0 | ✗ RUN_FAIL | — | None | 39015 |
| lavamd | L1 | ✗ RUN_FAIL | — | None | 39225 |
| lavamd | L2 | ✗ RUN_FAIL | — | None | 39406 |
| lavamd | L3 | ✗ RUN_FAIL | — | None | 39375 |
| lavamd | L4 | ✗ RUN_FAIL | — | None | 38934 |
| lud | L0 | ✗ RUN_FAIL | — | None | 47653 |
| lud | L1 | ✗ RUN_FAIL | — | None | 47684 |
| lud | L2 | ✗ RUN_FAIL | — | None | 47471 |
| lud | L3 | ✗ RUN_FAIL | — | None | 47616 |
| lud | L4 | ✗ RUN_FAIL | — | None | 48334 |
| myocyte | L0 | ✗ RUN_FAIL | — | None | 287657 |
| myocyte | L1 | ✗ RUN_FAIL | — | None | 297102 |
| myocyte | L2 | ✗ RUN_FAIL | — | None | 301545 |
| myocyte | L3 | ✗ RUN_FAIL | — | None | 460482 |
| myocyte | L4 | ✗ RUN_FAIL | — | None | 443838 |
| nn | L0 | ✗ RUN_FAIL | — | None | 44479 |
| nn | L1 | ✗ RUN_FAIL | — | None | 43805 |
| nn | L2 | ✗ RUN_FAIL | — | None | 39886 |
| nn | L3 | ✗ RUN_FAIL | — | None | 39206 |
| nn | L4 | ✗ RUN_FAIL | — | None | 41395 |
| nw | L0 | ✗ RUN_FAIL | — | None | 48535 |
| nw | L1 | ✗ RUN_FAIL | — | None | 49319 |
| nw | L2 | ✗ RUN_FAIL | — | None | 49043 |
| nw | L3 | ✗ RUN_FAIL | — | None | 49558 |
| nw | L4 | ✗ RUN_FAIL | — | None | 48929 |
| particlefilter | L0 | ✗ VERIFY_FAIL | 0.453× | wall_time | 82716 |
| particlefilter | L1 | ✗ VERIFY_FAIL | 0.459× | wall_time | 102687 |
| particlefilter | L2 | ✗ VERIFY_FAIL | 0.424× | wall_time | 77789 |
| particlefilter | L3 | ✗ VERIFY_FAIL | 0.427× | wall_time | 321898 |
| particlefilter | L4 | ✗ VERIFY_FAIL | 0.424× | wall_time | 99957 |
| pathfinder | L0 | ✗ RUN_FAIL | — | None | 19440 |
| pathfinder | L1 | ✗ RUN_FAIL | — | None | 19387 |
| pathfinder | L2 | ✓ PASS | — | wall_time | 19440 |
| pathfinder | L3 | ✗ RUN_FAIL | — | None | 19512 |
| pathfinder | L4 | ✗ RUN_FAIL | — | None | 21811 |
| srad | L0 | ✗ RUN_FAIL | — | None | 57486 |
| srad | L1 | ✗ RUN_FAIL | — | None | 54852 |
| srad | L2 | ✗ RUN_FAIL | — | None | 72271 |
| srad | L3 | ✗ RUN_FAIL | — | None | 57893 |
| srad | L4 | ✗ RUN_FAIL | — | None | 57051 |
| streamcluster | L0 | ✗ RUN_FAIL | — | None | 77181 |
| streamcluster | L1 | ✗ RUN_FAIL | — | None | 67123 |
| streamcluster | L2 | ✗ RUN_FAIL | — | None | 66606 |
| streamcluster | L3 | ✗ RUN_FAIL | — | None | 66747 |
| streamcluster | L4 | ✗ RUN_FAIL | — | None | 66915 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| backprop | L0 | ✗ VERIFY_FAIL |
| backprop | L1 | ✓ PASS |
| backprop | L2 | ✗ VERIFY_FAIL |
| backprop | L3 | ✗ VERIFY_FAIL |
| backprop | L4 | ✗ VERIFY_FAIL |
| bfs | L0 | ✓ PASS |
| bfs | L1 | ✓ PASS |
| bfs | L2 | ✓ PASS |
| bfs | L3 | ✗ RUN_FAIL |
| bfs | L4 | ✗ RUN_FAIL |
| bptree | L0 | ✗ RUN_FAIL |
| bptree | L1 | ✗ RUN_FAIL |
| bptree | L2 | ✗ RUN_FAIL |
| bptree | L3 | ✗ RUN_FAIL |
| bptree | L4 | ✓ PASS |
| cfd | L0 | ✗ VERIFY_FAIL |
| cfd | L1 | ✗ VERIFY_FAIL |
| cfd | L2 | ✗ VERIFY_FAIL |
| cfd | L3 | ✗ VERIFY_FAIL |
| cfd | L4 | ✗ VERIFY_FAIL |
| dwt2d | L0 | ✗ RUN_FAIL |
| dwt2d | L1 | ✗ RUN_FAIL |
| dwt2d | L2 | ✗ RUN_FAIL |
| dwt2d | L3 | ✗ RUN_FAIL |
| dwt2d | L4 | ✗ RUN_FAIL |
| gaussian | L0 | ✗ RUN_FAIL |
| gaussian | L1 | ✗ RUN_FAIL |
| gaussian | L2 | ✗ RUN_FAIL |
| gaussian | L3 | ✗ RUN_FAIL |
| gaussian | L4 | ✗ RUN_FAIL |
| heartwall | L0 | ✗ RUN_FAIL |
| heartwall | L1 | ✗ RUN_FAIL |
| heartwall | L2 | ✗ RUN_FAIL |
| heartwall | L3 | ✗ RUN_FAIL |
| heartwall | L4 | ✗ RUN_FAIL |
| hotspot | L0 | ✓ PASS |
| hotspot | L1 | ✓ PASS |
| hotspot | L2 | ✓ PASS |
| hotspot | L3 | ✓ PASS |
| hotspot | L4 | ✗ RUN_FAIL |
| hotspot3d | L0 | ✓ PASS |
| hotspot3d | L1 | ✓ PASS |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✓ PASS |
| hybridsort | L0 | ✗ RUN_FAIL |
| hybridsort | L1 | ✗ RUN_FAIL |
| hybridsort | L2 | ✗ RUN_FAIL |
| hybridsort | L3 | ✗ RUN_FAIL |
| hybridsort | L4 | ✗ RUN_FAIL |
| kmeans | L0 | ✗ VERIFY_FAIL |
| kmeans | L1 | ✗ VERIFY_FAIL |
| kmeans | L2 | ✗ VERIFY_FAIL |
| kmeans | L3 | ✗ VERIFY_FAIL |
| kmeans | L4 | ✗ VERIFY_FAIL |
| lavamd | L0 | ✗ RUN_FAIL |
| lavamd | L1 | ✗ RUN_FAIL |
| lavamd | L2 | ✗ RUN_FAIL |
| lavamd | L3 | ✗ RUN_FAIL |
| lavamd | L4 | ✗ RUN_FAIL |
| lud | L0 | ✗ RUN_FAIL |
| lud | L1 | ✗ RUN_FAIL |
| lud | L2 | ✗ RUN_FAIL |
| lud | L3 | ✗ RUN_FAIL |
| lud | L4 | ✗ RUN_FAIL |
| myocyte | L0 | ✗ RUN_FAIL |
| myocyte | L1 | ✗ RUN_FAIL |
| myocyte | L2 | ✗ RUN_FAIL |
| myocyte | L3 | ✗ RUN_FAIL |
| myocyte | L4 | ✗ RUN_FAIL |
| nn | L0 | ✗ RUN_FAIL |
| nn | L1 | ✗ RUN_FAIL |
| nn | L2 | ✗ RUN_FAIL |
| nn | L3 | ✗ RUN_FAIL |
| nn | L4 | ✗ RUN_FAIL |
| nw | L0 | ✗ RUN_FAIL |
| nw | L1 | ✗ RUN_FAIL |
| nw | L2 | ✗ RUN_FAIL |
| nw | L3 | ✗ RUN_FAIL |
| nw | L4 | ✗ RUN_FAIL |
| particlefilter | L0 | ✗ VERIFY_FAIL |
| particlefilter | L1 | ✗ VERIFY_FAIL |
| particlefilter | L2 | ✗ VERIFY_FAIL |
| particlefilter | L3 | ✗ VERIFY_FAIL |
| particlefilter | L4 | ✗ VERIFY_FAIL |
| pathfinder | L0 | ✗ RUN_FAIL |
| pathfinder | L1 | ✗ RUN_FAIL |
| pathfinder | L2 | ✓ PASS |
| pathfinder | L3 | ✗ RUN_FAIL |
| pathfinder | L4 | ✗ RUN_FAIL |
| srad | L0 | ✗ RUN_FAIL |
| srad | L1 | ✗ RUN_FAIL |
| srad | L2 | ✗ RUN_FAIL |
| srad | L3 | ✗ RUN_FAIL |
| srad | L4 | ✗ RUN_FAIL |
| streamcluster | L0 | ✗ RUN_FAIL |
| streamcluster | L1 | ✗ RUN_FAIL |
| streamcluster | L2 | ✗ RUN_FAIL |
| streamcluster | L3 | ✗ RUN_FAIL |
| streamcluster | L4 | ✗ RUN_FAIL |
