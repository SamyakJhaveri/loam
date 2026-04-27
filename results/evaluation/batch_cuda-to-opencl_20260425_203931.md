# Eval Batch: cuda-to-opencl — 2026-04-25
**Date:** 2026-04-25  |  **Tasks:** 48

## azure-gpt-5.4
**9/16 PASS (56%)** | FAILURES=7 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| bfs | ✓ PASS | 0.811× | wall_time | 13856 |
| bptree | ✓ PASS | 0.682× | wall_time | 14350 |
| cfd | ✗ VERIFY_FAIL | — | wall_time | 36746 |
| dwt2d | ✓ PASS | 0.345× | wall_time | 40484 |
| gaussian | ✗ RUN_FAIL | — | None | 13690 |
| heartwall | ✗ RUN_FAIL | — | None | 48299 |
| hotspot | ✓ PASS | 0.587× | wall_time | 8752 |
| hotspot3d | ✓ PASS | 0.854× | wall_time | 8747 |
| lavamd | ✗ RUN_FAIL | — | None | 13152 |
| lud | ✓ PASS | 0.285× | wall_time | 15287 |
| myocyte | ✗ RUN_FAIL | — | None | 73352 |
| nw | ✓ PASS | 0.336× | wall_time | 14608 |
| particlefilter | ✗ VERIFY_FAIL | 0.442× | wall_time | 31425 |
| pathfinder | ✓ PASS | — | wall_time | 6685 |
| srad | ✓ PASS | 0.341× | wall_time | 19355 |
| streamcluster | ✗ RUN_FAIL | — | None | 22031 |

## Cross-Model Summary

| Kernel | azure-gpt-5.4 |
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
