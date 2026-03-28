# Eval Batch: omp-to-omp_target — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## claude-sonnet-4-6
**4/5 PASS (80%)** | FAILURES=1 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.221× | wall_time | 42610 |
| xsbench | L1 | ✓ PASS | 1.226× | wall_time | 42609 |
| xsbench | L2 | ✓ PASS | 1.168× | wall_time | 42614 |
| xsbench | L3 | ✓ PASS | 1.210× | wall_time | 42622 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 101760 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✗ RUN_FAIL |
