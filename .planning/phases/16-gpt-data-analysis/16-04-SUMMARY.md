---
phase: 16-gpt-data-analysis
plan: "04"
subsystem: paper-figures
tags: [figures, dual-model, gpt, qwen, coverage-gaps, latex]
dependency_graph:
  requires: [16-02, 16-03]
  provides: [per-model-figures, coverage-gaps-doc]
  affects: [docs/paper/figures/, docs/paper/latex/, results/analysis/]
tech_stack:
  added: []
  patterns: [per-model-figure-split, _qwen/_gpt-suffix-convention]
key_files:
  created:
    - docs/paper/figures/f3_kernel_model_heatmap_qwen.pdf
    - docs/paper/figures/f3_kernel_model_heatmap_gpt.pdf
    - docs/paper/figures/f4_failure_taxonomy_qwen.pdf
    - docs/paper/figures/f4_failure_taxonomy_gpt.pdf
    - docs/paper/figures/f5_pass_at_k_by_direction_qwen.pdf
    - docs/paper/figures/f5_pass_at_k_by_direction_gpt.pdf
    - docs/paper/figures/f6_cross_suite_comparison_qwen.pdf
    - docs/paper/figures/f6_cross_suite_comparison_gpt.pdf
    - results/analysis/coverage_gaps.md
    - docs/paper/latex/overleaf.tex
  modified:
    - scripts/generate_paper_figures.py
    - scripts/evaluation/test_generate_paper_figures.py
    - docs/paper/latex/paper.tex
    - docs/paper/latex/appendices.tex
  deleted:
    - docs/paper/figures/f3_kernel_model_heatmap.pdf
    - docs/paper/figures/f4_failure_taxonomy.pdf
    - docs/paper/figures/f5_pass_at_k_by_direction.pdf
    - docs/paper/figures/f6_cross_suite_comparison.pdf
    - docs/paper/latex/overleaf_main.tex
decisions:
  - "Per-model figure split (separate _qwen/_gpt PDF per figure) rather than combined dual-model figures"
  - "LaTeX paper.tex and appendices.tex reference _qwen variants as primary paper figures"
  - "_directions_for_model removed as dead code; tests use list(ALL_DIRECTIONS) directly"
metrics:
  duration_minutes: ~30
  completed_date: "2026-04-07"
  tasks_completed: 3
  files_changed: 29
---

# Phase 16 Plan 04: Per-Model Figures and Coverage Gap Documentation Summary

Per-model figure split (f3/f4/f5/f6 each into _qwen + _gpt PDF variants), LaTeX reference fixes in paper.tex and appendices.tex, dead code removal from generate_paper_figures.py, and GPT omp_target-to-cuda coverage gap documentation in results/analysis/coverage_gaps.md.

## What Was Done

### Task 1 — Figure Verification (T5)

Verified all 8 per-model figures (generated in prior session at Apr 7 14:21) are present and well-sized:

| Figure | _qwen size | _gpt size |
|--------|-----------|-----------|
| f3_kernel_model_heatmap | 57,090 bytes | 56,822 bytes |
| f4_failure_taxonomy | 43,853 bytes | 43,568 bytes |
| f5_pass_at_k_by_direction | 15,114 bytes | 15,444 bytes |
| f6_cross_suite_comparison | 22,277 bytes | 21,303 bytes |

T2 model comparison table verified: GPT-4.1 mini row has real numbers (`32/117 (27.4%)`), no "pending" cells.

F7 augmentation robustness (already committed at d80e628): dual-model lines (orange=Qwen, sky blue=GPT) with Wilson CI error bars.

### Task 2 — Human Visual Checkpoint (BLOCKING GATE)

User visually approved:
- T2 table GPT row: `32/117 (27.4%)` overall, `9/26 (34.6%)` cuda-to-omp, `3/22 (13.6%)` omp-to-cuda
- Per-model figure split decision confirmed
- F7 dual-model augmentation figure confirmed

### Task 3 — Coverage Gap Documentation (T6)

Created `results/analysis/coverage_gaps.md` documenting:
- 7 of 8 translation directions covered in cross-model comparison
- GPT-4.1 mini missing `omp_target-to-cuda` direction
- Per-kernel agreement: 13 both-pass, 5 both-fail, 11 Qwen-only, 2 GPT-only (31 common kernels)
- Paper-ready footnote text for Section 6.9
- "---" placeholder convention for GPT omp_target-to-cuda cells in per-direction tables

### Additional Work (committed together)

- `paper.tex` and `appendices.tex`: fixed `\includegraphics` references from old combined names to `_qwen` suffixed variants
- `overleaf.tex`: rename of `overleaf_main.tex` with same _qwen fixes applied
- `generate_paper_figures.py`: removed `_directions_for_model` dead code
- `test_generate_paper_figures.py`: updated to use `list(ALL_DIRECTIONS)` directly

## Decisions Made

**D-1: Per-model figure split over combined figures.**
F3/F4/F5/F6 each produce `_qwen` and `_gpt` variants rather than a single combined figure. Decision made in prior session (commit dab1069). Rationale: heatmaps and failure taxonomies are cleaner per-model; direct comparison is served by T2 table and F7.

**D-2: Paper LaTeX references _qwen as primary.**
`paper.tex` and `appendices.tex` use `_qwen` variants as the displayed figures. GPT variants exist on disk for supplemental use or side-by-side if needed. This preserves the paper's focus on the complete Qwen dataset while GPT data is introduced in the comparison section.

**D-3: _directions_for_model removed as dead code.**
The helper was introduced during the per-model split implementation but became unnecessary once `ALL_DIRECTIONS` was used as the canonical source. Removing it avoids confusion about which direction set governs figure generation.

## Key Artifacts for Phase 17

Phase 17 (paper-integration) will need:

| Artifact | Path | Use |
|----------|------|-----|
| Coverage gaps doc | `results/analysis/coverage_gaps.md` | Section 6.9 footnote, "---" cell guidance |
| T2 table | `docs/paper/figures/t2_model_comparison.tex` | Direct `\input{}` in paper |
| Per-model figures | `docs/paper/figures/f{3,4,5,6}_*_{qwen,gpt}.pdf` | `\includegraphics` in paper/appendix |
| F7 augmentation | `docs/paper/figures/f7_augmentation_robustness.pdf` | Section 6.8 figure |
| Footnote text | See coverage_gaps.md § Impact on Paper | Insert verbatim in Section 6.9 |

## Deviations from Plan

**1. [Rule 2 - Missing Critical] LaTeX includegraphics references not updated in plan**
- Found during: post-commit review / user instruction
- Issue: paper.tex and appendices.tex still referenced old combined figure filenames after per-model split
- Fix: Updated `\includegraphics` calls in paper.tex (f3/f4) and appendices.tex (f5/f6) to use `_qwen` suffix
- Files modified: `docs/paper/latex/paper.tex`, `docs/paper/latex/appendices.tex`, `docs/paper/latex/overleaf.tex`
- Commit: 46bb67e

**2. [Rule 1 - Bug] _directions_for_model dead code removed**
- Found during: user instruction (validation pass surfaced it)
- Issue: `_directions_for_model` helper in generate_paper_figures.py became unreachable after per-model split refactor
- Fix: Removed function; test updated to use `list(ALL_DIRECTIONS)` directly
- Files modified: `scripts/generate_paper_figures.py`, `scripts/evaluation/test_generate_paper_figures.py`
- Commit: 46bb67e

## Commit Log

| Hash | Description |
|------|-------------|
| 46bb67e | feat(16-04): per-model figures, LaTeX ref fixes, dead code removal, coverage gaps |

(F7 and T2 were committed earlier at d80e628 and b269fbd respectively as part of wave 3 work.)

## Self-Check: PASSED

- `docs/paper/figures/f3_kernel_model_heatmap_qwen.pdf` — FOUND (57,090 bytes)
- `docs/paper/figures/f3_kernel_model_heatmap_gpt.pdf` — FOUND (56,822 bytes)
- `docs/paper/figures/f4_failure_taxonomy_qwen.pdf` — FOUND (43,853 bytes)
- `docs/paper/figures/f4_failure_taxonomy_gpt.pdf` — FOUND (43,568 bytes)
- `docs/paper/figures/f5_pass_at_k_by_direction_qwen.pdf` — FOUND
- `docs/paper/figures/f5_pass_at_k_by_direction_gpt.pdf` — FOUND
- `docs/paper/figures/f6_cross_suite_comparison_qwen.pdf` — FOUND
- `docs/paper/figures/f6_cross_suite_comparison_gpt.pdf` — FOUND
- `results/analysis/coverage_gaps.md` — FOUND (42 lines)
- `docs/paper/figures/t2_model_comparison.tex` — FOUND (GPT row: 32/117 (27.4%))
- `docs/paper/figures/f7_augmentation_robustness.pdf` — FOUND (committed d80e628)
- Commit 46bb67e — FOUND
