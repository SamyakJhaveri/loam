# Eval Batch: omp_target-to-cuda — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 24

## azure-gpt-5.3-codex
**8/8 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| convolution1d | ✓ PASS | — | wall_time | 6962 |
| floydwarshall | ✓ PASS | 1.109× | wall_time | 4409 |
| heat2d | ✓ PASS | 0.586× | wall_time | 4530 |
| iso2dfd | ✓ PASS | — | wall_time | 6438 |
| jacobi | ✓ PASS | — | wall_time | 3790 |
| md | ✓ PASS | — | wall_time | 5208 |
| nqueen | ✓ PASS | — | wall_time | 5215 |
| page-rank | ✓ PASS | — | wall_time | 5324 |

## Cross-Model Summary

| Kernel | azure-gpt-5.3-codex |
|--------|---|
| convolution1d | ✓ PASS |
| floydwarshall | ✓ PASS |
| heat2d | ✓ PASS |
| iso2dfd | ✓ PASS |
| jacobi | ✓ PASS |
| md | ✓ PASS |
| nqueen | ✓ PASS |
| page-rank | ✓ PASS |
