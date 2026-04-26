# ParBench Evaluation Summary
**Generated:** 2026-04-26 07:23  |  **Total tasks:** 1052

## Pass Rates by Model

| Model | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|------------:|---------------:|
| azure-gpt-5.4 | 267 | 426 | 62.7% | 97 | 35 | 24 | 3 |
| together-qwen-3.5-397b-a17b | 230 | 626 | 36.7% | 245 | 121 | 29 | 1 |

## Pass Rates by Translation Direction

| Direction | PASS | Total | Rate |
|-----------|-----:|------:|-----:|
| cuda-to-omp | 127 | 192 | 66.1% |
| cuda-to-omp_target | 23 | 48 | 47.9% |
| cuda-to-opencl | 42 | 126 | 33.3% |
| omp-to-cuda | 79 | 176 | 44.9% |
| omp-to-omp_target | 20 | 30 | 66.7% |
| omp-to-opencl | 71 | 138 | 51.4% |
| omp_target-to-cuda | 63 | 80 | 78.8% |
| omp_target-to-omp | 29 | 30 | 96.7% |
| opencl-to-cuda | 11 | 114 | 9.7% |
| opencl-to-omp | 32 | 118 | 27.1% |

## Pass Rates by Augmentation Level

| Level | PASS | Total | Rate |
|-------|-----:|------:|-----:|
| L0 | 369 | 852 | 43.3% |
| L1 | 37 | 50 | 74.0% |
| L2 | 32 | 50 | 64.0% |
| L3 | 31 | 50 | 62.0% |
| L4 | 28 | 50 | 56.0% |

> **Scope note (level-invariance claim).** L1–L4 results reflect only kernels that passed L0 (conditional ablation — `derive_l0_passers.py` filter at `:79` uses pass@1-of-any on the canonical L0 cells). Any level-invariance observation here is scoped to the **L0-passer subset** by construction; it is NOT an unconditional statement about augmentation robustness on kernels that fail L0. See `.planning/_archive/phase-02-llm-eval-testing/02-THREATS-TO-VALIDITY.md` §4 and the Bucket D D1 unconditional probe for context.

## pass@1 Metrics (Dual Reporting)

Cells are `(kernel, direction, augment_level, model)` tuples. `of_any` = fraction of cells with ≥1 PASS across all samples. `mean` = average single-draw pass rate across cells (passes / samples, averaged over cells). Both metrics coincide when every cell is at 0 / k or k / k passes; they diverge structurally at any interior rate.

| Level | Cells | pass@1_of_any | pass@1_mean | divergence |
|-------|------:|--------------:|------------:|-----------:|
| L0 | 284 | 52.5% | 43.3% | +0.0915 |
| L1 | 50 | 74.0% | 74.0% | +0.0000 |
| L2 | 50 | 64.0% | 64.0% | +0.0000 |
| L3 | 50 | 62.0% | 62.0% | +0.0000 |
| L4 | 50 | 56.0% | 56.0% | +0.0000 |

## Pass Rates by Translation Complexity

| Complexity Class | PASS | Total | Rate | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL |
|-----------------|-----:|------:|-----:|----------:|--------:|------------:|
| multi_to_multi | 6 | 60 | 10.0% | 38 | 11 | 3 |
| multi_to_single | 98 | 192 | 51.0% | 28 | 65 | 1 |
| single_file | 372 | 636 | 58.5% | 147 | 77 | 40 |
| single_to_multi | 21 | 164 | 12.8% | 129 | 3 | 9 |

### Model × Complexity Cross-Tab

| Complexity Class | azure-gpt-5.4 | together-qwen-3.5-397b-a17b |
|-----------------|---:|---:|
| multi_to_multi | 6/30 (20.0%) | 0/30 (0.0%) |
| multi_to_single | 61/78 (78.2%) | 37/114 (32.5%) |
| single_file | 184/240 (76.7%) | 188/396 (47.5%) |
| single_to_multi | 16/78 (20.5%) | 5/86 (5.8%) |

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
| BUILD_FAIL | 342 |
| RUN_FAIL | 156 |
| VERIFY_FAIL | 53 |
| EXTRACTION_FAIL | 4 |

## Self-Repair (Iterative Retry) Effectiveness

- Tasks with recorded attempts: **1052**
- Passed on first attempt: **497**
- Repaired by retry: **0**

