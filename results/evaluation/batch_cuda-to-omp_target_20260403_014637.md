# Eval Batch: cuda-to-omp_target — 2026-04-03
**Date:** 2026-04-03  |  **Tasks:** 40

## together-qwen-3.5-397b-a17b
**7/40 PASS (17%)** | FAILURES=33 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| convolution1d | L0 | ✗ BUILD_FAIL | — | None | 23624 |
| convolution1d | L1 | ✗ BUILD_FAIL | — | None | 23012 |
| convolution1d | L2 | ✗ BUILD_FAIL | — | None | 25487 |
| convolution1d | L3 | ✗ VERIFY_FAIL | — | wall_time | 22846 |
| convolution1d | L4 | ✗ BUILD_FAIL | — | None | 24961 |
| floydwarshall | L0 | ✗ RUN_FAIL | — | None | 16715 |
| floydwarshall | L1 | ✓ PASS | — | wall_time | 3839 |
| floydwarshall | L2 | ✗ RUN_FAIL | — | None | 16927 |
| floydwarshall | L3 | ✗ RUN_FAIL | — | None | 17329 |
| floydwarshall | L4 | ✗ BUILD_FAIL | — | None | 17596 |
| heat2d | L0 | ✗ BUILD_FAIL | — | None | 15649 |
| heat2d | L1 | ✗ BUILD_FAIL | — | None | 15720 |
| heat2d | L2 | ✗ BUILD_FAIL | — | None | 15478 |
| heat2d | L3 | ✗ BUILD_FAIL | — | None | 15549 |
| heat2d | L4 | ✗ BUILD_FAIL | — | None | 15845 |
| iso2dfd | L0 | ✗ BUILD_FAIL | — | None | 36726 |
| iso2dfd | L1 | ✗ BUILD_FAIL | — | None | 25330 |
| iso2dfd | L2 | ✗ BUILD_FAIL | — | None | 27619 |
| iso2dfd | L3 | ✗ RUN_FAIL | — | None | 26023 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 5873 |
| jacobi | L0 | ✗ BUILD_FAIL | — | None | 15361 |
| jacobi | L1 | ✓ PASS | — | wall_time | 3365 |
| jacobi | L2 | ✗ BUILD_FAIL | — | None | 13427 |
| jacobi | L3 | ✓ PASS | — | wall_time | 14821 |
| jacobi | L4 | ✗ BUILD_FAIL | — | None | 15746 |
| md | L0 | ✗ BUILD_FAIL | — | None | 19624 |
| md | L1 | ✓ PASS | — | wall_time | 4881 |
| md | L2 | ✗ BUILD_FAIL | — | None | 19147 |
| md | L3 | ✗ BUILD_FAIL | — | None | 19065 |
| md | L4 | ✗ BUILD_FAIL | — | None | 19520 |
| nqueen | L0 | ✗ BUILD_FAIL | — | None | 22581 |
| nqueen | L1 | ✗ RUN_FAIL | — | None | 21862 |
| nqueen | L2 | ✓ PASS | — | wall_time | 22896 |
| nqueen | L3 | ✗ RUN_FAIL | — | None | 21934 |
| nqueen | L4 | ✗ VERIFY_FAIL | — | wall_time | 21734 |
| page-rank | L0 | ✓ PASS | — | wall_time | 11025 |
| page-rank | L1 | ✗ BUILD_FAIL | — | None | 20873 |
| page-rank | L2 | ✗ RUN_FAIL | — | None | 20609 |
| page-rank | L3 | ✗ BUILD_FAIL | — | None | 21125 |
| page-rank | L4 | ✗ BUILD_FAIL | — | None | 21186 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| convolution1d | L0 | ✗ BUILD_FAIL |
| convolution1d | L1 | ✗ BUILD_FAIL |
| convolution1d | L2 | ✗ BUILD_FAIL |
| convolution1d | L3 | ✗ VERIFY_FAIL |
| convolution1d | L4 | ✗ BUILD_FAIL |
| floydwarshall | L0 | ✗ RUN_FAIL |
| floydwarshall | L1 | ✓ PASS |
| floydwarshall | L2 | ✗ RUN_FAIL |
| floydwarshall | L3 | ✗ RUN_FAIL |
| floydwarshall | L4 | ✗ BUILD_FAIL |
| heat2d | L0 | ✗ BUILD_FAIL |
| heat2d | L1 | ✗ BUILD_FAIL |
| heat2d | L2 | ✗ BUILD_FAIL |
| heat2d | L3 | ✗ BUILD_FAIL |
| heat2d | L4 | ✗ BUILD_FAIL |
| iso2dfd | L0 | ✗ BUILD_FAIL |
| iso2dfd | L1 | ✗ BUILD_FAIL |
| iso2dfd | L2 | ✗ BUILD_FAIL |
| iso2dfd | L3 | ✗ RUN_FAIL |
| iso2dfd | L4 | ✓ PASS |
| jacobi | L0 | ✗ BUILD_FAIL |
| jacobi | L1 | ✓ PASS |
| jacobi | L2 | ✗ BUILD_FAIL |
| jacobi | L3 | ✓ PASS |
| jacobi | L4 | ✗ BUILD_FAIL |
| md | L0 | ✗ BUILD_FAIL |
| md | L1 | ✓ PASS |
| md | L2 | ✗ BUILD_FAIL |
| md | L3 | ✗ BUILD_FAIL |
| md | L4 | ✗ BUILD_FAIL |
| nqueen | L0 | ✗ BUILD_FAIL |
| nqueen | L1 | ✗ RUN_FAIL |
| nqueen | L2 | ✓ PASS |
| nqueen | L3 | ✗ RUN_FAIL |
| nqueen | L4 | ✗ VERIFY_FAIL |
| page-rank | L0 | ✓ PASS |
| page-rank | L1 | ✗ BUILD_FAIL |
| page-rank | L2 | ✗ RUN_FAIL |
| page-rank | L3 | ✗ BUILD_FAIL |
| page-rank | L4 | ✗ BUILD_FAIL |
