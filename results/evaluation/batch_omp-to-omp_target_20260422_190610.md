# Eval Batch: omp-to-omp_target — 2026-04-22
**Date:** 2026-04-22  |  **Tasks:** 12

## together-qwen-3.5-397b-a17b
**7/12 PASS (58%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| floydwarshall | L1 | ✓ PASS | — | wall_time | 7387 |
| floydwarshall | L2 | ✓ PASS | — | wall_time | 5421 |
| floydwarshall | L3 | ✗ BUILD_FAIL | — | None | 5805 |
| floydwarshall | L4 | ✗ BUILD_FAIL | — | None | 4148 |
| heat2d | L1 | ✓ PASS | — | wall_time | 7241 |
| heat2d | L2 | ✗ BUILD_FAIL | — | None | 4427 |
| heat2d | L3 | ✗ VERIFY_FAIL | — | wall_time | 5801 |
| heat2d | L4 | ✗ RUN_FAIL | — | None | 4404 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 8471 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 6071 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 8587 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 6668 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| floydwarshall | L1 | ✓ PASS |
| floydwarshall | L2 | ✓ PASS |
| floydwarshall | L3 | ✗ BUILD_FAIL |
| floydwarshall | L4 | ✗ BUILD_FAIL |
| heat2d | L1 | ✓ PASS |
| heat2d | L2 | ✗ BUILD_FAIL |
| heat2d | L3 | ✗ VERIFY_FAIL |
| heat2d | L4 | ✗ RUN_FAIL |
| iso2dfd | L1 | ✓ PASS |
| iso2dfd | L2 | ✓ PASS |
| iso2dfd | L3 | ✓ PASS |
| iso2dfd | L4 | ✓ PASS |
