# Phase 12: Fix Stale Pass@k Values in Paper.tex

**Type:** Gap Closure (BLOCKER)
**Created:** 2026-04-05 from v1.0 milestone audit
**Closes:** VERIFY-01 regression

## Problem

Phase 1 Plan 05 regenerated `paper_data.json` with `--suite rodinia` AFTER Plans 01-04 verified
Sections 1-5 against older data. This created 8+ stale pass@k values in paper.tex Sections 6.7-6.8:

- Task count: 426 → 288
- Pair count: 142 → 96
- Macro pass@1: 19.7% → 15.3%
- Additional pass@k values and aggregate rates

## Ground Truth

- `results/analysis/paper_data_rodinia.json` (Phase 7 regenerated)
- `results/analysis/paper_data.json` (full 1,248-task dataset)

## Scope

Only paper.tex Sections 6.6-6.8 (pass@k, per-kernel tiers, statistical analysis).
Earlier sections (1-5) were verified before the regression was introduced.
