# Token Usage Analysis — ParBench Evaluation

**906 results** across 1 models, 31 kernels, 8 directions.
Grand total: **46,099,020 tokens**, estimated cost: **$32.83**.

## Table 1: Per-Model Token Statistics

| Model | N | Pass% | Prompt (mean) | Completion (mean) | tok/s (mean) | Total Cost | Cost/PASS |
|-------|--:|------:|--------------:|------------------:|-------------:|-----------:|----------:|
| Qwen 3.5 397B (Together) | 906 | 27.7% | 40,082 | 10,800 | 119 | $32.83 | $0.0157 |

## Table 2: Per-Kernel Token Statistics (sorted by prompt size)

| Kernel | N | Pass% | Prompt (mean) | Completion (mean) |
|--------|--:|------:|--------------:|------------------:|
| myocyte | 48 | 0.0% | 170,082 | 55,068 |
| heartwall | 48 | 0.0% | 104,230 | 23,971 |
| dwt2d | 16 | 0.0% | 86,592 | 29,475 |
| streamcluster | 48 | 4.2% | 61,367 | 18,155 |
| cfd | 48 | 37.5% | 60,965 | 11,146 |
| bptree | 48 | 12.5% | 52,615 | 11,011 |
| gaussian | 16 | 0.0% | 52,045 | 13,773 |
| particlefilter | 48 | 47.9% | 47,872 | 10,670 |
| xsbench | 18 | 0.0% | 27,583 | 4,092 |
| backprop | 48 | 25.0% | 27,098 | 6,912 |
| srad | 48 | 31.2% | 26,716 | 6,455 |
| rsbench | 18 | 0.0% | 25,961 | 6,622 |
| nw | 48 | 41.7% | 23,359 | 8,714 |
| lavamd | 48 | 4.2% | 23,262 | 4,179 |
| lud | 48 | 39.6% | 22,760 | 5,053 |
| bfs | 48 | 41.7% | 19,108 | 3,239 |
| hotspot3d | 48 | 52.1% | 15,783 | 5,857 |
| hotspot | 48 | 50.0% | 12,866 | 4,590 |
| pathfinder | 48 | 35.4% | 12,146 | 4,173 |
| mixbench | 18 | 11.1% | 8,784 | 3,113 |
| nn | 16 | 50.0% | 8,573 | 4,412 |
| md | 6 | 16.7% | 3,416 | 1,431 |
| iso2dfd | 12 | 58.3% | 2,996 | 2,573 |
| convolution1d | 6 | 0.0% | 2,720 | 2,865 |
| page-rank | 6 | 50.0% | 2,486 | 2,226 |
| nqueen | 6 | 33.3% | 2,446 | 2,369 |
| scan | 9 | 0.0% | 2,320 | 2,673 |
| floydwarshall | 12 | 75.0% | 1,902 | 1,740 |
| heat2d | 12 | 75.0% | 1,774 | 1,628 |
| jacobi | 6 | 0.0% | 1,544 | 2,121 |
| stencil1d | 9 | 77.8% | 1,058 | 1,156 |

## Table 3: Per-Direction Token Statistics

| Direction | N | Pass% | Prompt (mean) | Completion (mean) |
|-----------|--:|------:|--------------:|------------------:|
| cuda-to-omp | 152 | 50.0% | 27,323 | 8,664 |
| omp-to-cuda | 152 | 36.8% | 33,454 | 11,971 |
| cuda-to-opencl | 145 | 13.8% | 51,160 | 11,300 |
| opencl-to-cuda | 145 | 4.1% | 55,566 | 15,911 |
| omp-to-opencl | 129 | 25.6% | 42,481 | 7,348 |
| opencl-to-omp | 129 | 32.6% | 46,475 | 12,729 |
| omp_target-to-cuda | 30 | 60.0% | 2,171 | 2,043 |
| cuda-to-omp_target | 24 | 0.0% | 2,530 | 2,133 |

## Table 4: Per-Augmentation-Level Statistics

| Level | N | Pass% | Prompt (mean) | Completion (mean) |
|-------|--:|------:|--------------:|------------------:|
| L0 | 522 | 22.6% | 23,062 | 6,600 |
| L1 | 96 | 34.4% | 62,351 | 16,037 |
| L2 | 96 | 36.5% | 61,877 | 15,486 |
| L3 | 96 | 37.5% | 64,534 | 17,637 |
| L4 | 96 | 30.2% | 64,114 | 16,873 |

## Table 5: Cost Analysis

| Model | Total Cost | Cost on PASS | Cost on FAIL | Cost/PASS | Cost/Task |
|-------|----------:|-----------:|-----------:|----------:|----------:|
| Qwen 3.5 397B (Together) | $32.83 | $3.93 | $28.91 | $0.0157 | $0.0362 |
| **TOTAL** | **$32.83** | | | | |

## Correlations

- **Kernel-level (prompt)**: Spearman(mean prompt tokens, pass rate) = **-0.4573**
- **Result-level (prompt)**: Mean prompt tokens for PASS = **17,052**, for FAIL = **48,907**
- **Result-level (completion)**: Spearman(completion tokens, pass) = **-0.1032**; Mean completion for PASS = **4,750**, for FAIL = **13,118**

