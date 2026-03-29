# ParBench Evaluation Summary
**Generated:** 2026-03-28 15:54  |  **Total tasks:** 562

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| claude-sonnet-4-6 | 102 | 188 | 54.3% | 15 | 36 | 23 | 12 |
| gemini-2.5-flash-lite | 16 | 187 | 8.6% | 92 | 48 | 14 | 17 |
| groq-llama-3.3-70b-versatile | 19 | 187 | 10.2% | 73 | 39 | 18 | 38 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 62 | 255 | 24.3% |
| cuda-to-omp_target | 4 | 15 | 26.7% |
| cuda-to-opencl | 20 | 66 | 30.3% |
| omp-to-cuda | 9 | 63 | 14.3% |
| omp-to-omp_target | 0 | 15 | 0.0% |
| omp-to-opencl | 22 | 58 | 37.9% |
| omp_target-to-cuda | 4 | 15 | 26.7% |
| omp_target-to-omp | 3 | 15 | 20.0% |
| omp_target-to-opencl | 4 | 15 | 26.7% |
| opencl-to-cuda | 5 | 15 | 33.3% |
| opencl-to-omp | 0 | 15 | 0.0% |
| opencl-to-omp_target | 4 | 15 | 26.7% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 63 | 226 | 27.9% |
| L1 | 20 | 84 | 23.8% |
| L2 | 21 | 84 | 25.0% |
| L3 | 17 | 84 | 20.2% |
| L4 | 16 | 84 | 19.1% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 25 | 153 | 16.3% | 80 | 20 | 4 |
| multi_to_single | 74 | 237 | 31.2% | 52 | 59 | 25 |
| single_file | 23 | 94 | 24.5% | 10 | 32 | 22 |
| single_to_multi | 15 | 78 | 19.2% | 38 | 12 | 4 |

### Model × Complexity Cross-Tab

| Complexity Class | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|-----------------|---:|---:|---:|
| multi_to_multi | 19/51 (37.2%) | 3/51 (5.9%) | 3/51 (5.9%) |
| multi_to_single | 55/79 (69.6%) | 9/79 (11.4%) | 10/79 (12.7%) |
| single_file | 15/32 (46.9%) | 4/31 (12.9%) | 4/31 (12.9%) |
| single_to_multi | 13/26 (50.0%) | 0/26 (0.0%) | 2/26 (7.7%) |

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
| RUN_FAIL | 123 |
| EXTRACTION_FAIL | 67 |
| VERIFY_FAIL | 55 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **562**
- Passed on first attempt: **107**
- Repaired by retry: **30**

