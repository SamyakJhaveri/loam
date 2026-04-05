---
phase: 08-figure-regeneration
plan: 02
subsystem: figure-generation
tags: [matplotlib, figures, paper, T2-table, verification, PDF, PNG]
dependency_graph:
  requires:
    - "08-01: Updated generate_paper_figures.py with 2-model layout and 5-suite coverage"
  provides:
    - "T2 LaTeX table with 2-model layout (Qwen populated + GPT-4.1 mini pending)"
    - "All 10 figure PDFs verified (6 main + 4 appendix)"
    - "All 10 figure PNGs verified alongside PDFs"
    - "Full pipeline run with zero warnings and zero skipped figures"
  affects:
    - "docs/paper/figures/t2_model_comparison.tex"
    - "docs/paper/figures/f2_repo_vs_kernel.{pdf,png}"
    - "docs/paper/figures/f3_kernel_model_heatmap.{pdf,png}"
    - "docs/paper/figures/f4_failure_taxonomy.{pdf,png}"
    - "docs/paper/figures/f5_pass_at_k_by_direction.{pdf,png}"
    - "docs/paper/figures/f6_cross_suite_comparison.{pdf,png}"
    - "docs/paper/figures/f7_augmentation_robustness.{pdf,png}"
    - "docs/paper/figures/c1_repair_transition_matrix.{pdf,png}"
    - "docs/paper/figures/c2_repair_rate_by_direction.{pdf,png}"
    - "docs/paper/figures/c3_transform_frequency.{pdf,png}"
    - "docs/paper/figures/c4_selection_funnel.{pdf,png}"
tech_stack:
  added: []
  patterns:
    - "2-model T2 table: Model | Overall | per-direction columns"
key_files:
  created: []
  modified:
    - "scripts/generate_paper_figures.py"
decisions:
  - "T2 table uses pass/total (rate%) format per cell instead of separate PASS/Total/Rate columns"
  - "GPT-4.1 mini row shows 'pending' text in all 7 cells (overall + 6 directions)"
metrics:
  duration: "2min"
  completed: "2026-04-05"
  tasks_completed: 2
  tasks_total: 2
  files_modified: 1
---

# Phase 08 Plan 02: Figure Generation Pipeline Execution Summary

Restructured T2 LaTeX table to 2-model layout with Qwen 3.5 397B data fully populated (49/138, 35.5% overall) and GPT-4.1 mini showing "pending" across all fields. Ran full figure generation pipeline (`--figure all -v`), verified all 10 PDFs + 10 PNGs + 1 LaTeX table exist and are non-empty with zero warnings.

## Task Results

### Task 1: Restructure T2 LaTeX table for 2-model layout
**Commit:** 2aa1a9c

- Replaced old 3-direction Rodinia-only T2 table (llrrrrrrr format with Direction, Model, PASS, Total, Rate, etc.)
- New table: 2-row layout with 8 columns (Model + Overall + 6 directions)
- Qwen row: 49/138 (35.5%) overall, per-direction: CUDA->OMP 16/26 (61.5%), OMP->CUDA 14/26 (53.8%), CUDA->OCL 4/23 (17.4%), OCL->CUDA 2/23 (8.7%), OMP->OCL 6/20 (30.0%), OCL->OMP 7/20 (35.0%)
- GPT-4.1 mini row: "pending" in all 7 cells

### Task 2: Run full figure generation, verify all outputs
**Commit:** No code changes required -- verification-only task

Full pipeline ran successfully (`--figure all -v`):

**Main body figures:**
- F2: Repo vs Kernel-Level Counts (15.3 KB PDF)
- F3: Per-Kernel Translation Outcomes -- 29 kernels x 6 directions across 5 suites (47.9 KB PDF)
- F4: Failure Taxonomy -- 138 tasks across 6 directions (41.8 KB PDF)
- F5: pass@k by Direction -- 414 sample records (12.8 KB PDF)
- F6: Cross-Suite Comparison -- 5 suites: rodinia 34.5%, xsbench 0%, rsbench 0%, mixbench 33.3%, hecbench 90.0% (13.0 KB PDF)
- F7: Augmentation Robustness -- Qwen L0-L4: 61.5%, 53.8%, 65.4%, 53.8%, 61.5% (11.3 KB PDF)

**Appendix figures:**
- C.1: Self-Repair Transition Matrix -- 4x5, 624 multi-attempt records (18.3 KB PDF)
- C.2: Repair Rate by Direction -- 6 directions, range 4.4%-35.6% (14.1 KB PDF)
- C.3: Transform Frequency Heatmap -- 22 kernels x 5 transforms (86.2 KB PDF)
- C.4: HeCBench Selection Funnel -- 506 -> 60 pipeline (20.6 KB PDF)

**Table:**
- T2: t2_model_comparison.tex -- 2-model layout (400 bytes)

**Verification results:**
- 10/10 PDFs exist and >5KB
- 10/10 PNGs exist alongside PDFs
- T2 LaTeX table exists and >100 bytes
- 0 warnings, 0 skipped figures, 0 errors

## Deviations from Plan

None -- plan executed exactly as written. No rendering issues encountered.

## Known Stubs

None -- all data is live from result JSONs on disk.

## Self-Check: PASSED
