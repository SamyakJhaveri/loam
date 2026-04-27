# ParBench Evaluation Summary
**Generated:** 2026-04-27 01:45  |  **Total tasks:** 1448

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-5.4 | 621 | 822 | 75.5% | 123 | 43 | 32 | 3 |
| together-qwen-3.5-397b-a17b | 230 | 626 | 36.7% | 245 | 121 | 29 | 1 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 206 | 280 | 73.6% |
| cuda-to-omp_target | 53 | 80 | 66.2% |
| cuda-to-opencl | 90 | 178 | 50.6% |
| omp-to-cuda | 133 | 236 | 56.4% |
| omp-to-omp_target | 30 | 42 | 71.4% |
| omp-to-opencl | 118 | 194 | 60.8% |
| omp_target-to-cuda | 95 | 112 | 84.8% |
| omp_target-to-omp | 41 | 42 | 97.6% |
| opencl-to-cuda | 26 | 134 | 19.4% |
| opencl-to-omp | 59 | 150 | 39.3% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 369 | 852 | 43.3% |
| L1 | 125 | 149 | 83.9% |
| L2 | 122 | 149 | 81.9% |
| L3 | 117 | 149 | 78.5% |
| L4 | 118 | 149 | 79.2% |

> **Scope note (level-invariance claim).** L1–L4 results reflect only kernels that passed L0 (conditional ablation — `derive_l0_passers.py` filter at `:79` uses pass@1-of-any on the canonical L0 cells). Any level-invariance observation here is scoped to the **L0-passer subset** by construction; it is NOT an unconditional statement about augmentation robustness on kernels that fail L0. See `.planning/_archive/phase-02-llm-eval-testing/02-THREATS-TO-VALIDITY.md` §4 and the Bucket D D1 unconditional probe for context.

## pass@1 Metrics (Dual Reporting)

Cells are `(kernel, direction, augment_level, model)` tuples. `of_any` = fraction of cells with ≥1 PASS across all samples. `mean` = average single-draw pass rate across cells (passes / samples, averaged over cells). Both metrics coincide when every cell is at 0 / k or k / k passes; they diverge structurally at any interior rate.

| Level | Cells | pass@1_of_any | pass@1_mean | divergence |
|-------|------:|--------------:|------------:|-----------:|
| L0 | 284 | 52.5% | 43.3% | +0.0915 |
| L1 | 149 | 83.9% | 83.9% | +0.0000 |
| L2 | 149 | 81.9% | 81.9% | +0.0000 |
| L3 | 149 | 78.5% | 78.5% | +0.0000 |
| L4 | 149 | 79.2% | 79.2% | +0.0000 |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 15 | 72 | 20.8% | 41 | 11 | 3 |
| multi_to_single | 178 | 280 | 63.6% | 34 | 67 | 1 |
| single_file | 615 | 896 | 68.6% | 154 | 83 | 44 |
| single_to_multi | 43 | 200 | 21.5% | 139 | 3 | 13 |

### Model × Complexity Cross-Tab

| Complexity Class | azure-gpt-5.4 | together-qwen-3.5-397b-a17b |
|-----------------|---:|---:|
| multi_to_multi | 15/42 (35.7%) | 0/30 (0.0%) |
| multi_to_single | 141/166 (84.9%) | 37/114 (32.5%) |
| single_file | 427/500 (85.4%) | 188/396 (47.5%) |
| single_to_multi | 38/114 (33.3%) | 5/86 (5.8%) |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | azure-gpt-5.4 | together-qwen-3.5-397b-a17b |
|--------|---|---|
| backprop | ✓ PASS | ✗ BUILD_FAIL |
| bfs | ✓ PASS | ✓ PASS |
| bptree | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| cfd | ✓ PASS | ✓ PASS |
| convolution1d | ✓ PASS | ✗ BUILD_FAIL |
| floydwarshall | ✓ PASS | ✗ BUILD_FAIL |
| heartwall | ✓ PASS | ✗ BUILD_FAIL |
| heat2d | ✓ PASS | ✗ BUILD_FAIL |
| hotspot | ✓ PASS | ✗ BUILD_FAIL |
| hotspot3d | ✓ PASS | ✓ PASS |
| iso2dfd | ✓ PASS | ✗ BUILD_FAIL |
| jacobi | ✓ PASS | ✗ BUILD_FAIL |
| lavamd | ✓ PASS | ✗ BUILD_FAIL |
| lud | ✓ PASS | ✓ PASS |
| md | ✓ PASS | ✗ BUILD_FAIL |
| mixbench | ✓ PASS | ✗ BUILD_FAIL |
| myocyte | ✗ EXTRACTION_FAIL | ✗ BUILD_FAIL |
| nn | ✓ PASS | ✗ BUILD_FAIL |
| nqueen | ✓ PASS | ✗ BUILD_FAIL |
| nw | ✓ PASS | ✗ BUILD_FAIL |
| page-rank | ✓ PASS | ✗ BUILD_FAIL |
| particlefilter | ✓ PASS | ✓ PASS |
| pathfinder | ✓ PASS | ✓ PASS |
| rsbench | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| scan | ✓ PASS | ✗ RUN_FAIL |
| srad | ✓ PASS | ✓ PASS |
| stencil1d | ✓ PASS | ✓ PASS |
| streamcluster | ✓ PASS | ✗ RUN_FAIL |
| xsbench | ✗ BUILD_FAIL | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 368 |
| RUN_FAIL | 164 |
| VERIFY_FAIL | 61 |
| EXTRACTION_FAIL | 4 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **1448**
- Passed on first attempt: **851**
- Repaired by retry: **0**

