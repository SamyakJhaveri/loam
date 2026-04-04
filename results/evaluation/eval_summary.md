# ParBench Evaluation Summary
**Generated:** 2026-04-04 13:34  |  **Total tasks:** 1136

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| together-qwen-3.5-397b-a17b | 356 | 1136 | 31.3% | 459 | 233 | 66 | 21 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 101 | 192 | 52.6% |
| cuda-to-omp_target | 7 | 64 | 10.9% |
| cuda-to-opencl | 28 | 160 | 17.5% |
| omp-to-cuda | 79 | 192 | 41.1% |
| omp-to-opencl | 36 | 144 | 25.0% |
| omp_target-to-cuda | 57 | 80 | 71.2% |
| opencl-to-cuda | 6 | 160 | 3.8% |
| opencl-to-omp | 42 | 144 | 29.2% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 141 | 568 | 24.8% |
| L1 | 53 | 142 | 37.3% |
| L2 | 57 | 142 | 40.1% |
| L3 | 56 | 142 | 39.4% |
| L4 | 49 | 142 | 34.5% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 6 | 80 | 7.5% | 57 | 13 | 3 |
| multi_to_single | 66 | 216 | 30.6% | 46 | 101 | 1 |
| single_file | 266 | 624 | 42.6% | 189 | 118 | 50 |
| single_to_multi | 18 | 216 | 8.3% | 167 | 1 | 12 |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✓ PASS |
| bfs | ✓ PASS |
| bptree | ✗ BUILD_FAIL |
| cfd | ✓ PASS |
| convolution1d | ✗ BUILD_FAIL |
| floydwarshall | ✗ RUN_FAIL |
| heartwall | ✗ BUILD_FAIL |
| heat2d | ✗ BUILD_FAIL |
| hotspot | ✓ PASS |
| hotspot3d | ✓ PASS |
| iso2dfd | ✗ BUILD_FAIL |
| jacobi | ✗ BUILD_FAIL |
| lavamd | ✓ PASS |
| lud | ✓ PASS |
| md | ✗ BUILD_FAIL |
| mixbench | ✗ BUILD_FAIL |
| myocyte | ✗ BUILD_FAIL |
| nn | ✗ BUILD_FAIL |
| nqueen | ✗ BUILD_FAIL |
| nw | ✓ PASS |
| page-rank | ✓ PASS |
| particlefilter | ✓ PASS |
| pathfinder | ✓ PASS |
| rsbench | ✗ BUILD_FAIL |
| scan | ✓ PASS |
| srad | ✓ PASS |
| stencil1d | ✓ PASS |
| streamcluster | ✗ BUILD_FAIL |
| xsbench | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 459 |
| RUN_FAIL | 233 |
| VERIFY_FAIL | 66 |
| EXTRACTION_FAIL | 21 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **1136**
- Passed on first attempt: **239**
- Repaired by retry: **117**

