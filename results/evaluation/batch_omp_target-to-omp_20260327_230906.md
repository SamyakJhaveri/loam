# Eval Batch: omp_target-to-omp — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## claude-sonnet-4-6
**3/5 PASS (60%)** | FAILURES=2 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ RUN_FAIL | — | None | 82328 |
| xsbench | L1 | ✓ PASS | 0.706× | wall_time | 83458 |
| xsbench | L2 | ✓ PASS | 0.711× | wall_time | 82838 |
| xsbench | L3 | ✗ RUN_FAIL | — | None | 84737 |
| xsbench | L4 | ✓ PASS | 0.705× | wall_time | 82139 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✗ RUN_FAIL |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✗ RUN_FAIL |
| xsbench | L4 | ✓ PASS |
