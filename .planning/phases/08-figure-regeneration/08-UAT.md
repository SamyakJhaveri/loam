---
status: complete
phase: 08-figure-regeneration
source: [08-01-SUMMARY.md, 08-02-SUMMARY.md]
started: 2026-04-04T22:00:00Z
updated: 2026-04-04T22:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Full Figure Pipeline Runs Without Errors
expected: Run `python3 scripts/generate_paper_figures.py --figure all -v` from project root. Script completes with zero errors/warnings. All 10 figures + T2 table generated successfully.
result: pass

### 2. F3 Heatmap Shows All Kernels Across 5 Suites
expected: Open `docs/paper/figures/f3_kernel_model_heatmap.pdf`. Single-panel heatmap with kernel rows grouped by suite with black divider lines. 6 direction columns. Status abbreviations or missing-API labels in each cell.
result: pass

### 3. F4 Failure Taxonomy Is Direction-Grouped Stacked Bar
expected: Open `docs/paper/figures/f4_failure_taxonomy.pdf`. Single-panel stacked bar chart grouped by direction. 6 direction bars with status categories stacked. Total of 138 tasks reflected across all bars.
result: pass

### 4. F6 Cross-Suite Comparison Shows 5 Suites with CIs
expected: Open `docs/paper/figures/f6_cross_suite_comparison.pdf`. 5 bars showing pass rates with asymmetric Wilson CI error bars. Pass/total annotations visible.
result: pass

### 5. F7 Augmentation Robustness Is Qwen-Only Line Chart
expected: Open `docs/paper/figures/f7_augmentation_robustness.pdf`. Qwen-only line chart showing pass rates at L0 through L4. All suites (26 kernels). Pass rate labels at all points.
result: pass

### 6. T2 LaTeX Table Has 2-Model Layout
expected: Open `docs/paper/figures/t2_model_comparison.tex`. Table has 2 rows: Qwen 3.5 397B (with real data: 49/138 overall, per-direction breakdowns) and GPT-4.1 mini (showing "pending" in all cells). No old model names present.
result: pass

### 7. All 10 PDFs and PNGs Exist and Are Non-Trivial
expected: All 10 PDF files exist in `docs/paper/figures/` and are >5KB. Corresponding PNG files also exist. T2 LaTeX file exists and is >100 bytes.
result: pass

### 8. Old Model References Fully Removed
expected: Grep `scripts/generate_paper_figures.py` for old model names: `claude-sonnet`, `groq-llama`, `gemini-2.5`. Zero matches found. No fallback constants remain.
result: pass

## Summary

total: 8
passed: 8
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none]
