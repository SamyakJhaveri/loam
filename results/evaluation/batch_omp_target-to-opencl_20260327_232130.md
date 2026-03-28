# Eval Batch: omp_target-to-opencl — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## claude-sonnet-4-6
**4/5 PASS (80%)** | FAILURES=1 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.023× | wall_time | 38774 |
| xsbench | L1 | ✓ PASS | 1.021× | wall_time | 38870 |
| xsbench | L2 | ✓ PASS | 1.026× | wall_time | 38820 |
| xsbench | L3 | ✓ PASS | 1.030× | wall_time | 38857 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 81381 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✗ RUN_FAIL |
