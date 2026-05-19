---
name: eval-grader
description: >
  Evaluation result grading and classification workflow. Use when classifying eval
  results into pass/fail categories, diagnosing failure patterns in batch results,
  computing pass rates with proper exclusions, or preparing result tables for papers.
  Handles the grading pipeline: load results, apply exclusions, classify failure modes,
  compute statistics, generate summary tables.
auto-activate: false
---

# Eval Result Grader

Structured workflow for grading and classifying evaluation results from batch runs.
Produces defensible statistics for paper reporting.

**Trigger:** `/eval-grader` or when classifying/summarizing eval batch results.

## When to use

- After `/post-eval` completes and you need to classify results
- Computing pass rates for paper tables
- Diagnosing systematic failure patterns across models
- Comparing two models' results on the same task set

## Arguments

- `<result-path>` — path to a result JSON or directory of results
- `--model <name>` — filter to specific model
- `--config <name>` — filter to specific configuration

## Grading Pipeline

### Step 1: Load Results

Read result files from the project's results directory. Each result should contain
at minimum: task identifier, model, configuration, and outcome status.

### Step 2: Apply Exclusions

Apply known-failing case exclusions. The exclusion list should be maintained in
`known-issues.md` or equivalent. Key rules:
- Exclude cases where the task itself is known to be broken
- Document the exclusion formula and denominator clearly
- Report excluded count alongside statistics

### Step 3: Classify Failure Modes

For non-passing results, classify into fine-grained categories relevant to the
project's domain. Build a failure taxonomy with:
- Category and subcategory
- Typical root cause
- Count and percentage of total failures

### Step 4: Compute Statistics

Report per model and configuration:
```
Pass rate:       PASS / N_valid x 100
Failure breakdown: <category>: X%, <category>: Y%
```

For papers: report both single-sample and multi-sample pass rates if applicable.

### Step 5: Generate Summary Table

Output a markdown table suitable for paper inclusion.

## Verification Gates

Before reporting any statistic:
1. Confirm exclusion list was applied
2. Confirm denominator matches expected task count
3. Cross-check at least 2-3 individual results manually
4. Flag anomalies (e.g., tasks that pass at baseline but fail with augmentation)
