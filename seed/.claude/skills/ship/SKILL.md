---
name: ship
description: >
  Orchestrates the full shipping pipeline in strict order. Runs session-critique,
  then validate (both waves), then commit, then PR. Use when work is complete
  and ready to ship. Enforces ordering to prevent premature commits and skipped
  critiques. Accepts optional argument 'critique-only' to run just the critique
  step. NOT for mid-implementation checks (use /validate), code review without
  shipping (use /multi-review), or committing without the full pipeline (use
  /commit directly only if critique + validate already passed).
argument-hint: "[critique-only]"
---

# Ship Pipeline

Strict-ordering orchestrator. Runs four stages in sequence, halting on failure.

## Arguments

- `/ship` (no args) → all 4 stages
- `/ship critique-only` → stage 1 only (session-critique without proceeding to validate/commit/PR — useful for mid-session quality checks)

## Hard Rules

1. **Never skip or reorder stages.** The sequence is: critique → validate → commit → PR.
2. **If stage 1 or 2 fails, do NOT proceed to stage 3.** Fix findings first.
3. **Each stage uses the existing skill's full logic.** Do not reimplement any step inline — invoke the skill.
4. **Report status between stages.** After each stage completes, state what passed and what's next.

## Pipeline

### Stage 1: Session Critique

Invoke `/session-critique`.

This spawns an advisor-pattern agent team that adversarially reviews all work in the current session **against the decisions the user made during it**. It surfaces findings for decision-drift, regressions, over-engineering, dangling references, and scope hygiene.

**Gate:** All BLOCK/HIGH/MEDIUM findings must be resolved (fixed or explicitly dismissed by user) before proceeding; an unresolved BLOCK halts the pipeline. If the user dismisses a finding, record the dismissal reason.

**If `critique-only` was passed:** Stop here. Report findings and exit. Do not proceed to Stage 2.

### Stage 2: Validate

Invoke `/validate` (full — both waves, NOT quick).

This runs the two-wave validation loop: deterministic checks, rule-based tests. Must produce `.validation_passed` sentinel with `waves_passed=2`.

**Gate:** All waves must pass. On failure, enter the fix loop per `.claude/rules/validation-loop.md`. Max 3 iterations. After 3 fails, halt and escalate to user.

### Stage 3: Commit

Invoke `/commit`.

**Pre-check:** Confirm `.validation_passed` exists and `waves_passed=2` before proceeding. If sentinel is missing or stale, return to Stage 2.

Split commits by scope if the session produced multiple logical changes. Never bundle unrelated changes into a single commit.

### Stage 4: PR

Invoke `/pr`.

Push to remote and open a GitHub PR with summary and test plan.

**Post-check:** Report the PR URL. Pipeline complete.

## Failure Handling

| Failure | Action |
|---------|--------|
| Stage 1 finds HIGH/MEDIUM issues | Fix findings, re-run Stage 1 |
| Stage 2 validation fails | Enter fix loop (max 3 iterations), re-run Stage 2 |
| Stage 3 commit blocked by pre-commit gate | Return to Stage 2 (sentinel likely stale) |
| Stage 4 push fails | Report error, do NOT force push |
| Any stage fails 3 times | Halt pipeline, escalate to user |
