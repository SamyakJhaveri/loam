# ParBench Statistical Analysis

**Generated:** 2026-03-31T23:50:25.237985  |  **Records:** 906  |  **Alpha:** 0.05

## 1. Pass Rates with 95% Wilson Score CIs

### By Model
| Model | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| together-qwen-3.5-397b-a17b | 27.7% | [24.9%, 30.7%] | 906 |

### By Direction
| Direction | Rate | 95% CI | n |
|-----------|-----:|-------:|--:|
| cuda-to-omp | 50.0% | [42.1%, 57.9%] | 152 |
| cuda-to-omp_target | 0.0% | [0.0%, 13.8%] | 24 |
| cuda-to-opencl | 13.8% | [9.1%, 20.3%] | 145 |
| omp-to-cuda | 36.8% | [29.6%, 44.8%] | 152 |
| omp-to-opencl | 25.6% | [18.8%, 33.7%] | 129 |
| omp_target-to-cuda | 60.0% | [42.3%, 75.4%] | 30 |
| opencl-to-cuda | 4.1% | [1.9%, 8.7%] | 145 |
| opencl-to-omp | 32.6% | [25.1%, 41.0%] | 129 |

### By Kernel
| Kernel | Rate | 95% CI | n |
|--------|-----:|-------:|--:|
| backprop | 25.0% | [14.9%, 38.8%] | 48 |
| bfs | 41.7% | [28.8%, 55.7%] | 48 |
| bptree | 12.5% | [5.9%, 24.7%] | 48 |
| cfd | 37.5% | [25.2%, 51.6%] | 48 |
| convolution1d | 0.0% | [0.0%, 39.0%] | 6 * |
| dwt2d | 0.0% | [0.0%, 19.4%] | 16 |
| floydwarshall | 75.0% | [46.8%, 91.1%] | 12 |
| gaussian | 0.0% | [0.0%, 19.4%] | 16 |
| heartwall | 0.0% | [0.0%, 7.4%] | 48 |
| heat2d | 75.0% | [46.8%, 91.1%] | 12 |
| hotspot | 50.0% | [36.4%, 63.6%] | 48 |
| hotspot3d | 52.1% | [38.3%, 65.5%] | 48 |
| iso2dfd | 58.3% | [31.9%, 80.7%] | 12 |
| jacobi | 0.0% | [0.0%, 39.0%] | 6 * |
| lavamd | 4.2% | [1.1%, 14.0%] | 48 |
| lud | 39.6% | [27.0%, 53.7%] | 48 |
| md | 16.7% | [3.0%, 56.4%] | 6 * |
| mixbench | 11.1% | [3.1%, 32.8%] | 18 |
| myocyte | 0.0% | [0.0%, 7.4%] | 48 |
| nn | 50.0% | [28.0%, 72.0%] | 16 |
| nqueen | 33.3% | [9.7%, 70.0%] | 6 * |
| nw | 41.7% | [28.8%, 55.7%] | 48 |
| page-rank | 50.0% | [18.8%, 81.2%] | 6 * |
| particlefilter | 47.9% | [34.5%, 61.7%] | 48 |
| pathfinder | 35.4% | [23.4%, 49.6%] | 48 |
| rsbench | 0.0% | [0.0%, 17.6%] | 18 |
| scan | 0.0% | [0.0%, 29.9%] | 9 * |
| srad | 31.2% | [20.0%, 45.3%] | 48 |
| stencil1d | 77.8% | [45.3%, 93.7%] | 9 * |
| streamcluster | 4.2% | [1.1%, 14.0%] | 48 |
| xsbench | 0.0% | [0.0%, 17.6%] | 18 |

### By Augmentation Level
| Level | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| L0 | 22.6% | [19.2%, 26.4%] | 522 |
| L1 | 34.4% | [25.6%, 44.3%] | 96 |
| L2 | 36.5% | [27.5%, 46.4%] | 96 |
| L3 | 37.5% | [28.5%, 47.5%] | 96 |
| L4 | 30.2% | [21.9%, 40.0%] | 96 |

## 3. Augmentation Level Independence (Chi-Squared)

**H0:** Pass rate is independent of augmentation level.
**Correction:** Bonferroni for multiple comparisons.

### By Model
| Model | chi2 | p (corrected) | Cramer's V | Significant? | Low expected? |
|-------|-----:|-------------:|----------:|:------------:|:-------------:|
| together-qwen-3.5-397b-a17b | 9.43 | 0.1023 | 0.249 (small) | No | No |

## 4. Augmentation Trend (Cochran-Armitage, cuda-to-omp)

**H0:** No monotonic trend in pass rate across L0-L4.

| Group | z | p-value | Trend | Significant? |
|-------|--:|--------:|:------|:------------:|
| overall | -0.166 | 0.8684 | decreasing | No |
| together-qwen-3.5-397b-a17b | -0.166 | 0.8684 | decreasing | No |

## 5. Direction Asymmetry (McNemar's Test, L0 only)

| Direction Pair | n paired | Fwd Rate | Rev Rate | Cohen's h | p-value | Significant? |
|----------------|--------:|--------:|--------:|----------:|--------:|:------------:|
| opencl-to-omp vs omp-to-opencl | 18 | 38.9% | 27.8% | 0.236 | 0.7266 | No |
| cuda-to-omp_target vs omp_target-to-cuda | 8 | 0.0% | 62.5% | -1.823 | 0.0625 | No |
| cuda-to-omp vs omp-to-cuda | 24 | 58.3% | 54.2% | 0.084 | 1.0000 | No |
| cuda-to-opencl vs opencl-to-cuda | 20 | 15.0% | 10.0% | 0.152 | 1.0000 | No |

## 6. Augmentation Curves with CIs

### together-qwen-3.5-397b-a17b
| Level | Rate | 95% CI | Pass/Total |
|-------|-----:|-------:|----------:|
| L0 | 22.6% | [19.2%, 26.4%] | 118/522 |
| L1 | 34.4% | [25.6%, 44.3%] | 33/96 |
| L2 | 36.5% | [27.5%, 46.4%] | 35/96 |
| L3 | 37.5% | [28.5%, 47.5%] | 36/96 |
| L4 | 30.2% | [21.9%, 40.0%] | 29/96 |

## 7. Sample Size Adequacy Flags

**7 cells with n < 10** (insufficient for reliable CI):

| Cell | n | Note |
|------|--:|:-----|
| kernel:convolution1d | 6 | n < 10; CI width exceeds 30pp |
| kernel:jacobi | 6 | n < 10; CI width exceeds 30pp |
| kernel:md | 6 | n < 10; CI width exceeds 30pp |
| kernel:nqueen | 6 | n < 10; CI width exceeds 30pp |
| kernel:page-rank | 6 | n < 10; CI width exceeds 30pp |
| kernel:scan | 9 | n < 10; CI width exceeds 30pp |
| kernel:stencil1d | 9 | n < 10; CI width exceeds 30pp |

## 8. Pass@k Estimates

| Task | n | c | pass@1 | pass@3 | pass@10 |
|------|--:|--:|-------:|-------:|--------:|
| ('backprop', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 3 | 1.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('dwt2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('dwt2d', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('gaussian', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('gaussian', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('myocyte', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nn', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nn', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
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
| ('scan', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
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

