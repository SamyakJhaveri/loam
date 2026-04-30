# Eval Batch: omp-to-opencl — 2026-04-29
**Date:** 2026-04-29  |  **Tasks:** 42

## azure-gpt-5.3-codex
**11/14 PASS (78%)** | FAILURES=3 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| bfs | ✓ PASS | 0.823× | wall_time | 12450 |
| bptree | ✓ PASS | 0.673× | wall_time | 24441 |
| cfd | ✗ VERIFY_FAIL | — | wall_time | 25673 |
| heartwall | ✗ RUN_FAIL | — | None | 38640 |
| hotspot | ✓ PASS | 0.548× | wall_time | 11124 |
| hotspot3d | ✓ PASS | 0.896× | wall_time | 7300 |
| lavamd | ✓ PASS | 0.005× | wall_time | 10817 |
| lud | ✓ PASS | 0.288× | wall_time | 14799 |
| myocyte | ✓ PASS | 0.002× | wall_time | 45397 |
| nw | ✓ PASS | 0.318× | wall_time | 13928 |
| particlefilter | ✓ PASS | 0.276× | wall_time | 21434 |
| pathfinder | ✓ PASS | — | wall_time | 6436 |
| srad | ✓ PASS | 0.363× | wall_time | 13389 |
| streamcluster | ✗ RUN_FAIL | — | None | 29310 |

## Cross-Model Summary

| Kernel | azure-gpt-5.3-codex |
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
