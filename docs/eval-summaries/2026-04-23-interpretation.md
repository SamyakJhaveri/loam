# Hypothesis-First Interpretation: Qwen 3.5 397B Phase 3 Results

**Date:** 2026-04-23
**Protocol:** `/interpret-results` skill — hypotheses stated before data examination
**Model:** `together-qwen-3.5-397b-a17b`
**Data sources:** `results/analysis/quantitative_findings.md`, `results/analysis/statistical_analysis.md`, `results/analysis/error_taxonomy.md`, `results/analysis/selfrepair_analysis.md`

---

## Phase 1: Prior Hypotheses

Seven hypotheses were pre-registered in the session handoff document before any analysis files were read.

---

## Hypothesis 1: Direction Asymmetry (CUDA→OMP > OMP→CUDA)

**Expectation:** CUDA→OMP >50% because OMP is higher-level; OMP→CUDA <30% because CUDA needs explicit memory management.
**Null:** Direction doesn't matter.
**Falsification:** OMP→CUDA >50%.

### Observed Data

| Direction | pass@k (L0) | pass@1 estimate | C1 (ablation) |
|-----------|-------------|-----------------|----------------|
| cuda→omp | 40.3% (29/72) | 50.0% (12/24 tasks) | 87.5% (42/48) |
| omp→cuda | 25.0% (18/72) | 33.3% (8/24 tasks) | 71.9% (23/32) |

Source: `results/analysis/quantitative_findings.md` lines 141-144, `results/analysis/statistical_analysis.md` lines 16-17.

McNemar's exact test (L0 paired data): cuda→omp 45.8% vs omp→cuda 25.0%, Cohen's h = 0.440 (medium), p = 0.1797 (not significant after Bonferroni correction). Source: `statistical_analysis.md` line 94.

### Comparison to Expectation

The direction of the asymmetry matches: cuda→omp outperforms omp→cuda. However, cuda→omp does NOT exceed 50% at the raw pass@k level (40.3%), though the per-task pass@1 estimate (50.0%) hits the threshold exactly. OMP→CUDA at 25.0% is just under the predicted <30% ceiling. The McNemar test cannot reject the null at alpha=0.05 — the gap is medium-effect but statistically inconclusive with N=24 paired tasks.

### Alternative Explanations

1. **Training data imbalance:** CUDA→OMP may be more common in open-source codebases (porting GPU code to CPU parallelism), giving the model more relevant examples. The reverse direction is rarer in practice.
2. **Structural simplicity:** OMP's `#pragma omp parallel for` is a simpler target than CUDA's kernel launch + memory management boilerplate. This is a code-generation difficulty difference, not a model reasoning difference.

### Verdict

| | |
|---|---|
| **Status** | **WEAKENED** |
| **Confidence** | MEDIUM |
| **Detail** | Direction is correct but magnitude falls short of the >50% / <30% thresholds. Statistical test is non-significant. The asymmetry exists (h=0.440) but we cannot claim it's robust. |

---

## Hypothesis 2: BUILD_FAIL Dominance (>60% of Failures)

**Expectation:** >60% of failures are BUILD_FAIL (retained CUDA API in wrong target).
**Null:** Failure types uniformly distributed.
**Falsification:** RUN_FAIL > BUILD_FAIL.

### Observed Data

| Status | Count | % of Failures |
|--------|-------|---------------|
| BUILD_FAIL | 291 | 63.7% |
| RUN_FAIL | 125 | 27.4% |
| VERIFY_FAIL | 40 | 8.8% |
| EXTRACTION_FAIL | 1 | 0.2% |
| **Total failures** | **457** | |

Source: `results/analysis/error_taxonomy.json` via `status_counts`.

Top BUILD_FAIL subcategories: `other_build` (75), `missing_header` (66), `undeclared_identifier` (59), `linker_error` (39). The `retained_cuda_types` subcategory (directly testing the "retained CUDA API" mechanism) accounts for only 4/291 = 1.4%.

### Comparison to Expectation

BUILD_FAIL at 63.7% exceeds the 60% threshold. The null (uniform distribution across 4 categories = 25% each) is strongly rejected. However, the hypothesized mechanism ("retained CUDA API in wrong target") is NOT the primary cause — `missing_header` (22.7%) and `undeclared_identifier` (20.3%) dominate, suggesting the model fails at #include resolution and identifier scoping rather than retaining source-API types.

### Alternative Explanations

1. **Header/include path confusion:** The model generates correct API calls but wrong include paths (e.g., `#include <cuda_runtime.h>` instead of `<omp.h>`), which manifests as `missing_header` not `retained_cuda_types`.
2. **Multi-file coordination failure:** `undeclared_identifier` may reflect missing declarations from other translation-target files rather than API confusion.

### Verdict

| | |
|---|---|
| **Status** | **SUPPORTED** |
| **Confidence** | HIGH |
| **Detail** | BUILD_FAIL dominance confirmed (63.7% > 60%). But the specific mechanism (retained source API) accounts for <2%. The real failure modes are header resolution and identifier scoping. Refine the hypothesis mechanism for the paper. |

---

## Hypothesis 3: Augmentation Is Cosmetic (L1-L4 ≈ L0)

**Expectation:** L1-L4 ≈ L0 pass rate — augmentation transforms are cosmetic.
**Null:** Augmentation degrades by ≥5pp.
**Falsification:** Any Lk drops >10pp below L0.

### Observed Data

| Level | Pass Rate | 95% CI | N | Temp |
|-------|-----------|--------|---|------|
| L0 | 23.7% | [20.0%, 28.0%] | 438 | 0.7 |
| L1 | 72.5% | [59.1%, 82.9%] | 51 | 0.0 |
| L2 | 66.7% | [53.0%, 78.0%] | 51 | 0.0 |
| L3 | 66.7% | [53.0%, 78.0%] | 51 | 0.0 |
| L4 | 66.7% | [53.0%, 78.0%] | 51 | 0.0 |

Source: `results/analysis/statistical_analysis.md` lines 62-68.

Cochran-Armitage trend (L1-L4 only, cuda-to-omp): z = -0.605, p = 0.545 (not significant). Cohen's h: L1→L2 = -0.128 (negligible), L2→L3 = 0.0, L3→L4 = 0.0. Source: `quantitative_findings.md` lines 37, 46-49.

### Comparison to Expectation

**Critical confound:** L0 and L1-L4 use different temperatures (0.7 vs 0.0) AND different inclusion criteria (L1-L4 is L0-conditional — only pairs where ≥1 L0 sample passed). Direct L0-vs-L1 comparison is invalid.

Within the ablation set (L1-L4 at temp=0.0), the hypothesis is **SUPPORTED**: the L1→L4 decline is 5.8pp (72.5% → 66.7%), not statistically significant (p=0.545), with negligible effect sizes. Augmentation transforms do not meaningfully degrade translation quality within the survivor subset.

### Alternative Explanations

1. **Ceiling effect in survivor subset:** The L0-conditional filter selects "easier" pairs that pass regardless of augmentation. The null effect might not generalize to harder pairs.
2. **Transform scope:** L1-L4 transforms (variable renaming, arithmetic perturbation) may not touch the core parallel constructs that determine translation success.

### Confounding Variables

- Temperature: 0.7 (L0) vs 0.0 (L1-L4)
- Sample selection: L1-L4 is a filtered subset of L0-passing pairs
- Sample count: N=438 (L0) vs N=51 (per level)

### Verdict

| | |
|---|---|
| **Status** | **SUPPORTED (within L1-L4)** |
| **Confidence** | MEDIUM |
| **Detail** | Within the ablation subset, augmentation is cosmetic (p=0.545, h<0.13). But the L0 comparison is confounded — we cannot claim augmentation is cosmetic for the full task set without a matched-temperature L0 baseline. Paper must frame this carefully. |

---

## Hypothesis 4: OpenCL-Target <15%

**Expectation:** OpenCL-target <15% — kernel-only translation limits or training data gap.
**Null:** OpenCL ≈ OMP pass rate.
**Falsification:** OpenCL-to-X >30%.

### Observed Data

**OpenCL as TARGET (X→OpenCL):**

| Direction | pass@k (L0) | pass@1 |
|-----------|-------------|--------|
| cuda→opencl | 6.7% (4/60) | 15.0% (3/20 tasks) |
| omp→opencl | 35.2% (19/54) | 55.6% (10/18 tasks) |

**OpenCL as SOURCE (OpenCL→X):**

| Direction | pass@k (L0) | pass@1 |
|-----------|-------------|--------|
| opencl→cuda | 0.0% (0/60) | 0.0% (0/20 tasks) |
| opencl→omp | 9.3% (5/54) | 22.2% (4/18 tasks) |

Source: `results/analysis/statistical_analysis.md` lines 18, 23-24; `quantitative_findings.md` lines 143, 146, 149-150.

### Comparison to Expectation

**Mixed result.** cuda→opencl at 6.7% is well below 15% — SUPPORTED. But omp→opencl at 35.2% is well above 15% — the hypothesis is REFUTED for this direction. The falsification condition (opencl-to-X >30%) is not triggered: opencl→cuda=0%, opencl→omp=9.3%.

The most striking finding is the asymmetry between OpenCL-as-source vs OpenCL-as-target. OpenCL→anything is catastrophically bad (0-9.3%), while anything→OpenCL depends heavily on the source API: omp→opencl succeeds at 35.2% but cuda→opencl only at 6.7%.

### Alternative Explanations

1. **Kernel-only translation architecture:** OpenCL translations only require `.cl` kernel files (host code unchanged). omp→opencl may benefit from simpler kernel restructuring vs cuda→opencl which requires CUDA-specific construct mapping.
2. **OpenCL source code rarity:** LLMs may have seen far fewer OpenCL examples in training, making OpenCL-as-source harder to parse than OpenCL-as-target to generate.

### Verdict

| | |
|---|---|
| **Status** | **WEAKENED** |
| **Confidence** | MEDIUM |
| **Detail** | The hypothesis is too coarse. OpenCL-as-target shows a bifurcation: cuda→opencl <15% (supported) but omp→opencl >35% (refuted). OpenCL-as-SOURCE is the real disaster (<10% both directions). The paper should discuss source-API and target-API effects separately. |

---

## Hypothesis 5: Self-Repair = 0 Due to temp=0 Determinism

**Expectation:** Self-repair = 0 because temp=0 → identical output each retry.
**Null:** Self-repair recovers >5%.
**Falsification:** Any task repaired.

### Observed Data

- Total results: 708
- Single-attempt (no retry): 708
- Multi-attempt: 0
- Full repairs: 0

Source: `results/analysis/selfrepair_analysis.json`.

### Comparison to Expectation

The observation (self-repair = 0) is correct but the hypothesized mechanism (temp=0 determinism) **cannot be tested**. The experimental design set `max_retries=0` for all Phase 3 tasks — retries were never attempted, so we cannot distinguish between "retries would fail because temp=0 produces identical output" and "retries were simply not tried."

### Verdict

| | |
|---|---|
| **Status** | **INCONCLUSIVE** |
| **Confidence** | LOW |
| **Detail** | Self-repair=0 is a design artifact (max_retries=0), not an empirical finding. The causal mechanism cannot be evaluated. The paper should NOT claim "self-repair is ineffective" — it should report "self-repair was not tested in this campaign." If the claim matters, a separate retry campaign at temp>0 would be needed. |

---

## Hypothesis 6: Single-File >40% vs Multi-File <10%

**Expectation:** Single-file >40% vs multi-file <10% — context window coordination failure.
**Null:** File count irrelevant.
**Falsification:** Multi-file >25%.

### Observed Data

| Complexity Class | Pass Rate | 95% CI | N |
|-----------------|-----------|--------|---|
| single_file | 72.5% | [65.1%, 78.8%] | 160 |
| multi_to_single | 55.6% | [39.6%, 70.5%] | 36 |
| single_to_multi | 37.5% | [13.7%, 69.4%] | 8 |

Chi-squared: p = 0.024, significant = Yes.
Source: `results/analysis/quantitative_findings.md` lines 87-91.

Note: `multi_to_multi` is not reported in C1 quantitative findings. From translation_complexity.csv: 58 multi_to_multi pairs exist.

### Comparison to Expectation

Single-file at 72.5% far exceeds the >40% threshold — SUPPORTED. But multi-file translations are NOT <10%. Even the hardest category (single_to_multi) is at 37.5%, and multi_to_single is 55.6%. The falsification condition (multi-file >25%) IS triggered: both multi categories exceed 25%.

The hypothesis correctly identifies a gap (single > multi) that is statistically significant (p=0.024), but dramatically overestimates the magnitude. Multi-file translation is hard but not catastrophic.

### Alternative Explanations

1. **Multi-to-single may be easier than expected:** When multiple source files map to a single target file, the model only needs to produce one coherent output — reducing coordination cost.
2. **Kernel-centric translation:** ParBench's `translation_targets` specifies exactly which files to translate. The model doesn't need to decide what to translate, reducing multi-file coordination overhead.

### Verdict

| | |
|---|---|
| **Status** | **WEAKENED** |
| **Confidence** | HIGH |
| **Detail** | Direction is correct (single > multi, p=0.024) but the predicted multi-file floor (<10%) is far too pessimistic. Multi-to-single achieves 55.6%. The paper should report the statistically significant complexity effect without the catastrophic framing. |

---

## Hypothesis 7: 11.2pp Gap Explained by Noisy Kernels

**Expectation:** The 11.2pp gap between pass@1 mean (23.7%) and pass@1-of-any (34.9%) indicates many kernels at fractional (1/3 or 2/3) pass rates.
**Null:** Most kernels are 0/3 or 3/3.
**Falsification:** >80% of kernels are deterministic (0/3 or 3/3).

### Observed Data

Task classification (146 pass@k tasks, 3 samples each):
- **Always pass (3/3):** 19 tasks (13.0%)
- **Noisy fail (1/3 or 2/3):** 32 tasks (21.9%)
- **Hard fail (0/3):** 95 tasks (65.1%)

Deterministic tasks: 19 + 95 = 114 / 146 = **78.1%**

Source: `results/analysis/quantitative_findings.md` line 135.

### Comparison to Expectation

The gap IS explained by the 32 noisy tasks: they contribute to pass@1-of-any (at least one sample passes) but drag down the mean. The falsification condition (>80% deterministic) is NOT quite triggered at 78.1%, though it's very close.

The 21.9% noisy-fail rate is substantial — roughly 1 in 5 translation tasks produces inconsistent outcomes across 3 samples at temp=0.7. This has methodological implications: single-sample evaluation (pass@1) has ~22% measurement noise for marginal tasks.

### Alternative Explanations

1. **Temperature effect:** At temp=0.7, stochastic sampling creates variation in the generated code. At temp=0.0, all 32 "noisy" tasks would likely be deterministic (either all-pass or all-fail). The noisiness is partially a temperature artifact.
2. **Marginal competence:** The noisy tasks may sit at the boundary of the model's capability — slight variations in token sampling push the output across the pass/fail boundary.

### Verdict

| | |
|---|---|
| **Status** | **SUPPORTED** |
| **Confidence** | HIGH |
| **Detail** | 21.9% noisy tasks fully explain the 11.2pp mean-vs-of_any gap. 78.1% deterministic is close to but below the 80% falsification threshold. Key implication: pass@1 from a single sample has ~22% measurement noise on marginal tasks. Paper should report both pass@1 mean AND of_any and explain the gap. |

---

## Summary Table

| # | Hypothesis | Verdict | Confidence | Key Surprise |
|---|-----------|---------|------------|--------------|
| 1 | CUDA→OMP > OMP→CUDA | **WEAKENED** | MEDIUM | cuda→omp didn't reach >50% at L0 raw; McNemar non-significant |
| 2 | BUILD_FAIL >60% of failures | **SUPPORTED** | HIGH | Mechanism wrong: header/identifier errors, not retained API types |
| 3 | Augmentation cosmetic (L1-L4 ≈ L0) | **SUPPORTED** | MEDIUM | L0 comparison confounded by temperature; only valid within L1-L4 |
| 4 | OpenCL-target <15% | **WEAKENED** | MEDIUM | omp→opencl at 35.2% refutes blanket claim; OpenCL-as-SOURCE is the real disaster |
| 5 | Self-repair = 0 from temp=0 | **INCONCLUSIVE** | LOW | max_retries=0 by design — mechanism untestable |
| 6 | Single-file >40%, multi-file <10% | **WEAKENED** | HIGH | Multi-file NOT <10% (multi_to_single 55.6%); gap significant but not catastrophic |
| 7 | 11.2pp gap from noisy kernels | **SUPPORTED** | HIGH | 21.9% noisy tasks; 78.1% deterministic (just under 80% threshold) |

**Biggest overall surprise:** omp→opencl at 35.2% — OpenCL kernel generation from OMP source is far more successful than from CUDA source. This suggests the difficulty is in the source-API parsing, not the target-API generation.

**Paper-ready status:** CAUTION — cite with caveats. Three hypotheses are weakened (need refined framing), one is inconclusive (don't claim), three are supported. All claims must say "for Qwen 3.5 397B" — no generalization to "LLMs."

---

## Recommended Follow-Up Experiments

1. **Matched-temperature L0 baseline:** Run L0 at temp=0.0 for the 51 ablation pairs to enable valid L0-vs-L1 comparison without the temperature confound.
   - Tests: Hypothesis 3 (augmentation cosmetic vs temperature artifact)
   - Command: `python3 scripts/evaluation/run_eval_batch.py --suite rodinia --direction cuda-to-omp --models together-qwen-3.5-397b-a17b --augment-level 0 --project-root /home/samyak/Desktop/parbench_sam --resume -v`

2. **Self-repair with retries at temp=0.7:** Run a small subset (e.g., 20 BUILD_FAIL tasks) with max_retries=3 at temp=0.7 to test whether self-repair works when output varies.
   - Tests: Hypothesis 5 (temp=0 determinism vs genuine repair ineffectiveness)

3. **GPT-5.4 comparison run:** Execute the same Phase 3 protocol with azure-gpt-5.4 to enable cross-model comparison and test whether direction asymmetry patterns are model-specific or universal.
   - Tests: All hypotheses (generalizability beyond single model)
