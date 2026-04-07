# ParBench Evaluation Summary
**Generated:** 2026-04-07 11:20  |  **Total tasks:** 1951

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-4.1-mini | 222 | 815 | 27.2% | 477 | 74 | 42 | 0 |
| together-qwen-3.5-397b-a17b | 356 | 1136 | 31.3% | 459 | 233 | 66 | 21 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 170 | 384 | 44.3% |
| cuda-to-omp_target | 7 | 128 | 5.5% |
| cuda-to-opencl | 73 | 320 | 22.8% |
| omp-to-cuda | 94 | 276 | 34.1% |
| omp-to-opencl | 83 | 288 | 28.8% |
| omp_target-to-cuda | 57 | 80 | 71.2% |
| opencl-to-cuda | 7 | 187 | 3.7% |
| opencl-to-omp | 87 | 288 | 30.2% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 234 | 946 | 24.7% |
| L1 | 84 | 252 | 33.3% |
| L2 | 90 | 251 | 35.9% |
| L3 | 88 | 251 | 35.1% |
| L4 | 82 | 251 | 32.7% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 6 | 143 | 4.2% | 101 | 28 | 7 |
| multi_to_single | 136 | 424 | 32.1% | 151 | 128 | 7 |
| single_file | 418 | 1076 | 38.9% | 441 | 150 | 66 |
| single_to_multi | 18 | 308 | 5.8% | 243 | 1 | 28 |

### Model × Complexity Cross-Tab

| Complexity Class | azure-gpt-4.1-mini | together-qwen-3.5-397b-a17b |
|-----------------|---:|---:|
| multi_to_multi | 0/63 (0.0%) | 6/80 (7.5%) |
| multi_to_single | 70/208 (33.7%) | 66/216 (30.6%) |
| single_file | 152/452 (33.6%) | 266/624 (42.6%) |
| single_to_multi | 0/92 (0.0%) | 18/216 (8.3%) |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | azure-gpt-4.1-mini | together-qwen-3.5-397b-a17b |
|--------|---|---|
| backprop | ✗ BUILD_FAIL | ✓ PASS |
| bfs | ✓ PASS | ✓ PASS |
| bptree | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| cfd | ✓ PASS | ✓ PASS |
| convolution1d | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| floydwarshall | ✗ BUILD_FAIL | ✗ RUN_FAIL |
| heartwall | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| heat2d | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| hotspot | ✓ PASS | ✓ PASS |
| hotspot3d | ✓ PASS | ✓ PASS |
| iso2dfd | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| jacobi | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| lavamd | ✗ VERIFY_FAIL | ✓ PASS |
| lud | ✗ BUILD_FAIL | ✓ PASS |
| md | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| mixbench | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| myocyte | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| nn | ✓ PASS | ✗ BUILD_FAIL |
| nqueen | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| nw | ✓ PASS | ✓ PASS |
| page-rank | ✗ BUILD_FAIL | ✓ PASS |
| particlefilter | ✓ PASS | ✓ PASS |
| pathfinder | ✓ PASS | ✓ PASS |
| rsbench | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| scan | ✗ BUILD_FAIL | ✓ PASS |
| srad | ✓ PASS | ✓ PASS |
| stencil1d | ✗ BUILD_FAIL | ✓ PASS |
| streamcluster | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | ✗ BUILD_FAIL | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 936 |
| RUN_FAIL | 307 |
| VERIFY_FAIL | 108 |
| EXTRACTION_FAIL | 21 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **1951**
- Passed on first attempt: **419**
- Repaired by retry: **159**

