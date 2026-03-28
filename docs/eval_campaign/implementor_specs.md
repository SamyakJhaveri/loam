# Implementor Specs: SC26 Eval Campaign Code Changes

**Author:** Implementor Agent
**Date:** 2026-03-28
**Status:** Design complete (pending implementation)

---

## Task A: Temperature / Pass@k Support

### A1. Add `temperature` parameter to `call_llm()`

**File:** `scripts/evaluation/llm_evaluate.py`
**Line:** 443-448 (function signature)

**Current code:**
```python
def call_llm(
    model: str,
    system_msg: str,
    messages: list[dict[str, str]],
    verbose: bool = False,
) -> dict[str, Any]:
```

**Proposed code:**
```python
def call_llm(
    model: str,
    system_msg: str,
    messages: list[dict[str, str]],
    verbose: bool = False,
    temperature: float = 0.0,
) -> dict[str, Any]:
```

**Docstring update** (line 449-460): Add `temperature` to Args section:
```
    Args:
        ...
        temperature: Sampling temperature (0.0 = deterministic, >0 = stochastic).
            For pass@k evaluation, use temperature > 0 (e.g. 0.8).
            Ignored for o1/o3/o4 reasoning models (they don't accept temperature).
```

### A2. Thread `temperature` through all 6 provider branches

Each provider branch currently hardcodes `temperature=0`. Replace with the parameter.

**Anthropic branch (line 500-506):**
```python
# Current (line 503):
        temperature=0,
# Proposed:
        temperature=temperature,
```

**OpenAI branch (line 535-542):**
```python
# Current (line 542):
            kwargs["temperature"] = 0
# Proposed:
            kwargs["temperature"] = temperature
```

**Azure branch (line 586-591):**
```python
# Current (line 589):
            temperature=0,
# Proposed:
            temperature=temperature,
```

**Groq branch (line 621-627):**
```python
# Current (line 624):
            temperature=0,
# Proposed:
            temperature=temperature,
```

**Gemini branch (line 655-665):**
```python
# Current (line 658):
            temperature=0,
# Proposed:
            temperature=temperature,
```

**Note:** The `o1/o3/o4` reasoning model guard at line 541 already skips temperature for those models. This is correct behavior — no change needed there.

### A3. Add `temperature` parameter to `evaluate_translation()`

**File:** `scripts/evaluation/llm_evaluate.py`
**Line:** 844-854 (function signature)

**Current code:**
```python
def evaluate_translation(
    source_path: Path,
    target_path: Path,
    model: str,
    project_root: Path,
    augment_level: int = 0,
    max_retries: int = 1,
    verbose: bool = False,
    dry_run: bool = False,
    use_cpu_timing: bool = False,
) -> dict[str, Any]:
```

**Proposed code:**
```python
def evaluate_translation(
    source_path: Path,
    target_path: Path,
    model: str,
    project_root: Path,
    augment_level: int = 0,
    max_retries: int = 1,
    verbose: bool = False,
    dry_run: bool = False,
    use_cpu_timing: bool = False,
    temperature: float = 0.0,
    sample_id: int | None = None,
) -> dict[str, Any]:
```

**Thread temperature to `call_llm()` call (line 1006):**
```python
# Current:
                llm_result = call_llm(model, system_msg, messages, verbose=verbose)
# Proposed:
                llm_result = call_llm(model, system_msg, messages, verbose=verbose, temperature=temperature)
```

**Add `sample_id` to result JSON (after line 1228):**
```python
        "augment_level": augment_level,
        "sample_id": sample_id,   # NEW: None for single-sample, 0..N-1 for pass@k
        "temperature": temperature,  # NEW: track what temperature was used
        "translation_mode": translation_mode,
```

### A4. Add `--temperature` and `--num-samples` to `run_eval_batch.py` CLI

**File:** `scripts/evaluation/run_eval_batch.py`
**Line:** After line 441 (after `--max-retries` argument)

**Proposed additions:**
```python
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        metavar="TEMP",
        help=(
            "LLM sampling temperature (0.0 = deterministic). "
            "For pass@k evaluation, use 0.8. Default: 0.0."
        ),
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=1,
        metavar="N",
        help=(
            "Number of independent samples per task (for pass@k). "
            "Each sample gets a distinct seed suffix in the result filename. "
            "Default: 1 (standard evaluation)."
        ),
    )
```

### A5. Modify `_build_tasks()` to generate per-sample tasks

**File:** `scripts/evaluation/run_eval_batch.py`
**Line:** 58-120

**Current inner loop (lines 106-116):**
```python
        for model in models:
            for level in levels:
                tasks.append({
                    "kernel": kernel,
                    "src_spec": src_spec_path,
                    "tgt_spec": tgt_spec_path,
                    "model": model,
                    "augment_level": level,
                    "src_id": src_spec_path.stem,
                    "tgt_id": tgt_spec_path.stem,
                })
```

**Proposed inner loop:**
```python
        for model in models:
            for level in levels:
                for sample in range(num_samples):
                    tasks.append({
                        "kernel": kernel,
                        "src_spec": src_spec_path,
                        "tgt_spec": tgt_spec_path,
                        "model": model,
                        "augment_level": level,
                        "sample_id": sample if num_samples > 1 else None,
                        "src_id": src_spec_path.stem,
                        "tgt_id": tgt_spec_path.stem,
                    })
```

**Also add `num_samples: int = 1` parameter to `_build_tasks()` signature (line 58).**

### A6. Modify `_result_path()` for sample suffix

**File:** `scripts/evaluation/run_eval_batch.py`
**Line:** 123-126

**Current code:**
```python
def _result_path(project_root: Path, model: str, src_id: str, tgt_id: str, augment_level: int = 0) -> Path:
    safe_model = model.replace("/", "_")
    level_tag = f"-L{augment_level}" if augment_level > 0 else ""
    return project_root / "results" / "evaluation" / safe_model / f"{src_id}-to-{tgt_id}{level_tag}.json"
```

**Proposed code:**
```python
def _result_path(
    project_root: Path, model: str, src_id: str, tgt_id: str,
    augment_level: int = 0, sample_id: int | None = None,
) -> Path:
    safe_model = model.replace("/", "_")
    level_tag = f"-L{augment_level}" if augment_level > 0 else ""
    sample_tag = f"-s{sample_id}" if sample_id is not None else ""
    return project_root / "results" / "evaluation" / safe_model / f"{src_id}-to-{tgt_id}{level_tag}{sample_tag}.json"
```

**Filename scheme:** `{src_id}-to-{tgt_id}[-L{N}][-s{M}].json`
- L0 single sample: `rodinia-bfs-cuda-to-rodinia-bfs-omp.json` (unchanged)
- L2 single sample: `rodinia-bfs-cuda-to-rodinia-bfs-omp-L2.json` (unchanged)
- L0 sample 3 of 10: `rodinia-bfs-cuda-to-rodinia-bfs-omp-s3.json`
- L2 sample 3 of 10: `rodinia-bfs-cuda-to-rodinia-bfs-omp-L2-s3.json`

### A7. Thread temperature + sample_id through `run_batch()`

**File:** `scripts/evaluation/run_eval_batch.py`
**Line:** 133-141 (`run_batch` signature)

Add `temperature: float = 0.0` parameter. In the inner loop (line 178-188), pass it:

```python
            result = evaluate_translation(
                source_path=task["src_spec"],
                target_path=task["tgt_spec"],
                model=model,
                project_root=project_root,
                augment_level=augment_level,
                use_cpu_timing=use_cpu_timing,
                max_retries=max_retries,
                verbose=verbose,
                temperature=temperature,            # NEW
                sample_id=task.get("sample_id"),     # NEW
            )
```

Also update `_result_path` calls at line 152 to include `sample_id=task.get("sample_id")`.

### A8. Pass@k computation function

**File:** `scripts/evaluation/run_eval_batch.py` (bottom, before `main()`)
**Or:** `scripts/analysis/statistical_analysis.py` (preferred — keeps analysis separate)

**Proposed function:**
```python
import math

def pass_at_k(n: int, c: int, k: int) -> float:
    """Compute pass@k metric (Chen et al. 2021, Codex paper).

    Args:
        n: Total number of samples generated per task.
        c: Number of correct (PASS) samples.
        k: k value (e.g., 1, 5, 10).

    Returns:
        pass@k probability estimate.

    Formula: pass@k = 1 - C(n-c, k) / C(n, k)
    where C(a, b) = a! / (b! * (a-b)!)

    Uses log-space computation to avoid overflow for large n.
    """
    if c == 0:
        return 0.0
    if n - c < k:
        return 1.0
    # Compute in log space: log(C(n-c, k)) - log(C(n, k))
    log_ratio = sum(
        math.log(n - c - i) - math.log(n - i)
        for i in range(k)
    )
    return 1.0 - math.exp(log_ratio)
```

**Justification:** This is the exact estimator from Chen et al. 2021 ("Evaluating Large Language Models Trained on Code", Codex paper, Section 2). It is the unbiased estimator and is standard in the code generation evaluation literature (HumanEval, MBPP, SWE-bench). The log-space computation avoids integer overflow when n is large.

### A9. Changes required in `main()` of `run_eval_batch.py`

**Line:** 464-471 (`_build_tasks` call): Add `num_samples=args.num_samples`
**Line:** 489-497 (`run_batch` call): Add `temperature=args.temperature`
**Line:** 510-518 (batch summary JSON): Add `"temperature": args.temperature, "num_samples": args.num_samples`

---

## Task B: Statistical Analysis Script

### B1. Script skeleton and CLI

**File:** `scripts/analysis/statistical_analysis.py` (NEW)
**Pattern follows:** `scripts/analysis/selfrepair_analysis.py` (loading pattern), `scripts/evaluation/analyze_eval.py` (result loading)

```python
#!/usr/bin/env python3
"""
scripts/analysis/statistical_analysis.py

Statistical significance analysis for ParBench evaluation results.

Computes:
  - Wilson score 95% CI for every reported pass rate
  - Chi-squared / Fisher's exact test: augmentation level x pass/fail
  - Effect sizes: Cramer's V, odds ratios, Cohen's h
  - Per-model augmentation curves with CIs
  - Pass@k estimates (when multi-sample results exist)

Output:
  results/analysis/statistical_analysis.json
  results/analysis/statistical_analysis.md

Dependencies: scipy, numpy (install via pip in venv)

Usage:
    python3 scripts/analysis/statistical_analysis.py \
        --project-root /home/samyak/Desktop/parbench_sam
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
```

### B2. Result loading (reuse from analyze_eval.py)

**Import directly from analyze_eval.py:**
```python
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.evaluation.analyze_eval import load_results, EXCLUDED_SPECS, _kernel_from_spec
```

This avoids code duplication. `load_results()` already handles model dirs, augment level extraction, direction inference, and KNOWN_FAIL exclusion.

### B3. Wilson Score CI function

```python
def wilson_ci(passes: int, total: int, alpha: float = 0.05) -> dict:
    """Wilson score confidence interval for a binomial proportion.

    Wilson score is preferred over normal approximation because it:
    - Never produces intervals outside [0, 1]
    - Is accurate even for small n and extreme p
    - Is the default in modern clinical statistics

    Args:
        passes: Number of successes.
        total: Number of trials.
        alpha: Significance level (0.05 = 95% CI).

    Returns:
        {"rate": float, "ci_lower": float, "ci_upper": float, "n": int}
    """
    if total == 0:
        return {"rate": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "n": 0}

    z = sp_stats.norm.ppf(1 - alpha / 2)
    p_hat = passes / total
    denom = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denom
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total) / denom

    return {
        "rate": round(p_hat, 4),
        "ci_lower": round(max(0.0, center - spread), 4),
        "ci_upper": round(min(1.0, center + spread), 4),
        "n": total,
    }
```

### B4. Chi-squared / Fisher's exact test

```python
def test_augmentation_independence(
    records: list[dict],
    group_key: str = "model",
) -> list[dict]:
    """Test independence: augmentation level x pass/fail.

    For each group (model or direction), build a contingency table:
      rows = augmentation levels (L0-L4)
      cols = [PASS, NOT_PASS]

    Uses chi-squared when all expected cell counts >= 5,
    falls back to Fisher's exact (2x2 only) or reports chi-squared
    with a "low_expected_counts" warning.

    Applies Bonferroni correction for multiple comparisons.

    Returns list of test result dicts.
    """
    groups = defaultdict(lambda: defaultdict(lambda: {"pass": 0, "fail": 0}))
    for r in records:
        group = r.get(group_key, "unknown")
        level = r.get("augment_level", 0)
        if r.get("overall_status") == "PASS":
            groups[group][level]["pass"] += 1
        else:
            groups[group][level]["fail"] += 1

    results = []
    n_tests = len(groups)  # Bonferroni denominator

    for group, levels in sorted(groups.items()):
        if len(levels) < 2:
            continue

        # Build contingency table: rows=levels, cols=[pass, fail]
        level_keys = sorted(levels.keys())
        table = np.array([[levels[lv]["pass"], levels[lv]["fail"]] for lv in level_keys])

        # Check expected cell counts
        row_totals = table.sum(axis=1, keepdims=True)
        col_totals = table.sum(axis=0, keepdims=True)
        grand_total = table.sum()
        if grand_total == 0:
            continue
        expected = row_totals * col_totals / grand_total
        low_expected = bool((expected < 5).any())

        # Chi-squared test
        chi2, p_value, dof, _ = sp_stats.chi2_contingency(table)

        # Bonferroni correction
        p_corrected = min(p_value * n_tests, 1.0)

        # Cramer's V effect size
        min_dim = min(table.shape[0], table.shape[1]) - 1
        cramers_v = math.sqrt(chi2 / (grand_total * min_dim)) if min_dim > 0 and grand_total > 0 else 0.0

        result = {
            "group": group,
            "group_key": group_key,
            "levels_tested": level_keys,
            "contingency_table": table.tolist(),
            "chi2": round(chi2, 4),
            "p_value": round(p_value, 6),
            "p_corrected_bonferroni": round(p_corrected, 6),
            "dof": dof,
            "cramers_v": round(cramers_v, 4),
            "low_expected_counts": low_expected,
            "significant_at_05": p_corrected < 0.05,
            "n_total": int(grand_total),
        }

        # Fisher's exact for 2x2 tables (L0 vs aggregated L1-L4)
        if len(level_keys) >= 2:
            l0_pass = levels.get(0, {"pass": 0})["pass"]
            l0_fail = levels.get(0, {"pass": 0, "fail": 0})["fail"]
            aug_pass = sum(levels[lv]["pass"] for lv in level_keys if lv > 0)
            aug_fail = sum(levels[lv]["fail"] for lv in level_keys if lv > 0)
            fisher_table = np.array([[l0_pass, l0_fail], [aug_pass, aug_fail]])
            if fisher_table.sum() > 0:
                odds_ratio, fisher_p = sp_stats.fisher_exact(fisher_table)
                result["fisher_exact_l0_vs_augmented"] = {
                    "table": fisher_table.tolist(),
                    "odds_ratio": round(odds_ratio, 4) if not np.isinf(odds_ratio) else "inf",
                    "p_value": round(fisher_p, 6),
                    "p_corrected": round(min(fisher_p * n_tests, 1.0), 6),
                }

        results.append(result)

    return results
```

### B5. Cohen's h effect size

```python
def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h effect size for comparing two proportions.

    h = 2 * arcsin(sqrt(p1)) - 2 * arcsin(sqrt(p2))

    |h| interpretation: 0.2 = small, 0.5 = medium, 0.8 = large
    """
    return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))
```

### B6. Per-model augmentation curves with CIs

```python
def augmentation_curves(records: list[dict]) -> dict:
    """Build per-model augmentation curves with Wilson CIs.

    Returns:
        {model: {level: {rate, ci_lower, ci_upper, n, pass, total}}}
    """
    # Group by (model, level)
    groups = defaultdict(lambda: {"pass": 0, "total": 0})
    for r in records:
        model = r.get("model", "unknown")
        level = r.get("augment_level", 0)
        groups[(model, level)]["total"] += 1
        if r.get("overall_status") == "PASS":
            groups[(model, level)]["pass"] += 1

    curves = defaultdict(dict)
    for (model, level), counts in sorted(groups.items()):
        ci = wilson_ci(counts["pass"], counts["total"])
        ci["pass"] = counts["pass"]
        ci["total"] = counts["total"]
        curves[model][f"L{level}"] = ci

    return dict(curves)
```

### B7. Pass@k aggregation (when multi-sample data exists)

```python
def pass_at_k(n: int, c: int, k: int) -> float:
    """Unbiased pass@k estimator (Chen et al. 2021).

    pass@k = 1 - C(n-c, k) / C(n, k)
    Computed in log space to avoid overflow.
    """
    if c == 0:
        return 0.0
    if n - c < k:
        return 1.0
    log_ratio = sum(math.log(n - c - i) - math.log(n - i) for i in range(k))
    return 1.0 - math.exp(log_ratio)


def compute_pass_at_k_table(records: list[dict], k_values: list[int] = [1, 5, 10]) -> dict:
    """Compute pass@k for each (kernel, model, direction, level) group.

    Groups results by task identity (excluding sample_id). For each group,
    counts n (total samples) and c (PASS samples), then computes pass@k.

    Returns:
        {(kernel, model, direction, level): {k: pass_at_k_value}}
    """
    # Group by task identity
    groups = defaultdict(lambda: {"n": 0, "c": 0})
    for r in records:
        key = (
            r.get("kernel", "?"),
            r.get("model", "?"),
            r.get("direction", "?"),
            r.get("augment_level", 0),
        )
        groups[key]["n"] += 1
        if r.get("overall_status") == "PASS":
            groups[key]["c"] += 1

    table = {}
    for key, counts in sorted(groups.items()):
        n, c = counts["n"], counts["c"]
        table[str(key)] = {
            "n": n,
            "c": c,
            **{f"pass@{k}": round(pass_at_k(n, c, k), 4) for k in k_values if k <= n},
        }

    return table
```

### B8. Main function and output

```python
def main():
    parser = argparse.ArgumentParser(
        description="Statistical analysis for ParBench evaluation results.",
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05)")
    parser.add_argument("--k-values", nargs="+", type=int, default=[1, 5, 10], help="k values for pass@k")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    results_dir = project_root / "results" / "evaluation"
    output_dir = project_root / "results" / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)

    records = load_results(results_dir)
    print(f"Loaded {len(records)} result records.")

    # 1. Wilson CIs for all aggregations
    # By model
    by_model_ci = {}
    model_groups = defaultdict(list)
    for r in records:
        model_groups[r.get("model", "unknown")].append(r)
    for model, recs in sorted(model_groups.items()):
        passes = sum(1 for r in recs if r.get("overall_status") == "PASS")
        by_model_ci[model] = wilson_ci(passes, len(recs), args.alpha)

    # By direction
    by_direction_ci = {}
    dir_groups = defaultdict(list)
    for r in records:
        dir_groups[r.get("direction", "unknown")].append(r)
    for direction, recs in sorted(dir_groups.items()):
        passes = sum(1 for r in recs if r.get("overall_status") == "PASS")
        by_direction_ci[direction] = wilson_ci(passes, len(recs), args.alpha)

    # 2. Chi-squared tests
    chi2_by_model = test_augmentation_independence(records, group_key="model")
    chi2_by_direction = test_augmentation_independence(records, group_key="direction")

    # 3. Augmentation curves
    aug_curves = augmentation_curves(records)

    # 4. Pairwise Cohen's h (model comparisons)
    model_rates = {m: ci["rate"] for m, ci in by_model_ci.items()}
    pairwise_h = {}
    models = sorted(model_rates.keys())
    for i, m1 in enumerate(models):
        for m2 in models[i+1:]:
            h = cohens_h(model_rates[m1], model_rates[m2])
            pairwise_h[f"{m1} vs {m2}"] = {
                "cohens_h": round(h, 4),
                "effect_size": "large" if abs(h) >= 0.8 else "medium" if abs(h) >= 0.5 else "small" if abs(h) >= 0.2 else "negligible",
            }

    # 5. Pass@k (if multi-sample data exists)
    has_samples = any(r.get("sample_id") is not None for r in records)
    pass_k_table = compute_pass_at_k_table(records, args.k_values) if has_samples else {}

    # Assemble output
    output = {
        "generated_at": datetime.now().isoformat(),
        "alpha": args.alpha,
        "total_records": len(records),
        "wilson_ci_by_model": by_model_ci,
        "wilson_ci_by_direction": by_direction_ci,
        "chi2_augmentation_by_model": chi2_by_model,
        "chi2_augmentation_by_direction": chi2_by_direction,
        "augmentation_curves": aug_curves,
        "pairwise_cohens_h": pairwise_h,
        "pass_at_k": pass_k_table,
    }

    # Write JSON
    json_path = output_dir / "statistical_analysis.json"
    json_path.write_text(json.dumps(output, indent=2, default=str))
    print(f"JSON: {json_path}")

    # Write Markdown
    md = _build_markdown(output)
    md_path = output_dir / "statistical_analysis.md"
    md_path.write_text(md)
    print(f"Markdown: {md_path}")
```

### B9. Markdown report builder

```python
def _build_markdown(data: dict) -> str:
    """Build publication-ready Markdown tables from statistical analysis."""
    lines = [
        "# ParBench Statistical Analysis",
        f"**Generated:** {data['generated_at']}  |  **Records:** {data['total_records']}  |  **Alpha:** {data['alpha']}",
        "",
        "## Pass Rates with 95% Wilson Score CIs",
        "",
        "### By Model",
        "| Model | Rate | 95% CI | n |",
        "|-------|-----:|-------:|--:|",
    ]
    for model, ci in data["wilson_ci_by_model"].items():
        lines.append(f"| {model} | {ci['rate']*100:.1f}% | [{ci['ci_lower']*100:.1f}%, {ci['ci_upper']*100:.1f}%] | {ci['n']} |")

    lines += ["", "### By Direction", "| Direction | Rate | 95% CI | n |", "|-----------|-----:|-------:|--:|"]
    for direction, ci in data["wilson_ci_by_direction"].items():
        lines.append(f"| {direction} | {ci['rate']*100:.1f}% | [{ci['ci_lower']*100:.1f}%, {ci['ci_upper']*100:.1f}%] | {ci['n']} |")

    lines += [
        "",
        "## Chi-Squared Test: Augmentation Level x Pass/Fail",
        "",
        "**H0:** Pass rate is independent of augmentation level.",
        "**Correction:** Bonferroni for multiple comparisons.",
        "",
        "### By Model",
        "| Model | chi2 | p (corrected) | Cramer's V | Significant? | Low expected? |",
        "|-------|-----:|-------------:|----------:|:------------:|:-------------:|",
    ]
    for t in data["chi2_augmentation_by_model"]:
        sig = "Yes" if t["significant_at_05"] else "No"
        low = "Yes" if t["low_expected_counts"] else "No"
        lines.append(f"| {t['group']} | {t['chi2']:.2f} | {t['p_corrected_bonferroni']:.4f} | {t['cramers_v']:.3f} | {sig} | {low} |")

    lines += [
        "",
        "## Pairwise Model Comparisons (Cohen's h)",
        "| Comparison | Cohen's h | Effect Size |",
        "|------------|----------:|:------------|",
    ]
    for pair, h in data["pairwise_cohens_h"].items():
        lines.append(f"| {pair} | {h['cohens_h']:.3f} | {h['effect_size']} |")

    lines += [
        "",
        "## Augmentation Curves with CIs",
        "",
    ]
    for model, levels in data["augmentation_curves"].items():
        lines.append(f"### {model}")
        lines.append("| Level | Rate | 95% CI | Pass/Total |")
        lines.append("|-------|-----:|-------:|----------:|")
        for level, ci in sorted(levels.items()):
            lines.append(f"| {level} | {ci['rate']*100:.1f}% | [{ci['ci_lower']*100:.1f}%, {ci['ci_upper']*100:.1f}%] | {ci['pass']}/{ci['total']} |")
        lines.append("")

    if data.get("pass_at_k"):
        lines += ["## Pass@k Estimates", ""]
        # Format depends on data shape — simplified table
        lines.append("| Task | n | c | pass@1 | pass@5 | pass@10 |")
        lines.append("|------|--:|--:|-------:|-------:|--------:|")
        for key, vals in data["pass_at_k"].items():
            p1 = vals.get("pass@1", "—")
            p5 = vals.get("pass@5", "—")
            p10 = vals.get("pass@10", "—")
            lines.append(f"| {key} | {vals['n']} | {vals['c']} | {p1} | {p5} | {p10} |")
        lines.append("")

    return "\n".join(lines) + "\n"
```

### B10. Dependencies

**Must be installed in venv:**
```bash
python3 -m pip install scipy numpy
```

Both are standard scientific Python packages. `scipy.stats` provides `chi2_contingency`, `fisher_exact`, and `norm.ppf`. `numpy` is required by `scipy` and used for array operations.

---

## Task C: Third Benchmark Onboarding (Parboil)

### C1. Background

Parboil is a benchmark suite from the University of Illinois (IMPACT research group) containing 12 benchmarks with implementations in CUDA, OpenMP, and OpenCL. It is a natural third suite alongside Rodinia and XSBench because:
- Overlapping HPC domain (stencils, linear algebra, image processing)
- Well-studied in the literature (cited alongside Rodinia)
- Multiple API implementations per kernel (CUDA, OMP, OpenCL)

**If Parboil is unavailable** (it requires a registration form), use **SNU NPB (Seoul National University NAS Parallel Benchmarks)** as the backup. SNU NPB has CUDA + OpenCL + OpenMP implementations of the NAS benchmarks (CG, EP, FT, IS, LU, MG, SP, BT).

### C2. Source location and config

**Directory:** `parboil/parboil-src/` (following `xsbench/xsbench-src/` convention)

**File:** `config/paths.json`
```json
{
    "project_root": "/Users/samyakjhaveri/Desktop/parbench_sam",
    "downloads_root": "/Users/samyakjhaveri/Desktop/parbench_sam",
    "hecbench_root": "/Users/samyakjhaveri/Desktop/parbench_sam/HeCBench-master",
    "parboil_root": "/Users/samyakjhaveri/Desktop/parbench_sam/parboil/parboil-src"
}
```

**File:** `.gitignore` — add:
```
parboil/parboil-src/
```

### C3. Survey script design

**File:** `scripts/survey/survey_parboil.py` (NEW)
**Pattern follows:** XSBench had no survey script but the generator itself served that role.

```python
#!/usr/bin/env python3
"""
scripts/survey/survey_parboil.py — Survey Parboil benchmark suite.

Walks the Parboil source tree and identifies:
  - Which benchmarks exist
  - Which API variants each benchmark has (cuda, omp, opencl)
  - Source files per variant
  - Build system (Makefile structure)
  - Verification method (comparison files, self-checking)

Output: analysis/data/parboil_survey.json

Usage:
    python3 scripts/survey/survey_parboil.py \
        --parboil-root parboil/parboil-src \
        --project-root /home/samyak/Desktop/parbench_sam
"""
```

**Key functions:**
1. `discover_benchmarks(parboil_root)` — list subdirectories in `benchmarks/`
2. `discover_variants(bench_dir)` — list subdirectories in `benchmarks/{name}/src/`; map directory names to API enums (e.g., `cuda`, `cuda_base`, `omp`, `opencl_base`, `opencl_nvidia`)
3. `survey_variant(bench_dir, variant)` — for each variant: list `.c/.cu/.cl` source files, `.h` headers, check for `Makefile`, check for dataset/reference output in `benchmarks/{name}/datasets/`
4. `main()` — write `analysis/data/parboil_survey.json`

### C4. Spec generator design

**File:** `scripts/generators/generate_parboil_specs.py` (NEW)
**Pattern follows:** `scripts/generators/generate_xsbench_specs.py`

**Structure mirrors XSBench generator exactly:**

```python
#!/usr/bin/env python3
"""
Generate ParBench spec files for the Parboil benchmark suite.

Parboil contains 12 benchmarks from UIUC IMPACT with CUDA, OpenMP, and OpenCL variants.

Writes: specs/parboil-{kernel}-{api}.json  (one per kernel-API pair)
        manifest.jsonl                      (entries appended)

Usage:
    python3 scripts/generators/generate_parboil_specs.py [--dry-run] [--force]
"""

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SPECS_DIR = PROJECT_ROOT / "specs"
MANIFEST_FILE = PROJECT_ROOT / "manifest.jsonl"

PARBOIL_REPO_URL = "https://github.com/abduld/Parboil"  # or IMPACT official
PARBOIL_COMMIT = "<TBD after clone>"
PARBOIL_REPO_ROOT = "parboil/parboil-src"
PARBOIL_LICENSE = "Illinois/NCSA"

REFERENCE_PLATFORM = {
    # Same as XSBench — same hardware
    "platform_id": "rtx4070-r9-7900x",
    "gpu": { ... },
    "cpu": { ... },
    "software": { ... },
}
```

**Parboil benchmark → API availability estimate** (based on published Parboil documentation):

| Benchmark | CUDA | OMP | OpenCL | Category |
|-----------|:----:|:---:|:------:|----------|
| bfs       | Yes  | Yes | Yes    | graph |
| cutcp     | Yes  | Yes | Yes    | molecular_dynamics |
| histo     | Yes  | Yes | Yes    | image |
| lbm       | Yes  | Yes | Yes    | stencil |
| mri-gridding | Yes | Yes | Yes  | image |
| mri-q     | Yes  | Yes | Yes    | image |
| sad       | Yes  | Yes | Yes    | image |
| sgemm     | Yes  | Yes | Yes    | linear_algebra |
| spmv      | Yes  | Yes | Yes    | linear_algebra |
| stencil   | Yes  | Yes | Yes    | stencil |
| tpacf     | Yes  | Yes | Yes    | other |
| NONE_KNOWN| —    | —   | —      | — |

**Estimated yield:** 11 benchmarks x 3 APIs = 33 specs.

**Key differences from XSBench generator:**
1. Parboil uses a custom `parboil` build tool (`./parboil run bfs cuda small`), not `make`. The spec `build.commands.build` must be adapted to call the Parboil build script or use the per-variant Makefile directly.
2. Parboil provides datasets (small, medium, large) in `datasets/`. The spec must reference the correct dataset path for `run.arguments`.
3. Verification uses reference output files in `datasets/{bench}/output/`, not self-checking patterns. The spec will need a custom verification strategy comparing output against reference file.

**Spec naming convention:** `parboil-{kernel}-{api}.json` (e.g., `parboil-bfs-cuda.json`, `parboil-sgemm-omp.json`)

### C5. SNU NPB backup design

If Parboil is unavailable:

**Directory:** `snu-npb/snu-npb-src/`
**Generator:** `scripts/generators/generate_snu_npb_specs.py`
**Repo:** `https://github.com/GMAP/NPB-GPU` or SNU's original

**SNU NPB kernels with multi-API support:**

| Benchmark | CUDA | OMP | OpenCL |
|-----------|:----:|:---:|:------:|
| CG        | Yes  | Yes | Yes    |
| EP        | Yes  | Yes | Yes    |
| FT        | Yes  | Yes | Yes    |
| IS        | Yes  | Yes | Yes    |
| LU        | Yes  | Yes | Yes    |
| MG        | Yes  | Yes | Yes    |
| SP        | Yes  | Yes | Yes    |
| BT        | Yes  | Yes | Yes    |

**Estimated yield:** 8 benchmarks x 3 APIs = 24 specs.

---

## Task D: Batch Scripts for OpenCL Directions

### D1. Common pattern

All 4 scripts follow the same structure as `run_xsbench_eval.sh` and `run_rodinia_augmented_eval.sh`:
- tmux self-launch
- API key pre-flight
- venv activation
- configurable models, levels, retries
- Pass 1 + retry Pass 2
- Completeness check
- Analysis regeneration

### D2. Kernel lists per direction

**Important:** The kernel list depends on the direction because not all kernels have all API variants. Based on the known spec inventory:

**Rodinia kernels with OpenCL specs:** backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, lavamd, lud, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster (16 kernels; excluding kmeans-opencl and nn-opencl which are KNOWN_FAIL).

**Rodinia kernels with CUDA specs (non-KNOWN_FAIL):** backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, lavamd, lud, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster (16 kernels; excluding kmeans-cuda, mummergpu-cuda, hybridsort-cuda).

**Rodinia kernels with OMP specs (non-KNOWN_FAIL):** backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, lavamd, lud, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster (16 kernels; excluding mummergpu-omp).

**XSBench:** xsbench (1 kernel, all 3 APIs)

For OpenCL directions, both source AND target must be non-KNOWN_FAIL. The intersection for each direction:

| Direction | Rodinia kernels | XSBench | Total per model |
|-----------|:-:|:-:|:-:|
| cuda-to-opencl | 16 (drop nn-opencl, kmeans-opencl targets) = **14** | 1 | 15 |
| opencl-to-cuda | 14 (drop kmeans-opencl, nn-opencl sources) | 1 | 15 |
| omp-to-opencl | 16 (drop nn-opencl, kmeans-opencl targets) = **14** | 1 | 15 |
| opencl-to-omp | 14 (drop kmeans-opencl, nn-opencl sources) | 1 | 15 |

**Wait — correction.** The KNOWN_FAIL check is at the *spec* level in `analyze_eval.py` EXCLUDED_SPECS. The *batch runner* `_build_tasks()` doesn't filter KNOWN_FAIL; it just skips missing spec files. Since the KNOWN_FAIL specs still exist as files, they would be included in batch runs. But analysis excludes them.

For correctness, the batch scripts should explicitly exclude KNOWN_FAIL kernel-API combinations. The safest approach: specify `--kernels` explicitly with only the valid ones.

**Kernels valid as OpenCL SOURCE (not KNOWN_FAIL):** All except kmeans, nn → 16 kernels
**Kernels valid as OpenCL TARGET (not KNOWN_FAIL):** All except kmeans, nn → 16 kernels

Since the KNOWN_FAIL list affects both source and target: use the intersection of non-KNOWN_FAIL source and non-KNOWN_FAIL target.

**For Rodinia, the safe OpenCL kernel list** (where both CUDA/OMP and OpenCL specs are non-KNOWN_FAIL):
```
backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster
```
That's **15 kernels** (nn excluded from OpenCL target/source due to KNOWN_FAIL).

### D3. Script: `run_cuda_to_opencl.sh`

**File:** `scripts/batch/run_cuda_to_opencl.sh` (NEW)

```bash
#!/usr/bin/env bash
# run_cuda_to_opencl.sh — Rodinia + XSBench: CUDA-to-OpenCL evaluation
#
# Runs 3 models x (15 Rodinia + 1 XSBench) kernels x augmentation levels
# Self-launches in a detached tmux session.
#
# Usage:
#   bash scripts/batch/run_cuda_to_opencl.sh          # launch (default)
#   bash scripts/batch/run_cuda_to_opencl.sh --attach  # attach to session
#
# Override defaults:
#   MODELS="claude-sonnet-4-6" AUGMENT_LEVELS="0" bash scripts/batch/run_cuda_to_opencl.sh

set -euo pipefail

SESSION="cuda_to_opencl_eval"
PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
LOGFILE="$PROJECT_ROOT/results/evaluation/cuda_to_opencl_eval.log"
DIRECTION="cuda-to-opencl"

# Overridable defaults
MODELS="${MODELS:-claude-sonnet-4-6 gemini-2.5-flash-lite groq-llama-3.3-70b-versatile}"
AUGMENT_LEVELS="${AUGMENT_LEVELS:-0}"
MAX_RETRIES="${MAX_RETRIES:-3}"

# Rodinia kernels where BOTH cuda source AND opencl target are non-KNOWN_FAIL
RODINIA_KERNELS="backprop bfs bptree cfd heartwall hotspot hotspot3d lavamd lud myocyte nw particlefilter pathfinder srad streamcluster"

# ── tmux self-launch ─────────────────────────────────────────────────────────
if [[ "${1:-}" == "--attach" ]]; then
    exec tmux attach -t "$SESSION"
fi

if [[ -z "${TMUX:-}" ]] && [[ "${1:-}" != "--inside-tmux" ]]; then
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    mkdir -p "$(dirname "$LOGFILE")"
    tmux new-session -d -s "$SESSION" -x 220 -y 50 \
        "bash \"$0\" --inside-tmux 2>&1 | tee \"$LOGFILE\"; echo ''; echo '=== SESSION FINISHED ==='; read -r -p 'Press Enter to close...'"
    echo "Launched tmux session '$SESSION'."
    echo "  Attach with:  tmux attach -t $SESSION"
    echo "  Log file:     $LOGFILE"
    exit 0
fi

# ── Inside tmux ──────────────────────────────────────────────────────────────
trap 'echo ""; echo "INTERRUPTED at $(date -Iseconds)"; exit 130' INT TERM

echo "============================================================"
echo " $DIRECTION Evaluation"
echo " $(date)"
echo " Repo: $PROJECT_ROOT"
echo "============================================================"
echo ""

source "$PROJECT_ROOT/env_parbench/bin/activate"
echo "[env] Python: $(python3 --version)"
echo ""

# Pre-flight: verify API keys
echo "--- Pre-flight checks ---"
MISSING_KEYS=""
for VAR in ANTHROPIC_API_KEY GEMINI_API_KEY GROQ_API_KEY; do
    if [ -z "${!VAR:-}" ]; then
        echo "  FATAL: $VAR is not set."
        MISSING_KEYS="$MISSING_KEYS $VAR"
    else
        echo "  OK: $VAR is set"
    fi
done
if [ -n "$MISSING_KEYS" ]; then
    echo "FATAL: Missing API keys:$MISSING_KEYS — aborting."
    exit 1
fi
echo ""

echo "Configuration:"
echo "  Direction: $DIRECTION"
echo "  Models: $MODELS"
echo "  Augment levels: $AUGMENT_LEVELS"
echo "  Max retries: $MAX_RETRIES"
echo ""

cd "$PROJECT_ROOT"
START_TIME=$(date +%s)

# ── Pass 1: Rodinia ──────────────────────────────────────────────────────────
echo "=== Rodinia ($DIRECTION) ==="
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --direction "$DIRECTION" \
    --kernels $RODINIA_KERNELS \
    --models $MODELS \
    --augment-levels $AUGMENT_LEVELS \
    --max-retries "$MAX_RETRIES" \
    --resume -v \
    --project-root "$PROJECT_ROOT"
echo ""

# ── Pass 2: XSBench ─────────────────────────────────────────────────────────
echo "=== XSBench ($DIRECTION) ==="
python3 scripts/evaluation/run_eval_batch.py \
    --suite xsbench \
    --direction "$DIRECTION" \
    --models $MODELS \
    --augment-levels $AUGMENT_LEVELS \
    --max-retries "$MAX_RETRIES" \
    --resume -v \
    --project-root "$PROJECT_ROOT"
echo ""

# ── Regenerate analysis ─────────────────────────────────────────────────────
echo "=== Regenerating analysis ==="
python3 scripts/evaluation/analyze_eval.py \
    --project-root "$PROJECT_ROOT" \
    --write-dashboard || echo "  Warning: analysis failed"
echo ""

# ── Summary ──────────────────────────────────────────────────────────────────
END_TIME=$(date +%s)
ELAPSED=$(( (END_TIME - START_TIME) / 60 ))
echo "============================================================"
echo " $DIRECTION EVAL COMPLETE — $(date)"
echo " Elapsed: ${ELAPSED} minutes"
echo " Log: $LOGFILE"
echo "============================================================"
```

### D4. Scripts: `run_opencl_to_cuda.sh`, `run_omp_to_opencl.sh`, `run_opencl_to_omp.sh`

**Identical structure to D3** with these changes per script:

| Script | DIRECTION | SESSION | LOGFILE stem | Rodinia kernels |
|--------|-----------|---------|-------------|-----------------|
| `run_opencl_to_cuda.sh` | `opencl-to-cuda` | `opencl_to_cuda_eval` | `opencl_to_cuda_eval.log` | Same 15 |
| `run_omp_to_opencl.sh` | `omp-to-opencl` | `omp_to_opencl_eval` | `omp_to_opencl_eval.log` | Same 15 |
| `run_opencl_to_omp.sh` | `opencl-to-omp` | `opencl_to_omp_eval` | `opencl_to_omp_eval.log` | Same 15 |

The kernel list is the same for all 4 scripts because the 15 valid kernels are the intersection of non-KNOWN_FAIL specs across all 3 APIs.

---

## Task E: Analysis Pipeline Updates

### E1. Update `EXCLUDED_SPECS` in `analyze_eval.py`

**File:** `scripts/evaluation/analyze_eval.py`
**Line:** 47-54

**Current code:**
```python
EXCLUDED_SPECS: frozenset[str] = frozenset({
    "rodinia-kmeans-cuda",
    "rodinia-mummergpu-cuda",
    "rodinia-mummergpu-omp",
    "rodinia-hybridsort-cuda",
    "rodinia-nn-opencl",
    "rodinia-kmeans-opencl",
})
```

**Proposed code (no change needed):** The current `EXCLUDED_SPECS` is already correct. It already includes the 2 KNOWN_FAIL OpenCL specs (`nn-opencl`, `kmeans-opencl`). OpenCL direction results will automatically be included in analysis because:
1. `load_results()` walks all model dirs and loads all JSON files
2. `_direction_from_ids()` correctly infers opencl directions (e.g., `cuda-to-opencl`)
3. `build_summary()` groups by direction, which will create new entries for `cuda-to-opencl`, `opencl-to-cuda`, `omp-to-opencl`, `opencl-to-omp`

The only exclusion needed is spec-level, which is already handled.

### E2. Update `--expected-directions` default in `analyze_eval.py`

**File:** `scripts/evaluation/analyze_eval.py`
**Line:** 498-502

**Current code:**
```python
    parser.add_argument(
        "--expected-directions",
        nargs="+",
        default=["cuda-to-omp"],
        metavar="DIR",
```

**Proposed code:**
```python
    parser.add_argument(
        "--expected-directions",
        nargs="+",
        default=[
            "cuda-to-omp", "omp-to-cuda",
            "cuda-to-opencl", "opencl-to-cuda",
            "omp-to-opencl", "opencl-to-omp",
        ],
        metavar="DIR",
```

This ensures `--show-gaps` checks for completeness across all 6 standard directions (excluding omp_target which is case-study only).

### E3. Update `--expected-models` default

**File:** `scripts/evaluation/analyze_eval.py`
**Line:** 487-494

**Current code:**
```python
    parser.add_argument(
        "--expected-models",
        nargs="+",
        default=[
            "azure-gpt-4.1",
            "claude-sonnet-4-6",
            "gemini-2.5-flash-lite",
            "groq-llama-3.3-70b-versatile",
        ],
```

**Proposed code:**
```python
    parser.add_argument(
        "--expected-models",
        nargs="+",
        default=[
            "claude-sonnet-4-6",
            "gemini-2.5-flash-lite",
            "groq-llama-3.3-70b-versatile",
        ],
```

Remove `azure-gpt-4.1` since it was dropped from the eval campaign (3-model decision).

### E4. Update `--expected-levels` default

**File:** `scripts/evaluation/analyze_eval.py`
**Line:** 505-512

**Current code:**
```python
    parser.add_argument(
        "--expected-levels",
        nargs="+",
        type=int,
        default=[0],
```

**Proposed code:**
```python
    parser.add_argument(
        "--expected-levels",
        nargs="+",
        type=int,
        default=[0, 1, 2, 3, 4],
```

This makes `--show-gaps` check for L0-L4 completeness by default, matching the full campaign scope.

### E5. Dashboard data: No code changes needed

`write_dashboard_js()` already includes `byDirection` and `byComplexity` in the JS output. When OpenCL direction results are loaded, they will automatically appear in the dashboard data. The dashboard JS will show new direction entries without any code modification.

### E6. Summary of analyze_eval.py changes

| Line | What | Change |
|------|------|--------|
| 47-54 | EXCLUDED_SPECS | No change needed (already correct) |
| 487-494 | --expected-models default | Remove azure-gpt-4.1 |
| 499-502 | --expected-directions default | Add 5 new directions |
| 506-510 | --expected-levels default | Change [0] to [0,1,2,3,4] |

These are minimal, safe changes. All 4 are in CLI defaults only — no core logic changes.

---

## Cross-Cutting Concerns

### New dependencies to install
```bash
source env_parbench/bin/activate
python3 -m pip install scipy numpy
```

### New files created
| File | Purpose |
|------|---------|
| `scripts/analysis/statistical_analysis.py` | Statistical significance tests |
| `scripts/batch/run_cuda_to_opencl.sh` | CUDA-to-OpenCL batch |
| `scripts/batch/run_opencl_to_cuda.sh` | OpenCL-to-CUDA batch |
| `scripts/batch/run_omp_to_opencl.sh` | OMP-to-OpenCL batch |
| `scripts/batch/run_opencl_to_omp.sh` | OpenCL-to-OMP batch |
| `scripts/survey/survey_parboil.py` | Parboil source survey |
| `scripts/generators/generate_parboil_specs.py` | Parboil spec generator |

### Existing files modified
| File | Changes |
|------|---------|
| `scripts/evaluation/llm_evaluate.py` | temperature param in `call_llm()` + `evaluate_translation()` |
| `scripts/evaluation/run_eval_batch.py` | --temperature, --num-samples flags; sample_id in tasks/paths |
| `scripts/evaluation/analyze_eval.py` | CLI defaults for models/directions/levels |
| `config/paths.json` | Add parboil_root |
| `.gitignore` | Add parboil/parboil-src/ |

### Backward compatibility
- All new parameters have defaults matching current behavior (temperature=0.0, num_samples=1, sample_id=None)
- Existing result filenames are unchanged (sample_id=None produces no suffix)
- `analyze_eval.py` changes are CLI defaults only; passing explicit flags still works
- `statistical_analysis.py` is purely additive (new script, no modifications to existing analysis)

---

## Risk Assessment

| Change | Risk | Mitigation |
|--------|------|------------|
| Temperature threading in call_llm | Low — pure parameter pass-through | Each provider branch is a 1-line change |
| Pass@k multi-sample | Medium — increases task count by N | --num-samples defaults to 1; only activated when explicitly set |
| Parboil onboarding | Medium — Parboil build system is non-standard | Survey script runs first; generator adapts based on survey |
| OpenCL batch scripts | Low — follows exact existing pattern | Kernel lists explicitly exclude KNOWN_FAIL |
| analyze_eval.py defaults | Low — CLI defaults only | No logic changes; existing explicit flags override |
| scipy dependency | Low — standard, well-tested | Only used in statistical_analysis.py, not in eval pipeline |
