# Eval Batch: omp-to-opencl — 2026-04-26
**Date:** 2026-04-26  |  **Tasks:** 56

## azure-gpt-5.4
**47/56 PASS (83%)** | FAILURES=9 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| bfs | L1 | ✓ PASS | 0.849× | wall_time | 12927 |
| bfs | L2 | ✓ PASS | 0.808× | wall_time | 12841 |
| bfs | L3 | ✓ PASS | 0.805× | wall_time | 13016 |
| bfs | L4 | ✓ PASS | 0.820× | wall_time | 13216 |
| bptree | L1 | ✓ PASS | 0.658× | wall_time | 25277 |
| bptree | L2 | ✓ PASS | 0.634× | wall_time | 25077 |
| bptree | L3 | ✓ PASS | 0.651× | wall_time | 26064 |
| bptree | L4 | ✓ PASS | 0.661× | wall_time | 26674 |
| hotspot | L1 | ✓ PASS | 0.355× | wall_time | 11236 |
| hotspot | L2 | ✓ PASS | 0.552× | wall_time | 15183 |
| hotspot | L3 | ✓ PASS | 0.546× | wall_time | 14085 |
| hotspot | L4 | ✓ PASS | 0.442× | wall_time | 11723 |
| hotspot3d | L1 | ✗ VERIFY_FAIL | 0.064× | wall_time | 12089 |
| hotspot3d | L2 | ✗ VERIFY_FAIL | 0.064× | wall_time | 9529 |
| hotspot3d | L3 | ✗ VERIFY_FAIL | 0.068× | wall_time | 12832 |
| hotspot3d | L4 | ✗ VERIFY_FAIL | 0.064× | wall_time | 11031 |
| lavamd | L1 | ✗ RUN_FAIL | — | None | 10490 |
| lavamd | L2 | ✓ PASS | 0.005× | wall_time | 11996 |
| lavamd | L3 | ✓ PASS | 0.005× | wall_time | 11323 |
| lavamd | L4 | ✓ PASS | 0.005× | wall_time | 11434 |
| lud | L1 | ✓ PASS | 0.245× | wall_time | 15598 |
| lud | L2 | ✓ PASS | 0.161× | wall_time | 14808 |
| lud | L3 | ✓ PASS | 0.271× | wall_time | 15945 |
| lud | L4 | ✓ PASS | 0.246× | wall_time | 15466 |
| mixbench | L1 | ✓ PASS | 8.441× | wall_time | 15518 |
| mixbench | L2 | ✓ PASS | 6.900× | wall_time | 15827 |
| mixbench | L3 | ✓ PASS | 7.236× | wall_time | 16452 |
| mixbench | L4 | ✓ PASS | 8.586× | wall_time | 16671 |
| myocyte | L1 | ✗ RUN_FAIL | — | None | 45353 |
| myocyte | L2 | ✓ PASS | 0.002× | wall_time | 45925 |
| myocyte | L3 | ✗ RUN_FAIL | — | None | 46716 |
| myocyte | L4 | ✓ PASS | 0.002× | wall_time | 48430 |
| nw | L1 | ✓ PASS | 0.318× | wall_time | 14443 |
| nw | L2 | ✓ PASS | 0.326× | wall_time | 14689 |
| nw | L3 | ✓ PASS | 0.324× | wall_time | 15139 |
| nw | L4 | ✓ PASS | 0.344× | wall_time | 16078 |
| particlefilter | L1 | ✓ PASS | 0.270× | wall_time | 21875 |
| particlefilter | L2 | ✗ VERIFY_FAIL | 0.262× | wall_time | 22512 |
| particlefilter | L3 | ✓ PASS | 0.112× | wall_time | 22846 |
| particlefilter | L4 | ✓ PASS | 0.129× | wall_time | 23673 |
| pathfinder | L1 | ✓ PASS | — | wall_time | 6894 |
| pathfinder | L2 | ✓ PASS | — | wall_time | 6709 |
| pathfinder | L3 | ✓ PASS | — | wall_time | 5827 |
| pathfinder | L4 | ✓ PASS | — | wall_time | 6767 |
| rsbench | L1 | ✓ PASS | 0.882× | wall_time | 30654 |
| rsbench | L2 | ✓ PASS | 0.882× | wall_time | 31478 |
| rsbench | L3 | ✓ PASS | 0.881× | wall_time | 31357 |
| rsbench | L4 | ✓ PASS | 0.883× | wall_time | 31707 |
| srad | L1 | ✓ PASS | 0.359× | wall_time | 14952 |
| srad | L2 | ✓ PASS | 0.350× | wall_time | 16485 |
| srad | L3 | ✓ PASS | 0.365× | wall_time | 15312 |
| srad | L4 | ✗ RUN_FAIL | — | None | 14424 |
| xsbench | L1 | ✓ PASS | 0.996× | wall_time | 30718 |
| xsbench | L2 | ✓ PASS | 0.989× | wall_time | 29683 |
| xsbench | L3 | ✓ PASS | 0.980× | wall_time | 31763 |
| xsbench | L4 | ✓ PASS | 1.005× | wall_time | 31251 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.4 |
|--------|-------|---|
| bfs | L1 | ✓ PASS |
| bfs | L2 | ✓ PASS |
| bfs | L3 | ✓ PASS |
| bfs | L4 | ✓ PASS |
| bptree | L1 | ✓ PASS |
| bptree | L2 | ✓ PASS |
| bptree | L3 | ✓ PASS |
| bptree | L4 | ✓ PASS |
| hotspot | L1 | ✓ PASS |
| hotspot | L2 | ✓ PASS |
| hotspot | L3 | ✓ PASS |
| hotspot | L4 | ✓ PASS |
| hotspot3d | L1 | ✗ VERIFY_FAIL |
| hotspot3d | L2 | ✗ VERIFY_FAIL |
| hotspot3d | L3 | ✗ VERIFY_FAIL |
| hotspot3d | L4 | ✗ VERIFY_FAIL |
| lavamd | L1 | ✗ RUN_FAIL |
| lavamd | L2 | ✓ PASS |
| lavamd | L3 | ✓ PASS |
| lavamd | L4 | ✓ PASS |
| lud | L1 | ✓ PASS |
| lud | L2 | ✓ PASS |
| lud | L3 | ✓ PASS |
| lud | L4 | ✓ PASS |
| mixbench | L1 | ✓ PASS |
| mixbench | L2 | ✓ PASS |
| mixbench | L3 | ✓ PASS |
| mixbench | L4 | ✓ PASS |
| myocyte | L1 | ✗ RUN_FAIL |
| myocyte | L2 | ✓ PASS |
| myocyte | L3 | ✗ RUN_FAIL |
| myocyte | L4 | ✓ PASS |
| nw | L1 | ✓ PASS |
| nw | L2 | ✓ PASS |
| nw | L3 | ✓ PASS |
| nw | L4 | ✓ PASS |
| particlefilter | L1 | ✓ PASS |
| particlefilter | L2 | ✗ VERIFY_FAIL |
| particlefilter | L3 | ✓ PASS |
| particlefilter | L4 | ✓ PASS |
| pathfinder | L1 | ✓ PASS |
| pathfinder | L2 | ✓ PASS |
| pathfinder | L3 | ✓ PASS |
| pathfinder | L4 | ✓ PASS |
| rsbench | L1 | ✓ PASS |
| rsbench | L2 | ✓ PASS |
| rsbench | L3 | ✓ PASS |
| rsbench | L4 | ✓ PASS |
| srad | L1 | ✓ PASS |
| srad | L2 | ✓ PASS |
| srad | L3 | ✓ PASS |
| srad | L4 | ✗ RUN_FAIL |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
