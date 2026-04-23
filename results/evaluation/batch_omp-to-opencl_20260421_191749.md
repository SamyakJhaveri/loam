# Eval Batch: omp-to-opencl — 2026-04-21
**Date:** 2026-04-21  |  **Tasks:** 51

## together-qwen-3.5-397b-a17b
**6/17 PASS (35%)** | FAILURES=11 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| backprop | ✗ VERIFY_FAIL | 0.006× | wall_time | 15383 |
| bfs | ✓ PASS | 0.830× | wall_time | 14221 |
| bptree | ✗ RUN_FAIL | — | None | 24806 |
| cfd | ✗ VERIFY_FAIL | — | wall_time | 30708 |
| heartwall | ✗ RUN_FAIL | — | None | 37597 |
| hotspot | ✓ PASS | 0.564× | wall_time | 12401 |
| hotspot3d | ✓ PASS | 0.876× | wall_time | 8767 |
| kmeans | ✗ VERIFY_FAIL | 2.864× | wall_time | 49337 |
| lavamd | ✗ RUN_FAIL | — | None | 15337 |
| lud | ✓ PASS | 0.276× | wall_time | 18199 |
| myocyte | ✗ RUN_FAIL | — | None | 53472 |
| nn | ✗ RUN_FAIL | — | None | 11728 |
| nw | ✗ RUN_FAIL | — | None | 13907 |
| particlefilter | ✗ VERIFY_FAIL | 0.477× | wall_time | 18626 |
| pathfinder | ✓ PASS | — | wall_time | 6193 |
| srad | ✗ RUN_FAIL | — | None | 13559 |
| streamcluster | ✓ PASS | 0.198× | wall_time | 29777 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✗ VERIFY_FAIL |
| bfs | ✓ PASS |
| bptree | ✗ RUN_FAIL |
| cfd | ✗ VERIFY_FAIL |
| heartwall | ✗ RUN_FAIL |
| hotspot | ✓ PASS |
| hotspot3d | ✓ PASS |
| kmeans | ✗ VERIFY_FAIL |
| lavamd | ✗ RUN_FAIL |
| lud | ✓ PASS |
| myocyte | ✗ RUN_FAIL |
| nn | ✗ RUN_FAIL |
| nw | ✗ RUN_FAIL |
| particlefilter | ✗ VERIFY_FAIL |
| pathfinder | ✓ PASS |
| srad | ✗ RUN_FAIL |
| streamcluster | ✓ PASS |
