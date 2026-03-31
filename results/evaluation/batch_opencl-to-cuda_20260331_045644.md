# Eval Batch: opencl-to-cuda — 2026-03-31
**Date:** 2026-03-31  |  **Tasks:** 100

## together-qwen-3.5-397b-a17b
**6/100 PASS (6%)** | FAILURES=94 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| backprop | L0 | ✗ BUILD_FAIL | — | None | 61903 |
| backprop | L1 | ✗ BUILD_FAIL | — | None | 70707 |
| backprop | L2 | ✗ BUILD_FAIL | — | None | 61834 |
| backprop | L3 | ✗ BUILD_FAIL | — | None | 63612 |
| backprop | L4 | ✗ BUILD_FAIL | — | None | 63797 |
| bfs | L0 | ✗ BUILD_FAIL | — | None | 60539 |
| bfs | L1 | ✗ BUILD_FAIL | — | None | 60141 |
| bfs | L2 | ✗ BUILD_FAIL | — | None | 62916 |
| bfs | L3 | ✗ BUILD_FAIL | — | None | 64797 |
| bfs | L4 | ✗ BUILD_FAIL | — | None | 65982 |
| bptree | L0 | ✗ BUILD_FAIL | — | None | 112645 |
| bptree | L1 | ✗ BUILD_FAIL | — | None | 117690 |
| bptree | L2 | ✗ BUILD_FAIL | — | None | 111211 |
| bptree | L3 | ✗ BUILD_FAIL | — | None | 114076 |
| bptree | L4 | ✗ BUILD_FAIL | — | None | 114533 |
| cfd | L0 | ✓ PASS | — | wall_time | 144843 |
| cfd | L1 | ✓ PASS | — | wall_time | 148014 |
| cfd | L2 | ✗ BUILD_FAIL | — | None | 145272 |
| cfd | L3 | ✓ PASS | — | wall_time | 146743 |
| cfd | L4 | ✗ BUILD_FAIL | — | None | 145046 |
| dwt2d | L0 | ✗ BUILD_FAIL | — | None | 144969 |
| dwt2d | L1 | ✗ EXTRACTION_FAIL | — | None | 153358 |
| dwt2d | L2 | ✗ BUILD_FAIL | — | None | 147887 |
| dwt2d | L3 | ✗ BUILD_FAIL | — | None | 150226 |
| dwt2d | L4 | ✗ BUILD_FAIL | — | None | 148512 |
| gaussian | L0 | ✗ VERIFY_FAIL | 0.500× | wall_time | 77607 |
| gaussian | L1 | ✗ VERIFY_FAIL | 0.500× | wall_time | 74913 |
| gaussian | L2 | ✗ VERIFY_FAIL | 0.503× | wall_time | 78447 |
| gaussian | L3 | ✗ VERIFY_FAIL | 0.493× | wall_time | 79506 |
| gaussian | L4 | ✗ VERIFY_FAIL | 0.507× | wall_time | 80237 |
| heartwall | L0 | ✗ BUILD_FAIL | — | None | 207810 |
| heartwall | L1 | ✗ BUILD_FAIL | — | None | 245791 |
| heartwall | L2 | ✗ BUILD_FAIL | — | None | 209498 |
| heartwall | L3 | ✗ BUILD_FAIL | — | None | 209490 |
| heartwall | L4 | ✗ BUILD_FAIL | — | None | 247880 |
| hotspot | L0 | ✗ VERIFY_FAIL | 0.611× | wall_time | 43256 |
| hotspot | L1 | ✗ VERIFY_FAIL | 0.634× | wall_time | 42353 |
| hotspot | L2 | ✗ VERIFY_FAIL | 0.653× | wall_time | 39750 |
| hotspot | L3 | ✗ VERIFY_FAIL | 0.554× | wall_time | 45979 |
| hotspot | L4 | ✗ VERIFY_FAIL | 0.626× | wall_time | 40178 |
| hotspot3d | L0 | ✗ BUILD_FAIL | — | None | 51239 |
| hotspot3d | L1 | ✗ BUILD_FAIL | — | None | 51027 |
| hotspot3d | L2 | ✗ BUILD_FAIL | — | None | 58719 |
| hotspot3d | L3 | ✗ BUILD_FAIL | — | None | 52545 |
| hotspot3d | L4 | ✗ BUILD_FAIL | — | None | 58360 |
| hybridsort | L0 | ✗ BUILD_FAIL | — | None | 169865 |
| hybridsort | L1 | ✗ BUILD_FAIL | — | None | 166803 |
| hybridsort | L2 | ✗ BUILD_FAIL | — | None | 143908 |
| hybridsort | L3 | ✗ BUILD_FAIL | — | None | 141849 |
| hybridsort | L4 | ✗ BUILD_FAIL | — | None | 151311 |
| kmeans | L0 | ✗ BUILD_FAIL | — | None | 109713 |
| kmeans | L1 | ✗ BUILD_FAIL | — | None | 105922 |
| kmeans | L2 | ✗ BUILD_FAIL | — | None | 109221 |
| kmeans | L3 | ✗ BUILD_FAIL | — | None | 106170 |
| kmeans | L4 | ✗ BUILD_FAIL | — | None | 110028 |
| lavamd | L0 | ✗ BUILD_FAIL | — | None | 44910 |
| lavamd | L1 | ✗ BUILD_FAIL | — | None | 45411 |
| lavamd | L2 | ✗ BUILD_FAIL | — | None | 44867 |
| lavamd | L3 | ✗ BUILD_FAIL | — | None | 44497 |
| lavamd | L4 | ✗ BUILD_FAIL | — | None | 45381 |
| lud | L0 | ✗ BUILD_FAIL | — | None | 53263 |
| lud | L1 | ✗ BUILD_FAIL | — | None | 81924 |
| lud | L2 | ✗ BUILD_FAIL | — | None | 51518 |
| lud | L3 | ✗ BUILD_FAIL | — | None | 53798 |
| lud | L4 | ✗ BUILD_FAIL | — | None | 55569 |
| myocyte | L0 | ✗ BUILD_FAIL | — | None | 270967 |
| myocyte | L1 | ✗ BUILD_FAIL | — | None | 271053 |
| myocyte | L2 | ✗ BUILD_FAIL | — | None | 264709 |
| myocyte | L3 | ✗ BUILD_FAIL | — | None | 248459 |
| myocyte | L4 | ✗ BUILD_FAIL | — | None | 264807 |
| nn | L0 | ✗ RUN_FAIL | — | None | 62184 |
| nn | L1 | ✗ VERIFY_FAIL | 0.520× | wall_time | 66854 |
| nn | L2 | ✗ BUILD_FAIL | — | None | 67893 |
| nn | L3 | ✗ VERIFY_FAIL | 0.510× | wall_time | 61809 |
| nn | L4 | ✗ VERIFY_FAIL | 0.513× | wall_time | 68311 |
| nw | L0 | ✗ BUILD_FAIL | — | None | 69727 |
| nw | L1 | ✗ BUILD_FAIL | — | None | 67860 |
| nw | L2 | ✗ BUILD_FAIL | — | None | 71942 |
| nw | L3 | ✗ BUILD_FAIL | — | None | 67780 |
| nw | L4 | ✗ BUILD_FAIL | — | None | 70796 |
| particlefilter | L0 | ✓ PASS | 0.525× | wall_time | 105195 |
| particlefilter | L1 | ✓ PASS | 0.616× | wall_time | 44957 |
| particlefilter | L2 | ✓ PASS | 0.600× | wall_time | 101436 |
| particlefilter | L3 | ✗ BUILD_FAIL | — | None | 161691 |
| particlefilter | L4 | ✗ RUN_FAIL | — | None | 155062 |
| pathfinder | L0 | ✗ BUILD_FAIL | — | None | 35128 |
| pathfinder | L1 | ✗ BUILD_FAIL | — | None | 48647 |
| pathfinder | L2 | ✗ BUILD_FAIL | — | None | 38545 |
| pathfinder | L3 | ✗ BUILD_FAIL | — | None | 49035 |
| pathfinder | L4 | ✗ VERIFY_FAIL | 0.621× | wall_time | 42338 |
| srad | L0 | ✗ BUILD_FAIL | — | None | 71514 |
| srad | L1 | ✗ BUILD_FAIL | — | None | 87549 |
| srad | L2 | ✗ BUILD_FAIL | — | None | 88142 |
| srad | L3 | ✗ BUILD_FAIL | — | None | 83358 |
| srad | L4 | ✗ BUILD_FAIL | — | None | 86197 |
| streamcluster | L0 | ✗ BUILD_FAIL | — | None | 128728 |
| streamcluster | L1 | ✗ BUILD_FAIL | — | None | 131595 |
| streamcluster | L2 | ✗ BUILD_FAIL | — | None | 130175 |
| streamcluster | L3 | ✗ BUILD_FAIL | — | None | 130637 |
| streamcluster | L4 | ✗ BUILD_FAIL | — | None | 134613 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| backprop | L0 | ✗ BUILD_FAIL |
| backprop | L1 | ✗ BUILD_FAIL |
| backprop | L2 | ✗ BUILD_FAIL |
| backprop | L3 | ✗ BUILD_FAIL |
| backprop | L4 | ✗ BUILD_FAIL |
| bfs | L0 | ✗ BUILD_FAIL |
| bfs | L1 | ✗ BUILD_FAIL |
| bfs | L2 | ✗ BUILD_FAIL |
| bfs | L3 | ✗ BUILD_FAIL |
| bfs | L4 | ✗ BUILD_FAIL |
| bptree | L0 | ✗ BUILD_FAIL |
| bptree | L1 | ✗ BUILD_FAIL |
| bptree | L2 | ✗ BUILD_FAIL |
| bptree | L3 | ✗ BUILD_FAIL |
| bptree | L4 | ✗ BUILD_FAIL |
| cfd | L0 | ✓ PASS |
| cfd | L1 | ✓ PASS |
| cfd | L2 | ✗ BUILD_FAIL |
| cfd | L3 | ✓ PASS |
| cfd | L4 | ✗ BUILD_FAIL |
| dwt2d | L0 | ✗ BUILD_FAIL |
| dwt2d | L1 | ✗ EXTRACTION_FAIL |
| dwt2d | L2 | ✗ BUILD_FAIL |
| dwt2d | L3 | ✗ BUILD_FAIL |
| dwt2d | L4 | ✗ BUILD_FAIL |
| gaussian | L0 | ✗ VERIFY_FAIL |
| gaussian | L1 | ✗ VERIFY_FAIL |
| gaussian | L2 | ✗ VERIFY_FAIL |
| gaussian | L3 | ✗ VERIFY_FAIL |
| gaussian | L4 | ✗ VERIFY_FAIL |
| heartwall | L0 | ✗ BUILD_FAIL |
| heartwall | L1 | ✗ BUILD_FAIL |
| heartwall | L2 | ✗ BUILD_FAIL |
| heartwall | L3 | ✗ BUILD_FAIL |
| heartwall | L4 | ✗ BUILD_FAIL |
| hotspot | L0 | ✗ VERIFY_FAIL |
| hotspot | L1 | ✗ VERIFY_FAIL |
| hotspot | L2 | ✗ VERIFY_FAIL |
| hotspot | L3 | ✗ VERIFY_FAIL |
| hotspot | L4 | ✗ VERIFY_FAIL |
| hotspot3d | L0 | ✗ BUILD_FAIL |
| hotspot3d | L1 | ✗ BUILD_FAIL |
| hotspot3d | L2 | ✗ BUILD_FAIL |
| hotspot3d | L3 | ✗ BUILD_FAIL |
| hotspot3d | L4 | ✗ BUILD_FAIL |
| hybridsort | L0 | ✗ BUILD_FAIL |
| hybridsort | L1 | ✗ BUILD_FAIL |
| hybridsort | L2 | ✗ BUILD_FAIL |
| hybridsort | L3 | ✗ BUILD_FAIL |
| hybridsort | L4 | ✗ BUILD_FAIL |
| kmeans | L0 | ✗ BUILD_FAIL |
| kmeans | L1 | ✗ BUILD_FAIL |
| kmeans | L2 | ✗ BUILD_FAIL |
| kmeans | L3 | ✗ BUILD_FAIL |
| kmeans | L4 | ✗ BUILD_FAIL |
| lavamd | L0 | ✗ BUILD_FAIL |
| lavamd | L1 | ✗ BUILD_FAIL |
| lavamd | L2 | ✗ BUILD_FAIL |
| lavamd | L3 | ✗ BUILD_FAIL |
| lavamd | L4 | ✗ BUILD_FAIL |
| lud | L0 | ✗ BUILD_FAIL |
| lud | L1 | ✗ BUILD_FAIL |
| lud | L2 | ✗ BUILD_FAIL |
| lud | L3 | ✗ BUILD_FAIL |
| lud | L4 | ✗ BUILD_FAIL |
| myocyte | L0 | ✗ BUILD_FAIL |
| myocyte | L1 | ✗ BUILD_FAIL |
| myocyte | L2 | ✗ BUILD_FAIL |
| myocyte | L3 | ✗ BUILD_FAIL |
| myocyte | L4 | ✗ BUILD_FAIL |
| nn | L0 | ✗ RUN_FAIL |
| nn | L1 | ✗ VERIFY_FAIL |
| nn | L2 | ✗ BUILD_FAIL |
| nn | L3 | ✗ VERIFY_FAIL |
| nn | L4 | ✗ VERIFY_FAIL |
| nw | L0 | ✗ BUILD_FAIL |
| nw | L1 | ✗ BUILD_FAIL |
| nw | L2 | ✗ BUILD_FAIL |
| nw | L3 | ✗ BUILD_FAIL |
| nw | L4 | ✗ BUILD_FAIL |
| particlefilter | L0 | ✓ PASS |
| particlefilter | L1 | ✓ PASS |
| particlefilter | L2 | ✓ PASS |
| particlefilter | L3 | ✗ BUILD_FAIL |
| particlefilter | L4 | ✗ RUN_FAIL |
| pathfinder | L0 | ✗ BUILD_FAIL |
| pathfinder | L1 | ✗ BUILD_FAIL |
| pathfinder | L2 | ✗ BUILD_FAIL |
| pathfinder | L3 | ✗ BUILD_FAIL |
| pathfinder | L4 | ✗ VERIFY_FAIL |
| srad | L0 | ✗ BUILD_FAIL |
| srad | L1 | ✗ BUILD_FAIL |
| srad | L2 | ✗ BUILD_FAIL |
| srad | L3 | ✗ BUILD_FAIL |
| srad | L4 | ✗ BUILD_FAIL |
| streamcluster | L0 | ✗ BUILD_FAIL |
| streamcluster | L1 | ✗ BUILD_FAIL |
| streamcluster | L2 | ✗ BUILD_FAIL |
| streamcluster | L3 | ✗ BUILD_FAIL |
| streamcluster | L4 | ✗ BUILD_FAIL |
