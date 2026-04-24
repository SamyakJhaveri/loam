# Quantitative Findings — NeurIPS 2026 ParBench

Generated: 2026-04-24T22:01:13.141684+00:00
Git hash: f013989

## File Counts

- Total on disk: 708
- Excluded (KNOWN_FAIL, 8 specs): 66
- Valid after exclusion: 642
- Campaign 1 (temp=0.0): 0
- Campaign 2 (temp=0.7): 642

---

## Campaign 1: Primary Evaluation (temperature=0.0)

### Dimension 1: Aggregate Pass Rates

**Overall:** 0.0% [0.0%, 0.0%] (n=0)

### Dimension 2: Per-Direction Pass Rates (L0 only)

### Dimension 3: Direction Asymmetry (McNemar, L0)

No direction pairs found for McNemar test.

### Dimension 4: Augmentation Trends

**Aggregate Cochran-Armitage:** z=?, p=?, trend=?, significant=No

### Dimension 5: Failure Taxonomy

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

**Statistical test:** insufficient_data, p=None, significant=No

### Dimension 10: Cross-Suite Comparison (L0)

### Dimension 11: Token Cost Analysis

- **Total cost:** ?
- **Cost per task:** ?
- **Cost per PASS:** ?
- **Tasks with tokens:** 0

### Dimension 12: SLoC Correlation

- **Spearman:** rho=?, p=? (not significant)
- **Pearson:** r=?, p=? (not significant)
- **Interpretation:** ?
- **n kernels:** 0

### Dimension 13: OpenCL Kernel-Only Effect (L0)

- **X-to-OpenCL (kernel-only):** 0.0% [0.0%, 0.0%] (n=0)
- **X-to-OMP (full program):** 0.0% [0.0%, 0.0%] (n=0)
- **Fisher's exact:** p=None, OR=?, Cohen's h=?, significant=No

---

## Campaign 2: pass@k Evaluation (temperature=0.7)

**Overall:** 36.6% [33.0%, 40.4%] (n=642)

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
| 1 | overall_pass_rate_rodinia | rodinia_only | 0.0% [0.0%, 0.0%] | abstract/line~71, S6.1/line~707 |
| 2 | primary_campaign_task_counts | all_suite | 0 Rodinia, 0 all-suite | abstract/line~61, S5.2/line~630 |
| 3 | passk_task_count | all_suite | 146 pass@k tasks | S1/line~106, S5.5/line~689 |
| 4 | build_fail_percentage | all_suite | 0/0 = 0.0% | abstract/line~66, S1/line~107, S6.2/line~714 |
| 5 | verify_fail_percentage | all_suite | 0/0 = 0.0% | abstract/line~66, S6.2/line~714 |
| 6 | cuda_to_omp_pass_rate | all_suite | ? | S6.1/line~909, S7.1/line~1041 |
| 7 | l0_pass_rate | all_suite | ? | S6.4/line~899 |
| 8 | cochran_armitage_trend | all_suite | z=None, p=None | abstract/line~71, S6.4/line~899, S6.8/line~1003 |
| 9 | self_repair_rate | all_suite | 0.0% | S6.3/line~859, S7.1/line~1049 |
| 10 | repair_count | all_suite | 0 of 0 repaired | S6.3/line~849, S6.3/line~859 |
| 11 | regression_count | all_suite | 0 regressions | S6.3/line~853 |
| 12 | cohens_h_range | all_suite | h range [0.0000, 0.0000] | S6.4/implied |
| 13 | spec_count | all_suite | 96 specs (60+25+4+4+3) | abstract/line~60, S3.2/line~297, S4.3/line~511 |
| 14 | opencl_to_cuda_pass_rate | all_suite | ? | S6.1/line~941 |
| 15 | multi_file_percentage | all_suite | 76/206 = 36.9% | S1/implied, S4/implied |
| 16 | overall_pass_rate_all_suite | all_suite | 0.0% [0.0%, 0.0%] | S6.1 (all-suite scope) |
| 17 | first_attempt_pass | all_suite | 0 | S6.3/line~848 |
| 18 | pass_at_k_rates | all_suite | pass@1=34.9%, pass@3=13.0% | S6.5/line~955 |
| 19 | token_cost | all_suite | $0.00 | S5.2/implied |
| 20 | sloc_correlation | all_suite | None | S7/implied |

---

## Cross-Check Results

Checks run: 7
Status: pass
