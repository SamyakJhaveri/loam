# Eval Batch: omp_target-to-cuda — 2026-04-27
**Date:** 2026-04-27  |  **Tasks:** 32

## azure-gpt-5.4
**32/32 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| convolution1d | L1 | ✓ PASS | — | wall_time | 7793 |
| convolution1d | L2 | ✓ PASS | — | wall_time | 8470 |
| convolution1d | L3 | ✓ PASS | — | wall_time | 7257 |
| convolution1d | L4 | ✓ PASS | — | wall_time | 8424 |
| floydwarshall | L1 | ✓ PASS | 1.026× | wall_time | 4672 |
| floydwarshall | L2 | ✓ PASS | 0.845× | wall_time | 4747 |
| floydwarshall | L3 | ✓ PASS | 0.845× | wall_time | 4799 |
| floydwarshall | L4 | ✓ PASS | 0.847× | wall_time | 5523 |
| heat2d | L1 | ✓ PASS | 0.586× | wall_time | 4764 |
| heat2d | L2 | ✓ PASS | 0.591× | wall_time | 5413 |
| heat2d | L3 | ✓ PASS | 0.583× | wall_time | 5037 |
| heat2d | L4 | ✓ PASS | 0.585× | wall_time | 6236 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 6751 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 6787 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 7342 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 6718 |
| jacobi | L1 | ✓ PASS | — | wall_time | 3893 |
| jacobi | L2 | ✓ PASS | — | wall_time | 6651 |
| jacobi | L3 | ✓ PASS | — | wall_time | 4705 |
| jacobi | L4 | ✓ PASS | — | wall_time | 4675 |
| md | L1 | ✓ PASS | — | wall_time | 7592 |
| md | L2 | ✓ PASS | — | wall_time | 7609 |
| md | L3 | ✓ PASS | — | wall_time | 6742 |
| md | L4 | ✓ PASS | — | wall_time | 7051 |
| nqueen | L1 | ✓ PASS | — | wall_time | 5783 |
| nqueen | L2 | ✓ PASS | — | wall_time | 6151 |
| nqueen | L3 | ✓ PASS | — | wall_time | 6947 |
| nqueen | L4 | ✓ PASS | — | wall_time | 6767 |
| page-rank | L1 | ✓ PASS | — | wall_time | 6675 |
| page-rank | L2 | ✓ PASS | — | wall_time | 6321 |
| page-rank | L3 | ✓ PASS | — | wall_time | 7315 |
| page-rank | L4 | ✓ PASS | — | wall_time | 6343 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.4 |
|--------|-------|---|
| convolution1d | L1 | ✓ PASS |
| convolution1d | L2 | ✓ PASS |
| convolution1d | L3 | ✓ PASS |
| convolution1d | L4 | ✓ PASS |
| floydwarshall | L1 | ✓ PASS |
| floydwarshall | L2 | ✓ PASS |
| floydwarshall | L3 | ✓ PASS |
| floydwarshall | L4 | ✓ PASS |
| heat2d | L1 | ✓ PASS |
| heat2d | L2 | ✓ PASS |
| heat2d | L3 | ✓ PASS |
| heat2d | L4 | ✓ PASS |
| iso2dfd | L1 | ✓ PASS |
| iso2dfd | L2 | ✓ PASS |
| iso2dfd | L3 | ✓ PASS |
| iso2dfd | L4 | ✓ PASS |
| jacobi | L1 | ✓ PASS |
| jacobi | L2 | ✓ PASS |
| jacobi | L3 | ✓ PASS |
| jacobi | L4 | ✓ PASS |
| md | L1 | ✓ PASS |
| md | L2 | ✓ PASS |
| md | L3 | ✓ PASS |
| md | L4 | ✓ PASS |
| nqueen | L1 | ✓ PASS |
| nqueen | L2 | ✓ PASS |
| nqueen | L3 | ✓ PASS |
| nqueen | L4 | ✓ PASS |
| page-rank | L1 | ✓ PASS |
| page-rank | L2 | ✓ PASS |
| page-rank | L3 | ✓ PASS |
| page-rank | L4 | ✓ PASS |
