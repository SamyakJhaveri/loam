# Eval Batch: cuda-to-omp_target — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.237× | wall_time | 105296 |
| xsbench | L1 | ✓ PASS | 1.245× | wall_time | 47275 |
| xsbench | L2 | ✓ PASS | 1.240× | wall_time | 47289 |
| xsbench | L3 | ✓ PASS | 1.081× | wall_time | 105651 |
| xsbench | L4 | ✓ PASS | 1.089× | wall_time | 47459 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
