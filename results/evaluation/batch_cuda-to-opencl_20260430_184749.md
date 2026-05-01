# Eval Batch: cuda-to-opencl — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 48

## azure-gpt-5.3-codex
**47/48 PASS (97%)** | FAILURES=1 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| bfs | L1 | ✓ PASS | 0.821× | wall_time | 14013 |
| bfs | L2 | ✓ PASS | 0.811× | wall_time | 13868 |
| bfs | L3 | ✓ PASS | 0.824× | wall_time | 13599 |
| bfs | L4 | ✓ PASS | 0.796× | wall_time | 13617 |
| bptree | L1 | ✓ PASS | 0.691× | wall_time | 13495 |
| bptree | L2 | ✓ PASS | 0.676× | wall_time | 13179 |
| bptree | L3 | ✓ PASS | 0.672× | wall_time | 13519 |
| bptree | L4 | ✓ PASS | 0.684× | wall_time | 13545 |
| dwt2d | L1 | ✓ PASS | 0.099× | wall_time | 35788 |
| dwt2d | L2 | ✓ PASS | 0.365× | wall_time | 36939 |
| dwt2d | L3 | ✗ RUN_FAIL | — | None | 38210 |
| dwt2d | L4 | ✓ PASS | 0.270× | wall_time | 37221 |
| hotspot | L1 | ✓ PASS | 0.593× | wall_time | 8670 |
| hotspot | L2 | ✓ PASS | 0.593× | wall_time | 8992 |
| hotspot | L3 | ✓ PASS | 0.562× | wall_time | 8802 |
| hotspot | L4 | ✓ PASS | 0.570× | wall_time | 9186 |
| hotspot3d | L1 | ✓ PASS | 0.896× | wall_time | 7867 |
| hotspot3d | L2 | ✓ PASS | 0.897× | wall_time | 8253 |
| hotspot3d | L3 | ✓ PASS | 0.874× | wall_time | 8077 |
| hotspot3d | L4 | ✓ PASS | 0.874× | wall_time | 8275 |
| lud | L1 | ✓ PASS | 0.286× | wall_time | 14361 |
| lud | L2 | ✓ PASS | 0.293× | wall_time | 14838 |
| lud | L3 | ✓ PASS | 0.288× | wall_time | 14001 |
| lud | L4 | ✓ PASS | 0.293× | wall_time | 13789 |
| mixbench | L1 | ✓ PASS | 8.108× | wall_time | 13197 |
| mixbench | L2 | ✓ PASS | 6.786× | wall_time | 14937 |
| mixbench | L3 | ✓ PASS | 7.004× | wall_time | 14239 |
| mixbench | L4 | ✓ PASS | 6.708× | wall_time | 13824 |
| nw | L1 | ✓ PASS | 0.363× | wall_time | 14075 |
| nw | L2 | ✓ PASS | 0.375× | wall_time | 14187 |
| nw | L3 | ✓ PASS | 0.342× | wall_time | 14388 |
| nw | L4 | ✓ PASS | 0.364× | wall_time | 14271 |
| pathfinder | L1 | ✓ PASS | — | wall_time | 6177 |
| pathfinder | L2 | ✓ PASS | — | wall_time | 6218 |
| pathfinder | L3 | ✓ PASS | — | wall_time | 6036 |
| pathfinder | L4 | ✓ PASS | — | wall_time | 6805 |
| rsbench | L1 | ✓ PASS | 0.929× | wall_time | 30258 |
| rsbench | L2 | ✓ PASS | 0.929× | wall_time | 29945 |
| rsbench | L3 | ✓ PASS | 0.880× | wall_time | 30197 |
| rsbench | L4 | ✓ PASS | 0.879× | wall_time | 30436 |
| srad | L1 | ✓ PASS | 0.336× | wall_time | 17461 |
| srad | L2 | ✓ PASS | 0.345× | wall_time | 16645 |
| srad | L3 | ✓ PASS | 0.345× | wall_time | 17962 |
| srad | L4 | ✓ PASS | 0.344× | wall_time | 16333 |
| xsbench | L1 | ✓ PASS | 0.982× | wall_time | 31811 |
| xsbench | L2 | ✓ PASS | 1.023× | wall_time | 32034 |
| xsbench | L3 | ✓ PASS | 0.965× | wall_time | 31871 |
| xsbench | L4 | ✓ PASS | 0.980× | wall_time | 31875 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.3-codex |
|--------|-------|---|
| bfs | L1 | ✓ PASS |
| bfs | L2 | ✓ PASS |
| bfs | L3 | ✓ PASS |
| bfs | L4 | ✓ PASS |
| bptree | L1 | ✓ PASS |
| bptree | L2 | ✓ PASS |
| bptree | L3 | ✓ PASS |
| bptree | L4 | ✓ PASS |
| dwt2d | L1 | ✓ PASS |
| dwt2d | L2 | ✓ PASS |
| dwt2d | L3 | ✗ RUN_FAIL |
| dwt2d | L4 | ✓ PASS |
| hotspot | L1 | ✓ PASS |
| hotspot | L2 | ✓ PASS |
| hotspot | L3 | ✓ PASS |
| hotspot | L4 | ✓ PASS |
| hotspot3d | L1 | ✓ PASS |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✓ PASS |
| lud | L1 | ✓ PASS |
| lud | L2 | ✓ PASS |
| lud | L3 | ✓ PASS |
| lud | L4 | ✓ PASS |
| mixbench | L1 | ✓ PASS |
| mixbench | L2 | ✓ PASS |
| mixbench | L3 | ✓ PASS |
| mixbench | L4 | ✓ PASS |
| nw | L1 | ✓ PASS |
| nw | L2 | ✓ PASS |
| nw | L3 | ✓ PASS |
| nw | L4 | ✓ PASS |
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
| srad | L4 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
