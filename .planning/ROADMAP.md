# Roadmap: ParBench

## Milestones

- **v1.0 SC26 Paper Completion Sprint** — Phases 1-14, shipped 2026-04-06 ([archive](milestones/v1.0-ROADMAP.md))

## Phases

<details>
<summary>v1.0 SC26 Paper Completion Sprint (Phases 1-14) — SHIPPED 2026-04-06</summary>

- [x] Phase 1: Data Verification & Ground Truth (5/5 plans) — completed 2026-04-03
- [x] Phase 2: Benchmark Characterization Data (3/3 plans) — completed 2026-04-03
- [x] Phase 3: Augmentation Analysis & Story (3/3 plans) — completed 2026-04-04
- [x] Phase 4: Methodology & Reviewer Defense (2/2 plans) — completed 2026-04-05
- [x] Phase 5: Introduction, Positioning & Char Table (2/2 plans) — completed 2026-04-05
- ~~Phase 6: RSBench Single-File Re-spec~~ — DROPPED
- [x] Phase 7: Full Analysis Regeneration (2/2 plans) — completed 2026-04-04
- [x] Phase 8: Figure Regeneration (2/2 plans) — completed 2026-04-04
- [x] Phase 9: Objective Quantitative Analysis (3/3 plans) — completed 2026-04-05
- ~~Phase 10: Qualitative Analysis & Research Narrative~~ — DROPPED
- [x] Phase 11: Paper TeX Integration (4/4 plans) — completed 2026-04-06
- [x] Phase 12: Fix Stale Pass@k Values (3/3 plans) — completed 2026-04-06
- [x] Phase 12.1: SC26 Review P0 Quick Fixes (1/1 plan) — completed 2026-04-06
- [x] Phase 13: Paper Figure & Table Wiring (2/2 plans) — completed 2026-04-06
- [x] Phase 14: Verification Backfill & Housekeeping (1/1 plan) — completed 2026-04-06

</details>

### Phase 15: Paper Review Tools & Panel Fixes

**Goal:** Execute 7 SC26 review panel fixes (FIX-2a, FIX-2b, FIX-3, SF-1, SF-3, SF-6, SF-7) and adversarially review the Phases 16-18 GPT integration plan.
**Plans:** 2/2 plans complete

Plans:
- [x] 15-01-PLAN.md — Apply 6 LaTeX paper edits (FIX-2a, FIX-2b, FIX-3, SF-1, SF-3, SF-6)
- [x] 15-02-PLAN.md — Create MIT LICENSE (SF-7) and adversarial review of GPT integration plan

### Phase 15.5: Pre-Work — Figure Fixes & Dependencies

**Goal:** Fix figure generation scripts (GPT color, F7 dual-model), request hardware specs from Niranjan, verify analyze_eval.py multi-model support. Blockers for Phase 16.
**Plans:** 2/2 plans complete

Plans:
- [x] 15.5-01-PLAN.md — GPT color fix in MODEL_COLORS + F7 dual-model refactor with CI bars
- [x] 15.5-02-PLAN.md — Hardware specs email draft + analyze_eval.py --expected-models fix

### Phase 16: GPT-4.1 Mini Data Analysis & Summary Generation

**Goal:** Produce machine-readable analysis files for GPT-4.1 mini (eval_summary, paper_data, error_taxonomy), write cross_model_comparison.py (critical path), regenerate all figures with dual-model data.
**Plans:** 4/4 plans complete

Plans:
- [x] 16-01-PLAN.md — T1+T2+T3: Refresh eval_summary, generate paper_data_gpt41mini.json, refresh error_taxonomy
- [x] 16-02-PLAN.md — Fix T2 table hardcoded GPT "pending" + T3b schema gate validation
- [x] 16-03-PLAN.md — T4: Write cross_model_comparison.py from scratch (critical path for Section 6.9)
- [x] 16-04-PLAN.md — T5+T6: Regenerate all figures with dual-model data + document coverage gaps

### Phase 17: Paper Integration — Dual-Model Results & Differentiation

**Goal:** Update paper.tex with GPT-4.1 mini data: fill 17 `\pending{}` markers (1 kept for hardware specs), 24 `\tbd{}` table cells, write Section 6.9 (cross-model comparison), add augmentation degradation examples, add prompt anonymization subsection, wire per-model figures.
**Plans:** 4/5 plans complete

Plans:
- [x] 17-01-PLAN.md — 17A + 17A-tbd: Fill all pending markers and tbd table cells with GPT data
- [x] 17-02-PLAN.md — 17B: Write Section 6.9 (Cross-Model Comparison) with statistics
- [x] 17-03-PLAN.md — 17C + 17D: Augmentation degradation examples + prompt anonymization subsection
- [x] 17-04-PLAN.md — 17E: Wire per-model figures (Qwen main body, GPT appendix) + final validation

### Phase 18: Cross-Model Verification Sprint

**Goal:** Verify every data claim in the updated paper against on-disk result files. Final quality gate before April 8 submission.
**Plans:** 1 plan (10 tasks in 3 waves)

- [ ] PLAN.md — Wave 1: cite-check (T1-T3), Wave 2: spot-checks (T4-T6), Wave 3: final checks (T7-T10)

### Phase 19: GPT-4.1-mini Complete Data Re-Analysis

**Goal:** Regenerate eval_summary, paper_data_gpt41mini, error_taxonomy, cross_model_comparison, and all paper figures with the corrected/complete GPT dataset. Background: 200 invalid HeCBench cuda-to-omp/omp_target results (Argonne empty-prompt batch) removed; 213 valid local results (omp/omp_target-to-cuda HeCBench + rodinia fixes) added. Structural change: cuda-to-omp_target direction removed, omp_target-to-cuda added.
**Plans:** 1 plan

Plans:
- [ ] 19-01-PLAN.md — Stage GPT result files, run 4 analysis scripts + figure regeneration, produce 19-NUMBERS.md + 19-STRUCTURAL-CHANGES.md, validate and commit

### Phase 20: Final Paper Update (overleaf.tex + appendices.tex + paper.tex)

**Goal:** Update ALL GPT-4.1-mini numbers in overleaf.tex, appendices.tex, and paper.tex to match Phase 19 analysis outputs (re-run with expanded XSBench data). Includes structural updates: cross-model direction table row changes, removal of stale "omp_target unavailable" footnote, rewrite of invalid h=0.86 effect-size discussion. Fold in working-tree methodology edits.
**Plans:** 4/4 plans complete

Plans:
- [x] 20-02-PLAN.md — Re-run Phase 19 analysis pipeline with XSBench data + capture 20-NUMBERS.md
- [x] 20-03-PLAN.md — Update overleaf.tex (all 13 structural changes + numeric) + appendices.tex (4 tables)
- [x] 20-04-PLAN.md — Sync paper.tex + final verification + commit

## Progress

| Milestone | Phases | Plans | Requirements | Status | Shipped |
|-----------|--------|-------|-------------|--------|---------|
| v1.0 SC26 Paper Sprint | 13 (2 dropped, 1 research stub) | 33/33 | 39/39 | Complete | 2026-04-06 |
| GPT Integration & Submission | 7 (15, 15.5, 16, 17, 18, 19, 20) | 4/16 | -- | In Progress | -- |
