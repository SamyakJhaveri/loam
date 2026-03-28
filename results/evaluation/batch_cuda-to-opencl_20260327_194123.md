# Eval Batch: cuda-to-opencl — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 0.969× | wall_time | 50304 |
| xsbench | L1 | ✓ PASS | 1.028× | wall_time | 50296 |
| xsbench | L2 | ✓ PASS | 1.021× | wall_time | 50296 |
| xsbench | L3 | ✓ PASS | 1.021× | wall_time | 50307 |
| xsbench | L4 | ✓ PASS | 0.976× | wall_time | 50498 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
