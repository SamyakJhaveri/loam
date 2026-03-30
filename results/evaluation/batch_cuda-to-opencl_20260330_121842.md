# Eval Batch: cuda-to-opencl — 2026-03-30
**Date:** 2026-03-30  |  **Tasks:** 100

## together-qwen-3.5-397b-a17b
**0/100 PASS (0%)** | FAILURES=100 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| backprop | L0 | ✗ VERIFY_FAIL | 1.000× | wall_time | 56227 |
| backprop | L1 | ✗ VERIFY_FAIL | 1.000× | wall_time | 56856 |
| backprop | L2 | ✗ VERIFY_FAIL | 1.000× | wall_time | 62681 |
| backprop | L3 | ✗ VERIFY_FAIL | 1.000× | wall_time | 56539 |
| backprop | L4 | ✗ VERIFY_FAIL | 1.000× | wall_time | 55105 |
| bfs | L0 | ✗ RUN_FAIL | — | None | 44777 |
| bfs | L1 | ✗ VERIFY_FAIL | 0.892× | wall_time | 51908 |
| bfs | L2 | ✗ RUN_FAIL | — | None | 44813 |
| bfs | L3 | ✗ RUN_FAIL | — | None | 44715 |
| bfs | L4 | ✗ RUN_FAIL | — | None | 45129 |
| bptree | L0 | ✗ RUN_FAIL | — | None | 68264 |
| bptree | L1 | ✗ RUN_FAIL | — | None | 43101 |
| bptree | L2 | ✗ RUN_FAIL | — | None | 57691 |
| bptree | L3 | ✗ RUN_FAIL | — | None | 45157 |
| bptree | L4 | ✗ RUN_FAIL | — | None | 52922 |
| cfd | L0 | ✗ VERIFY_FAIL | — | wall_time | 123476 |
| cfd | L1 | ✗ VERIFY_FAIL | — | wall_time | 126013 |
| cfd | L2 | ✗ VERIFY_FAIL | — | wall_time | 128279 |
| cfd | L3 | ✗ VERIFY_FAIL | — | wall_time | 132273 |
| cfd | L4 | ✗ VERIFY_FAIL | — | wall_time | 125841 |
| dwt2d | L0 | ✗ RUN_FAIL | — | None | 166734 |
| dwt2d | L1 | ✗ RUN_FAIL | — | None | 174324 |
| dwt2d | L2 | ✗ RUN_FAIL | — | None | 175627 |
| dwt2d | L3 | ✗ RUN_FAIL | — | None | 166851 |
| dwt2d | L4 | ✗ RUN_FAIL | — | None | 225594 |
| gaussian | L0 | ✗ RUN_FAIL | — | None | 71934 |
| gaussian | L1 | ✗ RUN_FAIL | — | None | 45137 |
| gaussian | L2 | ✗ RUN_FAIL | — | None | 101358 |
| gaussian | L3 | ✗ RUN_FAIL | — | None | 72084 |
| gaussian | L4 | ✗ RUN_FAIL | — | None | 77022 |
| heartwall | L0 | ✗ VERIFY_FAIL | 548.000× | wall_time | 160261 |
| heartwall | L1 | ✗ VERIFY_FAIL | 548.000× | wall_time | 163559 |
| heartwall | L2 | ✗ VERIFY_FAIL | 548.000× | wall_time | 165942 |
| heartwall | L3 | ✗ VERIFY_FAIL | 548.000× | wall_time | 163466 |
| heartwall | L4 | ✗ VERIFY_FAIL | 548.000× | wall_time | 188486 |
| hotspot | L0 | ✗ VERIFY_FAIL | 0.566× | wall_time | 40109 |
| hotspot | L1 | ✗ VERIFY_FAIL | 0.671× | wall_time | 34346 |
| hotspot | L2 | ✗ VERIFY_FAIL | 0.677× | wall_time | 39539 |
| hotspot | L3 | ✗ VERIFY_FAIL | 0.685× | wall_time | 30184 |
| hotspot | L4 | ✗ RUN_FAIL | — | None | 33791 |
| hotspot3d | L0 | ✗ RUN_FAIL | — | None | 38596 |
| hotspot3d | L1 | ✗ RUN_FAIL | — | None | 26958 |
| hotspot3d | L2 | ✗ RUN_FAIL | — | None | 38005 |
| hotspot3d | L3 | ✗ RUN_FAIL | — | None | 34849 |
| hotspot3d | L4 | ✗ RUN_FAIL | — | None | 43307 |
| hybridsort | L0 | ✗ RUN_FAIL | — | None | 111801 |
| hybridsort | L1 | ✗ RUN_FAIL | — | None | 110398 |
| hybridsort | L2 | ✗ RUN_FAIL | — | None | 114391 |
| hybridsort | L3 | ✗ RUN_FAIL | — | None | 110964 |
| hybridsort | L4 | ✗ RUN_FAIL | — | None | 112880 |
| kmeans | L0 | ✗ VERIFY_FAIL | 2.914× | wall_time | 85596 |
| kmeans | L1 | ✗ VERIFY_FAIL | 2.892× | wall_time | 85131 |
| kmeans | L2 | ✗ VERIFY_FAIL | 2.937× | wall_time | 93052 |
| kmeans | L3 | ✗ VERIFY_FAIL | 2.897× | wall_time | 91925 |
| kmeans | L4 | ✗ VERIFY_FAIL | 2.826× | wall_time | 85464 |
| lavamd | L0 | ✗ RUN_FAIL | — | None | 39085 |
| lavamd | L1 | ✗ RUN_FAIL | — | None | 39068 |
| lavamd | L2 | ✗ RUN_FAIL | — | None | 39075 |
| lavamd | L3 | ✗ RUN_FAIL | — | None | 39488 |
| lavamd | L4 | ✗ RUN_FAIL | — | None | 39592 |
| lud | L0 | ✗ VERIFY_FAIL | 0.467× | wall_time | 48016 |
| lud | L1 | ✗ RUN_FAIL | — | None | 47669 |
| lud | L2 | ✗ RUN_FAIL | — | None | 47624 |
| lud | L3 | ✗ RUN_FAIL | — | None | 47661 |
| lud | L4 | ✗ RUN_FAIL | — | None | 47796 |
| myocyte | L0 | ✗ VERIFY_FAIL | 1.000× | wall_time | 212412 |
| myocyte | L1 | ✗ VERIFY_FAIL | 1.000× | wall_time | 447318 |
| myocyte | L2 | ✗ VERIFY_FAIL | 1.000× | wall_time | 209599 |
| myocyte | L3 | ✗ VERIFY_FAIL | 1.000× | wall_time | 297105 |
| myocyte | L4 | ✗ VERIFY_FAIL | 1.000× | wall_time | 305135 |
| nn | L0 | ✗ RUN_FAIL | — | None | 45376 |
| nn | L1 | ✗ RUN_FAIL | — | None | 38437 |
| nn | L2 | ✗ RUN_FAIL | — | None | 54161 |
| nn | L3 | ✗ RUN_FAIL | — | None | 37766 |
| nn | L4 | ✗ RUN_FAIL | — | None | 43021 |
| nw | L0 | ✗ EXTRACTION_FAIL | — | None | 129311 |
| nw | L1 | ✗ RUN_FAIL | — | None | 53723 |
| nw | L2 | ✗ RUN_FAIL | — | None | 48804 |
| nw | L3 | ✗ RUN_FAIL | — | None | 64449 |
| nw | L4 | ✗ RUN_FAIL | — | None | 57685 |
| particlefilter | L0 | ✗ VERIFY_FAIL | 0.456× | wall_time | 147192 |
| particlefilter | L1 | ✗ VERIFY_FAIL | 0.453× | wall_time | 96590 |
| particlefilter | L2 | ✗ VERIFY_FAIL | 0.462× | wall_time | 123932 |
| particlefilter | L3 | ✗ VERIFY_FAIL | 0.456× | wall_time | 148605 |
| particlefilter | L4 | ✗ VERIFY_FAIL | 0.459× | wall_time | 123966 |
| pathfinder | L0 | ✗ VERIFY_FAIL | — | wall_time | 20860 |
| pathfinder | L1 | ✗ VERIFY_FAIL | — | wall_time | 22221 |
| pathfinder | L2 | ✗ VERIFY_FAIL | — | wall_time | 25895 |
| pathfinder | L3 | ✗ VERIFY_FAIL | — | wall_time | 21007 |
| pathfinder | L4 | ✗ VERIFY_FAIL | — | wall_time | 24975 |
| srad | L0 | ✗ RUN_FAIL | — | None | 57195 |
| srad | L1 | ✗ RUN_FAIL | — | None | 54292 |
| srad | L2 | ✗ RUN_FAIL | — | None | 54630 |
| srad | L3 | ✗ RUN_FAIL | — | None | 54415 |
| srad | L4 | ✗ RUN_FAIL | — | None | 60557 |
| streamcluster | L0 | ✗ RUN_FAIL | — | None | 66678 |
| streamcluster | L1 | ✗ RUN_FAIL | — | None | 66809 |
| streamcluster | L2 | ✗ RUN_FAIL | — | None | 67216 |
| streamcluster | L3 | ✗ RUN_FAIL | — | None | 77489 |
| streamcluster | L4 | ✗ RUN_FAIL | — | None | 67921 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| backprop | L0 | ✗ VERIFY_FAIL |
| backprop | L1 | ✗ VERIFY_FAIL |
| backprop | L2 | ✗ VERIFY_FAIL |
| backprop | L3 | ✗ VERIFY_FAIL |
| backprop | L4 | ✗ VERIFY_FAIL |
| bfs | L0 | ✗ RUN_FAIL |
| bfs | L1 | ✗ VERIFY_FAIL |
| bfs | L2 | ✗ RUN_FAIL |
| bfs | L3 | ✗ RUN_FAIL |
| bfs | L4 | ✗ RUN_FAIL |
| bptree | L0 | ✗ RUN_FAIL |
| bptree | L1 | ✗ RUN_FAIL |
| bptree | L2 | ✗ RUN_FAIL |
| bptree | L3 | ✗ RUN_FAIL |
| bptree | L4 | ✗ RUN_FAIL |
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
| heartwall | L0 | ✗ VERIFY_FAIL |
| heartwall | L1 | ✗ VERIFY_FAIL |
| heartwall | L2 | ✗ VERIFY_FAIL |
| heartwall | L3 | ✗ VERIFY_FAIL |
| heartwall | L4 | ✗ VERIFY_FAIL |
| hotspot | L0 | ✗ VERIFY_FAIL |
| hotspot | L1 | ✗ VERIFY_FAIL |
| hotspot | L2 | ✗ VERIFY_FAIL |
| hotspot | L3 | ✗ VERIFY_FAIL |
| hotspot | L4 | ✗ RUN_FAIL |
| hotspot3d | L0 | ✗ RUN_FAIL |
| hotspot3d | L1 | ✗ RUN_FAIL |
| hotspot3d | L2 | ✗ RUN_FAIL |
| hotspot3d | L3 | ✗ RUN_FAIL |
| hotspot3d | L4 | ✗ RUN_FAIL |
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
| lud | L0 | ✗ VERIFY_FAIL |
| lud | L1 | ✗ RUN_FAIL |
| lud | L2 | ✗ RUN_FAIL |
| lud | L3 | ✗ RUN_FAIL |
| lud | L4 | ✗ RUN_FAIL |
| myocyte | L0 | ✗ VERIFY_FAIL |
| myocyte | L1 | ✗ VERIFY_FAIL |
| myocyte | L2 | ✗ VERIFY_FAIL |
| myocyte | L3 | ✗ VERIFY_FAIL |
| myocyte | L4 | ✗ VERIFY_FAIL |
| nn | L0 | ✗ RUN_FAIL |
| nn | L1 | ✗ RUN_FAIL |
| nn | L2 | ✗ RUN_FAIL |
| nn | L3 | ✗ RUN_FAIL |
| nn | L4 | ✗ RUN_FAIL |
| nw | L0 | ✗ EXTRACTION_FAIL |
| nw | L1 | ✗ RUN_FAIL |
| nw | L2 | ✗ RUN_FAIL |
| nw | L3 | ✗ RUN_FAIL |
| nw | L4 | ✗ RUN_FAIL |
| particlefilter | L0 | ✗ VERIFY_FAIL |
| particlefilter | L1 | ✗ VERIFY_FAIL |
| particlefilter | L2 | ✗ VERIFY_FAIL |
| particlefilter | L3 | ✗ VERIFY_FAIL |
| particlefilter | L4 | ✗ VERIFY_FAIL |
| pathfinder | L0 | ✗ VERIFY_FAIL |
| pathfinder | L1 | ✗ VERIFY_FAIL |
| pathfinder | L2 | ✗ VERIFY_FAIL |
| pathfinder | L3 | ✗ VERIFY_FAIL |
| pathfinder | L4 | ✗ VERIFY_FAIL |
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
