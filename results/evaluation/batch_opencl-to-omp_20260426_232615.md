# Eval Batch: opencl-to-omp — 2026-04-26
**Date:** 2026-04-26  |  **Tasks:** 32

## azure-gpt-5.4
**27/32 PASS (84%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| bfs | L1 | ✓ PASS | 0.002× | wall_time | 17305 |
| bfs | L2 | ✓ PASS | 0.002× | wall_time | 17250 |
| bfs | L3 | ✓ PASS | 0.002× | wall_time | 16715 |
| bfs | L4 | ✓ PASS | 0.002× | wall_time | 17133 |
| cfd | L1 | ✓ PASS | 0.975× | wall_time | 30739 |
| cfd | L2 | ✓ PASS | 0.980× | wall_time | 30413 |
| cfd | L3 | ✓ PASS | 0.973× | wall_time | 29367 |
| cfd | L4 | ✓ PASS | 0.977× | wall_time | 29274 |
| hotspot3d | L1 | ✓ PASS | 1.436× | wall_time | 17107 |
| hotspot3d | L2 | ✓ PASS | 1.024× | wall_time | 15428 |
| hotspot3d | L3 | ✓ PASS | 0.981× | wall_time | 15922 |
| hotspot3d | L4 | ✓ PASS | 1.019× | wall_time | 16022 |
| lud | L1 | ✓ PASS | 1.000× | wall_time | 17302 |
| lud | L2 | ✗ BUILD_FAIL | — | None | 17435 |
| lud | L3 | ✓ PASS | 1.000× | wall_time | 17087 |
| lud | L4 | ✓ PASS | 1.000× | wall_time | 17529 |
| particlefilter | L1 | ✓ PASS | 1.000× | wall_time | 42662 |
| particlefilter | L2 | ✓ PASS | 1.000× | wall_time | 39057 |
| particlefilter | L3 | ✓ PASS | 0.875× | wall_time | 41833 |
| particlefilter | L4 | ✓ PASS | 1.000× | wall_time | 42751 |
| rsbench | L1 | ✓ PASS | 1.047× | wall_time | 31002 |
| rsbench | L2 | ✓ PASS | 1.014× | wall_time | 30032 |
| rsbench | L3 | ✓ PASS | 1.047× | wall_time | 32034 |
| rsbench | L4 | ✓ PASS | 1.041× | wall_time | 32202 |
| srad | L1 | ✓ PASS | 0.462× | wall_time | 32956 |
| srad | L2 | ✗ BUILD_FAIL | — | None | 24257 |
| srad | L3 | ✓ PASS | 0.462× | wall_time | 26267 |
| srad | L4 | ✓ PASS | 0.462× | wall_time | 26066 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 38981 |
| xsbench | L2 | ✓ PASS | 0.542× | wall_time | 33155 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 33118 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 31507 |

## Cross-Model Summary

| Kernel | Level | azure-gpt-5.4 |
|--------|-------|---|
| bfs | L1 | ✓ PASS |
| bfs | L2 | ✓ PASS |
| bfs | L3 | ✓ PASS |
| bfs | L4 | ✓ PASS |
| cfd | L1 | ✓ PASS |
| cfd | L2 | ✓ PASS |
| cfd | L3 | ✓ PASS |
| cfd | L4 | ✓ PASS |
| hotspot3d | L1 | ✓ PASS |
| hotspot3d | L2 | ✓ PASS |
| hotspot3d | L3 | ✓ PASS |
| hotspot3d | L4 | ✓ PASS |
| lud | L1 | ✓ PASS |
| lud | L2 | ✗ BUILD_FAIL |
| lud | L3 | ✓ PASS |
| lud | L4 | ✓ PASS |
| particlefilter | L1 | ✓ PASS |
| particlefilter | L2 | ✓ PASS |
| particlefilter | L3 | ✓ PASS |
| particlefilter | L4 | ✓ PASS |
| rsbench | L1 | ✓ PASS |
| rsbench | L2 | ✓ PASS |
| rsbench | L3 | ✓ PASS |
| rsbench | L4 | ✓ PASS |
| srad | L1 | ✓ PASS |
| srad | L2 | ✗ BUILD_FAIL |
| srad | L3 | ✓ PASS |
| srad | L4 | ✓ PASS |
| xsbench | L1 | ✗ BUILD_FAIL |
| xsbench | L2 | ✓ PASS |
| xsbench | L3 | ✗ BUILD_FAIL |
| xsbench | L4 | ✗ BUILD_FAIL |
