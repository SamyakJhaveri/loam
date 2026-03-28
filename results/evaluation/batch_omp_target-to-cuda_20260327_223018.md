# Eval Batch: omp_target-to-cuda — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 0.996× | wall_time | 73097 |
| xsbench | L1 | ✓ PASS | 0.975× | wall_time | 74209 |
| xsbench | L2 | ✓ PASS | 0.963× | wall_time | 73692 |
| xsbench | L3 | ✓ PASS | 0.971× | wall_time | 73361 |
| xsbench | L4 | ✓ PASS | 0.965× | wall_time | 74312 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
