---
paths:
  - ".claude/hooks/**"
  - ".claude/skills/validate/**"
  - ".claude/agents/self-critic.md"
---

# Post-Session Validation Loop

> Loads when working on validation hooks, skills, or agents.
> Run `/validate` after implementation. Pre-commit hook requires validation to pass.

## Quick Reference

```bash
/validate          # Full validation (~2 min)
/validate quick    # Wave 1 only (~30s: code quality + diff review + self-critic)
/validate fix      # Re-run failed waves after implementing fixes
```

## Wave Structure

| Wave | Agents (parallel) | Gate | ~Time |
|------|-------------------|------|-------|
| 1 | code-simplifier†, plan-reviewer, self-critic | self-critic or plan-reviewer FAIL blocks | 30s |
| 2 | project tests, linter, shell syntax checks | Test failures or syntax errors block | 60s |

†code-simplifier: advisory — WARN, not blocking

## Fix Loop Protocol

1. Collect ALL FAIL verdicts from the current wave
2. Enter plan mode with a targeted fix plan
3. **Wait for user approval** — no implementation before approval
4. Implement fixes (targeted only — no scope creep)
5. Re-run `/validate fix` (failed wave + downstream only)
6. Max 3 iterations. After 3 fails → escalate to user.

## Commit Gate Enforcement

`.validation_passed` sentinel in project root:
- Written by `/validate` after waves pass
- Checked by `.claude/hooks/pre-commit-gate.sh` before `git commit`
- **Invalidated** (deleted) by `.claude/hooks/sentinel-cleanup.sh` whenever any file is edited
- TTL: 30 minutes — re-validate if sentinel is older than that
- Listed in `.gitignore` (never committed)

## Context Budget

Each agent returns max 50 lines structured verdict.
Main session receives ~50-line aggregated report.
Subagent isolation: no raw test output, no verbose logs in main context.

## Override

User says "skip validation" → acknowledge, document in commit message: `[skip-validate: reason]`.
