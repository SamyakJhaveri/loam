# Eval Batch: omp_target-to-cuda — 2026-04-24
**Date:** 2026-04-24  |  **Tasks:** 32

## together-qwen-3.5-397b-a17b
**24/32 PASS (75%)** | FAILURES=8 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| convolution1d | L1 | ✗ BUILD_FAIL | — | None | 12249 |
| convolution1d | L2 | ✓ PASS | — | wall_time | 11796 |
| convolution1d | L3 | ✗ BUILD_FAIL | — | None | 6002 |
| convolution1d | L4 | ✗ BUILD_FAIL | — | None | 6624 |
| floydwarshall | L1 | ✓ PASS | 0.843× | wall_time | 7570 |
| floydwarshall | L2 | ✓ PASS | 0.849× | wall_time | 5914 |
| floydwarshall | L3 | ✓ PASS | 1.093× | wall_time | 5762 |
| floydwarshall | L4 | ✓ PASS | 1.073× | wall_time | 8666 |
| heat2d | L1 | ✓ PASS | 0.579× | wall_time | 7300 |
| heat2d | L2 | ✓ PASS | 0.585× | wall_time | 7525 |
| heat2d | L3 | ✓ PASS | 0.579× | wall_time | 7395 |
| heat2d | L4 | ✗ BUILD_FAIL | — | None | 6343 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 8615 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 6846 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 8668 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 8534 |
| jacobi | L1 | ✓ PASS | — | wall_time | 4644 |
| jacobi | L2 | ✗ BUILD_FAIL | — | None | 12935 |
| jacobi | L3 | ✗ BUILD_FAIL | — | None | 6957 |
| jacobi | L4 | ✓ PASS | — | wall_time | 3479 |
| md | L1 | ✓ PASS | — | wall_time | 8545 |
| md | L2 | ✗ RUN_FAIL | — | None | 6665 |
| md | L3 | ✓ PASS | — | wall_time | 9383 |
| md | L4 | ✓ PASS | — | wall_time | 10262 |
| nqueen | L1 | ✓ PASS | — | wall_time | 7269 |
| nqueen | L2 | ✓ PASS | — | wall_time | 7213 |
| nqueen | L3 | ✓ PASS | — | wall_time | 10484 |
| nqueen | L4 | ✓ PASS | — | wall_time | 7380 |
| page-rank | L1 | ✓ PASS | — | wall_time | 5723 |
| page-rank | L2 | ✓ PASS | — | wall_time | 8228 |
| page-rank | L3 | ✓ PASS | — | wall_time | 5606 |
| page-rank | L4 | ✗ BUILD_FAIL | — | None | 5279 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| convolution1d | L1 | ✗ BUILD_FAIL |
| convolution1d | L2 | ✓ PASS |
| convolution1d | L3 | ✗ BUILD_FAIL |
| convolution1d | L4 | ✗ BUILD_FAIL |
| floydwarshall | L1 | ✓ PASS |
| floydwarshall | L2 | ✓ PASS |
| floydwarshall | L3 | ✓ PASS |
| floydwarshall | L4 | ✓ PASS |
| heat2d | L1 | ✓ PASS |
| heat2d | L2 | ✓ PASS |
| heat2d | L3 | ✓ PASS |
| heat2d | L4 | ✗ BUILD_FAIL |
| iso2dfd | L1 | ✓ PASS |
| iso2dfd | L2 | ✓ PASS |
| iso2dfd | L3 | ✓ PASS |
| iso2dfd | L4 | ✓ PASS |
| jacobi | L1 | ✓ PASS |
| jacobi | L2 | ✗ BUILD_FAIL |
| jacobi | L3 | ✗ BUILD_FAIL |
| jacobi | L4 | ✓ PASS |
| md | L1 | ✓ PASS |
| md | L2 | ✗ RUN_FAIL |
| md | L3 | ✓ PASS |
| md | L4 | ✓ PASS |
| nqueen | L1 | ✓ PASS |
| nqueen | L2 | ✓ PASS |
| nqueen | L3 | ✓ PASS |
| nqueen | L4 | ✓ PASS |
| page-rank | L1 | ✓ PASS |
| page-rank | L2 | ✓ PASS |
| page-rank | L3 | ✓ PASS |
| page-rank | L4 | ✗ BUILD_FAIL |
