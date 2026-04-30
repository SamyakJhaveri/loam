# Eval Batch: opencl-to-omp — 2026-04-29
**Date:** 2026-04-29  |  **Tasks:** 42

## azure-gpt-5.3-codex
**5/14 PASS (35%)** | FAILURES=9 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| bfs | ✓ PASS | 0.001× | wall_time | 15435 |
| bptree | ✗ BUILD_FAIL | — | None | 30761 |
| cfd | ✓ PASS | 0.909× | wall_time | 26678 |
| heartwall | ✗ BUILD_FAIL | — | None | 61681 |
| hotspot | ✗ VERIFY_FAIL | 0.758× | wall_time | 9368 |
| hotspot3d | ✓ PASS | 1.024× | wall_time | 12201 |
| lavamd | ✗ BUILD_FAIL | — | None | 12473 |
| lud | ✓ PASS | 1.000× | wall_time | 15448 |
| myocyte | ✗ BUILD_FAIL | — | None | 49161 |
| nw | ✗ RUN_FAIL | — | None | 15672 |
| particlefilter | ✗ BUILD_FAIL | — | None | 37337 |
| pathfinder | ✗ BUILD_FAIL | — | None | 10290 |
| srad | ✓ PASS | 0.353× | wall_time | 20704 |
| streamcluster | ✗ VERIFY_FAIL | 0.951× | wall_time | 31292 |

## Cross-Model Summary

| Kernel | azure-gpt-5.3-codex |
|--------|---|
| bfs | ✓ PASS |
| bptree | ✗ BUILD_FAIL |
| cfd | ✓ PASS |
| heartwall | ✗ BUILD_FAIL |
| hotspot | ✗ VERIFY_FAIL |
| hotspot3d | ✓ PASS |
| lavamd | ✗ BUILD_FAIL |
| lud | ✓ PASS |
| myocyte | ✗ BUILD_FAIL |
| nw | ✗ RUN_FAIL |
| particlefilter | ✗ BUILD_FAIL |
| pathfinder | ✗ BUILD_FAIL |
| srad | ✓ PASS |
| streamcluster | ✗ VERIFY_FAIL |
