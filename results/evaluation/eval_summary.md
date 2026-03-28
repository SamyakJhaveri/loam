# ParBench Evaluation Summary
**Generated:** 2026-03-28 01:54  |  **Total tasks:** 468

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| claude-sonnet-4-6 | 81 | 156 | 51.9% | 15 | 30 | 19 | 11 |
| gemini-2.5-flash-lite | 11 | 156 | 7.0% | 92 | 32 | 10 | 11 |
| groq-llama-3.3-70b-versatile | 13 | 156 | 8.3% | 73 | 27 | 16 | 27 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 62 | 255 | 24.3% |
| cuda-to-omp_target | 4 | 15 | 26.7% |
| cuda-to-opencl | 5 | 15 | 33.3% |
| omp-to-cuda | 9 | 63 | 14.3% |
| omp-to-omp_target | 0 | 15 | 0.0% |
| omp-to-opencl | 5 | 15 | 33.3% |
| omp_target-to-cuda | 4 | 15 | 26.7% |
| omp_target-to-omp | 3 | 15 | 20.0% |
| omp_target-to-opencl | 4 | 15 | 26.7% |
| opencl-to-cuda | 5 | 15 | 33.3% |
| opencl-to-omp | 0 | 15 | 0.0% |
| opencl-to-omp_target | 4 | 15 | 26.7% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 31 | 132 | 23.5% |
| L1 | 20 | 84 | 23.8% |
| L2 | 21 | 84 | 25.0% |
| L3 | 17 | 84 | 20.2% |
| L4 | 16 | 84 | 19.1% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 23 | 144 | 16.0% | 80 | 18 | 2 |
| multi_to_single | 62 | 195 | 31.8% | 52 | 40 | 22 |
| single_file | 5 | 54 | 9.3% | 10 | 19 | 20 |
| single_to_multi | 15 | 75 | 20.0% | 38 | 12 | 1 |

### Model × Complexity Cross-Tab

| Complexity Class | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|-----------------|---:|---:|---:|
| multi_to_multi | 17/48 (35.4%) | 3/48 (6.2%) | 3/48 (6.2%) |
| multi_to_single | 47/65 (72.3%) | 8/65 (12.3%) | 7/65 (10.8%) |
| single_file | 4/18 (22.2%) | 0/18 (0.0%) | 1/18 (5.6%) |
| single_to_multi | 13/25 (52.0%) | 0/25 (0.0%) | 2/25 (8.0%) |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|---|---|---|
| backprop | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| bfs | ✗ VERIFY_FAIL | ✗ BUILD_FAIL | ✗ VERIFY_FAIL |
| bptree | ✓ PASS | ✓ PASS | ✓ PASS |
| cfd | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| heartwall | ✗ BUILD_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| hotspot | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ RUN_FAIL |
| hotspot3d | ✓ PASS | ✓ PASS | ✓ PASS |
| lavamd | ✓ PASS | ✗ VERIFY_FAIL | ✗ BUILD_FAIL |
| lud | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| myocyte | ✗ BUILD_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| nn | ✓ PASS | ✗ VERIFY_FAIL | ✗ RUN_FAIL |
| nw | ✗ VERIFY_FAIL | ✗ EXTRACTION_FAIL | ✗ BUILD_FAIL |
| particlefilter | ✓ PASS | ✗ BUILD_FAIL | ✓ PASS |
| pathfinder | ✗ VERIFY_FAIL | ✗ BUILD_FAIL | ✗ VERIFY_FAIL |
| srad | ✓ PASS | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL |
| streamcluster | ✗ VERIFY_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 180 |
| RUN_FAIL | 89 |
| EXTRACTION_FAIL | 49 |
| VERIFY_FAIL | 45 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **468**
- Passed on first attempt: **78**
- Repaired by retry: **27**

