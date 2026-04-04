# ParBench Statistical Analysis

**Generated:** 2026-04-04T13:35:14.047922  |  **Records:** 1136  |  **Alpha:** 0.05

## 1. Pass Rates with 95% Wilson Score CIs

### By Model
| Model | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| together-qwen-3.5-397b-a17b | 31.3% | [28.7%, 34.1%] | 1136 |

### By Direction
| Direction | Rate | 95% CI | n |
|-----------|-----:|-------:|--:|
| cuda-to-omp | 52.6% | [45.6%, 59.6%] | 192 |
| cuda-to-omp_target | 10.9% | [5.4%, 20.9%] | 64 |
| cuda-to-opencl | 17.5% | [12.4%, 24.1%] | 160 |
| omp-to-cuda | 41.1% | [34.4%, 48.2%] | 192 |
| omp-to-opencl | 25.0% | [18.6%, 32.7%] | 144 |
| omp_target-to-cuda | 71.2% | [60.5%, 80.0%] | 80 |
| opencl-to-cuda | 3.8% | [1.7%, 7.9%] | 160 |
| opencl-to-omp | 29.2% | [22.4%, 37.0%] | 144 |

### By Kernel
| Kernel | Rate | 95% CI | n |
|--------|-----:|-------:|--:|
| backprop | 39.6% | [27.0%, 53.7%] | 48 |
| bfs | 41.7% | [28.8%, 55.7%] | 48 |
| bptree | 12.5% | [5.9%, 24.7%] | 48 |
| cfd | 37.5% | [25.2%, 51.6%] | 48 |
| convolution1d | 0.0% | [0.0%, 19.4%] | 16 |
| dwt2d | 0.0% | [0.0%, 19.4%] | 16 |
| floydwarshall | 78.1% | [61.3%, 89.0%] | 32 |
| gaussian | 0.0% | [0.0%, 19.4%] | 16 |
| heartwall | 0.0% | [0.0%, 7.4%] | 48 |
| heat2d | 75.0% | [57.9%, 86.8%] | 32 |
| hotspot | 50.0% | [36.4%, 63.6%] | 48 |
| hotspot3d | 52.1% | [38.3%, 65.5%] | 48 |
| iso2dfd | 68.8% | [51.4%, 82.0%] | 32 |
| jacobi | 37.5% | [18.5%, 61.4%] | 16 |
| lavamd | 4.2% | [1.1%, 14.0%] | 48 |
| lud | 39.6% | [27.0%, 53.7%] | 48 |
| md | 43.8% | [23.1%, 66.8%] | 16 |
| mixbench | 20.8% | [11.7%, 34.3%] | 48 |
| myocyte | 0.0% | [0.0%, 7.4%] | 48 |
| nn | 50.0% | [28.0%, 72.0%] | 16 |
| nqueen | 50.0% | [28.0%, 72.0%] | 16 |
| nw | 41.7% | [28.8%, 55.7%] | 48 |
| page-rank | 56.2% | [33.2%, 76.9%] | 16 |
| particlefilter | 47.9% | [34.5%, 61.7%] | 48 |
| pathfinder | 35.4% | [23.4%, 49.6%] | 48 |
| rsbench | 0.0% | [0.0%, 7.4%] | 48 |
| scan | 20.8% | [9.2%, 40.5%] | 24 |
| srad | 31.2% | [20.0%, 45.3%] | 48 |
| stencil1d | 91.7% | [74.2%, 97.7%] | 24 |
| streamcluster | 4.2% | [1.1%, 14.0%] | 48 |
| xsbench | 0.0% | [0.0%, 7.4%] | 48 |

### By Augmentation Level
| Level | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| L0 | 24.8% | [21.4%, 28.5%] | 568 |
| L1 | 37.3% | [29.8%, 45.5%] | 142 |
| L2 | 40.1% | [32.4%, 48.4%] | 142 |
| L3 | 39.4% | [31.8%, 47.6%] | 142 |
| L4 | 34.5% | [27.2%, 42.6%] | 142 |

## 3. Augmentation Level Independence (Chi-Squared)

**H0:** Pass rate is independent of augmentation level.
**Correction:** Bonferroni for multiple comparisons.

### By Model
| Model | chi2 | p (corrected) | Cramer's V | Significant? | Low expected? |
|-------|-----:|-------------:|----------:|:------------:|:-------------:|
| together-qwen-3.5-397b-a17b | 10.34 | 0.0701 | 0.232 (small) | No | No |

## 4. Augmentation Trend (Cochran-Armitage, cuda-to-omp)

**H0:** No monotonic trend in pass rate across L0-L4.

| Group | z | p-value | Trend | Significant? |
|-------|--:|--------:|:------|:------------:|
| overall | -0.000 | 1.0000 | decreasing | No |
| together-qwen-3.5-397b-a17b | -0.000 | 1.0000 | decreasing | No |

## 5. Direction Asymmetry (McNemar's Test, L0 only)

| Direction Pair | n paired | Fwd Rate | Rev Rate | Cohen's h | p-value | Significant? |
|----------------|--------:|--------:|--------:|----------:|--------:|:------------:|
| cuda-to-omp_target vs omp_target-to-cuda | 8 | 12.5% | 75.0% | -1.372 | 0.0625 | No |
| opencl-to-cuda vs cuda-to-opencl | 20 | 10.0% | 20.0% | -0.284 | 0.6875 | No |
| cuda-to-omp vs omp-to-cuda | 24 | 66.7% | 58.3% | 0.172 | 0.6875 | No |
| opencl-to-omp vs omp-to-opencl | 18 | 38.9% | 33.3% | 0.116 | 1.0000 | No |

## 6. Augmentation Curves with CIs

### together-qwen-3.5-397b-a17b
| Level | Rate | 95% CI | Pass/Total |
|-------|-----:|-------:|----------:|
| L0 | 24.8% | [21.4%, 28.5%] | 141/568 |
| L1 | 37.3% | [29.8%, 45.5%] | 53/142 |
| L2 | 40.1% | [32.4%, 48.4%] | 57/142 |
| L3 | 39.4% | [31.8%, 47.6%] | 56/142 |
| L4 | 34.5% | [27.2%, 42.6%] | 49/142 |

## 8. Pass@k Estimates

| Task | n | c | pass@1 | pass@3 | pass@10 |
|------|--:|--:|-------:|-------:|--------:|
| ('backprop', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 3 | 1.0 | --- | --- |
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

