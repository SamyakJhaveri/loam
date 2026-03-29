# ParBench Statistical Analysis

**Generated:** 2026-03-28T15:54:49.618640  |  **Records:** 562  |  **Alpha:** 0.05

## 1. Pass Rates with 95% Wilson Score CIs

### By Model
| Model | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| claude-sonnet-4-6 | 54.3% | [47.1%, 61.2%] | 188 |
| gemini-2.5-flash-lite | 8.6% | [5.3%, 13.5%] | 187 |
| groq-llama-3.3-70b-versatile | 10.2% | [6.6%, 15.3%] | 187 |

### By Direction
| Direction | Rate | 95% CI | n |
|-----------|-----:|-------:|--:|
| cuda-to-omp | 24.3% | [19.5%, 29.9%] | 255 |
| cuda-to-omp_target | 26.7% | [10.9%, 51.9%] | 15 |
| cuda-to-opencl | 30.3% | [20.5%, 42.2%] | 66 |
| omp-to-cuda | 14.3% | [7.7%, 25.0%] | 63 |
| omp-to-omp_target | 0.0% | [0.0%, 20.4%] | 15 |
| omp-to-opencl | 37.9% | [26.6%, 50.8%] | 58 |
| omp_target-to-cuda | 26.7% | [10.9%, 51.9%] | 15 |
| omp_target-to-omp | 20.0% | [7.0%, 45.2%] | 15 |
| omp_target-to-opencl | 26.7% | [10.9%, 51.9%] | 15 |
| opencl-to-cuda | 33.3% | [15.2%, 58.3%] | 15 |
| opencl-to-omp | 0.0% | [0.0%, 20.4%] | 15 |
| opencl-to-omp_target | 26.7% | [10.9%, 51.9%] | 15 |

### By Kernel
| Kernel | Rate | 95% CI | n |
|--------|-----:|-------:|--:|
| backprop | 62.5% | [42.7%, 78.8%] | 24 |
| bfs | 16.7% | [6.7%, 35.9%] | 24 |
| bptree | 58.3% | [38.8%, 75.5%] | 24 |
| cfd | 20.8% | [9.2%, 40.5%] | 24 |
| dwt2d | 66.7% | [20.8%, 93.8%] | 3 * |
| gaussian | 0.0% | [0.0%, 56.1%] | 3 * |
| heartwall | 0.0% | [0.0%, 13.8%] | 24 |
| hotspot | 12.5% | [4.3%, 31.0%] | 24 |
| hotspot3d | 62.5% | [42.7%, 78.8%] | 24 |
| lavamd | 33.3% | [18.0%, 53.3%] | 24 |
| lud | 41.7% | [24.5%, 61.2%] | 24 |
| myocyte | 4.2% | [0.7%, 20.2%] | 24 |
| nn | 16.7% | [5.8%, 39.2%] | 18 |
| nw | 12.5% | [4.3%, 31.0%] | 24 |
| particlefilter | 41.7% | [24.5%, 61.2%] | 24 |
| pathfinder | 20.8% | [9.2%, 40.5%] | 24 |
| srad | 16.7% | [6.7%, 35.9%] | 24 |
| streamcluster | 4.5% | [0.8%, 21.8%] | 22 |
| xsbench | 18.9% | [13.8%, 25.2%] | 180 |

### By Augmentation Level
| Level | Rate | 95% CI | n |
|-------|-----:|-------:|--:|
| L0 | 27.9% | [22.4%, 34.1%] | 226 |
| L1 | 23.8% | [16.0%, 33.9%] | 84 |
| L2 | 25.0% | [17.0%, 35.2%] | 84 |
| L3 | 20.2% | [13.0%, 30.0%] | 84 |
| L4 | 19.1% | [12.1%, 28.7%] | 84 |

## 2. Model Comparison

**Omnibus chi-squared:** chi2(2) = 136.93, p = 0.00e+00
**Cramer's V:** 0.494 (medium)

### Pairwise Comparisons (Fisher's exact, Bonferroni-corrected)
| Pair | OR [95% CI] | p (corrected) | Cohen's h | Effect |
|------|-------------|-------------:|----------:|:------:|
| claude-sonnet-4-6 vs gemini-2.5-flash-lite | 12.68 [7.05, 22.80] | 0.0000 ** | 1.062 | large |
| claude-sonnet-4-6 vs groq-llama-3.3-70b-versatile | 10.49 [6.02, 18.26] | 0.0000 ** | 1.007 | large |
| gemini-2.5-flash-lite vs groq-llama-3.3-70b-versatile | 0.83 [0.41, 1.66] | 1.0000 | -0.055 | small |

## 3. Augmentation Level Independence (Chi-Squared)

**H0:** Pass rate is independent of augmentation level.
**Correction:** Bonferroni for multiple comparisons.

### By Model
| Model | chi2 | p (corrected) | Cramer's V | Significant? | Low expected? |
|-------|-----:|-------------:|----------:|:------------:|:-------------:|
| claude-sonnet-4-6 | 0.66 | 1.0000 | 0.088 (negligible) | No | No |
| gemini-2.5-flash-lite | 3.55 | 1.0000 | 0.204 (small) | No | Yes |
| groq-llama-3.3-70b-versatile | 1.13 | 1.0000 | 0.116 (small) | No | Yes |

## 4. Augmentation Trend (Cochran-Armitage, cuda-to-omp)

**H0:** No monotonic trend in pass rate across L0-L4.

| Group | z | p-value | Trend | Significant? |
|-------|--:|--------:|:------|:------------:|
| claude-sonnet-4-6 | -0.153 | 0.8780 | decreasing | No |
| gemini-2.5-flash-lite | -1.599 | 0.1097 | decreasing | No |
| groq-llama-3.3-70b-versatile | -0.952 | 0.3410 | decreasing | No |
| overall | -1.239 | 0.2155 | decreasing | No |

## 5. Direction Asymmetry (McNemar's Test, L0 only)

| Direction Pair | n paired | Fwd Rate | Rev Rate | Cohen's h | p-value | Significant? |
|----------------|--------:|--------:|--------:|----------:|--------:|:------------:|
| opencl-to-omp_target vs omp_target-to-opencl | 3 | 33.3% | 33.3% | 0.000 | 1.0000 | No |
| omp-to-opencl vs opencl-to-omp | 3 | 33.3% | 0.0% | 1.231 | 1.0000 | No |
| omp_target-to-omp vs omp-to-omp_target | 3 | 0.0% | 0.0% | 0.000 | 1.0000 | No |
| cuda-to-opencl vs opencl-to-cuda | 3 | 33.3% | 33.3% | 0.000 | 1.0000 | No |
| omp_target-to-cuda vs cuda-to-omp_target | 3 | 33.3% | 33.3% | 0.000 | 1.0000 | No |
| omp-to-cuda vs cuda-to-omp | 51 | 17.6% | 29.4% | -0.279 | 0.1796 | No |

## 6. Augmentation Curves with CIs

### claude-sonnet-4-6
| Level | Rate | 95% CI | Pass/Total |
|-------|-----:|-------:|----------:|
| L0 | 56.6% | [45.4%, 67.1%] | 43/76 |
| L1 | 53.6% | [35.8%, 70.5%] | 15/28 |
| L2 | 57.1% | [39.1%, 73.5%] | 16/28 |
| L3 | 46.4% | [29.5%, 64.2%] | 13/28 |
| L4 | 53.6% | [35.8%, 70.5%] | 15/28 |

### gemini-2.5-flash-lite
| Level | Rate | 95% CI | Pass/Total |
|-------|-----:|-------:|----------:|
| L0 | 10.7% | [5.5%, 19.7%] | 8/75 |
| L1 | 10.7% | [3.7%, 27.2%] | 3/28 |
| L2 | 10.7% | [3.7%, 27.2%] | 3/28 |
| L3 | 7.1% | [2.0%, 22.7%] | 2/28 |
| L4 | 0.0% | [0.0%, 12.1%] | 0/28 |

### groq-llama-3.3-70b-versatile
| Level | Rate | 95% CI | Pass/Total |
|-------|-----:|-------:|----------:|
| L0 | 16.0% | [9.4%, 25.9%] | 12/75 |
| L1 | 7.1% | [2.0%, 22.7%] | 2/28 |
| L2 | 7.1% | [2.0%, 22.7%] | 2/28 |
| L3 | 7.1% | [2.0%, 22.7%] | 2/28 |
| L4 | 3.6% | [0.6%, 17.7%] | 1/28 |

## 7. Sample Size Adequacy Flags

**26 cells with n < 10** (insufficient for reliable CI):

| Cell | n | Note |
|------|--:|:-----|
| kernel:dwt2d | 3 | n < 10; CI width exceeds 30pp |
| kernel:gaussian | 3 | n < 10; CI width exceeds 30pp |
| model_x_dir:claude-sonnet-4-6/cuda-to-omp_target | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:claude-sonnet-4-6/omp-to-omp_target | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:claude-sonnet-4-6/omp_target-to-cuda | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:claude-sonnet-4-6/omp_target-to-omp | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:claude-sonnet-4-6/omp_target-to-opencl | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:claude-sonnet-4-6/opencl-to-cuda | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:claude-sonnet-4-6/opencl-to-omp | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:claude-sonnet-4-6/opencl-to-omp_target | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:gemini-2.5-flash-lite/cuda-to-omp_target | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:gemini-2.5-flash-lite/omp-to-omp_target | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:gemini-2.5-flash-lite/omp_target-to-cuda | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:gemini-2.5-flash-lite/omp_target-to-omp | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:gemini-2.5-flash-lite/omp_target-to-opencl | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:gemini-2.5-flash-lite/opencl-to-cuda | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:gemini-2.5-flash-lite/opencl-to-omp | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:gemini-2.5-flash-lite/opencl-to-omp_target | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:groq-llama-3.3-70b-versatile/cuda-to-omp_target | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:groq-llama-3.3-70b-versatile/omp-to-omp_target | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:groq-llama-3.3-70b-versatile/omp_target-to-cuda | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:groq-llama-3.3-70b-versatile/omp_target-to-omp | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:groq-llama-3.3-70b-versatile/omp_target-to-opencl | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:groq-llama-3.3-70b-versatile/opencl-to-cuda | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:groq-llama-3.3-70b-versatile/opencl-to-omp | 5 | n < 10; CI width exceeds 30pp |
| model_x_dir:groq-llama-3.3-70b-versatile/opencl-to-omp_target | 5 | n < 10; CI width exceeds 30pp |

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

