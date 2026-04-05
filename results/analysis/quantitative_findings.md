# Quantitative Findings — SC26 ParBench

Generated: 2026-04-05T04:06:26.011212+00:00
Git hash: 03f5c6a

## File Counts

- Total on disk: 1248
- Excluded (KNOWN_FAIL, 8 specs): 128
- Valid after exclusion: 1120
- Campaign 1 (temp=0.0): 700
- Campaign 2 (temp=0.7): 420

---

## Campaign 1: Primary Evaluation (temperature=0.0)

### Dimension 1: Aggregate Pass Rates

**Overall:** 38.0% [34.5%, 41.6%] (n=700)

| Suite | Pass Rate | 95% CI | n |
|-------|-----------|--------|---|
| hecbench | 64.6% | [56.1%, 72.3%] | 130 |
| mixbench | 26.7% | [14.2%, 44.5%] | 30 |
| rodinia | 36.2% | [32.1%, 40.6%] | 480 |
| rsbench | 0.0% | [0.0%, 11.3%] | 30 |
| xsbench | 0.0% | [0.0%, 11.3%] | 30 |

### Dimension 2: Per-Direction Pass Rates (L0 only)

**Standard directions:**

| Direction | Pass Rate | 95% CI | n |
|-----------|-----------|--------|---|
| cuda-to-omp | 66.7% | [46.7%, 82.0%] | 24 |
| cuda-to-opencl | 20.0% | [8.1%, 41.6%] | 20 |
| omp-to-cuda | 58.3% | [38.8%, 75.5%] | 24 |
| omp-to-opencl | 33.3% | [16.3%, 56.2%] | 18 |
| opencl-to-cuda | 10.0% | [2.8%, 30.1%] | 20 |
| opencl-to-omp | 38.9% | [20.3%, 61.4%] | 18 |

**Case study directions (omp_target):**

| Direction | Pass Rate | 95% CI | n |
|-----------|-----------|--------|---|
| cuda-to-omp_target | 12.5% | [2.2%, 47.1%] | 8 |
| omp_target-to-cuda | 75.0% | [40.9%, 92.8%] | 8 |

*Observation: cuda-to-omp has 6.7x higher pass rate than opencl-to-cuda.*

### Dimension 3: Direction Asymmetry (McNemar, L0)

| Pair | Fwd Rate | Rev Rate | p-value | Cohen's h | Effect | Sig? |
|------|----------|----------|---------|-----------|--------|------|
| cuda-to-omp_target vs omp_target-to-cuda | 12.5% | 75.0% | 0.0625 | -1.3717 | large | No |
| omp-to-cuda vs cuda-to-omp | 58.3% | 66.7% | 0.6875 | -0.1724 | negligible | No |
| opencl-to-cuda vs cuda-to-opencl | 10.0% | 20.0% | 0.6875 | -0.2838 | small | No |
| opencl-to-omp vs omp-to-opencl | 38.9% | 33.3% | 1.0 | 0.1157 | negligible | No |

### Dimension 4: Augmentation Trends

**Aggregate Cochran-Armitage:** z=-0.7709, p=0.440789, trend=decreasing, significant=No

| Level | Pass Rate | 95% CI | n |
|-------|-----------|--------|---|
| L0 | 40.0% | [32.3%, 48.3%] | 140 |
| L1 | 37.1% | [29.6%, 45.4%] | 140 |
| L2 | 40.0% | [32.3%, 48.3%] | 140 |
| L3 | 38.6% | [30.9%, 46.8%] | 140 |
| L4 | 34.3% | [26.9%, 42.5%] | 140 |

**Cohen's h (adjacent levels):**
- L0_to_L1: h=-0.0587
- L1_to_L2: h=0.0587
- L2_to_L3: h=-0.0293
- L3_to_L4: h=-0.0891

### Dimension 5: Failure Taxonomy

| Status | Count | % |
|--------|-------|---|
| PASS | 266 | 38.0% |
| BUILD_FAIL | 237 | 33.9% |
| RUN_FAIL | 144 | 20.6% |
| VERIFY_FAIL | 51 | 7.3% |
| EXTRACTION_FAIL | 1 | 0.1% |
| ERROR | 1 | 0.1% |

**Top-3 BUILD_FAIL subcategories:**

| Subcategory | Count |
|-------------|-------|
| undeclared_identifier | 56 |
| missing_header | 55 |
| other_build | 51 |

### Dimension 6: Self-Repair Effectiveness (Campaign 1 only)

**Overall repair rate:** 20.4% (111 full repairs / 544 initially failing)
- Multi-attempt records: 549
- Regressions: 4
- Mean attempts to success: 2.39

**Per initial failure type:**

| Initial Status | Total | Full Repair | Partial | No Change | Regression | Repair Rate |
|----------------|-------|-------------|---------|-----------|------------|-------------|
| BUILD_FAIL | 342 | 72 | 39 | 229 | 2 | 21.1% |
| EXTRACTION_FAIL | 27 | 15 | 12 | 0 | 0 | 55.6% |
| RUN_FAIL | 148 | 17 | 2 | 127 | 2 | 11.5% |
| VERIFY_FAIL | 27 | 7 | 0 | 20 | 0 | 25.9% |

*Observation: 20.4% of initially-failing tasks are fully repaired through the retry loop.*

### Dimension 8: Per-Kernel Difficulty Tiers (L0)

**Total kernels:** 31

| Rank | Kernel | Suite | Pass Rate | 95% CI | Passes/Total | Tier |
|------|--------|-------|-----------|--------|--------------|------|
| 1 | page-rank | hecbench | 100.0% | [34.2%, 100.0%] | 2/2 | Q1_easiest |
| 2 | stencil1d | hecbench | 100.0% | [34.2%, 100.0%] | 2/2 | Q1_easiest |
| 3 | hotspot3d | rodinia | 83.3% | [43.6%, 97.0%] | 5/6 | Q1_easiest |
| 4 | floydwarshall | hecbench | 75.0% | [30.1%, 95.4%] | 3/4 | Q1_easiest |
| 5 | heat2d | hecbench | 75.0% | [30.1%, 95.4%] | 3/4 | Q1_easiest |
| 6 | iso2dfd | hecbench | 75.0% | [30.1%, 95.4%] | 3/4 | Q1_easiest |
| 7 | bfs | rodinia | 66.7% | [30.0%, 90.3%] | 4/6 | Q1_easiest |
| 8 | cfd | rodinia | 66.7% | [30.0%, 90.3%] | 4/6 | Q2 |
| 9 | hotspot | rodinia | 66.7% | [30.0%, 90.3%] | 4/6 | Q2 |
| 10 | particlefilter | rodinia | 66.7% | [30.0%, 90.3%] | 4/6 | Q2 |
| 11 | backprop | rodinia | 50.0% | [18.8%, 81.2%] | 3/6 | Q2 |
| 12 | lud | rodinia | 50.0% | [18.8%, 81.2%] | 3/6 | Q2 |
| 13 | md | hecbench | 50.0% | [9.4%, 90.5%] | 1/2 | Q2 |
| 14 | nn | rodinia | 50.0% | [9.4%, 90.5%] | 1/2 | Q2 |
| 15 | nqueen | hecbench | 50.0% | [9.4%, 90.5%] | 1/2 | Q2 |
| 16 | nw | rodinia | 50.0% | [18.8%, 81.2%] | 3/6 | Q3 |
| 17 | pathfinder | rodinia | 50.0% | [18.8%, 81.2%] | 3/6 | Q3 |
| 18 | scan | hecbench | 50.0% | [9.4%, 90.5%] | 1/2 | Q3 |
| 19 | mixbench | mixbench | 33.3% | [9.7%, 70.0%] | 2/6 | Q3 |
| 20 | srad | rodinia | 33.3% | [9.7%, 70.0%] | 2/6 | Q3 |
| 21 | bptree | rodinia | 16.7% | [3.0%, 56.4%] | 1/6 | Q3 |
| 22 | lavamd | rodinia | 16.7% | [3.0%, 56.4%] | 1/6 | Q3 |
| 23 | convolution1d | hecbench | 0.0% | [0.0%, 65.8%] | 0/2 | Q3 |
| 24 | dwt2d | rodinia | 0.0% | [0.0%, 65.8%] | 0/2 | Q4_hardest |
| 25 | gaussian | rodinia | 0.0% | [0.0%, 65.8%] | 0/2 | Q4_hardest |
| 26 | heartwall | rodinia | 0.0% | [0.0%, 39.0%] | 0/6 | Q4_hardest |
| 27 | jacobi | hecbench | 0.0% | [0.0%, 65.8%] | 0/2 | Q4_hardest |
| 28 | myocyte | rodinia | 0.0% | [0.0%, 39.0%] | 0/6 | Q4_hardest |
| 29 | rsbench | rsbench | 0.0% | [0.0%, 39.0%] | 0/6 | Q4_hardest |
| 30 | streamcluster | rodinia | 0.0% | [0.0%, 39.0%] | 0/6 | Q4_hardest |
| 31 | xsbench | xsbench | 0.0% | [0.0%, 39.0%] | 0/6 | Q4_hardest |

**Top-5 easiest:** page-rank (100.0%), stencil1d (100.0%), hotspot3d (83.3%), floydwarshall (75.0%), heat2d (75.0%)
**Top-5 hardest:** jacobi (0.0%), myocyte (0.0%), rsbench (0.0%), streamcluster (0.0%), xsbench (0.0%)

**Direction anomalies (>50pp gap):**

- hotspot3d: cuda-to-omp=100.0% vs opencl-to-cuda=0.0% (100.0pp gap)
- floydwarshall: cuda-to-omp=100.0% vs cuda-to-omp_target=0.0% (100.0pp gap)
- heat2d: cuda-to-omp=100.0% vs cuda-to-omp_target=0.0% (100.0pp gap)
- iso2dfd: cuda-to-omp=100.0% vs cuda-to-omp_target=0.0% (100.0pp gap)
- bfs: cuda-to-omp=100.0% vs omp-to-opencl=0.0% (100.0pp gap)
- cfd: cuda-to-omp=100.0% vs cuda-to-opencl=0.0% (100.0pp gap)
- hotspot: cuda-to-omp=100.0% vs omp-to-opencl=0.0% (100.0pp gap)
- particlefilter: cuda-to-omp=100.0% vs cuda-to-opencl=0.0% (100.0pp gap)
- backprop: cuda-to-omp=100.0% vs omp-to-cuda=0.0% (100.0pp gap)
- lud: cuda-to-omp=100.0% vs cuda-to-opencl=0.0% (100.0pp gap)
- md: omp_target-to-cuda=100.0% vs cuda-to-omp_target=0.0% (100.0pp gap)
- nn: omp-to-cuda=100.0% vs cuda-to-omp=0.0% (100.0pp gap)
- nqueen: omp_target-to-cuda=100.0% vs cuda-to-omp_target=0.0% (100.0pp gap)
- nw: cuda-to-omp=100.0% vs cuda-to-opencl=0.0% (100.0pp gap)
- pathfinder: cuda-to-omp=100.0% vs cuda-to-opencl=0.0% (100.0pp gap)
- scan: cuda-to-omp=100.0% vs omp-to-cuda=0.0% (100.0pp gap)
- mixbench: omp-to-cuda=100.0% vs cuda-to-omp=0.0% (100.0pp gap)
- srad: cuda-to-omp=100.0% vs cuda-to-opencl=0.0% (100.0pp gap)
- bptree: omp-to-opencl=100.0% vs cuda-to-omp=0.0% (100.0pp gap)
- lavamd: cuda-to-omp=100.0% vs cuda-to-opencl=0.0% (100.0pp gap)

### Dimension 9: Translation Complexity Correlation

| Complexity Class | Pass Rate | 95% CI | Passes/Total |
|------------------|-----------|--------|--------------|
| single_file | 51.3% | [46.3%, 56.3%] | 195/380 |
| multi_to_single | 36.3% | [28.7%, 44.7%] | 49/135 |
| single_to_multi | 13.3% | [8.6%, 20.1%] | 18/135 |
| multi_to_multi | 8.0% | [3.1%, 18.8%] | 4/50 |

**Statistical test:** chi_squared, p=0.0, significant=Yes

### Dimension 10: Cross-Suite Comparison (L0)

| Suite | Pass Rate (L0) | 95% CI | n | Mean SLoC | Multi-File % |
|-------|----------------|--------|---|-----------|-------------|
| hecbench | 61.5% | [42.5%, 77.6%] | 26 | 165.1 | 38.5% |
| mixbench | 33.3% | [9.7%, 70.0%] | 6 | 312.0 | 0.0% |
| rodinia | 39.6% | [30.4%, 49.6%] | 96 | 753.5 | 35.0% |
| rsbench | 0.0% | [0.0%, 39.0%] | 6 | 1016.0 | 25.0% |
| xsbench | 0.0% | [0.0%, 39.0%] | 6 | 1390.0 | 50.0% |

### Dimension 11: Token Cost Analysis

- **Total cost:** $55.88
- **Cost per task:** $0.0799
- **Cost per PASS:** $0.2101
- **Tasks with tokens:** 699

| Suite | Input Tokens | Output Tokens | Cost | Tasks | Cost/Task |
|-------|-------------|---------------|------|-------|-----------|
| hecbench | 954,122 | 506,296 | $2.40 | 130 | $0.0184 |
| mixbench | 956,950 | 184,528 | $1.24 | 30 | $0.0413 |
| rodinia | 30,032,281 | 7,688,763 | $45.70 | 480 | $0.0952 |
| rsbench | 2,585,369 | 407,812 | $3.02 | 29 | $0.1041 |
| xsbench | 2,940,964 | 489,064 | $3.53 | 30 | $0.1175 |

### Dimension 12: SLoC Correlation

- **Spearman:** rho=-0.471, p=0.007481 (significant)
- **Pearson:** r=-0.3595, p=0.04702 (significant)
- **Interpretation:** significant_negative
- **n kernels:** 31

### Dimension 13: OpenCL Kernel-Only Effect (L0)

- **X-to-OpenCL (kernel-only):** 26.3% [15.0%, 42.0%] (n=38)
- **X-to-OMP (full program):** 54.8% [40.0%, 68.8%] (n=42)
- **Fisher's exact:** p=0.012762, OR=0.295, Cohen's h=-0.5889, significant=Yes

---

## Campaign 2: pass@k Evaluation (temperature=0.7)

**Overall:** 19.3% [15.8%, 23.3%] (n=420)

### Dimension 7: pass@k Estimates

**Total tasks:** 140
- **pass@1** (any seed passes): 27.1% [20.5%, 35.0%]
- **pass@3** (all seeds pass): 11.4% [7.2%, 17.8%]

**Task classification:** 16 always pass, 22 noisy fail, 102 hard fail

**Per-direction pass@k:**

| Direction | pass@1 | pass@3 | n |
|-----------|--------|--------|---|
| cuda-to-omp | 45.8% | 20.8% | 24 |
| cuda-to-omp_target | 0.0% | 0.0% | 8 |
| cuda-to-opencl | 20.0% | 5.0% | 20 |
| omp-to-cuda | 29.2% | 16.7% | 24 |
| omp-to-opencl | 33.3% | 5.6% | 18 |
| omp_target-to-cuda | 75.0% | 50.0% | 8 |
| opencl-to-cuda | 0.0% | 0.0% | 20 |
| opencl-to-omp | 22.2% | 5.6% | 18 |

**Per-suite pass@k:**

| Suite | pass@1 | pass@3 | n |
|-------|--------|--------|---|
| hecbench | 53.8% | 34.6% | 26 |
| mixbench | 33.3% | 0.0% | 6 |
| rodinia | 22.9% | 7.3% | 96 |
| rsbench | 0.0% | 0.0% | 6 |
| xsbench | 0.0% | 0.0% | 6 |

---

## Paper Claims Mapping

| # | Claim ID | Scope | Display Value | Paper Location |
|---|----------|-------|---------------|----------------|
| 1 | overall_pass_rate_rodinia | rodinia_only | 36.2% [32.1%, 40.6%] | abstract/line~71, S6.1/line~707 |
| 2 | primary_campaign_task_counts | all_suite | 480 Rodinia, 700 all-suite | abstract/line~61, S5.2/line~630 |
| 3 | passk_task_count | all_suite | 140 pass@k tasks | S1/line~106, S5.5/line~689 |
| 4 | build_fail_percentage | all_suite | 237/700 = 33.9% | abstract/line~66, S1/line~107, S6.2/line~714 |
| 5 | verify_fail_percentage | all_suite | 51/700 = 7.3% | abstract/line~66, S6.2/line~714 |
| 6 | cuda_to_omp_pass_rate | all_suite | 66.7% | S6.1/line~909, S7.1/line~1041 |
| 7 | l0_pass_rate | all_suite | 40.0% | S6.4/line~899 |
| 8 | cochran_armitage_trend | all_suite | z=-0.7709, p=0.440789 | abstract/line~71, S6.4/line~899, S6.8/line~1003 |
| 9 | self_repair_rate | all_suite | 20.4% | S6.3/line~859, S7.1/line~1049 |
| 10 | repair_count | all_suite | 111 of 544 repaired | S6.3/line~849, S6.3/line~859 |
| 11 | regression_count | all_suite | 4 regressions | S6.3/line~853 |
| 12 | cohens_h_range | all_suite | h range [-0.0891, 0.0587] | S6.4/implied |
| 13 | spec_count | all_suite | 96 specs (60+25+4+4+3) | abstract/line~60, S3.2/line~297, S4.3/line~511 |
| 14 | opencl_to_cuda_pass_rate | all_suite | 10.0% | S6.1/line~941 |
| 15 | multi_file_percentage | all_suite | 76/206 = 36.9% | S1/implied, S4/implied |
| 16 | overall_pass_rate_all_suite | all_suite | 38.0% [34.5%, 41.6%] | S6.1 (all-suite scope) |
| 17 | first_attempt_pass | all_suite | 155 | S6.3/line~848 |
| 18 | pass_at_k_rates | all_suite | pass@1=27.1%, pass@3=11.4% | S6.5/line~955 |
| 19 | token_cost | all_suite | $55.88 | S5.2/implied |
| 20 | sloc_correlation | all_suite | rho=-0.471, p=0.007481 | S7/implied |

---

## Cross-Check Results

Checks run: 8
Status: pass

- INFO: C1 overall pass rate minor diff: paper_data=0.3831, ours=0.38 (diff=0.0031). Expected due to 8 vs 6 KNOWN_FAIL exclusions.
- INFO: Self-repair rate minor diff: selfrepair_analysis=0.1875, ours=0.204 (diff=0.0165). Expected due to different KNOWN_FAIL exclusion scope.
- INFO: Token count minor diff: token_analysis prompt=43828465, ours=37469686 (ratio=0.85). Expected due to different KNOWN_FAIL exclusion scope.
