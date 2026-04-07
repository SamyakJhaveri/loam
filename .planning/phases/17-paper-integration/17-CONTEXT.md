# Phase 17: Paper Integration — Dual-Model Results, Comparison & Differentiation

## Goal
Update all paper sections with GPT-4.1 mini data, replace ALL 19 `\pending{}` markers, fill ALL 18 `\tbd{}` table cells, write the new cross-model comparison subsection (Section 6.9), add augmentation degradation examples, and emphasize prompt anonymization as a key differentiator.

## Dependencies
- Phase 16 (all analysis outputs + regenerated figures must exist)
- `cross_model_comparison.json` must exist with chi-squared p-value and Cohen's h before 17B starts

## Blocks
- Phase 18 (verification depends on completed paper edits)

## Source
Master plan: `/home/samyak/.claude/plans/hashed-sauteeing-kite.md`, "Phase 17" section (lines 195-343)

## Critical Corrections (from adversarial review)
1. `\pending{}` count is 19 (NOT 11 as originally estimated)
2. `\tbd{}` count is 18 table cells (NOT 1)
3. lavamd example: L4 is PASS (not omitted)
4. bptree example: L3 is PASS (model partially recovers)
5. Page budget HIGH RISK: 2-3 pages being added vs SC limit of 10

## Key Files
- `docs/paper/latex/paper.tex` — primary edit target
- `results/analysis/paper_data_gpt41mini.json` — GPT numbers source
- `results/analysis/cross_model_comparison.json` — statistical comparison source
- `scripts/evaluation/llm_evaluate.py` — anonymization code to cross-check (line 570)

## Agent Team Strategy (STRONGLY RECOMMENDED)
- Wave 1 (parallel): Subagent A greps paper.tex for exact line numbers; Subagent B compiles PDF and counts pages
- Wave 2 (single agent, sequential): one paper-drafter agent applies ALL edits in document order
- Wave 3 (parallel): figure reference updates + page count audit
