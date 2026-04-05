---
phase: 09-objective-quantitative-analysis
plan: 01
subsystem: analysis
tags: [quantitative, statistics, wilson-ci, mcnemar, cochran-armitage, provenance]
dependency_graph:
  requires: [results/evaluation/together-qwen-3.5-397b-a17b/*.json]
  provides: [scripts/analysis/quantitative_findings.py, results/analysis/quantitative_findings.json]
  affects: [09-02-PLAN, 09-03-PLAN]
tech_stack:
  added: [scipy.stats, numpy]
  patterns: [provenance-wrapped findings, Wilson CI, McNemar exact, Cochran-Armitage trend, failure taxonomy regex]
key_files:
  created:
    - scripts/analysis/quantitative_findings.py
    - scripts/analysis/test_quantitative_findings.py
  modified: []
decisions:
  - "Used 8 KNOWN_FAIL exclusions (6 Rodinia + 2 HeCBench) per known-issues.md, yielding 700 C1 / 420 C2 instead of paper_data.json's 710/426 (which uses 6)"
  - "Cross-check against existing analysis files warns but does not fail on expected minor differences from different exclusion counts"
  - "Direction asymmetry pairs on (suite, kernel) tuple to prevent cross-suite false pairing per Research Pitfall 4"
metrics:
  duration: 9min
  completed_date: 2026-04-05
  tasks: 1
  files: 2
---

# Phase 09 Plan 01: Quantitative Findings Foundation Summary

Monolithic quantitative findings script computing 5 statistical dimensions with provenance framework, producing structured JSON and markdown output from 1,248 Qwen evaluation results.

## Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 (RED) | TDD failing tests | c93955b | scripts/analysis/test_quantitative_findings.py |
| 1 (GREEN) | Implementation + test fix | 2ad72ee | scripts/analysis/quantitative_findings.py, scripts/analysis/test_quantitative_findings.py |

## What Was Built

### Data Pipeline
- Loads all 1,248 result JSONs from `results/evaluation/together-qwen-3.5-397b-a17b/`
- Excludes 128 records matching 8 KNOWN_FAIL specs (6 Rodinia + 2 HeCBench)
- Splits remaining 1,120 records into Campaign 1 (700, temp=0.0) and Campaign 2 (420, temp=0.7)

### Five Quantitative Dimensions (Campaign 1)

| Dimension | Finding | Key Metric |
|-----------|---------|------------|
| 1. Aggregate pass rates | 38.0% [34.5%, 41.6%] overall | Wilson 95% CI, n=700 |
| 2. Per-direction rates (L0) | cuda-to-omp best at 66.7%, opencl-to-cuda worst at 10.0% | 6 standard + 2 case study |
| 3. Direction asymmetry | McNemar paired on (suite, kernel) | Bonferroni-corrected alpha |
| 4. Augmentation trends | Cochran-Armitage per-direction + aggregate with Cohen's h | Non-significant trend |
| 5. Failure taxonomy | BUILD_FAIL dominant, subcategorized via regex | Top-3 subcategories reported |

### Provenance Framework
- Every computed value wrapped with `make_finding()`: value, source, files_matched, derivation, optional CI fields
- All rates stored as decimals 0-1 per design decision D-21

### Cross-Check
- Compares against existing paper_data.json, statistical_analysis.json, error_taxonomy.json
- Minor expected difference: C1 pass rate 0.38 vs paper_data's 0.3831 (due to 8 vs 6 KNOWN_FAIL exclusions)
- Status: pass (no warnings starting with "WARNING")

## Per-Suite Breakdown (Campaign 1)

| Suite | Pass Rate | n |
|-------|-----------|---|
| hecbench | 64.6% | 130 |
| mixbench | 26.7% | 30 |
| rodinia | 36.3% | 480 |
| rsbench | 0.0% | 30 |
| xsbench | 0.0% | 30 |

## Tests

13 tests covering all core functions:
- KNOWN_FAIL exclusion (8 specs, 6 Rodinia + 2 HeCBench)
- Campaign split (temp=0.0 vs temp>0)
- Wilson CI fields and edge cases
- Provenance wrapper with and without CI
- Suite extraction for all 5 suites
- Direction extraction with omp_target
- Augment level parsing from filenames
- Failure taxonomy classification
- McNemar pairing on (suite, kernel)
- Cochran-Armitage per-direction and aggregate

## Deviations from Plan

None -- plan executed exactly as written.

## Self-Check: PASSED

- [x] scripts/analysis/quantitative_findings.py exists (1471 lines, >500 min)
- [x] scripts/analysis/test_quantitative_findings.py exists (313 lines)
- [x] Commit c93955b exists (RED phase)
- [x] Commit 2ad72ee exists (GREEN phase)
- [x] Output JSON produced at results/analysis/quantitative_findings.json (1702 lines)
- [x] Output markdown produced at results/analysis/quantitative_findings.md (111 lines)
- [x] 13/13 tests pass
- [x] Exit code 0
- [x] File counts: 1248 total, 700 C1, 420 C2
