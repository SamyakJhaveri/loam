# Eval Batch: omp_target-to-cuda — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 32

## azure-gpt-5.3-codex
**32/32 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| convolution1d | L1 | ✓ PASS | — | wall_time | 6182 |
| convolution1d | L2 | ✓ PASS | — | wall_time | 6813 |
| convolution1d | L3 | ✓ PASS | — | wall_time | 6602 |
| convolution1d | L4 | ✓ PASS | — | wall_time | 6690 |
| floydwarshall | L1 | ✓ PASS | 1.109× | wall_time | 4316 |
| floydwarshall | L2 | ✓ PASS | 1.101× | wall_time | 4122 |
| floydwarshall | L3 | ✓ PASS | 1.095× | wall_time | 4030 |
| floydwarshall | L4 | ✓ PASS | 1.105× | wall_time | 4496 |
| heat2d | L1 | ✓ PASS | 0.582× | wall_time | 3931 |
| heat2d | L2 | ✓ PASS | 0.597× | wall_time | 4488 |
| heat2d | L3 | ✓ PASS | 0.583× | wall_time | 4468 |
| heat2d | L4 | ✓ PASS | 0.588× | wall_time | 4808 |
| iso2dfd | L1 | ✓ PASS | — | wall_time | 6016 |
| iso2dfd | L2 | ✓ PASS | — | wall_time | 5914 |
| iso2dfd | L3 | ✓ PASS | — | wall_time | 6017 |
| iso2dfd | L4 | ✓ PASS | — | wall_time | 6355 |
| jacobi | L1 | ✓ PASS | — | wall_time | 3538 |
| jacobi | L2 | ✓ PASS | — | wall_time | 3336 |
| jacobi | L3 | ✓ PASS | — | wall_time | 3580 |
| jacobi | L4 | ✓ PASS | — | wall_time | 3893 |
| md | L1 | ✓ PASS | — | wall_time | 5491 |
| md | L2 | ✓ PASS | — | wall_time | 6465 |
| md | L3 | ✓ PASS | — | wall_time | 5495 |
| md | L4 | ✓ PASS | — | wall_time | 5513 |
| nqueen | L1 | ✓ PASS | — | wall_time | 5093 |
| nqueen | L2 | ✓ PASS | — | wall_time | 5383 |
| nqueen | L3 | ✓ PASS | — | wall_time | 5097 |
| nqueen | L4 | ✓ PASS | — | wall_time | 5650 |
| page-rank | L1 | ✓ PASS | — | wall_time | 6141 |
| page-rank | L2 | ✓ PASS | — | wall_time | 5351 |
| page-rank | L3 | ✓ PASS | — | wall_time | 5012 |
| page-rank | L4 | ✓ PASS | — | wall_time | 5244 |

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
| heat2d | L4 | ✓ PASS |
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
| nqueen | L1 | ✓ PASS |
| nqueen | L2 | ✓ PASS |
| nqueen | L3 | ✓ PASS |
| nqueen | L4 | ✓ PASS |
| page-rank | L1 | ✓ PASS |
| page-rank | L2 | ✓ PASS |
| page-rank | L3 | ✓ PASS |
| page-rank | L4 | ✓ PASS |
