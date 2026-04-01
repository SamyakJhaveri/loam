# ParBench Evaluation Summary
**Generated:** 2026-03-31 19:45  |  **Total tasks:** 906

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| together-qwen-3.5-397b-a17b | 251 | 906 | 27.7% | 366 | 199 | 69 | 21 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 76 | 152 | 50.0% |
| cuda-to-omp_target | 0 | 24 | 0.0% |
| cuda-to-opencl | 20 | 145 | 13.8% |
| omp-to-cuda | 56 | 152 | 36.8% |
| omp-to-opencl | 33 | 129 | 25.6% |
| omp_target-to-cuda | 18 | 30 | 60.0% |
| opencl-to-cuda | 6 | 145 | 4.1% |
| opencl-to-omp | 42 | 129 | 32.6% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 118 | 522 | 22.6% |
| L1 | 33 | 96 | 34.4% |
| L2 | 35 | 96 | 36.5% |
| L3 | 36 | 96 | 37.5% |
| L4 | 29 | 96 | 30.2% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 6 | 70 | 8.6% | 47 | 13 | 3 |
| multi_to_single | 59 | 196 | 30.1% | 41 | 87 | 8 |
| single_file | 168 | 444 | 37.8% | 131 | 98 | 46 |
| single_to_multi | 18 | 196 | 9.2% | 147 | 1 | 12 |

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
| page-rank | ✗ RUN_FAIL |
| particlefilter | ✓ PASS |
| pathfinder | ✓ PASS |
| rsbench | ✗ BUILD_FAIL |
| scan | ✗ BUILD_FAIL |
| srad | ✓ PASS |
| stencil1d | ✗ BUILD_FAIL |
| streamcluster | ✗ BUILD_FAIL |
| xsbench | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 366 |
| RUN_FAIL | 199 |
| VERIFY_FAIL | 69 |
| EXTRACTION_FAIL | 21 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **906**
- Passed on first attempt: **160**
- Repaired by retry: **91**

