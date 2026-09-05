---
name: ship
disable-model-invocation: true
description: >
  Orchestrates the full shipping pipeline in strict order: session-critique, then
  validate, then commit, then PR, then a handoff completion record.
  Use when work is complete and ready to ship. Enforces ordering to prevent
  premature commits and skipped critiques. Accepts optional argument
  'critique-only' to run just the critique step. NOT for mid-implementation
  checks (use /validate), code review without shipping (use /code-review), or
  committing without the full pipeline.
argument-hint: "[critique-only]"
---

# Ship Pipeline

Strict-ordering orchestrator. Runs five stages in sequence, halting on failure.

Requires the `session-critique` and `validate` skills, plus `sam_handoff` for the
completion record.

## Arguments

- `/ship` (no args) -> all 5 stages
- `/ship critique-only` -> stage 1 only (session-critique without proceeding to validate/commit/PR, useful for mid-session quality checks)

## Hard Rules

1. **Never skip or reorder stages.** The sequence is: critique -> validate -> commit -> PR -> handoff record.
2. **If stage 1 or 2 fails, do NOT proceed to stage 3.** Fix findings first.
3. **Each stage uses the existing skill's full logic.** Where a stage names a skill, invoke the skill instead of reimplementing it inline.
4. **Report status between stages.** After each stage completes, state what passed and what's next.

## Pipeline

### Stage 1: Session Critique

Invoke `/session-critique`.

This spawns an advisor-pattern agent team that adversarially reviews all work in the current session **against the decisions the user made during it**. It surfaces findings for decision-drift, regressions, over-engineering, dangling references, and scope hygiene.

**Gate:** All BLOCK/HIGH/MEDIUM findings must be resolved (fixed or explicitly dismissed by the user) before proceeding; an unresolved BLOCK halts the pipeline. If the user dismisses a finding, record the dismissal reason.

**If `critique-only` was passed:** Stop here. Report findings and exit. Do not proceed to Stage 2.

### Stage 2: Validate

Invoke `/validate`.

This runs the build-validator gate through the validate skill.

**Gate:** The gate verdict must be PASS. On failure, enter the skill's fix loop. Max 3 iterations. After 3 fails, halt and escalate to the user.

### Stage 3: Commit

Commit inline with git. In a project rendered from Loam, the commit gate is the
sentinel trio: `.validation_passed` is written by
`.claude/hooks/run-validate-waves.sh`, removed by `sentinel-cleanup.sh` on the
next edit, and required by `pre-commit-gate.sh` on `git commit`. When that script
exists, run `.claude/hooks/run-validate-waves.sh` in its own Bash call before the
commit so the gate has a fresh sentinel. In a project bootstrapped by
`/bootstrap-cc-setup`, the native git pre-commit hook applies instead and
independently re-runs the fast deterministic checks, failing the commit if any
fail.

```bash
git status --short
git diff --stat HEAD
```

Stage only the files belonging to one logical change, then commit:

```bash
git add <paths>
git commit -m "<type>: <subject>"
```

Split commits by scope if the session produced multiple logical changes. Never bundle unrelated changes into a single commit. If the pre-commit hook rejects the commit, return to Stage 2 and fix the reported failures; never bypass the hook.

### Stage 4: PR

First decide whether this change is docs-only. Resolve the default branch the way codex-review does (`git symbolic-ref --short refs/remotes/origin/HEAD`, falling back to main) and run `git diff --name-only <default>...HEAD`. The change is docs-only when every path is under `docs/`, or is a `*.md` file outside `seed/` and `cultivation/`. Docs-only changes go direct to the default branch under the hybrid branch policy: skip the push and the PR, report 'docs-only: stage 4 skipped', and continue to stage 5. Otherwise push and open the PR:

```bash
git push -u origin HEAD
gh pr create --title "<title>" --body "<summary + test plan>"
```

Never force push. If the push fails, report the error and stop.

**Post-check:** Report the PR URL, or that stage 4 was skipped as docs-only.

### Stage 5: Completion Record

Invoke `/sam_handoff` (per Hard Rule 3, use the skill, do not restate its schema
inline). Runs AFTER commit + PR so the record can cite the post-commit SHA and
the opened PR number when there is one. Every shipped work-stream leaves a machine-findable
record, so no more hand-pasted summaries.

**Post-check:** Report the handoff record path. Pipeline complete.

## Failure Handling

| Failure | Action |
|---------|--------|
| Stage 1 finds HIGH/MEDIUM issues | Fix findings, re-run Stage 1 |
| Stage 2 validation fails | Enter fix loop (max 3 iterations), re-run Stage 2 |
| Stage 3 commit blocked by the pre-commit hook | Return to Stage 2, fix the reported failures, retry |
| Stage 4 push fails | Report error, do NOT force push |
| Any stage fails 3 times | Halt pipeline, escalate to user |
