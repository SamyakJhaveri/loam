# Phase 16: GPT-4.1 Mini Data Analysis & Summary Generation - Research

**Researched:** 2026-04-07
**Domain:** Data analysis pipeline (Python scripts), statistical computation, figure generation
**Confidence:** HIGH

## Summary

Phase 16 produces all machine-readable analysis artifacts that Phase 17 needs to fill 18 `\pending{}` narrative markers and 24 `\tbd{}` table cells in `paper.tex`. The infrastructure is largely in place: `eval_summary.json` already contains both models (2 keys), `generate_paper_data.py` accepts `--results-dir` for per-model output, and `generate_paper_figures.py` auto-discovers all models via `load_eval_results()`. The critical path is writing `cross_model_comparison.py` from scratch -- this script does not exist yet and Phase 17B (Section 6.9) is hard-gated on its output.

There are three significant findings from research: (1) `build_error_taxonomy.py` does NOT have `--results-dir` -- it uses `--project-root` and iterates ALL model directories, so the PLAN.md T3 command is wrong; (2) `generate_paper_figures.py`'s T2 table generator is hardcoded with "pending" for GPT and will NOT auto-populate with real data even after figure regeneration; (3) `eval_summary.json` already has both models with GPT showing 222/815 = 27.2% pass rate (not the ~26.6% from the earlier estimate, likely due to including all suites vs. primary-campaign-only filtering).

**Primary recommendation:** Fix the T3 command to use `--project-root`, fix T2 table generation in the figure script to use actual GPT data, then follow the T1-T6 execution order with T4 (cross_model_comparison.py) as the highest-risk critical path item.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Full run, no deferrals. All T1-T6 as planned. No tasks skipped even under deadline pressure.
- **D-02:** Run `--figure all` -- regenerate all 13 figures in one command. Accept small style-drift risk from matplotlib version. F7 was already refactored in Phase 15.5 (dual-model with Wilson CI); T5 will update it with real GPT data.
- **D-03:** Full statistics suite -- all four outputs required: (1) Chi-squared test on 2x2 contingency table, (2) Per-direction paired comparison for 7 common directions only, (3) Cohen's h effect sizes, (4) Per-kernel agreement matrix with four-way granularity.
- **D-04:** Four-way kernel matrix (both-pass / both-fail / Qwen-only-pass / GPT-only-pass), not binary.
- **D-05:** Phase 16 is BLOCKED on Le's `omp_target-to-cuda` GPT evaluation data.
- **D-05-fallback:** If Le cannot deliver by end of day April 7, proceed with 7-direction cross-model comparison with footnote.

### Claude's Discretion
None specified -- all decisions are locked.

### Deferred Ideas (OUT OF SCOPE)
- omp_target-to-cuda direction cross-model comparison -- blocked on Le's data
- Per-kernel matrix visualization (heatmap figure) -- leave as JSON output
</user_constraints>

## Current State Inventory

### GPT Result Files [VERIFIED: filesystem scan]
- **Total files:** 897 in `results/evaluation/azure-gpt-4.1-mini/`
- **Directions present (7):**
  - cuda-to-omp: 208 files
  - cuda-to-opencl: 184 files
  - omp-to-opencl: 160 files
  - opencl-to-omp: 160 files
  - omp-to-cuda: 94 files
  - cuda-to-omp_target: 64 files
  - opencl-to-cuda: 27 files
- **Direction MISSING:** omp_target-to-cuda (0 files) -- BLOCKER per D-05

### eval_summary.json [VERIFIED: JSON inspection]
- **Already has 2 model keys:** `azure-gpt-4.1-mini` and `together-qwen-3.5-397b-a17b`
- GPT stats: 222 PASS / 815 total = 27.24%
- Qwen stats: 356 PASS / 1136 total = 31.34%
- **Implication for T1:** Running `analyze_eval.py` will REGENERATE this file. The current file already has both models, so T1 is effectively a refresh/validation step, not a "first discovery" step.
- **Note:** The 27.24% overall rate differs from the CONTEXT.md estimate of ~26.6%. The CONTEXT.md figure may be from an earlier count or primary-campaign-only filtering (EXCLUDED_SPECS + pass@k exclusion).

### results/analysis/ [VERIFIED: filesystem scan]
- `paper_data.json` -- Qwen only (model: together-qwen-3.5-397b-a17b), 710 primary campaign tasks, 38.3% overall pass rate
- `paper_data_rodinia.json` -- Qwen Rodinia subset
- `error_taxonomy.json` -- Qwen only (1248 total results, per_model has only together-qwen-3.5-397b-a17b)
- **Missing (expected):** `paper_data_gpt41mini.json`, `error_taxonomy_gpt41mini.json`, `cross_model_comparison.json`, `coverage_gaps.md`

### cross_model_comparison.py [VERIFIED: filesystem check]
- **DOES NOT EXIST** -- must be written from scratch. This is the critical path.

## Standard Stack

### Core (already installed)
| Library | Version | Purpose | Verified |
|---------|---------|---------|----------|
| scipy | 1.17.1 | Chi-squared test, Wilson CI, binomial test | [VERIFIED: pip import] |
| numpy | 2.4.3 | Array operations, contingency tables | [VERIFIED: pip import] |
| matplotlib | 3.10.8 | Figure generation | [VERIFIED: pip import] |
| scienceplots | (installed) | IEEE publication styles | [VERIFIED: pip import] |

No new packages needed. All statistical functions available in scipy.stats.

## Architecture Patterns

### Script CLI Interfaces (CRITICAL -- fixes needed)

| Script | CLI Interface | Per-Model? | Output |
|--------|--------------|------------|--------|
| `analyze_eval.py` | `--project-root` | Auto-discovers ALL models | `eval_summary.json` (multi-model) |
| `generate_paper_data.py` | `--results-dir` + `--output` | YES -- single model per run | `paper_data_*.json` (single-model) |
| `build_error_taxonomy.py` | `--project-root` ONLY | NO -- iterates ALL models | `error_taxonomy.json` (multi-model) |
| `generate_paper_figures.py` | `--project-root` + `--figure` | Auto-discovers ALL models | `docs/paper/figures/*.pdf` |

### PLAN.md T3 Command is WRONG [VERIFIED: --help output]

The PLAN.md specifies:
```bash
python3 scripts/analysis/build_error_taxonomy.py \
  --results-dir results/evaluation/azure-gpt-4.1-mini \
  --output results/analysis/error_taxonomy_gpt41mini.json
```

**This will FAIL.** `build_error_taxonomy.py` does not accept `--results-dir` or `--output`. It only accepts `--project-root` and always writes to `results/analysis/error_taxonomy.json` and `results/analysis/error_taxonomy.md`.

**Correct approach for T3:** Run `build_error_taxonomy.py --project-root /home/samyak/Desktop/parbench_sam` -- this will regenerate `error_taxonomy.json` with BOTH models in the `per_model` dict. To produce a separate GPT-only file (`error_taxonomy_gpt41mini.json`), the planner has two options:

1. **Option A (recommended):** Just re-run the script. The output `error_taxonomy.json` will contain `per_model` with both `together-qwen-3.5-397b-a17b` and `azure-gpt-4.1-mini`. `cross_model_comparison.py` can extract GPT data from this combined file.

2. **Option B:** Write a small wrapper or modify the script to accept `--model` filter. This adds complexity for marginal benefit.

### T2 Table Generation is HARDCODED [VERIFIED: code inspection]

`generate_paper_figures.py` lines 1612-1616 hardcode the GPT row as "pending":
```python
# GPT row (all pending)
pending_cells = ["pending"] * (1 + len(DIRECTIONS))
lines.append(
    "GPT-4.1 mini & " + " & ".join(pending_cells) + r" \\"
)
```

**When T5 runs `--figure all`, T2 will still show "pending" for GPT.** The planner must either:
1. Fix `generate_t2_model_table()` before T5 to compute actual GPT stats (like the Qwen row does), OR
2. Accept that T2 will be wrong and fix it in Phase 17 as a paper.tex edit.

**Recommendation:** Fix it in T5's scope. The code already has the pattern from the Qwen row (lines 1576-1609). Duplicating it for GPT is ~15 lines of code.

### paper_data.json Schema [VERIFIED: JSON inspection]

The `paper_data.json` output from `generate_paper_data.py` has this structure (both Qwen and GPT outputs will match):

```python
{
    "model": "together-qwen-3.5-397b-a17b",
    "results_dir": "...",
    "primary_campaign": {
        "total": 710,
        "overall": {
            "total": 710, "pass": 272,
            "pass_rate": 0.3831,           # NOTE: field is "pass_rate" not "rate"
            "ci_lower": 0.3481, "ci_upper": 0.4194,
            "by_status": {"BUILD_FAIL": 241, ...}
        },
        "by_direction": {
            "cuda-to-omp": {
                "total": 120, "pass": 77,
                "pass_rate": 0.6417,       # NOTE: "pass_rate" not "rate"
                "ci_lower": 0.5527, "ci_upper": 0.7218,
                "by_status": {...}
            },
            ...
        },
        "by_kernel": {
            "backprop": {"total": 30, "pass": 13, "pass_rate": 0.4333, ...},
            ...
        }
    }
}
```

**Key for cross_model_comparison.py:** The field name is `pass_rate`, not `rate`. The `eval_summary.json` uses `rate` while `paper_data.json` uses `pass_rate`. This naming inconsistency must be handled.

### error_taxonomy.json Schema [VERIFIED: JSON inspection]

```python
{
    "total_results": 1248,
    "total_pass": 356,
    "total_failures": 892,
    "status_counts": {...},
    "build_fail_categories": {...},     # Each has "by_model" breakdown
    "run_fail_categories": {...},
    "per_model": {
        "together-qwen-3.5-397b-a17b": {
            "total": 1248, "pass": 356,
            "build_fail": {"other_build": 86, ...},
            "run_fail": {...},
            ...
        }
    }
}
```

After re-running with GPT data present, `per_model` will have both model keys.

### Execution Order [VERIFIED: PLAN.md + dependency analysis]

```
T1 (analyze_eval) -> T2 + T3 (parallel) -> T3b (gate) -> T4 + T5 (parallel) -> T6
```

**Refinement:** T2 and T3 can also start without waiting for T1, since they read raw result JSONs directly. However, T1 first ensures data integrity via the aggregator.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chi-squared test | Custom implementation | `scipy.stats.chi2_contingency` | Handles Yates correction, returns p-value |
| Cohen's h effect size | Custom math | `2 * arcsin(sqrt(p1)) - 2 * arcsin(sqrt(p2))` | Formula is simple but edge cases (p=0, p=1) need clamping -- copy from `generate_paper_data.py` lines 200-203 |
| Wilson CI | Custom formula | Copy from `generate_paper_data.py:wilson_ci()` | Already tested, uses scipy.stats.norm.ppf |
| Per-kernel matching | Custom name parsing | `_kernel_from_spec()` pattern: `spec_id.split("-")` then `"-".join(parts[1:-1])` | Both scripts use this -- keep consistent |

## Common Pitfalls

### Pitfall 1: build_error_taxonomy.py CLI Mismatch
**What goes wrong:** T3 command fails with "unrecognized arguments: --results-dir"
**Why it happens:** PLAN.md assumed the script had per-model CLI like `generate_paper_data.py`
**How to avoid:** Use `--project-root` only. Accept combined multi-model output.
**Warning signs:** Script exits with error code 2

### Pitfall 2: paper_data.json Field Name "pass_rate" vs "rate"
**What goes wrong:** `cross_model_comparison.py` reads `paper_data["primary_campaign"]["overall"]["rate"]` and gets KeyError
**Why it happens:** `eval_summary.json` uses "rate" but `paper_data.json` uses "pass_rate"
**How to avoid:** Use "pass_rate" when reading paper_data.json files
**Warning signs:** KeyError in cross_model_comparison.py

### Pitfall 3: T2 Table Hardcoded "pending"
**What goes wrong:** After T5 figure regeneration, `t2_model_comparison.tex` still shows "pending" for GPT
**Why it happens:** `generate_t2_model_table()` hardcodes GPT row as all "pending"
**How to avoid:** Fix `generate_t2_model_table()` to compute GPT stats from records before running T5
**Warning signs:** Visual inspection of generated .tex file

### Pitfall 4: GPT Missing omp_target-to-cuda Direction
**What goes wrong:** cross_model_comparison.py crashes when trying to pair Qwen's omp_target-to-cuda data with non-existent GPT data
**Why it happens:** GPT has 7 directions, Qwen has 8
**How to avoid:** Per-direction comparison must use only common directions (7). Overall comparison uses all available data per model.
**Warning signs:** KeyError or empty comparison for omp_target-to-cuda

### Pitfall 5: GPT Total Tasks vs Primary Campaign Tasks
**What goes wrong:** Comparing raw totals (815 GPT vs 1136 Qwen) is misleading because they include different augmentation levels and sample counts
**Why it happens:** GPT may not have the same augmentation and pass@k coverage as Qwen
**How to avoid:** `paper_data_gpt41mini.json` filters to primary campaign (temp=0, non-sample) automatically
**Warning signs:** Total task counts not matching expected primary campaign sizes

### Pitfall 6: error_taxonomy_gpt41mini.json Naming Expectation
**What goes wrong:** Downstream scripts expect `error_taxonomy_gpt41mini.json` but `build_error_taxonomy.py` always writes `error_taxonomy.json`
**Why it happens:** The plan assumed per-model output files
**How to avoid:** Either (a) accept that the combined file is sufficient, or (b) add a post-processing step to extract GPT data into a separate file
**Warning signs:** Missing file errors in T4/T6

## Code Examples

### Chi-squared Test Pattern (for cross_model_comparison.py)
```python
# Source: scipy docs + existing codebase pattern
from scipy import stats as sp_stats
import numpy as np

# Build 2x2 contingency table: model x pass/fail
# Qwen: pass=272, fail=438 (710 total primary)
# GPT:  pass=X,   fail=Y
table = np.array([[qwen_pass, qwen_fail],
                   [gpt_pass, gpt_fail]])
chi2, p_value, dof, expected = sp_stats.chi2_contingency(table)
```
[VERIFIED: scipy.stats.chi2_contingency available in scipy 1.17.1]

### Cohen's h Effect Size Pattern
```python
# Source: generate_paper_data.py lines 200-203
import math
def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h effect size for two proportions."""
    return 2 * math.asin(math.sqrt(max(0.0, min(1.0, p1)))) - \
           2 * math.asin(math.sqrt(max(0.0, min(1.0, p2))))
```
[VERIFIED: existing codebase pattern in generate_paper_data.py]

### Per-Kernel Agreement Matrix Pattern
```python
# Four-way classification per D-04
for kernel in common_kernels:
    qwen_pass = qwen_by_kernel[kernel]["pass_rate"] > 0  # or per-direction
    gpt_pass = gpt_by_kernel[kernel]["pass_rate"] > 0
    if qwen_pass and gpt_pass:
        both_pass.append(kernel)
    elif not qwen_pass and not gpt_pass:
        both_fail.append(kernel)
    elif qwen_pass and not gpt_pass:
        qwen_only_pass.append(kernel)
    else:
        gpt_only_pass.append(kernel)
```
[ASSUMED: specific threshold for "pass" needs to be defined -- likely per-(kernel, direction) L0 status, not aggregate rate]

### Reading paper_data.json for Cross-Model Comparison
```python
import json
from pathlib import Path

qwen = json.loads(Path("results/analysis/paper_data.json").read_text())
gpt = json.loads(Path("results/analysis/paper_data_gpt41mini.json").read_text())

# Overall comparison
qwen_overall = qwen["primary_campaign"]["overall"]
gpt_overall = gpt["primary_campaign"]["overall"]

# Per-direction comparison (7 common directions only)
COMMON_DIRS = [
    "cuda-to-omp", "omp-to-cuda",
    "cuda-to-opencl", "opencl-to-cuda",
    "omp-to-opencl", "opencl-to-omp",
    "cuda-to-omp_target",
]
```
[VERIFIED: paper_data.json schema from JSON inspection]

## cross_model_comparison.py Design Specification

### Inputs
1. `results/analysis/paper_data.json` (Qwen primary campaign data)
2. `results/analysis/paper_data_gpt41mini.json` (GPT primary campaign data)
3. Optionally: raw result JSONs from `results/evaluation/{model}/` for per-kernel L0 pairing

### Outputs
`results/analysis/cross_model_comparison.json` with structure:
```json
{
    "generated_at": "ISO timestamp",
    "models": ["together-qwen-3.5-397b-a17b", "azure-gpt-4.1-mini"],
    "common_directions": ["cuda-to-omp", ...],  // 7 directions
    "missing_directions": {"azure-gpt-4.1-mini": ["omp_target-to-cuda"]},
    "overall": {
        "contingency_table": [[qwen_pass, qwen_fail], [gpt_pass, gpt_fail]],
        "chi_squared": {"chi2": X, "p_value": X, "dof": 1},
        "qwen_rate": X, "gpt_rate": X,
        "cohens_h": X, "effect_size": "small|medium|large"
    },
    "per_direction": {
        "cuda-to-omp": {
            "qwen": {"pass": N, "total": N, "rate": X},
            "gpt": {"pass": N, "total": N, "rate": X},
            "cohens_h": X
        },
        ...
    },
    "per_kernel_matrix": {
        "both_pass": ["bfs", ...],
        "both_fail": ["dwt2d", ...],
        "qwen_only_pass": [...],
        "gpt_only_pass": [...]
    }
}
```

### Statistical Methods Required
1. **Chi-squared test:** `scipy.stats.chi2_contingency` on 2x2 table [VERIFIED: available]
2. **Cohen's h:** `2 * arcsin(sqrt(p1)) - 2 * arcsin(sqrt(p2))` [VERIFIED: pattern in codebase]
3. **Per-direction comparison:** Iterate 7 common directions, compute pass rates and Cohen's h per direction
4. **Per-kernel matrix:** Match kernels across models using L0 base results only, classify into 4 categories per D-04

### Design Decision: Per-Kernel Matching Granularity
The per-kernel matrix needs to define what "pass" means per kernel. Options:
- **Per kernel overall:** Kernel passes if ANY direction passes for that model (too loose)
- **Per (kernel, direction) L0:** Each (kernel, direction) pair at L0 is classified independently (most granular, matches PLAN.md intent)

**Recommendation:** Use per-(kernel, direction) L0 pairs for the 7 common directions. This gives the most informative four-way matrix and matches how the paper presents per-kernel data.

## Figure Regeneration Details

### Figures Affected by Dual-Model Data [VERIFIED: code inspection]

| Figure | How It Uses Dual-Model Data | Impact |
|--------|---------------------------|--------|
| F3 (kernel heatmap) | Aggregates ALL records (kernel x direction) -- last-write-wins for status | Minimal -- more data points but same visual structure |
| F4 (failure taxonomy) | Aggregates ALL models by direction | Counts increase; proportions may shift |
| F5 (pass@k) | Uses sample records only (GPT may not have samples) | Only if GPT has `-sN` sample files |
| F6 (cross-suite) | Aggregates ALL models by suite | More data points |
| F7 (augmentation) | Iterates MODEL_COLORS, draws per-model lines | **KEY FIGURE** -- will show GPT line alongside Qwen |
| T2 (model table) | **HARDCODED "pending"** for GPT | **MUST FIX** before T5 |
| C.1 (repair transitions) | Uses attempts[] data from all models | Additional repair data |
| C.2 (repair rate) | Per-direction repair rates | Additional data |
| C.3 (transform frequency) | Augmentation data | May not affect (depends on GPT augmented results) |
| C.4 (selection funnel) | Static survey data -- no model dependency | No change |
| F2 (repo vs kernel) | Static survey data -- no model dependency | No change |

### F5 Sample Data Check [ASSUMED]
GPT pass@k evaluation may not have been run. If `results/evaluation/azure-gpt-4.1-mini/` contains no `-sN` suffix files, F5 will only show Qwen data. This is acceptable -- pass@k is a Qwen-specific analysis in the current paper structure.

### F7 Augmentation Data Check [VERIFIED: direction data]
GPT has cuda-to-omp results (208 files including augmented L1-L4). F7 filters to cuda-to-omp direction specifically. GPT augmentation line WILL appear in F7.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (installed in venv) |
| Config file | None specific to analysis scripts |
| Quick run command | `python3 -m pytest scripts/analysis/test_generate_paper_data.py -x` |
| Full suite command | `python3 -m pytest scripts/analysis/ -x` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| T1 | eval_summary has 2 model keys | smoke | `python3 -c "import json; d=json.load(open('results/evaluation/eval_summary.json')); assert len(d['by_model'])==2"` | N/A (inline) |
| T2 | paper_data_gpt41mini.json exists with pass_rate | smoke | `python3 -c "import json; d=json.load(open('results/analysis/paper_data_gpt41mini.json')); assert 'pass_rate' in d['primary_campaign']['overall']"` | N/A (inline) |
| T3 | error_taxonomy.json has GPT in per_model | smoke | `python3 -c "import json; d=json.load(open('results/analysis/error_taxonomy.json')); assert 'azure-gpt-4.1-mini' in d['per_model']"` | N/A (inline) |
| T4 | cross_model_comparison.json has chi-squared and Cohen's h | smoke | `python3 -c "import json; d=json.load(open('results/analysis/cross_model_comparison.json')); assert 'chi_squared' in d.get('overall',{})"` | N/A (inline) |
| T5 | Figures regenerated with dual-model data | visual | Manual check of f7_augmentation_robustness.pdf | Manual |

### Wave 0 Gaps
- No existing test file for `cross_model_comparison.py` (new script)
- Inline smoke tests sufficient for pipeline verification
- Existing tests: `test_generate_paper_data.py`, `test_build_error_taxonomy.py` (unit tests for those scripts)

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GPT pass@k sample files (-sN) may not exist | Figure Regeneration | F5 shows Qwen only -- acceptable per paper structure |
| A2 | Per-kernel matrix should use per-(kernel, direction) L0 granularity | cross_model_comparison.py Design | Less informative matrix if using kernel-overall aggregation |
| A3 | The ~26.6% GPT pass rate estimate is for primary campaign only (post-exclusion) vs 27.24% for all tasks | Current State Inventory | Minor numerical difference -- paper_data output will be authoritative |

## Open Questions

1. **omp_target-to-cuda GPT data status**
   - What we know: 0 files exist as of research time
   - What's unclear: Whether Le will deliver before April 7 EOD
   - Recommendation: Proceed with 7-direction fallback per D-05-fallback. cross_model_comparison.py should handle both 7 and 8 direction scenarios gracefully.

2. **error_taxonomy_gpt41mini.json separate file**
   - What we know: `build_error_taxonomy.py` cannot produce per-model output files
   - What's unclear: Whether downstream consumers need a separate GPT-only file
   - Recommendation: Use the combined `error_taxonomy.json` (with both models in `per_model`). If a separate file is needed, add a 5-line post-processing step to extract GPT data.

3. **T2 table fix scope**
   - What we know: Code is hardcoded with "pending"
   - What's unclear: Whether this fix belongs in T5 (figure regen) or should be a separate pre-task
   - Recommendation: Fix `generate_t2_model_table()` as part of T5 prep (same file, ~15 lines).

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3 | All scripts | Yes | 3.x (venv) | -- |
| scipy | cross_model_comparison.py | Yes | 1.17.1 | -- |
| numpy | cross_model_comparison.py, figures | Yes | 2.4.3 | -- |
| matplotlib | Figure generation | Yes | 3.10.8 | -- |
| scienceplots | IEEE figure styling | Yes | installed | -- |

No missing dependencies.

## Security Domain

Security enforcement not applicable -- this phase involves data analysis scripts operating on local evaluation result files. No authentication, network access, user input sanitization, or cryptography involved.

## Sources

### Primary (HIGH confidence)
- `scripts/evaluation/analyze_eval.py` -- CLI args, model discovery logic (lines 1-80)
- `scripts/analysis/generate_paper_data.py` -- `--results-dir` interface, output schema (lines 1-60, 1135-1174)
- `scripts/analysis/build_error_taxonomy.py` -- `--project-root` only interface, per_model output (lines 450-475, 999-1030)
- `scripts/generate_paper_figures.py` -- MODEL_COLORS, T2 hardcoded "pending" (lines 84-102, 1565-1631)
- `results/evaluation/eval_summary.json` -- current 2-model state
- `results/analysis/paper_data.json` -- Qwen schema with pass_rate field
- `results/analysis/error_taxonomy.json` -- Qwen-only per_model structure
- Filesystem scan of `results/evaluation/azure-gpt-4.1-mini/` -- 897 files, 7 directions
- `docs/paper/latex/paper.tex` -- 18 `\pending{}` markers, 24 `\tbd{}` table cells

### Secondary (MEDIUM confidence)
- `.planning/phases/16-gpt-data-analysis/PLAN.md` -- task breakdown (T3 command is wrong)
- `~/.claude/plans/hashed-sauteeing-kite.md` lines 114-191 -- original phase specification

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all packages verified installed with versions
- Architecture: HIGH -- all scripts inspected, CLI interfaces verified, schemas documented
- Pitfalls: HIGH -- discovered 3 concrete issues (T3 CLI, T2 hardcoded, field naming) through direct code inspection

**Research date:** 2026-04-07
**Valid until:** 2026-04-08 (deadline-driven, data-specific research)
