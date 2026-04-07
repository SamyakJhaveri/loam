# Phase 18: Cross-Model Verification Sprint

## Goal
Verify every data claim in the updated paper against on-disk result files. This is the final quality gate before commit and submission. Every number, percentage, statistical claim, and example in paper.tex must be traceable to actual result JSONs.

## Dependencies
- Phase 16 (analysis outputs must exist)
- Phase 17 (paper edits must be complete)

## Blocks
- Final commit (`.validation_passed` sentinel required)
- Paper submission (April 8, 2026 deadline)

## Source
Master plan: `/home/samyak/.claude/plans/hashed-sauteeing-kite.md`, "Phase 18" section (lines 346-390)

## Verification Scope
1. GPT table numbers vs paper_data_gpt41mini.json
2. Statistical claims (chi-squared, Wilson CIs, Cohen's h) reproducible from cross_model_comparison.json
3. Prose claims match data (percentages, rankings, BUILD_FAIL framing)
4. Augmentation examples match actual result JSONs (lavamd L4=PASS, bptree L3=PASS)
5. Anonymization description matches actual code in llm_evaluate.py
6. Figure data visible (GPT color #56B4E9, not grey)
7. Zero remaining \pending{} and \tbd{} markers
8. Table edge cases (missing direction footnote, aggregate formula)
9. Full /validate loop passes
10. LaTeX compiles clean, page count ≤ 10
