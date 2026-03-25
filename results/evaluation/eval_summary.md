# ParBench Evaluation Summary
**Generated:** 2026-03-24 19:22  |  **Total tasks:** 68

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-4.1 | 9 | 17 | 52.9% | 4 | 4 | 0 | 0 |
| claude-sonnet-4-6 | 12 | 17 | 70.6% | 2 | 3 | 0 | 0 |
| gemini-2.5-flash-lite | 4 | 17 | 23.5% | 10 | 2 | 0 | 1 |
| groq-llama-3.3-70b-versatile | 5 | 17 | 29.4% | 10 | 1 | 0 | 1 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 30 | 68 | 44.1% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 30 | 68 | 44.1% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 2 | 12 | 16.7% | 8 | 1 | 0 |
| multi_to_single | 21 | 44 | 47.7% | 16 | 6 | 0 |
| single_file | 7 | 12 | 58.3% | 2 | 3 | 0 |

### Model × Complexity Cross-Tab

| Complexity Class | azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|-----------------|---:|---:|---:|---:|
| multi_to_multi | 1/3 (33.3%) | 1/3 (33.3%) | 0/3 (0.0%) | 0/3 (0.0%) |
| multi_to_single | 6/11 (54.5%) | 9/11 (81.8%) | 3/11 (27.3%) | 3/11 (27.3%) |
| single_file | 2/3 (66.7%) | 2/3 (66.7%) | 1/3 (33.3%) | 2/3 (66.7%) |

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

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 26 |
| RUN_FAIL | 10 |
| EXTRACTION_FAIL | 2 |
| VERIFY_FAIL | 0 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **68**
- Passed on first attempt: **24**
- Repaired by retry: **6**

