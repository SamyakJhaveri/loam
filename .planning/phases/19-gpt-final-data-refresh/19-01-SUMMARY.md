---
phase: 19-gpt-final-data-refresh
plan: "01"
subsystem: data-analysis
tags: [gpt-4.1-mini, analysis-pipeline, figures, data-refresh]
dependency_graph:
  requires: []
  provides: [paper_data_gpt41mini.json, cross_model_comparison.json, eval_summary.json, error_taxonomy.json, 19-NUMBERS.md, 19-STRUCTURAL-CHANGES.md]
  affects: [paper.tex, overleaf.tex, appendices.tex]
tech_stack:
  added: []
  patterns: [sequential-pipeline-execution, cross-model-comparison]
key_files:
  created:
    - .planning/phases/19-gpt-final-data-refresh/19-NUMBERS.md
    - .planning/phases/19-gpt-final-data-refresh/19-STRUCTURAL-CHANGES.md
  modified:
    - results/evaluation/azure-gpt-4.1-mini/ (200 deleted, 213 added, 9 modified)
    - results/evaluation/eval_summary.json
    - results/evaluation/eval_summary.md
    - results/analysis/paper_data_gpt41mini.json
    - results/analysis/error_taxonomy.json
    - results/analysis/error_taxonomy.md
    - results/analysis/cross_model_comparison.json
    - docs/paper/figures/ (14 PDFs + 14 PNGs + 1 .tex regenerated)
decisions:
  - "D-01: Direction set change confirmed -- 7 common directions (not 6 as predicted). cuda-to-omp_target is Qwen-only; omp_target-to-cuda is common to both."
  - "D-02: All 14 figure PDFs regenerated via --figure all. T2 outputs .tex. All fresh."
  - "D-03: 19-STRUCTURAL-CHANGES.md produced with 9 structural edits and paper.tex line references."
metrics:
  duration: 302s
  completed: "2026-04-08T22:59:00Z"
  tasks_completed: 3
  tasks_total: 3
  files_changed: 461
---

# Phase 19 Plan 01: GPT-4.1-mini Complete Data Re-Analysis Summary

Regenerated all GPT analysis files and paper figures from corrected 910-file dataset; GPT pass rate improved from 29.2% to 31.8% (177/557), cross-model chi2 dropped from 10.97 to 5.54 (p=0.019), Cohen's h from 0.19 to 0.14, and produced 19-NUMBERS.md + 19-STRUCTURAL-CHANGES.md for Phase 20.

## Task Completion

| Task | Name | Status | Key Outputs |
|------|------|--------|-------------|
| 1 | Stage result files and run analysis pipeline | Done | 910 files staged; eval_summary, paper_data_gpt41mini, error_taxonomy, cross_model_comparison regenerated |
| 2 | Regenerate figures and produce Phase 20 reference artifacts | Done | 14 PDFs + 14 PNGs fresh; 19-NUMBERS.md (all values + JSON paths); 19-STRUCTURAL-CHANGES.md (9 structural edits) |
| 3 | Stage analysis files, figures, and planning artifacts | Done (staging only) | 461 files staged; commit deferred to orchestrator |

## Key Numbers (Post-Regeneration)

### GPT-4.1 mini Primary Campaign
- Total tasks: 557 (was 551)
- PASS: 177 (was 161)
- Pass rate: 31.8% [28.1%, 35.8%] (was 29.2% [25.6%, 33.2%])
- BUILD_FAIL: 247 / 44.3% of tasks (was 316 / 57.4%)
- VERIFY_FAIL: 79 / 14.2% (was 31 / 5.6%)
- RUN_FAIL: 54 / 9.7% (was 43 / 7.8%)

### Cross-Model Comparison
- Chi-squared: 5.54 (was 10.97)
- p-value: 0.019 (was 0.000926) -- still significant at alpha=0.05
- Cohen's h: 0.14 (was 0.19) -- negligible
- Common directions: 7 (was 7, but the SET changed)
- Missing GPT direction: cuda-to-omp_target (was omp_target-to-cuda)

### Per-Kernel Agreement
- Common kernels: 29 (was 31)
- Both pass: 18 (was 13) -- 5 kernels moved from qwen-only to both-pass
- Both fail: 4 (was 5)
- Qwen only: 6 (was 11)
- GPT only: 1 (was 2)

### Combined
- Total: 1,267 tasks (was 1,261)
- PASS: 449 (was 433)
- Rate: 35.4% (was 34.3%)

## Deviations from Plan

### Deviation 1: 7 Common Directions, Not 6
The RESEARCH.md predicted 6 common cross-model directions after the data refresh. Actual result: 7 common directions. This happened because Qwen has omp_target-to-cuda data (from Phase 16 HeCBench evaluations), so omp_target-to-cuda is shared between both models. Only cuda-to-omp_target is Qwen-exclusive. The 19-STRUCTURAL-CHANGES.md was written with the correct 7-direction values.

### Deviation 2: Pass@k fields missing hard_fail/noisy/always_pass
The pass@k section of 19-NUMBERS.md shows `None` for hard_fail, noisy, always_pass fields. These were not produced by the pass@k analysis for GPT. This is informational only and does not affect Phase 20 paper updates (these fields are not referenced in paper.tex).

## Verification Results

### Task 1 Verification
- total_on_disk=910 (>= 900): PASS
- cuda-to-omp_target absent from by_direction: PASS
- omp_target-to-cuda present in by_direction: PASS
- chi2=5.5396 (differs from stale 10.97): PASS

### Task 2 Verification
- All 14 figure PDFs FRESH (mtime within last hour): PASS
- 19-NUMBERS.md exists and non-empty: PASS
- 19-STRUCTURAL-CHANGES.md has 9 structural items (>= 5): PASS

## Known Stubs

None -- all analysis files contain real data from the corrected 910-file dataset. No placeholder values or mock data.

## Threat Flags

None -- no new network endpoints, auth paths, or file access patterns introduced. All scripts are existing, previously-verified analysis tools.
