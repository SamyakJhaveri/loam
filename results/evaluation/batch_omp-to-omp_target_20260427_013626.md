# Eval Batch: omp-to-omp_target — 2026-04-27
**Date:** 2026-04-27  |  **Tasks:** 12

## azure-gpt-5.4
**10/12 PASS (83%)** | FAILURES=2 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| floydwarshall | L1 | ✓ PASS | — | wall_time | 4541 |
| floydwarshall | L2 | ✓ PASS | — | wall_time | 4855 |
| floydwarshall | L3 | ✗ RUN_FAIL | — | None | 4158 |
| floydwarshall | L4 | ✓ PASS | — | wall_time | 5382 |
| heat2d | L1 | ✓ PASS | — | wall_time | 5463 |
| heat2d | L2 | ✓ PASS | — | wall_time | 5591 |
| heat2d | L3 | ✓ PASS | — | wall_time | 7117 |
| heat2d | L4 | ✗ RUN_FAIL | — | None | 5443 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 5688 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 5812 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 8824 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 6169 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.4 |
|--------|-------|---|
| floydwarshall | L1 | ✓ PASS |
| floydwarshall | L2 | ✓ PASS |
| floydwarshall | L3 | ✗ RUN_FAIL |
| floydwarshall | L4 | ✓ PASS |
| heat2d | L1 | ✓ PASS |
| heat2d | L2 | ✓ PASS |
| heat2d | L3 | ✓ PASS |
| heat2d | L4 | ✗ RUN_FAIL |
| iso2dfd | L1 | ✓ PASS |
| iso2dfd | L2 | ✓ PASS |
| iso2dfd | L3 | ✓ PASS |
| iso2dfd | L4 | ✓ PASS |
