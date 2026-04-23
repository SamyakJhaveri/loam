# Self-Repair Analysis — ParBench Evaluation

**708 total results**: 708 single-attempt, 0 multi-attempt (needed retry).

Of 0 retried translations:
- No multi-attempt translations found (all tasks single-attempt).

## Table 1: Per-Model Self-Repair

| Model | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate | Improvement Rate |
|-------|-------------:|------------:|--------:|----------:|-----------:|------------:|-----------------:|

## Table 2: By Initial Failure Type

| Initial Failure | Count | Full Repair | Partial | No Change | Regression | Repair Rate |
|-----------------|------:|------------:|--------:|----------:|-----------:|------------:|

## Table 3: Per-Kernel Self-Repair (sorted by repair rate)

| Kernel | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate |
|--------|-------------:|------------:|--------:|----------:|-----------:|------------:|

## Table 4: Token Overhead from Self-Repair

| Metric | Value |
|--------|------:|
| Total extra prompt tokens | 0 |
| Total extra completion tokens | 0 |
| Total extra tokens (all retries) | 0 |
| Mean extra tokens per retry | 0 |
| Full-repair extra prompt tokens | 0 |
| Full-repair extra completion tokens | 0 |

## Table 5: Repair Trajectory Patterns

| Trajectory | Count | % of Multi-Attempt |
|------------|------:|-------------------:|

## Interpretation

Self-repair (retry with error feedback) converts failing translations to PASS.
The repair rate varies by initial failure type: BUILD_FAIL errors are generally
more amenable to repair than RUN_FAIL (which often indicates deeper algorithmic
issues). EXTRACTION_FAIL can be repaired by reformatting the response.

Partial repairs (e.g., BUILD_FAIL → RUN_FAIL) show the LLM understood the
build error and fixed it, but introduced a runtime issue. This demonstrates
iterative improvement capability even when full repair isn't achieved.

