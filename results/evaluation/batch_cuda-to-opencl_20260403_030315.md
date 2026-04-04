# Eval Batch: cuda-to-opencl — 2026-04-03
**Date:** 2026-04-03  |  **Tasks:** 5

## together-qwen-3.5-397b-a17b
**0/5 PASS (0%)** | FAILURES=4 | ERROR=1 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| rsbench | L0 | ! ERROR | — | None | — |
| rsbench | L1 | ✗ RUN_FAIL | — | None | 114909 |
| rsbench | L2 | ✗ RUN_FAIL | — | None | 115563 |
| rsbench | L3 | ✗ RUN_FAIL | — | None | 173506 |
| rsbench | L4 | ✗ RUN_FAIL | — | None | 173657 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| rsbench | L0 | ! ERROR |
| rsbench | L1 | ✗ RUN_FAIL |
| rsbench | L2 | ✗ RUN_FAIL |
| rsbench | L3 | ✗ RUN_FAIL |
| rsbench | L4 | ✗ RUN_FAIL |
