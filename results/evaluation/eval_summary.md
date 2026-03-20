# ParBench Evaluation Summary
**Generated:** 2026-03-19 16:40  |  **Total tasks:** 17

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|
| azure-gpt-4.1 | 6 | 10 | 60.0% | 4 | 0 | 0 |
| claude-sonnet-4-20250514 | 3 | 7 | 42.9% | 3 | 1 | 0 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 8 | 16 | 50.0% |
| omp-to-cuda | 1 | 1 | 100.0% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 9 | 17 | 52.9% |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | azure-gpt-4.1 | claude-sonnet-4-20250514 |
|--------|---|---|
| backprop | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| bfs | ✓ PASS | ✓ PASS |
| hotspot | ✓ PASS | ✗ BUILD_FAIL |
| kmeans | ✗ BUILD_FAIL | — |
| lud | ✓ PASS | — |
| nn | ✓ PASS | — |
| nw | ✓ PASS | ✓ PASS |
| pathfinder | ✓ PASS | — |
| srad | ✗ BUILD_FAIL | ✗ RUN_FAIL |
| streamcluster | ✗ BUILD_FAIL | — |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 7 |
| RUN_FAIL | 1 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **17**
- Passed on first attempt: **0**
- Repaired by retry: **9**

