# Eval Batch: cuda-to-omp_target — 2026-04-27
**Date:** 2026-04-27  |  **Tasks:** 32

## azure-gpt-5.4
**30/32 PASS (93%)** | FAILURES=2 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| convolution1d | L1 | ✓ PASS | — | wall_time | 8285 |
| convolution1d | L2 | ✓ PASS | — | wall_time | 8636 |
| convolution1d | L3 | ✓ PASS | — | wall_time | 8469 |
| convolution1d | L4 | ✓ PASS | — | wall_time | 8174 |
| floydwarshall | L1 | ✓ PASS | — | wall_time | 4666 |
| floydwarshall | L2 | ✓ PASS | — | wall_time | 6534 |
| floydwarshall | L3 | ✓ PASS | — | wall_time | 6096 |
| floydwarshall | L4 | ✓ PASS | — | wall_time | 5475 |
| heat2d | L1 | ✓ PASS | — | wall_time | 4677 |
| heat2d | L2 | ✓ PASS | — | wall_time | 5214 |
| heat2d | L3 | ✓ PASS | — | wall_time | 4247 |
| heat2d | L4 | ✗ RUN_FAIL | — | None | 5788 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 8709 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 9267 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 8957 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 9537 |
| jacobi | L1 | ✓ PASS | — | wall_time | 4407 |
| jacobi | L2 | ✓ PASS | — | wall_time | 3277 |
| jacobi | L3 | ✓ PASS | — | wall_time | 4611 |
| jacobi | L4 | ✓ PASS | — | wall_time | 5510 |
| md | L1 | ✓ PASS | — | wall_time | 7509 |
| md | L2 | ✓ PASS | — | wall_time | 7709 |
| md | L3 | ✓ PASS | — | wall_time | 7689 |
| md | L4 | ✓ PASS | — | wall_time | 7380 |
| nqueen | L1 | ✓ PASS | — | wall_time | 5981 |
| nqueen | L2 | ✓ PASS | — | wall_time | 5431 |
| nqueen | L3 | ✓ PASS | — | wall_time | 6383 |
| nqueen | L4 | ✓ PASS | — | wall_time | 6228 |
| page-rank | L1 | ✗ BUILD_FAIL | — | None | 8699 |
| page-rank | L2 | ✓ PASS | — | wall_time | 6273 |
| page-rank | L3 | ✓ PASS | — | wall_time | 7836 |
| page-rank | L4 | ✓ PASS | — | wall_time | 7127 |

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
| heat2d | L4 | ✗ RUN_FAIL |
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
| page-rank | L1 | ✗ BUILD_FAIL |
| page-rank | L2 | ✓ PASS |
| page-rank | L3 | ✓ PASS |
| page-rank | L4 | ✓ PASS |
