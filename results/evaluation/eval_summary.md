# ParBench Evaluation Summary
**Generated:** 2026-03-22 22:14  |  **Total tasks:** 34

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|
| azure-gpt-4.1 | 9 | 17 | 52.9% | 4 | 4 | 0 |
| groq-llama-3.3-70b-versatile | 5 | 17 | 29.4% | 11 | 1 | 0 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 14 | 34 | 41.2% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 14 | 34 | 41.2% |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | azure-gpt-4.1 | groq-llama-3.3-70b-versatile |
|--------|---|---|
| backprop | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| bfs | ✓ PASS | ✓ PASS |
| bptree | ✓ PASS | ✗ BUILD_FAIL |
| cfd | ✓ PASS | ✗ BUILD_FAIL |
| heartwall | ✗ RUN_FAIL | ✗ BUILD_FAIL |
| hotspot | ✗ RUN_FAIL | ✗ BUILD_FAIL |
| hotspot3d | ✓ PASS | ✓ PASS |
| kmeans | ✓ PASS | ✗ BUILD_FAIL |
| lavamd | ✓ PASS | ✗ BUILD_FAIL |
| lud | ✓ PASS | ✓ PASS |
| myocyte | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| nn | ✓ PASS | ✓ PASS |
| nw | ✗ RUN_FAIL | ✗ BUILD_FAIL |
| particlefilter | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| pathfinder | ✓ PASS | ✓ PASS |
| srad | ✗ RUN_FAIL | ✗ RUN_FAIL |
| streamcluster | ✗ BUILD_FAIL | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 15 |
| RUN_FAIL | 5 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **34**
- Passed on first attempt: **9**
- Repaired by retry: **5**

