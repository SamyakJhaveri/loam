# Eval Batch: omp_target-to-cuda — 2026-04-22
**Date:** 2026-04-22  |  **Tasks:** 32

## together-qwen-3.5-397b-a17b
**23/32 PASS (71%)** | FAILURES=9 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| convolution1d | L1 | ✗ BUILD_FAIL | — | None | 9295 |
| convolution1d | L2 | ✗ BUILD_FAIL | — | None | 9506 |
| convolution1d | L3 | ✗ BUILD_FAIL | — | None | 8212 |
| convolution1d | L4 | ✓ PASS | — | wall_time | 9449 |
| floydwarshall | L1 | ✓ PASS | 1.098× | wall_time | 5628 |
| floydwarshall | L2 | ✓ PASS | 0.851× | wall_time | 5657 |
| floydwarshall | L3 | ✓ PASS | 1.095× | wall_time | 8231 |
| floydwarshall | L4 | ✓ PASS | 1.056× | wall_time | 5925 |
| heat2d | L1 | ✓ PASS | 0.592× | wall_time | 7145 |
| heat2d | L2 | ✓ PASS | 0.588× | wall_time | 5286 |
| heat2d | L3 | ✓ PASS | 0.580× | wall_time | 5518 |
| heat2d | L4 | ✓ PASS | 0.589× | wall_time | 6250 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 9232 |
| iso2dfd | L2 | ✗ BUILD_FAIL | — | None | 6542 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 6715 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 9919 |
| jacobi | L1 | ✗ BUILD_FAIL | — | None | 8554 |
| jacobi | L2 | ✗ BUILD_FAIL | — | None | 18862 |
| jacobi | L3 | ✗ BUILD_FAIL | — | None | 8909 |
| jacobi | L4 | ✗ BUILD_FAIL | — | None | 10708 |
| md | L1 | ✓ PASS | — | wall_time | 9863 |
| md | L2 | ✓ PASS | — | wall_time | 10202 |
| md | L3 | ✓ PASS | — | wall_time | 9776 |
| md | L4 | ✓ PASS | — | wall_time | 9425 |
| nqueen | L1 | ✓ PASS | — | wall_time | 7355 |
| nqueen | L2 | ✓ PASS | — | wall_time | 7289 |
| nqueen | L3 | ✓ PASS | — | wall_time | 7536 |
| nqueen | L4 | ✓ PASS | — | wall_time | 11571 |
| page-rank | L1 | ✓ PASS | — | wall_time | 6735 |
| page-rank | L2 | ✗ BUILD_FAIL | — | None | 6709 |
| page-rank | L3 | ✓ PASS | — | wall_time | 7631 |
| page-rank | L4 | ✓ PASS | — | wall_time | 6868 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| convolution1d | L1 | ✗ BUILD_FAIL |
| convolution1d | L2 | ✗ BUILD_FAIL |
| convolution1d | L3 | ✗ BUILD_FAIL |
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
| iso2dfd | L2 | ✗ BUILD_FAIL |
| iso2dfd | L3 | ✓ PASS |
| iso2dfd | L4 | ✓ PASS |
| jacobi | L1 | ✗ BUILD_FAIL |
| jacobi | L2 | ✗ BUILD_FAIL |
| jacobi | L3 | ✗ BUILD_FAIL |
| jacobi | L4 | ✗ BUILD_FAIL |
| md | L1 | ✓ PASS |
| md | L2 | ✓ PASS |
| md | L3 | ✓ PASS |
| md | L4 | ✓ PASS |
| nqueen | L1 | ✓ PASS |
| nqueen | L2 | ✓ PASS |
| nqueen | L3 | ✓ PASS |
| nqueen | L4 | ✓ PASS |
| page-rank | L1 | ✓ PASS |
| page-rank | L2 | ✗ BUILD_FAIL |
| page-rank | L3 | ✓ PASS |
| page-rank | L4 | ✓ PASS |
