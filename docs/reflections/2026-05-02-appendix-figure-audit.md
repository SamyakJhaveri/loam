# Reflection: Appendix Figure Audit

**Date:** 2026-05-02
**Session work:** Audited Appendix H/I figure data accuracy, fixed captions/prose, created Qwen kernel heatmap, ran Codex cross-review
**Files touched:** 2 files modified + 1 new tikz figure in `docs/paper/NeurIPS_ready_version/`

## What Surprised Me

- **The F4 figures use first-sample (s0) data, not all records.** The `get_canonical_l0()` function in `generate_paper_figures.py` (line 412-424) returns only `sample_id=0` when records are marked `is_sample=True`. This means "per-kernel status heatmaps" and "failure taxonomy" figures show 1/3 of the actual data. The captions never stated this — creating a silent discrepancy where the main body says "822 records" but the figure shows 136 first-sample outcomes.

- **Qwen and GPT F4 figures use different direction scopes.** Qwen F4 shows 6 standard directions (137 tasks), GPT/Codex F4 shows 8 directions including case-study pairs (136 tasks). The count difference (137 vs 136) comes from KNOWN_FAIL pre-exclusion differences, not a data error. But this was never documented — a reviewer comparing matched figures would flag it as an inconsistency.

- **The "46% linker error" stat exists only in the JSON, not in the paper.** The `quantitative_findings_azure-gpt-5.4.json` has a full BUILD_FAIL subcategory breakdown (linker_error: 57/123 = 46.3%) but this number appears nowhere in the paper text or tables. Attempting to cite it in a caption would create an ungrounded claim.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (add to "Key Build/Run Rules" section)

```
## Figure Data Source Convention

All per-kernel heatmaps (F3) and failure taxonomy figures (F4) use L0 first-sample
(s0) data via `generate_paper_figures.py::get_canonical_l0()`. This is NOT the same
as the per-record pass rates reported in tables (which use all 3 samples + ablation).

When writing captions referencing these figures:
- Always specify "L0, first sample per task" in the caption
- Do NOT say "across N records" (implies all records are visualized)
- Cross-references from the main body should say "taxonomy" without record counts
```

**Why:** This session discovered the mismatch because the main body caption said "822 records" while the figure showed 136 task outcomes. Without this documented, any future figure caption edit will re-introduce the ambiguity. The `get_canonical_l0()` function's fallback-to-s0 behavior is non-obvious and not documented anywhere except the code itself.

## Prompt Improvement

**Original approach:** "find out if everything is accurate and written as per the writing style of the main body"

**Better approach:** Specify the exact verification axes upfront to avoid a broad sweep:

```
Audit Appendix H for:
1. Data accuracy: verify figure values against results/analysis/quantitative_findings_azure-gpt-5.4.json
2. Caption scope: does each caption specify L0/all-records, per-task/per-record, which directions?
3. Cross-references: do all \ref{} targets exist and point both ways?
4. Aggregation method: what does generate_paper_figures.py::get_canonical_l0() actually select?
5. Scope consistency with Qwen F4 in main body (same number of directions? same task count?)
```

This would have saved ~15 minutes of exploration discovering the s0-only aggregation method by trial and error.

## Gotcha Discovered

**Symptom:** GPT-5.4 F4 figure "pass" counts (21/24 for CUDA→OMP) don't match the per-record pass rate (60/72 = 83.3% → expected ~20/24) or the macro pass@3 rate (91.7% → expected ~22/24).

**Root cause:** `generate_paper_figures.py::get_canonical_l0()` returns ONLY `sample_id=0` records. The figure shows each task's s0 outcome, not a multi-sample aggregate. The value 21/24 = 87.5% is the actual s0 micro-average for that direction, which happens to fall between pass@1 (83.3%) and pass@3 (91.7%) by coincidence.

**Fix:** Document the aggregation convention in captions. Verify figures against s0 files only (`*-s0.json`), not against the full pass_rate computed from all 3 samples.

**Status:** NEW GOTCHA — not yet documented. Should be added to active-gotchas.md or a new paper-conventions rule file.
