# Phase 13: Paper.tex Figure & Table Wiring

**Type:** Gap Closure
**Created:** 2026-04-05 from v1.0 milestone audit
**Closes:** 4 integration gaps, 2 E2E flow breaks, AUG-04 partial

## Problem

Phase 8 regenerated all figures and Phase 3 produced augmentation figures, but paper.tex
was never updated to reference the new outputs:

1. **F6 filename changed:** `f6_xsbench_comparison.pdf` → `f6_cross_suite_comparison.pdf` (paper.tex line ~977)
2. **F3 redesigned:** Triple-panel → single-panel 29-kernel x 6-direction heatmap (paper.tex line ~812)
3. **Aug figures orphaned:** `aug_heatmap.pdf` (37KB) and `aug_trend.pdf` (18KB) exist but no `\includegraphics`
4. **T2 table orphaned:** `t2_model_comparison.tex` exists but no `\input`

## Files to Modify

- `docs/paper/latex/paper.tex` — all 4 fixes are in this file

## Verification

After edits, `pdflatex paper.tex` should compile without missing figure/table warnings.
