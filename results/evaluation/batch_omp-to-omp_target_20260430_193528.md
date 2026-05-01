# Eval Batch: omp-to-omp_target — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 12

## azure-gpt-5.3-codex
**8/12 PASS (66%)** | FAILURES=4 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| floydwarshall | L1 | ✓ PASS | — | wall_time | 3789 |
| floydwarshall | L2 | ✓ PASS | — | wall_time | 3693 |
| floydwarshall | L3 | ✗ RUN_FAIL | — | None | 3677 |
| floydwarshall | L4 | ✗ VERIFY_FAIL | — | wall_time | 3834 |
| heat2d | L1 | ✓ PASS | — | wall_time | 3448 |
| heat2d | L2 | ✓ PASS | — | wall_time | 3459 |
| heat2d | L3 | ✗ VERIFY_FAIL | — | wall_time | 5158 |
| heat2d | L4 | ✗ RUN_FAIL | — | None | 4639 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 5382 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 5275 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 5303 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 5182 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.3-codex |
|--------|-------|---|
| floydwarshall | L1 | ✓ PASS |
| floydwarshall | L2 | ✓ PASS |
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
