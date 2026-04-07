# Phase 16: GPT-4.1 Mini Data Analysis — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-07
**Phase:** 16-gpt-data-analysis
**Areas discussed:** Deadline Sequencing, Figure Regen Scope, cross_model_comparison.py Design, Coverage Gap Treatment

---

## Deadline Sequencing

| Option | Description | Selected |
|--------|-------------|----------|
| Full run, no deferrals | T1→T2+T3→T3b→T4+T5→T6 as planned, all 7 artifacts | ✓ |
| Parallel-max with gate | Run T1+T2+T3 simultaneously, then gate, then T4+T5+T6 in parallel | |
| Critical path only | T1, T2, T4 mandatory; T3, T6 nice-to-have | |

**User's choice:** Full run, no deferrals
**Notes:** All T1-T6 must complete. No tasks skipped even under April 8 pressure.

---

## Figure Regen Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Targeted: F3, F4, F5, F7 only | Only the 4 dual-model figures; leaves 9 working figures untouched | |
| --figure all (as planned) | Regenerate all 13 figures in one command | ✓ |

**User's choice:** `--figure all` as in existing plan
**Notes:** Accept small style-drift risk. F7 already refactored in Phase 15.5.

---

## cross_model_comparison.py Design

| Option | Description | Selected |
|--------|-------------|----------|
| Full: chi-sq + Cohen's h + per-direction + per-kernel matrix | All four statistics for Section 6.9 | ✓ |
| Minimal: chi-sq + Cohen's h only | Headline stats only | |
| Chi-sq + Cohen's h + per-direction (no kernel matrix) | Skip dense per-kernel matrix | |

**User's choice:** Full — all four statistics

### Per-kernel matrix granularity

| Option | Description | Selected |
|--------|-------------|----------|
| Binary: AGREE / DIVERGE | Simple pass/fail agreement | |
| Four-way: both-pass / both-fail / Qwen-only-pass / GPT-only-pass | Distinguishes which model performs better on divergent kernels | ✓ |

**User's choice:** Four-way granularity
**Notes:** Enables Section 6.9 narrative about which model performs better on specific kernels.

---

## Coverage Gap Treatment

**Discovery:** `omp_target-to-cuda` has 0 files in `results/evaluation/azure-gpt-4.1-mini/`. Le never submitted this direction.

| Option | Description | Selected |
|--------|-------------|----------|
| Proceed without it — exclude from cross-model comparison | 7-direction comparison with footnote | |
| Wait for Le before starting Phase 16 | Block until full 8-direction data arrives | ✓ |

**User's choice:** Wait for Le's data

### Fallback decision (if Le can't deliver today)

| Option | Description | Selected |
|--------|-------------|----------|
| Proceed with 7 directions at deadline | Run Phase 16 with what we have; footnote the gap; don't miss April 8 | ✓ |
| Request extension or submit without Section 6.9 | Skip cross-model section or request deadline extension | |

**User's choice:** Proceed with 7 directions as fallback at April 8 deadline

---
