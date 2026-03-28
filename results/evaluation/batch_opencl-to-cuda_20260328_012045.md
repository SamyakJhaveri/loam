# Eval Batch: opencl-to-cuda — 2026-03-28
**Date:** 2026-03-28  |  **Tasks:** 5

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.009× | wall_time | 43852 |
| xsbench | L1 | ✓ PASS | 1.004× | wall_time | 43955 |
| xsbench | L2 | ✓ PASS | 1.002× | wall_time | 92122 |
| xsbench | L3 | ✓ PASS | 0.887× | wall_time | 44010 |
| xsbench | L4 | ✓ PASS | 0.928× | wall_time | 44034 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
