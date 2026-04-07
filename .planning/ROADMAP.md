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

**Goal:** Update paper.tex with GPT-4.1 mini data: fill 19 `\pending{}` markers, 18 `\tbd{}` table cells, write Section 6.9 (cross-model comparison), add augmentation degradation examples, emphasize prompt anonymization.
**Plans:** 1 plan (5 sub-tasks: 17A-17E + page budget audit)

- [ ] PLAN.md — 17A: fill pending, 17A-tbd: fill tbd, 17B: Section 6.9, 17C: augmentation evidence, 17D: anonymization, 17E: figures

### Phase 18: Cross-Model Verification Sprint

**Goal:** Verify every data claim in the updated paper against on-disk result files. Final quality gate before April 8 submission.
**Plans:** 1 plan (10 tasks in 3 waves)

- [ ] PLAN.md — Wave 1: cite-check (T1-T3), Wave 2: spot-checks (T4-T6), Wave 3: final checks (T7-T10)

## Progress

| Milestone | Phases | Plans | Requirements | Status | Shipped |
|-----------|--------|-------|-------------|--------|---------|
| v1.0 SC26 Paper Sprint | 13 (2 dropped, 1 research stub) | 33/33 | 39/39 | Complete | 2026-04-06 |
| GPT Integration & Submission | 5 (15, 15.5, 16, 17, 18) | 4/9 | — | In Progress | — |
