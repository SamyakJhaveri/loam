# Quantitative Findings — NeurIPS 2026 ParBench

Generated: 2026-04-23T17:48:37.925145+00:00
Git hash: 9839533

## File Counts

- Total on disk: 708
- Excluded (KNOWN_FAIL, 8 specs): 66
- Valid after exclusion: 642
- Campaign 1 (temp=0.0): 204
- Campaign 2 (temp=0.7): 438

---

## Campaign 1: Primary Evaluation (temperature=0.0)

### Dimension 1: Aggregate Pass Rates

**Overall:** 68.1% [61.5%, 74.2%] (n=204)

| Suite | Pass Rate | 95% CI | n |
|-------|-----------|--------|---|
| hecbench | 81.8% | [72.5%, 88.5%] | 88 |
| mixbench | 50.0% | [15.0%, 85.0%] | 4 |
| rodinia | 60.2% | [50.8%, 68.9%] | 108 |
| xsbench | 0.0% | [0.0%, 49.0%] | 4 |

### Dimension 2: Per-Direction Pass Rates (L0 only)

### Dimension 3: Direction Asymmetry (McNemar, L0)

No direction pairs found for McNemar test.

### Dimension 4: Augmentation Trends

**Aggregate Cochran-Armitage:** z=-0.6048, p=0.545315, trend=decreasing, significant=No

| Level | Pass Rate | 95% CI | n |
|-------|-----------|--------|---|
| L1 | 72.5% | [59.1%, 82.9%] | 51 |
| L2 | 66.7% | [53.0%, 78.0%] | 51 |
| L3 | 66.7% | [53.0%, 78.0%] | 51 |
| L4 | 66.7% | [53.0%, 78.0%] | 51 |

**Cohen's h (adjacent levels):**
- L1_to_L2: h=-0.128
- L2_to_L3: h=0.0
- L3_to_L4: h=0.0

### Dimension 5: Failure Taxonomy

| Status | Count | % |
|--------|-------|---|
| PASS | 139 | 68.1% |
| BUILD_FAIL | 33 | 16.2% |
| RUN_FAIL | 28 | 13.7% |
| VERIFY_FAIL | 4 | 2.0% |
| EXTRACTION_FAIL | 0 | 0.0% |
| ERROR | 0 | 0.0% |

**Top-3 BUILD_FAIL subcategories:**

| Subcategory | Count |
|-------------|-------|
| other_build | 10 |
| undeclared_identifier | 9 |
| linker_error | 6 |

### Dimension 6: Self-Repair Effectiveness (Campaign 1 only)

**Overall repair rate:** 0.0% (0 full repairs / 0 initially failing)
- Multi-attempt records: 0
- Regressions: 0
- Mean attempts to success: 0.0

*Observation: 0.0% of initially-failing tasks are fully repaired through the retry loop.*

### Dimension 8: Per-Kernel Difficulty Tiers (L0)

**Total kernels:** 0


### Dimension 9: Translation Complexity Correlation

| Complexity Class | Pass Rate | 95% CI | Passes/Total |
|------------------|-----------|--------|--------------|
| single_file | 72.5% | [65.1%, 78.8%] | 116/160 |
| multi_to_single | 55.6% | [39.6%, 70.5%] | 20/36 |
| single_to_multi | 37.5% | [13.7%, 69.4%] | 3/8 |

**Statistical test:** chi_squared_warning_small_cells, p=0.023678, significant=Yes

### Dimension 10: Cross-Suite Comparison (L0)

### Dimension 11: Token Cost Analysis

- **Total cost:** $5.05
- **Cost per task:** $0.0248
- **Cost per PASS:** $0.0364
- **Tasks with tokens:** 204

| Suite | Input Tokens | Output Tokens | Cost | Tasks | Cost/Task |
|-------|-------------|---------------|------|-------|-----------|
| hecbench | 188,849 | 460,888 | $1.77 | 88 | $0.0201 |
| mixbench | 44,772 | 9,776 | $0.06 | 4 | $0.0155 |
| rodinia | 1,128,819 | 670,044 | $3.09 | 108 | $0.0286 |
| xsbench | 113,782 | 17,245 | $0.13 | 4 | $0.0326 |

### Dimension 12: SLoC Correlation

- **Spearman:** rho=?, p=? (not significant)
- **Pearson:** r=?, p=? (not significant)
- **Interpretation:** ?
- **n kernels:** ?

### Dimension 13: OpenCL Kernel-Only Effect (L0)

- **X-to-OpenCL (kernel-only):** 0.0% [0.0%, 0.0%] (n=0)
- **X-to-OMP (full program):** 0.0% [0.0%, 0.0%] (n=0)
- **Fisher's exact:** p=None, OR=?, Cohen's h=?, significant=No

---

## Campaign 2: pass@k Evaluation (temperature=0.7)

**Overall:** 23.7% [20.0%, 28.0%] (n=438)

### Dimension 7: pass@k Estimates

**Total tasks:** 146
- **pass@1** (any seed passes): 34.9% [27.7%, 43.0%]
- **pass@3** (all seeds pass): 13.0% [8.5%, 19.4%]

**Task classification:** 19 always pass, 32 noisy fail, 95 hard fail

**Per-direction pass@k:**

| Direction | pass@1 | pass@3 | n |
|-----------|--------|--------|---|
| cuda-to-omp | 50.0% | 29.2% | 24 |
| cuda-to-omp_target | 0.0% | 0.0% | 8 |
| cuda-to-opencl | 15.0% | 0.0% | 20 |
| omp-to-cuda | 33.3% | 16.7% | 24 |
| omp-to-omp_target | 100.0% | 0.0% | 3 |
| omp-to-opencl | 55.6% | 11.1% | 18 |
| omp_target-to-cuda | 100.0% | 37.5% | 8 |
| omp_target-to-omp | 100.0% | 100.0% | 3 |
| opencl-to-cuda | 0.0% | 0.0% | 20 |
| opencl-to-omp | 22.2% | 0.0% | 18 |

**Per-suite pass@k:**

| Suite | pass@1 | pass@3 | n |
|-------|--------|--------|---|
| hecbench | 68.8% | 34.4% | 32 |
| mixbench | 16.7% | 0.0% | 6 |
| rodinia | 28.1% | 8.3% | 96 |
| rsbench | 0.0% | 0.0% | 6 |
| xsbench | 16.7% | 0.0% | 6 |

---

## Paper Claims Mapping

| # | Claim ID | Scope | Display Value | Paper Location |
|---|----------|-------|---------------|----------------|
| 1 | overall_pass_rate_rodinia | rodinia_only | 60.2% [50.8%, 68.9%] | abstract/line~71, S6.1/line~707 |
| 2 | primary_campaign_task_counts | all_suite | 108 Rodinia, 204 all-suite | abstract/line~61, S5.2/line~630 |
| 3 | passk_task_count | all_suite | 146 pass@k tasks | S1/line~106, S5.5/line~689 |
| 4 | build_fail_percentage | all_suite | 33/204 = 16.2% | abstract/line~66, S1/line~107, S6.2/line~714 |
| 5 | verify_fail_percentage | all_suite | 4/204 = 2.0% | abstract/line~66, S6.2/line~714 |
| 6 | cuda_to_omp_pass_rate | all_suite | ? | S6.1/line~909, S7.1/line~1041 |
| 7 | l0_pass_rate | all_suite | ? | S6.4/line~899 |
| 8 | cochran_armitage_trend | all_suite | z=-0.6048, p=0.545315 | abstract/line~71, S6.4/line~899, S6.8/line~1003 |
| 9 | self_repair_rate | all_suite | 0.0% | S6.3/line~859, S7.1/line~1049 |
| 10 | repair_count | all_suite | 0 of 0 repaired | S6.3/line~849, S6.3/line~859 |
| 11 | regression_count | all_suite | 0 regressions | S6.3/line~853 |
| 12 | cohens_h_range | all_suite | h range [-0.1280, 0.0000] | S6.4/implied |
| 13 | spec_count | all_suite | 96 specs (60+25+4+4+3) | abstract/line~60, S3.2/line~297, S4.3/line~511 |
| 14 | opencl_to_cuda_pass_rate | all_suite | ? | S6.1/line~941 |
| 15 | multi_file_percentage | all_suite | 76/206 = 36.9% | S1/implied, S4/implied |
| 16 | overall_pass_rate_all_suite | all_suite | 68.1% [61.5%, 74.2%] | S6.1 (all-suite scope) |
| 17 | first_attempt_pass | all_suite | 139 | S6.3/line~848 |
| 18 | pass_at_k_rates | all_suite | pass@1=34.9%, pass@3=13.0% | S6.5/line~955 |
| 19 | token_cost | all_suite | $5.05 | S5.2/implied |
| 20 | sloc_correlation | all_suite | None | S7/implied |

---

## Cross-Check Results

Checks run: 3
Status: pass
