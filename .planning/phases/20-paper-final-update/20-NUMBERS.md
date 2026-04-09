# Phase 20 Reference Numbers

Generated from freshly regenerated analysis files (2026-04-09) after adding 32 XSBench GPT result files.
Phase 20 executor: use these values (NOT 19-NUMBERS.md) to update paper.tex, overleaf.tex, appendices.tex.

**Data source change:** 910 GPT files (Phase 19) -> 942 GPT files (Phase 20). All numbers below supersede 19-NUMBERS.md.

---

## Section 1: GPT-4.1 mini Overall Stats

- **total_tasks**: 577  (`paper_data_gpt41mini.json > primary_campaign > overall > total`)
- **pass**: 177  (`paper_data_gpt41mini.json > primary_campaign > overall > pass`)
- **pass_rate**: 0.3068 (30.7%)  (`paper_data_gpt41mini.json > primary_campaign > overall > pass_rate`)
- **ci_lower**: 0.2705 (27.1%)  (`paper_data_gpt41mini.json > primary_campaign > overall > ci_lower`)
- **ci_upper**: 0.3456 (34.6%)  (`paper_data_gpt41mini.json > primary_campaign > overall > ci_upper`)
- **BUILD_FAIL**: 267  (`paper_data_gpt41mini.json > primary_campaign > overall > by_status > BUILD_FAIL`)
- **RUN_FAIL**: 54  (`paper_data_gpt41mini.json > primary_campaign > overall > by_status > RUN_FAIL`)
- **VERIFY_FAIL**: 79  (`paper_data_gpt41mini.json > primary_campaign > overall > by_status > VERIFY_FAIL`)
- **PASS**: 177  (`paper_data_gpt41mini.json > primary_campaign > overall > by_status > PASS`)
- **file_counts.total_on_disk**: 942  (`paper_data_gpt41mini.json > file_counts > total_on_disk`)
- **file_counts.excluded_known_fail**: 97  (`paper_data_gpt41mini.json > file_counts > excluded_known_fail`)
- **file_counts.primary_campaign**: 577  (`paper_data_gpt41mini.json > file_counts > primary_campaign`)
- **file_counts.passk_campaign**: 268  (`paper_data_gpt41mini.json > file_counts > passk_campaign`)

### Derived percentages (computed from above):
- BUILD_FAIL %: 267/577 = 46.3%
- RUN_FAIL %: 54/577 = 9.4%
- VERIFY_FAIL %: 79/577 = 13.7%

---

## Section 2: Cross-Model Comparison

- **chi_squared**: 7.8336  (`cross_model_comparison.json > overall > chi_squared > chi2`)
- **p_value**: 0.005128  (`cross_model_comparison.json > overall > chi_squared > p_value`)
- **cohens_h**: 0.1607  (`cross_model_comparison.json > overall > cohens_h`)
- **effect_size**: negligible  (`cross_model_comparison.json > overall > effect_size`)
- **gpt_rate**: 0.3068  (`cross_model_comparison.json > overall > gpt > rate`)
- **gpt_pass**: 177  (`cross_model_comparison.json > overall > gpt > pass`)
- **gpt_total**: 577  (`cross_model_comparison.json > overall > gpt > total`)
- **qwen_rate**: 0.3831  (`cross_model_comparison.json > overall > qwen > rate`)
- **qwen_pass**: 272  (`cross_model_comparison.json > overall > qwen > pass`)
- **qwen_total**: 710  (`cross_model_comparison.json > overall > qwen > total`)
- **common_directions**: 7  (`cross_model_comparison.json > common_directions` -- list of 7 direction strings)
- **missing_directions**: `{"azure-gpt-4.1-mini": ["cuda-to-omp_target"]}`  (`cross_model_comparison.json > missing_directions`)
- **total_common_kernels**: 30  (`cross_model_comparison.json > per_kernel_matrix > total_common_kernels`)

---

## Section 3: Per-Direction GPT Rates

| Direction | Total | Pass | Rate | CI Lower | CI Upper | JSON Key Path |
|-----------|-------|------|------|----------|----------|---------------|
| cuda-to-omp | 85 | 48 | 56.5% | 45.9% | 66.5% | `paper_data_gpt41mini.json > primary_campaign > by_direction > cuda-to-omp` |
| cuda-to-opencl | 90 | 30 | 33.3% | 24.4% | 43.6% | `paper_data_gpt41mini.json > primary_campaign > by_direction > cuda-to-opencl` |
| omp-to-cuda | 107 | 16 | 14.9% | 9.4% | 22.9% | `paper_data_gpt41mini.json > primary_campaign > by_direction > omp-to-cuda` |
| omp-to-opencl | 80 | 30 | 37.5% | 27.7% | 48.4% | `paper_data_gpt41mini.json > primary_campaign > by_direction > omp-to-opencl` |
| omp_target-to-cuda | 50 | 15 | 30.0% | 19.1% | 43.8% | `paper_data_gpt41mini.json > primary_campaign > by_direction > omp_target-to-cuda` |
| opencl-to-cuda | 85 | 1 | 1.2% | 0.2% | 6.4% | `paper_data_gpt41mini.json > primary_campaign > by_direction > opencl-to-cuda` |
| opencl-to-omp | 80 | 37 | 46.2% | 35.8% | 57.1% | `paper_data_gpt41mini.json > primary_campaign > by_direction > opencl-to-omp` |

---

## Section 4: Per-Direction Cross-Model

| Direction | Qwen Rate | GPT Rate | Cohen's h | Effect Size | JSON Key Path |
|-----------|-----------|----------|-----------|-------------|---------------|
| cuda-to-omp | 0.6417 | 0.5647 | 0.1576 | negligible | `cross_model_comparison.json > per_direction > cuda-to-omp` |
| cuda-to-opencl | 0.2000 | 0.3333 | -0.3036 | small | `cross_model_comparison.json > per_direction > cuda-to-opencl` |
| omp-to-cuda | 0.5250 | 0.1495 | 0.8268 | large | `cross_model_comparison.json > per_direction > omp-to-cuda` |
| omp-to-opencl | 0.2778 | 0.3750 | -0.2078 | small | `cross_model_comparison.json > per_direction > omp-to-opencl` |
| omp_target-to-cuda | 0.7800 | 0.3000 | 1.0059 | large | `cross_model_comparison.json > per_direction > omp_target-to-cuda` |
| opencl-to-cuda | 0.0600 | 0.0118 | 0.2772 | small | `cross_model_comparison.json > per_direction > opencl-to-cuda` |
| opencl-to-omp | 0.3889 | 0.4625 | -0.1490 | negligible | `cross_model_comparison.json > per_direction > opencl-to-omp` |

**Effect size summary:** 2 large (omp-to-cuda, omp_target-to-cuda), 3 small (cuda-to-opencl, omp-to-opencl, opencl-to-cuda), 2 negligible (cuda-to-omp, opencl-to-omp)
**Note:** "2 of 7 large" replaces 19-NUMBERS "1 of 7" (both_fail count change caused reclassification check -- actually h values did not change for these directions, but the count of large effects is still 2)

---

## Section 5: Per-Kernel Agreement

Source: `cross_model_comparison.json > per_kernel_matrix`

- **total_common_kernels**: 30  (`per_kernel_matrix > total_common_kernels`)
- **both_pass**: 18  (`per_kernel_matrix > counts > both_pass`)
- **both_fail**: 5  (`per_kernel_matrix > counts > both_fail`)
- **qwen_only_pass**: 6  (`per_kernel_matrix > counts > qwen_only_pass`)
- **gpt_only_pass**: 1  (`per_kernel_matrix > counts > gpt_only_pass`)

### Kernel Name Lists

**both_pass (18):** backprop, bfs, cfd, heat2d, hotspot, hotspot3d, jacobi, lavamd, lud, md, mixbench, nn, nw, page-rank, particlefilter, pathfinder, srad, streamcluster
(`cross_model_comparison.json > per_kernel_matrix > both_pass`)

**both_fail (5):** convolution1d, gaussian, heartwall, myocyte, xsbench
(`cross_model_comparison.json > per_kernel_matrix > both_fail`)

**qwen_only_pass (6):** bptree, floydwarshall, iso2dfd, nqueen, scan, stencil1d
(`cross_model_comparison.json > per_kernel_matrix > qwen_only_pass`)

**gpt_only_pass (1):** dwt2d
(`cross_model_comparison.json > per_kernel_matrix > gpt_only_pass`)

---

## Section 6: Self-Repair (GPT)

Source: `paper_data_gpt41mini.json > primary_campaign > self_repair`

- **first_attempt_pass**: 134 (23.2%)  (`self_repair > first_attempt_pass`)
- **first_attempt_pass_rate**: 0.2322, CI=[0.1996, 0.2684], n=577  (`self_repair > first_attempt_pass_rate`)
- **repaired**: 43 (7.5%)  (`self_repair > repaired`)
- **repair_rate**: 0.0971, CI=[0.0729, 0.1282], n=443  (`self_repair > repair_rate`)
- **partial_repair**: 28  (`self_repair > partial_repair`)
- **total_pass (computed)**: 134 + 43 = 177 (30.7%)  (= first_attempt_pass + repaired)
- **persistent_fail**: 367 (63.6%)  (`self_repair > persistent_fail`)
- **regression**: 5 (0.9%)  (`self_repair > regression`)
- **relative_improvement (computed)**: 43/134 = +32.1%

### Full accounting: 134 + 43 + 28 + 5 + 367 = 577 = total_tasks

---

## Section 7: Augmentation (GPT)

Source: `paper_data_gpt41mini.json > primary_campaign > augmentation > all_directions`

| Level | Rate | n | CI Lower | CI Upper | JSON Key |
|-------|------|---|----------|----------|----------|
| L0 | 0.2931 (29.3%) | 116 | 0.2180 | 0.3815 | `augmentation > all_directions > L0` |
| L1 | 0.2845 (28.4%) | 116 | 0.2103 | 0.3725 | `augmentation > all_directions > L1` |
| L2 | 0.3130 (31.3%) | 115 | 0.2355 | 0.4027 | `augmentation > all_directions > L2` |
| L3 | 0.3130 (31.3%) | 115 | 0.2355 | 0.4027 | `augmentation > all_directions > L3` |
| L4 | 0.3304 (33.0%) | 115 | 0.2512 | 0.4207 | `augmentation > all_directions > L4` |

- **Cochran-Armitage z**: 0.6188  (`augmentation > cochran_armitage > z`)
- **Cochran-Armitage p**: 0.536064  (`augmentation > cochran_armitage > p_value`)
- **Cochran-Armitage significant**: False  (`augmentation > cochran_armitage > significant`)

---

## Section 8: Pass@k (GPT)

Source: `paper_data_gpt41mini.json > passk_campaign > aggregate_passk`

- **greedy_rate**: 0.3068 (30.7%)  (`primary_campaign > overall > pass_rate` -- greedy = primary temp=0.0)
- **pass@1_macro_avg**: 0.2556 (25.6%)  (`passk_campaign > aggregate_passk > pass@1_macro_avg`)
- **pass@3_macro_avg**: 0.3146 (31.5%)  (`passk_campaign > aggregate_passk > pass@3_macro_avg`)
- **n_tasks**: 90  (`passk_campaign > aggregate_passk > n_tasks`)
- **total_samples**: (check JSON)  (`passk_campaign > aggregate_passk > total_samples`)

**Note:** hard_fail, noisy, always_pass keys do NOT exist in aggregate_passk. Omit from paper.

---

## Section 9: Error Taxonomy (GPT)

Source: `error_taxonomy.json > build_fail_categories > [category] > by_model > azure-gpt-4.1-mini`

### GPT BUILD_FAIL Subcategories (top)

| Subcategory | GPT Count | Qwen Count | Total | JSON Key Path |
|-------------|-----------|------------|-------|---------------|
| missing_header | 151 | 120 | 271 | `build_fail_categories > missing_header > by_model > azure-gpt-4.1-mini` |
| other_build | 88 | 86 | 174 | `build_fail_categories > other_build > by_model > azure-gpt-4.1-mini` |
| missing_target_api | 92 | 79 | 171 | `build_fail_categories > missing_target_api > by_model > azure-gpt-4.1-mini` |
| undeclared_identifier | 37 | 114 | 151 | `build_fail_categories > undeclared_identifier > by_model > azure-gpt-4.1-mini` |
| linker_error | 54 | 62 | 116 | `build_fail_categories > linker_error > by_model > azure-gpt-4.1-mini` |
| syntax_error | 3 | 20 | 23 | `build_fail_categories > syntax_error > by_model > azure-gpt-4.1-mini` |
| type_mismatch | 4 | 14 | 18 | `build_fail_categories > type_mismatch > by_model > azure-gpt-4.1-mini` |
| implicit_declaration | 11 | 6 | 17 | `build_fail_categories > implicit_declaration > by_model > azure-gpt-4.1-mini` |
| redefinition | 1 | 7 | 8 | `build_fail_categories > redefinition > by_model > azure-gpt-4.1-mini` |
| retained_cuda_types | 1 | 5 | 6 | `build_fail_categories > retained_cuda_types > by_model > azure-gpt-4.1-mini` |
| retained_cuda_api | 1 | 4 | 5 | `build_fail_categories > retained_cuda_api > by_model > azure-gpt-4.1-mini` |

**GPT BUILD_FAIL total**: 267 (`paper_data_gpt41mini.json > primary_campaign > overall > by_status > BUILD_FAIL`)
**GPT VERIFY_FAIL total**: 79 (`paper_data_gpt41mini.json > primary_campaign > overall > by_status > VERIFY_FAIL`)

### GPT RUN_FAIL Subcategories

| Subcategory | GPT Count | JSON Key Path |
|-------------|-----------|---------------|
| wrong_exit_code | 73 | `run_fail_categories > wrong_exit_code > by_model > azure-gpt-4.1-mini` |
| segfault | 17 | `run_fail_categories > segfault > by_model > azure-gpt-4.1-mini` |
| abort | 16 | `run_fail_categories > abort > by_model > azure-gpt-4.1-mini` |
| opencl_jit_error | 9 | `run_fail_categories > opencl_jit_error > by_model > azure-gpt-4.1-mini` |
| data_file_missing | 1 | `run_fail_categories > data_file_missing > by_model > azure-gpt-4.1-mini` |

### GPT VERIFY_FAIL Subcategories

| Subcategory | GPT Count | JSON Key Path |
|-------------|-----------|---------------|
| wrong_numerical_output | 109 | `verify_fail_categories > wrong_numerical_output > by_model > azure-gpt-4.1-mini` |
| other_verify | 20 | `verify_fail_categories > other_verify > by_model > azure-gpt-4.1-mini` |
| missing_output | 6 | `verify_fail_categories > missing_output > by_model > azure-gpt-4.1-mini` |
| verification_error | 2 | `verify_fail_categories > verification_error > by_model > azure-gpt-4.1-mini` |

---

## Section 10: Combined/Aggregate

- **Qwen pass**: 272  (`paper_data.json > primary_campaign > overall > pass`)
- **Qwen total**: 710  (`paper_data.json > primary_campaign > overall > total`)
- **GPT pass**: 177  (`paper_data_gpt41mini.json > primary_campaign > overall > pass`)
- **GPT total**: 577  (`paper_data_gpt41mini.json > primary_campaign > overall > total`)
- **Combined pass**: 272 + 177 = 449
- **Combined total**: 710 + 577 = 1,287
- **Combined rate**: 449/1287 = 0.3489 (34.9%)
- **Combined Wilson CI**: [0.3233, 0.3753] = [32.3%, 37.5%]

### Wilson CI Computation (for audit):
```python
from scipy import stats as sp_stats
import math

def wilson_ci(passes, total, alpha=0.05):
    z = sp_stats.norm.ppf(1 - alpha / 2)
    p_hat = passes / total
    denom = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denom
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total) / denom
    return (round(max(0.0, center - spread), 4), round(min(1.0, center + spread), 4))

wilson_ci(449, 1287) == (0.3233, 0.3753)
```

---

## Section 11: Deltas from 19-NUMBERS.md

All values that changed between 19-NUMBERS.md (910 files) and fresh Phase 20 values (942 files):

### Overall GPT Stats
| Metric | Old (19) | New (20) | Delta |
|--------|----------|----------|-------|
| total_tasks | 557 | 577 | +20 |
| pass_rate | 0.3178 (31.8%) | 0.3068 (30.7%) | -1.1pp |
| ci_lower | 0.2805 | 0.2705 | -0.0100 |
| ci_upper | 0.3576 | 0.3456 | -0.0120 |
| BUILD_FAIL | 247 | 267 | +20 |
| file_total | 910 | 942 | +32 |
| persistent_fail | 347 | 367 | +20 |

**Note:** pass count stayed at 177 (XSBench tasks all failed). Rate dropped because denominator grew.

### Cross-Model
| Metric | Old (19) | New (20) | Delta |
|--------|----------|----------|-------|
| chi2 | 5.5396 | 7.8336 | +2.29 |
| p_value | 0.01859 | 0.005128 | more significant |
| cohens_h | 0.137 | 0.1607 | +0.024 |
| common_kernels | 29 | 30 | +1 (xsbench rejoined as both_fail) |
| both_fail | 4 | 5 | +1 (xsbench) |

### Per-Direction GPT (changed directions only)
| Direction | Old Total | New Total | Old Rate | New Rate |
|-----------|-----------|-----------|----------|----------|
| cuda-to-omp | 80 | 85 | 60.0% | 56.5% |
| cuda-to-opencl | 85 | 90 | 35.3% | 33.3% |
| omp-to-opencl | 75 | 80 | 40.0% | 37.5% |
| opencl-to-omp | 75 | 80 | 49.3% | 46.2% |

**Note:** omp-to-cuda (107) and omp_target-to-cuda (50) and opencl-to-cuda (85) unchanged -- no XSBench tasks in those directions.

### Cross-Model Per-Direction (changed GPT rates)
| Direction | Old GPT Rate | New GPT Rate | Old h | New h |
|-----------|-------------|-------------|-------|-------|
| cuda-to-omp | 0.6000 | 0.5647 | 0.086 | 0.1576 |
| cuda-to-opencl | 0.3529 | 0.3333 | -0.3449 | -0.3036 |
| omp-to-opencl | 0.4000 | 0.3750 | -0.2591 | -0.2078 |
| opencl-to-omp | 0.4933 | 0.4625 | -0.2107 | -0.1490 |

### Combined/Aggregate
| Metric | Old (19) | New (20) | Delta |
|--------|----------|----------|-------|
| combined_total | 1,267 | 1,287 | +20 |
| combined_rate | 35.4% | 34.9% | -0.5pp |

### Augmentation
| Level | Old Rate | New Rate | Old n | New n |
|-------|----------|----------|-------|-------|
| L0 | 0.3036 | 0.2931 | 112 | 116 |
| L1 | 0.2946 | 0.2845 | 112 | 116 |
| L2 | 0.3243 | 0.3130 | 111 | 115 |
| L3 | 0.3243 | 0.3130 | 111 | 115 |
| L4 | 0.3423 | 0.3304 | 111 | 115 |
| CA z | 0.6455 | 0.6188 | -- | -- |
| CA p | 0.518605 | 0.536064 | -- | -- |

### Pass@k
| Metric | Old (19) | New (20) | Delta |
|--------|----------|----------|-------|
| pass@1 | 0.2674 | 0.2556 | -0.012 |
| pass@3 | 0.3294 | 0.3146 | -0.015 |
| n_tasks | 86 | 90 | +4 |

### Narrative Impact of Deltas

1. **GPT pass rate dropped** from 31.8% to 30.7% -- XSBench tasks all failed (both models), widening the gap.
2. **Chi-squared increased** from 5.54 to 7.83 (p from 0.019 to 0.005) -- more statistically significant difference.
3. **XSBench rejoined** the common-kernel set as both_fail (30 common kernels, was 29).
4. **All augmentation rates decreased** slightly -- more tasks, same conclusions (no significant trend).
5. **Cross-model h values shifted** for 4 directions (all moved toward zero, i.e., slightly less divergent).
6. **Combined rate dropped** from 35.4% to 34.9% -- XSBench additions all failed.

### Values That Did NOT Change
- GPT pass count: still 177
- GPT RUN_FAIL: still 54
- GPT VERIFY_FAIL: still 79
- omp-to-cuda direction: still 107 total, 16 pass
- omp_target-to-cuda direction: still 50 total, 15 pass
- opencl-to-cuda direction: still 85 total, 1 pass
- GPT regression count: still 5
- GPT repaired count: still 43
- GPT first_attempt_pass: still 134
- Qwen data: entirely unchanged (272/710 = 38.3%)
