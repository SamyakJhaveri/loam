# ParBench Evaluation Summary
**Generated:** 2026-03-26 10:57  |  **Total tasks:** 452

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-4.1 | 9 | 17 | 52.9% | 4 | 4 | 0 | 0 |
| claude-sonnet-4-6 | 106 | 145 | 73.1% | 10 | 29 | 0 | 0 |
| gemini-2.5-flash-lite | 16 | 145 | 11.0% | 89 | 30 | 0 | 10 |
| groq-llama-3.3-70b-versatile | 27 | 145 | 18.6% | 71 | 19 | 0 | 27 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 110 | 287 | 38.3% |
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
| L1 | 32 | 87 | 36.8% |
| L2 | 31 | 87 | 35.6% |
| L3 | 29 | 87 | 33.3% |
| L4 | 25 | 87 | 28.7% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 30 | 138 | 21.7% | 76 | 18 | 0 |
| multi_to_single | 93 | 221 | 42.1% | 65 | 46 | 0 |
| single_file | 25 | 48 | 52.1% | 9 | 12 | 0 |
| single_to_multi | 10 | 45 | 22.2% | 24 | 6 | 0 |

### Model × Complexity Cross-Tab

| Complexity Class | azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|-----------------|---:|---:|---:|---:|
| multi_to_multi | 1/3 (33.3%) | 26/45 (57.8%) | 0/45 (0.0%) | 3/45 (6.7%) |
| multi_to_single | 6/11 (54.5%) | 60/70 (85.7%) | 12/70 (17.1%) | 15/70 (21.4%) |
| single_file | 2/3 (66.7%) | 10/15 (66.7%) | 4/15 (26.7%) | 9/15 (60.0%) |
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
| BUILD_FAIL | 174 |
| RUN_FAIL | 82 |
| EXTRACTION_FAIL | 37 |
| VERIFY_FAIL | 0 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **452**
- Passed on first attempt: **127**
- Repaired by retry: **31**

