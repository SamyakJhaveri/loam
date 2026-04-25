# Eval Batch: cuda-to-opencl — 2026-04-23
**Date:** 2026-04-23  |  **Tasks:** 12

## together-qwen-3.5-397b-a17b
**4/12 PASS (33%)** | FAILURES=8 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| bfs | L1 | ✗ RUN_FAIL | — | None | 15473 |
| bfs | L2 | ✗ RUN_FAIL | — | None | 15300 |
| bfs | L3 | ✗ RUN_FAIL | — | None | 15233 |
| bfs | L4 | ✗ RUN_FAIL | — | None | 15400 |
| hotspot | L1 | ✗ RUN_FAIL | — | None | 10746 |
| hotspot | L2 | ✓ PASS | 0.578× | wall_time | 10514 |
| hotspot | L3 | ✓ PASS | 0.574× | wall_time | 9198 |
| hotspot | L4 | ✗ RUN_FAIL | — | None | 10358 |
| hotspot3d | L1 | ✗ RUN_FAIL | — | None | 9898 |
| hotspot3d | L2 | ✓ PASS | 0.888× | wall_time | 9798 |
| hotspot3d | L3 | ✗ RUN_FAIL | — | None | 9860 |
| hotspot3d | L4 | ✓ PASS | 0.874× | wall_time | 9758 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| bfs | L1 | ✗ RUN_FAIL |
| bfs | L2 | ✗ RUN_FAIL |
| bfs | L3 | ✗ RUN_FAIL |
| bfs | L4 | ✗ RUN_FAIL |
| hotspot | L1 | ✗ RUN_FAIL |
| hotspot | L2 | ✓ PASS |
| hotspot | L3 | ✓ PASS |
| hotspot | L4 | ✗ RUN_FAIL |
| hotspot3d | L1 | ✗ RUN_FAIL |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✗ RUN_FAIL |
| hotspot3d | L4 | ✓ PASS |
