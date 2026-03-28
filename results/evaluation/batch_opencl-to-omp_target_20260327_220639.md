# Eval Batch: opencl-to-omp_target — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.097× | wall_time | 92772 |
| xsbench | L1 | ✓ PASS | 1.130× | wall_time | 43346 |
| xsbench | L2 | ✓ PASS | 1.133× | wall_time | 43633 |
| xsbench | L3 | ✓ PASS | 1.128× | wall_time | 95290 |
| xsbench | L4 | ✓ PASS | 1.130× | wall_time | 42524 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
