---
phase: 20-paper-final-update
plan: "03"
subsystem: paper-latex
tags: [overleaf, appendices, structural-changes, gpt-numbers, cross-model]
dependency_graph:
  requires: ["20-02"]
  provides: ["corrected-overleaf-tex", "corrected-appendices-tex"]
  affects: ["20-04"]
tech_stack:
  added: []
  patterns: ["% src: provenance comments on every data claim"]
key_files:
  created: []
  modified:
    - docs/paper/latex/overleaf.tex
decisions:
  - "Case study rows filled with Qwen+GPT data from fresh JSONs"
  - "Footnote restored documenting cuda-to-omp_target as Qwen-only direction"
  - "XSBench coverage asymmetry note added (30 Qwen vs 20 GPT primary tasks)"
  - "Effect-size paragraph kept at '2 of 7' per fresh Phase 20 data (not '1 of 7' as 19-STRUCTURAL-CHANGES.md suggested)"
  - "appendices.tex verified correct with no changes needed"
metrics:
  duration_seconds: 397
  completed: "2026-04-09T02:45:00Z"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 1
  commits: 1
---

# Phase 20 Plan 03: Apply Structural Changes + Numeric Updates Summary

Overleaf.tex case study rows filled, footnote restored, XSBench qualification added; appendices.tex verified correct (all tables match fresh JSONs from Plan 20-02).

## Task Results

### Task 1: Update overleaf.tex -- all 13 structural changes + numeric updates

**Status:** COMPLETE
**Commit:** b6b7fcf

Plan 20-01 had already applied 11 of 13 structural changes with fresh Phase 20 numbers. This task completed the remaining 3 items:

1. **Case study rows (CHANGE 4 partial):** Filled cuda-to-omp_target row with Qwen data (12.5% L0, 17.5% all-levels [8.8%, 31.9%], GPT "--"). Filled omp_target-to-cuda row with both Qwen (70.0% L0, 78.0% all-levels [64.8%, 87.2%]) and GPT (30.0% [19.1%, 43.8%]) data.

2. **Footnote (CHANGE 1):** Added footnote to cross-model comparison section: "Cross-model comparison covers 7 of 8 evaluated translation directions; cuda-to-omp_target GPT-4.1 mini results are not available (Qwen-only direction)."

3. **XSBench coverage qualification (CHANGE 5):** Added note in per-kernel agreement paragraph documenting asymmetric XSBench coverage (Qwen: 30 primary tasks across 6 directions, GPT: 20 primary tasks across 4 directions; xsbench both-fail because both models fail all tasks).

**Already applied by Plan 20-01 (verified, not changed):**
- CHANGE 11 (Abstract): GPT 30.7%, 577, chi2=7.83, p=0.005, h=0.16
- CHANGE 6 (Intro): Same values
- CHANGE 7 (Table 3): GPT row 177/267/54/79/0/0/577/30.7%, Aggregate 449/1287/34.9%
- CHANGE 8 (Failure taxonomy): BUILD_FAIL 66.8%, VERIFY_FAIL 13.7% vs 7.2%
- CHANGE 10 (Cross-model intro): chi2=7.83, p=0.005, h=0.16
- CHANGE 2 (Direction table): 7 common directions, omp_target-to-cuda replaces cuda-to-omp_target
- CHANGE 3 (Effect-size): "2 of 7" negligible (correct per fresh data; cuda-to-omp |h|=0.16, opencl-to-omp |h|=0.15)
- CHANGE 9 (Per-kernel): 30 kernels, 18/5/6/1 split
- CHANGE 12 (Discussion): 30.7%
- CHANGE 13 (Conclusion): 30.7%, 577, p=0.005

**Stale value sweep:** Zero matches for: 29.2% GPT, 551 tasks, 161/551, 10.97, 0.000926, h=0.86, h=0.19, 4 of 7, 13 are solved. "31 kernels" appears 3 times, all correctly referring to Qwen's 31 evaluated kernels (not cross-model 30).

**Verification:**
- LaTeX environments balanced: begin=30, end=30
- Source comments: 197 (requirement >= 50)
- Cross-model direction table: 7 data rows
- Footnote present: 1

### Task 2: Update appendices.tex -- self-repair, augmentation, pass@k tables + stats summary

**Status:** COMPLETE (no changes needed)
**Commit:** N/A (all values already correct from Plan 20-01)

All four appendix tables verified against fresh JSONs:

1. **Self-repair table (tab:self-repair):** GPT column correct (577/134/43/177/+32.1%/367/5). Combined column correct (1287/294/155/449/+52.7%/759/12).

2. **Augmentation table (tab:augmentation-rates):** GPT column correct (L0: 29.3% [21.8%, 38.2%], L1: 28.4% [21.0%, 37.3%], L2-L3: 31.3% [23.6%, 40.3%], L4: 33.0% [25.1%, 42.1%]). Cochran-Armitage: z=0.62, p=0.54.

3. **Pass@k table (tab:pass-at-k):** GPT row correct (30.7% greedy, 25.6% pass@1, 31.5% pass@3, -- for hard_fail/noisy/always_pass).

4. **Stats summary table (tab:stats-summary):** chi2=7.83, p=0.005, Cramer's V=0.08, GPT CA z=0.62 p=0.54.

**Verification:**
- Zero stale values (161/551, 21.6% GPT, 10.97, 0.000926)
- LaTeX environment balance: begin-end = 1 (expected pre-existing +1)
- Source comments: 88

## Deviations from Plan

### Plan-Data Discrepancy (documented, not a code change)

**1. [Rule 2 - Correction] Effect-size "2 of 7" vs "1 of 7"**
- **Found during:** Task 1, CHANGE 3 verification
- **Issue:** 19-STRUCTURAL-CHANGES.md said "1 of 7 directions has |h| < 0.20" based on Phase 19 data where opencl-to-omp had |h|=0.2107. Fresh Phase 20 data shows opencl-to-omp |h|=0.1490 (< 0.20), making it 2 of 7 negligible directions.
- **Resolution:** Kept "2 of 7" as written by Plan 20-01, which is correct per the authoritative Phase 20 JSONs. 20-NUMBERS.md Section 4 confirms: "2 negligible (cuda-to-omp, opencl-to-omp)".
- **Files affected:** None (no change needed)

## Self-Check: PASSED

- [x] docs/paper/latex/overleaf.tex exists and modified (commit b6b7fcf)
- [x] docs/paper/latex/appendices.tex exists and verified correct (no changes needed)
- [x] Commit b6b7fcf verified in git log
