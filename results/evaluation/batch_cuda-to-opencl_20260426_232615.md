# Eval Batch: cuda-to-opencl — 2026-04-26
**Date:** 2026-04-26  |  **Tasks:** 52

## azure-gpt-5.4
**48/52 PASS (92%)** | FAILURES=4 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| bfs | L1 | ✓ PASS | 0.821× | wall_time | 13870 |
| bfs | L2 | ✓ PASS | 0.826× | wall_time | 14067 |
| bfs | L3 | ✓ PASS | 0.810× | wall_time | 13805 |
| bfs | L4 | ✓ PASS | 0.819× | wall_time | 13834 |
| bptree | L1 | ✓ PASS | 0.697× | wall_time | 13678 |
| bptree | L2 | ✓ PASS | 0.676× | wall_time | 13989 |
| bptree | L3 | ✓ PASS | 0.656× | wall_time | 14735 |
| bptree | L4 | ✓ PASS | 0.680× | wall_time | 14106 |
| dwt2d | L1 | ✓ PASS | 0.298× | wall_time | 40132 |
| dwt2d | L2 | ✓ PASS | 0.249× | wall_time | 42776 |
| dwt2d | L3 | ✓ PASS | 0.108× | wall_time | 40026 |
| dwt2d | L4 | ✓ PASS | 0.114× | wall_time | 40243 |
| hotspot | L1 | ✓ PASS | 0.574× | wall_time | 8866 |
| hotspot | L2 | ✓ PASS | 0.596× | wall_time | 8794 |
| hotspot | L3 | ✓ PASS | 0.566× | wall_time | 9293 |
| hotspot | L4 | ✓ PASS | 0.566× | wall_time | 9887 |
| hotspot3d | L1 | ✓ PASS | 0.890× | wall_time | 8329 |
| hotspot3d | L2 | ✓ PASS | 0.891× | wall_time | 8240 |
| hotspot3d | L3 | ✓ PASS | 0.884× | wall_time | 10461 |
| hotspot3d | L4 | ✓ PASS | 0.893× | wall_time | 8008 |
| lud | L1 | ✓ PASS | 0.285× | wall_time | 14714 |
| lud | L2 | ✓ PASS | 0.288× | wall_time | 13728 |
| lud | L3 | ✓ PASS | 0.286× | wall_time | 14847 |
| lud | L4 | ✓ PASS | 0.283× | wall_time | 15117 |
| mixbench | L1 | ✓ PASS | 6.583× | wall_time | 15277 |
| mixbench | L2 | ✓ PASS | 6.628× | wall_time | 15876 |
| mixbench | L3 | ✗ RUN_FAIL | — | None | 16172 |
| mixbench | L4 | ✓ PASS | 7.044× | wall_time | 15011 |
| nw | L1 | ✓ PASS | 0.366× | wall_time | 14214 |
| nw | L2 | ✓ PASS | 0.363× | wall_time | 14100 |
| nw | L3 | ✓ PASS | 0.366× | wall_time | 14328 |
| nw | L4 | ✓ PASS | 0.338× | wall_time | 14632 |
| particlefilter | L1 | ✗ VERIFY_FAIL | 0.448× | wall_time | 30203 |
| particlefilter | L2 | ✓ PASS | 0.319× | wall_time | 29865 |
| particlefilter | L3 | ✗ VERIFY_FAIL | 0.451× | wall_time | 29303 |
| particlefilter | L4 | ✗ VERIFY_FAIL | 0.459× | wall_time | 30779 |
| pathfinder | L1 | ✓ PASS | — | wall_time | 6213 |
| pathfinder | L2 | ✓ PASS | — | wall_time | 6424 |
| pathfinder | L3 | ✓ PASS | — | wall_time | 6295 |
| pathfinder | L4 | ✓ PASS | — | wall_time | 7968 |
| rsbench | L1 | ✓ PASS | 0.934× | wall_time | 30269 |
| rsbench | L2 | ✓ PASS | 0.928× | wall_time | 31271 |
| rsbench | L3 | ✓ PASS | 0.809× | wall_time | 33586 |
| rsbench | L4 | ✓ PASS | 0.887× | wall_time | 32391 |
| srad | L1 | ✓ PASS | 0.354× | wall_time | 16915 |
| srad | L2 | ✓ PASS | 0.343× | wall_time | 19161 |
| srad | L3 | ✓ PASS | 0.339× | wall_time | 19245 |
| srad | L4 | ✓ PASS | 0.341× | wall_time | 18266 |
| xsbench | L1 | ✓ PASS | 0.984× | wall_time | 32953 |
| xsbench | L2 | ✓ PASS | 1.048× | wall_time | 32989 |
| xsbench | L3 | ✓ PASS | 1.053× | wall_time | 32983 |
| xsbench | L4 | ✓ PASS | 0.984× | wall_time | 32462 |

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
| dwt2d | L1 | ✓ PASS |
| dwt2d | L2 | ✓ PASS |
| dwt2d | L3 | ✓ PASS |
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
| mixbench | L3 | ✗ RUN_FAIL |
| mixbench | L4 | ✓ PASS |
| nw | L1 | ✓ PASS |
| nw | L2 | ✓ PASS |
| nw | L3 | ✓ PASS |
| nw | L4 | ✓ PASS |
| particlefilter | L1 | ✗ VERIFY_FAIL |
| particlefilter | L2 | ✓ PASS |
| particlefilter | L3 | ✗ VERIFY_FAIL |
| particlefilter | L4 | ✗ VERIFY_FAIL |
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
