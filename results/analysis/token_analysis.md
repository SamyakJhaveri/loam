# Token Usage Analysis — ParBench Evaluation

**500 results** across 4 models, 18 kernels, 12 directions.
Grand total: **27,844,892 tokens**, estimated cost: **$55.69**.

## Table 1: Per-Model Token Statistics

| Model | N | Pass% | Prompt (mean) | Completion (mean) | tok/s (mean) | Total Cost | Cost/PASS |
|-------|--:|------:|--------------:|------------------:|-------------:|-----------:|----------:|
| Claude Sonnet 4 | 161 | 70.2% | 38,084 | 12,136 | 90 | $47.70 | $0.2090 |
| Gemini 2.5 Flash-Lite | 161 | 10.6% | 53,888 | 17,860 | 451 | $1.51 | $0.0022 |
| Groq Llama 3.3 70B | 161 | 18.6% | 39,787 | 7,626 | 316 | $4.75 | $0.0115 |
| Azure GPT-4.1 | 17 | 52.9% | 28,181 | 5,619 | 108 | $1.72 | $0.0504 |

## Table 2: Per-Kernel Token Statistics (sorted by prompt size)

| Kernel | N | Pass% | Prompt (mean) | Completion (mean) |
|--------|--:|------:|--------------:|------------------:|
| myocyte | 19 | 10.5% | 148,840 | 27,909 |
| heartwall | 19 | 0.0% | 104,693 | 26,830 |
| kmeans | 16 | 43.8% | 70,974 | 4,871 |
| xsbench | 180 | 26.7% | 58,248 | 17,373 |
| cfd | 19 | 36.8% | 53,978 | 10,854 |
| bptree | 19 | 36.8% | 35,832 | 9,063 |
| streamcluster | 19 | 26.3% | 30,850 | 9,005 |
| particlefilter | 19 | 42.1% | 29,021 | 11,098 |
| lavamd | 19 | 63.2% | 19,872 | 1,974 |
| nw | 19 | 0.0% | 19,866 | 15,339 |
| lud | 19 | 52.6% | 19,471 | 4,599 |
| backprop | 19 | 57.9% | 14,970 | 7,275 |
| srad | 19 | 0.0% | 14,330 | 7,276 |
| hotspot | 19 | 0.0% | 11,873 | 7,308 |
| nn | 19 | 68.4% | 8,357 | 4,448 |
| bfs | 19 | 63.2% | 7,349 | 4,752 |
| hotspot3d | 19 | 68.4% | 5,953 | 4,553 |
| pathfinder | 19 | 73.7% | 4,852 | 2,855 |

## Table 3: Per-Direction Token Statistics

| Direction | N | Pass% | Prompt (mean) | Completion (mean) |
|-----------|--:|------:|--------------:|------------------:|
| cuda-to-omp | 287 | 38.3% | 37,740 | 9,800 |
| omp-to-cuda | 63 | 27.0% | 33,731 | 13,239 |
| cuda-to-omp_target | 15 | 33.3% | 65,333 | 20,106 |
| cuda-to-opencl | 15 | 33.3% | 75,505 | 9,768 |
| omp-to-omp_target | 15 | 26.7% | 53,025 | 23,606 |
| omp-to-opencl | 15 | 33.3% | 65,581 | 4,904 |
| omp_target-to-cuda | 15 | 40.0% | 40,416 | 18,299 |
| omp_target-to-omp | 15 | 13.3% | 47,452 | 23,677 |
| omp_target-to-opencl | 15 | 33.3% | 58,136 | 8,086 |
| opencl-to-cuda | 15 | 33.3% | 56,834 | 20,644 |
| opencl-to-omp | 15 | 0.0% | 63,275 | 21,923 |
| opencl-to-omp_target | 15 | 33.3% | 56,830 | 16,056 |

## Table 4: Per-Augmentation-Level Statistics

| Level | N | Pass% | Prompt (mean) | Completion (mean) |
|-------|--:|------:|--------------:|------------------:|
| L0 | 152 | 34.2% | 38,531 | 11,502 |
| L1 | 87 | 36.8% | 45,066 | 12,759 |
| L2 | 87 | 35.6% | 44,644 | 12,198 |
| L3 | 87 | 33.3% | 46,804 | 13,103 |
| L4 | 87 | 28.7% | 45,503 | 12,564 |

## Table 5: Cost Analysis

| Model | Total Cost | Cost on PASS | Cost on FAIL | Cost/PASS | Cost/Task |
|-------|----------:|-----------:|-----------:|----------:|----------:|
| Claude Sonnet 4 | $47.70 | $23.62 | $24.08 | $0.2090 | $0.2963 |
| Gemini 2.5 Flash-Lite | $1.51 | $0.04 | $1.48 | $0.0022 | $0.0094 |
| Groq Llama 3.3 70B | $4.75 | $0.34 | $4.41 | $0.0115 | $0.0295 |
| Azure GPT-4.1 | $1.72 | $0.45 | $1.27 | $0.0504 | $0.1013 |
| **TOTAL** | **$55.69** | | | | |

## Correlations

- **Kernel-level (prompt)**: Spearman(mean prompt tokens, pass rate) = **-0.5501**
- **Result-level (prompt)**: Mean prompt tokens for PASS = **22,912**, for FAIL = **53,837**
- **Result-level (completion)**: Spearman(completion tokens, pass) = **-0.4779**; Mean completion for PASS = **6,838**, for FAIL = **15,097**

