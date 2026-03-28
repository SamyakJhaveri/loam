# Eval Batch: omp-to-opencl — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.026× | wall_time | 45615 |
| xsbench | L1 | ✓ PASS | 0.984× | wall_time | 45599 |
| xsbench | L2 | ✓ PASS | 1.033× | wall_time | 45601 |
| xsbench | L3 | ✓ PASS | 1.038× | wall_time | 45598 |
| xsbench | L4 | ✓ PASS | 1.038× | wall_time | 45659 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
