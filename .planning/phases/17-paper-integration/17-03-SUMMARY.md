---
phase: 17-paper-integration
plan: "03"
status: complete
subsystem: paper-tex
tags: [augmentation-examples, anonymization, methodology, section-5, section-6.5]
dependency_graph:
  requires: [17-02-SUMMARY.md, paper_data.json, llm_evaluate.py, result JSONs for lavamd/bptree]
  provides: [paper.tex augmentation case studies, paper.tex anonymization subsection]
  affects: [17-04]
tech_stack:
  added: []
  patterns: [inline-src-comments, data-verified-against-disk]
key_files:
  created: []
  modified: [docs/paper/latex/paper.tex]
decisions:
  - Used actual result file data instead of plan's incorrect lavamd claims (L0+L4 PASS, not all 5)
  - Used actual failure types from result JSONs (bptree L0=BUILD_FAIL not RUN_FAIL)
  - Option B for anonymization (self-contained, no cross-ref to incomplete appendix)
  - Inserted anonymization subsection between Metrics and Hardware/Software in Section 5
metrics:
  duration_seconds: 148
  completed: "2026-04-08T00:31:57Z"
  task_count: 2
  file_count: 1
---

# Phase 17 Plan 03: Augmentation Case Studies and Prompt Anonymization Summary

Added augmentation degradation case studies (lavamd U-shaped, bptree recovery-then-reversion) verified against on-disk result JSONs, plus a self-contained Prompt Anonymization subsection documenting all 6 measures from llm_evaluate.py's build_translation_prompt().

## Summary

Two complementary additions to paper.tex:

1. **Augmentation degradation case studies (Section 6.5)** -- Two per-kernel examples inserted at the end of the Augmentation Robustness subsection, demonstrating that augmentation effects are kernel-specific and non-monotonic:
   - **lavamd** (CUDA-to-OMP): U-shaped pattern -- L0=PASS, L1=BUILD_FAIL, L2=BUILD_FAIL, L3=VERIFY_FAIL, L4=PASS. L4 succeeds on first attempt while L0 required self-repair.
   - **bptree** (CUDA-to-OMP): Recovery-then-reversion -- L0=BUILD_FAIL, L1=RUN_FAIL, L2=RUN_FAIL, L3=PASS (via self-repair), L4=BUILD_FAIL.

2. **Prompt Anonymization subsection (Section 5)** -- New subsection documenting all 6 anonymization measures from the evaluation pipeline: kernel identity removal, comment stripping, filename genericization, target filename anonymization, build command anonymization, and support file genericization. Each measure includes a `% src:` comment tracing to the specific function and line in `llm_evaluate.py`.

## Changes Made

### Task 1: Augmentation case studies (commit 261087d)

- Inserted 8 lines of LaTeX (2 paragraphs + 4 source comments) between the Fisher exact test paragraph and `\subsection{Cross-Direction Analysis}`
- lavamd example with verified per-level data: L0=PASS(2 attempts), L1=BUILD_FAIL(3), L2=BUILD_FAIL(3), L3=VERIFY_FAIL(3), L4=PASS(1)
- bptree example with verified per-level data: L0=BUILD_FAIL(3), L1=RUN_FAIL(3), L2=RUN_FAIL(3), L3=PASS(2), L4=BUILD_FAIL(3)
- Both examples frame as reinforcing the augmentation null-result interpretation

### Task 2: Prompt Anonymization subsection (commit 01b768c)

- Inserted 17 lines of LaTeX (subsection header + enumerate environment with 6 items + closing paragraph)
- Placed between `\subsection{Metrics}` and `\subsection{Hardware and Software}` in Section 5
- All 6 measures cross-referenced to llm_evaluate.py source
- Closing paragraph connects anonymization to augmentation as complementary contamination defenses
- Option B chosen: self-contained subsection with no cross-reference to incomplete appendix

## Verification Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| `grep 'lavamd'` count | >= 1 | 7 | PASS |
| `grep 'bptree'` count | >= 1 | 6 | PASS |
| L4 PASS for lavamd | >= 1 match | "PASS again at L4" | PASS |
| recovery-then-reversion for bptree | >= 1 match | present | PASS |
| L3 PASS for bptree | >= 1 match | "PASS at L3 (via self-repair)" | PASS |
| non-monotonic pattern | >= 1 match | present | PASS |
| `\subsection{Prompt Anonymization}` | 1 | 1 (line 619) | PASS |
| `\label{sec:anonymization}` | 1 | 1 | PASS |
| Kernel identity removal (measure 1) | >= 1 | 1 | PASS |
| Comment stripping (measure 2) | >= 1 | 1 | PASS |
| Filename genericization (measure 3) | >= 1 | 1 | PASS |
| Target filename anonymization (measure 4) | >= 1 | 1 | PASS |
| Build command anonymization (measure 5) | >= 1 | 1 | PASS |
| Support file genericization (measure 6) | >= 1 | 1 | PASS |
| Anonymization in Section 5 | between lines 553-687 | line 619 | PASS |
| LaTeX environments balanced | begin=end | 26=26 | PASS |
| anonymi term count | >= 5 | 8 | PASS |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected lavamd per-level data claims**
- **Found during:** Task 1 data verification
- **Issue:** Plan claimed lavamd passes "at ALL augmentation levels including L4" (all 5 levels PASS). Actual on-disk result files show: L0=PASS, L1=BUILD_FAIL, L2=BUILD_FAIL, L3=VERIFY_FAIL, L4=PASS. Only 2 of 5 levels pass.
- **Fix:** Rewrote lavamd example to describe the actual U-shaped pattern, which is actually a more interesting and informative case study than universal pass.
- **Files modified:** docs/paper/latex/paper.tex
- **Commit:** 261087d

**2. [Rule 1 - Bug] Corrected bptree per-level failure types**
- **Found during:** Task 1 data verification
- **Issue:** Plan claimed "L0--L2 fail (RUN_FAIL)" but actual data shows L0=BUILD_FAIL (not RUN_FAIL). Also L4 is BUILD_FAIL (not RUN_FAIL as plan stated).
- **Fix:** Used actual failure categories from result JSONs in the paper text.
- **Files modified:** docs/paper/latex/paper.tex
- **Commit:** 261087d

## Issues Encountered

None beyond the data accuracy deviations documented above. The plan's CONTEXT.md source had stale/incorrect per-level data for lavamd; verifying against the actual result files on disk (as the critical_traps section warned) caught this before it propagated into the paper.
