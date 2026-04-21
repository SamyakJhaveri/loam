---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: pre-launch-ready
stopped_at: Pre-Phase-3 cleanup complete (5 commits unpushed, doc pruning + STATE refresh in flight); Phase 3 canonical streams gated on push + Le provisioning + budget refresh
last_updated: "2026-04-20T17:35:00.000Z"
last_activity: 2026-04-20
progress:
  total_phases: 4
  completed_phases: 2
  total_plans: 13
  completed_plans: 13
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (refreshed 2026-04-20 in commit `126aa94`)

**Core value:** Every evaluation result is reproducible and pipeline-correct -- so model comparisons in the NeurIPS paper are defensible under peer review.
**Current focus:** Phase 3 — Full Evaluation Runs (canonical + L0-conditional ablation)

## Current Position

Phase: 03 (Full Evaluation Runs) — pre-launch; canonical streams not yet started
Plans: Phase 2 complete (8/8 plans landed 2026-04-17); Phase 3 launch manifest in `.planning/phases/03-oracle-framework/04-S7-LAUNCH-MANIFEST.md`
Status: Pre-Phase-3 audit & cleanup complete on 2026-04-20 (commits `a8046a3` `6fd48c8` `126aa94` `c24f366` `c695f9f` — local, unpushed). Phase 3 launch gated on the three Launch Blockers below.
Last activity: 2026-04-20

Progress: [##########] 100% Phase 1 complete · Phase 2 complete · Phase 3 pre-launch (cleanup landed)

## Launch Blockers (Phase 3 canonical)

The Phase 3 launch manifest (`04-S7-LAUNCH-MANIFEST.md` §1 entry gate table) points here.

1. **Push 5 cleanup commits to `origin/main`.** Bash perms block `git push origin main`; user must run `! git push origin main`. Commits in order: `a8046a3` (W1 evaluation.md grep idiom) → `6fd48c8` (W2 analysis script CLI hardening + C1-C4 tombstone + 2 batch scripts archived) → `126aa94` (W3 docs refresh) → `c24f366` (W4+W5 augmentation + phase 01/02 archival) → `c695f9f` (CLAUDE.md user behavioral guidance).
2. **Le provisions `azure-gpt-5.4`** on his Azure resource and confirms TPM quota ≥200k sustained. Operator runbook: `docs/neurips2026-gpt5-handoff.md`.
3. **Gal sign-off refresh** on the recomputed budget. Approved figure was $559 (2026-04-17); refreshed at current Azure pricing lands at ~$848 — see `project_budget_math_2026_04_17.md` memory + `project_budget_overshoot.md`. Per Gal: "if anything changes I will let you know"; recomputation has not yet been re-confirmed.

When all three close, `run_eval_batch.py` launches per `04-S7-LAUNCH-MANIFEST.md` §2 with zero further code changes required.

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- **[2026-04-16]** Canonical = pass@3 L0 temp=0.7 thinking=ON self-repair=OFF, both Qwen 3.5 397B + Azure GPT-5.4
- **[2026-04-16]** Ablation filter = pass@1-of-any from 3 canonical samples
- **[2026-04-16]** Ablation scope = all 4 levels (L1+L2+L3+L4) on ALL L0-passers, no subsets
- **[2026-04-16]** No audit sample of L0-failers; Phase 4 **must** write a threats-to-validity subsection acknowledging this — that subsection is an outstanding TODO.
- **[2026-04-17]** Gal signed off on GPT budget overshoot at $559; refreshed at current pricing ≈ $848 (pending re-confirmation).
- **[2026-04-16]** 3-phase launch: canonical → derive L0-passers → ablation (canonical must complete first)
- **[2026-04-19]** S7c oracle audit complete: 88/88 sweep PASS, 8 specs downgraded for cross-API divergence (full table in `known-issues.md`).
- **[2026-04-20]** Pre-Phase-3 results purged from `results/evaluation/` per user directive (1248 Qwen + 905 GPT-4.1-mini); Phase 3 reconstitutes all numbers from scratch.
- **[2026-04-20]** Pre-Phase-3 audit & cleanup landed (5 commits, W1-W5 of plan `before-we-move-on-lazy-sphinx.md`); 8 stale planning/docs `.md` files deleted in follow-up commit.
- AskSage is BLOCKED -- deferred to post-submission (not on May 1 critical path)
- Portability (hardcoded compiler paths in specs) deferred to post-NeurIPS

### Open Items (post-launch, not Phase 3 blockers)

- Phase 4 threats-to-validity subsection — covers "no L0-failer audit" decision
- Post-NeurIPS S6.5 — bulk-tag the 153 untagged HeCBench specs

## Session Continuity

Last session: 2026-04-20T17:35:00.000Z
Stopped at: Pre-Phase-3 cleanup complete; STATE.md refresh + memory refresh + 8-file delete in flight as the 6th unpushed commit.
Resume file: None
Next: After this commit lands and user pushes all 6 commits, Phase 3 canonical streams launch when Launch Blockers 2 + 3 close. Operator entry point: `docs/neurips2026-gpt5-handoff.md`.
