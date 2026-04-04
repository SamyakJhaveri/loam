# Eval Batch: omp-to-opencl — 2026-04-03
**Date:** 2026-04-03  |  **Tasks:** 5

## together-qwen-3.5-397b-a17b
**3/5 PASS (60%)** | FAILURES=2 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| mixbench | L0 | ✓ PASS | 4.677× | wall_time | 12660 |
| mixbench | L1 | ✓ PASS | 7.989× | wall_time | 11934 |
| mixbench | L2 | ✓ PASS | 6.867× | wall_time | 44189 |
| mixbench | L3 | ✗ RUN_FAIL | — | None | 66577 |
| mixbench | L4 | ✗ RUN_FAIL | — | None | 50368 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| mixbench | L0 | ✓ PASS |
| mixbench | L1 | ✓ PASS |
| mixbench | L2 | ✓ PASS |
| mixbench | L3 | ✗ RUN_FAIL |
| mixbench | L4 | ✗ RUN_FAIL |
