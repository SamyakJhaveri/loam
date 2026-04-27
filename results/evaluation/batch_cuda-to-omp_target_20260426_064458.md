# Eval Batch: cuda-to-omp_target — 2026-04-26
**Date:** 2026-04-26  |  **Tasks:** 24

## azure-gpt-5.4
**8/8 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| convolution1d | ✓ PASS | — | wall_time | 9115 |
| floydwarshall | ✓ PASS | — | wall_time | 6119 |
| heat2d | ✓ PASS | — | wall_time | 5862 |
| iso2dfd | ✓ PASS | — | wall_time | 7401 |
| jacobi | ✓ PASS | — | wall_time | 4724 |
| md | ✓ PASS | — | wall_time | 6536 |
| nqueen | ✓ PASS | — | wall_time | 7338 |
| page-rank | ✓ PASS | — | wall_time | 6343 |

## Cross-Model Summary

| Kernel | azure-gpt-5.4 |
|--------|---|
| convolution1d | ✓ PASS |
| floydwarshall | ✓ PASS |
| heat2d | ✓ PASS |
| iso2dfd | ✓ PASS |
| jacobi | ✓ PASS |
| md | ✓ PASS |
| nqueen | ✓ PASS |
| page-rank | ✓ PASS |
