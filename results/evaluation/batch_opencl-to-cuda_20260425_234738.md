# Eval Batch: opencl-to-cuda — 2026-04-25
**Date:** 2026-04-25  |  **Tasks:** 48

## azure-gpt-5.4
**2/16 PASS (12%)** | FAILURES=14 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| bfs | ✗ BUILD_FAIL | — | None | 22562 |
| bptree | ✗ BUILD_FAIL | — | None | 52240 |
| cfd | ✓ PASS | — | wall_time | 44254 |
| dwt2d | ✗ BUILD_FAIL | — | None | 39097 |
| gaussian | ✗ VERIFY_FAIL | 0.493× | wall_time | 26639 |
| heartwall | ✗ BUILD_FAIL | — | None | 65063 |
| hotspot | ✗ VERIFY_FAIL | 0.637× | wall_time | 13236 |
| hotspot3d | ✗ BUILD_FAIL | — | None | 16576 |
| lavamd | ✗ BUILD_FAIL | — | None | 17599 |
| lud | ✗ BUILD_FAIL | — | None | 21126 |
| myocyte | ✗ EXTRACTION_FAIL | — | None | 67575 |
| nw | ✗ BUILD_FAIL | — | None | 19793 |
| particlefilter | ✓ PASS | 0.633× | wall_time | 45435 |
| pathfinder | ✗ BUILD_FAIL | — | None | 13416 |
| srad | ✗ BUILD_FAIL | — | None | 27039 |
| streamcluster | ✗ BUILD_FAIL | — | None | 38122 |

## Cross-Model Summary

| Kernel | azure-gpt-5.4 |
|--------|---|
| bfs | ✗ BUILD_FAIL |
| bptree | ✗ BUILD_FAIL |
| cfd | ✓ PASS |
| dwt2d | ✗ BUILD_FAIL |
| gaussian | ✗ VERIFY_FAIL |
| heartwall | ✗ BUILD_FAIL |
| hotspot | ✗ VERIFY_FAIL |
| hotspot3d | ✗ BUILD_FAIL |
| lavamd | ✗ BUILD_FAIL |
| lud | ✗ BUILD_FAIL |
| myocyte | ✗ EXTRACTION_FAIL |
| nw | ✗ BUILD_FAIL |
| particlefilter | ✓ PASS |
| pathfinder | ✗ BUILD_FAIL |
| srad | ✗ BUILD_FAIL |
| streamcluster | ✗ BUILD_FAIL |
