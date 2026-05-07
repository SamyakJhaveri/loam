---
name: fix-bug
description: Bug fix workflow — reproduce, diagnose, plan, fix, verify, record. Use when a test fails, a build step fails, or results show an unexpected pattern. Mandates reproduction before diagnosis. Integrates with /validate on exit.
---

# Bug Fix Workflow

Structured workflow for diagnosing and fixing a bug.

## Arguments
- `$ARGUMENTS` — bug description or spec name

## Workflow

### Phase 1: Reproduce
- Identify the failing command or test
- Run it and capture the exact error output
- Check `.claude/rules/known-issues.md` — is this a known bug?

### Phase 2: Diagnose
Use subagents to explore the relevant code paths in parallel:
- Trace the error to its root cause
- Identify all files involved in the call chain
- Check if the bug affects other specs/kernels

### Phase 3: Plan
Enter plan mode. Draft the fix:
- Root cause explanation
- Proposed change (minimal and targeted)
- Files to modify
- Risk of regression

Present the plan and **wait for user approval**.

### Phase 4: Fix
- Implement the minimal fix
- Do NOT refactor surrounding code
- Add a test if one doesn't exist for this case

### Phase 5: Verify
- Reproduce the original error — confirm it's fixed
- Run project test suite (e.g., `python3 -m pytest tests/ -v`)
- Check for regressions in related areas

### Phase 6: Record
- Update `.claude/rules/known-issues.md` if this was a known bug (mark as fixed)
- Update CLAUDE.md if new gotchas were discovered
