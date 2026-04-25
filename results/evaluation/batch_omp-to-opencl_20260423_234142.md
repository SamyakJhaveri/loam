# Eval Batch: omp-to-opencl — 2026-04-23
**Date:** 2026-04-23  |  **Tasks:** 40

## together-qwen-3.5-397b-a17b
**20/40 PASS (50%)** | FAILURES=20 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| backprop | L1 | ✓ PASS | 0.005× | wall_time | 17653 |
| backprop | L2 | ✓ PASS | 0.005× | wall_time | 15286 |
| backprop | L3 | ✓ PASS | 0.005× | wall_time | 15179 |
| backprop | L4 | ✗ VERIFY_FAIL | 0.006× | wall_time | 15556 |
| bfs | L1 | ✓ PASS | 0.808× | wall_time | 15861 |
| bfs | L2 | ✗ RUN_FAIL | — | None | 15176 |
| bfs | L3 | ✗ RUN_FAIL | — | None | 14024 |
| bfs | L4 | ✓ PASS | 0.807× | wall_time | 14877 |
| hotspot | L1 | ✓ PASS | 0.566× | wall_time | 20522 |
| hotspot | L2 | ✗ RUN_FAIL | — | None | 9751 |
| hotspot | L3 | ✗ RUN_FAIL | — | None | 11619 |
| hotspot | L4 | ✗ RUN_FAIL | — | None | 10185 |
| hotspot3d | L1 | ✓ PASS | 0.892× | wall_time | 9521 |
| hotspot3d | L2 | ✓ PASS | 0.874× | wall_time | 11052 |
| hotspot3d | L3 | ✓ PASS | 0.882× | wall_time | 9585 |
| hotspot3d | L4 | ✓ PASS | 0.891× | wall_time | 9675 |
| lud | L1 | ✓ PASS | 0.264× | wall_time | 14512 |
| lud | L2 | ✗ RUN_FAIL | — | None | 14188 |
| lud | L3 | ✓ PASS | 0.276× | wall_time | 15167 |
| lud | L4 | ✗ RUN_FAIL | — | None | 14806 |
| mixbench | L1 | ✓ PASS | 7.893× | wall_time | 12855 |
| mixbench | L2 | ✗ RUN_FAIL | — | None | 13331 |
| mixbench | L3 | ✗ RUN_FAIL | — | None | 12975 |
| mixbench | L4 | ✗ RUN_FAIL | — | None | 13618 |
| nw | L1 | ✓ PASS | 0.323× | wall_time | 19006 |
| nw | L2 | ✓ PASS | 0.330× | wall_time | 17831 |
| nw | L3 | ✓ PASS | 0.327× | wall_time | 13872 |
| nw | L4 | ✓ PASS | 0.317× | wall_time | 14657 |
| pathfinder | L1 | ✓ PASS | — | wall_time | 7799 |
| pathfinder | L2 | ✓ PASS | — | wall_time | 8574 |
| pathfinder | L3 | ✓ PASS | — | wall_time | 5298 |
| pathfinder | L4 | ✗ RUN_FAIL | — | None | 5590 |
| streamcluster | L1 | ✗ RUN_FAIL | — | None | 30023 |
| streamcluster | L2 | ✗ RUN_FAIL | — | None | 29975 |
| streamcluster | L3 | ✗ RUN_FAIL | — | None | 30709 |
| streamcluster | L4 | ✗ RUN_FAIL | — | None | 34182 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 31307 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 32553 |
| xsbench | L3 | ✗ RUN_FAIL | — | None | 36984 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 34095 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| backprop | L1 | ✓ PASS |
| backprop | L2 | ✓ PASS |
| backprop | L3 | ✓ PASS |
| backprop | L4 | ✗ VERIFY_FAIL |
| bfs | L1 | ✓ PASS |
| bfs | L2 | ✗ RUN_FAIL |
| bfs | L3 | ✗ RUN_FAIL |
| bfs | L4 | ✓ PASS |
| hotspot | L1 | ✓ PASS |
| hotspot | L2 | ✗ RUN_FAIL |
| hotspot | L3 | ✗ RUN_FAIL |
| hotspot | L4 | ✗ RUN_FAIL |
| hotspot3d | L1 | ✓ PASS |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✓ PASS |
| lud | L1 | ✓ PASS |
| lud | L2 | ✗ RUN_FAIL |
| lud | L3 | ✓ PASS |
| lud | L4 | ✗ RUN_FAIL |
| mixbench | L1 | ✓ PASS |
| mixbench | L2 | ✗ RUN_FAIL |
| mixbench | L3 | ✗ RUN_FAIL |
| mixbench | L4 | ✗ RUN_FAIL |
| nw | L1 | ✓ PASS |
| nw | L2 | ✓ PASS |
| nw | L3 | ✓ PASS |
| nw | L4 | ✓ PASS |
| pathfinder | L1 | ✓ PASS |
| pathfinder | L2 | ✓ PASS |
| pathfinder | L3 | ✓ PASS |
| pathfinder | L4 | ✗ RUN_FAIL |
| streamcluster | L1 | ✗ RUN_FAIL |
| streamcluster | L2 | ✗ RUN_FAIL |
| streamcluster | L3 | ✗ RUN_FAIL |
| streamcluster | L4 | ✗ RUN_FAIL |
| xsbench | L1 | ✗ RUN_FAIL |
| xsbench | L2 | ✗ RUN_FAIL |
| xsbench | L3 | ✗ RUN_FAIL |
| xsbench | L4 | ✗ RUN_FAIL |
