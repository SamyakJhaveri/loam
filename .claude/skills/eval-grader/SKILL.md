---
name: eval-grader
description: "LLM eval result grading and classification workflow for ParBench. Use when classifying eval results into pass/fail categories, when diagnosing patterns in batch results (e.g., which kernels fail most), when computing pass rates excluding KNOWN_FAIL specs, or when preparing result tables for the NeurIPS paper. Handles the full grading pipeline: load result JSON → apply KNOWN_FAIL exclusion → classify by failure mode → compute statistics → generate summary tables."
---

# Eval Result Grader

Structured workflow for grading and classifying LLM evaluation results from ParBench
batch runs. Produces defensible statistics for paper reporting.

**Trigger:** `/eval-grader` or when classifying/summarizing eval batch results.

## When to use

- After `/post-eval` completes and you need to classify results
- Computing pass rates for paper tables
- Diagnosing systematic failure patterns across models or directions
- Comparing two models' results on the same spec set

## Arguments

- `<result-path>` — path to a result JSON or directory of results
- `--model <name>` — filter to specific model
- `--direction <src-to-tgt>` — filter to translation direction (e.g., `cuda-to-omp`)

## Grading Pipeline

### Step 1: Load Results

Read result JSON(s) from `results/evaluation/`. Each result has:
```json
{
  "spec_id": "rodinia-srad-cuda",
  "target_api": "omp",
  "overall_status": "PASS" | "BUILD_FAIL" | "RUN_FAIL" | "VERIFY_FAIL",
  "model": "together-qwen-3.5-397b-a17b",
  "augmentation_level": "L0" | "L1" | "L2" | "L3" | "L4"
}
```

### Step 2: Apply Exclusions

**KNOWN_FAIL exclusion (CRITICAL):**
Exclude any result where EITHER the source spec OR the target spec is in the KNOWN_FAIL list.
The 8 KNOWN_FAIL specs are in `known-issues.md`. The denominator formula:

```
N_valid = N_total - N_target_KF - N_source_KF + N_both_KF
```

**Phantom spec exclusion:** 5 deleted phantom specs (gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl) — exclude any results referencing these.

### Step 3: Classify Failure Modes

For non-PASS results, classify into categories:

| Category | Indicator | Typical cause |
|----------|-----------|---------------|
| BUILD_FAIL:syntax | Compiler error on generated code | LLM produced invalid syntax |
| BUILD_FAIL:missing_include | Missing header/library | LLM forgot API-specific includes |
| BUILD_FAIL:type_error | Type mismatch | Incomplete API type translation |
| RUN_FAIL:segfault | SIGSEGV/SIGBUS | Null pointer, buffer overrun |
| RUN_FAIL:timeout | Exceeded time limit | Infinite loop or deadlock |
| VERIFY_FAIL:wrong_output | Output doesn't match oracle | Semantic translation error |
| VERIFY_FAIL:empty_output | No output produced | Early exit or crash without signal |

### Step 4: Compute Statistics

Report these metrics (per model × direction × augmentation level):

```
Pass rate:       PASS / N_valid × 100
Build rate:      (PASS + RUN_FAIL + VERIFY_FAIL) / N_valid × 100
Failure breakdown: BUILD_FAIL: X%, RUN_FAIL: Y%, VERIFY_FAIL: Z%
```

For the paper, report pass@1 (single sample) and pass@1-of-3 (any of 3 samples passes).

### Step 5: Generate Summary Table

Output a markdown table suitable for paper inclusion:

```markdown
| Model | Direction | L0 | L1 | L2 | L3 | L4 |
|-------|-----------|----|----|----|----|-----|
| qwen-3.5 | cuda→omp | X% | Y% | ... | ... | ... |
```

## Verification Gates

Before reporting any statistic:
1. Confirm KNOWN_FAIL exclusion was applied
2. Confirm denominator matches expected spec count (88 non-KNOWN_FAIL)
3. Cross-check at least 2 individual results manually
4. Flag any spec that PASS at L0 but FAIL at higher augmentation levels (anomaly)

## Integration

- Uses result JSONs from `results/evaluation/` (immutable — never modify)
- Feeds into `/cite-check` for paper claim verification
- Feeds into `/interpret-results` for hypothesis-first analysis
