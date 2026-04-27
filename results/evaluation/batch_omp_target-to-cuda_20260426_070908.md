# Eval Batch: omp_target-to-cuda — 2026-04-26
**Date:** 2026-04-26  |  **Tasks:** 24

## azure-gpt-5.4
**8/8 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| convolution1d | ✓ PASS | — | wall_time | 7837 |
| floydwarshall | ✓ PASS | 1.091× | wall_time | 4778 |
| heat2d | ✓ PASS | 0.580× | wall_time | 4864 |
| iso2dfd | ✓ PASS | — | wall_time | 7159 |
| jacobi | ✓ PASS | — | wall_time | 5449 |
| md | ✓ PASS | — | wall_time | 6827 |
| nqueen | ✓ PASS | — | wall_time | 6852 |
| page-rank | ✓ PASS | — | wall_time | 6093 |

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
