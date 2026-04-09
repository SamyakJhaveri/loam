# Feature Landscape: Fair Multi-Model LLM Code Evaluation Framework

**Domain:** Multi-campaign, multi-model HPC benchmark evaluation (CUDA/OpenMP/OpenCL translation)
**Researched:** 2026-04-09
**Context:** Adding Campaign 2 (pass@k=3, stochastic) and AskSage multi-model support to existing Campaign 1 (pass@1, deterministic self-repair) Qwen 3.5 397B baseline.

---

## Table Stakes

Features that must be present or results are not publishable. Missing any of these invalidates model comparisons.

| Feature | Why Expected | Complexity | Current Status |
|---------|--------------|------------|----------------|
| Identical prompt per (source, target, augment_level) tuple | Different prompts = different tasks; model comparison meaningless | Low | PRESENT — prompt is spec-derived, deterministic |
| `campaign_id` field in every result JSON | Without tagging, Campaign 1 and Campaign 2 results cannot be separated in analysis | Low | MISSING — results currently have no campaign tag |
| `temperature` field per result | Wilson CI and stochastic/deterministic separation hinge on this | Low | PRESENT — field exists, recorded as `0.0` for Campaign 1 |
| `sample_id` field per result (0-indexed, 0..n-1) | Needed to group n samples per (task, model) for pass@k computation | Low | PRESENT — field exists, always `0` in Campaign 1 |
| Consistent denominator across models | Different exclusion rules per model = unfair comparison; KNOWN_FAIL policy must be identical | Low | PRESENT for Qwen; must be enforced for new models |
| `model` field per result | Self-evidently required for multi-model analysis | Low | PRESENT |
| Unbiased pass@k estimator: `1 - C(n-c, k) / C(n, k)` | Naive `(c/n)^k` or `c/n` are biased estimators; Chen et al. 2021 (Codex/HumanEval) established this as standard | Medium | MISSING — `statistical_analysis.py` has a placeholder comment "Pass@k estimates (when multi-sample results exist)" but no Campaign 2 data exists yet |
| Per-task pass@k macro-averaged across tasks | Micro-average (sum all passes / sum all samples) conflates task difficulty; macro-average is the standard (Chen et al. 2021, ParEval HPDC 2024) | Medium | MISSING — analysis pipeline not yet built for Campaign 2 |
| Identical benchmark corpus (spec set) per model | Adding or removing specs between model runs contaminates comparison; denominator = 1,120 non-KNOWN_FAIL results per model | Low | PARTIALLY PRESENT — Qwen has full coverage; GPT-4.1 mini invalid non-Rodinia data must be re-run |
| Wilson score 95% CI on every reported pass rate | Without CIs, a 31% vs 34% difference is not interpretable; standard in clinical/ML evaluation | Low | PRESENT — `wilson_ci()` exists in `statistical_analysis.py` |
| Separation of Campaign 1 and Campaign 2 in analysis | The two campaigns measure different capabilities; mixing them produces an incoherent aggregate | Medium | MISSING — needs analysis path gating on `campaign_id` |
| Thinking/reasoning explicitly disabled for all models | Gemini Flash Lite audited (2026-03-26) — thinking is OFF by default but must be forced. Qwen thinking OFF via `enable_thinking=False`. All models must be base-capability-equivalent. | Low | PRESENT for Qwen/Gemini — must be enforced for AskSage models |

---

## Differentiators

Features that distinguish ParBench's multi-model evaluation as a NeurIPS-quality contribution rather than a routine benchmark run.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Two-campaign design: robustness vs. sampling capability | Campaign 1 (temp=0, self-repair, L0-L4) measures deterministic robustness under augmentation stress. Campaign 2 (temp=0.7, pass@k=3, L0 only, single-shot) measures stochastic diversity. These are orthogonal capability axes — no other HPC translation benchmark separates them. | Medium | The key scientific claim: a model can be robust (high C1) but brittle under diversity (low C2), or vice versa. This enables quadrant analysis. |
| Augmentation-level robustness curves per model | L0-L4 pass rate decay curve per model in Campaign 1 reveals sensitivity to source code variation. Cochran-Armitage trend test already implemented. | Low | Already supported by existing `statistical_analysis.py`. |
| Direction asymmetry analysis | CUDA→OMP vs OMP→CUDA pass rate gap. McNemar's exact test already in codebase. Papers like LASSI, ParEval measure only one direction. | Low | Already supported. |
| Per-kernel tier classification | Identifies kernels where model ranking inverts (backprop anomaly: Gemini beats Llama). Publishable as evidence of domain-specific capability. | Low | Already observed and documented in `known-issues-archive.md`. |
| Translation complexity breakdown | single_file vs multi_to_single vs multi_to_multi stratification of pass rates. Few benchmarks distinguish structural complexity. | Low | `translation_complexity.csv` + `analyze_eval.py` already support this. |
| Pairwise Fisher's exact + Bonferroni correction for model comparison | Omnibus chi-squared + Bonferroni-corrected pairwise tests with effect sizes (Cohen's h, Cramer's V, odds ratios with Woolf CI). This is publication-grade statistical rigor for a benchmark paper. | Low | Already in `statistical_analysis.py`. |
| Cross-campaign correlation analysis | Per-model (Campaign 1 pass@1, Campaign 2 pass@3) scatter. If uncorrelated, that is the key finding: robustness and sampling capability are genuinely independent. | Medium | Requires Campaign 2 data. Analysis structure must be built. |
| AskSage / Argonne-hosted model evaluation | Access to models not publicly available via commercial APIs (national lab deployments). Creates unique comparison point unavailable to most benchmark papers. | High | Blocked on AskSage response schema confirmation. |
| Self-repair analysis: repair rate and repair value per model | What fraction of ultimately-PASS results required >1 attempt? Does self-repair disproportionately help certain kernels? Per-model repair rate already tracked in result JSONs via `total_attempts`. | Low | `total_attempts` field already captured. Analysis script exists in `evaluation.md` inline snippet. |

---

## Anti-Features

Features to deliberately NOT build for NeurIPS submission.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| BLEU / CodeBLEU metrics | Surface-level string similarity is not a correctness measure; the benchmark's entire value proposition is build-run-verify functional correctness. BabelTower (ICML 2022) used BLEU; ParBench's conjunction verification semantics is the differentiator. | Report compilation success rate + functional pass rate only |
| Wall-clock speedup ratios in main results | `baseline_wall_time_seconds` values are sub-millisecond (0.001s), making `speedup_ratio` numerically unreliable (bfs shows 0.002x). Known limitation documented in `known-issues-archive.md`. | Note as limitation; defer to future work with `nvprof`/`ncu` kernel timing |
| per-model "thinking" budget tuning | Disabling thinking uniformly is the correct control for capability comparison. Allowing different thinking budgets would introduce an inference-compute confound (the Gemini audit caught exactly this). | Force thinking OFF uniformly via API params; document in methods |
| Dashboard-driven result management | The static HTML dashboard is for visualization only; using it to manage which results count in statistics creates localStorage divergence bugs (documented incident 2026-03-25). | All denominator logic lives in Python analysis scripts only |
| New benchmark suites beyond current 5 | Adding HeCBench II, Polybench, etc. at this stage widens scope without improving per-suite depth. NeurIPS Datasets & Benchmarks track rewards depth and rigor. | Fix depth: complete all 5 suites × all model pairs |
| Pass@k for k > n | Mathematically undefined in the Chen et al. estimator when k > n. With n=3 samples (Campaign 2 default), only pass@1 and pass@3 are valid. Pass@2 is computable but adds little. | Report pass@1 and pass@3; document n=3 choice |
| Aggregate metrics across campaigns | A single "overall pass rate" blending Campaign 1 and Campaign 2 has no clear interpretation. The two campaigns have different temperatures, retry policies, and k values. | Always report campaigns separately; never blend |
| Re-running Campaign 1 results for existing models | The 1,248 Qwen results are the established baseline. Re-running with a different random state would invalidate comparison to earlier-reported numbers. | Use `--resume` to append; never overwrite existing results |

---

## Feature Dependencies

Campaign 2 pass@k computation depends on:
- `campaign_id` field being present in result JSONs (must be added before Campaign 2 runs)
- `sample_id` values 0, 1, 2 for n=3 samples per task (currently always 0 in Campaign 1)
- Pass@k estimator implementation in `statistical_analysis.py`

Cross-campaign correlation analysis depends on:
- Campaign 2 data existing for at least one model (currently none)
- Both campaigns using identical (source, target) pairs — enforced by shared spec corpus

AskSage adapter depends on:
- AskSage API response schema confirmed by researcher (currently BLOCKED)
- Thinking/reasoning disable mechanism confirmed for the hosted models

Fair multi-model denominator depends on:
- GPT-4.1 mini non-Rodinia invalid results (209/897) being re-run locally
- KNOWN_FAIL exclusion applied consistently across all models

---

## Answering the Four Questions

### 1. Table-Stakes for pass@k Evaluation Consistency

The non-negotiable requirements (HIGH confidence, grounded in Chen et al. 2021 HumanEval and ParEval HPDC 2024):

- **Same prompt, same spec** for every model on every task. ParBench already enforces this via spec-derived prompts. The anonymization map (generic filenames) must not change between models.
- **Same n per task** across models. With n=3 for Campaign 2, every model must produce exactly 3 samples for every (source, target) pair. Partial runs must be excluded from the denominator.
- **sample_id 0..n-1 per task** in each result JSON. Already exists as a field; Campaign 2 must actually use values 0, 1, 2 rather than always 0.
- **Temperature fixed at 0.7** for all Campaign 2 runs. Temperature is recorded in the result JSON; the analysis predicates `is_deterministic()` / `is_stochastic()` already check this field.
- **No cross-campaign mixing** in the pass@k denominator. Requires `campaign_id` tagging (currently absent).
- **Unbiased estimator formula**: `pass@k = 1 - C(n-c, k) / C(n, k)`. Must be macro-averaged per task, not micro-averaged. This is the Chen et al. (2021) formula; naive `(c/n)^k` is biased.

### 2. Metadata per Result for Fair Retrospective Model Comparison

The current result JSON schema already captures most required fields. The gaps are:

Fields already present and sufficient:
- `model`, `source_spec`, `target_spec`, `kernel`, `augment_level`, `temperature`, `sample_id`
- `overall_status`, `build_status`, `run_status`, `verify_status`
- `prompt_tokens`, `completion_tokens`, `llm_response_time_seconds`
- `total_attempts`, `max_retries`
- `translation_mode`, `translation_type`, `run_args_mode`, `verification_mode`
- `timestamp`, `finish_reason`

Fields missing or under-populated:
- `campaign_id` (e.g., `"campaign1"` or `"campaign2"`) — ABSENT. Required to partition results by campaign in analysis.
- `campaign_temperature` (the intended temperature for the campaign, as distinct from the recorded value) — could be derived but explicit is safer.
- `prompt_hash` (SHA of the system+user message, for verifying prompt identity across models) — ABSENT. Enables post-hoc verification that all models received equivalent prompts. LOW priority but HIGH value for reproducibility claims.
- `translated_files` — PRESENT in Campaign 1 results. Must remain present in Campaign 2.

### 3. Standard Statistical Methods for pass@k and pass@1 Reporting

Based on Chen et al. 2021 (HumanEval), ParEval (HPDC 2024), and the codebase's own `statistical_analysis.py`:

**For pass@1 (Campaign 1):**
- Wilson score 95% CI on every reported pass rate (already implemented)
- Pairwise Fisher's exact test with Bonferroni correction for model comparisons (already implemented)
- Cohen's h effect size for proportion differences (already implemented)
- Cochran-Armitage trend test for augmentation level effect (already implemented)
- McNemar's exact test for direction asymmetry (already implemented)

**For pass@k (Campaign 2):**
- Unbiased estimator: `pass@k = E[1 - C(n-c,k)/C(n,k)]` computed per task, macro-averaged across tasks (NOT yet implemented — the comment exists in `statistical_analysis.py` line 17 but no implementation)
- With n=3, k=3: the estimator degenerates — `pass@3 = c/n` because `C(n-c,3)/C(3,3)` counts arrangements. With k=3 and n=3, pass@3 equals 1 only when c=3, 0 otherwise. This is numerically fine but means pass@3 = fraction of tasks where ALL 3 samples pass.
- Wilson CI on the per-task pass@3 distribution (fraction of tasks with c=3 out of n=3)
- Cross-campaign comparison: Chi-squared on (Campaign 1 pass@1) vs (Campaign 2 pass@3) per model, with Cohen's h effect size

**Key invariant:** The denominator for all statistics must exclude results where EITHER source OR target spec is KNOWN_FAIL. This is the 1,120 non-KNOWN_FAIL baseline established for Campaign 1.

### 4. Campaign 1 vs Campaign 2 — What Each Enables

**Campaign 1** (temp=0, self-repair up to 3 retries, L0-L4 augmentation, pass@1):
- Measures **deterministic robustness**: given the model's greedy best output plus repair opportunities, does it produce functionally correct code?
- The self-repair dimension answers: "Can the model fix its own mistakes given compiler feedback?"
- The L0-L4 dimension answers: "Does pass rate decay when source code is obfuscated? Is the model pattern-matching or understanding?"
- Paper claims enabled:
  - "Model X achieves Y% pass@1 on Rodinia CUDA→OpenMP translation under deterministic conditions."
  - "Self-repair raises the pass rate from A% to B%, with model-specific repair rates of R%."
  - "Pass rates are level-invariant / show monotonic decay across L0-L4 (Cochran-Armitage trend z=Z, p=P)."
  - "Model X is significantly better than Model Y (Fisher's exact, p<0.05, Cohen's h=H, 'medium' effect)."

**Campaign 2** (temp=0.7, single-shot no self-repair, L0 only, k=3 samples, pass@k=3):
- Measures **stochastic sampling capability**: across multiple independent samples at non-zero temperature, does any sample succeed?
- No self-repair means the metric isolates generation quality from repair heuristics.
- L0 only means the source code is unmodified — eliminates augmentation as a variable.
- Paper claims enabled:
  - "Model X achieves Y% pass@3 on Rodinia CUDA→OpenMP, compared to Z% pass@1 in Campaign 1."
  - "Models with high Campaign 1 pass@1 do / do not correlate with high Campaign 2 pass@3 (Pearson r=R, p=P), showing that robustness and sampling diversity are [correlated/orthogonal] capabilities."
  - "For task T, Model X fails deterministically (Campaign 1 pass@1=0) but succeeds stochastically (Campaign 2 pass@3 > 0), suggesting the model knows the solution but requires re-sampling."
  - The k=3 constraint: with n=3 samples, the unbiased estimator for pass@3 is c=n all passing. This is a strict capability bar: the model must succeed on every sample. This is interpretable as "reliability" rather than "luck."

**What each campaign CANNOT claim:**
- Campaign 1 CANNOT claim performance diversity or temperature robustness — it is a single best-of-one-with-repair.
- Campaign 2 CANNOT claim repair capability or augmentation robustness — it is raw generation quality.
- Neither campaign claims wall-clock performance (speedup ratio) — timing data is unreliable at sub-millisecond baselines.

---

## Sources

- Chen et al. 2021, "Evaluating Large Language Models Trained on Code" (HumanEval): https://arxiv.org/pdf/2107.03374 — establishes pass@k unbiased estimator formula
- Nichols et al. 2024, "Can Large Language Models Write Parallel Code?" (ParEval, HPDC 2024): https://pssg.cs.umd.edu/assets/papers/2024-06-pareval-hpdc.pdf — HPC-specific pass@1 methodology
- LASSI (2024): https://arxiv.org/html/2407.01638 — self-correcting pipeline for parallel code translation
- CodeRosetta NeurIPS 2024: https://proceedings.neurips.cc//paper_files/paper/2024/hash/b6edb87876bec4ac2260bffa083cb992-Abstract-Conference.html — NeurIPS D&B track precedent for parallel code translation
- HPC-Coder-v2 (2024): https://arxiv.org/abs/2412.15178 — multi-model HPC code benchmark
- Statistical methods in codebase: `/home/samyak/Desktop/parbench_sam/scripts/analysis/statistical_analysis.py` (Wilson CI, Fisher's exact, Cochran-Armitage, McNemar — HIGH confidence, directly verified)
- Existing result schema: `/home/samyak/Desktop/parbench_sam/results/evaluation/together-qwen-3.5-397b-a17b/rodinia-bfs-cuda-to-rodinia-bfs-omp.json` (directly inspected)
- Known gaps: `.claude/rules/evaluation.md`, `.claude/rules/known-issues.md`, `.planning/PROJECT.md`
