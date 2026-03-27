# ParBench Evaluation Summary
**Generated:** 2026-03-26 21:46  |  **Total tasks:** 500

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-4.1 | 9 | 17 | 52.9% | 4 | 4 | 0 | 0 |
| claude-sonnet-4-6 | 113 | 161 | 70.2% | 16 | 32 | 0 | 0 |
| gemini-2.5-flash-lite | 17 | 161 | 10.6% | 100 | 33 | 0 | 11 |
| groq-llama-3.3-70b-versatile | 30 | 161 | 18.6% | 82 | 20 | 0 | 28 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 110 | 287 | 38.3% |
| cuda-to-omp_target | 5 | 15 | 33.3% |
| cuda-to-opencl | 5 | 15 | 33.3% |
| omp-to-cuda | 17 | 63 | 27.0% |
| omp-to-omp_target | 4 | 15 | 26.7% |
| omp-to-opencl | 5 | 15 | 33.3% |
| omp_target-to-cuda | 6 | 15 | 40.0% |
| omp_target-to-omp | 2 | 15 | 13.3% |
| omp_target-to-opencl | 5 | 15 | 33.3% |
| opencl-to-cuda | 5 | 15 | 33.3% |
| opencl-to-omp | 0 | 15 | 0.0% |
| opencl-to-omp_target | 5 | 15 | 33.3% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 52 | 152 | 34.2% |
| L1 | 32 | 87 | 36.8% |
| L2 | 31 | 87 | 35.6% |
| L3 | 29 | 87 | 33.3% |
| L4 | 25 | 87 | 28.7% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 32 | 147 | 21.8% | 82 | 18 | 0 |
| multi_to_single | 93 | 221 | 42.1% | 65 | 46 | 0 |
| single_file | 27 | 57 | 47.4% | 12 | 16 | 0 |
| single_to_multi | 17 | 75 | 22.7% | 43 | 9 | 0 |

### Model × Complexity Cross-Tab

| Complexity Class | azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|-----------------|---:|---:|---:|---:|
| multi_to_multi | 1/3 (33.3%) | 27/48 (56.2%) | 0/48 (0.0%) | 4/48 (8.3%) |
| multi_to_single | 6/11 (54.5%) | 60/70 (85.7%) | 12/70 (17.1%) | 15/70 (21.4%) |
| single_file | 2/3 (66.7%) | 11/18 (61.1%) | 5/18 (27.8%) | 9/18 (50.0%) |
| single_to_multi | — | 15/25 (60.0%) | 0/25 (0.0%) | 2/25 (8.0%) |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|---|---|---|---|
| backprop | ✗ BUILD_FAIL | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| bfs | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✓ PASS |
| bptree | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| cfd | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| heartwall | ✗ RUN_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL | ✗ EXTRACTION_FAIL |
| hotspot | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ BUILD_FAIL |
| hotspot3d | ✓ PASS | ✓ PASS | ✓ PASS | ✓ PASS |
| kmeans | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| lavamd | ✓ PASS | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| lud | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✓ PASS |
| myocyte | ✗ BUILD_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| nn | ✓ PASS | ✓ PASS | ✓ PASS | ✓ PASS |
| nw | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL | ✗ BUILD_FAIL |
| particlefilter | ✗ BUILD_FAIL | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| pathfinder | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✓ PASS |
| srad | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ RUN_FAIL |
| streamcluster | ✗ BUILD_FAIL | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | — | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 202 |
| RUN_FAIL | 89 |
| EXTRACTION_FAIL | 39 |
| VERIFY_FAIL | 0 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **500**
- Passed on first attempt: **134**
- Repaired by retry: **35**

