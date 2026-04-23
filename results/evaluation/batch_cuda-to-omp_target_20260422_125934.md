# Eval Batch: cuda-to-omp_target — 2026-04-22
**Date:** 2026-04-22  |  **Tasks:** 30

## together-qwen-3.5-397b-a17b
**0/10 PASS (0%)** | FAILURES=10 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| convolution1d | ✗ BUILD_FAIL | — | None | 5547 |
| floydwarshall | ✗ BUILD_FAIL | — | None | 4325 |
| heat2d | ✗ BUILD_FAIL | — | None | 10339 |
| iso2dfd | ✗ BUILD_FAIL | — | None | 7459 |
| jacobi | ✗ BUILD_FAIL | — | None | 4001 |
| md | ✗ BUILD_FAIL | — | None | 8789 |
| nqueen | ✗ BUILD_FAIL | — | None | 7333 |
| page-rank | ✗ BUILD_FAIL | — | None | 9030 |
| scan | ✗ BUILD_FAIL | — | None | 15326 |
| stencil1d | ✗ RUN_FAIL | — | None | 13798 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| convolution1d | ✗ BUILD_FAIL |
| floydwarshall | ✗ BUILD_FAIL |
| heat2d | ✗ BUILD_FAIL |
| iso2dfd | ✗ BUILD_FAIL |
| jacobi | ✗ BUILD_FAIL |
| md | ✗ BUILD_FAIL |
| nqueen | ✗ BUILD_FAIL |
| page-rank | ✗ BUILD_FAIL |
| scan | ✗ BUILD_FAIL |
| stencil1d | ✗ RUN_FAIL |
