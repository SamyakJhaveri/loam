# ParBench Evaluation Summary
**Generated:** 2026-04-23 11:21  |  **Total tasks:** 642

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| together-qwen-3.5-397b-a17b | 243 | 642 | 37.9% | 252 | 115 | 31 | 1 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 71 | 120 | 59.2% |
| cuda-to-omp_target | 0 | 24 | 0.0% |
| cuda-to-opencl | 5 | 72 | 6.9% |
| omp-to-cuda | 41 | 104 | 39.4% |
| omp-to-omp_target | 11 | 21 | 52.4% |
| omp-to-opencl | 44 | 94 | 46.8% |
| omp_target-to-cuda | 39 | 56 | 69.6% |
| omp_target-to-omp | 21 | 21 | 100.0% |
| opencl-to-cuda | 0 | 60 | 0.0% |
| opencl-to-omp | 11 | 70 | 15.7% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 104 | 438 | 23.7% |
| L1 | 37 | 51 | 72.5% |
| L2 | 34 | 51 | 66.7% |
| L3 | 34 | 51 | 66.7% |
| L4 | 34 | 51 | 66.7% |

> **Scope note (level-invariance claim).** L1–L4 results reflect only kernels that passed L0 (conditional ablation — `derive_l0_passers.py` filter at `:79` uses pass@1-of-any on the canonical L0 cells). Any level-invariance observation here is scoped to the **L0-passer subset** by construction; it is NOT an unconditional statement about augmentation robustness on kernels that fail L0. See `.planning/_archive/phase-02-llm-eval-testing/02-THREATS-TO-VALIDITY.md` §4 and the Bucket D D1 unconditional probe for context.

## pass@1 Metrics (Dual Reporting)

Cells are `(kernel, direction, augment_level, model)` tuples. `of_any` = fraction of cells with ≥1 PASS across all samples. `mean` = average single-draw pass rate across cells (passes / samples, averaged over cells). Both metrics coincide when every cell is at 0 / k or k / k passes; they diverge structurally at any interior rate.

| Level | Cells | pass@1_of_any | pass@1_mean | divergence |
|-------|------:|--------------:|------------:|-----------:|
| L0 | 146 | 34.9% | 23.7% | +0.1119 |
| L1 | 51 | 72.5% | 72.5% | +0.0000 |
| L2 | 51 | 66.7% | 66.7% | +0.0000 |
| L3 | 51 | 66.7% | 66.7% | +0.0000 |
| L4 | 51 | 66.7% | 66.7% | +0.0000 |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 0 | 30 | 0.0% | 21 | 7 | 2 |
| multi_to_single | 37 | 117 | 31.6% | 25 | 52 | 3 |
| single_file | 200 | 406 | 49.3% | 130 | 56 | 20 |
| single_to_multi | 6 | 89 | 6.7% | 76 | 0 | 6 |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✗ BUILD_FAIL |
| bfs | ✓ PASS |
| bptree | ✗ BUILD_FAIL |
| cfd | ✓ PASS |
| convolution1d | ✗ BUILD_FAIL |
| floydwarshall | ✗ BUILD_FAIL |
| heartwall | ✗ BUILD_FAIL |
| heat2d | ✗ BUILD_FAIL |
| hotspot | ✗ BUILD_FAIL |
| hotspot3d | ✓ PASS |
| iso2dfd | ✗ BUILD_FAIL |
| jacobi | ✗ BUILD_FAIL |
| lavamd | ✗ BUILD_FAIL |
| lud | ✓ PASS |
| md | ✗ BUILD_FAIL |
| mixbench | ✗ BUILD_FAIL |
| myocyte | ✗ BUILD_FAIL |
| nn | ✗ BUILD_FAIL |
| nqueen | ✗ BUILD_FAIL |
| nw | ✗ BUILD_FAIL |
| page-rank | ✗ BUILD_FAIL |
| particlefilter | ✓ PASS |
| pathfinder | ✓ PASS |
| rsbench | ✗ BUILD_FAIL |
| scan | ✗ RUN_FAIL |
| srad | ✓ PASS |
| stencil1d | ✓ PASS |
| streamcluster | ✗ RUN_FAIL |
| xsbench | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 252 |
| RUN_FAIL | 115 |
| VERIFY_FAIL | 31 |
| EXTRACTION_FAIL | 1 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **642**
- Passed on first attempt: **243**
- Repaired by retry: **0**

