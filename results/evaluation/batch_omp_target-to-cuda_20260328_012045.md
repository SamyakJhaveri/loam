# Eval Batch: omp_target-to-cuda — 2026-03-28
**Date:** 2026-03-28  |  **Tasks:** 5

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 0.881× | wall_time | 34882 |
| xsbench | L1 | ✓ PASS | 0.924× | wall_time | 34516 |
| xsbench | L2 | ✓ PASS | 0.917× | wall_time | 34548 |
| xsbench | L3 | ✓ PASS | 0.919× | wall_time | 35241 |
| xsbench | L4 | ✓ PASS | 1.013× | wall_time | 73066 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 |
|--------|-------|---|
| xsbench | L0 | ✓ PASS |
| xsbench | L1 | ✓ PASS |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✓ PASS |
| xsbench | L4 | ✓ PASS |
