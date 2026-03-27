# Verification Strategy Audit & Reverification Analysis

**Session:** S-VERIFY
**Date:** 2026-03-27
**Branch:** `session/s-verify`

## Executive Summary

A systematic audit of ParBench's verification pipeline revealed that **exit_code-only
verification was masking silent correctness failures**. The `verify_run()` function in
`harness/verifier.py` used a "first definitive result wins" strategy — since `exit_code`
was always listed first in spec strategies, `stdout_pattern` was **never evaluated** for
any of the 46 dual-strategy specs.

### Changes Made

1. **Verifier semantics** (`harness/verifier.py`): Changed from disjunction ("first match
   wins") to conjunction ("all must agree"). Every non-SKIP strategy must PASS for overall
   PASS. FAIL on any failure returns immediately.

2. **Strategy ordering** (64 specs): Reordered `stdout_pattern` before `exit_code` in all
   specs. While the new conjunction semantics make ordering irrelevant for correctness,
   stdout_pattern-first gives earlier, more informative failure messages.

3. **Pattern replacement** (51 specs): Replaced generic `(?i)(pass|correct|match|verified)`
   patterns with kernel-specific patterns derived from actual binary stdout output.

4. **New patterns** (16 specs): Added `stdout_pattern` to 16 of 18 previously
   exit_code-only specs. Two specs (`bfs-omp`, `lavamd-omp`) kept exit_code-only because
   they produce no meaningful stdout.

5. **Pipeline fix** (`llm_evaluate.py`): Now stores **full** translated code (not 200-byte
   preview) and `run_stdout_snippet` for ALL results (not just failures).

## Baseline Impact

### Before (58 non-KNOWN_FAIL specs)

- 58/58 PASS (100%) — exit_code-only verification, stdout_pattern never checked

### After (with corrected verification)

- **53/58 TRUE PASS** (91.4%) — 49 Rodinia + 4 XSBench
- **5/58 FALSE PASS** (8.6%) — all Rodinia; these specs exit cleanly but produce wrong output

### FALSE PASS Specs (5)

| Spec | Root Cause | Stdout Evidence |
|------|-----------|-----------------|
| `rodinia-backprop-opencl` | No stdout at all; stderr: "number of input points must be divided by 16" | Empty stdout → pattern fails |
| `rodinia-heartwall-opencl` | Prints usage text instead of computing — wrong run args | "Usage: heartwall <input> <output>" |
| `rodinia-myocyte-omp` | Wrong argument count | "ERROR: 3 is the incorrect number of arguments" |
| `rodinia-myocyte-opencl` | Unknown argument error | Argument parsing failure |
| `rodinia-pathfinder-omp` | Wrong run args format | "Usage: pathfiner width num_of_steps" |

**Corrected baseline: 53/58 TRUE PASS (49/54 Rodinia + 4/4 XSBench)** — these 5 Rodinia specs need run argument fixes
before they can be used in eval batches. The corrected verification now catches them.

## Impact on 169 Existing PASS Eval Results

### Data Retention Gap (CRITICAL)

Retroactive re-verification of the 169 existing PASS eval results is **impossible** due to
a data retention limitation in `llm_evaluate.py`:

1. **`translated_files` was truncated to 200 bytes** (line 1188-1189, pre-fix):
   ```python
   translated_files_preview = {f: extracted_last[f][:200] for f in target_filenames ...}
   ```
   200 bytes of source code cannot compile — all 152 reverification attempts got BUILD_FAIL.

2. **`run_stdout_snippet` was null for all PASS results** — the pipeline only stored stdout
   for failures, not successes.

### Reverification Attempt Results

| Category | Count | Explanation |
|----------|------:|-------------|
| BUILD_FAIL | 152 | Truncated translated_files cannot compile |
| RUN_FAIL | 15 | Binary from previous build still present; ran with wrong input |
| FALSE_PASS | 2 | Groq results that happened to run (stale binary) |
| TRUE_PASS | 0 | No result could be properly re-verified |

**Conclusion:** The 169 existing PASS results cannot be retroactively validated with the
corrected stdout_pattern strategies. The `overall_status: PASS` in these result JSONs means
"compiled, ran, and exited with code 0" — it does NOT guarantee correct output.

### What CAN Be Inferred

Although we cannot re-verify individual results, we can assess **risk exposure**:

- **5 target specs with FALSE_PASS baselines** affect eval results targeting those specs:
  - `backprop-opencl`, `heartwall-opencl`, `myocyte-omp`, `myocyte-opencl`, `pathfinder-omp`
  - Any PASS eval result targeting these specs is suspect (the reference binary itself
    doesn't produce correct output due to wrong run args)

- **53 target specs with TRUE PASS baselines** have valid verification strategies. PASS
  eval results targeting these specs were verified by exit_code only, but the baseline
  reference binary DOES produce the expected stdout_pattern output. The LLM translations
  may or may not match.

## Pipeline Fixes Applied

### 1. `harness/verifier.py` — Conjunction Semantics

```python
# Before: returned on first PASS or FAIL (disjunction)
# After: ALL non-SKIP strategies must PASS (conjunction)
for strategy in strategies:
    result = check_strategy(strategy, run_result)
    if result.status == Status.FAIL:
        return result  # Fail fast
    if result.status == Status.PASS:
        passed_strategies.append(stype)
    # SKIP: ignore
if passed_strategies:
    return PASS  # All checked strategies passed
```

### 2. `llm_evaluate.py` — Full Data Retention

- `translated_files`: Now stores full translated code (was truncated to 200 bytes)
- `run_stdout_snippet`: Now stored for ALL results, not just failures
- Future eval runs will support retroactive re-verification

### 3. Spec Strategy Patterns

All 64 Rodinia+XSBench specs now have kernel-specific stdout_pattern strategies derived
from actual binary output. Pattern strength classification:

| Strength | Count | Example | Description |
|----------|------:|---------|-------------|
| Strong (self-checking) | 4 | `"PASS!"` (huffman), `"Verification checksum: \\d+ \\(Valid\\)"` (xsbench) | Program prints pass/fail |
| Strong (completion) | 28 | `"Training done"` (backprop), `"Computation Done"` (srad) | Computation finished marker |
| Medium (output) | 18 | `"Accuracy:"` (hotspot3d), `"XE:"` (particlefilter) | Computation-specific output |
| Weak (startup) | 10 | `"Use GPU device"` (hotspot-opencl), `"PARSEC Benchmark Suite"` (streamcluster) | Program started but no completion marker |
| None (exit_code only) | 2 | bfs-omp, lavamd-omp | No meaningful stdout |

## Recommendations

### Immediate (before next eval batch)

1. **Fix the 5 FALSE_PASS specs' run arguments** — these need source argc analysis per
   the Run Argument Verification Protocol in `spec-conventions.md`
2. **Re-run eval batches** with corrected verification to get TRUE pass rates
3. **All future results** will have full translated code and stdout stored

### For SC26 Paper

1. **Report corrected baseline:** 53/58 TRUE PASS (not 58/58)
2. **Acknowledge verification limitation** in existing L0 results: "PASS indicates
   successful compilation and clean exit, but stdout correctness was not verified for the
   169 L0 results due to a data retention limitation since corrected"
3. **New eval batches** with corrected verification will have validated stdout output
4. **The 5 FALSE_PASS specs** should be excluded from reported results or fixed first

### Long-term

1. Implement `numeric_comparison` strategy for floating-point outputs
2. Consider storing full LLM response (not just extracted files) for reproducibility
3. Add reference stdout capture to baseline population script
