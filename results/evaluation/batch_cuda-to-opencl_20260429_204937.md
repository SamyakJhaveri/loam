# Eval Batch: cuda-to-opencl — 2026-04-29
**Date:** 2026-04-29  |  **Tasks:** 48

## azure-gpt-5.3-codex
**9/16 PASS (56%)** | FAILURES=7 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| bfs | ✓ PASS | 0.829× | wall_time | 13554 |
| bptree | ✓ PASS | 0.691× | wall_time | 13343 |
| cfd | ✗ VERIFY_FAIL | — | wall_time | 36869 |
| dwt2d | ✓ PASS | 0.060× | wall_time | 36656 |
| gaussian | ✗ RUN_FAIL | — | None | 13106 |
| heartwall | ✗ RUN_FAIL | — | None | 45730 |
| hotspot | ✓ PASS | 0.596× | wall_time | 8952 |
| hotspot3d | ✓ PASS | 0.887× | wall_time | 8125 |
| lavamd | ✗ RUN_FAIL | — | None | 13040 |
| lud | ✓ PASS | 0.295× | wall_time | 14232 |
| myocyte | ✗ RUN_FAIL | — | None | 65106 |
| nw | ✓ PASS | 0.367× | wall_time | 14253 |
| particlefilter | ✗ VERIFY_FAIL | 0.468× | wall_time | 27163 |
| pathfinder | ✓ PASS | — | wall_time | 5843 |
| srad | ✓ PASS | 0.374× | wall_time | 15994 |
| streamcluster | ✗ RUN_FAIL | — | None | 21406 |

## Cross-Model Summary

| Kernel | azure-gpt-5.3-codex |
|--------|---|
| bfs | ✓ PASS |
| bptree | ✓ PASS |
| cfd | ✗ VERIFY_FAIL |
| dwt2d | ✓ PASS |
| gaussian | ✗ RUN_FAIL |
| heartwall | ✗ RUN_FAIL |
| hotspot | ✓ PASS |
| hotspot3d | ✓ PASS |
| lavamd | ✗ RUN_FAIL |
| lud | ✓ PASS |
| myocyte | ✗ RUN_FAIL |
| nw | ✓ PASS |
| particlefilter | ✗ VERIFY_FAIL |
| pathfinder | ✓ PASS |
| srad | ✓ PASS |
| streamcluster | ✗ RUN_FAIL |
