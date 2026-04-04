# Eval Batch: omp_target-to-cuda — 2026-04-03
**Date:** 2026-04-03  |  **Tasks:** 50

## together-qwen-3.5-397b-a17b
**39/50 PASS (78%)** | FAILURES=11 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| convolution1d | L0 | ✗ BUILD_FAIL | — | None | 22827 |
| convolution1d | L1 | ✗ BUILD_FAIL | — | None | 25069 |
| convolution1d | L2 | ✗ BUILD_FAIL | — | None | 26438 |
| convolution1d | L3 | ✗ BUILD_FAIL | — | None | 23294 |
| convolution1d | L4 | ✗ BUILD_FAIL | — | None | 24669 |
| floydwarshall | L0 | ✓ PASS | 1.131× | wall_time | 3556 |
| floydwarshall | L1 | ✓ PASS | 1.115× | wall_time | 3551 |
| floydwarshall | L2 | ✓ PASS | 1.106× | wall_time | 3554 |
| floydwarshall | L3 | ✓ PASS | 0.880× | wall_time | 3571 |
| floydwarshall | L4 | ✓ PASS | 1.109× | wall_time | 3821 |
| heat2d | L0 | ✓ PASS | 0.600× | wall_time | 3397 |
| heat2d | L1 | ✓ PASS | 0.606× | wall_time | 3405 |
| heat2d | L2 | ✓ PASS | 0.624× | wall_time | 3404 |
| heat2d | L3 | ✓ PASS | 0.610× | wall_time | 3414 |
| heat2d | L4 | ✓ PASS | 0.594× | wall_time | 4147 |
| iso2dfd | L0 | ✓ PASS | — | wall_time | 13773 |
| iso2dfd | L1 | ✗ RUN_FAIL | — | None | 25577 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 13791 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 5469 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 5511 |
| jacobi | L0 | ✗ RUN_FAIL | — | None | 13747 |
| jacobi | L1 | ✓ PASS | — | wall_time | 3215 |
| jacobi | L2 | ✓ PASS | — | wall_time | 12124 |
| jacobi | L3 | ✓ PASS | — | wall_time | 12757 |
| jacobi | L4 | ✓ PASS | — | wall_time | 3258 |
| md | L0 | ✓ PASS | — | wall_time | 11251 |
| md | L1 | ✓ PASS | — | wall_time | 19678 |
| md | L2 | ✓ PASS | — | wall_time | 4815 |
| md | L3 | ✓ PASS | — | wall_time | 4816 |
| md | L4 | ✓ PASS | — | wall_time | 4968 |
| nqueen | L0 | ✓ PASS | — | wall_time | 12056 |
| nqueen | L1 | ✓ PASS | — | wall_time | 4775 |
| nqueen | L2 | ✓ PASS | — | wall_time | 12259 |
| nqueen | L3 | ✓ PASS | — | wall_time | 4590 |
| nqueen | L4 | ✓ PASS | — | wall_time | 5466 |
| page-rank | L0 | ✓ PASS | — | wall_time | 4386 |
| page-rank | L1 | ✓ PASS | — | wall_time | 4348 |
| page-rank | L2 | ✓ PASS | — | wall_time | 4396 |
| page-rank | L3 | ✓ PASS | — | wall_time | 4369 |
| page-rank | L4 | ✓ PASS | — | wall_time | 4391 |
| scan | L0 | ✗ BUILD_FAIL | — | None | 21364 |
| scan | L1 | ✗ BUILD_FAIL | — | None | 21375 |
| scan | L2 | ✗ BUILD_FAIL | — | None | 20382 |
| scan | L3 | ✓ PASS | — | wall_time | 21257 |
| scan | L4 | ✗ BUILD_FAIL | — | None | 22425 |
| stencil1d | L0 | ✓ PASS | 0.084× | wall_time | 2005 |
| stencil1d | L1 | ✓ PASS | 0.008× | wall_time | 1996 |
| stencil1d | L2 | ✓ PASS | 0.525× | wall_time | 2020 |
| stencil1d | L3 | ✓ PASS | 0.085× | wall_time | 2028 |
| stencil1d | L4 | ✓ PASS | 0.084× | wall_time | 2164 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| convolution1d | L0 | ✗ BUILD_FAIL |
| convolution1d | L1 | ✗ BUILD_FAIL |
| convolution1d | L2 | ✗ BUILD_FAIL |
| convolution1d | L3 | ✗ BUILD_FAIL |
| convolution1d | L4 | ✗ BUILD_FAIL |
| floydwarshall | L0 | ✓ PASS |
| floydwarshall | L1 | ✓ PASS |
| floydwarshall | L2 | ✓ PASS |
| floydwarshall | L3 | ✓ PASS |
| floydwarshall | L4 | ✓ PASS |
| heat2d | L0 | ✓ PASS |
| heat2d | L1 | ✓ PASS |
| heat2d | L2 | ✓ PASS |
| heat2d | L3 | ✓ PASS |
| heat2d | L4 | ✓ PASS |
| iso2dfd | L0 | ✓ PASS |
| iso2dfd | L1 | ✗ RUN_FAIL |
| iso2dfd | L2 | ✓ PASS |
| iso2dfd | L3 | ✓ PASS |
| iso2dfd | L4 | ✓ PASS |
| jacobi | L0 | ✗ RUN_FAIL |
| jacobi | L1 | ✓ PASS |
| jacobi | L2 | ✓ PASS |
| jacobi | L3 | ✓ PASS |
| jacobi | L4 | ✓ PASS |
| md | L0 | ✓ PASS |
| md | L1 | ✓ PASS |
| md | L2 | ✓ PASS |
| md | L3 | ✓ PASS |
| md | L4 | ✓ PASS |
| nqueen | L0 | ✓ PASS |
| nqueen | L1 | ✓ PASS |
| nqueen | L2 | ✓ PASS |
| nqueen | L3 | ✓ PASS |
| nqueen | L4 | ✓ PASS |
| page-rank | L0 | ✓ PASS |
| page-rank | L1 | ✓ PASS |
| page-rank | L2 | ✓ PASS |
| page-rank | L3 | ✓ PASS |
| page-rank | L4 | ✓ PASS |
| scan | L0 | ✗ BUILD_FAIL |
| scan | L1 | ✗ BUILD_FAIL |
| scan | L2 | ✗ BUILD_FAIL |
| scan | L3 | ✓ PASS |
| scan | L4 | ✗ BUILD_FAIL |
| stencil1d | L0 | ✓ PASS |
| stencil1d | L1 | ✓ PASS |
| stencil1d | L2 | ✓ PASS |
| stencil1d | L3 | ✓ PASS |
| stencil1d | L4 | ✓ PASS |
