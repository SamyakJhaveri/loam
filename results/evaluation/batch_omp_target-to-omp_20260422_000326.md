# Eval Batch: omp_target-to-omp — 2026-04-22
**Date:** 2026-04-22  |  **Tasks:** 15

## together-qwen-3.5-397b-a17b
**3/5 PASS (60%)** | FAILURES=2 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| floydwarshall | ✓ PASS | 1.219× | wall_time | 4136 |
| heat2d | ✓ PASS | 3.032× | wall_time | 5126 |
| iso2dfd | ✓ PASS | 1.453× | wall_time | 5471 |
| scan | ✗ BUILD_FAIL | — | None | 14732 |
| stencil1d | ✗ BUILD_FAIL | — | None | 11998 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| floydwarshall | ✓ PASS |
| heat2d | ✓ PASS |
| iso2dfd | ✓ PASS |
| scan | ✗ BUILD_FAIL |
| stencil1d | ✗ BUILD_FAIL |
