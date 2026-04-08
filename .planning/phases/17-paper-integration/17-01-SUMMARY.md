---
phase: 17-paper-integration
plan: "01"
status: complete
subsystem: paper-tex
tags: [data-integration, gpt-41-mini, tables, pending-markers]
dependency_graph:
  requires: [16-04-SUMMARY.md, paper_data_gpt41mini.json, cross_model_comparison.json, error_taxonomy.json]
  provides: [paper.tex with all GPT data fills, zero tbd cells, zero content-line pending markers except hardware]
  affects: [17-02, 17-03, 17-04]
tech_stack:
  added: []
  patterns: [inline-src-comments, wilson-ci]
key_files:
  created: []
  modified: [docs/paper/latex/paper.tex]
decisions:
  - Used JSON CI bounds directly (minor rounding differences from plan values)
  - Deferred pass@k cross-model comparison (different task subsets)
  - Deferred Azure cost data (unavailable)
  - Preserved hardware specs pending marker with TODO comment
metrics:
  duration_seconds: 294
  completed: "2026-04-08T00:23:11Z"
  task_count: 2
  file_count: 1
---

# Phase 17 Plan 01: Fill GPT-4.1 Mini Data into Paper.tex Summary

All placeholder markers in paper.tex replaced with verified GPT-4.1 mini data from pre-computed JSON analysis files, transforming the paper from a single-model draft to a dual-model submission.

## Summary

Filled 17 content-line `\pending{}` markers and 24 `\tbd` table cells in paper.tex with verified GPT-4.1 mini data. Every number was verified against the actual JSON source files before insertion. Every filled value includes an inline `% src:` comment tracing to its data origin. The aggregate row uses sum of counts (433/1261=34.3%) per D-04-aggregate, not average of rates (33.75%).

## Changes Made

### Task 1: Fill 17 pending markers (commit ef90c86)
- **Abstract (line 84):** Replaced GPT pending with chi-squared result (29.2%, p<0.001, h=0.19)
- **Introduction contributions (line 151):** Replaced with 551 tasks, 1,261 total, two-provider framing
- **Findings paragraph (line 170):** Replaced with GPT pass rate and negligible effect size
- **Line 577:** Updated stale "pending" text to dual-model statement
- **Line 632:** Preserved hardware specs pending marker, added TODO(samyak) comment
- **Line 663:** Replaced evaluation cost pending with deferral text + TODO comment
- **Line 672:** Replaced results intro pending with 551/1,261 total tasks
- **Line 697:** Replaced overall pass rates pending with GPT 29.2% and chi-squared test
- **Line 702:** Replaced chi-squared standalone pending with full test statistics
- **Line 797:** Replaced per-kernel pending with cross-model agreement (13 both-pass, 11 qwen-only, 2 gpt-only)
- **Line 836:** Replaced tier boundaries pending with two-model consensus confirmation
- **Line 917:** Replaced augmentation pending with GPT L0-L4 coverage note
- **Line 969:** Replaced OpenCL asymmetry pending with GPT 30.0% vs 3.7% (25/27 BUILD_FAIL)
- **Line 986:** Replaced pass@k pending with deferral (different task subsets)
- **Line 1016:** Replaced model capability pending with GPT 29.2% cross-architecture demonstration
- **Line 1030:** Replaced direction asymmetry pending with GPT 40.0% vs 3.7% gap
- **Line 1033:** Replaced augmentation null result pending with BUILD_FAIL dominance evidence
- **Lines 1057-1061:** Replaced "Single-model evaluation" heading and text with "Two-model evaluation"
- **Line 1094:** Replaced conclusion pending with GPT 29.2% and p<0.001

### Task 2: Fill 24 tbd table cells (commit c694db2)
- **tab:overall-pass GPT row (9 cells):** 161 / 316 / 43 / 31 / 0 / 0 / 551 / 29.2% / [25.6%, 33.2%]
- **tab:overall-pass Aggregate row (9 cells):** 433 / 557 / 187 / 82 / 1 / 1 / 1,261 / 34.3% / [31.8%, 37.0%]
- **tab:direction-rates GPT column (6 cells):**
  - cuda-to-omp: 40.0% (48/120) [31.7%, 48.9%]
  - omp-to-cuda: 17.9% (15/84) [11.1%, 27.4%]
  - opencl-to-omp: 41.1% (37/90) [31.5%, 51.4%]
  - omp-to-opencl: 33.3% (30/90) [24.5%, 43.6%]
  - cuda-to-opencl: 30.0% (30/100) [21.9%, 39.6%]
  - opencl-to-cuda: 3.7% (1/27) [0.7%, 18.3%]

## Verification Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Content-line pending markers | 1 (hardware) | 1 | PASS |
| tbd content-line cells | 0 | 0 | PASS |
| src: paper_data_gpt41mini comments | >= 8 | 17 | PASS |
| src: cross_model_comparison comments | >= 5 | 6 | PASS |
| "Two models are evaluated" (line 577) | 1 match | 1 | PASS |
| "Two-model evaluation" (threats) | 1 match | 1 | PASS |
| "Single-model evaluation" removed | 0 matches | 0 | PASS |
| Balanced LaTeX environments | begin=end | 23=23 | PASS |
| Wilson CI aggregate 433/1261 | [31.8%, 37.0%] | [31.8%, 37.0%] | PASS |

## Deviations from Plan

### Minor CI Bound Adjustments

**[Rule 1 - Bug prevention] Used actual JSON CI bounds instead of plan values**
- **Found during:** Task 1 and Task 2
- **Issue:** Plan CI bounds had minor rounding differences from JSON source (e.g., plan said CI upper 0.4893 for cuda-to-omp but JSON has 0.4894)
- **Fix:** Used JSON values directly per critical trap #5 ("verify ALL numbers against actual JSON file contents")
- **Files modified:** docs/paper/latex/paper.tex
- **Impact:** None -- differences are in 4th decimal place

## Issues Encountered

None -- plan executed as written. All gate files existed. All numbers matched expected ranges from JSON sources.
