# ParBench Evaluation Summary
**Generated:** 2026-04-30 12:01  |  **Total tasks:** 1874

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-5.3-codex | 267 | 426 | 62.7% | 107 | 29 | 23 | 0 |
| azure-gpt-5.4 | 621 | 822 | 75.5% | 123 | 43 | 32 | 3 |
| together-qwen-3.5-397b-a17b | 230 | 626 | 36.7% | 245 | 121 | 29 | 1 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 261 | 352 | 74.2% |
| cuda-to-omp_target | 77 | 104 | 74.0% |
| cuda-to-opencl | 123 | 235 | 52.3% |
| omp-to-cuda | 173 | 308 | 56.2% |
| omp-to-omp_target | 39 | 51 | 76.5% |
| omp-to-opencl | 160 | 245 | 65.3% |
| omp_target-to-cuda | 119 | 136 | 87.5% |
| omp_target-to-omp | 50 | 51 | 98.0% |
| opencl-to-cuda | 37 | 191 | 19.4% |
| opencl-to-omp | 79 | 201 | 39.3% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 636 | 1278 | 49.8% |
| L1 | 125 | 149 | 83.9% |
| L2 | 122 | 149 | 81.9% |
| L3 | 117 | 149 | 78.5% |
| L4 | 118 | 149 | 79.2% |

> **Scope note (level-invariance claim).** L1–L4 results reflect only kernels that passed L0 (conditional ablation — `derive_l0_passers.py` filter at `:79` uses pass@1-of-any on the canonical L0 cells). Any level-invariance observation here is scoped to the **L0-passer subset** by construction; it is NOT an unconditional statement about augmentation robustness on kernels that fail L0. See `.planning/_archive/phase-02-llm-eval-testing/02-THREATS-TO-VALIDITY.md` §4 and the Bucket D D1 unconditional probe for context.

## pass@1 Metrics (Dual Reporting)

Cells are `(kernel, direction, augment_level, model)` tuples. `of_any` = fraction of cells with ≥1 PASS across all samples. `mean` = average single-draw pass rate across cells (passes / samples, averaged over cells). Both metrics coincide when every cell is at 0 / k or k / k passes; they diverge structurally at any interior rate.

| Level | Cells | pass@1_of_any | pass@1_mean | divergence |
|-------|------:|--------------:|------------:|-----------:|
| L0 | 426 | 57.8% | 49.8% | +0.0798 |
| L1 | 149 | 83.9% | 83.9% | +0.0000 |
| L2 | 149 | 81.9% | 81.9% | +0.0000 |
| L3 | 149 | 78.5% | 78.5% | +0.0000 |
| L4 | 149 | 79.2% | 79.2% | +0.0000 |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 22 | 102 | 21.6% | 62 | 13 | 3 |
| multi_to_single | 233 | 358 | 65.1% | 43 | 80 | 2 |
| single_file | 807 | 1136 | 71.0% | 172 | 95 | 62 |
| single_to_multi | 56 | 278 | 20.1% | 198 | 5 | 17 |

### Model × Complexity Cross-Tab

| Complexity Class | azure-gpt-5.3-codex | azure-gpt-5.4 | together-qwen-3.5-397b-a17b |
|-----------------|---:|---:|---:|
| multi_to_multi | 7/30 (23.3%) | 15/42 (35.7%) | 0/30 (0.0%) |
| multi_to_single | 55/78 (70.5%) | 141/166 (84.9%) | 37/114 (32.5%) |
| single_file | 192/240 (80.0%) | 427/500 (85.4%) | 188/396 (47.5%) |
| single_to_multi | 13/78 (16.7%) | 38/114 (33.3%) | 5/86 (5.8%) |

## Kernel × Model Matrix (cuda→omp, L0)

| Kernel | azure-gpt-5.3-codex | azure-gpt-5.4 | together-qwen-3.5-397b-a17b |
|--------|---|---|---|
| backprop | ✗ BUILD_FAIL | ✓ PASS | ✗ BUILD_FAIL |
| bfs | ✓ PASS | ✓ PASS | ✓ PASS |
| bptree | ✗ BUILD_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| cfd | ✓ PASS | ✓ PASS | ✓ PASS |
| convolution1d | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| floydwarshall | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| heartwall | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| heat2d | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| hotspot | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| hotspot3d | ✓ PASS | ✓ PASS | ✓ PASS |
| iso2dfd | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| jacobi | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| lavamd | ✗ VERIFY_FAIL | ✓ PASS | ✗ BUILD_FAIL |
| lud | ✓ PASS | ✓ PASS | ✓ PASS |
| md | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| mixbench | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| myocyte | ✗ BUILD_FAIL | ✗ EXTRACTION_FAIL | ✗ BUILD_FAIL |
| nn | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| nqueen | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| nw | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| page-rank | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |
| particlefilter | ✓ PASS | ✓ PASS | ✓ PASS |
| pathfinder | ✓ PASS | ✓ PASS | ✓ PASS |
| rsbench | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| scan | ✓ PASS | ✓ PASS | ✗ RUN_FAIL |
| srad | ✓ PASS | ✓ PASS | ✓ PASS |
| stencil1d | ✓ PASS | ✓ PASS | ✓ PASS |
| streamcluster | ✓ PASS | ✓ PASS | ✗ RUN_FAIL |
| xsbench | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |

## Failure Taxonomy

| Status | Count |
|--------|------:|
| BUILD_FAIL | 475 |
| RUN_FAIL | 193 |
| VERIFY_FAIL | 84 |
| EXTRACTION_FAIL | 4 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **1874**
- Passed on first attempt: **1118**
- Repaired by retry: **0**

