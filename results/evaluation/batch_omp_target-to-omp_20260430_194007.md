# Eval Batch: omp_target-to-omp — 2026-04-30
**Date:** 2026-04-30  |  **Tasks:** 12

## azure-gpt-5.3-codex
**12/12 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| floydwarshall | L1 | ✓ PASS | 1.182× | wall_time | 3736 |
| floydwarshall | L2 | ✓ PASS | 1.192× | wall_time | 4137 |
| floydwarshall | L3 | ✓ PASS | 1.008× | wall_time | 4447 |
| floydwarshall | L4 | ✓ PASS | 1.234× | wall_time | 3768 |
| heat2d | L1 | ✓ PASS | 3.000× | wall_time | 3207 |
| heat2d | L2 | ✓ PASS | 3.032× | wall_time | 3181 |
| heat2d | L3 | ✓ PASS | 3.032× | wall_time | 3189 |
| heat2d | L4 | ✓ PASS | 3.032× | wall_time | 3475 |
| iso2dfd | L1 | ✓ PASS | 1.540× | wall_time | 5414 |
| iso2dfd | L2 | ✓ PASS | 1.510× | wall_time | 5124 |
| iso2dfd | L3 | ✓ PASS | 1.510× | wall_time | 5429 |
| iso2dfd | L4 | ✓ PASS | 1.510× | wall_time | 5375 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.3-codex |
|--------|-------|---|
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
