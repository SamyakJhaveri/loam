# Statistical Methodology for SC26 Paper

**Author:** Statistician Agent (eval-campaign team)
**Date:** 2026-03-28
**Status:** Complete
**Addresses:** Audit weakness W4 (lack of statistical rigor)

---

## Table of Contents

1. [A. Confidence Intervals (Wilson Score)](#a-confidence-intervals)
2. [B. Hypothesis Testing](#b-hypothesis-testing)
3. [C. Effect Sizes](#c-effect-sizes)
4. [D. Pass@k Methodology](#d-passk-methodology)
5. [E. Sample Size Adequacy](#e-sample-size-adequacy)
6. [F. Augmentation Curves](#f-augmentation-curves)
7. [G. Profiling Feasibility](#g-profiling-feasibility)
8. [Appendix: Python Implementation](#appendix-python-implementation)

---

## A. Confidence Intervals

### Method: Wilson Score Interval

The Wilson score interval is preferred over the Wald (normal approximation) interval for
binary outcomes because it maintains correct coverage even for small n and proportions
near 0 or 1. The Wald interval (p +/- z*sqrt(p(1-p)/n)) can produce negative bounds
and has systematically poor coverage below n=40.

**Formula:**

```
lower = (p + z^2/(2n) - z * sqrt(p(1-p)/n + z^2/(4n^2))) / (1 + z^2/n)
upper = (p + z^2/(2n) + z * sqrt(p(1-p)/n + z^2/(4n^2))) / (1 + z^2/n)
```

Where z = 1.96 for 95% CI, p = observed proportion, n = sample size.

**Paper format:** `51.92% [43.8%, 59.9%]` (point estimate with bracketed 95% Wilson CI)

### Application to Current Data

| Cross-tabulation | Current n per cell | Projected n after campaign | CI width (typical) |
|---|---|---|---|
| Per-model overall | 156 | ~300+ | +/-7-8% |
| Per-direction (cuda-to-omp) | 85 (per model: ~19-95) | ~200+ | +/-10-15% |
| Per-direction (OpenCL dirs) | 5 per model | ~57 per model | +/-25% -> +/-13% |
| Per-kernel overall | 18 | ~54+ | +/-20-23% |
| Per-level (cuda-to-omp) | 57 (19 per model) | ~57 | +/-12-15% |
| Per (model x direction) | 5-95 | 19-95 | varies widely |
| Per (model x kernel) | 1-6 | 1-6 | N/A (too small) |

### Minimum Sample Size Rule

**Flag cells where n < 10 as "insufficient for reliable CI."**

Rationale: Wilson CIs remain valid for small n, but their width exceeds +/-30% when n < 10,
making point estimates uninformative. These cells should be reported in supplementary
materials only, with a footnote: "n < 10; CI width exceeds 30 percentage points."

### Current Data: Key CIs (Computed from eval_summary.json)

| Slice | Pass | Total | Rate | Wilson 95% CI |
|---|---|---|---|---|
| Claude Sonnet overall | 81 | 156 | 51.92% | [44.1%, 59.6%] |
| Gemini Flash Lite overall | 11 | 156 | 7.05% | [4.0%, 12.2%] |
| Groq Llama 3.3 70B overall | 13 | 156 | 8.33% | [4.9%, 13.7%] |
| cuda-to-omp overall | 62 | 255 | 24.31% | [19.5%, 29.9%] |
| omp-to-cuda overall | 9 | 63 | 14.29% | [7.7%, 25.0%] |
| L0 overall | 31 | 132 | 23.48% | [17.0%, 31.6%] |
| L4 overall | 16 | 84 | 19.05% | [12.0%, 29.0%] |

### Python Implementation

```python
from scipy.stats import norm
import numpy as np

def wilson_ci(successes: int, total: int, z: float = 1.96) -> tuple[float, float, float]:
    """Wilson score interval for binomial proportion.

    Returns (point_estimate, lower, upper).
    """
    if total == 0:
        return (0.0, 0.0, 0.0)
    p = successes / total
    denom = 1 + z**2 / total
    center = p + z**2 / (2 * total)
    spread = z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2))
    lower = (center - spread) / denom
    upper = (center + spread) / denom
    return (p, max(0.0, lower), min(1.0, upper))

# Example: Claude Sonnet overall
p, lo, hi = wilson_ci(81, 156)
print(f"Claude Sonnet: {p*100:.2f}% [{lo*100:.1f}%, {hi*100:.1f}%]")
# Output: Claude Sonnet: 51.92% [44.1%, 59.6%]
```

---

## B. Hypothesis Testing

### B1. Augmentation Level Independence

**Research question:** Does augmenting the source code (levels L0-L4) affect LLM
translation success rate?

**H0:** Pass rate is independent of augmentation level (L0, L1, L2, L3, L4).
**H1:** At least one augmentation level has a different pass rate.

**Test:** Pearson's chi-squared test on a 2x5 contingency table (pass/fail x L0-L4).

**Current data (all models, all directions with augmentation):**

| | L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| PASS | 31 | 20 | 21 | 17 | 16 |
| FAIL | 101 | 64 | 63 | 67 | 68 |
| Total | 132 | 84 | 84 | 84 | 84 |

Note: L0 has more observations (132 vs 84) because L0 includes non-cuda-to-omp directions.

**Restriction for cleaner test:** Use cuda-to-omp direction only, where all 5 levels
are present with equal kernel coverage:

| | L0 | L1 | L2 | L3 | L4 |
|---|---|---|---|---|---|
| PASS | 16 | 14 | 14 | 12 | 11 |
| FAIL | 41 | 43 | 43 | 45 | 46 |
| Total | 57 | 57 | 57 | 57 | 57 |

**Decision rules:**
- Expected cell count check: minimum expected = 57 * 67/285 = 13.4 > 5. Chi-squared valid.
- If ANY expected cell < 5: use Fisher's exact test (via `scipy.stats.fisher_exact` for 2x2,
  or Freeman-Halton via `scipy.stats.fisher_exact` is 2x2 only; for 2x5 use Monte Carlo
  permutation test via `scipy.stats.chi2_contingency` with simulated p-value, or
  `rpy2` bridge to R's `fisher.test(simulate.p.value=TRUE)`).
- df = (2-1)(5-1) = 4
- Reject H0 if p < alpha_corrected

**Per-model variant:** Run the test separately for each model (3 tests).
**Per-direction variant:** Run for cuda-to-omp only (primary), then omp-to-cuda if n sufficient.

**Bonferroni correction:**
- Total tests in B1: 3 (per-model) + 1 (overall) = 4 tests
- Corrected alpha: 0.05 / 4 = 0.0125

**Python:**

```python
from scipy.stats import chi2_contingency
import numpy as np

def test_level_independence(pass_counts, fail_counts, alpha=0.05, n_tests=1):
    """Test H0: pass rate independent of augmentation level.

    pass_counts: list of pass counts per level [L0, L1, L2, L3, L4]
    fail_counts: list of fail counts per level
    """
    table = np.array([pass_counts, fail_counts])
    chi2, p, dof, expected = chi2_contingency(table)
    alpha_corrected = alpha / n_tests

    # Check expected cell counts
    min_expected = expected.min()
    if min_expected < 5:
        # Use Monte Carlo permutation (simulated p-value)
        # scipy chi2_contingency doesn't support simulation directly;
        # use permutation approach
        from scipy.stats import permutation_test
        print(f"WARNING: min expected cell = {min_expected:.1f} < 5. "
              f"Consider Fisher-Freeman-Halton test.")

    return {
        'chi2': chi2,
        'p_value': p,
        'dof': dof,
        'min_expected': min_expected,
        'alpha_corrected': alpha_corrected,
        'reject_h0': p < alpha_corrected,
        'interpretation': (
            f"chi2({dof}) = {chi2:.3f}, p = {p:.4f}. "
            f"{'Reject' if p < alpha_corrected else 'Fail to reject'} H0 "
            f"at alpha = {alpha_corrected:.4f} (Bonferroni-corrected)."
        )
    }

# Current data: cuda-to-omp, all models
result = test_level_independence(
    pass_counts=[16, 14, 14, 12, 11],
    fail_counts=[41, 43, 43, 45, 46],
    alpha=0.05, n_tests=4
)
print(result['interpretation'])
# Expected: chi2(4) ~ 1.5, p ~ 0.83 -> fail to reject H0
# (augmentation levels do NOT significantly affect pass rate)
```

### B2. Model Comparison

**Research question:** Do the 3 models differ in translation success rate?

**H0:** All 3 models have equal pass rates (p_claude = p_gemini = p_groq).
**H1:** At least one model's pass rate differs.

**Omnibus test:** Pearson's chi-squared on 2x3 table:

| | Claude Sonnet | Gemini Flash Lite | Groq Llama 3.3 |
|---|---|---|---|
| PASS | 81 | 11 | 13 |
| FAIL | 75 | 145 | 143 |
| Total | 156 | 156 | 156 |

- df = (2-1)(3-1) = 2
- Expected cells: min expected = 156 * 105/468 = 35.0 >> 5. Chi-squared valid.

**Pairwise comparisons (post-hoc):** 3 pairs with Bonferroni correction.

| Pair | Test | Alpha |
|---|---|---|
| Claude vs Gemini | Fisher's exact (2x2) | 0.05/3 = 0.0167 |
| Claude vs Groq | Fisher's exact (2x2) | 0.0167 |
| Gemini vs Groq | Fisher's exact (2x2) | 0.0167 |

Note: Fisher's exact is preferred for pairwise comparisons even when chi-squared is valid,
because it gives exact p-values. For n=156 per group, both tests will agree.

**Python:**

```python
from scipy.stats import chi2_contingency, fisher_exact
import numpy as np

def test_model_comparison(model_data: dict, alpha=0.05):
    """Test H0: all models have equal pass rates.

    model_data: {model_name: (pass, total), ...}
    """
    models = list(model_data.keys())
    table = np.array([
        [model_data[m][0] for m in models],           # PASS row
        [model_data[m][1] - model_data[m][0] for m in models]  # FAIL row
    ])

    # Omnibus chi-squared
    chi2, p_omni, dof, expected = chi2_contingency(table)

    # Pairwise Fisher's exact with Bonferroni
    n_pairs = len(models) * (len(models) - 1) // 2
    alpha_pair = alpha / n_pairs
    pairwise = []
    for i in range(len(models)):
        for j in range(i+1, len(models)):
            pair_table = np.array([
                [model_data[models[i]][0], model_data[models[j]][0]],
                [model_data[models[i]][1] - model_data[models[i]][0],
                 model_data[models[j]][1] - model_data[models[j]][0]]
            ])
            odds_ratio, p_fisher = fisher_exact(pair_table)
            pairwise.append({
                'pair': f"{models[i]} vs {models[j]}",
                'odds_ratio': odds_ratio,
                'p_value': p_fisher,
                'significant': p_fisher < alpha_pair
            })

    return {
        'omnibus_chi2': chi2, 'omnibus_p': p_omni, 'dof': dof,
        'pairwise': pairwise, 'alpha_corrected': alpha_pair
    }

result = test_model_comparison({
    'claude-sonnet': (81, 156),
    'gemini-flash-lite': (11, 156),
    'groq-llama-3.3': (13, 156)
})
print(f"Omnibus: chi2({result['dof']}) = {result['omnibus_chi2']:.2f}, "
      f"p = {result['omnibus_p']:.2e}")
for pw in result['pairwise']:
    sig = "*" if pw['significant'] else "ns"
    print(f"  {pw['pair']}: OR={pw['odds_ratio']:.2f}, p={pw['p_value']:.2e} {sig}")
```

### B3. Direction Asymmetry

**Research question:** Is translating from API A to API B equally likely to succeed as
translating from B to A?

**H0:** Pass rate for A-to-B equals B-to-A (on the same kernels).
**H1:** The rates differ (directional asymmetry exists).

**Test:** McNemar's test (for paired binary data).

McNemar's test is appropriate here because each kernel appears in BOTH directions. We
classify each (kernel, model) pair into one of four cells:

| | A-to-B PASS | A-to-B FAIL |
|---|---|---|
| **B-to-A PASS** | a (both pass) | b (B-to-A only) |
| **B-to-A FAIL** | c (A-to-B only) | d (both fail) |

McNemar's statistic: chi2 = (b - c)^2 / (b + c), df = 1.
When b + c < 25, use exact binomial test (McNemar's exact).

**Direction pairs to test:**

| Pair | n_paired (at L0, per model) | n_paired (all models) | Test variant |
|---|---|---|---|
| cuda <-> omp | 19 per model | 57 | McNemar's exact (b+c likely < 25) |
| cuda <-> opencl | 5 per model | 15 | McNemar's exact |
| omp <-> opencl | 5 per model | 15 | McNemar's exact |

**Bonferroni correction:** 3 direction pairs x 3 models + 3 overall = 12 tests.
Alpha corrected = 0.05 / 12 = 0.00417.

**Current data availability:**
- cuda <-> omp at L0: All 19 kernels x 3 models = 57 paired observations. **SUFFICIENT.**
- cuda <-> opencl at L0: Only 5 kernels (XSBench) x 3 models = 15. **MARGINAL.**
- omp <-> opencl at L0: Only 5 kernels x 3 models = 15. **MARGINAL.**

**After campaign (adding OpenCL Rodinia directions):**
- cuda <-> opencl: ~19 kernels x 3 models = 57 paired. **SUFFICIENT.**
- omp <-> opencl: ~19 kernels x 3 models = 57 paired. **SUFFICIENT.**

**Python:**

```python
from statsmodels.stats.contingency_tables import mcnemar
import numpy as np

def test_direction_asymmetry(paired_results: list[tuple[bool, bool]],
                              pair_name: str, alpha: float = 0.05,
                              n_tests: int = 1):
    """Test H0: no directional asymmetry in translation success.

    paired_results: list of (a_to_b_pass, b_to_a_pass) for each kernel-model pair.
    """
    # Build 2x2 contingency table
    a = sum(1 for (ab, ba) in paired_results if ab and ba)      # both pass
    b = sum(1 for (ab, ba) in paired_results if not ab and ba)   # B-to-A only
    c = sum(1 for (ab, ba) in paired_results if ab and not ba)   # A-to-B only
    d = sum(1 for (ab, ba) in paired_results if not ab and not ba) # both fail
    table = np.array([[a, b], [c, d]])

    alpha_corrected = alpha / n_tests
    discordant = b + c

    if discordant < 25:
        # Use exact McNemar's test (binomial)
        from scipy.stats import binomtest
        result = binomtest(b, discordant, 0.5, alternative='two-sided')
        p = result.pvalue
        method = "exact"
    else:
        # Use chi-squared McNemar's
        bunch = mcnemar(table, exact=False, correction=True)
        p = bunch.pvalue
        method = "chi-squared"

    return {
        'pair': pair_name,
        'table': {'both_pass': a, 'b_to_a_only': b,
                  'a_to_b_only': c, 'both_fail': d},
        'discordant': discordant,
        'method': method,
        'p_value': p,
        'alpha_corrected': alpha_corrected,
        'reject_h0': p < alpha_corrected,
        'interpretation': (
            f"{pair_name}: discordant pairs = {discordant} "
            f"(b={b}, c={c}), p = {p:.4f} ({method}). "
            f"{'Reject' if p < alpha_corrected else 'Fail to reject'} H0 "
            f"at alpha = {alpha_corrected:.4f}."
        )
    }
```

---

## C. Effect Sizes

Effect sizes quantify the magnitude of observed differences, independent of sample size.
They are essential for the paper because:
1. A statistically significant difference with a tiny effect size is not practically interesting.
2. SC26 reviewers expect effect size reporting per APA guidelines.
3. Effect sizes allow comparison across studies (e.g., our model gap vs. CodeRosetta's).

### C1. Cramer's V (for chi-squared tests)

**Formula:** V = sqrt(chi2 / (n * (min(r, c) - 1)))

Where chi2 is the chi-squared statistic, n is total observations, r and c are table dimensions.

**Interpretation thresholds (df* = min(r,c) - 1):**

| df* | Small | Medium | Large |
|---|---|---|---|
| 1 | 0.10 | 0.30 | 0.50 |
| 2 | 0.07 | 0.21 | 0.35 |
| 3 | 0.06 | 0.17 | 0.29 |
| 4 | 0.05 | 0.15 | 0.25 |

**Application:** Report Cramer's V for every chi-squared test in B1 (level independence,
df*=4) and B2 (model comparison, df*=1).

**Expected for B2 (model comparison):** Claude at 52% vs Gemini/Groq at 7-8% implies
V ~ 0.45-0.50, which is a **large** effect size. This is a strong result for the paper.

```python
def cramers_v(chi2: float, n: int, r: int, c: int) -> tuple[float, str]:
    """Compute Cramer's V and interpret."""
    df_star = min(r, c) - 1
    v = np.sqrt(chi2 / (n * df_star))
    # Thresholds from Cohen (1988) for df*=1
    if df_star == 1:
        thresholds = [(0.1, 'negligible'), (0.3, 'small'), (0.5, 'medium')]
    elif df_star == 2:
        thresholds = [(0.07, 'negligible'), (0.21, 'small'), (0.35, 'medium')]
    else:
        thresholds = [(0.06, 'negligible'), (0.17, 'small'), (0.29, 'medium')]
    label = 'large'
    for thresh, name in thresholds:
        if v < thresh:
            label = name
            break
    return (v, label)
```

### C2. Odds Ratios with Woolf's Method CI

**Formula:**
- OR = (a * d) / (b * c) for 2x2 table [[a, b], [c, d]]
- ln(OR) has standard error: SE = sqrt(1/a + 1/b + 1/c + 1/d) (Woolf's method)
- 95% CI for ln(OR): ln(OR) +/- 1.96 * SE
- Exponentiate for CI on OR scale

**Application:** Report for each pairwise model comparison in B2.

**Edge case:** When any cell is 0, add 0.5 to all cells (Haldane-Anscombe correction).

```python
def odds_ratio_ci(table_2x2, z=1.96):
    """Odds ratio with Woolf's method CI (Haldane-corrected)."""
    a, b, c, d = table_2x2.flatten()
    # Haldane correction if any cell is zero
    if min(a, b, c, d) == 0:
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    OR = (a * d) / (b * c)
    log_OR = np.log(OR)
    SE = np.sqrt(1/a + 1/b + 1/c + 1/d)
    ci_lower = np.exp(log_OR - z * SE)
    ci_upper = np.exp(log_OR + z * SE)
    return {'OR': OR, 'CI_lower': ci_lower, 'CI_upper': ci_upper, 'SE': SE}
```

### C3. Cohen's h (for comparing two proportions)

**Formula:** h = 2 * arcsin(sqrt(p1)) - 2 * arcsin(sqrt(p2))

**Interpretation thresholds:**
- |h| < 0.20: small effect
- 0.20 <= |h| < 0.80: medium effect
- |h| >= 0.80: large effect

**Application:** Report for direction asymmetry (B3) and pairwise model comparisons.

**Expected:**
- Claude (52%) vs Gemini (7%): h = 2*arcsin(sqrt(0.52)) - 2*arcsin(sqrt(0.07)) = 1.06.
  This is a **large** effect.
- cuda-to-omp (24%) vs omp-to-cuda (14%): h = 0.25. This is a **medium** effect.

```python
def cohens_h(p1: float, p2: float) -> tuple[float, str]:
    """Cohen's h for comparing two proportions."""
    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
    abs_h = abs(h)
    if abs_h < 0.20:
        label = 'small'
    elif abs_h < 0.80:
        label = 'medium'
    else:
        label = 'large'
    return (h, label)

# Claude vs Gemini
h, label = cohens_h(81/156, 11/156)
print(f"Cohen's h = {h:.3f} ({label})")
# Output: Cohen's h = 1.064 (large)
```

---

## D. Pass@k Methodology

### Background

Pass@k (from Chen et al. 2021, "Evaluating Large Language Models Trained on Code") is the
standard metric for code generation benchmarks. It estimates the probability that at least
one of k sampled completions passes, using an unbiased estimator.

### Unbiased Estimator

**Formula:**
```
pass@k = 1 - C(n-c, k) / C(n, k)
```

Where:
- n = total samples generated per task
- c = number of correct (PASS) samples among n
- k = number of samples the user "selects" (budget)
- C(a, b) = binomial coefficient "a choose b"

For numerical stability (avoiding large factorials), use:
```
pass@k = 1 - prod((n-c-i) / (n-i) for i in range(k))
```

### Recommended Configuration

| Parameter | Value | Rationale |
|---|---|---|
| n (samples per task) | 10 | Balances cost vs CI width; standard in HumanEval/SWE-bench |
| k values to report | 1, 3, 5| k=1 = greedy, k=3 = practical budget, k=5 = generous budget |
| Temperature | 0.8 | Standard for pass@k (higher diversity than greedy); Chen et al. default |
| Top-p | 0.95 | Standard nucleus sampling |

### Why Not Our Current Setup

Our current evaluation uses temperature=0 (greedy decoding) with max_retries=2.
This gives us effectively pass@1 with self-repair, NOT pass@k.

**Critical distinction:**
- Current results: pass@1 with up to 2 retry attempts (self-repair via error feedback)
- Pass@k: k independent samples at temperature > 0, no error feedback between samples

The self-repair mechanism is a **different** metric. Both should be reported:
- **Pass@1 (greedy + self-repair)**: Our current 22.44%. Report as "pass rate with 2-attempt self-repair."
- **Pass@k (independent sampling)**: Requires new runs at temperature=0.8 with n=10 samples.

### Pilot Study Design

Before committing to full pass@k evaluation (expensive: 10x current cost), run a pilot:

| Parameter | Value |
|---|---|
| Kernels | 5 diverse: backprop (easy), hotspot3d (medium), bfs (hard), lavamd (medium), nw (hard) |
| Models | All 3: claude-sonnet, gemini-flash-lite, groq-llama |
| Samples per task | n = 10 |
| Direction | cuda-to-omp only |
| Augmentation | L0 only |
| Temperature | 0.8 |
| Total API calls | 5 kernels x 3 models x 10 samples = 150 calls |

**Decision gate:** If pass@3 is within 5 percentage points of pass@1 (greedy) for all
models, independent sampling adds little information over self-repair. Report pass@1 with
self-repair as the primary metric and pass@k as supplementary.

### Python Implementation

```python
from math import comb
import numpy as np

def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator (Chen et al. 2021).

    n: total samples
    c: number passing
    k: budget
    """
    if n - c < k:
        return 1.0
    # Numerically stable version
    return 1.0 - np.prod([(n - c - i) / (n - i) for i in range(k)])

def pass_at_k_table(task_results: dict[str, tuple[int, int]],
                     k_values: list[int] = [1, 3, 5]) -> dict:
    """Compute pass@k for multiple tasks.

    task_results: {task_id: (n_total, n_correct), ...}
    Returns: {k: mean_pass_at_k, ...}
    """
    result = {}
    for k in k_values:
        scores = [pass_at_k(n, c, k) for n, c in task_results.values()]
        result[k] = {
            'mean': np.mean(scores),
            'std': np.std(scores),
            'per_task': dict(zip(task_results.keys(), scores))
        }
    return result

# Example: if backprop gets 7/10 correct samples
print(f"pass@1 = {pass_at_k(10, 7, 1):.3f}")  # 0.700
print(f"pass@3 = {pass_at_k(10, 7, 3):.3f}")  # 0.992
```

---

## E. Sample Size Adequacy

### Current Data Inventory (from eval_summary.json, 2026-03-28)

| Slice | n | Adequate for CI? | Adequate for chi2? |
|---|---|---|---|
| **Per-model overall** | 156 each | YES (width ~16pp) | YES |
| **Per-direction: cuda-to-omp** | 255 (85/model) | YES | YES |
| **Per-direction: omp-to-cuda** | 63 (21/model) | YES (width ~22pp) | MARGINAL per-model |
| **Per-direction: cuda-to-opencl** | 15 (5/model) | NO (n<10/model) | NO |
| **Per-direction: all other** | 15 each (5/model) | NO | NO |
| **Per-kernel overall** | 18 each | MARGINAL (width ~23pp) | MARGINAL |
| **Per-kernel x model** | 6 each | NO | NO |
| **Per-level: cuda-to-omp** | 57 each (19/model) | YES | YES |
| **Per (model x level): cuda-to-omp** | 19 each | YES (width ~22pp) | MARGINAL |

### Minimum Detectable Effect Size at 80% Power

For a two-proportion z-test at alpha=0.05 (two-sided), 80% power:

| n per group | Min detectable diff (from 50%) | Min detectable diff (from 10%) |
|---|---|---|
| 5 | 62pp | 34pp |
| 15 | 36pp | 20pp |
| 19 | 32pp | 18pp |
| 57 | 18pp | 10pp |
| 84 | 15pp | 8pp |
| 156 | 11pp | 6pp |

**Interpretation:** With n=19 per model per level (cuda-to-omp), we can detect a level
effect of ~32pp from a 50% baseline (Claude) but only ~18pp from a 10% baseline
(Gemini/Groq). The Gemini/Groq cells are underpowered for level effects.

### Projected Data After Campaign

The eval campaign adds:
1. **OpenCL Rodinia directions** (~6 new directions x 19 kernels x 3 models = ~342 tasks)
2. **Augmented levels L1-L4 for new directions** (~4 levels x 6 directions x 19 x 3 = ~1368)

This substantially improves:

| Slice | Current n | Projected n | Improvement |
|---|---|---|---|
| cuda-to-opencl per model | 5 | ~95 (19 kernels x 5 levels) | 19x |
| opencl-to-cuda per model | 5 | ~95 | 19x |
| Per (model x dir x level) cells | 0-19 | 19 | All cells filled |
| Per-kernel x model (all dirs) | 6 | ~18 | 3x |

### Which Cells Belong in Main Paper vs. Supplementary

**Main paper (n >= 15 per cell):**
- Per-model overall pass rates with Wilson CIs
- Per-direction pass rates (aggregated across models) for the 6 standard directions
- Model comparison chi-squared test and pairwise Fisher's exact
- Augmentation curve (cuda-to-omp only, per-model, n=19 per cell)
- Direction asymmetry for cuda<->omp (n=57 paired)
- Failure taxonomy proportions with Wilson CIs

**Supplementary materials (n < 15 per cell, or exploratory):**
- Per-kernel pass rates (n=6-18 per cell)
- Per (model x kernel) breakdown (n=1-6 per cell)
- omp_target directions (case study, n=5 per model)
- Per-kernel tier analysis (descriptive, no inferential tests)
- Pass@k pilot results (if conducted)

**Python: power analysis**

```python
from statsmodels.stats.power import NormalIndPower

def min_detectable_effect(n_per_group, alpha=0.05, power=0.80, baseline=0.5):
    """Minimum detectable difference from baseline proportion."""
    analysis = NormalIndPower()
    # effect_size is Cohen's h
    h = analysis.solve_power(nobs1=n_per_group, alpha=alpha, power=power,
                              ratio=1.0, alternative='two-sided')
    # Convert h back to proportion difference (approximate)
    p2_upper = np.sin(np.arcsin(np.sqrt(baseline)) + h/2)**2
    diff = p2_upper - baseline
    return {'cohens_h': h, 'approx_diff': diff, 'n': n_per_group}
```

---

## F. Augmentation Curves (Addresses Audit W8)

### Design

**Goal:** Quantify how source code augmentation (obfuscation levels L0-L4) affects LLM
translation success, controlling for direction and kernel.

**Restriction:** cuda-to-omp only. This eliminates the direction confound (other directions
are only available at L0 currently) and ensures balanced design (same 19 kernels at every level).

### Data Structure

For each of 3 models x 19 kernels x 5 levels = 285 observations:
- Binary outcome: PASS/FAIL
- Independent variable: augmentation level (ordinal: L0 < L1 < L2 < L3 < L4)
- Stratifying variable: model

### Analysis 1: Per-Model Pass Rate with Wilson CIs

For each model, compute pass rate at each level with Wilson 95% CI (n=19 per cell).

**Current data (cuda-to-omp):**

| Level | Claude (n=19) | Gemini (n=19) | Groq (n=19) | All (n=57) |
|---|---|---|---|---|
| L0 | 10/19 = 52.6% | 3/19 = 15.8% | 3/19 = 15.8% | 16/57 = 28.1% |
| L1 | 9/19 = 47.4% | 3/19 = 15.8% | 2/19 = 10.5% | 14/57 = 24.6% |
| L2 | 9/19 = 47.4% | 3/19 = 15.8% | 2/19 = 10.5% | 14/57 = 24.6% |
| L3 | 8/19 = 42.1% | 2/19 = 10.5% | 2/19 = 10.5% | 12/57 = 21.1% |
| L4 | 10/19 = 52.6% | 0/19 = 0.0% | 1/19 = 5.3% | 11/57 = 19.3% |

**Observation:** Claude shows no clear trend (~42-53%, fluctuating). Gemini and Groq show
a possible downward trend at L4, but n=19 per cell means wide CIs (~+/-20pp). The pattern
is consistent with the level-invariance claim from augmentation baseline testing.

### Analysis 2: Cochran-Armitage Trend Test

Tests whether there is a **monotonic trend** in pass rate across ordered levels.

**H0:** No linear trend in pass rate across L0-L4.
**H1:** There is a linear (increasing or decreasing) trend.

This is more powerful than chi-squared for detecting ordered effects because it uses the
ordinal structure of the levels, rather than treating them as nominal categories.

**Scores:** L0=0, L1=1, L2=2, L3=3, L4=4 (equally spaced).

**Application:**
- Run per-model (3 tests) and overall (1 test). Bonferroni: alpha = 0.05/4 = 0.0125.
- Report the trend slope (decrease in pass rate per level) with CI.

```python
from scipy.stats import norm
import numpy as np

def cochran_armitage_trend(pass_counts, total_counts, scores=None):
    """Cochran-Armitage test for trend in binomial proportions.

    pass_counts: array of successes per group
    total_counts: array of totals per group
    scores: ordinal scores (default: 0, 1, 2, ...)
    """
    k = len(pass_counts)
    if scores is None:
        scores = np.arange(k)
    n = np.array(total_counts, dtype=float)
    r = np.array(pass_counts, dtype=float)
    N = n.sum()
    R = r.sum()
    p_bar = R / N

    # Weighted mean of scores
    t_bar = np.sum(n * scores) / N

    # Numerator
    numerator = np.sum(scores * (r - n * p_bar))

    # Denominator
    denominator_sq = p_bar * (1 - p_bar) * (np.sum(n * scores**2) - N * t_bar**2)
    denominator = np.sqrt(denominator_sq)

    if denominator == 0:
        return {'z': 0, 'p_value': 1.0, 'trend_direction': 'none'}

    z = numerator / denominator
    p_value = 2 * norm.sf(abs(z))  # two-sided

    return {
        'z': z,
        'p_value': p_value,
        'trend_direction': 'decreasing' if z < 0 else 'increasing',
        'interpretation': (
            f"z = {z:.3f}, p = {p_value:.4f}. "
            f"{'Significant' if p_value < 0.05 else 'No significant'} "
            f"{'decreasing' if z < 0 else 'increasing'} trend."
        )
    }

# All models, cuda-to-omp
result = cochran_armitage_trend(
    pass_counts=[16, 14, 14, 12, 11],
    total_counts=[57, 57, 57, 57, 57]
)
print(result['interpretation'])
# Expected: mild decreasing trend, likely not significant at n=57 per level
```

### Analysis 3: Plot Design

**Figure specification:**
- X-axis: Augmentation level (L0, L1, L2, L3, L4)
- Y-axis: Pass rate (0-100%)
- 3 curves: one per model (Claude = blue solid, Gemini = orange dashed, Groq = green dotted)
- Error bands: Wilson 95% CI as shaded region around each curve
- Annotations: n per point, horizontal dashed line at overall pass rate
- Caption: "Effect of source code augmentation on translation success rate (cuda-to-omp,
  19 Rodinia+XSBench kernels). Shaded bands show Wilson 95% confidence intervals."

**matplotlib code:**

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_augmentation_curves(model_data, output_path):
    """Plot augmentation level vs pass rate with Wilson CIs.

    model_data: {model_name: {level: (pass, total), ...}, ...}
    """
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    levels = ['L0', 'L1', 'L2', 'L3', 'L4']
    x = np.arange(len(levels))

    colors = {'claude-sonnet': '#2196F3', 'gemini-flash-lite': '#FF9800',
              'groq-llama-3.3': '#4CAF50'}
    styles = {'claude-sonnet': '-', 'gemini-flash-lite': '--', 'groq-llama-3.3': ':'}

    for model, level_data in model_data.items():
        rates, lowers, uppers = [], [], []
        for lv in levels:
            p, lo, hi = wilson_ci(*level_data[lv])
            rates.append(p * 100)
            lowers.append(lo * 100)
            uppers.append(hi * 100)

        color = colors.get(model, 'gray')
        style = styles.get(model, '-')
        ax.plot(x, rates, style, color=color, linewidth=2, label=model, marker='o')
        ax.fill_between(x, lowers, uppers, alpha=0.15, color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(levels)
    ax.set_xlabel('Augmentation Level')
    ax.set_ylabel('Pass Rate (%)')
    ax.set_ylim(-5, 100)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
```

---

## G. Profiling Feasibility

### Current Timing Data Assessment

**Source:** `run_time_seconds` field in PASS result JSONs + `baseline_wall_time_seconds`.

**Known limitation (from known-issues.md):**
- All 105 PASS results use `timing_method: "wall_time"`.
- `translated_cpu_time_seconds` and `translated_kernel_time_seconds` are `null` everywhere.
- `speedup_ratio` is computed from wall-clock times that include OS scheduling, I/O,
  memory allocation, and data transfer overhead.
- Sub-millisecond baseline wall times (e.g., nn at 0.001s) produce unreliable ratios.

### Publishability Assessment

**Wall-clock ratios are NOT publishable as performance data** in the SC26 paper.

Reasons:
1. Wall-clock time includes non-kernel overhead (malloc, file I/O, data transfer).
2. Single-run measurements (no warm-up, no repetition, no median).
3. Sub-millisecond baselines make ratios meaningless (dominated by measurement noise).
4. Different parallelism models (CUDA GPU vs OpenMP CPU) have fundamentally different
   overhead profiles -- wall-clock comparison conflates implementation quality with
   hardware difference.

### What CAN Be Published

1. **Qualitative performance category:** For PASS results, classify as:
   - "Correct and runs" (primary claim -- functional correctness)
   - Do NOT claim speedup or performance parity

2. **Runtime order-of-magnitude:** Report that translated OpenMP codes complete in
   "sub-second to single-digit seconds" to demonstrate they are not pathologically slow.

3. **Future work:** "Kernel-level profiling using nvprof/ncu (CUDA) and perf/omp_get_wtime
   (OpenMP) is planned for measuring translation-induced performance overhead."

### Paper Paragraph Template

> **Performance.** ParBench evaluates functional correctness (build + run + output
> verification), not performance parity. Wall-clock execution times for passing
> translations range from < 1 ms to ~2 s, confirming that LLM-generated OpenMP code
> is not pathologically inefficient. However, we do not report speedup ratios because
> (a) our single-run wall-clock measurements include non-kernel overhead (I/O, memory
> allocation), (b) comparing GPU kernel time to CPU thread time conflates translation
> quality with hardware capability, and (c) reliable performance comparison requires
> multi-run profiling with warm-up (via nvprof/ncu for CUDA, omp_get_wtime for OpenMP),
> which we leave to future work. Recent work on LLM-generated code profiling
> (TRACY, arXiv:2508.11468) demonstrates that automated profiling pipelines can be
> integrated with benchmark harnesses; extending ParBench with such profiling is a
> natural next step.

### Wall-Clock Summary Statistics (for supplementary only)

```python
def summarize_wall_clock(result_files: list[str]):
    """Compute descriptive stats for wall-clock times (supplementary material only)."""
    import json
    times = []
    for f in result_files:
        with open(f) as fp:
            d = json.load(fp)
        if d.get('overall_status') == 'PASS' and d.get('translated_wall_time_seconds'):
            times.append({
                'kernel': d['kernel'],
                'model': d['model'],
                'baseline_s': d.get('baseline_wall_time_seconds'),
                'translated_s': d.get('translated_wall_time_seconds'),
            })
    if not times:
        return {}
    translated = [t['translated_s'] for t in times if t['translated_s']]
    return {
        'n': len(translated),
        'median_s': np.median(translated),
        'min_s': min(translated),
        'max_s': max(translated),
        'note': 'Wall-clock only. NOT kernel time. NOT publishable as speedup.'
    }
```

---

## Appendix: Python Implementation

### Complete Analysis Script

The following script can be run against the eval results to produce all statistical
outputs for the paper. Save as `scripts/analysis/stat_analysis.py`.

```python
#!/usr/bin/env python3
"""Statistical analysis for SC26 paper.

Usage:
    python3 scripts/analysis/stat_analysis.py --results-dir results/evaluation/
"""
import json
import glob
import argparse
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact, norm
from math import comb
from collections import defaultdict
from pathlib import Path


# ── Wilson Score Interval ──────────────────────────────────────────

def wilson_ci(successes, total, z=1.96):
    if total == 0:
        return (0.0, 0.0, 0.0)
    p = successes / total
    denom = 1 + z**2 / total
    center = p + z**2 / (2 * total)
    spread = z * np.sqrt(p * (1 - p) / total + z**2 / (4 * total**2))
    return (p, max(0.0, (center - spread) / denom),
            min(1.0, (center + spread) / denom))


# ── Cramer's V ─────────────────────────────────────────────────────

def cramers_v(chi2, n, r, c):
    df_star = min(r, c) - 1
    if df_star == 0 or n == 0:
        return 0.0
    return np.sqrt(chi2 / (n * df_star))


# ── Cohen's h ──────────────────────────────────────────────────────

def cohens_h(p1, p2):
    return 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))


# ── Odds Ratio (Woolf) ────────────────────────────────────────────

def odds_ratio_woolf(table_2x2, z=1.96):
    a, b, c, d = [float(x) for x in table_2x2.flatten()]
    if min(a, b, c, d) == 0:
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    OR = (a * d) / (b * c)
    log_OR = np.log(OR)
    SE = np.sqrt(1/a + 1/b + 1/c + 1/d)
    return {'OR': OR, 'CI_lower': np.exp(log_OR - z * SE),
            'CI_upper': np.exp(log_OR + z * SE)}


# ── Pass@k ─────────────────────────────────────────────────────────

def pass_at_k(n, c, k):
    if n - c < k:
        return 1.0
    return 1.0 - np.prod([(n - c - i) / (n - i) for i in range(k)])


# ── Cochran-Armitage Trend ─────────────────────────────────────────

def cochran_armitage(pass_counts, total_counts, scores=None):
    k = len(pass_counts)
    if scores is None:
        scores = np.arange(k, dtype=float)
    n = np.array(total_counts, dtype=float)
    r = np.array(pass_counts, dtype=float)
    N = n.sum()
    R = r.sum()
    p_bar = R / N
    t_bar = np.sum(n * scores) / N
    numerator = np.sum(scores * (r - n * p_bar))
    denom_sq = p_bar * (1 - p_bar) * (np.sum(n * scores**2) - N * t_bar**2)
    if denom_sq <= 0:
        return {'z': 0, 'p_value': 1.0}
    z_stat = numerator / np.sqrt(denom_sq)
    p_val = 2 * norm.sf(abs(z_stat))
    return {'z': z_stat, 'p_value': p_val}


# ── McNemar's Test ─────────────────────────────────────────────────

def mcnemar_test(paired_results):
    """paired_results: list of (a_to_b_pass: bool, b_to_a_pass: bool)"""
    from scipy.stats import binomtest
    b = sum(1 for (ab, ba) in paired_results if not ab and ba)
    c = sum(1 for (ab, ba) in paired_results if ab and not ba)
    discordant = b + c
    if discordant == 0:
        return {'b': b, 'c': c, 'p_value': 1.0, 'method': 'exact'}
    result = binomtest(b, discordant, 0.5, alternative='two-sided')
    return {'b': b, 'c': c, 'p_value': result.pvalue, 'method': 'exact'}


# ── Main ───────────────────────────────────────────────────────────

def load_results(results_dir):
    results = []
    for model_dir in ['claude-sonnet-4-6', 'gemini-2.5-flash-lite',
                       'groq-llama-3.3-70b-versatile']:
        pattern = str(Path(results_dir) / model_dir / '*.json')
        for f in glob.glob(pattern):
            with open(f) as fp:
                results.append(json.load(fp))
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results-dir', default='results/evaluation/')
    args = parser.parse_args()

    results = load_results(args.results_dir)
    print(f"Loaded {len(results)} result files\n")

    # ── A. Per-model Wilson CIs ──
    print("=" * 60)
    print("A. CONFIDENCE INTERVALS (Wilson Score, 95%)")
    print("=" * 60)
    model_counts = defaultdict(lambda: [0, 0])
    for r in results:
        m = r['model']
        model_counts[m][1] += 1
        if r['overall_status'] == 'PASS':
            model_counts[m][0] += 1
    for m, (s, t) in sorted(model_counts.items()):
        p, lo, hi = wilson_ci(s, t)
        print(f"  {m}: {p*100:.2f}% [{lo*100:.1f}%, {hi*100:.1f}%] (n={t})")

    # ── B2. Model comparison ──
    print(f"\n{'=' * 60}")
    print("B2. MODEL COMPARISON")
    print("=" * 60)
    models_list = sorted(model_counts.keys())
    table = np.array([
        [model_counts[m][0] for m in models_list],
        [model_counts[m][1] - model_counts[m][0] for m in models_list]
    ])
    chi2, p_omni, dof, expected = chi2_contingency(table)
    v = cramers_v(chi2, table.sum(), 2, len(models_list))
    print(f"  Omnibus chi2({dof}) = {chi2:.2f}, p = {p_omni:.2e}, V = {v:.3f}")

    # Pairwise
    n_pairs = len(models_list) * (len(models_list) - 1) // 2
    alpha_pair = 0.05 / n_pairs
    for i in range(len(models_list)):
        for j in range(i+1, len(models_list)):
            mi, mj = models_list[i], models_list[j]
            t2x2 = np.array([
                [model_counts[mi][0], model_counts[mj][0]],
                [model_counts[mi][1]-model_counts[mi][0],
                 model_counts[mj][1]-model_counts[mj][0]]
            ])
            OR, p_f = fisher_exact(t2x2)
            h = cohens_h(model_counts[mi][0]/model_counts[mi][1],
                         model_counts[mj][0]/model_counts[mj][1])
            sig = "*" if p_f < alpha_pair else "ns"
            print(f"  {mi[:15]} vs {mj[:15]}: OR={OR:.2f}, p={p_f:.2e}, "
                  f"h={h:.3f} {sig}")

    # ── B1. Level independence (cuda-to-omp) ──
    print(f"\n{'=' * 60}")
    print("B1. AUGMENTATION LEVEL INDEPENDENCE (cuda-to-omp)")
    print("=" * 60)
    c2o = [r for r in results
           if r.get('source_spec','').endswith('-cuda')
           and r.get('target_spec','').endswith('-omp')]
    level_counts = defaultdict(lambda: [0, 0])
    for r in c2o:
        lv = f"L{r.get('augment_level', 0)}"
        level_counts[lv][1] += 1
        if r['overall_status'] == 'PASS':
            level_counts[lv][0] += 1
    levels = sorted(level_counts.keys())
    pass_c = [level_counts[lv][0] for lv in levels]
    fail_c = [level_counts[lv][1] - level_counts[lv][0] for lv in levels]
    for lv in levels:
        s, t = level_counts[lv]
        p, lo, hi = wilson_ci(s, t)
        print(f"  {lv}: {p*100:.1f}% [{lo*100:.1f}%, {hi*100:.1f}%] (n={t})")
    chi2_l, p_l, dof_l, _ = chi2_contingency(np.array([pass_c, fail_c]))
    print(f"  Chi2({dof_l}) = {chi2_l:.3f}, p = {p_l:.4f}")
    ca = cochran_armitage(pass_c, [level_counts[lv][1] for lv in levels])
    print(f"  Cochran-Armitage trend: z = {ca['z']:.3f}, p = {ca['p_value']:.4f}")

    print(f"\n{'=' * 60}")
    print("Analysis complete.")


if __name__ == '__main__':
    main()
```

---

## Summary of Recommended Tests for SC26 Paper

| Section | Test | Data | Key Metric | Paper Location |
|---|---|---|---|---|
| Model comparison | Chi-squared + pairwise Fisher | 3 x 156 | V, OR, h | S6.1 (main) |
| Level independence | Chi-squared + Cochran-Armitage | 5 x 57 | V, trend z | S6.3 (main) |
| Direction asymmetry | McNemar's exact | 57 paired | discordant ratio | S6.2 (main) |
| Per-model CIs | Wilson score | 156 each | CI width | All tables |
| Per-direction CIs | Wilson score | 15-255 | CI width | S6.2 + supp |
| Per-kernel CIs | Wilson score | 18 each | CI width | Supplementary |
| Effect sizes | Cramer's V, Cohen's h, OR | varies | magnitude | All tests |
| Pass@k | Chen et al. estimator | pilot: 150 | pass@1,3,5 | S6.4 or supp |
| Profiling | Descriptive only | 105 PASS | wall-clock range | S7 (limitation) |

### Multiple Testing Summary

| Family | Tests | Correction | Corrected alpha |
|---|---|---|---|
| B1 (level independence) | 4 (3 per-model + 1 overall) | Bonferroni | 0.0125 |
| B2 (pairwise model) | 3 pairs | Bonferroni | 0.0167 |
| B3 (direction asymmetry) | 12 (3 pairs x 3 models + 3 overall) | Bonferroni | 0.00417 |
| **Total** | **19 tests** | | |

All p-values should be reported as raw values with significance assessed against corrected
thresholds. Report both raw and corrected significance for transparency.
