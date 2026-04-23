# Eval Batch: cuda-to-opencl — 2026-04-22
**Date:** 2026-04-22  |  **Tasks:** 12

## together-qwen-3.5-397b-a17b
**1/12 PASS (8%)** | FAILURES=11 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| bfs | L1 | ✗ RUN_FAIL | — | None | 17172 |
| bfs | L2 | ✗ RUN_FAIL | — | None | 15347 |
| bfs | L3 | ✗ RUN_FAIL | — | None | 15861 |
| bfs | L4 | ✗ RUN_FAIL | — | None | 18897 |
| hotspot | L1 | ✗ RUN_FAIL | — | None | 10804 |
| hotspot | L2 | ✗ RUN_FAIL | — | None | 13252 |
| hotspot | L3 | ✗ RUN_FAIL | — | None | 11944 |
| hotspot | L4 | ✗ RUN_FAIL | — | None | 21269 |
| hotspot3d | L1 | ✗ RUN_FAIL | — | None | 10486 |
| hotspot3d | L2 | ✓ PASS | 0.893× | wall_time | 10769 |
| hotspot3d | L3 | ✗ RUN_FAIL | — | None | 9425 |
| hotspot3d | L4 | ✗ RUN_FAIL | — | None | 10098 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| bfs | L1 | ✗ RUN_FAIL |
| bfs | L2 | ✗ RUN_FAIL |
| bfs | L3 | ✗ RUN_FAIL |
| bfs | L4 | ✗ RUN_FAIL |
| hotspot | L1 | ✗ RUN_FAIL |
| hotspot | L2 | ✗ RUN_FAIL |
| hotspot | L3 | ✗ RUN_FAIL |
| hotspot | L4 | ✗ RUN_FAIL |
| hotspot3d | L1 | ✗ RUN_FAIL |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✗ RUN_FAIL |
| hotspot3d | L4 | ✗ RUN_FAIL |
