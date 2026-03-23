# Post-Session Validation Loop

> Auto-loaded on every task. Defines the validation protocol required before every commit.
> Run `/validate` after implementation. Never commit without passing the validation loop.

## Quick Reference

```bash
/validate          # Full 4-wave validation (~3 min, 10+ agents)
/validate quick    # Wave 1 only (~30s: schema + diff + security)
/validate fix      # Re-run failed waves after implementing fixes
```

## Wave Structure

| Wave | Agents (parallel) | Gate | ~Time |
|------|-------------------|------|-------|
| 1 | verify-app, diff-reviewer, security-scanner | All must PASS | 30s |
| 2 | test-synthesizer, regression-checker, spec-auditor* | All must PASS | 60s |
| 3 | consistency-checker, code-simplifier† | consistency must PASS | 45s |
| 4 | self-critic, plan-reviewer‡ | self-critic must PASS | 30s |

*spec-auditor: only when `specs/` files changed
†code-simplifier: advisory — WARN, not blocking
‡plan-reviewer: only when fix loop was triggered

## Fix Loop Protocol

1. Collect ALL FAIL verdicts from the current wave
2. Enter plan mode with a targeted fix plan
3. **Wait for user approval** — no implementation before approval
4. Implement fixes (targeted only — no scope creep)
5. Re-run `/validate fix` (failed wave + downstream only)
6. Max 3 iterations. After 3 fails → escalate to user.

## Commit Gate Enforcement

`.validation_passed` sentinel in project root:
- Written by `/validate` after all waves PASS
- Checked by `.claude/hooks/pre-commit-gate.sh` before `git commit`
- **Invalidated** (deleted) by `.claude/hooks/sentinel-cleanup.sh` whenever any file is edited
- TTL: 30 minutes — re-validate if sentinel is older than that
- Listed in `.gitignore` (never committed)

## Anti-Rationalization Stop Hook

When Claude tries to stop, a prompt-type Stop hook injects:
> "BEFORE STOPPING: (1) Was /validate run? (2) All task items finished? (3) Evidence for
> every 'works'/'fixed' claim? (4) Docs updated for gotchas? If ANY is NO — address it."

This is the Trail of Bits anti-rationalization pattern. If validation hasn't passed, the
Stop hook prevents premature completion.

## Self-Improvement Feedback Loop (Kaizen)

After Wave 4 self-critic runs:
- **If rationalization pattern found** → add new anti-pattern to `workflow.md`
- **If stale docs found** → update as part of fix loop (not deferred)
- **If repeated mistake pattern** → consider creating a new PreToolUse hook to block it
- **If new gotcha** → add to `known-issues.md`

Every validation run is an opportunity to improve the process. Do not defer lessons.

## Context Budget

Each agent returns max 50 lines structured verdict.
Main session receives ~50-line aggregated report.
Subagent isolation: no raw test output, no verbose logs in main context.

## Override (emergency only)

User says "skip validation" → acknowledge, document in commit message: `[skip-validate: reason]`.
This must be rare. self-critic will flag systematic overuse as a quality concern.
