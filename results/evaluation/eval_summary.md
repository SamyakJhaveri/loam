# ParBench Evaluation Summary
**Generated:** 2026-04-08 22:16  |  **Total tasks:** 1949

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-4.1-mini | 246 | 813 | 30.3% | 357 | 91 | 119 | 0 |
| together-qwen-3.5-397b-a17b | 356 | 1136 | 31.3% | 459 | 233 | 66 | 21 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 170 | 320 | 53.1% |
| cuda-to-omp_target | 7 | 64 | 10.9% |
| cuda-to-opencl | 73 | 296 | 24.7% |
| omp-to-cuda | 95 | 323 | 29.4% |
| omp-to-opencl | 83 | 264 | 31.4% |
| omp_target-to-cuda | 80 | 160 | 50.0% |
| opencl-to-cuda | 7 | 258 | 2.7% |
| opencl-to-omp | 87 | 264 | 33.0% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 244 | 936 | 26.1% |
| L1 | 86 | 254 | 33.9% |
| L2 | 93 | 253 | 36.8% |
| L3 | 92 | 253 | 36.4% |
| L4 | 87 | 253 | 34.4% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 6 | 141 | 4.3% | 99 | 28 | 7 |
| multi_to_single | 136 | 397 | 34.3% | 124 | 128 | 7 |
| single_file | 442 | 1066 | 41.5% | 313 | 167 | 143 |
| single_to_multi | 18 | 345 | 5.2% | 280 | 1 | 28 |

### Model × Complexity Cross-Tab

| Complexity Class | azure-gpt-4.1-mini | together-qwen-3.5-397b-a17b |
|-----------------|---:|---:|
| multi_to_multi | 0/61 (0.0%) | 6/80 (7.5%) |
| multi_to_single | 70/181 (38.7%) | 66/216 (30.6%) |
| single_file | 176/442 (39.8%) | 266/624 (42.6%) |
| single_to_multi | 0/129 (0.0%) | 18/216 (8.3%) |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | azure-gpt-4.1-mini | together-qwen-3.5-397b-a17b |
|--------|---|---|
| backprop | ✗ BUILD_FAIL | ✓ PASS |
| bfs | ✓ PASS | ✓ PASS |
| bptree | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| cfd | ✓ PASS | ✓ PASS |
| convolution1d | — | ✗ BUILD_FAIL |
| floydwarshall | — | ✗ RUN_FAIL |
| heartwall | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| heat2d | — | ✗ BUILD_FAIL |
| hotspot | ✓ PASS | ✓ PASS |
| hotspot3d | ✓ PASS | ✓ PASS |
| iso2dfd | — | ✗ BUILD_FAIL |
| jacobi | — | ✗ BUILD_FAIL |
| lavamd | ✗ VERIFY_FAIL | ✓ PASS |
| lud | ✗ BUILD_FAIL | ✓ PASS |
| md | — | ✗ BUILD_FAIL |
| mixbench | — | ✗ BUILD_FAIL |
| myocyte | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| nn | ✓ PASS | ✗ BUILD_FAIL |
| nqueen | — | ✗ BUILD_FAIL |
| nw | ✓ PASS | ✓ PASS |
| page-rank | — | ✓ PASS |
| particlefilter | ✓ PASS | ✓ PASS |
| pathfinder | ✓ PASS | ✓ PASS |
| rsbench | — | ✗ BUILD_FAIL |
| scan | — | ✓ PASS |
| srad | ✓ PASS | ✓ PASS |
| stencil1d | — | ✓ PASS |
| streamcluster | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | — | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 816 |
| RUN_FAIL | 324 |
| VERIFY_FAIL | 185 |
| EXTRACTION_FAIL | 21 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **1949**
- Passed on first attempt: **442**
- Repaired by retry: **160**

