# Eval Batch: omp-to-omp_target — 2026-04-22
**Date:** 2026-04-22  |  **Tasks:** 15

## together-qwen-3.5-397b-a17b
**2/5 PASS (40%)** | FAILURES=3 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| floydwarshall | ✓ PASS | — | wall_time | 5537 |
| heat2d | ✗ BUILD_FAIL | — | None | 3998 |
| iso2dfd | ✓ PASS | — | wall_time | 8555 |
| scan | ✗ BUILD_FAIL | — | None | 7404 |
| stencil1d | ✗ BUILD_FAIL | — | None | 6176 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| floydwarshall | ✓ PASS |
| heat2d | ✗ BUILD_FAIL |
| iso2dfd | ✓ PASS |
| scan | ✗ BUILD_FAIL |
| stencil1d | ✗ BUILD_FAIL |
