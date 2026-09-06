---
name: ship
disable-model-invocation: true
description: >
  Use when work is complete and ready to ship through risk-based independent
  review, deterministic validation, commit, PR, and a completion record. Accepts
  optional argument
  'critique-only' to run just the critique step. NOT for mid-implementation
  checks (use /validate), code review without shipping (use /code-review), or
  committing without the full pipeline.
argument-hint: "[critique-only]"
---

# Ship Pipeline

Strict-ordering orchestrator. Runs five stages in sequence. It reuses evidence only when
the content fingerprint and criteria match.

Requires the `session-critique` and `validate` skills, plus `sam_handoff` for the
completion record.

## Arguments

- `/ship` (no args) -> all 5 stages
- `/ship critique-only` -> stage 1 only (session-critique without proceeding to validate/commit/PR, useful for mid-session quality checks)

## Hard Rules

1. **Never reorder stages.** The sequence is: review decision -> validate -> commit -> PR -> handoff record.
2. **If stage 1 or 2 fails, do NOT proceed to stage 3.** Fix findings first.
3. **Each stage uses the existing skill's full logic.** Where a stage names a skill, invoke the skill instead of reimplementing it inline.
4. **Report status between stages.** After each stage completes, state what passed and what's next.

## Pipeline

### Stage 1: Independent Review Decision

Resolve a fixed diff fingerprint. Reuse a durable independent review only when it names
that fingerprint and the same criteria.

Invoke `/session-critique` when the diff affects security, a trust boundary, architecture,
or several subsystems, or when the user asked for independent review. Keep one aggregate
review. For routine changes, record `review skipped: routine scope` and continue.

**Gate:** All BLOCK/HIGH/MEDIUM findings must be resolved (fixed or explicitly dismissed by the user) before proceeding; an unresolved BLOCK halts the pipeline. If the user dismisses a finding, record the dismissal reason.

**If `critique-only` was passed:** Stop here. Report the reused or new findings and exit.

### Stage 2: Validate

Confirm the changed paths belong to this logical change, then stage only those paths.
The validator fingerprints the Git index, so staging must happen before validation.

```bash
git status --short
git diff --stat HEAD
git add <paths>
git diff --cached --stat
```

Invoke `/validate`.

This runs or reuses the one content-bound gate through the validate skill. Do not run a
standalone full suite, smoke test, or validator agent beside it.

**Gate:** The gate verdict must be PASS. On failure, enter the skill's fix loop. Max 3 iterations. After 3 fails, halt and escalate to the user.

### Stage 3: Commit

Commit inline with git. Run the shared validator's `check` command immediately before the
commit. If the fingerprint changed, return to Stage 2 before attempting the commit. Do
not use a failed commit attempt to discover a known boundary mismatch.

```bash
git status --short
git diff --cached --stat
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
record.

**Post-check:** Report the handoff record path. Pipeline complete.

## Failure Handling

| Failure | Action |
|---------|--------|
| Stage 1 finds HIGH/MEDIUM issues | Fix findings; review again only after material changes or for a named unresolved risk |
| Stage 2 validation fails | Enter fix loop (max 3 iterations), re-run Stage 2 |
| Stage 3 commit blocked by the pre-commit hook | Return to Stage 2, fix the reported failures, retry |
| Stage 4 push fails | Report error, do NOT force push |
| Any stage fails 3 times | Halt pipeline, escalate to user |
