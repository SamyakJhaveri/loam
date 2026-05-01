# Eval Batch: omp-to-opencl — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 56

## azure-gpt-5.3-codex
**50/56 PASS (89%)** | FAILURES=6 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| bfs | L1 | ✓ PASS | 0.812× | wall_time | 12299 |
| bfs | L2 | ✓ PASS | 0.815× | wall_time | 12372 |
| bfs | L3 | ✓ PASS | 0.812× | wall_time | 12725 |
| bfs | L4 | ✓ PASS | 0.834× | wall_time | 12348 |
| bptree | L1 | ✓ PASS | 0.652× | wall_time | 24414 |
| bptree | L2 | ✓ PASS | 0.656× | wall_time | 23589 |
| bptree | L3 | ✗ RUN_FAIL | — | None | 23992 |
| bptree | L4 | ✓ PASS | 0.663× | wall_time | 23123 |
| hotspot | L1 | ✓ PASS | 0.548× | wall_time | 11558 |
| hotspot | L2 | ✓ PASS | 0.550× | wall_time | 11003 |
| hotspot | L3 | ✓ PASS | 0.543× | wall_time | 9987 |
| hotspot | L4 | ✓ PASS | 0.560× | wall_time | 10275 |
| hotspot3d | L1 | ✓ PASS | 0.877× | wall_time | 7494 |
| hotspot3d | L2 | ✓ PASS | 0.886× | wall_time | 7377 |
| hotspot3d | L3 | ✓ PASS | 0.887× | wall_time | 7285 |
| hotspot3d | L4 | ✓ PASS | 0.886× | wall_time | 11214 |
| lavamd | L1 | ✓ PASS | 0.005× | wall_time | 11150 |
| lavamd | L2 | ✗ RUN_FAIL | — | None | 10371 |
| lavamd | L3 | ✓ PASS | 0.005× | wall_time | 10683 |
| lavamd | L4 | ✓ PASS | 0.005× | wall_time | 11092 |
| lud | L1 | ✓ PASS | 0.253× | wall_time | 14445 |
| lud | L2 | ✓ PASS | 0.281× | wall_time | 14414 |
| lud | L3 | ✓ PASS | 0.278× | wall_time | 15638 |
| lud | L4 | ✓ PASS | 0.271× | wall_time | 14289 |
| mixbench | L1 | ✓ PASS | 8.104× | wall_time | 12722 |
| mixbench | L2 | ✓ PASS | 7.398× | wall_time | 12361 |
| mixbench | L3 | ✓ PASS | 9.228× | wall_time | 12128 |
| mixbench | L4 | ✓ PASS | 9.194× | wall_time | 12491 |
| myocyte | L1 | ✓ PASS | 0.002× | wall_time | 45375 |
| myocyte | L2 | ✓ PASS | 0.002× | wall_time | 45061 |
| myocyte | L3 | ✓ PASS | 0.002× | wall_time | 43073 |
| myocyte | L4 | ✓ PASS | 0.002× | wall_time | 44314 |
| nw | L1 | ✓ PASS | 0.367× | wall_time | 13811 |
| nw | L2 | ✓ PASS | 0.318× | wall_time | 14168 |
| nw | L3 | ✓ PASS | 0.324× | wall_time | 14218 |
| nw | L4 | ✓ PASS | 0.319× | wall_time | 14244 |
| particlefilter | L1 | ✓ PASS | 0.271× | wall_time | 19771 |
| particlefilter | L2 | ✓ PASS | 0.280× | wall_time | 20613 |
| particlefilter | L3 | ✗ VERIFY_FAIL | 0.378× | wall_time | 19175 |
| particlefilter | L4 | ✗ VERIFY_FAIL | 0.380× | wall_time | 18923 |
| pathfinder | L1 | ✓ PASS | — | wall_time | 5573 |
| pathfinder | L2 | ✓ PASS | — | wall_time | 5805 |
| pathfinder | L3 | ✓ PASS | — | wall_time | 6364 |
| pathfinder | L4 | ✓ PASS | — | wall_time | 6155 |
| rsbench | L1 | ✓ PASS | 0.873× | wall_time | 29644 |
| rsbench | L2 | ✓ PASS | 0.883× | wall_time | 30207 |
| rsbench | L3 | ✓ PASS | 0.883× | wall_time | 29666 |
| rsbench | L4 | ✓ PASS | 0.929× | wall_time | 30320 |
| srad | L1 | ✗ RUN_FAIL | — | None | 13976 |
| srad | L2 | ✓ PASS | 0.348× | wall_time | 13565 |
| srad | L3 | ✓ PASS | 0.378× | wall_time | 13932 |
| srad | L4 | ✓ PASS | 0.370× | wall_time | 14251 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 29397 |
| xsbench | L2 | ✓ PASS | 1.007× | wall_time | 29368 |
| xsbench | L3 | ✓ PASS | 1.009× | wall_time | 29942 |
| xsbench | L4 | ✓ PASS | 0.993× | wall_time | 29262 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.3-codex |
|--------|-------|---|
| bfs | L1 | ✓ PASS |
| bfs | L2 | ✓ PASS |
| bfs | L3 | ✓ PASS |
| bfs | L4 | ✓ PASS |
| bptree | L1 | ✓ PASS |
| bptree | L2 | ✓ PASS |
| bptree | L3 | ✗ RUN_FAIL |
| bptree | L4 | ✓ PASS |
| hotspot | L1 | ✓ PASS |
| hotspot | L2 | ✓ PASS |
| hotspot | L3 | ✓ PASS |
| hotspot | L4 | ✓ PASS |
| hotspot3d | L1 | ✓ PASS |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✓ PASS |
| lavamd | L1 | ✓ PASS |
| lavamd | L2 | ✗ RUN_FAIL |
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
| myocyte | L1 | ✓ PASS |
| myocyte | L2 | ✓ PASS |
| myocyte | L3 | ✓ PASS |
| myocyte | L4 | ✓ PASS |
| nw | L1 | ✓ PASS |
| nw | L2 | ✓ PASS |
| nw | L3 | ✓ PASS |
| nw | L4 | ✓ PASS |
| particlefilter | L1 | ✓ PASS |
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
| srad | L1 | ✗ RUN_FAIL |
| srad | L2 | ✓ PASS |
| srad | L3 | ✓ PASS |
| srad | L4 | ✓ PASS |
| xsbench | L1 | ✗ RUN_FAIL |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
