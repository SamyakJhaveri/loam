# Eval Batch: cuda-to-opencl — 2026-03-31
**Date:** 2026-03-31  |  **Tasks:** 60

## together-qwen-3.5-397b-a17b
**2/20 PASS (10%)** | FAILURES=18 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| backprop | ✗ VERIFY_FAIL | 0.006× | wall_time | 16807 |
| bfs | ✗ RUN_FAIL | — | None | 14520 |
| bptree | ✗ RUN_FAIL | — | None | 13412 |
| cfd | ✗ VERIFY_FAIL | — | wall_time | 37346 |
| dwt2d | ✗ RUN_FAIL | — | None | 37813 |
| gaussian | ✗ RUN_FAIL | — | None | 18581 |
| heartwall | ✗ RUN_FAIL | — | None | 44221 |
| hotspot | ✗ RUN_FAIL | — | None | 8946 |
| hotspot3d | ✓ PASS | 0.909× | wall_time | 8171 |
| hybridsort | ✗ RUN_FAIL | — | None | 35183 |
| kmeans | ✗ VERIFY_FAIL | 2.961× | wall_time | 27295 |
| lavamd | ✗ RUN_FAIL | — | None | 11877 |
| lud | ✗ RUN_FAIL | — | None | 14395 |
| myocyte | ✗ RUN_FAIL | — | None | 102567 |
| nn | ✗ RUN_FAIL | — | None | 15388 |
| nw | ✓ PASS | 0.316× | wall_time | 14143 |
| particlefilter | ✗ EXTRACTION_FAIL | — | None | 26061 |
| pathfinder | ✗ RUN_FAIL | — | None | 5807 |
| srad | ✗ RUN_FAIL | — | None | 22678 |
| streamcluster | ✗ RUN_FAIL | — | None | 21827 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✗ VERIFY_FAIL |
| bfs | ✗ RUN_FAIL |
| bptree | ✗ RUN_FAIL |
| cfd | ✗ VERIFY_FAIL |
| dwt2d | ✗ RUN_FAIL |
| gaussian | ✗ RUN_FAIL |
| heartwall | ✗ RUN_FAIL |
| hotspot | ✗ RUN_FAIL |
| hotspot3d | ✓ PASS |
| hybridsort | ✗ RUN_FAIL |
| kmeans | ✗ VERIFY_FAIL |
| lavamd | ✗ RUN_FAIL |
| lud | ✗ RUN_FAIL |
| myocyte | ✗ RUN_FAIL |
| nn | ✗ RUN_FAIL |
| nw | ✓ PASS |
| particlefilter | ✗ EXTRACTION_FAIL |
| pathfinder | ✗ RUN_FAIL |
| srad | ✗ RUN_FAIL |
| streamcluster | ✗ RUN_FAIL |
