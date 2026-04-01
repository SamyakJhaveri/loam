# Eval Batch: omp-to-opencl — 2026-03-31
**Date:** 2026-03-31  |  **Tasks:** 51

## together-qwen-3.5-397b-a17b
**2/17 PASS (11%)** | FAILURES=15 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| backprop | ✓ PASS | 0.005× | wall_time | 14739 |
| bfs | ✗ RUN_FAIL | — | None | 13120 |
| bptree | ✓ PASS | 0.655× | wall_time | 24362 |
| cfd | ✗ VERIFY_FAIL | — | wall_time | 25849 |
| heartwall | ✗ RUN_FAIL | — | None | 36383 |
| hotspot | ✗ RUN_FAIL | — | None | 9012 |
| hotspot3d | ✗ RUN_FAIL | — | None | 7460 |
| kmeans | ✗ VERIFY_FAIL | 2.832× | wall_time | 41916 |
| lavamd | ✗ RUN_FAIL | — | None | 10690 |
| lud | ✗ RUN_FAIL | — | None | 18397 |
| myocyte | ✗ EXTRACTION_FAIL | — | None | 80466 |
| nn | ✗ RUN_FAIL | — | None | 11918 |
| nw | ✗ RUN_FAIL | — | None | 13435 |
| particlefilter | ✗ VERIFY_FAIL | 0.429× | wall_time | 17922 |
| pathfinder | ✗ RUN_FAIL | — | None | 4747 |
| srad | ✗ RUN_FAIL | — | None | 12974 |
| streamcluster | ✗ RUN_FAIL | — | None | 28881 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✓ PASS |
| bfs | ✗ RUN_FAIL |
| bptree | ✓ PASS |
| cfd | ✗ VERIFY_FAIL |
| heartwall | ✗ RUN_FAIL |
| hotspot | ✗ RUN_FAIL |
| hotspot3d | ✗ RUN_FAIL |
| kmeans | ✗ VERIFY_FAIL |
| lavamd | ✗ RUN_FAIL |
| lud | ✗ RUN_FAIL |
| myocyte | ✗ EXTRACTION_FAIL |
| nn | ✗ RUN_FAIL |
| nw | ✗ RUN_FAIL |
| particlefilter | ✗ VERIFY_FAIL |
| pathfinder | ✗ RUN_FAIL |
| srad | ✗ RUN_FAIL |
| streamcluster | ✗ RUN_FAIL |
