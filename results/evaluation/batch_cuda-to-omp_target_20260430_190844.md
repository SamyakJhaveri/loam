# Eval Batch: cuda-to-omp_target — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 32

## azure-gpt-5.3-codex
**29/32 PASS (90%)** | FAILURES=3 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| convolution1d | L1 | ✓ PASS | — | wall_time | 6118 |
| convolution1d | L2 | ✓ PASS | — | wall_time | 6263 |
| convolution1d | L3 | ✓ PASS | — | wall_time | 6358 |
| convolution1d | L4 | ✓ PASS | — | wall_time | 5743 |
| floydwarshall | L1 | ✓ PASS | — | wall_time | 4521 |
| floydwarshall | L2 | ✓ PASS | — | wall_time | 4118 |
| floydwarshall | L3 | ✓ PASS | — | wall_time | 5123 |
| floydwarshall | L4 | ✓ PASS | — | wall_time | 5340 |
| heat2d | L1 | ✓ PASS | — | wall_time | 5449 |
| heat2d | L2 | ✓ PASS | — | wall_time | 3721 |
| heat2d | L3 | ✓ PASS | — | wall_time | 4782 |
| heat2d | L4 | ✗ RUN_FAIL | — | None | 4040 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 6746 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 6567 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 7278 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 6568 |
| jacobi | L1 | ✓ PASS | — | wall_time | 3637 |
| jacobi | L2 | ✓ PASS | — | wall_time | 4418 |
| jacobi | L3 | ✓ PASS | — | wall_time | 3962 |
| jacobi | L4 | ✓ PASS | — | wall_time | 3891 |
| md | L1 | ✓ PASS | — | wall_time | 6524 |
| md | L2 | ✓ PASS | — | wall_time | 6988 |
| md | L3 | ✓ PASS | — | wall_time | 6827 |
| md | L4 | ✓ PASS | — | wall_time | 6739 |
| nqueen | L1 | ✗ BUILD_FAIL | — | None | 5904 |
| nqueen | L2 | ✓ PASS | — | wall_time | 5954 |
| nqueen | L3 | ✓ PASS | — | wall_time | 5037 |
| nqueen | L4 | ✓ PASS | — | wall_time | 4975 |
| page-rank | L1 | ✓ PASS | — | wall_time | 6260 |
| page-rank | L2 | ✓ PASS | — | wall_time | 6049 |
| page-rank | L3 | ✓ PASS | — | wall_time | 6684 |
| page-rank | L4 | ✗ BUILD_FAIL | — | None | 5716 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.3-codex |
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
| nqueen | L1 | ✗ BUILD_FAIL |
| nqueen | L2 | ✓ PASS |
| nqueen | L3 | ✓ PASS |
| nqueen | L4 | ✓ PASS |
| page-rank | L1 | ✓ PASS |
| page-rank | L2 | ✓ PASS |
| page-rank | L3 | ✓ PASS |
| page-rank | L4 | ✗ BUILD_FAIL |
