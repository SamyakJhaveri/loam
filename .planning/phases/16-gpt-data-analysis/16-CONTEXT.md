# Phase 16: GPT-4.1 Mini Data Analysis & Summary Generation

## Goal
Produce machine-readable analysis files for GPT-4.1 mini that parallel the existing Qwen analysis outputs. This includes regenerating eval_summary with both models, generating paper_data and error taxonomy for GPT, writing a NEW cross_model_comparison.py script (critical path), and regenerating all figures with dual-model data.

## Dependencies
- Phase 15.5 PW-A (figure color fix) must be done before T5
- Phase 15.5 PW-C (analyze_eval.py verification) should be done before T1

## Blocks
- Phase 17 (all paper integration depends on Phase 16 outputs)
- Phase 18 (verification depends on Phase 16 + 17 outputs)

## Source
Master plan: `/home/samyak/.claude/plans/hashed-sauteeing-kite.md`, "Phase 16" section (lines 114-191)

## Key Data
- GPT-4.1 mini results: `results/evaluation/azure-gpt-4.1-mini/` (897 files: 606 primary, 291 pass@k)
- GPT pass rate: 26.6% (161/606) vs Qwen 38.3% (272/710)
- GPT BUILD_FAIL: 56.4% vs Qwen 33.9%
- Coverage gap: GPT missing omp_target-to-cuda direction

## Output Artifacts
1. `results/evaluation/eval_summary.json` — updated with both models
2. `results/analysis/paper_data_gpt41mini.json` — GPT paper stats
3. `results/analysis/error_taxonomy_gpt41mini.json` — GPT error classes
4. `results/analysis/cross_model_comparison.json` — statistical comparison
5. `docs/paper/figures/f3_kernel_model_heatmap.pdf` — dual-model
6. `docs/paper/figures/f4_failure_taxonomy.pdf` — dual-model
7. `docs/paper/figures/f5_pass_at_k_by_direction.pdf` — dual-model
8. `docs/paper/figures/f7_augmentation_robustness.pdf` — dual-model (if GPT cuda-to-omp exists)
