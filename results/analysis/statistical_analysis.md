# ParBench Statistical Analysis

**Generated:** 2026-04-23T10:48:30.398492  |  **Records:** 642  |  **Alpha:** 0.05

## 1. Pass Rates with 95% Wilson Score CIs

### By Model
| Model | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| together-qwen-3.5-397b-a17b | 37.9% | [34.2%, 41.7%] | 642 |

### By Direction
| Direction | Rate | 95% CI | n |
|-----------|-----:|-------:|--:|
| cuda-to-omp | 59.2% | [50.2%, 67.5%] | 120 |
| cuda-to-omp_target | 0.0% | [0.0%, 13.8%] | 24 |
| cuda-to-opencl | 6.9% | [3.0%, 15.2%] | 72 |
| omp-to-cuda | 39.4% | [30.6%, 49.0%] | 104 |
| omp-to-omp_target | 52.4% | [32.4%, 71.7%] | 21 |
| omp-to-opencl | 46.8% | [37.0%, 56.8%] | 94 |
| omp_target-to-cuda | 69.6% | [56.7%, 80.1%] | 56 |
| omp_target-to-omp | 100.0% | [84.5%, 100.0%] | 21 |
| opencl-to-cuda | 0.0% | [0.0%, 6.0%] | 60 |
| opencl-to-omp | 15.7% | [9.0%, 26.0%] | 70 |

### By Kernel
| Kernel | Rate | 95% CI | n |
|--------|-----:|-------:|--:|
| backprop | 18.2% | [7.3%, 38.5%] | 22 |
| bfs | 50.0% | [34.1%, 65.9%] | 34 |
| bptree | 0.0% | [0.0%, 17.6%] | 18 |
| cfd | 31.8% | [16.4%, 52.7%] | 22 |
| convolution1d | 20.0% | [5.7%, 51.0%] | 10 |
| dwt2d | 0.0% | [0.0%, 39.0%] | 6 * |
| floydwarshall | 81.6% | [66.6%, 90.8%] | 38 |
| gaussian | 0.0% | [0.0%, 39.0%] | 6 * |
| heartwall | 0.0% | [0.0%, 17.6%] | 18 |
| heat2d | 76.3% | [60.8%, 87.0%] | 38 |
| hotspot | 50.0% | [33.1%, 66.8%] | 30 |
| hotspot3d | 55.9% | [39.5%, 71.1%] | 34 |
| iso2dfd | 84.2% | [69.6%, 92.6%] | 38 |
| jacobi | 10.0% | [1.8%, 40.4%] | 10 |
| lavamd | 0.0% | [0.0%, 17.6%] | 18 |
| lud | 46.7% | [30.2%, 63.9%] | 30 |
| md | 50.0% | [23.7%, 76.3%] | 10 |
| mixbench | 13.6% | [4.8%, 33.3%] | 22 |
| myocyte | 0.0% | [0.0%, 17.6%] | 18 |
| nn | 0.0% | [0.0%, 39.0%] | 6 * |
| nqueen | 60.0% | [31.3%, 83.2%] | 10 |
| nw | 40.0% | [24.6%, 57.7%] | 30 |
| page-rank | 60.0% | [31.3%, 83.2%] | 10 |
| particlefilter | 34.6% | [19.4%, 53.8%] | 26 |
| pathfinder | 33.3% | [19.2%, 51.2%] | 30 |
| rsbench | 0.0% | [0.0%, 17.6%] | 18 |
| scan | 0.0% | [0.0%, 39.0%] | 6 * |
| srad | 34.6% | [19.4%, 53.8%] | 26 |
| stencil1d | 71.4% | [45.4%, 88.3%] | 14 |
| streamcluster | 4.5% | [0.8%, 21.8%] | 22 |
| xsbench | 4.5% | [0.8%, 21.8%] | 22 |

### By Augmentation Level
| Level | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| L0 | 23.7% | [20.0%, 28.0%] | 438 |
| L1 | 72.5% | [59.1%, 82.9%] | 51 |
| L2 | 66.7% | [53.0%, 78.0%] | 51 |
| L3 | 66.7% | [53.0%, 78.0%] | 51 |
| L4 | 66.7% | [53.0%, 78.0%] | 51 |

## 3. Augmentation Level Independence (Chi-Squared)

**H0:** Pass rate is independent of augmentation level.
**Correction:** Bonferroni for multiple comparisons.

### By Model
| Model | chi2 | p (corrected) | Cramer's V | Significant? | Low expected? |
|-------|-----:|-------------:|----------:|:------------:|:-------------:|
| together-qwen-3.5-397b-a17b | 28.31 | 0.0000 | 0.486 (medium) | Yes | Yes |

## 4. Augmentation Trend (Cochran-Armitage, cuda-to-omp)

**H0:** No monotonic trend in pass rate across L0-L4.

| Group | z | p-value | Trend | Significant? |
|-------|--:|--------:|:------|:------------:|
| overall | -0.781 | 0.4350 | decreasing | No |
| together-qwen-3.5-397b-a17b | -0.781 | 0.4350 | decreasing | No |

## 5. Direction Asymmetry (McNemar's Test, L0 only)

| Direction Pair | n paired | Fwd Rate | Rev Rate | Cohen's h | p-value | Significant? |
|----------------|--------:|--------:|--------:|----------:|--------:|:------------:|
| opencl-to-cuda vs cuda-to-opencl | 20 | 0.0% | 5.0% | -0.451 | 1.0000 | No |
| cuda-to-omp vs omp-to-cuda | 24 | 45.8% | 25.0% | 0.440 | 0.1797 | No |
| omp_target-to-omp vs omp-to-omp_target | 3 | 100.0% | 66.7% | 1.231 | 1.0000 | No |
| opencl-to-omp vs omp-to-opencl | 18 | 16.7% | 38.9% | -0.506 | 0.2891 | No |
| cuda-to-omp_target vs omp_target-to-cuda | 8 | 0.0% | 75.0% | -2.094 | 0.0312 | No |

## 6. Augmentation Curves with CIs

### together-qwen-3.5-397b-a17b
| Level | Rate | 95% CI | Pass/Total |
|-------|-----:|-------:|----------:|
| L0 | 23.7% | [20.0%, 28.0%] | 104/438 |
| L1 | 72.5% | [59.1%, 82.9%] | 37/51 |
| L2 | 66.7% | [53.0%, 78.0%] | 34/51 |
| L3 | 66.7% | [53.0%, 78.0%] | 34/51 |
| L4 | 66.7% | [53.0%, 78.0%] | 34/51 |

## 7. Sample Size Adequacy Flags

**4 cells with n < 10** (insufficient for reliable CI):

| Cell | n | Note |
|------|--:|:-----|
| kernel:dwt2d | 6 | n < 10; CI width exceeds 30pp |
| kernel:gaussian | 6 | n < 10; CI width exceeds 30pp |
| kernel:nn | 6 | n < 10; CI width exceeds 30pp |
| kernel:scan | 6 | n < 10; CI width exceeds 30pp |

## 8. Pass@k Estimates

| Task | n | c | pass@1 | pass@3 | pass@10 |
|------|--:|--:|-------:|-------:|--------:|
| ('backprop', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('backprop', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bfs', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('bptree', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('cfd', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('convolution1d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('dwt2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('dwt2d', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('floydwarshall', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('gaussian', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('gaussian', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heartwall', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('heat2d', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 3 | 1.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('hotspot3d', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp-to-omp_target', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('iso2dfd', 'together-qwen-3.5-397b-a17b', 'omp_target-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('jacobi', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lavamd', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 3 | 1.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('lud', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('md', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('mixbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
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
| ('nn', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nqueen', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('nw', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp_target', 0) | 3 | 0 | 0.0 | --- | --- |
| ('page-rank', 'together-qwen-3.5-397b-a17b', 'omp_target-to-cuda', 0) | 3 | 3 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 3 | 1.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('particlefilter', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('pathfinder', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 2 | 0.6667 | --- | --- |
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
| ('srad', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('srad', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('stencil1d', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 2 | 0.6667 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'opencl-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('streamcluster', 'together-qwen-3.5-397b-a17b', 'opencl-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-omp', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'cuda-to-opencl', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-cuda', 0) | 3 | 0 | 0.0 | --- | --- |
| ('xsbench', 'together-qwen-3.5-397b-a17b', 'omp-to-opencl', 0) | 3 | 1 | 0.3333 | --- | --- |
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

