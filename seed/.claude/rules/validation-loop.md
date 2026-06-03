---
paths:
  - ".claude/hooks/**"
  - ".claude/skills/validate/**"
  - ".claude/agents/verification-lead.md"
---

# Post-Session Validation Loop

> Loads when working on validation hooks, skills, or agents.
> Run `/validate` after implementation. Pre-commit hook requires validation to pass.

## Quick Reference

```bash
/validate          # Full validation (~1-2 min, both waves)
/validate quick    # Wave 1 only (~30s, deterministic — INSUFFICIENT for commit)
/validate fix      # Re-run failed waves after implementing fixes
```

## Wave Structure (60/30/10 layer-triage applied)

| Wave | Layer | Checks | Gate | ~Time |
|------|-------|--------|------|-------|
| 1 | **Deterministic** | ruff, mypy, `git diff --check`, regex grep for new TODO/FIXME/XXX, `bash -n` on changed `.sh` | Any FAIL blocks; no LLM calls | 10–30s |
| 2 | **Rule-based** | pytest, project-specific validation scripts | Any FAIL blocks; no LLM calls | 30–90s |

This ordering follows `.claude/rules/layer-triage.md`: deterministic checks fire first because they're cheapest and produce the highest-confidence verdicts, rule-based tests second. Both waves are LLM-free.

The probabilistic layer (Layer 3 of 60/30/10) is **not** part of the commit gate — deep adversarial review (drift detection, rationalization, code simplification) is invoked manually via `/session-critique` when you want it, not forced on every commit.

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
- **Includes `waves_passed=N`** field — N is the highest wave that passed (1 for `quick`, 2 for full)
- Checked by `.claude/hooks/pre-commit-gate.sh` before `git commit`:
  - Sentinel must exist
  - Age < 30 minutes (re-validate if stale)
  - `waves_passed >= 2` (rejects `/validate quick` results)
  - No tracked file edited after sentinel mtime
- **Invalidated** (deleted) by `.claude/hooks/sentinel-cleanup.sh` whenever any file is edited
- Listed in `.gitignore` (never committed)

## No commit-message override

`pre-commit-gate.sh` enforces the gate solely via the `.validation_passed` sentinel; it does NOT parse commit messages, so there is no `[skip-validate]` escape hatch. The gate is intentionally unconditional. Even a docs-only edit must pass full `/validate` (both waves) before it can be committed — the gate requires `waves_passed>=2`, so anything short of both waves (e.g., `/validate quick`) leaves the commit blocked. To bypass deliberately, disable the hook in `settings.json`.
