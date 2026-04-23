# Token Usage Analysis — ParBench Evaluation

**642 results** across 1 models, 31 kernels, 10 directions.
Grand total (from result JSONs): **11,836,173 tokens** (7,606,944 input + 4,229,229 output), estimated cost: **$19.79**.

### Actual Billing (Together AI, Mar 27 – Apr 2 2026)

- **Input tokens:** 96,241,738 (96.2M)
- **Output tokens:** 24,324,474 (24.3M)
- **Total tokens:** 120,566,212 (120.6M)
- **Total cost:** $145.37
- **Requests:** ~4,600

Result JSONs capture ~46% of billed tokens. The gap reflects system prompt overhead, HTTP-level retries, and JSON-mode formatting tokens billed by the provider.

## Table 1: Per-Model Token Statistics

| Model | N | Pass% | Prompt (mean) | Completion (mean) | tok/s (mean) | Total Cost | Cost/PASS |
|-------|--:|------:|--------------:|------------------:|-------------:|-----------:|----------:|
| Qwen 3.5 397B (Together) | 642 | 37.9% | 11,849 | 6,588 | 132 | $19.79 | $0.0244 |

## Table 2: Per-Kernel Token Statistics (sorted by prompt size)

| Kernel | N | Pass% | Prompt (mean) | Completion (mean) |
|--------|--:|------:|--------------:|------------------:|
| myocyte | 18 | 0.0% | 45,667 | 20,750 |
| heartwall | 18 | 0.0% | 37,232 | 13,027 |
| cfd | 22 | 31.8% | 28,710 | 8,013 |
| xsbench | 22 | 4.5% | 27,738 | 6,137 |
| dwt2d | 6 | 0.0% | 27,408 | 11,110 |
| rsbench | 18 | 0.0% | 25,959 | 6,029 |
| particlefilter | 26 | 34.6% | 22,718 | 8,082 |
| streamcluster | 22 | 4.5% | 22,065 | 7,604 |
| bptree | 18 | 0.0% | 20,297 | 6,516 |
| gaussian | 6 | 0.0% | 15,472 | 4,942 |
| backprop | 22 | 18.2% | 11,504 | 3,453 |
| lud | 30 | 46.7% | 11,051 | 6,500 |
| srad | 26 | 34.6% | 10,949 | 6,170 |
| mixbench | 22 | 13.6% | 9,221 | 5,742 |
| lavamd | 18 | 0.0% | 8,945 | 4,618 |
| bfs | 34 | 50.0% | 8,596 | 4,415 |
| nw | 30 | 40.0% | 8,355 | 7,937 |
| hotspot3d | 34 | 55.9% | 6,315 | 4,941 |
| hotspot | 30 | 50.0% | 6,139 | 7,014 |
| pathfinder | 30 | 33.3% | 3,733 | 6,572 |
| md | 10 | 50.0% | 3,376 | 5,604 |
| iso2dfd | 38 | 84.2% | 2,928 | 6,022 |
| convolution1d | 10 | 20.0% | 2,770 | 6,336 |
| nn | 6 | 0.0% | 2,722 | 4,876 |
| page-rank | 10 | 60.0% | 2,420 | 5,109 |
| nqueen | 10 | 60.0% | 2,420 | 6,071 |
| scan | 6 | 0.0% | 2,348 | 6,894 |
| floydwarshall | 38 | 81.6% | 1,876 | 4,048 |
| heat2d | 38 | 76.3% | 1,786 | 3,942 |
| jacobi | 10 | 10.0% | 1,423 | 6,476 |
| stencil1d | 14 | 71.4% | 1,074 | 7,629 |

## Table 3: Per-Direction Token Statistics

| Direction | N | Pass% | Prompt (mean) | Completion (mean) |
|-----------|--:|------:|--------------:|------------------:|
| cuda-to-omp | 120 | 59.2% | 9,562 | 7,472 |
| omp-to-cuda | 104 | 39.4% | 7,634 | 7,648 |
| omp-to-opencl | 94 | 46.8% | 15,950 | 4,484 |
| cuda-to-opencl | 72 | 6.9% | 18,412 | 4,707 |
| opencl-to-omp | 70 | 15.7% | 19,357 | 8,856 |
| opencl-to-cuda | 60 | 0.0% | 20,072 | 9,204 |
| omp_target-to-cuda | 56 | 69.6% | 2,315 | 5,737 |
| cuda-to-omp_target | 24 | 0.0% | 2,528 | 5,309 |
| omp-to-omp_target | 21 | 52.4% | 2,185 | 3,713 |
| omp_target-to-omp | 21 | 100.0% | 2,151 | 3,712 |

## Table 4: Per-Augmentation-Level Statistics

| Level | N | Pass% | Prompt (mean) | Completion (mean) |
|-------|--:|------:|--------------:|------------------:|
| L0 | 438 | 23.7% | 13,997 | 7,012 |
| L1 | 51 | 72.5% | 7,193 | 5,682 |
| L2 | 51 | 66.7% | 7,193 | 5,585 |
| L3 | 51 | 66.7% | 7,203 | 5,760 |
| L4 | 51 | 66.7% | 7,356 | 5,678 |

## Table 5: Cost Analysis

| Model | Total Cost | Cost on PASS | Cost on FAIL | Cost/PASS | Cost/Task |
|-------|----------:|-----------:|-----------:|----------:|----------:|
| Qwen 3.5 397B (Together) | $19.79 | $5.92 | $13.87 | $0.0244 | $0.0308 |
| **TOTAL** | **$19.79** | | | | |

## Correlations

- **Kernel-level (prompt)**: Spearman(mean prompt tokens, pass rate) = **-0.6065**
- **Result-level (prompt)**: Mean prompt tokens for PASS = **5,889**, for FAIL = **15,478**
- **Result-level (completion)**: Spearman(completion tokens, pass) = **0.0185**; Mean completion for PASS = **5,786**, for FAIL = **7,076**

