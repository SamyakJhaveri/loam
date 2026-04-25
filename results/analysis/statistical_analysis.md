# ParBench Statistical Analysis

**Generated:** 2026-04-24T22:02:39.313537  |  **Records:** 626  |  **Alpha:** 0.05

## 1. Pass Rates with 95% Wilson Score CIs

### By Model
| Model | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| together-qwen-3.5-397b-a17b | 36.7% | [33.1%, 40.6%] | 626 |

### By Direction
| Direction | Rate | 95% CI | n |
|-----------|-----:|-------:|--:|
| cuda-to-omp | 55.8% | [46.9%, 64.4%] | 120 |
| cuda-to-omp_target | 0.0% | [0.0%, 13.8%] | 24 |
| cuda-to-opencl | 11.6% | [6.0%, 21.2%] | 69 |
| omp-to-cuda | 37.5% | [28.8%, 47.1%] | 104 |
| omp-to-omp_target | 52.4% | [32.4%, 71.7%] | 21 |
| omp-to-opencl | 39.1% | [29.5%, 49.6%] | 87 |
| omp_target-to-cuda | 71.4% | [58.5%, 81.6%] | 56 |
| omp_target-to-omp | 95.2% | [77.3%, 99.2%] | 21 |
| opencl-to-cuda | 0.0% | [0.0%, 6.3%] | 57 |
| opencl-to-omp | 16.4% | [9.4%, 27.1%] | 67 |

### By Kernel
| Kernel | Rate | 95% CI | n |
|--------|-----:|-------:|--:|
| backprop | 0.0% | [0.0%, 39.0%] | 6 * |
| bfs | 44.1% | [28.9%, 60.6%] | 34 |
| bptree | 0.0% | [0.0%, 17.6%] | 18 |
| cfd | 27.3% | [13.2%, 48.1%] | 22 |
| convolution1d | 20.0% | [5.7%, 51.0%] | 10 |
| dwt2d | 0.0% | [0.0%, 39.0%] | 6 * |
| floydwarshall | 76.3% | [60.8%, 87.0%] | 38 |
| gaussian | 0.0% | [0.0%, 39.0%] | 6 * |
| heartwall | 0.0% | [0.0%, 17.6%] | 18 |
| heat2d | 76.3% | [60.8%, 87.0%] | 38 |
| hotspot | 46.7% | [30.2%, 63.9%] | 30 |
| hotspot3d | 58.8% | [42.2%, 73.6%] | 34 |
| iso2dfd | 84.2% | [69.6%, 92.6%] | 38 |
| jacobi | 30.0% | [10.8%, 60.3%] | 10 |
| lavamd | 0.0% | [0.0%, 17.6%] | 18 |
| lud | 46.7% | [30.2%, 63.9%] | 30 |
| md | 40.0% | [16.8%, 68.7%] | 10 |
| mixbench | 9.1% | [2.5%, 27.8%] | 22 |
| myocyte | 0.0% | [0.0%, 17.6%] | 18 |
| nn | 0.0% | [0.0%, 39.0%] | 6 * |
| nqueen | 60.0% | [31.3%, 83.2%] | 10 |
| nw | 36.7% | [21.9%, 54.5%] | 30 |
| page-rank | 60.0% | [31.3%, 83.2%] | 10 |
| particlefilter | 34.6% | [19.4%, 53.8%] | 26 |
| pathfinder | 26.7% | [14.2%, 44.5%] | 30 |
| rsbench | 0.0% | [0.0%, 17.6%] | 18 |
| scan | 0.0% | [0.0%, 39.0%] | 6 * |
| srad | 34.6% | [19.4%, 53.8%] | 26 |
| stencil1d | 64.3% | [38.8%, 83.7%] | 14 |
| streamcluster | 4.5% | [0.8%, 21.8%] | 22 |
| xsbench | 4.5% | [0.8%, 21.8%] | 22 |

### By Augmentation Level
| Level | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| L0 | 23.9% | [20.1%, 28.2%] | 426 |
| L1 | 74.0% | [60.5%, 84.1%] | 50 |
| L2 | 64.0% | [50.1%, 75.9%] | 50 |
| L3 | 62.0% | [48.1%, 74.1%] | 50 |
| L4 | 56.0% | [42.3%, 68.8%] | 50 |

## 3. Augmentation Level Independence (Chi-Squared)

**H0:** Pass rate is independent of augmentation level.
**Correction:** Bonferroni for multiple comparisons.

### By Model
| Model | chi2 | p (corrected) | Cramer's V | Significant? | Low expected? |
|-------|-----:|-------------:|----------:|:------------:|:-------------:|
| together-qwen-3.5-397b-a17b | 18.00 | 0.0025 | 0.387 (medium) | Yes | No |

## 5. Direction Asymmetry (McNemar's Test, L0 only)

| Direction Pair | n paired | Fwd Rate | Rev Rate | Cohen's h | p-value | Significant? |
|----------------|--------:|--------:|--------:|----------:|--------:|:------------:|
| omp-to-opencl vs opencl-to-omp | 17 | 41.2% | 17.6% | 0.526 | 0.2891 | No |
| cuda-to-omp vs omp-to-cuda | 24 | 45.8% | 25.0% | 0.440 | 0.1797 | No |
| omp-to-omp_target vs omp_target-to-omp | 3 | 66.7% | 100.0% | -1.231 | 1.0000 | No |
| omp_target-to-cuda vs cuda-to-omp_target | 8 | 75.0% | 0.0% | 2.094 | 0.0312 | No |
| cuda-to-opencl vs opencl-to-cuda | 19 | 5.3% | 0.0% | 0.463 | 1.0000 | No |

## 6. Augmentation Curves with CIs

### together-qwen-3.5-397b-a17b
| Level | Rate | 95% CI | Pass/Total |
|-------|-----:|-------:|----------:|
| L0 | 23.9% | [20.1%, 28.2%] | 102/426 |
| L1 | 74.0% | [60.5%, 84.1%] | 37/50 |
| L2 | 64.0% | [50.1%, 75.9%] | 32/50 |
| L3 | 62.0% | [48.1%, 74.1%] | 31/50 |
| L4 | 56.0% | [42.3%, 68.8%] | 28/50 |

## 7. Sample Size Adequacy Flags

**5 cells with n < 10** (insufficient for reliable CI):

| Cell | n | Note |
|------|--:|:-----|
| kernel:backprop | 6 | n < 10; CI width exceeds 30pp |
| kernel:dwt2d | 6 | n < 10; CI width exceeds 30pp |
| kernel:gaussian | 6 | n < 10; CI width exceeds 30pp |
| kernel:nn | 6 | n < 10; CI width exceeds 30pp |
| kernel:scan | 6 | n < 10; CI width exceeds 30pp |

## 8. Pass@k Estimates

| Task | n | c | pass@1 | pass@3 | pass@10 |
|------|--:|--:|-------:|-------:|--------:|
| ('backprop', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 1) | 1 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 2) | 1 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 3) | 1 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 4) | 1 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 3) | 1 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 4) | 1 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 1) | 1 | 1 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 2) | 1 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 3) | 1 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 4) | 1 | 1 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 1) | 1 | 0 | 0.0 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 3) | 1 | 0 | 0.0 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 4) | 1 | 0 | 0.0 | --- | --- |
| ('dwt2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('dwt2d', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 4) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 1) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 2) | 1 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 3) | 1 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 4) | 1 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 4) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 3) | 1 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('gaussian', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('gaussian', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 4) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 1) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 2) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 3) | 1 | 0 | 0.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 4) | 1 | 0 | 0.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 4) | 1 | 0 | 0.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 1) | 1 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 2) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 3) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 4) | 1 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 4) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 3 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 1) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 2) | 1 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 3) | 1 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 4) | 1 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 1) | 1 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 2) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 3) | 1 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 4) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 1) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 2) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 3) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 4) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 1) | 1 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 2) | 1 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 4) | 1 | 0 | 0.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 1) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 2) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 3) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 4) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 4) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 2) | 1 | 0 | 0.0 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 3) | 1 | 0 | 0.0 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 4) | 1 | 1 | 1.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 3 | 1.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 1) | 1 | 1 | 1.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 2) | 1 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 3) | 1 | 1 | 1.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 4) | 1 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 2) | 1 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 4) | 1 | 0 | 0.0 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 2) | 1 | 0 | 0.0 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 4) | 1 | 1 | 1.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 1) | 1 | 1 | 1.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 2) | 1 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 3) | 1 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 4) | 1 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nn', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nn', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 4) | 1 | 1 | 1.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 1) | 1 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 2) | 1 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 3) | 1 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 4) | 1 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 1) | 1 | 1 | 1.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 2) | 1 | 1 | 1.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 3) | 1 | 1 | 1.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 4) | 1 | 1 | 1.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 4) | 1 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 1) | 1 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 2) | 1 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 4) | 1 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 1) | 1 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 2) | 1 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 3) | 1 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 4) | 1 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 1) | 1 | 1 | 1.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 2) | 1 | 1 | 1.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 3) | 1 | 1 | 1.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 4) | 1 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('rsbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('rsbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('rsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('rsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('rsbench', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('rsbench', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('scan', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('scan', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 1 | 1.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 1 | 1.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 1) | 1 | 1 | 1.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 2) | 1 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 3) | 1 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 4) | 1 | 0 | 0.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 1) | 1 | 0 | 0.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 2) | 1 | 0 | 0.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 3) | 1 | 1 | 1.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 4) | 1 | 0 | 0.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 1) | 1 | 1 | 1.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 2) | 1 | 1 | 1.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 3) | 1 | 1 | 1.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 4) | 1 | 1 | 1.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 1) | 1 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 2) | 1 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 3) | 1 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 4) | 1 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 1) | 1 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 2) | 1 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 3) | 1 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 4) | 1 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |

---

## Methodology Notes

- **Wilson score intervals** preferred over Wald (normal approximation) for binary outcomes: valid for small n and extreme proportions.
- **Fisher's exact test** used for pairwise model comparisons (exact p-values, valid at any sample size).
- **Bonferroni correction** applied to all families of tests to control FWER.
- **Cochran-Armitage trend** uses ordinal structure of augmentation levels (more powerful than chi-squared for detecting monotonic trends).
- **McNemar's exact** used for direction asymmetry (paired binary data, exact binomial when discordant pairs < 25).
- **Cohen's h** thresholds: <0.2 small, 0.2-0.8 medium, >=0.8 large.
- **Cramer's V** thresholds depend on df* (see Cohen 1988).
- Cells with n < 10 flagged as insufficient for reliable inference.

