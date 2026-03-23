# ParBench Evaluation Summary
**Generated:** 2026-03-22 20:46  |  **Total tasks:** 17

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|
| azure-gpt-4.1 | 9 | 17 | 52.9% | 4 | 4 | 0 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 9 | 17 | 52.9% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 9 | 17 | 52.9% |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | azure-gpt-4.1 |
|--------|---|
| backprop | ✗ BUILD_FAIL |
| bfs | ✓ PASS |
| bptree | ✓ PASS |
| cfd | ✓ PASS |
| heartwall | ✗ RUN_FAIL |
| hotspot | ✗ RUN_FAIL |
| hotspot3d | ✓ PASS |
| kmeans | ✓ PASS |
| lavamd | ✓ PASS |
| lud | ✓ PASS |
| myocyte | ✗ BUILD_FAIL |
| nn | ✓ PASS |
| nw | ✗ RUN_FAIL |
| particlefilter | ✗ BUILD_FAIL |
| pathfinder | ✓ PASS |
| srad | ✗ RUN_FAIL |
| streamcluster | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 4 |
| RUN_FAIL | 4 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **17**
- Passed on first attempt: **7**
- Repaired by retry: **2**

