# Eval Batch: omp-to-opencl — 2026-03-31
**Date:** 2026-03-31  |  **Tasks:** 85

## together-qwen-3.5-397b-a17b
**22/85 PASS (25%)** | FAILURES=63 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| backprop | L0 | ✓ PASS | 0.005× | wall_time | 14732 |
| backprop | L1 | ✓ PASS | 0.005× | wall_time | 14735 |
| backprop | L2 | ✓ PASS | 0.005× | wall_time | 14763 |
| backprop | L3 | ✓ PASS | 0.004× | wall_time | 14846 |
| backprop | L4 | ✓ PASS | 0.005× | wall_time | 14637 |
| bfs | L0 | ✗ RUN_FAIL | — | None | 40605 |
| bfs | L1 | ✗ RUN_FAIL | — | None | 40680 |
| bfs | L2 | ✗ RUN_FAIL | — | None | 40617 |
| bfs | L3 | ✓ PASS | 0.843× | wall_time | 13161 |
| bfs | L4 | ✗ RUN_FAIL | — | None | 41286 |
| bptree | L0 | ✓ PASS | 0.657× | wall_time | 24232 |
| bptree | L1 | ✗ RUN_FAIL | — | None | 76479 |
| bptree | L2 | ✗ RUN_FAIL | — | None | 76671 |
| bptree | L3 | ✓ PASS | 0.664× | wall_time | 50193 |
| bptree | L4 | ✗ RUN_FAIL | — | None | 75847 |
| cfd | L0 | ✗ VERIFY_FAIL | — | wall_time | 92212 |
| cfd | L1 | ✗ VERIFY_FAIL | — | wall_time | 93285 |
| cfd | L2 | ✗ VERIFY_FAIL | — | wall_time | 95789 |
| cfd | L3 | ✗ VERIFY_FAIL | — | wall_time | 91984 |
| cfd | L4 | ✗ VERIFY_FAIL | — | wall_time | 98425 |
| heartwall | L0 | ✗ RUN_FAIL | — | None | 124577 |
| heartwall | L1 | ✗ RUN_FAIL | — | None | 124549 |
| heartwall | L2 | ✗ RUN_FAIL | — | None | 123075 |
| heartwall | L3 | ✗ RUN_FAIL | — | None | 122757 |
| heartwall | L4 | ✗ RUN_FAIL | — | None | 124437 |
| hotspot | L0 | ✗ RUN_FAIL | — | None | 32427 |
| hotspot | L1 | ✗ RUN_FAIL | — | None | 31664 |
| hotspot | L2 | ✓ PASS | 0.558× | wall_time | 9816 |
| hotspot | L3 | ✗ RUN_FAIL | — | None | 43183 |
| hotspot | L4 | ✓ PASS | 0.570× | wall_time | 9269 |
| hotspot3d | L0 | ✓ PASS | 0.891× | wall_time | 16738 |
| hotspot3d | L1 | ✗ RUN_FAIL | — | None | 24205 |
| hotspot3d | L2 | ✓ PASS | 0.893× | wall_time | 25740 |
| hotspot3d | L3 | ✓ PASS | 0.859× | wall_time | 7416 |
| hotspot3d | L4 | ✓ PASS | 0.852× | wall_time | 8285 |
| kmeans | L0 | ✗ VERIFY_FAIL | 3.002× | wall_time | 124773 |
| kmeans | L1 | ✗ VERIFY_FAIL | 2.903× | wall_time | 125055 |
| kmeans | L2 | ✗ VERIFY_FAIL | 2.897× | wall_time | 125345 |
| kmeans | L3 | ✗ VERIFY_FAIL | 2.926× | wall_time | 139959 |
| kmeans | L4 | ✗ VERIFY_FAIL | 2.914× | wall_time | 127335 |
| lavamd | L0 | ✗ RUN_FAIL | — | None | 34237 |
| lavamd | L1 | ✗ RUN_FAIL | — | None | 35004 |
| lavamd | L2 | ✗ RUN_FAIL | — | None | 34306 |
| lavamd | L3 | ✗ RUN_FAIL | — | None | 36559 |
| lavamd | L4 | ✗ RUN_FAIL | — | None | 34292 |
| lud | L0 | ✓ PASS | 0.253× | wall_time | 15740 |
| lud | L1 | ✓ PASS | 0.256× | wall_time | 14008 |
| lud | L2 | ✓ PASS | 0.219× | wall_time | 14178 |
| lud | L3 | ✓ PASS | 0.251× | wall_time | 17053 |
| lud | L4 | ✗ RUN_FAIL | — | None | 49322 |
| myocyte | L0 | ✗ RUN_FAIL | — | None | 294581 |
| myocyte | L1 | ✗ RUN_FAIL | — | None | 409665 |
| myocyte | L2 | ✗ RUN_FAIL | — | None | 416415 |
| myocyte | L3 | ✗ RUN_FAIL | — | None | 292337 |
| myocyte | L4 | ✗ RUN_FAIL | — | None | 303055 |
| nn | L0 | ✗ RUN_FAIL | — | None | 42424 |
| nn | L1 | ✗ RUN_FAIL | — | None | 39735 |
| nn | L2 | ✗ EXTRACTION_FAIL | — | None | 119070 |
| nn | L3 | ✗ RUN_FAIL | — | None | 39161 |
| nn | L4 | ✗ RUN_FAIL | — | None | 39871 |
| nw | L0 | ✗ RUN_FAIL | — | None | 44629 |
| nw | L1 | ✗ RUN_FAIL | — | None | 45371 |
| nw | L2 | ✗ RUN_FAIL | — | None | 45228 |
| nw | L3 | ✗ RUN_FAIL | — | None | 44863 |
| nw | L4 | ✗ RUN_FAIL | — | None | 50441 |
| particlefilter | L0 | ✗ VERIFY_FAIL | 0.451× | wall_time | 76888 |
| particlefilter | L1 | ✗ VERIFY_FAIL | 0.448× | wall_time | 60249 |
| particlefilter | L2 | ✗ VERIFY_FAIL | 0.395× | wall_time | 56682 |
| particlefilter | L3 | ✗ VERIFY_FAIL | 0.456× | wall_time | 91016 |
| particlefilter | L4 | ✗ VERIFY_FAIL | 0.451× | wall_time | 73968 |
| pathfinder | L0 | ✓ PASS | — | wall_time | 4753 |
| pathfinder | L1 | ✓ PASS | — | wall_time | 9829 |
| pathfinder | L2 | ✓ PASS | — | wall_time | 5044 |
| pathfinder | L3 | ✓ PASS | — | wall_time | 4657 |
| pathfinder | L4 | ✗ RUN_FAIL | — | None | 22460 |
| srad | L0 | ✗ RUN_FAIL | — | None | 44955 |
| srad | L1 | ✗ RUN_FAIL | — | None | 53701 |
| srad | L2 | ✗ RUN_FAIL | — | None | 46036 |
| srad | L3 | ✗ RUN_FAIL | — | None | 45250 |
| srad | L4 | ✗ RUN_FAIL | — | None | 45726 |
| streamcluster | L0 | ✗ RUN_FAIL | — | None | 87472 |
| streamcluster | L1 | ✗ RUN_FAIL | — | None | 87999 |
| streamcluster | L2 | ✗ RUN_FAIL | — | None | 87513 |
| streamcluster | L3 | ✗ RUN_FAIL | — | None | 151080 |
| streamcluster | L4 | ✗ RUN_FAIL | — | None | 96580 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| backprop | L0 | ✓ PASS |
| backprop | L1 | ✓ PASS |
| backprop | L2 | ✓ PASS |
| backprop | L3 | ✓ PASS |
| backprop | L4 | ✓ PASS |
| bfs | L0 | ✗ RUN_FAIL |
| bfs | L1 | ✗ RUN_FAIL |
| bfs | L2 | ✗ RUN_FAIL |
| bfs | L3 | ✓ PASS |
| bfs | L4 | ✗ RUN_FAIL |
| bptree | L0 | ✓ PASS |
| bptree | L1 | ✗ RUN_FAIL |
| bptree | L2 | ✗ RUN_FAIL |
| bptree | L3 | ✓ PASS |
| bptree | L4 | ✗ RUN_FAIL |
| cfd | L0 | ✗ VERIFY_FAIL |
| cfd | L1 | ✗ VERIFY_FAIL |
| cfd | L2 | ✗ VERIFY_FAIL |
| cfd | L3 | ✗ VERIFY_FAIL |
| cfd | L4 | ✗ VERIFY_FAIL |
| heartwall | L0 | ✗ RUN_FAIL |
| heartwall | L1 | ✗ RUN_FAIL |
| heartwall | L2 | ✗ RUN_FAIL |
| heartwall | L3 | ✗ RUN_FAIL |
| heartwall | L4 | ✗ RUN_FAIL |
| hotspot | L0 | ✗ RUN_FAIL |
| hotspot | L1 | ✗ RUN_FAIL |
| hotspot | L2 | ✓ PASS |
| hotspot | L3 | ✗ RUN_FAIL |
| hotspot | L4 | ✓ PASS |
| hotspot3d | L0 | ✓ PASS |
| hotspot3d | L1 | ✗ RUN_FAIL |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✓ PASS |
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
| lud | L0 | ✓ PASS |
| lud | L1 | ✓ PASS |
| lud | L2 | ✓ PASS |
| lud | L3 | ✓ PASS |
| lud | L4 | ✗ RUN_FAIL |
| myocyte | L0 | ✗ RUN_FAIL |
| myocyte | L1 | ✗ RUN_FAIL |
| myocyte | L2 | ✗ RUN_FAIL |
| myocyte | L3 | ✗ RUN_FAIL |
| myocyte | L4 | ✗ RUN_FAIL |
| nn | L0 | ✗ RUN_FAIL |
| nn | L1 | ✗ RUN_FAIL |
| nn | L2 | ✗ EXTRACTION_FAIL |
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
| pathfinder | L0 | ✓ PASS |
| pathfinder | L1 | ✓ PASS |
| pathfinder | L2 | ✓ PASS |
| pathfinder | L3 | ✓ PASS |
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
