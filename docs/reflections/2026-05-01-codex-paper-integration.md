# Reflection: Codex Paper Integration

**Date:** 2026-05-01
**Session work:** Integrated GPT-5.3-codex as third model across entire NeurIPS paper (10 LaTeX files, 1 Python script, 8 new figures)
**Files touched:** 35 files in `docs/paper/NeurIPS_ready_version/`, `scripts/`

## What Surprised Me

- **The T2 table generator used substring matching ("gpt" in model.lower()) that silently merged codex into the GPT-5.4 row.** Adding codex to MODEL_COLORS was necessary but not sufficient — the T2 function had hardcoded Qwen/GPT logic instead of iterating over the model registry. The figure generation script has two patterns: most functions iterate MODEL_COLORS dynamically (F3-F7 worked automatically), but T2 was hardcoded. The substring filter would have produced silently wrong numbers in the published table. Lesson: when adding a model to a figure generation pipeline, check whether each figure function discovers models dynamically or hardcodes them.

- **Per-record rates vs per-kernel rates caused a metric inconsistency in the augmentation table.** The augmentation_per_kernel_matrix JSON reports per-kernel L0 rates (83.3%, n=24 kernels), but the existing table columns use per-record rates (n=72 = 24 kernels x 3 samples). The self-critic caught this — the codex C->OMP L0 cell should have been 76.4% (55/72), not 83.3% (20/24). This is the kind of metric mismatch that looks correct at a glance but would be caught by a reviewer who checks denominators.

- **The Codex review process (GPT-5.4 cross-model check) died silently after 10 minutes of active work.** It ran 40+ verification commands successfully, then the process exited without producing its final report. The job metadata still showed "running" and the log file was capped at 200 lines. This meant we had to reconstruct findings from command logs rather than getting a clean report. The session-critique team was the actual quality gate, not the Codex review.

## Pattern Proposal

**Target:** `.claude/rules/evaluation.md` (append to existing file)

```
## Figure Generation Model Addition Checklist

When adding a new model to `scripts/generate_paper_figures.py`:
1. Add to all 5 model dictionaries (MODEL_COLORS, MODEL_DISPLAY, MODEL_DISPLAY_SHORT, MODEL_LINESTYLE, MODEL_SLUG)
2. Verify that EVERY figure function discovers models from MODEL_COLORS (or equivalent dict) — do NOT assume all functions iterate dynamically
3. Run `--figure all` and verify per-model output files exist for the new model
4. Check `t2_model_comparison.tex` specifically — it was historically hardcoded
5. After generation, verify the T2 table has N rows (one per model in MODEL_COLORS)
```

**Why:** The T2 hardcoding bug would have produced silently wrong per-direction numbers in a published table. The pattern prevents this by requiring explicit verification of each figure function's model-discovery mechanism.

## Prompt Improvement

**Original approach:** The HANDOFF.md provided exact dictionary entries and LaTeX copy-paste blocks for each step, but said "add after the GPT-5.4 entry" without flagging that T2 was structurally different from F3-F7.

**Better approach:** The handoff should have included a pre-implementation diagnostic for the figure script:

```
Before editing generate_paper_figures.py:
1. grep -n "def generate_" scripts/generate_paper_figures.py
2. For each function, check: does it iterate MODEL_COLORS/MODEL_SLUG,
   or does it hardcode model-specific logic?
3. Functions that hardcode need structural changes, not just dict entries.

Known hardcoded functions as of 2026-05-01:
- generate_t2_model_table() — hardcodes Qwen/GPT rows with substring matching
```

This would have caught the T2 issue at planning time rather than during review.

## Gotcha Discovered

**Symptom:** Augmentation table codex C->OMP L0 showed 83.3% (n=24) while all other models' C->OMP L0 cells showed per-record rates with n=72.

**Root cause:** Two different JSON files report "L0 pass rate" with different denominators. `augmentation_per_kernel_matrix_*.json > primary_matrix > aggregate > L0` gives per-kernel rate (20/24 = 83.3%, where 24 = number of CUDA->OMP kernels). `quantitative_findings_*.json > canonical > direction_pass_rates > standard > cuda-to-omp` gives per-record rate (55/72 = 76.4%, where 72 = 24 kernels x 3 samples). The existing Qwen/GPT columns used the per-record source, but the handoff pointed to the per-kernel source for codex.

**Fix:** Use `quantitative_findings_*.json > direction_pass_rates` for L0 in the augmentation table (per-record, n=72), matching the convention of existing columns. Use `augmentation_per_kernel_matrix` only for L1-L4 where single-sample evaluation makes per-kernel and per-record equivalent.

**Status:** NEW GOTCHA — not yet documented. Consider adding to known-issues.md or a paper-writing conventions doc.
