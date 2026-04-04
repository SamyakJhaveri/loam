# Token Usage Analysis — ParBench Evaluation

**1136 results** across 1 models, 31 kernels, 8 directions.
Grand total: **55,241,141 tokens**, estimated cost: **$39.03**.

## Table 1: Per-Model Token Statistics

| Model | N | Pass% | Prompt (mean) | Completion (mean) | tok/s (mean) | Total Cost | Cost/PASS |
|-------|--:|------:|--------------:|------------------:|-------------:|-----------:|----------:|
| Qwen 3.5 397B (Together) | 1136 | 31.3% | 38,581 | 10,046 | 111 | $39.03 | $0.0133 |

## Table 2: Per-Kernel Token Statistics (sorted by prompt size)

| Kernel | N | Pass% | Prompt (mean) | Completion (mean) |
|--------|--:|------:|--------------:|------------------:|
| myocyte | 48 | 0.0% | 170,082 | 55,068 |
| heartwall | 48 | 0.0% | 104,230 | 23,971 |
| dwt2d | 16 | 0.0% | 86,592 | 29,475 |
| xsbench | 48 | 0.0% | 71,614 | 11,723 |
| rsbench | 48 | 0.0% | 63,597 | 10,980 |
| streamcluster | 48 | 4.2% | 61,367 | 18,155 |
| cfd | 48 | 37.5% | 60,965 | 11,146 |
| bptree | 48 | 12.5% | 52,615 | 11,011 |
| gaussian | 16 | 0.0% | 52,045 | 13,773 |
| particlefilter | 48 | 47.9% | 47,872 | 10,670 |
| backprop | 48 | 39.6% | 27,098 | 6,912 |
| srad | 48 | 31.2% | 26,716 | 6,455 |
| nw | 48 | 41.7% | 23,359 | 8,714 |
| lavamd | 48 | 4.2% | 23,262 | 4,179 |
| mixbench | 48 | 20.8% | 23,231 | 5,012 |
| lud | 48 | 39.6% | 22,760 | 5,053 |
| bfs | 48 | 41.7% | 19,108 | 3,239 |
| hotspot3d | 48 | 52.1% | 15,783 | 5,857 |
| hotspot | 48 | 50.0% | 12,866 | 4,590 |
| pathfinder | 48 | 35.4% | 12,146 | 4,173 |
| convolution1d | 16 | 0.0% | 11,290 | 5,944 |
| nn | 16 | 50.0% | 8,573 | 4,412 |
| scan | 24 | 20.8% | 8,214 | 5,083 |
| md | 16 | 43.8% | 7,374 | 2,430 |
| nqueen | 16 | 50.0% | 7,010 | 4,180 |
| iso2dfd | 32 | 68.8% | 6,414 | 3,972 |
| page-rank | 16 | 56.2% | 5,762 | 3,299 |
| jacobi | 16 | 37.5% | 5,103 | 3,010 |
| heat2d | 32 | 75.0% | 3,179 | 2,166 |
| floydwarshall | 32 | 78.1% | 3,131 | 2,207 |
| stencil1d | 24 | 91.7% | 1,164 | 1,154 |

## Table 3: Per-Direction Token Statistics

| Direction | N | Pass% | Prompt (mean) | Completion (mean) |
|-----------|--:|------:|--------------:|------------------:|
| cuda-to-omp | 192 | 52.6% | 27,441 | 8,447 |
| omp-to-cuda | 192 | 41.1% | 32,324 | 11,084 |
| cuda-to-opencl | 160 | 17.5% | 53,946 | 11,607 |
| opencl-to-cuda | 160 | 3.8% | 57,164 | 15,284 |
| omp-to-opencl | 144 | 25.0% | 45,792 | 7,548 |
| opencl-to-omp | 144 | 29.2% | 48,800 | 12,194 |
| omp_target-to-cuda | 80 | 71.2% | 4,720 | 2,996 |
| cuda-to-omp_target | 64 | 10.9% | 9,018 | 4,339 |

## Table 4: Per-Augmentation-Level Statistics

| Level | N | Pass% | Prompt (mean) | Completion (mean) |
|-------|--:|------:|--------------:|------------------:|
| L0 | 568 | 24.8% | 23,652 | 6,579 |
| L1 | 142 | 37.3% | 52,658 | 12,974 |
| L2 | 142 | 40.1% | 52,468 | 12,666 |
| L3 | 142 | 39.4% | 54,800 | 14,467 |
| L4 | 142 | 34.5% | 54,116 | 13,947 |

## Table 5: Cost Analysis

| Model | Total Cost | Cost on PASS | Cost on FAIL | Cost/PASS | Cost/Task |
|-------|----------:|-----------:|-----------:|----------:|----------:|
| Qwen 3.5 397B (Together) | $39.03 | $4.73 | $34.31 | $0.0133 | $0.0344 |
| **TOTAL** | **$39.03** | | | | |

## Correlations

- **Kernel-level (prompt)**: Spearman(mean prompt tokens, pass rate) = **-0.7516**
- **Result-level (prompt)**: Mean prompt tokens for PASS = **14,166**, for FAIL = **49,725**
- **Result-level (completion)**: Spearman(completion tokens, pass) = **-0.1838**; Mean completion for PASS = **4,130**, for FAIL = **12,746**

