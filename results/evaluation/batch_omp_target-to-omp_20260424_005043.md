# Eval Batch: omp_target-to-omp — 2026-04-24
**Date:** 2026-04-24  |  **Tasks:** 12

## together-qwen-3.5-397b-a17b
**11/12 PASS (91%)** | FAILURES=1 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| floydwarshall | L1 | ✓ PASS | 1.219× | wall_time | 4174 |
| floydwarshall | L2 | ✓ PASS | 1.200× | wall_time | 5144 |
| floydwarshall | L3 | ✗ BUILD_FAIL | — | None | 18252 |
| floydwarshall | L4 | ✓ PASS | 1.218× | wall_time | 5956 |
| heat2d | L1 | ✓ PASS | 3.032× | wall_time | 5043 |
| heat2d | L2 | ✓ PASS | 3.032× | wall_time | 5062 |
| heat2d | L3 | ✓ PASS | 3.032× | wall_time | 5106 |
| heat2d | L4 | ✓ PASS | 3.032× | wall_time | 4867 |
| iso2dfd | L1 | ✓ PASS | 1.453× | wall_time | 8306 |
| iso2dfd | L2 | ✓ PASS | 1.453× | wall_time | 8107 |
| iso2dfd | L3 | ✓ PASS | 1.453× | wall_time | 8310 |
| iso2dfd | L4 | ✓ PASS | 1.453× | wall_time | 8189 |

## Cross-Model Summary

| Kernel | Level | together-qwen-3.5-397b-a17b |
|--------|-------|---|
| floydwarshall | L1 | ✓ PASS |
| floydwarshall | L2 | ✓ PASS |
| floydwarshall | L3 | ✗ BUILD_FAIL |
| floydwarshall | L4 | ✓ PASS |
| heat2d | L1 | ✓ PASS |
| heat2d | L2 | ✓ PASS |
| heat2d | L3 | ✓ PASS |
| heat2d | L4 | ✓ PASS |
| iso2dfd | L1 | ✓ PASS |
| iso2dfd | L2 | ✓ PASS |
| iso2dfd | L3 | ✓ PASS |
| iso2dfd | L4 | ✓ PASS |
