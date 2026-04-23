# Eval Batch: omp_target-to-cuda — 2026-04-21
**Date:** 2026-04-21  |  **Tasks:** 30

## together-qwen-3.5-397b-a17b
**7/10 PASS (70%)** | FAILURES=3 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| convolution1d | ✗ BUILD_FAIL | — | None | 8837 |
| floydwarshall | ✓ PASS | 1.088× | wall_time | 5603 |
| heat2d | ✓ PASS | 0.589× | wall_time | 5317 |
| iso2dfd | ✗ BUILD_FAIL | — | None | 5996 |
| jacobi | ✓ PASS | — | wall_time | 4288 |
| md | ✓ PASS | — | wall_time | 6335 |
| nqueen | ✓ PASS | — | wall_time | 7532 |
| page-rank | ✓ PASS | — | wall_time | 10999 |
| scan | ✗ BUILD_FAIL | — | None | 9705 |
| stencil1d | ✓ PASS | 0.465× | wall_time | 11177 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| convolution1d | ✗ BUILD_FAIL |
| floydwarshall | ✓ PASS |
| heat2d | ✓ PASS |
| iso2dfd | ✗ BUILD_FAIL |
| jacobi | ✓ PASS |
| md | ✓ PASS |
| nqueen | ✓ PASS |
| page-rank | ✓ PASS |
| scan | ✗ BUILD_FAIL |
| stencil1d | ✓ PASS |
