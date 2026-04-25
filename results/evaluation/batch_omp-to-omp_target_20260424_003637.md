# Eval Batch: omp-to-omp_target — 2026-04-24
**Date:** 2026-04-24  |  **Tasks:** 12

## together-qwen-3.5-397b-a17b
**7/12 PASS (58%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| floydwarshall | L1 | ✓ PASS | — | wall_time | 7217 |
| floydwarshall | L2 | ✗ VERIFY_FAIL | — | wall_time | 4378 |
| floydwarshall | L3 | ✗ RUN_FAIL | — | None | 6108 |
| floydwarshall | L4 | ✗ VERIFY_FAIL | — | wall_time | 5869 |
| heat2d | L1 | ✓ PASS | — | wall_time | 11579 |
| heat2d | L2 | ✓ PASS | — | wall_time | 4708 |
| heat2d | L3 | ✗ VERIFY_FAIL | — | wall_time | 11247 |
| heat2d | L4 | ✗ RUN_FAIL | — | None | 7057 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 5764 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 5948 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 5928 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 8993 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| floydwarshall | L1 | ✓ PASS |
| floydwarshall | L2 | ✗ VERIFY_FAIL |
| floydwarshall | L3 | ✗ RUN_FAIL |
| floydwarshall | L4 | ✗ VERIFY_FAIL |
| heat2d | L1 | ✓ PASS |
| heat2d | L2 | ✓ PASS |
| heat2d | L3 | ✗ VERIFY_FAIL |
| heat2d | L4 | ✗ RUN_FAIL |
| iso2dfd | L1 | ✓ PASS |
| iso2dfd | L2 | ✓ PASS |
| iso2dfd | L3 | ✓ PASS |
| iso2dfd | L4 | ✓ PASS |
