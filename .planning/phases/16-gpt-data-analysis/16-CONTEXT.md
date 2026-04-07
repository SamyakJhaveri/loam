# Phase 16: GPT-4.1 Mini Data Analysis & Summary Generation — Context

**Gathered:** 2026-04-07
**Status:** BLOCKED — waiting for Le's omp_target-to-cuda GPT results. Fallback: proceed with 7 directions if data not available by end of day April 7.

<domain>
## Phase Boundary

Produce all machine-readable analysis artifacts that Phase 17 needs to fill 19 `\pending{}` markers and 18 `\tbd{}` table cells. This includes: regenerating eval_summary with both models, generating paper_data and error_taxonomy for GPT, writing the new cross_model_comparison.py script (critical path for Section 6.9), and regenerating all figures with dual-model data.

Phase 16 does NOT write any paper.tex — that is Phase 17's job.

</domain>

<decisions>
## Implementation Decisions

### Execution Scope
- **D-01:** Full run, no deferrals. All T1-T6 as planned. No tasks skipped even under deadline pressure.

### Figure Regeneration
- **D-02:** Run `--figure all` — regenerate all 13 figures in one command. Accept small style-drift risk from matplotlib version. F7 was already refactored in Phase 15.5 (dual-model with Wilson CI); T5 will update it with real GPT data.

### cross_model_comparison.py Statistics
- **D-03:** Full statistics suite — all four outputs required:
  1. Chi-squared test on 2×2 contingency table (model × pass/fail)
  2. Per-direction paired comparison for 7 **common** directions only (GPT missing omp_target-to-cuda)
  3. Cohen's h effect sizes (overall + per-direction)
  4. Per-kernel agreement matrix — **four-way granularity**: both-pass / both-fail / Qwen-only-pass / GPT-only-pass
- **D-04:** Four-way kernel matrix (not binary). Enables Section 6.9 narrative about which kernels diverge and which model performs better.

### Coverage Gap
- **D-05:** Phase 16 is currently BLOCKED on Le's `omp_target-to-cuda` GPT evaluation data. Zero files exist for this direction in `results/evaluation/azure-gpt-4.1-mini/`. Contact Le to run and deliver these results.
- **D-05-fallback:** If Le cannot deliver `omp_target-to-cuda` data by end of day April 7, proceed with 7-direction cross-model comparison. Paper treatment: footnote stating "Cross-model comparison covers 7 of 8 directions; omp_target-to-cuda GPT results unavailable." Do NOT miss the April 8 deadline.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 16 Specification
- `.planning/phases/16-gpt-data-analysis/PLAN.md` — Full task breakdown T1-T6, commands, verification checklist, execution order

### Master Plan
- `/home/samyak/.claude/plans/hashed-sauteeing-kite.md` §Phase 16 (lines 114-191) — original phase specification

### Prior Analysis Scripts (read before writing cross_model_comparison.py)
- `scripts/analysis/generate_paper_data.py` — schema for paper_data.json output; cross_model_comparison.py must read this format
- `scripts/analysis/build_error_taxonomy.py` — error taxonomy schema
- `scripts/evaluation/analyze_eval.py` — how eval_summary.json is structured; cross_model_comparison.py reads this

### Phase 15.5 Completion Evidence
- `.planning/phases/15.5-pre-work-figure-fixes/15.5-01-SUMMARY.md` — PW-A done: GPT color #56B4E9, F7 dual-model refactored
- `.planning/phases/15.5-pre-work-figure-fixes/15.5-02-SUMMARY.md` — PW-C done: analyze_eval.py argparse default fixed

### Paper Integration Target
- `docs/paper/latex/paper.tex` — contains `\pending{}` markers and `\tbd{}` cells that Phase 17 fills using Phase 16 outputs

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/analysis/generate_paper_data.py` — has `--results-dir` CLI arg; handles source_spec/target_spec schema via `rsplit("-", 1)[-1]` — works with GPT result JSONs without modification
- `scripts/analysis/build_error_taxonomy.py` — similar structure; accepts `--results-dir`
- `scripts/evaluation/analyze_eval.py` — auto-discovers model dirs in `results/evaluation/`; argparse default fixed to `azure-gpt-4.1-mini` in Phase 15.5 PW-C
- `scripts/generate_paper_figures.py` — MODEL_COLORS has GPT entry (#56B4E9), GPT table row currently shows "data pending" cells; T5 will fill with real data

### GPT Result Schema
- GPT result JSONs use `source_spec` / `target_spec` fields (not `src_api`/`tgt_api`)
- Direction inferred via: `source_spec.rsplit("-",1)[-1] + "-to-" + target_spec.rsplit("-",1)[-1]`
- All existing analysis scripts handle this correctly — no schema mismatch

### GPT Coverage Confirmed
- 897 files total in `results/evaluation/azure-gpt-4.1-mini/`
- Directions present: cuda-to-omp, cuda-to-opencl, omp-to-cuda, opencl-to-cuda, omp-to-opencl, opencl-to-omp, cuda-to-omp_target
- Direction MISSING: omp_target-to-cuda (0 files) — **BLOCKER**, see D-05

### Integration Points
- `results/evaluation/eval_summary.json` — currently has 1 model key (together-qwen-3.5-397b-a17b only); T1 must add azure-gpt-4.1-mini
- `results/analysis/` — paper_data_gpt41mini.json and cross_model_comparison.json missing (expected). NOTE: `build_error_taxonomy.py` produces a combined `error_taxonomy.json` with both models in `per_model` dict — there is no separate `error_taxonomy_gpt41mini.json` file.

### Execution Order (from PLAN.md)
```
T1 → T2 + T3 (parallel) → T3b gate → T4 + T5 (parallel) → T6
```
Note: T2 and T3 can also run in parallel with T1 since they read raw result JSONs directly.

</code_context>

<specifics>
## Specific Ideas

- cross_model_comparison.py must produce four-way per-kernel matrix (both-pass/both-fail/Qwen-only-pass/GPT-only-pass), not just binary AGREE/DIVERGE
- Phase 17B (Section 6.9) requires chi-squared p-value and Cohen's h from cross_model_comparison.json before it can start — this is the hard gate
- F7 augmentation figure: already dual-model from Phase 15.5 (Qwen data real, GPT shows 26 kernels at L0); T5 will update with real GPT augmentation data if cuda-to-omp_target results exist

</specifics>

<deferred>
## Deferred Ideas

- omp_target-to-cuda direction cross-model comparison — blocked on Le's data; if not available by April 7 EOD, fold into 7-direction fallback with footnote
- Per-kernel matrix visualization (heatmap figure) — may not fit in 10-page IEEE format; leave as JSON output for now, Phase 17 can include if space allows

</deferred>

---

*Phase: 16-gpt-data-analysis*
*Context gathered: 2026-04-07*
