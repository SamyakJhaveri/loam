# Phase 19: GPT-4.1-mini Complete Data Re-Analysis — Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-08
**Phase:** 19-gpt-final-data-refresh
**Areas discussed:** Data scope confirmation, Figure regeneration scope, Phase 20 structural scope, Validation gate strategy

---

## Plans existed without context

| Option | Description | Selected |
|--------|-------------|----------|
| Continue and replan after | Capture context, then replan | ✓ |
| View existing plans | Show 19-01-PLAN.md first | |
| Cancel | Skip discuss-phase | |

**User's choice:** Continue and replan after

---

## Data Scope Confirmation

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, this is complete | All changes intentional — XSBench deletions correct, mixbench/Rodinia additions intentional | ✓ |
| Partial — some unexpected | Expected only HeCBench changes | |

**Context presented:** Scout discovered 200 total deletions include 32 XSBench files (not just 168 HeCBench), and 213 new files include mixbench omp/opencl→cuda + many Rodinia opencl→cuda (not just HeCBench omp/omp_target→cuda as plan described).

**User's choice:** Yes, this is complete — all changes intentional.

---

## Figure Regeneration Scope

| Option | Description | Selected |
|--------|-------------|----------|
| --figure all | Single command, full consistency, matches existing plan | ✓ |
| GPT variants only | Protects Qwen figures from matplotlib drift | |

**User's choice:** --figure all

---

## Phase 20 Structural Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Add 19-STRUCTURAL-CHANGES.md | Phase 19 produces explicit structural edit list for Phase 20 | ✓ |
| Phase 20 handles it implicitly | "Update ALL GPT numbers" covers structural changes | |

**Context:** Phase 17 wrote "omp_target-to-cuda unavailable" footnote + direction table with cuda-to-omp_target present. Both are structurally wrong after Phase 19. A numeric-only update would leave factually false prose in the paper.

**User's choice:** Phase 19 produces 19-STRUCTURAL-CHANGES.md listing exact structural edits Phase 20 must make.

---

## Validation Gate Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Full /validate | Standard 4-wave gate, ~3 min | ✓ |
| Targeted data check only | verify-app + spec-auditor only | |

**User's choice:** Full /validate — standard gate even for data-only commits.

---
