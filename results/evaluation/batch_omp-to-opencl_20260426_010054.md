# Eval Batch: omp-to-opencl — 2026-04-26
**Date:** 2026-04-26  |  **Tasks:** 42

## azure-gpt-5.4
**11/14 PASS (78%)** | FAILURES=3 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| bfs | ✓ PASS | 0.838× | wall_time | 12588 |
| bptree | ✓ PASS | 0.636× | wall_time | 24482 |
| cfd | ✗ VERIFY_FAIL | — | wall_time | 26874 |
| heartwall | ✗ RUN_FAIL | — | None | 46989 |
| hotspot | ✓ PASS | 0.554× | wall_time | 15573 |
| hotspot3d | ✓ PASS | 0.882× | wall_time | 12246 |
| lavamd | ✓ PASS | 0.005× | wall_time | 11435 |
| lud | ✓ PASS | 0.280× | wall_time | 16415 |
| myocyte | ✓ PASS | 0.002× | wall_time | 45767 |
| nw | ✓ PASS | 0.356× | wall_time | 14441 |
| particlefilter | ✓ PASS | 0.242× | wall_time | 25298 |
| pathfinder | ✓ PASS | — | wall_time | 10629 |
| srad | ✓ PASS | 0.392× | wall_time | 15504 |
| streamcluster | ✗ RUN_FAIL | — | None | 27791 |

## Cross-Model Summary

| Kernel | azure-gpt-5.4 |
|--------|---|
| bfs | ✓ PASS |
| bptree | ✓ PASS |
| cfd | ✗ VERIFY_FAIL |
| heartwall | ✗ RUN_FAIL |
| hotspot | ✓ PASS |
| hotspot3d | ✓ PASS |
| lavamd | ✓ PASS |
| lud | ✓ PASS |
| myocyte | ✓ PASS |
| nw | ✓ PASS |
| particlefilter | ✓ PASS |
| pathfinder | ✓ PASS |
| srad | ✓ PASS |
| streamcluster | ✗ RUN_FAIL |
