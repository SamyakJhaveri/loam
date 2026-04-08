# Phase 19: GPT-4.1-mini Complete Data Re-Analysis — Context

**Gathered:** 2026-04-08
**Status:** Ready for replanning

<domain>
## Phase Boundary

Regenerate all GPT-4.1-mini analysis files (eval_summary, paper_data_gpt41mini, error_taxonomy, cross_model_comparison) and all paper figures from the corrected 910-file GPT dataset. Stage, commit, and produce reference artifacts for Phase 20.

Phase 19 does NOT edit paper.tex, appendices.tex, or overleaf.tex — that is Phase 20's job.

**Hard prerequisite:** 213 new valid result files are already on disk as untracked files; 200 invalid files are already deleted from the working tree (not yet staged). Phase 19 begins by staging these changes.

</domain>

<decisions>
## Implementation Decisions

### Data Scope (confirmed complete)
- **D-01:** All on-disk changes are intentional and complete. The corrected dataset consists of:
  - **Deleted (200 files):** 168 HeCBench `cuda-to-omp` / `cuda-to-omp_target` + 32 XSBench `cuda-to-omp`, `cuda-to-opencl`, `omp-to-opencl` — all invalid Argonne empty-prompt batch (xsbench-src missing on Argonne machine)
  - **Added (213 untracked):** HeCBench `omp_target-to-cuda` + `omp-to-cuda`, mixbench `omp-to-cuda` + `opencl-to-cuda`, Rodinia `opencl-to-cuda` (backprop, bptree, gaussian, heartwall, hotspot, hotspot3d, hybridsort, kmeans, lavamd, lud, myocyte, nn, nw)
  - **Modified (9 files):** Pre-existing tracked files updated
  - **Net total on disk:** 910 files (was 897)
  - **XSBench net change:** -32 files, no replacement XSBench data added

### Figure Regeneration
- **D-02:** Run `--figure all` — regenerate all 13 figures in one command. Qwen data is unchanged, so Qwen figure outputs will be identical. This is preferred over selective regeneration for simplicity and consistency.

### Phase 20 Structural Changes Artifact
- **D-03:** Phase 19's final task produces `19-STRUCTURAL-CHANGES.md` in the phase directory. This explicitly lists the structural paper edits Phase 20 must make (beyond numeric substitution). This is critical because Phase 17 was written assuming omp_target-to-cuda was absent — now it is present.
  Minimum contents:
  1. Remove/rewrite "omp_target-to-cuda GPT results were unavailable" footnote
  2. Replace cuda-to-omp_target direction row with omp_target-to-cuda row in direction table
  3. Update all cross-model statistics (chi2, p-value, Cohen's h) with new values from cross_model_comparison.json
  4. Update per-direction table rows to match new 7-direction set
  5. Flag any XSBench-specific coverage changes in cross-suite analysis

### Validation Gate
- **D-04:** Full `/validate` before commit — standard 4-wave gate even for data-only commits. Do not bypass.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Current Data State
- `results/evaluation/azure-gpt-4.1-mini/` — 910 files on disk; 213 untracked (new), 200 unstaged deletions, 9 unstaged modifications
- `results/analysis/paper_data_gpt41mini.json` — STALE (generated 2026-04-07, total_on_disk=897); must be regenerated
- `results/analysis/cross_model_comparison.json` — STALE (generated 2026-04-07, chi2=10.97, h=0.19); must be regenerated
- `results/analysis/error_taxonomy.json` — STALE; must be regenerated
- `results/evaluation/eval_summary.json` — STALE; must be regenerated

### Existing Plan
- `.planning/phases/19-gpt-final-data-refresh/19-01-PLAN.md` — 5-task execution plan (Task 1: stage, T2: analysis pipeline, T3: figures, T4: print numbers, T5: commit)

### Analysis Scripts (all exist and are ready)
- `scripts/analysis/cross_model_comparison.py` — EXISTS (created in Phase 16)
- `scripts/analysis/generate_paper_data.py`
- `scripts/analysis/build_error_taxonomy.py`
- `scripts/evaluation/analyze_eval.py`
- `scripts/generate_paper_figures.py`

### Prior Phase Context (for impact awareness)
- `.planning/phases/16-gpt-data-analysis/16-CONTEXT.md` — D-03/D-04 define cross_model_comparison.py outputs (four-way kernel matrix, chi2, Cohen's h)
- `.planning/phases/17-paper-integration/17-CONTEXT.md` — D-02 (7-direction footnote now stale), D-08 (Section 6.9 statistics), D-09 (per-model figure split)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/evaluation/analyze_eval.py` — auto-discovers models from `results/evaluation/`; reads all result JSONs including new omp_target-to-cuda files without modification
- `scripts/analysis/generate_paper_data.py` — uses `source_spec.rsplit("-",1)[-1]` direction inference; handles HeCBench omp_target-to-cuda files correctly
- `scripts/analysis/cross_model_comparison.py` — reads paper_data.json (Qwen) and paper_data_gpt41mini.json (GPT); computes chi2, Cohen's h, four-way kernel matrix

### Critical Direction Change
- **Old GPT directions (7):** cuda-to-omp, cuda-to-opencl, omp-to-cuda, opencl-to-cuda, omp-to-opencl, opencl-to-omp, **cuda-to-omp_target**
- **New GPT directions (7):** cuda-to-omp, cuda-to-opencl, omp-to-cuda, opencl-to-cuda, omp-to-opencl, opencl-to-omp, **omp_target-to-cuda**
- The direction SET changed even though the count stays at 7. Phase 17's D-02-upgrade condition ("if omp_target-to-cuda arrives") is now satisfied retroactively.

### XSBench Coverage Impact
- 32 XSBench files deleted; 0 XSBench files added
- XSBench directions affected: those where XSBench was the SOURCE (required xsbench-src which was absent on Argonne)
- After Phase 19, GPT XSBench data will only include directions where XSBench is the TARGET (if any remain)

### Figure Files Post Phase 16-04 (check exist before regenerating)
- `docs/paper/figures/f3_kernel_model_heatmap_qwen.pdf` (main body)
- `docs/paper/figures/f3_kernel_model_heatmap_gpt.pdf` (appendix)
- `docs/paper/figures/f4_failure_taxonomy_qwen.pdf`
- `docs/paper/figures/f4_failure_taxonomy_gpt.pdf`
- `docs/paper/figures/f5_pass_at_k_by_direction_qwen.pdf`
- `docs/paper/figures/f5_pass_at_k_by_direction_gpt.pdf`
- `docs/paper/figures/f6_cross_suite_comparison_qwen.pdf`
- `docs/paper/figures/f6_cross_suite_comparison_gpt.pdf`
- `docs/paper/figures/f7_augmentation_robustness.pdf` (unified dual-model)

### Integration Points
- `results/evaluation/eval_summary.json` — must contain both model keys after T1
- `results/analysis/paper_data_gpt41mini.json` — primary Phase 20 number source
- `results/analysis/cross_model_comparison.json` — Section 6.9 statistics source for Phase 20

</code_context>

<specifics>
## Specific Ideas

- Task 4 should produce TWO outputs: (1) terminal print of all numeric values for reference, AND (2) a saved `19-NUMBERS.md` file listing all key numbers with their JSON paths — so Phase 20 executor can read the file without re-running scripts.
- Task 5 (commit) must include both the staged GPT results AND the analysis files AND figures in a single `data(19):` commit.
- `19-STRUCTURAL-CHANGES.md` must list exact paper locations (section, line range approximation) for each structural edit, not just a description of changes.

</specifics>

<deferred>
## Deferred Ideas

- Re-running XSBench GPT evals (valid, locally) to restore the deleted 32 files — not needed before submission, and eval runs take hours. Note for post-submission work.
- Per-kernel agreement matrix as a heatmap figure — JSON output only for now (Phase 17 decision).
- Page budget compression — deferred to Samyak + Le manual edit (Phase 17 D-05-compress).

</deferred>

---

*Phase: 19-gpt-final-data-refresh*
*Context gathered: 2026-04-08*
