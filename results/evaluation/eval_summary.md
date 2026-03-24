# ParBench Evaluation Summary
**Generated:** 2026-03-23 22:53  |  **Total tasks:** 51

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-4.1 | 9 | 17 | 52.9% | 4 | 4 | 0 | 0 |
| claude-sonnet-4-6 | 12 | 17 | 70.6% | 2 | 3 | 0 | 0 |
| groq-llama-3.3-70b-versatile | 5 | 17 | 29.4% | 10 | 1 | 0 | 1 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 26 | 51 | 51.0% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 26 | 51 | 51.0% |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | azure-gpt-4.1 | claude-sonnet-4-6 | groq-llama-3.3-70b-versatile |
|--------|---|---|---|
| backprop | ✗ BUILD_FAIL | ✓ PASS | ✗ BUILD_FAIL |
| bfs | ✓ PASS | ✓ PASS | ✓ PASS |
| bptree | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| cfd | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| heartwall | ✗ RUN_FAIL | ✗ BUILD_FAIL | ✗ EXTRACTION_FAIL |
| hotspot | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ BUILD_FAIL |
| hotspot3d | ✓ PASS | ✓ PASS | ✓ PASS |
| kmeans | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| lavamd | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| lud | ✓ PASS | ✓ PASS | ✓ PASS |
| myocyte | ✗ BUILD_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| nn | ✓ PASS | ✓ PASS | ✓ PASS |
| nw | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ BUILD_FAIL |
| particlefilter | ✗ BUILD_FAIL | ✓ PASS | ✗ BUILD_FAIL |
| pathfinder | ✓ PASS | ✓ PASS | ✓ PASS |
| srad | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ RUN_FAIL |
| streamcluster | ✗ BUILD_FAIL | ✓ PASS | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 16 |
| RUN_FAIL | 8 |
| EXTRACTION_FAIL | 1 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **51**
- Passed on first attempt: **21**
- Repaired by retry: **5**

