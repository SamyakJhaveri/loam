# Eval Batch: cuda-to-opencl — 2026-04-03
**Date:** 2026-04-03  |  **Tasks:** 5

## together-qwen-3.5-397b-a17b
**1/5 PASS (20%)** | FAILURES=4 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| mixbench | L0 | ✗ RUN_FAIL | — | None | 40880 |
| mixbench | L1 | ✓ PASS | 6.529× | wall_time | 43599 |
| mixbench | L2 | ✗ RUN_FAIL | — | None | 41189 |
| mixbench | L3 | ✗ RUN_FAIL | — | None | 45682 |
| mixbench | L4 | ✗ RUN_FAIL | — | None | 42579 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| mixbench | L0 | ✗ RUN_FAIL |
| mixbench | L1 | ✓ PASS |
| mixbench | L2 | ✗ RUN_FAIL |
| mixbench | L3 | ✗ RUN_FAIL |
| mixbench | L4 | ✗ RUN_FAIL |
