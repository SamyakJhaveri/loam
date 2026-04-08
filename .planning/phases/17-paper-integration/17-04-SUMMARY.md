---
phase: 17-paper-integration
plan: "04"
status: complete
subsystem: paper-tex
tags: [per-model-figures, dual-model, appendix-gpt, captions, cross-references]
dependency_graph:
  requires: [17-03-SUMMARY.md, f3/f4/f5/f6 Qwen and GPT PDFs]
  provides: [paper.tex with F5/F6 Qwen figures and updated F3/F4 captions, appendices.tex GPT figures section]
  affects: []
tech_stack:
  added: []
  patterns: [per-model-caption-annotation, appendix-cross-reference]
key_files:
  created: []
  modified: [docs/paper/latex/paper.tex, docs/paper/latex/appendices.tex]
decisions:
  - Kept existing appendix F5/F6 Qwen figures (fig:pass-at-k, fig:cross-suite labels) alongside new main-body F5/F6 (fig:f5-qwen, fig:f6-qwen labels) to avoid breaking existing cross-references
  - Replaced 'single-model' with 'per-model' in McNemar direction asymmetry text to eliminate stale framing
metrics:
  duration_seconds: 148
  completed: "2026-04-08T00:36:31Z"
  task_count: 3
  file_count: 2
---

# Phase 17 Plan 04: Per-Model Figure Wiring Summary

Wired per-model figures into paper.tex (Qwen F3/F4 caption updates, F5/F6 Qwen added to main body) and appendices.tex (new GPT-4.1 Mini Figures section with F3/F4/F5/F6 GPT variants). All 8 figure PDFs verified on disk. Full validation passes.

## Summary

Three tasks completed:

1. **F3/F4 caption updates + F5/F6 Qwen main body figures** -- Updated F3 and F4 captions to include "(Qwen 3.5 397B)" and cross-references to GPT appendix figures. Added F5 (pass@k by direction) and F6 (cross-suite comparison) as new figure environments in the pass@k analysis section of paper.tex.

2. **GPT-4.1 Mini Figures appendix section** -- Created new appendix section with all 4 GPT figure variants (F3/F4/F5/F6), each with "(GPT-4.1 mini)" in captions and cross-references back to main-body Qwen figures using correct labels (fig:kernel-heatmap, fig:failure-taxonomy, fig:f5-qwen, fig:f6-qwen).

3. **Final validation** -- Full Phase 17 validation passes: pending=1 (expected), tbd=0, paper.tex balanced (28/28), appendices.tex diff=1 (expected), all 9 figure PDFs exist, no stale single-model text.

## Changes Made

### Task 1: paper.tex (commit 103cf88)

- F3 caption (`fig:kernel-heatmap`): Added "(Qwen 3.5 397B)" and "GPT-4.1 mini results in Appendix Figure ref{fig:f3-gpt}"
- F4 caption (`fig:failure-taxonomy`): Added "(Qwen 3.5 397B)" and "GPT-4.1 mini results in Appendix Figure ref{fig:f4-gpt}"
- F5 figure environment added after pass@k curve reference (label: `fig:f5-qwen`)
- F6 figure environment added after cross-suite reference (label: `fig:f6-qwen`)
- Figure count: 3 -> 5 (+2)
- Environment balance: 26/26 -> 28/28 (balanced)

### Task 2: appendices.tex (commit c80c57f)

- New section "GPT-4.1 Mini Per-Model Figures" inserted before "Evaluation Cost Summary"
- 4 figure environments: fig:f3-gpt, fig:f4-gpt, fig:f5-gpt, fig:f6-gpt
- Each caption includes "(GPT-4.1 mini)" and cross-references the main-body Qwen figure
- Environment balance: 69/68 -> 73/72 (diff=1, correct)

### Task 3: paper.tex (commit e8c099f)

- Replaced "single-model sample size" with "per-model sample size" in McNemar direction asymmetry analysis

## Verification Results

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| pending count | 1 | 1 | PASS |
| tbd count | 0 | 0 | PASS |
| paper.tex begin/end | balanced | 28/28 | PASS |
| appendices.tex diff | 1 | 1 | PASS |
| F3 Qwen in paper.tex | >= 1 | 1 | PASS |
| F4 Qwen in paper.tex | >= 1 | 1 | PASS |
| F5 Qwen in paper.tex | >= 1 | 1 | PASS |
| F6 Qwen in paper.tex | >= 1 | 1 | PASS |
| F3 GPT in appendices.tex | >= 1 | 1 | PASS |
| F4 GPT in appendices.tex | >= 1 | 1 | PASS |
| F5 GPT in appendices.tex | >= 1 | 1 | PASS |
| F6 GPT in appendices.tex | >= 1 | 1 | PASS |
| Qwen 397B in captions | >= 4 | 5 | PASS |
| GPT-4.1 mini in captions | >= 4 | 7 | PASS |
| All 9 figure PDFs exist | 9 | 9 | PASS |
| Stale single-model text | 0 content | 0 content (1 comment) | PASS |
| Source comments | >= 20 | 51 | PASS |
| Section 6.9 present | 1 | 1 | PASS |
| lavamd/bptree present | >= 1 | 13 | PASS |
| Prompt Anonymization present | 1 | 1 | PASS |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Replaced stale 'single-model' phrasing**
- **Found during:** Task 3 validation
- **Issue:** Line 983 contained "single-model sample size" in the McNemar direction asymmetry analysis, which is stale given the dual-model paper framing.
- **Fix:** Changed to "per-model sample size" which is technically accurate (McNemar tests are run per-model).
- **Files modified:** docs/paper/latex/paper.tex
- **Commit:** e8c099f

## Issues Encountered

None beyond the minor stale text fix documented above.
