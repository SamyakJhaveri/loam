# Phase 19 Reference Numbers

Generated from regenerated analysis files (2026-04-08).
Phase 20 executor: use these values to update paper.tex, overleaf.tex, appendices.tex.

## GPT-4.1 mini Primary Campaign
- **total_tasks**: 557  (JSON: primary_campaign.overall.total)
- **pass**: 177  (JSON: primary_campaign.overall.pass)
- **pass_rate**: 0.3178 (31.8%)  (JSON: primary_campaign.overall.pass_rate)
- **ci_lower**: 0.2805 (28.1%)  (JSON: primary_campaign.overall.ci_lower)
- **ci_upper**: 0.3576 (35.8%)  (JSON: primary_campaign.overall.ci_upper)
- **BUILD_FAIL**: 247  (JSON: primary_campaign.overall.by_status.BUILD_FAIL)
- **RUN_FAIL**: 54  (JSON: primary_campaign.overall.by_status.RUN_FAIL)
- **VERIFY_FAIL**: 79  (JSON: primary_campaign.overall.by_status.VERIFY_FAIL)
- **PASS**: 177  (JSON: primary_campaign.overall.by_status.PASS)
- **file_counts.total_on_disk**: 910  (JSON: file_counts.total_on_disk)

## GPT-4.1 mini By Direction
- **cuda-to-omp**: total=80, pass=48, rate=60.0% [49.0%, 70.0%]  (JSON: primary_campaign.by_direction.cuda-to-omp)
- **cuda-to-opencl**: total=85, pass=30, rate=35.3% [26.0%, 45.9%]  (JSON: primary_campaign.by_direction.cuda-to-opencl)
- **omp-to-cuda**: total=107, pass=16, rate=14.9% [9.4%, 22.9%]  (JSON: primary_campaign.by_direction.omp-to-cuda)
- **omp-to-opencl**: total=75, pass=30, rate=40.0% [29.7%, 51.3%]  (JSON: primary_campaign.by_direction.omp-to-opencl)
- **omp_target-to-cuda**: total=50, pass=15, rate=30.0% [19.1%, 43.8%]  (JSON: primary_campaign.by_direction.omp_target-to-cuda)
- **opencl-to-cuda**: total=85, pass=1, rate=1.2% [0.2%, 6.4%]  (JSON: primary_campaign.by_direction.opencl-to-cuda)
- **opencl-to-omp**: total=75, pass=37, rate=49.3% [38.3%, 60.4%]  (JSON: primary_campaign.by_direction.opencl-to-omp)

## Combined (Qwen + GPT)
- **combined_total**: 1267 (Qwen:710 + GPT:557)
- **combined_pass**: 449
- **combined_rate**: 35.4%

## Cross-Model Comparison
- **chi_squared**: 5.5396  (JSON: overall.chi_squared.chi2)
- **p_value**: 0.01859  (JSON: overall.chi_squared.p_value)
- **cohens_h**: 0.137  (JSON: overall.cohens_h)
- **gpt_pass_rate**: 0.3178  (JSON: overall.gpt.rate)
- **qwen_pass_rate**: 0.3831  (JSON: overall.qwen.rate)
- **common_directions**: 7  (JSON: per_direction keys)
- **missing_directions**: {"azure-gpt-4.1-mini": ["cuda-to-omp_target"]}

### Per-Direction Cross-Model
- **cuda-to-omp**: qwen_rate=0.6417, gpt_rate=0.6, h=0.086, effect=negligible
- **cuda-to-opencl**: qwen_rate=0.2, gpt_rate=0.3529, h=-0.3449, effect=small
- **omp-to-cuda**: qwen_rate=0.525, gpt_rate=0.1495, h=0.8268, effect=large
- **omp-to-opencl**: qwen_rate=0.2778, gpt_rate=0.4, h=-0.2591, effect=small
- **omp_target-to-cuda**: qwen_rate=0.78, gpt_rate=0.3, h=1.0059, effect=large
- **opencl-to-cuda**: qwen_rate=0.06, gpt_rate=0.0118, h=0.2772, effect=small
- **opencl-to-omp**: qwen_rate=0.3889, gpt_rate=0.4933, h=-0.2107, effect=small

## Per-Kernel Agreement Matrix
- **total_common_kernels**: 29  (JSON: per_kernel_matrix.total_common_kernels; equals sum of counts dict)
- **both_pass**: 18  (JSON: per_kernel_matrix.counts.both_pass)
- **both_fail**: 4  (JSON: per_kernel_matrix.counts.both_fail)
- **qwen_only**: 6  (JSON: per_kernel_matrix.counts.qwen_only_pass)
- **gpt_only**: 1  (JSON: per_kernel_matrix.counts.gpt_only_pass)

## Self-Repair (GPT)
- **first_attempt_pass**: 134  (JSON: primary_campaign.self_repair.first_attempt_pass)
- **repaired**: 43  (JSON: primary_campaign.self_repair.repaired)
- **partial_repair**: 28  (JSON: primary_campaign.self_repair.partial_repair)
- **total_pass**: 177  (JSON: primary_campaign.overall.pass)
- **persistent_fail**: 347  (JSON: primary_campaign.self_repair.persistent_fail)
- **regression**: 5  (JSON: primary_campaign.self_repair.regression)
- **first_attempt_pass_rate**: 0.2406  (JSON: primary_campaign.self_repair.first_attempt_pass_rate.rate)
- **repair_rate**: 0.1017  (JSON: primary_campaign.self_repair.repair_rate.rate)
- NOTE: 134+43+28+5+347 = 557 = total_tasks (full accounting)

## Augmentation by Level (GPT)
- **L0**: rate=0.3036, n=112, CI=[0.2261, 0.3941]  (JSON: primary_campaign.augmentation.all_directions.L0; keys: rate, n, ci_lower, ci_upper)
- **L1**: rate=0.2946, n=112, CI=[0.2182, 0.3847]  (JSON: primary_campaign.augmentation.all_directions.L1; keys: rate, n, ci_lower, ci_upper)
- **L2**: rate=0.3243, n=111, CI=[0.2444, 0.416]  (JSON: primary_campaign.augmentation.all_directions.L2; keys: rate, n, ci_lower, ci_upper)
- **L3**: rate=0.3243, n=111, CI=[0.2444, 0.416]  (JSON: primary_campaign.augmentation.all_directions.L3; keys: rate, n, ci_lower, ci_upper)
- **L4**: rate=0.3423, n=111, CI=[0.2607, 0.4346]  (JSON: primary_campaign.augmentation.all_directions.L4; keys: rate, n, ci_lower, ci_upper)
- **Cochran-Armitage z**: 0.6455  (JSON: primary_campaign.augmentation.cochran_armitage.z)
- **Cochran-Armitage p**: 0.518605  (JSON: primary_campaign.augmentation.cochran_armitage.p_value)

## Pass@k (GPT)
- **pass@1**: 0.2674  (JSON: passk_campaign.aggregate_passk.pass@1_macro_avg)
- **pass@3**: 0.3294  (JSON: passk_campaign.aggregate_passk.pass@3_macro_avg)
- **n_tasks**: 86  (JSON: passk_campaign.aggregate_passk.n_tasks)
- **hard_fail**: None  (JSON: passk_campaign.aggregate_passk.hard_fail)
- **noisy**: None  (JSON: passk_campaign.aggregate_passk.noisy)
- **always_pass**: None  (JSON: passk_campaign.aggregate_passk.always_pass)

