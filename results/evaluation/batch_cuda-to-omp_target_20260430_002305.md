# Eval Batch: cuda-to-omp_target — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 24

## azure-gpt-5.3-codex
**8/8 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| convolution1d | ✓ PASS | — | wall_time | 5465 |
| floydwarshall | ✓ PASS | — | wall_time | 3961 |
| heat2d | ✓ PASS | — | wall_time | 3790 |
| iso2dfd | ✓ PASS | — | wall_time | 6660 |
| jacobi | ✓ PASS | — | wall_time | 3759 |
| md | ✓ PASS | — | wall_time | 7683 |
| nqueen | ✓ PASS | — | wall_time | 4801 |
| page-rank | ✓ PASS | — | wall_time | 7010 |

## Cross-Model Summary

| Kernel | azure-gpt-5.3-codex |
|--------|---|
| convolution1d | ✓ PASS |
| floydwarshall | ✓ PASS |
| heat2d | ✓ PASS |
| iso2dfd | ✓ PASS |
| jacobi | ✓ PASS |
| md | ✓ PASS |
| nqueen | ✓ PASS |
| page-rank | ✓ PASS |
