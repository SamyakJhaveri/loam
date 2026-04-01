# Eval Batch: cuda-to-omp_target — 2026-03-31
**Date:** 2026-03-31  |  **Tasks:** 24

## together-qwen-3.5-397b-a17b
**0/8 PASS (0%)** | FAILURES=8 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| convolution1d | ✗ BUILD_FAIL | — | None | 5085 |
| floydwarshall | ✗ RUN_FAIL | — | None | 3774 |
| heat2d | ✗ BUILD_FAIL | — | None | 3424 |
| iso2dfd | ✗ BUILD_FAIL | — | None | 6016 |
| jacobi | ✗ BUILD_FAIL | — | None | 3040 |
| md | ✗ BUILD_FAIL | — | None | 4916 |
| nqueen | ✗ BUILD_FAIL | — | None | 4945 |
| page-rank | ✗ RUN_FAIL | — | None | 4713 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| convolution1d | ✗ BUILD_FAIL |
| floydwarshall | ✗ RUN_FAIL |
| heat2d | ✗ BUILD_FAIL |
| iso2dfd | ✗ BUILD_FAIL |
| jacobi | ✗ BUILD_FAIL |
| md | ✗ BUILD_FAIL |
| nqueen | ✗ BUILD_FAIL |
| page-rank | ✗ RUN_FAIL |
