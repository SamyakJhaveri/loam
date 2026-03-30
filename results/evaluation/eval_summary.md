# ParBench Evaluation Summary
**Generated:** 2026-03-30 05:06  |  **Total tasks:** 188

> **CAVEAT (2026-03-30):** These numbers were generated from the pre-fix pipeline. A
> source-args bug caused cross-API translations to run with the *target* spec's arguments
> instead of the *source* spec's, producing systematic false negatives (43 Qwen tasks,
> 8 Gemini tasks). Pass rates below are UNDERESTIMATES. Campaigns must be re-run with
> the fixed pipeline before these numbers can be used in the paper. See
> `docs/plans/paper_update_summary.md` for full details.

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| together-qwen-3.5-397b-a17b | 45 | 188 | 23.9% | 61 | 51 | 31 | 0 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 31 | 80 | 38.8% |
| cuda-to-opencl | 0 | 28 | 0.0% |
| omp-to-cuda | 14 | 80 | 17.5% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 10 | 38 | 26.3% |
| L1 | 7 | 38 | 18.4% |
| L2 | 11 | 38 | 28.9% |
| L3 | 10 | 37 | 27.0% |
| L4 | 7 | 37 | 18.9% |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 1 | 25 | 4.0% | 15 | 7 | 2 |
| multi_to_single | 18 | 60 | 30.0% | 14 | 17 | 11 |
| single_file | 20 | 58 | 34.5% | 5 | 18 | 15 |
| single_to_multi | 6 | 45 | 13.3% | 27 | 9 | 3 |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✓ PASS |
| bfs | ✗ VERIFY_FAIL |
| bptree | ✗ BUILD_FAIL |
| cfd | ✓ PASS |
| heartwall | ✗ BUILD_FAIL |
| hotspot | ✗ RUN_FAIL |
| hotspot3d | ✓ PASS |
| lavamd | ✓ PASS |
| lud | ✓ PASS |
| myocyte | ✗ BUILD_FAIL |
| nn | ✓ PASS |
| nw | ✗ RUN_FAIL |
| particlefilter | ✓ PASS |
| pathfinder | ✗ VERIFY_FAIL |
| srad | ✗ RUN_FAIL |
| streamcluster | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 61 |
| RUN_FAIL | 51 |
| VERIFY_FAIL | 31 |
| EXTRACTION_FAIL | 0 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **188**
- Passed on first attempt: **14**
- Repaired by retry: **31**

