# Eval Batch: omp_target-to-omp — 2026-04-22
**Date:** 2026-04-22  |  **Tasks:** 12

## together-qwen-3.5-397b-a17b
**12/12 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| floydwarshall | L1 | ✓ PASS | 1.219× | wall_time | 5277 |
| floydwarshall | L2 | ✓ PASS | 1.222× | wall_time | 5112 |
| floydwarshall | L3 | ✓ PASS | 1.221× | wall_time | 5276 |
| floydwarshall | L4 | ✓ PASS | 1.229× | wall_time | 5619 |
| heat2d | L1 | ✓ PASS | 3.032× | wall_time | 5042 |
| heat2d | L2 | ✓ PASS | 3.000× | wall_time | 5043 |
| heat2d | L3 | ✓ PASS | 3.000× | wall_time | 5035 |
| heat2d | L4 | ✓ PASS | 3.032× | wall_time | 5806 |
| iso2dfd | L1 | ✓ PASS | 1.453× | wall_time | 7953 |
| iso2dfd | L2 | ✓ PASS | 1.453× | wall_time | 7984 |
| iso2dfd | L3 | ✓ PASS | 1.453× | wall_time | 5761 |
| iso2dfd | L4 | ✓ PASS | 1.426× | wall_time | 8026 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
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
