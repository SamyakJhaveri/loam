# Session 2b: Analysis Script Fixes & Statistical Corrections

**Owner:** Samyak
**Date:** 2026-03-31
**Prerequisite:** Session 2 completed (Qwen 3.5 397B analysis pipeline run)
**Objective:** Fix 5 bugs discovered during Session 2 that produce incorrect statistical results

---

## Copy-Pasteable Claude Code Prompt

```
You are executing Session 2b: Analysis Script Fixes & Statistical Corrections.

CONTEXT: Session 2 ran 5 analysis scripts on Qwen 3.5 397B evaluation data (1,018 result
files, 906 unique tasks after EXCLUDED_SPECS filtering, 27.7% overall pass rate). It
discovered 5 bugs in the analysis scripts that produce incorrect numbers. This session
fixes all 5.

READ THIS PLAN FIRST:
  docs/session_plans/session_2b_script_fixes.md

WORKFLOW:
1. Read the plan completely
2. Use /brainstorming for Issue 2 (Cochran-Armitage fix strategy)
3. Use /write-plan to create an implementation plan before touching code
4. Use /test-driven-development for ALL code changes (Issues 1-4)
5. After implementation, spawn a critic agent for code review
6. Run /validate before committing
7. End with /finishing-a-development-branch

FILES IN SCOPE (read these first):
  scripts/analysis/statistical_analysis.py    (Issues 1, 2)
  scripts/analysis/token_analysis.py          (Issue 3)
  scripts/analysis/build_error_taxonomy.py    (Issue 4)
  scripts/evaluation/generate_paper_figures.py (Issue 5 — defer or fix)
  scripts/evaluation/analyze_eval.py          (reference: EXCLUDED_SPECS at line 47)

DO NOT TOUCH: results/evaluation/*.json, c_augmentation/, harness/, specs/

ACCEPTANCE CRITERIA (all must pass before commit):
  [ ] pass@k uses stochastic-only data (temp>0); L0 n=3 not n=4
  [ ] Cochran-Armitage uses balanced groups (temp=0.0 only, or matched tasks)
  [ ] Cochran-Armitage trend direction matches F7 figure visual (decreasing, not increasing)
  [ ] token_analysis pass_rate matches eval_summary (0.277, not 0.247)
  [ ] VERIFY_FAIL has sub-categories in error_taxonomy.json
  [ ] All new code has tests (TDD: failing test written first)
  [ ] /validate passes
  [ ] All 5 analysis scripts re-run successfully after fixes
  [ ] Figures F5-F8 re-checked (should be unaffected by script fixes)
```

---

## Why This Session Exists

Session 2 successfully ran the full analysis pipeline on Qwen 3.5 397B data, but discovered
5 bugs in the analysis scripts. Three produce **incorrect statistical results** that would
be wrong if published in the SC26 paper (pass@k mixes deterministic and stochastic data,
Cochran-Armitage trend is confounded, token analysis has a wrong denominator). One leaves
a gap in the failure taxonomy (VERIFY_FAIL unclassified). One produces a stale figure (F9
XSBench uses legacy pilot data).

---

## Skill Usage Instructions

The new session MUST use these skills in order:

1. **`/brainstorming`** (superpowers:brainstorming) — For Issue 2 only. There are multiple
   valid approaches to fixing the Cochran-Armitage confound (filter to temp=0.0 only vs.
   filter to balanced subset). Brainstorm before choosing.

2. **`/write-plan`** (superpowers:writing-plans) — Create an implementation plan covering
   all 5 issues before touching any code. Get user approval.

3. **`/test-driven-development`** (superpowers:test-driven-development) — For Issues 1-4,
   write a failing test FIRST, then implement the fix, then confirm the test passes.

4. **Critic agent** (superpowers:requesting-code-review) — After all 4 code changes are
   implemented, spawn a critic agent to review all changes for correctness.

5. **`/validate`** — Full 4-wave validation before committing.

6. **`/finishing-a-development-branch`** (superpowers:finishing-a-development-branch) — To
   decide merge/PR/cleanup strategy.

---

## Issue 1 (HIGH): pass@k mixes deterministic and stochastic data

### Root Cause

`compute_pass_at_k_table()` in `statistical_analysis.py` (line 619) groups results by
`(kernel, model, direction, augment_level)` but does not distinguish between:
- **Deterministic runs** (temperature=0.0, L0-L4, max_retries=3) — 1 result per task
- **Stochastic samples** (temperature=0.7, sample_id=s0/s1/s2, max_retries=1) — 3 results per task

For the 110 overlapping Rodinia cuda-to-omp tasks, this yields n=4 (1 deterministic + 3
stochastic) instead of the correct n=3 (stochastic only).

### Evidence

32/110 Rodinia tasks disagree on `overall_status` between L0 deterministic (temp=0.0) and
s0 stochastic (temp=0.7). This means deterministic and stochastic runs are NOT equivalent
samples — mixing them violates the i.i.d. assumption underlying pass@k.

### Files to Modify

- `scripts/analysis/statistical_analysis.py` — function `compute_pass_at_k_table` (line 619)
- `scripts/analysis/statistical_analysis.py` — main function `has_samples` guard (line 1063)

### Proposed Fix

**Fix A — Filter stochastic-only in `compute_pass_at_k_table`:**

```python
def compute_pass_at_k_table(
    records: list[dict], k_values: list[int] | None = None
) -> dict:
    """Compute pass@k for each (kernel, model, direction, level) group.
    
    Uses ONLY stochastic samples (temperature > 0) to avoid mixing
    deterministic retries with stochastic samples.
    """
    if k_values is None:
        k_values = [1, 5, 10]

    # Filter to stochastic samples only (temperature > 0)
    sample_records = [r for r in records if (r.get("temperature") or 0) > 0]

    groups: dict[tuple, dict[str, int]] = defaultdict(lambda: {"n": 0, "c": 0})
    for r in sample_records:
        # ... rest unchanged ...
```

**Fix B — Tighten `has_samples` guard at line 1063:**

The current guard `any(r.get("sample_id") is not None for r in records)` triggers True for
ALL records because deterministic L0 files also have `sample_id: 0` (integer zero is not
None). Fix:

```python
# OLD (line 1063):
has_samples = any(r.get("sample_id") is not None for r in records)

# NEW — require temperature > 0 to identify true stochastic samples:
has_samples = any((r.get("temperature") or 0) > 0 for r in records)
```

### TDD Approach

1. Write a test with mixed records: 1 deterministic (temp=0.0, sample_id=0) + 3 stochastic
   (temp=0.7, sample_id=s0/s1/s2) for the same task
2. Assert that `compute_pass_at_k_table` returns n=3 (not n=4) for that group
3. Run test — expect FAIL with current code (n=4)
4. Apply fix
5. Run test — expect PASS (n=3)

### Verification

After fix, re-run:
```bash
python3 scripts/analysis/statistical_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --output results/analysis/statistical_analysis.json -v
```

Check the output JSON's `pass_at_k` section. Expected stochastic-only numbers (156 tasks,
468 samples across all directions):
- **pass@1 = 17.31%**
- **pass@2 = 22.01%**
- **pass@3 = 24.36%**

### Corrected pass@k by Direction (for verification)

These are the correct stochastic-only (n=3) numbers from Session 2 manual computation:

| Direction | Tasks | Samples | pass@1 | pass@2 | pass@3 |
|-----------|-------|---------|--------|--------|--------|
| cuda-to-omp | 110 | 330 | 15.71% | 20.38% | 22.73% |
| cuda-to-opencl | 13 | 39 | 28.21% | 35.90% | 38.46% |
| omp-to-cuda | 13 | 39 | 17.95% | 23.08% | 25.64% |
| omp-to-opencl | 7 | 21 | 9.52% | 19.05% | 28.57% |
| opencl-to-cuda | 13 | 39 | 17.95% | 25.64% | 30.77% |
| **Overall** | **156** | **468** | **17.31%** | **22.01%** | **24.36%** |

---

## Issue 2 (HIGH): Cochran-Armitage augmentation trend is confounded

### Root Cause

`compute_augmentation_trends()` in `statistical_analysis.py` (line 338) filters to
`direction == "cuda-to-omp"` but does NOT filter by temperature. This means:

- **L0** has 522 tasks: 110 deterministic (temp=0.0) + 412 stochastic samples (temp=0.7)
- **L1-L4** have 96 tasks each: deterministic only (temp=0.0)

The stochastic samples at L0 have much lower pass rates (~28%) compared to base runs (~61%
for the original 3-model pilot data). This dilutes L0 artificially, making it look like pass
rates INCREASE from L0 to L4.

### Evidence

The Cochran-Armitage test reports: z=2.606, p=0.009, direction="increasing" — but this is
an **artifact** of the unbalanced groups, not a real augmentation trend.

The controlled comparison (same 110 Rodinia kernels at each level, deterministic only) shows
the OPPOSITE — a DECREASE:
- L0: 37/110 = 33.6%
- L1: 33/110 = 30.0%
- L2: 35/110 = 31.8%
- L3: 36/110 = 32.7%
- L4: 29/110 = 26.4%

This matches the F7 figure visual (slightly decreasing augmentation curve).

### Files to Modify

- `scripts/analysis/statistical_analysis.py` — function `compute_augmentation_trends` (line 338)

### Decision Required: Fix Strategy

**USE `/brainstorming` BEFORE IMPLEMENTING.** There are multiple valid approaches:

**Option A: Filter to temperature=0.0 only.** Simple, ensures all levels use the same
experimental condition. Downside: discards stochastic data entirely for trend analysis.

**Option B: Filter to balanced subset (matched tasks at each level).** More statistically
rigorous — ensures the SAME set of tasks appears at every level. Implementation: find
the intersection of tasks across L0-L4, then restrict to that set.

**Option C: Run two separate analyses.** Report deterministic-only trend (Option A) as the
primary result, and note the stochastic confound as a limitation.

The brainstorming session should evaluate these options and recommend one.

### TDD Approach

1. Create test records with the confounding structure: L0 has extra stochastic records
   with lower pass rate, L1-L4 have deterministic only
2. Assert that the current function reports "increasing" trend (expected: PASS — confirms bug)
3. Apply fix (whichever option chosen)
4. Assert that the fixed function reports "decreasing" or "no_significant_trend"
5. Assert that L0 sample count equals L1-L4 sample count (balanced groups)

### Verification

After fix, check the `augmentation_trends` section in the output JSON:
- `overall.direction` should NOT be "increasing"
- `overall.total_counts` should be balanced (same value at each level)
- If significant, `overall.direction` should be "decreasing" (matching F7)

---

## Issue 3 (MEDIUM): token_analysis.py wrong pass rate denominator

### Root Cause

`token_analysis.py` loads ALL result files from `results/evaluation/{model}/` directories
without applying EXCLUDED_SPECS filtering. The pass count (251) is correct, but the total
(1018) includes results for excluded specs. The canonical denominator is 906 (after filtering).

### Evidence

- `token_analysis.py` reports: `pass_rate: 0.2466` (251/1018)
- `eval_summary.json` reports: `pass_rate: 0.277` (251/906)
- The correct number is **0.277** (251/906)

### Files to Modify

- `scripts/analysis/token_analysis.py` — function `load_all_results` (line 45) or pass rate
  computation (lines 188-189)

### Reference: EXCLUDED_SPECS list

From `scripts/evaluation/analyze_eval.py` lines 47-54:
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

### Proposed Fix

**Option A (preferred): Copy EXCLUDED_SPECS locally and apply as filter.**

The import `from scripts.evaluation.analyze_eval import EXCLUDED_SPECS` will NOT work
because `scripts/__init__.py` does not exist — Python cannot resolve the package path.
Instead, copy the frozenset directly into `token_analysis.py` with a canonical source comment:

```python
# Canonical source: scripts/evaluation/analyze_eval.py line 47
# Keep in sync — if EXCLUDED_SPECS changes there, update here too.
EXCLUDED_SPECS: frozenset[str] = frozenset({
    "rodinia-kmeans-cuda",
    "rodinia-mummergpu-cuda",
    "rodinia-mummergpu-omp",
    "rodinia-hybridsort-cuda",
    "rodinia-nn-opencl",
    "rodinia-kmeans-opencl",
})
```

Then add filtering in `load_all_results()`, after loading each result JSON:
```python
if data.get("source_spec") in EXCLUDED_SPECS or data.get("target_spec") in EXCLUDED_SPECS:
    continue
```

**Option B: Remove pass_rate from token_analysis.json entirely** and let consumers use
`eval_summary.json` for canonical rates. Less preferred — the field is used in the markdown
report generated by the same script.

> **Note:** If you want to try the import path anyway (e.g., via `sys.path` manipulation),
> it is possible but fragile. The local-copy approach is more robust and matches the pattern
> used by other standalone scripts in this project.

### TDD Approach

1. Write a test that creates mock results including an excluded spec
2. Assert that `load_all_results` returns only non-excluded results
3. Assert that pass_rate computation uses the filtered total
4. Run test — expect FAIL (current code returns all results)
5. Apply fix, confirm PASS

### Verification

After fix, re-run:
```bash
python3 scripts/analysis/token_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --output results/analysis/token_analysis.json
```

Check output: `pass_rate` should be approximately **0.277** (251/906), not 0.2466 (251/1018).

---

## Issue 4 (MEDIUM): VERIFY_FAIL unclassified in error taxonomy

### Root Cause

`build_error_taxonomy.py` has classifiers for BUILD_FAIL (line 325, 11 sub-categories),
RUN_FAIL (line 357, 7 sub-categories), and EXTRACTION_FAIL (line 380, 2 sub-categories),
but NO classifier for VERIFY_FAIL. In the `build_taxonomy()` function (line 415), the
dispatch chain at lines 465-552 handles BUILD_FAIL, RUN_FAIL, EXTRACTION_FAIL, and ERROR,
but VERIFY_FAIL results fall through to line 554 with `primary_category: None`.

The taxonomy data structure (line 417) also lacks a `verify_fail_categories` key.

### Evidence

94 VERIFY_FAIL results exist in the Qwen data. They appear in the output JSON under
`classified_results` with `primary_category: null` and `overall_status: "VERIFY_FAIL"`.
The `status_counts` correctly shows the count, but there's no breakdown.

### Files to Modify

- `scripts/analysis/build_error_taxonomy.py` — add `classify_verify_fail()` function and
  integrate into `build_taxonomy()` dispatch

### Proposed Fix

**Step 0 (CRITICAL): Discover actual field values in VERIFY_FAIL results BEFORE writing the classifier.**

Do NOT assume what `verify_status` values exist — inspect the actual data first:

```bash
grep -l 'VERIFY_FAIL' results/evaluation/together-qwen-3.5-397b-a17b/*.json \
  | head -10 \
  | xargs -I{} python3 -c "
import json
d = json.loads(open('{}').read())
print(d.get('verify_status'), '|', (d.get('run_stdout_snippet') or '')[:80])
"
```

Also check which fields are reliably populated:
```bash
grep -l 'VERIFY_FAIL' results/evaluation/together-qwen-3.5-397b-a17b/*.json \
  | head -5 \
  | xargs -I{} python3 -c "
import json
d = json.loads(open('{}').read())
print('verify_status:', repr(d.get('verify_status')))
print('run_exit_code:', repr(d.get('run_exit_code')))
print('run_stdout_snippet:', repr((d.get('run_stdout_snippet') or '')[:60]))
print('---')
"
```

Use the discovered values to define sub-categories. The categories below are a **starting
point** based on the expected schema — adjust them based on what the data actually contains.

**Step 1: Define VERIFY_FAIL sub-categories.**

```python
VERIFY_FAIL_CATEGORIES = [
    ("wrong_numerical_output", "stdout doesn't match expected pattern",
     lambda stdout, stderr, exit_code, verify_status:
         stdout and verify_status == "stdout_pattern_mismatch"),
    ("missing_output", "empty or no stdout produced",
     lambda stdout, stderr, exit_code, verify_status:
         not stdout or not stdout.strip()),
    ("exit_code_mismatch", "stdout matches but exit code wrong",
     lambda stdout, stderr, exit_code, verify_status:
         verify_status == "exit_code_mismatch"),
    ("partial_output", "stdout present but incomplete",
     lambda stdout, stderr, exit_code, verify_status:
         stdout and len(stdout.strip()) < 20),  # heuristic threshold
    ("other_verify", "unclassifiable verification failure",
     lambda stdout, stderr, exit_code, verify_status: True),  # catch-all
]
```

**Step 2: Write `classify_verify_fail(data)` function** (follow the pattern of
`classify_run_fail` at line 357).

```python
def classify_verify_fail(data):
    """Classify a VERIFY_FAIL result. Returns (primary, [secondaries])."""
    stdout = data.get("run_stdout_snippet") or ""
    stderr = data.get("run_stderr_snippet") or ""
    exit_code = data.get("run_exit_code")
    verify_status = data.get("verify_status") or ""

    primary = None
    secondaries = []

    for cat_name, _desc, check_fn in VERIFY_FAIL_CATEGORIES:
        if cat_name == "other_verify":
            if primary is None:
                primary = cat_name
            continue
        if check_fn(stdout, stderr, exit_code, verify_status):
            if primary is None:
                primary = cat_name
            else:
                secondaries.append(cat_name)

    return primary, secondaries
```

**Step 3: Add to taxonomy data structure** (line 417 area):
```python
"verify_fail_categories": defaultdict(lambda: {"count": 0, "examples": [], ...}),
```

**Step 4: Add dispatch in `build_taxonomy()`** — insert a new `elif status == "VERIFY_FAIL":`
block between the EXTRACTION_FAIL block (line 516) and the ERROR block (line 539).

**Step 5: Add to `per_kernel`, `per_model`, `per_direction` tracking.**

**Step 6: Add console summary section** in `main()` (after line 934, mirror the
BUILD_FAIL/RUN_FAIL summary pattern).

**Step 7: Add to `serialize_taxonomy()` and `generate_markdown()`.**

### TDD Approach

1. Write a test with mock VERIFY_FAIL results:
   - One with stdout that doesn't match pattern (wrong_numerical_output)
   - One with empty stdout (missing_output)
   - One with exit code mismatch
2. Assert `classify_verify_fail` returns correct primary categories
3. Assert `build_taxonomy` includes `verify_fail_categories` in output
4. Run test — expect FAIL (function doesn't exist yet)
5. Implement, confirm PASS

### Verification

After fix, re-run:
```bash
python3 scripts/analysis/build_error_taxonomy.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

Check `results/analysis/error_taxonomy.json`:
- `verify_fail_categories` key should exist
- Sum of all verify_fail sub-category counts should equal 94
- The console summary should show a VERIFY_FAIL section

Note: the script exits with code 1 for a validation warning (delta count check) — this is
expected behavior, not an error.

---

## Issue 5 (LOW): F9 XSBench figure hardcoded with legacy pilot data

### Root Cause

`scripts/evaluation/generate_paper_figures.py` lines 200-220 contain hardcoded XSBench
results for 3 legacy pilot models (claude-sonnet, gemini-flash-lite, groq-llama). The
`XSBENCH_L0` dict, `_XS_MODELS`, and `_XS_MODEL_DISPLAY` need to be updated with Qwen
data or made dynamic.

### Recommendation: DEFER

This is low priority because:
1. Qwen only has 3 XSBench directions (cuda-to-omp, omp-to-cuda, omp-to-opencl) — not the
   full 12-direction matrix the pilot had
2. Gemini 2.5 Flash data is expected April 3-5, which will require another update
3. F9 is not blocking any paper section

**If the session has bandwidth after Issues 1-4, fix it.** Otherwise, create a task for
Session 3 to replace hardcoded data with dynamic loading from result files.

### Files to Modify (if not deferred)

- `scripts/evaluation/generate_paper_figures.py` — lines 200-220 (`XSBENCH_L0`, `_XS_MODELS`,
  `_XS_MODEL_DISPLAY`) and function `generate_f9_xsbench` (line 1273)

### Proposed Fix (if not deferred)

Replace the hardcoded dict with dynamic loading:
```python
def _load_xsbench_results(project_root: Path) -> dict:
    """Load XSBench results from result JSONs for all available models."""
    # Glob for xsbench-* result files in all model directories
    # Build XSBENCH_L0 dict dynamically from file data
    ...
```

---

## Agent Team Design

For the new session, use `/agent-team` with this structure:

### Pre-Step: Brainstorming (not a spawned teammate)

Before spawning the agent team, the lead session invokes `/brainstorming` directly to
decide the Issue 2 fix strategy (Cochran-Armitage). This is a skill invocation in the main
session, not a spawned teammate — it completes before the team is created.

### Spawned Teammates (3 fixers + 1 critic)

| Teammate | Role | Files | Skills |
|----------|------|-------|--------|
| **stat-fixer** | Fix Issues 1 + 2 | `statistical_analysis.py` | `/test-driven-development` |
| **taxonomy-fixer** | Fix Issue 4 | `build_error_taxonomy.py` | `/test-driven-development` |
| **token-fixer** | Fix Issue 3 | `token_analysis.py` | `/test-driven-development` |
| **critic** | Review ALL changes | All modified files | `/requesting-code-review` |

### Execution Order

1. **`/brainstorming`** runs in lead session (Issue 2 strategy decision)
2. **stat-fixer**, **taxonomy-fixer**, **token-fixer** run in parallel (independent files,
   except stat-fixer has 2 issues in the same file — do Issue 1 first, then Issue 2)
3. **critic** runs last after all fixes are in

### Team Spawn Command

```
Create an agent team with 3 teammates (all Opus):
- stat-fixer: Fix Issues 1 and 2 in scripts/analysis/statistical_analysis.py using TDD.
  Issue 1: Filter compute_pass_at_k_table to stochastic-only (temp>0). Fix has_samples
  guard at line 1063. Issue 2: Fix compute_augmentation_trends to use balanced groups
  (use the strategy decided by brainstorming — already completed before team spawn).
- taxonomy-fixer: Fix Issue 4 in scripts/analysis/build_error_taxonomy.py using TDD.
  Add classify_verify_fail function and integrate into build_taxonomy dispatch.
  IMPORTANT: Run Step 0 data discovery FIRST (grep actual VERIFY_FAIL JSONs).
- token-fixer: Fix Issue 3 in scripts/analysis/token_analysis.py using TDD. Apply
  EXCLUDED_SPECS filtering (copy frozenset locally, same list as analyze_eval.py line 47).
Require plan approval from all before implementation.

After all 3 fixers complete, spawn a critic teammate to review all changes.
```

---

## Acceptance Criteria

- [ ] pass@k uses stochastic-only data (temp>0); L0 groups have n=3, not n=4
- [ ] `has_samples` guard uses `temperature > 0` check, not `sample_id is not None`
- [ ] Cochran-Armitage uses balanced groups (same task count at each level)
- [ ] Cochran-Armitage trend direction matches F7 figure visual (decreasing or flat, NOT increasing)
- [ ] token_analysis `pass_rate` matches eval_summary (~0.277, not ~0.247)
- [ ] VERIFY_FAIL has sub-categories in `error_taxonomy.json` with counts summing to 94
- [ ] All new code has tests (TDD: failing test written before implementation)
- [ ] `/validate` passes
- [ ] All 5 analysis scripts re-run successfully after fixes:
  ```bash
  python3 scripts/analysis/statistical_analysis.py --project-root . --output results/analysis/statistical_analysis.json -v
  python3 scripts/analysis/token_analysis.py --project-root . --output results/analysis/token_analysis.json
  python3 scripts/analysis/build_error_taxonomy.py --project-root .
  python3 scripts/evaluation/analyze_eval.py --project-root . --output-dir results/evaluation
  python3 scripts/evaluation/generate_paper_figures.py --project-root . --output-dir results/analysis/figures
  ```
- [ ] Figures F5-F8 visually unchanged (script fixes don't affect figure data pipelines)
- [ ] Issue 5 (F9 XSBench) either fixed or explicitly deferred with tracking task created

---

## Key Files Reference Table

| File | Purpose | Lines of Interest | Action |
|------|---------|-------------------|--------|
| `scripts/analysis/statistical_analysis.py` | Statistical tests, pass@k, trends | 619-652 (`compute_pass_at_k_table`), 338-396 (`compute_augmentation_trends`), 1063 (`has_samples` guard) | MODIFY (Issues 1, 2) |
| `scripts/analysis/token_analysis.py` | Token usage + cost analysis | 45-60 (`load_all_results`), 188-189 (pass_rate calc) | MODIFY (Issue 3) |
| `scripts/analysis/build_error_taxonomy.py` | Failure classification | 325 (`classify_build_fail`), 357 (`classify_run_fail`), 380 (`classify_extraction_fail`), 415-556 (`build_taxonomy` dispatch), 875 (`main`), 559 (`serialize_taxonomy`) | MODIFY (Issue 4) |
| `scripts/evaluation/generate_paper_figures.py` | Paper figure generation | 200-220 (`XSBENCH_L0` hardcoded data), 1273 (`generate_f9_xsbench`) | MODIFY or DEFER (Issue 5) |
| `scripts/evaluation/analyze_eval.py` | Eval summary + EXCLUDED_SPECS | 47-54 (`EXCLUDED_SPECS` definition) | READ ONLY (reference) |
| `results/analysis/statistical_analysis.json` | Output of statistical_analysis.py | pass_at_k section, augmentation_trends section | VERIFY after re-run |
| `results/analysis/token_analysis.json` | Output of token_analysis.py | pass_rate field | VERIFY after re-run |
| `results/analysis/error_taxonomy.json` | Output of build_error_taxonomy.py | verify_fail_categories section | VERIFY after re-run |

---

## Troubleshooting Guide

### "Grep EACCES error"
The Grep tool may fail with EACCES. Use bash grep instead:
```bash
grep -n "pattern" /path/to/file
```

### Scripts that don't support `-v` flag
Check `--help` first before passing `-v`. Not all analysis scripts accept verbose flags.
`statistical_analysis.py` supports `-v`. `token_analysis.py` does NOT — check its argparser.

### `build_error_taxonomy.py` exits code 1
This is the validation warning (delta count check), not a crash. Check the console output
for the actual classification results. The JSON and markdown outputs should still be written.

### Import errors when running scripts
Always activate the venv first:
```bash
source env_parbench/bin/activate
```
Note: `from scripts.evaluation.analyze_eval import EXCLUDED_SPECS` will fail because
`scripts/__init__.py` does not exist. The Issue 3 fix uses a local copy of the frozenset
with a canonical source comment — this is the recommended approach (see Issue 3 Proposed Fix).

### Test file location
Create test files adjacent to the scripts being tested:
- `scripts/analysis/test_statistical_analysis.py`
- `scripts/analysis/test_token_analysis.py`
- `scripts/analysis/test_build_error_taxonomy.py`

Or create a unified test file: `scripts/analysis/test_analysis_fixes.py`.
Use `python3 -m pytest <test_file> -v` to run.

### pass@k numbers don't match expected values
The expected values above are computed from 156 tasks with 468 stochastic samples. If your
numbers differ slightly, check:
1. Are EXCLUDED_SPECS being applied upstream? (They should be — check `analyze_eval.py`)
2. Is the temperature field actually populated in result JSONs? Grep for it:
   ```bash
   grep -c '"temperature"' results/evaluation/together-qwen-3.5-397b-a17b/*.json | tail -5
   ```
3. If temperature is missing from some files, you may need to infer stochastic status from
   the filename pattern (e.g., files containing `-s0`, `-s1`, `-s2` in the stem).

---

## Commit Message Template

```
Fix 4 analysis script bugs: pass@k, Cochran-Armitage, token rate, VERIFY_FAIL taxonomy

- Filter pass@k to stochastic-only samples (temp>0), fix has_samples guard
- Fix Cochran-Armitage trend: balanced groups at each augmentation level
- Apply EXCLUDED_SPECS filter in token_analysis.py (0.277 not 0.247)
- Add VERIFY_FAIL sub-classification to build_error_taxonomy.py
- [If done: Update F9 XSBench figure with dynamic data loading]

All fixes verified with TDD (failing tests first) and /validate.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```
