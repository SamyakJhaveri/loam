---
phase: 09-objective-quantitative-analysis
plan: 02
subsystem: analysis
tags: [quantitative, self-repair, pass-at-k, sloc-correlation, token-cost, complexity, opencl, paper-claims]
dependency_graph:
  requires: [09-01-SUMMARY, results/evaluation/together-qwen-3.5-397b-a17b/*.json, results/analysis/sloc_analysis.json, specs/*.json]
  provides: [scripts/analysis/quantitative_findings.py (complete 14-dimension), results/analysis/quantitative_findings.json, results/analysis/quantitative_findings.md]
  affects: [09-03-PLAN, phase-10, phase-11]
tech_stack:
  added: []
  patterns: [self-repair from attempts[], pass@k from seed variants, Spearman/Pearson correlation, Fisher's exact test, Chi-squared contingency]
key_files:
  created: []
  modified:
    - scripts/analysis/quantitative_findings.py
decisions:
  - "Self-repair computed from Campaign 1 only (max_retries=3); Campaign 2 excluded per Research Pitfall 8"
  - "pass@k uses simple fraction (pass@1 = any seed passes, pass@3 = all pass) per D-15"
  - "SLoC correlation is significant negative (rho=-0.471, p=0.007): larger kernels harder to translate"
  - "Paper claims extended to 20 entries (exceeding 15 minimum) with Rodinia-only and all-suite scopes"
  - "Cross-check diffs against selfrepair_analysis.json and token_analysis.json are expected due to different KNOWN_FAIL exclusion scope (8 vs 6)"
metrics:
  duration: 9min
  completed_date: 2026-04-05
  tasks: 1
  files: 1
---

# Phase 09 Plan 02: Quantitative Findings Extension Summary

Extended quantitative_findings.py from 5 dimensions to all 14, adding self-repair effectiveness, pass@k estimates, per-kernel difficulty tiers, complexity correlation, cross-suite comparison, token cost analysis, SLoC correlation (significant negative), OpenCL kernel-only effect, and 20-entry paper claims mapping.

## Commits

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add dimensions 6-13 + paper_claims + markdown | 30a1bfb | scripts/analysis/quantitative_findings.py |

## What Was Built

### New Dimensions Added (Campaign 1)

| Dimension | Key Finding | Key Metric |
|-----------|-------------|------------|
| 6. Self-repair | 20.4% repair rate, 111 full repairs, 4 regressions | Campaign 1 only, per-failure-type breakdown |
| 8. Per-kernel tiers | 31 kernels ranked, page-rank/stencil1d easiest (100%) | Quartile boundaries, top-5/bottom-5, direction anomalies |
| 9. Complexity correlation | Chi-squared test across 4 complexity classes | single_file, multi_to_single, single_to_multi, multi_to_multi |
| 10. Cross-suite | Per-suite L0 rates with SLoC and multi-file characteristics | SLoC from sloc_analysis.json, multi-file from specs |
| 11. Token cost | $55.88 total, $0.08/task, $0.21/PASS | Together AI pricing ($0.60/$3.60 per 1M) |
| 12. SLoC correlation | Spearman rho=-0.471, p=0.007 (significant negative) | Larger kernels harder to translate |
| 13. OpenCL kernel-only | Fisher's exact: X-to-opencl vs X-to-omp | Kernel-only vs full-program pass rate comparison |

### New Dimensions Added (Campaign 2)

| Dimension | Key Finding | Key Metric |
|-----------|-------------|------------|
| 7. pass@k | pass@1=27.1%, pass@3=11.4% across 140 tasks | Per-direction and per-suite breakdowns |

### Paper Claims Mapping (Dimension 14)

20 claims mapped to JSON paths with scope annotations:
- 1 Rodinia-only scoped claim (overall_pass_rate_rodinia)
- 19 all-suite scoped claims covering pass rates, task counts, failure percentages, self-repair, augmentation, token cost, SLoC correlation

### Script Statistics

- Total lines: 3,099 (from 1,471 in Plan 01)
- Output JSON: complete 14-dimension structure
- Output markdown: 302 lines with all dimension tables
- Cross-checks: 8+ checks against existing analysis files (paper_data, error_taxonomy, statistical, selfrepair, token)

### Key Quantitative Results

| Metric | Value |
|--------|-------|
| C1 overall pass rate | 38.0% [34.5%, 41.6%] (n=700) |
| Rodinia subset pass rate | 36.3% (n=480) |
| Self-repair rate | 20.4% (111/544 initially failing) |
| pass@1 (T=0.7) | 27.1% [20.5%, 35.0%] (n=140 tasks) |
| pass@3 (T=0.7) | 11.4% [7.2%, 17.8%] |
| SLoC-pass rate correlation | rho=-0.471, p=0.007 (significant) |
| Total token cost (C1) | $55.88 |
| Cost per PASS | $0.21 |

## Deviations from Plan

None -- plan executed exactly as written.

## Self-Check: PASSED

- [x] scripts/analysis/quantitative_findings.py exists (3,099 lines, >1,000 min)
- [x] Commit 30a1bfb exists
- [x] Script exits 0 with --project-root
- [x] campaign_1 contains: self_repair, per_kernel_tiers, complexity_correlation, cross_suite, token_cost, sloc_correlation, opencl_kernel_only_effect
- [x] campaign_2 contains: pass_at_k (with pass_at_1 and pass_at_3)
- [x] paper_claims has 20 entries (>= 15)
- [x] self_repair.overall_repair_rate field present
- [x] sloc_correlation.spearman.rho and p_value present
- [x] token_cost.total_cost field present
- [x] Markdown has "Per-Kernel Difficulty" section with table
- [x] Markdown has "Campaign 2" section with pass@k table
- [x] Markdown is 302 lines (> 200)
- [x] 13/13 existing tests pass
