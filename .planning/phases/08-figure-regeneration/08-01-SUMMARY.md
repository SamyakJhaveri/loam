---
phase: 08-figure-regeneration
plan: 01
subsystem: figure-generation
tags: [matplotlib, figures, paper, cleanup, heatmap, bar-chart]
dependency_graph:
  requires: []
  provides:
    - "Updated generate_paper_figures.py with 2-model layout and 5-suite coverage"
    - "F3 heatmap: 29 kernels x 6 directions with suite grouping"
    - "F4 taxonomy: all suites, all directions stacked bar"
    - "F6 cross-suite: 5-suite pass rate comparison with Wilson CIs"
    - "F7 augmentation: Qwen-only, all suites"
  affects:
    - "docs/paper/figures/f3_kernel_model_heatmap.{pdf,png}"
    - "docs/paper/figures/f4_failure_taxonomy.{pdf,png}"
    - "docs/paper/figures/f6_cross_suite_comparison.{pdf,png}"
    - "docs/paper/figures/f7_augmentation_robustness.{pdf,png}"
tech_stack:
  added: []
  patterns:
    - "_wilson_ci() helper for binomial confidence intervals"
    - "SUITE_COLORS and SUITE_DISPLAY mappings for 5-suite coverage"
    - "Suite grouping with divider lines in heatmap"
key_files:
  created: []
  modified:
    - "scripts/generate_paper_figures.py"
decisions:
  - "Used 29 kernels (not 34) in F3 -- 5 HeCBench omp_target-only kernels excluded per D-10"
  - "F3 uses single-panel 29x6 grid with text annotation for GPT-4.1 mini N/A instead of 6 gray columns"
  - "F4 changed from dual-panel model-grouped to single-panel direction-grouped stacked bar"
  - "Moved NA_COLOR before MODEL_COLORS to fix forward reference"
  - "Removed _draw_heatmap_panel and _draw_taxonomy_panel helpers (no longer used)"
metrics:
  duration: "6min"
  completed: "2026-04-05"
  tasks_completed: 3
  tasks_total: 3
  files_modified: 1
---

# Phase 08 Plan 01: Figure Script Modernization Summary

Updated `scripts/generate_paper_figures.py` with 2-model constants (Qwen + GPT-4.1 mini N/A), 5-suite SUITE_ORDER, redesigned F3/F4/F6/F7 figures, and removed all old model/fallback data.

## Task Results

### Task 1: Clean model constants, remove old fallback data, expand suite coverage
**Commit:** 1654e2c

- Removed 3 old models (claude-sonnet, groq-llama, gemini-2.5) from MODEL_COLORS, MODEL_DISPLAY, MODEL_DISPLAY_SHORT, MODEL_LINESTYLE
- Added `azure-gpt-4.1-mini` entries with N/A styling to all 4 model dicts
- Deleted `AUG_ROBUSTNESS`, `AUG_TOTAL`, `XSBENCH_L0`, `_XS_MODELS`, `_XS_MODEL_DISPLAY` fallback constants
- Expanded `SUITE_ORDER` from 3 to 5 suites, added `SUITE_DISPLAY` mapping
- Changed `build_kernel_model_matrix` default `suite` param from `"rodinia"` to `None`
- Redesigned F4 as single-panel all-suites/all-directions stacked bar (138 total tasks across 6 directions)
- Redesigned F7 as Qwen-only augmentation line chart covering all suites (26 kernels, L0-L4)

### Task 2: Redesign F3 heatmap for 29 kernels x 6 directions with suite grouping
**Commit:** 7c8a29d

- Replaced triple-panel Rodinia-only heatmap with single-panel all-suites design
- 29 kernels x 6 standard directions, grouped by suite with black divider lines (linewidth=2.0)
- Suite labels on left margin (rotated 90 degrees, bold, fontsize=9)
- Status abbreviations in each cell (P, BF, RF, VF, EF) with em-dash for missing data
- GPT-4.1 mini noted as pending via italic text annotation below legend
- Removed old `_draw_heatmap_panel` and `_draw_taxonomy_panel` helper functions
- Fixed NA_COLOR forward reference by moving definition before MODEL_COLORS

### Task 3: Redesign F6 as cross-suite bar chart and update FIGURE_REGISTRY
**Commit:** 5beb6f8

- Replaced `generate_f6_xsbench_comparison()` with `generate_f6_cross_suite_comparison()`
- Added `_wilson_ci()` helper for 95% Wilson score confidence intervals
- Added `SUITE_COLORS` mapping (Okabe-Ito palette per suite)
- 5 bars with pass rates, asymmetric error bars, and pass/total annotations
- Updated FIGURE_REGISTRY: `"F6": "f6_cross_suite_comparison"`
- Updated main() dispatch message and function call

## Verification Results

All 4 modified figures generated without errors:
- **F3:** 29 kernels across 5 suites (rodinia: 21, xsbench: 1, rsbench: 1, mixbench: 1, hecbench: 5) -- PDF 49KB, PNG 283KB
- **F4:** 138 tasks across 6 directions (26+26+23+23+20+20) -- no suite filter
- **F6:** 5 suites with pass rates: rodinia 38/110 (34.5%), xsbench 0/6 (0%), rsbench 0/6 (0%), mixbench 2/6 (33.3%), hecbench 9/10 (90.0%)
- **F7:** Qwen-only, 26 kernels, L0-L4 rates: 61.5%, 53.8%, 65.4%, 53.8%, 61.5%
- No old model names remain in script (grep count: 0)
- Script parses without syntax errors

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed NA_COLOR forward reference**
- **Found during:** Task 2
- **Issue:** After Task 1 moved old model constants, MODEL_COLORS at line 83 referenced NA_COLOR which was defined at line 124 -- causing NameError at import time
- **Fix:** Moved NA_COLOR definition to line 83 (before MODEL_COLORS), removed duplicate at old location
- **Files modified:** scripts/generate_paper_figures.py
- **Commit:** 7c8a29d

## Known Stubs

None -- all data is live from result JSONs on disk.

## Self-Check: PASSED
