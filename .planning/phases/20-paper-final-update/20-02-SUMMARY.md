---
phase: 20-paper-final-update
plan: "02"
subsystem: data-analysis
tags: [gpt-4.1-mini, analysis-pipeline, xsbench, data-refresh, cross-model]
dependency_graph:
  requires: []
  provides:
    - "Freshly regenerated paper_data_gpt41mini.json with 942-file dataset (577 primary tasks)"
    - "Freshly regenerated cross_model_comparison.json with 30 common kernels"
    - "Freshly regenerated error_taxonomy.json with full GPT subcategories"
    - "20-NUMBERS.md audit trail with all values and JSON key paths for paper edits"
  affects: [20-03-PLAN, 20-04-PLAN, paper.tex, overleaf.tex, appendices.tex]
tech_stack:
  added: []
  patterns: [sequential-pipeline-execution, cross-model-comparison, numbers-audit-trail]
key_files:
  created:
    - .planning/phases/20-paper-final-update/20-NUMBERS.md
  modified:
    - results/analysis/paper_data_gpt41mini.json
    - results/analysis/cross_model_comparison.json
    - results/analysis/error_taxonomy.json
    - results/analysis/error_taxonomy.md
    - results/evaluation/eval_summary.json
    - results/evaluation/eval_summary.md
    - docs/paper/figures/ (22 PDFs + PNGs + 1 .tex regenerated)
key_decisions:
  - "D-01: GPT primary tasks grew from 557 to 577 after XSBench addition; pass count unchanged at 177, rate dropped from 31.8% to 30.7%"
  - "D-02: XSBench rejoined common-kernel set as both_fail (30 kernels, was 29); xsbench both failed for both models"
  - "D-03: Chi-squared increased from 5.54 to 7.83 (p from 0.019 to 0.005) -- more statistically significant cross-model difference"
  - "D-04: All 20 new XSBench primary tasks resulted in BUILD_FAIL, explaining the increase from 247 to 267 BUILD_FAILs"
patterns_established:
  - "20-NUMBERS.md format: 11 sections with JSON key paths for every value, enabling traceable paper edits"
requirements_completed: []
metrics:
  duration: 6min
  completed: "2026-04-09"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 61
---

# Phase 20 Plan 02: Analysis Pipeline Re-Run with XSBench Data Summary

**Re-ran full analysis pipeline with 942-file GPT dataset (32 new XSBench results), producing fresh analysis JSONs and 318-line 20-NUMBERS.md audit trail; GPT 577 tasks at 30.7% pass rate, chi2=7.83 (p=0.005), 30 common kernels**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-09T02:11:59Z
- **Completed:** 2026-04-09T02:17:48Z
- **Tasks:** 2
- **Files modified:** 61

## Accomplishments
- Re-ran all 4 analysis scripts (analyze_eval, generate_paper_data, cross_model_comparison, build_error_taxonomy) with complete 942-file GPT dataset
- Regenerated all paper figures (14 PDFs + PNGs + LaTeX table) with updated XSBench data
- Created comprehensive 20-NUMBERS.md (318 lines) with all 11 required sections, JSON key paths for every value, and delta comparison against 19-NUMBERS.md

## Task Commits

Each task was committed atomically:

1. **Task 1: Re-run Phase 19 analysis pipeline with XSBench data** - `0feecf9` (feat)
2. **Task 2: Capture fresh numbers to 20-NUMBERS.md** - `671cb42` (docs)

## Files Created/Modified
- `results/evaluation/azure-gpt-4.1-mini/xsbench-*.json` (32 new files) - XSBench GPT evaluation results
- `results/analysis/paper_data_gpt41mini.json` - GPT primary campaign stats (577 tasks, 30.7%)
- `results/analysis/cross_model_comparison.json` - Cross-model chi2=7.83, 30 common kernels
- `results/analysis/error_taxonomy.json` - Failure subcategory counts by model
- `results/evaluation/eval_summary.json` - Aggregated eval summary for all models
- `docs/paper/figures/*.pdf` and `*.png` - 22 regenerated figure files
- `.planning/phases/20-paper-final-update/20-NUMBERS.md` - Audit trail for paper edits

## Decisions Made
- GPT pass rate dropped from 31.8% to 30.7% (same 177 passes, larger denominator of 577). This means paper text referencing "31.8%" must be updated to "30.7%".
- Chi-squared significance increased (p=0.005 vs 0.019) -- cross-model difference is now highly significant.
- XSBench added as both_fail in per-kernel agreement (both models fail on XSBench). Common kernels went from 29 to 30.
- All 20 new XSBench primary tasks resulted in BUILD_FAIL, consistent with XSBench being a complex multi-file kernel.
- Figure regeneration succeeded (scienceplots available in venv); all figures now reflect 942-file dataset.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] analyze_eval.py does not accept -v flag**
- **Found during:** Task 1 (STEP 1, script 1)
- **Issue:** The plan's RESEARCH.md CLI invocation included `-v` for analyze_eval.py, but the 20-02-PLAN task action correctly noted "NOTE: analyze_eval.py has NO -v flag -- omit it"
- **Fix:** Ran without `-v` flag as specified in the plan's action section
- **Files modified:** None (runtime adjustment only)
- **Verification:** Script completed successfully
- **Committed in:** 0feecf9

**2. [Rule 3 - Blocking] generate_paper_figures.py requires --project-root flag**
- **Found during:** Task 1 (STEP 2, figure regeneration)
- **Issue:** Plan's figure generation command omitted `--project-root`
- **Fix:** Added `--project-root /home/samyak/Desktop/parbench_sam` to the command
- **Files modified:** None (runtime adjustment only)
- **Verification:** All figures regenerated successfully
- **Committed in:** 0feecf9

---

**Total deviations:** 2 auto-fixed (both Rule 3 - blocking CLI issues)
**Impact on plan:** Trivial CLI flag adjustments. No scope creep.

## Issues Encountered
None beyond the CLI flag deviations documented above.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None -- all analysis files contain real data from the 942-file dataset. No placeholder values or mock data.

## Next Phase Readiness
- All analysis JSONs fresh and reflect complete 942-file dataset
- 20-NUMBERS.md provides complete audit trail for Plans 20-03 (overleaf.tex + appendices.tex edits) and 20-04 (paper.tex sync)
- Key numbers to propagate: GPT 577 tasks, 30.7% [27.1%, 34.6%], chi2=7.83, p=0.005, h=0.161, 30 common kernels, combined 449/1287=34.9% [32.3%, 37.5%]

## Self-Check: PASSED

All 6 key files verified on disk. Both task commits (0feecf9, 671cb42) verified in git log.

---
*Phase: 20-paper-final-update*
*Plan: 02*
*Completed: 2026-04-09*
