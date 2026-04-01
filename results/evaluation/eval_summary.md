# ParBench Evaluation Summary
**Generated:** 2026-04-01 03:20  |  **Total tasks:** 907

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| together-qwen-3.5-397b-a17b | 258 | 907 | 28.4% | 366 | 199 | 62 | 21 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 76 | 152 | 50.0% |
| cuda-to-omp_target | 0 | 24 | 0.0% |
| cuda-to-opencl | 27 | 145 | 18.6% |
| omp-to-cuda | 56 | 152 | 36.8% |
| omp-to-opencl | 33 | 129 | 25.6% |
| omp_target-to-cuda | 18 | 30 | 60.0% |
| opencl-to-cuda | 6 | 145 | 4.1% |
| opencl-to-omp | 42 | 129 | 32.6% |
| unknown | 0 | 1 | 0.0% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 122 | 523 | 23.3% |
| L1 | 33 | 96 | 34.4% |
| L2 | 36 | 96 | 37.5% |
| L3 | 37 | 96 | 38.5% |
| L4 | 30 | 96 | 31.2% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 6 | 70 | 8.6% | 47 | 13 | 3 |
| multi_to_single | 66 | 196 | 33.7% | 41 | 87 | 1 |
| single_file | 168 | 444 | 37.8% | 131 | 98 | 46 |
| single_to_multi | 18 | 196 | 9.2% | 147 | 1 | 12 |
| unknown | 0 | 1 | 0.0% | 0 | 0 | 0 |

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
| VERIFY_FAIL | 62 |
| EXTRACTION_FAIL | 21 |
| UNKNOWN | 1 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **906**
- Passed on first attempt: **163**
- Repaired by retry: **95**

