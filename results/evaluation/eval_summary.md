# ParBench Evaluation Summary
**Generated:** 2026-03-25 10:51  |  **Total tasks:** 248

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-4.1 | 9 | 17 | 52.9% | 4 | 4 | 0 | 0 |
| claude-sonnet-4-6 | 58 | 77 | 75.3% | 2 | 17 | 0 | 0 |
| gemini-2.5-flash-lite | 4 | 77 | 5.2% | 47 | 22 | 0 | 4 |
| groq-llama-3.3-70b-versatile | 7 | 77 | 9.1% | 40 | 15 | 0 | 14 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 30 | 83 | 36.1% |
| cuda-to-omp_target | 5 | 15 | 33.3% |
| cuda-to-opencl | 5 | 15 | 33.3% |
| omp-to-cuda | 6 | 15 | 40.0% |
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
| L0 | 41 | 104 | 39.4% |
| L1 | 10 | 36 | 27.8% |
| L2 | 9 | 36 | 25.0% |
| L3 | 10 | 36 | 27.8% |
| L4 | 8 | 36 | 22.2% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 25 | 102 | 24.5% | 51 | 18 | 0 |
| multi_to_single | 36 | 89 | 40.5% | 16 | 31 | 0 |
| single_file | 7 | 12 | 58.3% | 2 | 3 | 0 |
| single_to_multi | 10 | 45 | 22.2% | 24 | 6 | 0 |

### Model × Complexity Cross-Tab

| Complexity Class | azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|-----------------|---:|---:|---:|---:|
| multi_to_multi | 1/3 (33.3%) | 22/33 (66.7%) | 0/33 (0.0%) | 2/33 (6.1%) |
| multi_to_single | 6/11 (54.5%) | 24/26 (92.3%) | 3/26 (11.5%) | 3/26 (11.5%) |
| single_file | 2/3 (66.7%) | 2/3 (66.7%) | 1/3 (33.3%) | 2/3 (66.7%) |
| single_to_multi | — | 10/15 (66.7%) | 0/15 (0.0%) | 0/15 (0.0%) |

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
| BUILD_FAIL | 93 |
| RUN_FAIL | 58 |
| EXTRACTION_FAIL | 18 |
| VERIFY_FAIL | 0 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **248**
- Passed on first attempt: **60**
- Repaired by retry: **18**

