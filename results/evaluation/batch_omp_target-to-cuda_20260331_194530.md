# Eval Batch: omp_target-to-cuda — 2026-03-31
**Date:** 2026-03-31  |  **Tasks:** 30

## together-qwen-3.5-397b-a17b
**6/10 PASS (60%)** | FAILURES=4 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| convolution1d | ✗ BUILD_FAIL | — | None | 6138 |
| floydwarshall | ✓ PASS | 1.080× | wall_time | 3562 |
| heat2d | ✓ PASS | 0.591× | wall_time | 3404 |
| iso2dfd | ✓ PASS | — | wall_time | 5465 |
| jacobi | ✗ BUILD_FAIL | — | None | 2703 |
| md | ✗ BUILD_FAIL | — | None | 4594 |
| nqueen | ✓ PASS | — | wall_time | 4747 |
| page-rank | ✓ PASS | — | wall_time | 4900 |
| scan | ✗ BUILD_FAIL | — | None | 4673 |
| stencil1d | ✓ PASS | 0.088× | wall_time | 2104 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| convolution1d | ✗ BUILD_FAIL |
| floydwarshall | ✓ PASS |
| heat2d | ✓ PASS |
| iso2dfd | ✓ PASS |
| jacobi | ✗ BUILD_FAIL |
| md | ✗ BUILD_FAIL |
| nqueen | ✓ PASS |
| page-rank | ✓ PASS |
| scan | ✗ BUILD_FAIL |
| stencil1d | ✓ PASS |
