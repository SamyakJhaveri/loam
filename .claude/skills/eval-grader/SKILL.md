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

For non-PASS results, classify into fine-grained categories.

**BUILD_FAIL taxonomy (from Qwen 3.5 canonical audit, 2026-04-24):**

| Category | Subcategory | Typical cause |
|----------|-------------|---------------|
| Model translation errors | cuda_qualifier_error | `__global__`/`__device__` used incorrectly |
| | cuda_launch_syntax | `<<<>>>` kernel launch syntax errors |
| | not_in_scope / identifier_undefined | Variables/functions not declared |
| | syntax_error | General syntax (`expected a ")"`, etc.) |
| | implicit_declaration | C implicit function declarations |
| | type_conversion / unknown_type | Type system errors |
| OMP-specific errors | omp_invalid_pragma_syntax | Invalid OpenMP pragma (nvc++ strict) |
| | omp_nesting_violation | Illegal nesting of OMP constructs |
| Linker errors | linker_undefined_ref | Undefined references at link time |
| Header/file confusion | header_confusion | Model `#include`d source headers instead of inlining |
| | missing_generated_file | Model referenced files it should have produced |
| | wrong_lang_header | C++ headers in `.c` files |

**Header confusion is a prompt design artifact, not purely model error.** The prompt
shows header content but instructs inlining. Models that `#include` instead get
BUILD_FAIL. Quantify separately from genuine translation errors (~2-5% of total).

**RUN_FAIL / VERIFY_FAIL categories:**

| Category | Indicator | Typical cause |
|----------|-----------|---------------|
| RUN_FAIL:segfault | SIGSEGV/SIGBUS | Null pointer, buffer overrun |
| RUN_FAIL:timeout | 300s limit, exit_code=-1 | Infinite loop or deadlock |
| VERIFY_FAIL:wrong_output | stdout_pattern not matched | Semantic translation error |
| VERIFY_FAIL:numeric_mismatch | numeric_comparison failed | Numerical accuracy degradation |
| VERIFY_FAIL:false_positive_override | verify=pass, overall=VERIFY_FAIL | OpenCL clBuildProgram hidden failure |

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
