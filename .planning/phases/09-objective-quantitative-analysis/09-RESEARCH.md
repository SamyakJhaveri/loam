# Phase 9: Objective Quantitative Analysis - Research

**Researched:** 2026-04-04
**Domain:** Python data analysis, statistical computing, JSON processing, SC26 paper claim provenance
**Confidence:** HIGH

## Summary

Phase 9 creates a single monolithic Python script (`scripts/analysis/quantitative_findings.py`) that computes all 14 quantitative dimensions from raw result JSONs (1,248 files in `results/evaluation/together-qwen-3.5-397b-a17b/`), producing `results/analysis/quantitative_findings.json` + `.md`. The script follows the established pattern of existing analysis scripts (e.g., `benchmark_characterization.py`, `generate_paper_data.py`): argparse CLI, `PROJECT_ROOT` resolution, direct JSON loading, Wilson CIs, and structured output with markdown companion.

The primary technical challenge is the two-campaign separation (deterministic vs pass@k) and comprehensive 14-dimension coverage. All statistical methods (Wilson CI, McNemar, Cochran-Armitage, Cohen's h, Chi-squared/Fisher's exact) already have working implementations in `generate_paper_data.py` and `statistical_analysis.py` that can be referenced for correctness. The SLoC data is available in `results/analysis/sloc_analysis.json` (static source property, not eval-derived). Token pricing ($0.60/$3.60 per million for Qwen 3.5 397B) is already defined in `token_analysis.py` and confirmed against Together AI's published pricing.

**Primary recommendation:** Build the script as a self-contained monolith (per D-01) that loads raw JSONs, computes all metrics fresh (per D-02), cross-checks against existing analysis files (per D-03), and outputs both JSON and markdown. Reference existing statistical implementations for algorithm correctness but re-implement from raw data. Include a `--validate` flag for automated spot-checking.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Single monolithic script `scripts/analysis/quantitative_findings.py` — consistent with Phase 2 (benchmark_characterization.py) and Phase 3 (augmentation_analysis.py) patterns.
- **D-02:** Compute directly from raw result JSONs in `results/evaluation/together-qwen-3.5-397b-a17b/`. Do NOT depend on intermediate analysis files (paper_data.json, etc.) as primary data source — raw files are ground truth per Phase 1 D-07.
- **D-03:** After computing from raw, cross-check against existing analysis JSONs (paper_data.json, statistical_analysis.json, etc.) and warn on discrepancies >0.1%. This catches stale derived files.
- **D-04:** In practice, compute ALL eval-derived metrics fresh from raw result JSONs (per D-02). The only planned exception: SLoC data reads from existing `benchmark_characterization.json` / `sloc_analysis.json` (verified in Phase 2 — SLoC is a static source property, not an eval result). Claude may pull additional static metadata from existing analysis if justified, but eval pass rates, failure counts, and statistical tests must come from raw.
- **D-05:** Two evaluation campaigns must be analyzed SEPARATELY, never pooled.
- **D-06:** File discrimination by filename suffix: `-s{0,1,2}` suffix -> Campaign 2 (seed variants). No suffix or `-L{1-4}` suffix -> Campaign 1. Both live in the same directory.
- **D-07:** Campaign 1 feeds 12+ dimensions. Campaign 2 feeds pass@k dimension. Provenance (dim 14) applies to both.
- **D-08:** No cross-campaign comparison.
- **D-09:** Analyze the full 1,248-file dataset across all 5 suites.
- **D-10:** Auto-exclude the 8 KNOWN_FAIL specs by default.
- **D-11:** No `--suite` filter. Full dataset always.
- **D-12:** omp_target directions go in a dedicated "case-study" section.
- **D-13:** Glob result JSONs, parse each filename.
- **D-14:** Complexity classes from spec JSON fields (translation_targets, prompt_payload).
- **D-15:** Simple fraction for pass@k, no extrapolation. Report pass@1 and pass@3.
- **D-16:** Campaign 2 gets full per-direction + per-suite pass@k breakdowns.
- **D-17:** Quiet output with final summary line. `-v` for verbose.
- **D-18:** Campaign-first JSON layout: `metadata`, `campaign_1`, `campaign_2`, `cross_checks`.
- **D-19:** Provenance per finding with value/source/files_matched/derivation.
- **D-20:** Confidence intervals as separate numeric fields.
- **D-21:** All internal numeric values as decimals 0-1.
- **D-22:** Dedicated `paper_claims` section for Phase 11 audit.
- **D-23:** Both output files in `results/analysis/`.
- **D-24:** Paper-ready tables in markdown companion.
- **D-25:** Separate campaign sections in markdown.
- **D-26:** Per-kernel tables ordered by pass rate.
- **D-27:** Brief 1-line objective observations per table.
- **D-28:** Error taxonomy: top-level + top-3 build error subcategories.
- **D-29:** Self-repair computed from raw attempts[] arrays.
- **D-30:** McNemar's test from raw paired data.
- **D-31:** Cochran-Armitage for ALL directions and aggregate, plus Cohen's h.
- **D-32:** Per-kernel difficulty tiers: quartile-based + top-5/bottom-5.
- **D-33:** OpenCL kernel-only effect comparison.
- **D-34:** SLoC correlation: Claude's discretion (Spearman/Pearson).
- **D-35:** Token cost: Together AI pricing as constants.
- **D-36:** Exactly 14 roadmap dimensions.
- **D-37:** `--validate` flag for automated spot-checks.
- **D-38:** Validation includes cross-check comparison.
- **D-39:** Internal consistency checks in validation.
- **D-40:** Paper claims pre-audit in validation.
- **D-41:** Validation output to stdout AND JSON file.
- **D-42:** No `--dry-run` mode.

### Claude's Discretion
- JSON metadata content (file counts, timestamps, git hash)
- SLoC correlation method selection (Spearman vs Pearson vs both)
- Dimension-to-campaign mapping for edge cases
- Exact kernel ordering direction (ascending vs descending pass rate)
- Spot-check target selection for validation
- Edge cases in complexity classification
- Statistical test selection for OpenCL kernel-only effect (Fisher's exact vs Chi-squared)
- Statistical test selection for complexity correlation (Chi-squared vs Fisher's exact for small cells)

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| QUANT-01 | Aggregate pass rates by suite with Wilson 95% CIs | Wilson CI implementation in generate_paper_data.py lines 98-115; per-suite grouping by parsing source_spec prefix; data: 700 C1 valid files across 5 suites |
| QUANT-02 | Per-direction pass rates for all 6 standard + omp_target case-study | Direction extraction from source_spec/target_spec (rsplit on hyphen); 8 total directions in data; omp_target segregated per D-12 |
| QUANT-03 | Direction asymmetry with McNemar's test | McNemar implementation in generate_paper_data.py lines 167-215; pairs built from L0 records matching kernel across forward/reverse directions |
| QUANT-04 | Per-augmentation-level pass rates with Cochran-Armitage and Cohen's h | CA trend test in generate_paper_data.py lines 122-160; needs per-direction separate tests per D-31; Cohen's h: `2*arcsin(sqrt(p1)) - 2*arcsin(sqrt(p2))` |
| QUANT-05 | Failure taxonomy with build error subcategories | Classification patterns in generate_paper_data.py lines 222-486; 10+ build fail subcategories with regex patterns |
| QUANT-06 | Self-repair effectiveness from attempts[] arrays | Status ordering in selfrepair_analysis.py lines 32-40; classify_attempt_status + classify_repair functions; Campaign 1 only (max_retries=3) |
| QUANT-07 | Pass@k estimates from seed variants | Campaign 2 files (-s0/-s1/-s2); group by task (source_spec, target_spec), count passing seeds; report pass@1 (any) and pass@3 (all) |
| QUANT-08 | Per-kernel difficulty tiers | Group by kernel at L0, rank by pass rate, quartile boundaries, top-5/bottom-5 lists |
| QUANT-09 | Translation complexity correlation | Spec files provide translation_targets (list) and prompt_payload (list); classify pairs; Chi-squared or Fisher's exact test |
| QUANT-10 | Cross-suite comparison | Per-suite aggregates with SLoC from sloc_analysis.json; multi-file fraction from spec files |
| QUANT-11 | Token cost analysis | Pricing: $0.60 input / $3.60 output per 1M tokens; fields: prompt_tokens, completion_tokens in each result JSON |
| QUANT-12 | SLoC correlation with pass rate | SLoC from sloc_analysis.json keyed by kernel name; per-kernel pass rate from results; Spearman rho recommended |
| QUANT-13 | OpenCL kernel-only effect | Compare X-to-opencl pass rates (kernel-only, translation_type="kernel_only") vs X-to-omp (full_program); Fisher's exact recommended for small cells |
| QUANT-14 | Provenance trail for every number | Every computed value gets source/files_matched/derivation metadata; paper_claims section maps paper.tex locations to JSON paths |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Python 3 always**, never bare `python`. Venv: `source env_parbench/bin/activate`
- **Ruff** runs automatically via PostToolUse hook on all `.py` edits
- **Result JSONs are immutable** -- never modify existing result JSONs
- **`manifest.jsonl` is append-only** -- never modify existing entries
- **`overall_status` is authoritative** for result verdicts (not `run_status` or `error_message`)
- **`or {}` guard** for nullable spec fields: `(spec.get("field") or {}).get("subfield", default)`
- **Global flags BEFORE subcommand** for harness CLI
- **Pre-commit hook enforces `.validation_passed` sentinel** -- run `/validate` before commit
- **KNOWN_FAIL specs:** 8 specs (6 Rodinia + 2 HeCBench) -- exclude from eval batches
- **Use Opus for main work**
- **PROJECT_ROOT pattern:** `Path(__file__).resolve().parent.parent.parent`

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| scipy | 1.17.1 | Wilson CI (norm.ppf), McNemar (binomtest), Cochran-Armitage (chi2.cdf), Fisher's exact, chi2_contingency | Already used in statistical_analysis.py and generate_paper_data.py [VERIFIED: python3 import scipy] |
| numpy | 2.4.3 | Array operations for contingency tables, correlation | Already used in statistical_analysis.py [VERIFIED: python3 import numpy] |
| json (stdlib) | -- | JSON I/O for result files, spec files, output | Standard library [VERIFIED: codebase pattern] |
| argparse (stdlib) | -- | CLI argument parsing | Project convention per CLAUDE.md [VERIFIED: codebase pattern] |
| pathlib (stdlib) | -- | File path handling | Project convention [VERIFIED: codebase pattern] |
| math (stdlib) | -- | sqrt, asin for Cohen's h | Used in generate_paper_data.py [VERIFIED: codebase pattern] |
| re (stdlib) | -- | Filename parsing, error snippet classification | Used in generate_paper_data.py [VERIFIED: codebase pattern] |
| collections (stdlib) | -- | defaultdict, Counter for grouping | Used in all analysis scripts [VERIFIED: codebase pattern] |
| datetime (stdlib) | -- | Timestamps in metadata | Used in generate_paper_data.py [VERIFIED: codebase pattern] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| subprocess (stdlib) | -- | Get git hash for metadata | Optional, for reproducibility metadata |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom Wilson CI | statsmodels proportion_confint | statsmodels not in requirements; custom matches existing codebase |
| Manual Spearman | scipy.stats.spearmanr | scipy already available; spearmanr is the correct choice |

**Installation:**
No additional packages needed. All dependencies already in `requirements-lock.txt`.

## Architecture Patterns

### Recommended Project Structure
```
scripts/analysis/
    quantitative_findings.py   # New: monolithic script (D-01)
```

Output files:
```
results/analysis/
    quantitative_findings.json    # Machine-readable structured output
    quantitative_findings.md      # Human-readable paper-ready tables
    quantitative_findings_validation.json  # --validate output
```

### Pattern 1: Monolithic Analysis Script
**What:** Single script with all 14 dimensions computed in sequence, following benchmark_characterization.py pattern.
**When to use:** All Phase 9 work -- this is the locked decision.
**Example:**
```python
# Source: scripts/analysis/benchmark_characterization.py (project pattern)
#!/usr/bin/env python3
"""scripts/analysis/quantitative_findings.py

Comprehensive quantitative findings for SC26 paper.
Computes 14 dimensions from raw result JSONs.

Output: results/analysis/quantitative_findings.json + .md

Usage:
    python3 scripts/analysis/quantitative_findings.py \
        --project-root /home/samyak/Desktop/parbench_sam [-v] [--validate]
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
```

### Pattern 2: Data Loading and Campaign Separation
**What:** Load all result JSONs, exclude KNOWN_FAIL, split by campaign using temperature and filename suffix.
**When to use:** Foundation of all analysis -- must happen first.
**Example:**
```python
# Source: generate_paper_data.py lines 493-561 (project pattern)
EXCLUDED_SPECS: frozenset[str] = frozenset({
    "rodinia-kmeans-cuda",
    "rodinia-mummergpu-cuda",
    "rodinia-mummergpu-omp",
    "rodinia-hybridsort-cuda",
    "rodinia-nn-opencl",
    "rodinia-kmeans-opencl",
    "hecbench-stencil1d-omp_target",  # NEW: add HeCBench KNOWN_FAIL
    "hecbench-scan-omp_target",       # NEW: add HeCBench KNOWN_FAIL
})

def load_results(results_dir: Path, verbose: bool = False) -> list[dict]:
    """Load all result JSONs from the model directory."""
    records = []
    for json_file in sorted(results_dir.glob("*.json")):
        basename = json_file.name
        if basename.startswith("batch_") or basename == "eval_summary.json":
            continue
        data = json.load(open(json_file))
        stem = json_file.stem
        data["_filename"] = basename
        data["_stem"] = stem
        # Enrich with parsed metadata
        if "augment_level" not in data or data["augment_level"] is None:
            data["augment_level"] = _augment_level_from_filename(stem)
        if "direction" not in data or not data.get("direction"):
            data["direction"] = _direction_from_data(data)
        if "kernel" not in data or not data.get("kernel"):
            data["kernel"] = _kernel_from_spec(data.get("source_spec", ""))
        if "temperature" not in data or data["temperature"] is None:
            data["temperature"] = 0.0
        # Suite extraction
        data["_suite"] = data.get("source_spec", "").split("-")[0]
        records.append(data)
    return records

def split_campaigns(records: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split by temperature: Campaign 1 (temp=0.0), Campaign 2 (temp=0.7)."""
    primary = [r for r in records if (r.get("temperature") or 0) == 0.0]
    passk = [r for r in records if (r.get("temperature") or 0) > 0]
    return primary, passk
```

### Pattern 3: Wilson CI Computation
**What:** Wilson score confidence interval for binomial proportions.
**When to use:** Every pass rate computation in the script.
**Example:**
```python
# Source: generate_paper_data.py lines 98-115 (project pattern)
def wilson_ci(passes: int, total: int, alpha: float = 0.05) -> dict:
    """Wilson score CI. Returns dict with rate, ci_lower, ci_upper, n."""
    if total == 0:
        return {"value": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "n": 0,
                "ci_level": 0.95}
    z = sp_stats.norm.ppf(1 - alpha / 2)
    p_hat = passes / total
    denom = 1 + z**2 / total
    center = (p_hat + z**2 / (2 * total)) / denom
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * total)) / total) / denom
    return {
        "value": round(p_hat, 4),
        "ci_lower": round(max(0.0, center - spread), 4),
        "ci_upper": round(min(1.0, center + spread), 4),
        "n": total,
        "ci_level": 0.95,
    }
```

### Pattern 4: Filename Parsing for Campaign/Level/Seed
**What:** Extract augmentation level and seed from result filename stem.
**When to use:** Campaign discrimination and augmentation analysis.
**Example:**
```python
# Source: generate_paper_data.py lines 67-83 (project pattern)
def _augment_level_from_filename(stem: str) -> int:
    """L suffix -> augmentation level, else 0."""
    m = re.search(r"-L(\d+)(?:-s\d+)?$", stem)
    return int(m.group(1)) if m else 0

def _sample_id_from_filename(stem: str) -> int | None:
    """-s{N} suffix -> seed number, or None for Campaign 1."""
    m = re.search(r"-s(\d+)$", stem)
    return int(m.group(1)) if m else None
```

### Pattern 5: Provenance Wrapper
**What:** Every computed finding includes source metadata per D-19.
**When to use:** All output values in quantitative_findings.json.
**Example:**
```python
# New pattern required by D-19
def make_finding(value, source: str, files_matched: int, derivation: str,
                 ci_lower=None, ci_upper=None, ci_level=0.95) -> dict:
    """Wrap a computed value with provenance metadata."""
    result = {
        "value": value,
        "source": source,
        "files_matched": files_matched,
        "derivation": derivation,
    }
    if ci_lower is not None:
        result["ci_lower"] = ci_lower
        result["ci_upper"] = ci_upper
        result["ci_level"] = ci_level
    return result
```

### Pattern 6: Complexity Classification from Spec Files
**What:** Classify translation pairs by file count (single_file, multi_to_single, single_to_multi, multi_to_multi).
**When to use:** QUANT-09 complexity correlation dimension.
**Example:**
```python
# Source: classify_translation_pairs.py lines 49-70 (project pattern)
def _translation_targets_count(spec: dict) -> int:
    """Return number of translation target files."""
    files = spec.get("files") or {}
    tt = files.get("translation_targets")
    if tt is not None:
        return len(tt)
    return len(files.get("prompt_payload", []))

def _classify(src_count: int, tgt_count: int) -> str:
    if src_count == 1 and tgt_count == 1:
        return "single_file"
    elif src_count > 1 and tgt_count == 1:
        return "multi_to_single"
    elif src_count == 1 and tgt_count > 1:
        return "single_to_multi"
    else:
        return "multi_to_multi"
```

### Pattern 7: Pass@k from Seed Variants
**What:** Group Campaign 2 results by task, count passing seeds.
**When to use:** QUANT-07 pass@k dimension.
**Example:**
```python
# New pattern for pass@k (D-15, D-16)
def compute_pass_at_k(passk_records: list[dict]) -> dict:
    """pass@1 = any seed passes, pass@3 = all 3 seeds pass."""
    tasks: dict[tuple, list[bool]] = defaultdict(list)
    for r in passk_records:
        key = (r.get("source_spec"), r.get("target_spec"))
        tasks[key].append(r.get("overall_status") == "PASS")
    
    pass_at_1_count = sum(1 for seeds in tasks.values() if any(seeds))
    pass_at_3_count = sum(1 for seeds in tasks.values() if all(seeds) and len(seeds) == 3)
    total_tasks = len(tasks)
    
    return {
        "total_tasks": total_tasks,
        "pass_at_1": wilson_ci(pass_at_1_count, total_tasks),
        "pass_at_3": wilson_ci(pass_at_3_count, total_tasks),
    }
```

### Anti-Patterns to Avoid
- **Reading from intermediate analysis files for eval-derived metrics:** D-02 mandates raw JSON as primary source. Only SLoC data (static, not eval) may be read from existing analysis files.
- **Pooling campaigns:** D-05/D-08 strictly prohibit mixing Campaign 1 and Campaign 2 data.
- **Using `run_status` instead of `overall_status`:** Known quirk documented in CLAUDE.md and known-issues.md -- `overall_status` is authoritative.
- **Including KNOWN_FAIL specs:** All 8 must be excluded, not just the 6 Rodinia ones that `generate_paper_data.py` currently excludes.
- **Storing percentages (36.2%) instead of decimals (0.362):** D-21 mandates 0-1 decimals internally.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Wilson confidence intervals | Manual normal approximation | `scipy.stats.norm.ppf` + Wilson formula (already in codebase) | Wilson is more accurate at extremes; normal approx produces out-of-range CIs |
| McNemar's test | Manual chi-squared only | `scipy.stats.binomtest` for exact (n<25), chi-squared with continuity correction for large n | Exact test needed for small discordant counts |
| Cochran-Armitage trend test | Separate chi-squared tests per level | Custom implementation (already in generate_paper_data.py) | Tests for monotonic trend, not just independence |
| Fisher's exact test | Chi-squared with small cells | `scipy.stats.fisher_exact` | Chi-squared unreliable when expected cell counts < 5 |
| Spearman correlation | Manual rank computation | `scipy.stats.spearmanr` | Handles ties, returns p-value |
| JSON pretty-printing | Manual string formatting | `json.dumps(data, indent=2)` | Standard, reliable |

**Key insight:** All statistical tests needed are already implemented in the codebase (`generate_paper_data.py`, `statistical_analysis.py`). The implementations can be referenced for correctness, then re-applied to raw data per D-02.

## Common Pitfalls

### Pitfall 1: Excluding Only 6 KNOWN_FAIL Specs
**What goes wrong:** `generate_paper_data.py` only excludes 6 Rodinia specs. Phase 9 must exclude all 8 (including 2 HeCBench: `hecbench-stencil1d-omp_target`, `hecbench-scan-omp_target`).
**Why it happens:** Historical -- original analysis was Rodinia-only.
**How to avoid:** Use the full 8-spec exclusion set. Verified file impact: 128 files excluded (some have both src and tgt as KF, counted once), yielding 1120 valid files.
**Warning signs:** Total valid file count != 1120, or suite-level totals don't sum correctly.

### Pitfall 2: Campaign Discrimination Race Condition
**What goes wrong:** Relying solely on filename suffix for campaign separation vs. relying solely on temperature field. Both should agree, but edge cases possible.
**Why it happens:** D-06 specifies filename suffix as the discriminator; temperature field is the semantic meaning.
**How to avoid:** Use temperature field as primary discriminator (consistent with `generate_paper_data.py`), assert filename suffix agrees. Log any discrepancies.
**Warning signs:** Campaign file counts don't match: C1=700, C2=420 (after KF exclusion with all 8 specs).

### Pitfall 3: Direction Extraction from omp_target Specs
**What goes wrong:** `spec.rsplit("-", 1)[-1]` on `hecbench-convolution1d-omp_target` returns `omp_target` (correct), but on `rodinia-mummergpu-omp` returns `omp`. This is correct behavior but the underscore in `omp_target` can cause issues if directions are sorted or used as dict keys carelessly.
**Why it happens:** `omp_target` is a two-word API name joined by underscore.
**How to avoid:** Use the established `_direction_from_data()` helper that extracts API from the last hyphen-separated component.
**Warning signs:** `omp_target` directions missing or merged with `omp`.

### Pitfall 4: McNemar Pairing Across Suites
**What goes wrong:** McNemar pairs should match kernel names across forward/reverse directions. But kernels with the same name across suites (unlikely but possible) would create false pairs.
**Why it happens:** Kernel name alone isn't unique across suites.
**How to avoid:** Pair on (suite, kernel, source_api, target_api) to ensure exact matching.
**Warning signs:** More paired observations than expected for a direction.

### Pitfall 5: pass@k Task Grouping
**What goes wrong:** Campaign 2 has 3 seeds per task, but task identification must match on (source_spec, target_spec) exactly. Augmented variants (-L{N}-s{M}) don't exist in Campaign 2 data.
**Why it happens:** Campaign 2 is L0-only (verified: all seed files have augment_level=0, temperature=0.7).
**How to avoid:** Group strictly by (source_spec, target_spec). Verify each task has exactly 3 seeds.
**Warning signs:** Tasks with != 3 seeds, or augment_level != 0 in Campaign 2 data.

### Pitfall 6: Complexity Classification for Multi-Spec Kernels
**What goes wrong:** A result file references `source_spec` and `target_spec`. The complexity depends on both the source's file count and the target's file count. Some specs have `translation_targets` as a list (correct), but spec loading must handle the `or {}` guard.
**Why it happens:** The spec file format uses lists for `translation_targets` and `prompt_payload`.
**How to avoid:** Load both source and target spec files, count `translation_targets` in each, classify the pair.
**Warning signs:** Missing spec files for HeCBench kernels (they exist -- verified), or complexity counts not summing to total.

### Pitfall 7: Paper Claims Referencing Rodinia-Only Numbers
**What goes wrong:** Many paper.tex claims reference Rodinia-only numbers (480 primary tasks, 36.2% pass rate). Phase 9 computes ALL-suite numbers. The paper_claims section must track which scope each claim uses.
**Why it happens:** Paper was initially written with Rodinia data only; it has since been updated with some all-suite numbers but retains some Rodinia-specific claims.
**How to avoid:** In the paper_claims mapping, explicitly note the scope (all-suite vs Rodinia-only vs per-suite). Provide both all-suite and Rodinia-specific values where the paper uses Rodinia-specific numbers.
**Warning signs:** Validation shows many paper claims as "mismatched" when the scope simply differs.

### Pitfall 8: Self-Repair in Campaign 2
**What goes wrong:** Campaign 2 has max_retries=1, meaning only 1 attempt (no self-repair). Self-repair analysis must be restricted to Campaign 1 (max_retries=3).
**Why it happens:** D-29 says "compute from raw attempts[]" but doesn't explicitly mention campaign restriction. Campaign 2 files have `total_attempts=1` by design.
**How to avoid:** Only analyze self-repair for Campaign 1 records where max_retries > 1.
**Warning signs:** Self-repair rate of 0% in Campaign 2 (expected but shouldn't be reported as a finding).

## Code Examples

### Complete Data Pipeline Skeleton
```python
# Source: synthesized from generate_paper_data.py + benchmark_characterization.py patterns
def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive quantitative findings for SC26 paper"
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--validate", action="store_true",
                        help="Run automated spot-checks and cross-validation")
    args = parser.parse_args()

    results_dir = args.project_root / "results" / "evaluation" / "together-qwen-3.5-397b-a17b"
    
    # 1. Load all result JSONs
    all_records = load_results(results_dir, verbose=args.verbose)
    
    # 2. Exclude KNOWN_FAIL specs
    valid = exclude_known_fail(all_records)
    
    # 3. Split campaigns
    campaign_1, campaign_2 = split_campaigns(valid)
    
    # 4. Compute Campaign 1 dimensions (12+)
    c1_results = analyze_campaign_1(campaign_1, args.project_root, args.verbose)
    
    # 5. Compute Campaign 2 dimensions (pass@k)
    c2_results = analyze_campaign_2(campaign_2, args.verbose)
    
    # 6. Build paper_claims mapping
    claims = build_paper_claims(c1_results, c2_results, args.project_root)
    
    # 7. Cross-check against existing analysis files
    cross_checks = cross_check(c1_results, c2_results, args.project_root, args.verbose)
    
    # 8. Assemble output
    output = {
        "metadata": build_metadata(all_records, valid, campaign_1, campaign_2, args),
        "campaign_1": c1_results,
        "campaign_2": c2_results,
        "paper_claims": claims,
        "cross_checks": cross_checks,
    }
    
    # 9. Write JSON + markdown
    output_dir = args.project_root / "results" / "analysis"
    write_json(output, output_dir / "quantitative_findings.json")
    write_markdown(output, output_dir / "quantitative_findings.md")
    
    # 10. Validate if requested
    if args.validate:
        validation = run_validation(output, args.project_root, args.verbose)
        write_json(validation, output_dir / "quantitative_findings_validation.json")
    
    # 11. Print summary
    print(f"Quantitative findings: {len(all_records)} files processed, "
          f"{len(valid)} valid, {len(campaign_1)} C1, {len(campaign_2)} C2, "
          f"14 dimensions computed"
          + (f", {len(cross_checks.get('warnings', []))} cross-check warnings" if cross_checks else ""))

if __name__ == "__main__":
    main()
```

### Direction Asymmetry with McNemar (adapted for Phase 9)
```python
# Source: generate_paper_data.py lines 752-794 (project pattern, adapted)
def compute_direction_asymmetry(records: list[dict]) -> dict:
    """McNemar's exact test for paired direction comparison at L0."""
    l0 = [r for r in records if r.get("augment_level", 0) == 0]
    
    # Build lookup: (suite, kernel, direction) -> passed
    lookup: dict[tuple, bool] = {}
    for r in l0:
        suite = r.get("_suite", "unknown")
        kernel = r.get("kernel", "?")
        direction = r.get("direction", "unknown")
        passed = r.get("overall_status") == "PASS"
        lookup[(suite, kernel, direction)] = passed
    
    # Identify direction pairs and run McNemar
    # ... (follow existing pattern)
```

### Cochran-Armitage Per-Direction
```python
# Source: generate_paper_data.py lines 657-745 + D-31 extension
def compute_augmentation_trend(records: list[dict]) -> dict:
    """Cochran-Armitage for ALL directions separately AND aggregate."""
    result = {}
    
    # Aggregate across all directions
    result["aggregate"] = _cochran_armitage_for_records(records)
    
    # Per-direction
    by_dir: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_dir[r.get("direction", "unknown")].append(r)
    
    result["per_direction"] = {}
    for d, recs in sorted(by_dir.items()):
        result["per_direction"][d] = _cochran_armitage_for_records(recs)
    
    # Cohen's h between adjacent levels
    result["cohens_h_adjacent"] = _compute_adjacent_cohens_h(records)
    
    return result
```

### SLoC Correlation
```python
# Source: sloc_analysis.json structure + scipy.stats
def compute_sloc_correlation(campaign_1: list[dict], project_root: Path) -> dict:
    """Spearman + Pearson correlation between kernel SLoC and pass rate."""
    # Load SLoC data
    sloc_path = project_root / "results" / "analysis" / "sloc_analysis.json"
    sloc_data = json.loads(sloc_path.read_text())
    
    # Build per-kernel pass rates at L0
    l0 = [r for r in campaign_1 if r.get("augment_level", 0) == 0]
    kernel_pass: dict[str, dict] = defaultdict(lambda: {"pass": 0, "total": 0})
    for r in l0:
        k = r.get("kernel", "?")
        kernel_pass[k]["total"] += 1
        if r.get("overall_status") == "PASS":
            kernel_pass[k]["pass"] += 1
    
    # Pair SLoC with pass rate
    sloc_vals = []
    rate_vals = []
    kernels_data = sloc_data.get("kernels", {})
    for k, counts in kernel_pass.items():
        if k in kernels_data and counts["total"] > 0:
            sloc_vals.append(kernels_data[k]["physical_sloc"])
            rate_vals.append(counts["pass"] / counts["total"])
    
    if len(sloc_vals) < 3:
        return {"error": "Insufficient data for correlation"}
    
    spearman_r, spearman_p = sp_stats.spearmanr(sloc_vals, rate_vals)
    pearson_r, pearson_p = sp_stats.pearsonr(sloc_vals, rate_vals)
    
    return {
        "n_kernels": len(sloc_vals),
        "spearman": {"rho": round(spearman_r, 4), "p_value": round(spearman_p, 6)},
        "pearson": {"r": round(pearson_r, 4), "p_value": round(pearson_p, 6)},
    }
```

## Verified Data Landscape

### File Count Summary (VERIFIED against raw files on disk)

| Category | Count | Source |
|----------|-------|--------|
| Total result JSONs on disk | 1,248 | `ls *.json \| wc -l` [VERIFIED: filesystem] |
| Campaign 1 (temp=0.0, all levels) | 780 | [VERIFIED: grep + count] |
| Campaign 2 (temp=0.7, seeds s0-s2) | 468 | [VERIFIED: grep + count] |
| KNOWN_FAIL exclusion (all 8 specs) | 128 | [VERIFIED: python3 json scan] |
| Campaign 1 valid (excl KF) | 700 | 780 - 80 = 700 [VERIFIED] |
| Campaign 2 valid (excl KF) | 420 | 468 - 48 = 420 [VERIFIED] |
| Campaign 1 L0 | 156 | [VERIFIED: filename parse] |
| Campaign 1 L1-L4 | 624 | 156 * 4 = 624 [VERIFIED] |
| Campaign 1 L0 valid (excl KF) | 140 | [VERIFIED: python3 scan] |

### Per-Suite Campaign 1 Valid File Counts [VERIFIED]

| Suite | Campaign 1 | Campaign 2 |
|-------|-----------|-----------|
| Rodinia | 480 | 288 |
| HeCBench | 130 | 78 |
| XSBench | 30 | 18 |
| RSBench | 30 | 18 |
| mixbench | 30 | 18 |
| **Total** | **700** | **420** |

### Direction Distribution (L0, Campaign 1, excl KF) [VERIFIED]

| Direction | Count | Standard/Case-study |
|-----------|-------|---------------------|
| cuda-to-omp | 24 | Standard |
| omp-to-cuda | 24 | Standard |
| cuda-to-opencl | 20 | Standard |
| opencl-to-cuda | 20 | Standard |
| omp-to-opencl | 18 | Standard |
| opencl-to-omp | 18 | Standard |
| cuda-to-omp_target | 8 | Case-study |
| omp_target-to-cuda | 8 | Case-study |

### Result JSON Fields Available [VERIFIED: file inspection]

**Top-level fields used for analysis:**
- `source_spec`, `target_spec` -- spec identification
- `kernel` -- kernel name
- `overall_status` -- authoritative verdict: PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/EXTRACTION_FAIL
- `augment_level` -- 0-4 (Campaign 1) or 0 (Campaign 2)
- `temperature` -- 0.0 (Campaign 1) or 0.7 (Campaign 2)
- `sample_id` -- 0 (Campaign 1) or 0/1/2 (Campaign 2)
- `max_retries` -- 3 (Campaign 1) or 1 (Campaign 2)
- `total_attempts` -- 1-3 (Campaign 1) or 1 (Campaign 2)
- `prompt_tokens`, `completion_tokens` -- token counts
- `build_status`, `run_status`, `verify_status` -- per-stage status
- `build_error_snippet`, `run_stderr_snippet`, `run_stdout_snippet` -- error details
- `translation_type` -- "kernel_only" or "full_program"
- `error_message` -- extraction failure details

**Attempts array fields:**
- `attempt` -- attempt number (1-indexed)
- `build_status`, `run_status`, `verify_status` -- per-attempt status
- `extraction_fail` -- boolean
- `build_error_snippet`, `run_stderr_snippet`, `run_stdout_snippet` -- per-attempt details
- `prompt_tokens`, `completion_tokens` -- per-attempt token counts

### SLoC Data Location [VERIFIED]
- `results/analysis/sloc_analysis.json` -- keyed by kernel name (e.g., "backprop", "bfs")
- Each entry has `physical_sloc` field (integer)
- 35 kernels total

### Together AI Pricing [VERIFIED: Together AI website, confirmed against token_analysis.py]
- Input: $0.60 per 1M tokens
- Output: $3.60 per 1M tokens

### Existing Paper Claims to Map [VERIFIED: paper.tex grep]

Key claims in paper.tex that need provenance trails:
1. "overall pass rate of 36.2% [32.1%, 40.6%]" -- line 71, from 480 Rodinia primary tasks
2. "480 primary campaign tasks" -- lines 71, 106
3. "426 pass@k tasks" -- lines 106, 118
4. "BUILD_FAIL accounts for 30.8%" -- lines 71, 137
5. "VERIFY_FAIL accounts for 9.8%" -- lines 71, 137
6. "CUDA-to-OpenMP 65.0% [54.1%, 74.6%]" -- line 71
7. "68.8% at L0" -- lines 71, 135
8. "Cochran-Armitage z = -0.17, p = 0.87" -- lines 71, 139
9. "Self-repair doubles from 17.5% to 36.2%" -- line 143
10. "90 of 396 initially-failing tasks (22.7% repair rate)" -- line 143
11. "5 regressions (1.0%)" -- line 143
12. "Cohen's h = 0.26-0.31" -- lines 126, 141
13. "96 benchmark specifications" -- line 71
14. "OpenCL-to-CUDA (7.1%)" -- line 141
15. "24/96 (25%) multi-file" -- line 536

**Critical note:** Many of these reference Rodinia-only (480 tasks). Phase 9 will compute all-suite equivalents (700 C1 tasks). The paper_claims section must handle the scope mapping.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Rodinia-only analysis (480 tasks) | All-suite analysis (700 C1 / 420 C2 tasks) | 2026-04-03 (eval completion) | Numbers change; Rodinia subset should still be derivable |
| 6 KNOWN_FAIL exclusions | 8 KNOWN_FAIL exclusions | 2026-04-03 (HeCBench added) | 16 more files excluded |
| Single paper_data.json | Comprehensive quantitative_findings.json + paper_claims | Phase 9 (now) | Provenance tracking, 14-dimension coverage |
| Separate analysis scripts | Single monolithic quantitative findings | Phase 9 (now) | Cross-check against existing, single source of truth |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Spearman correlation is appropriate for SLoC vs pass rate (non-normal, ordinal-like data) | SLoC Correlation | LOW: Pearson also computed as backup; both are standard |
| A2 | Fisher's exact test is more appropriate than Chi-squared for OpenCL kernel-only effect (small cell counts expected with only 3 suites having OpenCL) | Statistical Methods | LOW: both will be computed; report whichever is appropriate given sample sizes |
| A3 | Paper claims referencing 480 tasks are Rodinia-only scoped; Phase 9 provides all-suite equivalents | Paper Claims | MEDIUM: if paper expects Phase 9 to replace 480-task numbers with 700-task numbers, the mapping is wrong. Mitigation: provide both in paper_claims |
| A4 | All Campaign 2 files have augment_level=0 (L0 only) | Campaign Separation | LOW: verified for sampled files; should be asserted in script |

## Open Questions

1. **Paper Claim Scope Resolution**
   - What we know: Paper.tex has many Rodinia-specific claims (480 tasks, 36.2%). Phase 9 computes all-suite numbers (700 tasks).
   - What's unclear: Should paper_claims map to Rodinia-subset or all-suite values? Or both?
   - Recommendation: Provide both. Each claim gets a `scope` field ("rodinia_only" or "all_suite"). Phase 10/11 decides which to use. Include Rodinia-only computations as a named subsection within Campaign 1.

2. **Build Error Subcategory Taxonomy Depth**
   - What we know: D-28 says "top-3 most common build error subcategories." The existing taxonomy has 10+ subcategories.
   - What's unclear: Should we report all subcategories or only top-3?
   - Recommendation: Compute all subcategories, sort by frequency, report top-3 in markdown. Full data in JSON.

3. **omp_target in Cochran-Armitage**
   - What we know: D-31 says "ALL directions separately." omp_target directions have only 8 L0 tasks each, limiting statistical power.
   - What's unclear: Whether Cochran-Armitage is meaningful with n=8 per level.
   - Recommendation: Compute it anyway but flag low sample size. Include an `adequate_sample_size` boolean per direction (threshold: n >= 10 per level).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | Script execution | Y | 3.12.3 | -- |
| scipy | Statistical tests | Y | 1.17.1 | -- |
| numpy | Array operations | Y | 2.4.3 | -- |
| ruff | Linting | Y | 0.11.13+ | -- |

No missing dependencies.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | pyproject.toml (ruff + pytest config) |
| Quick run command | `python3 -m pytest scripts/analysis/test_quantitative_findings.py -x` |
| Full suite command | `python3 -m pytest scripts/analysis/test_quantitative_findings.py -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| QUANT-01 | Aggregate pass rates by suite with Wilson CIs | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_suite_pass_rates -x` | Wave 0 |
| QUANT-02 | Per-direction pass rates | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_direction_pass_rates -x` | Wave 0 |
| QUANT-05 | Failure taxonomy | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_failure_taxonomy -x` | Wave 0 |
| QUANT-07 | pass@k estimates | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_passk -x` | Wave 0 |
| QUANT-09 | Complexity classification | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_complexity -x` | Wave 0 |
| QUANT-14 | Provenance trail | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_provenance -x` | Wave 0 |
| ALL | Script runs end-to-end | integration | `python3 scripts/analysis/quantitative_findings.py --project-root /home/samyak/Desktop/parbench_sam` | Wave 0 |
| ALL | Validation passes | integration | `python3 scripts/analysis/quantitative_findings.py --project-root /home/samyak/Desktop/parbench_sam --validate` | Wave 0 |

### Sampling Rate
- **Per task commit:** Quick run on critical tests
- **Per wave merge:** Full test suite + script end-to-end run
- **Phase gate:** Full suite green + `--validate` passes before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `scripts/analysis/test_quantitative_findings.py` -- covers QUANT-01 through QUANT-14 critical checks
- [ ] End-to-end test: run script, verify JSON output has all required sections
- [ ] Validation test: run `--validate`, verify all checks pass

## Security Domain

Not applicable. This phase processes only local data files (JSON) with no network I/O, no user input, no authentication, and no secrets handling. `security_enforcement` is not relevant for a data analysis script operating on immutable local files.

## Sources

### Primary (HIGH confidence)
- `scripts/analysis/generate_paper_data.py` -- reference implementation for data loading, Wilson CI, McNemar, Cochran-Armitage, error taxonomy, campaign separation [VERIFIED: direct code read]
- `scripts/analysis/statistical_analysis.py` -- reference implementation for Wilson CI, chi-squared, Fisher's exact, Cochran-Armitage, Cohen's h [VERIFIED: direct code read]
- `scripts/analysis/selfrepair_analysis.py` -- reference for self-repair classification from attempts[] [VERIFIED: direct code read]
- `scripts/analysis/build_error_taxonomy.py` -- reference for error subcategory regex patterns [VERIFIED: direct code read]
- `scripts/analysis/token_analysis.py` -- reference for pricing constants and token extraction [VERIFIED: direct code read]
- `scripts/analysis/classify_translation_pairs.py` -- reference for complexity classification [VERIFIED: direct code read]
- `results/evaluation/together-qwen-3.5-397b-a17b/*.json` -- raw result JSON structure [VERIFIED: direct file inspection]
- `results/analysis/sloc_analysis.json` -- SLoC data structure [VERIFIED: direct file inspection]
- `results/analysis/paper_data.json` -- existing analysis output structure [VERIFIED: direct file inspection]
- `docs/paper/latex/paper.tex` -- paper claims to map [VERIFIED: grep scan]

### Secondary (MEDIUM confidence)
- [Together AI Qwen3.5-397B-A17B pricing](https://www.together.ai/models/qwen3-5-397b-a17b) -- $0.60 input / $3.60 output per 1M tokens [VERIFIED: website fetch, matches token_analysis.py]

### Tertiary (LOW confidence)
None -- all claims verified.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already in use, versions verified
- Architecture: HIGH -- follows established monolithic script pattern from Phase 2/3
- Pitfalls: HIGH -- derived from actual codebase inspection and file counting
- Data landscape: HIGH -- all numbers verified against actual files on disk

**Research date:** 2026-04-04
**Valid until:** 2026-04-15 (data is static; no new eval runs expected before deadline)
