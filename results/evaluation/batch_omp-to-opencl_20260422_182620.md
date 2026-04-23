# Eval Batch: omp-to-opencl — 2026-04-22
**Date:** 2026-04-22  |  **Tasks:** 40

## together-qwen-3.5-397b-a17b
**25/40 PASS (62%)** | FAILURES=15 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| backprop | L1 | ✗ VERIFY_FAIL | 0.006× | wall_time | 15665 |
| backprop | L2 | ✓ PASS | 0.005× | wall_time | 14995 |
| backprop | L3 | ✗ VERIFY_FAIL | 0.006× | wall_time | 15957 |
| backprop | L4 | ✓ PASS | 0.003× | wall_time | 15357 |
| bfs | L1 | ✓ PASS | 0.817× | wall_time | 13586 |
| bfs | L2 | ✓ PASS | 0.783× | wall_time | 13582 |
| bfs | L3 | ✗ RUN_FAIL | — | None | 14339 |
| bfs | L4 | ✗ RUN_FAIL | — | None | 15208 |
| hotspot | L1 | ✓ PASS | 0.387× | wall_time | 17217 |
| hotspot | L2 | ✓ PASS | 0.572× | wall_time | 21487 |
| hotspot | L3 | ✓ PASS | 0.564× | wall_time | 11084 |
| hotspot | L4 | ✓ PASS | 0.566× | wall_time | 14895 |
| hotspot3d | L1 | ✓ PASS | 0.895× | wall_time | 8433 |
| hotspot3d | L2 | ✓ PASS | 0.882× | wall_time | 9651 |
| hotspot3d | L3 | ✓ PASS | 0.891× | wall_time | 10025 |
| hotspot3d | L4 | ✓ PASS | 0.888× | wall_time | 9310 |
| lud | L1 | ✓ PASS | 0.287× | wall_time | 14035 |
| lud | L2 | ✓ PASS | 0.298× | wall_time | 17016 |
| lud | L3 | ✗ RUN_FAIL | — | None | 21796 |
| lud | L4 | ✓ PASS | 0.243× | wall_time | 15088 |
| mixbench | L1 | ✗ RUN_FAIL | — | None | 13771 |
| mixbench | L2 | ✗ RUN_FAIL | — | None | 13300 |
| mixbench | L3 | ✓ PASS | 8.006× | wall_time | 14135 |
| mixbench | L4 | ✓ PASS | 6.959× | wall_time | 13342 |
| nw | L1 | ✓ PASS | 0.327× | wall_time | 16485 |
| nw | L2 | ✓ PASS | 0.366× | wall_time | 18813 |
| nw | L3 | ✓ PASS | 0.333× | wall_time | 19289 |
| nw | L4 | ✓ PASS | 0.061× | wall_time | 21509 |
| pathfinder | L1 | ✓ PASS | — | wall_time | 7739 |
| pathfinder | L2 | ✓ PASS | — | wall_time | 5378 |
| pathfinder | L3 | ✓ PASS | — | wall_time | 14164 |
| pathfinder | L4 | ✓ PASS | — | wall_time | 5270 |
| streamcluster | L1 | ✗ RUN_FAIL | — | None | 29865 |
| streamcluster | L2 | ✗ RUN_FAIL | — | None | 30727 |
| streamcluster | L3 | ✗ RUN_FAIL | — | None | 30243 |
| streamcluster | L4 | ✗ RUN_FAIL | — | None | 31683 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 31360 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 34122 |
| xsbench | L3 | ✗ RUN_FAIL | — | None | 34112 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 31433 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| backprop | L1 | ✗ VERIFY_FAIL |
| backprop | L2 | ✓ PASS |
| backprop | L3 | ✗ VERIFY_FAIL |
| backprop | L4 | ✓ PASS |
| bfs | L1 | ✓ PASS |
| bfs | L2 | ✓ PASS |
| bfs | L3 | ✗ RUN_FAIL |
| bfs | L4 | ✗ RUN_FAIL |
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
| lud | L3 | ✗ RUN_FAIL |
| lud | L4 | ✓ PASS |
| mixbench | L1 | ✗ RUN_FAIL |
| mixbench | L2 | ✗ RUN_FAIL |
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
| streamcluster | L1 | ✗ RUN_FAIL |
| streamcluster | L2 | ✗ RUN_FAIL |
| streamcluster | L3 | ✗ RUN_FAIL |
| streamcluster | L4 | ✗ RUN_FAIL |
| xsbench | L1 | ✗ RUN_FAIL |
| xsbench | L2 | ✗ RUN_FAIL |
| xsbench | L3 | ✗ RUN_FAIL |
| xsbench | L4 | ✗ RUN_FAIL |
