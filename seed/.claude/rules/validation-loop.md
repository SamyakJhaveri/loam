---
paths:
  - ".claude/hooks/**"
  - ".claude/skills/validate/**"
  - ".claude/agents/self-critic.md"
  - ".claude/agents/verification-lead.md"
  - ".claude/agents/plan-reviewer.md"
---

# Post-Session Validation Loop

> Loads when working on validation hooks, skills, or agents.
> Run `/validate` after implementation. Pre-commit hook requires validation to pass.

## Quick Reference

```bash
/validate          # Full validation (~2-3 min, all 3 waves)
/validate quick    # Wave 1 only (~30s, deterministic — INSUFFICIENT for commit)
/validate fix      # Re-run failed waves after implementing fixes
```

## Wave Structure (60/30/10 layer-triage applied)

| Wave | Layer | Checks | Gate | ~Time |
|------|-------|--------|------|-------|
| 1 | **Deterministic** | ruff, mypy, `git diff --check`, regex grep for new TODO/FIXME/XXX, `bash -n` on changed `.sh` | Any FAIL blocks; no LLM calls | 10–30s |
| 2 | **Rule-based** | pytest, project-specific validation scripts | Any FAIL blocks; no LLM calls | 30–90s |
| 3 | **Probabilistic** *(only if W1+W2 pass)* | plan-reviewer (drift from L2 Done + rollback safety), self-critic (rationalization, incomplete work, code simplification†) | plan-reviewer or self-critic FAIL blocks; code-simplification WARN doesn't | 60–90s |

†code simplification: absorbed into self-critic as advisory WARN, not blocking

This ordering follows `.claude/rules/layer-triage.md`: deterministic checks fire first because they're cheapest and produce the highest-confidence verdicts. Probabilistic LLM work runs last — and only after Wave 1+2 pass, so we never spend LLM budget reviewing code that already failed lint or tests.

## Fix Loop Protocol

1. Collect ALL FAIL verdicts from the current wave
2. Enter plan mode with a targeted fix plan
3. **Wait for user approval** — no implementation before approval
4. Implement fixes (targeted only — no scope creep)
5. Re-run `/validate fix` (failed wave + downstream only)
6. Max 3 iterations. After 3 fails → escalate to user; the L2 stage contract is probably the issue, not the implementation.

## Commit Gate Enforcement

`.validation_passed` sentinel in project root:
- Written by `/validate` (or `verification-lead` agent) after waves pass
- **Includes `waves_passed=N`** field — N is the highest wave that passed (1 for `quick`, 2 if Wave 3 skipped, 3 for full)
- Checked by `.claude/hooks/pre-commit-gate.sh` before `git commit`:
  - Sentinel must exist
  - Age < 30 minutes (re-validate if stale)
  - `waves_passed >= 3` (rejects `/validate quick` results)
  - No tracked file edited after sentinel mtime
- **Invalidated** (deleted) by `.claude/hooks/sentinel-cleanup.sh` whenever any file is edited
- Listed in `.gitignore` (never committed)

## Context Budget

Each Wave 3 agent returns max 50 lines structured verdict.
Main session receives ~50-line aggregated report.
Subagent isolation: no raw test output, no verbose logs in main context.

## Override

User says "skip validation" → acknowledge, document in commit message: `[skip-validate: reason]`.
