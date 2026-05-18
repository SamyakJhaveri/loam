---
name: validate
description: "Post-session validation loop — multi-wave checks before commit. Use before every git commit. Writes .validation_passed sentinel on success. NOT for: ad-hoc test runs, code review, or implementation work — only the Pipeline Gate between implement and commit."
---

# Post-Session Validation Loop

**Trigger:** When user types `/validate`, `/validate quick`, or `/validate fix`

Runs a wave-based validation loop after implementation work, before committing.

## Arguments

- (none) or `full` → full validation (recommended)
- `quick` → Wave 1 only: fast checks (~30s)
- `fix` → re-run failed waves only (after implementing fixes)

## Prerequisites

Before running `/validate`:
1. All implementation work for the session is complete (files saved)
2. Files are NOT yet committed (git diff HEAD shows your changes)

## Workflow

### Step 0: Snapshot (before any wave)

Capture baseline metrics:
```bash
echo "=== PRE-VALIDATION SNAPSHOT ==="
echo "Changed files: $(git diff --name-only HEAD | wc -l)"
git diff --name-only HEAD
```

---

### WAVE 1: Fast Checks (~30s)

**Launch agents IN PARALLEL:**

1. **code-simplifier** — code quality check on changed files
2. **plan-reviewer** — reviews git diff for regressions, partial implementations
3. **self-critic** — adversarial self-review (rationalization patterns, incomplete work)

**Wave 1 Gate:** If ANY agent returns FAIL → skip remaining waves, go to Fix Loop.

---

### WAVE 2: Deep Analysis (~60s)

**Skip if `/validate quick` was requested.**

Run project-specific checks:
- Unit tests: `python3 -m pytest tests/ -v` (if tests exist)
- Lint: `ruff check .` (if configured)
- Type check: `mypy` (if configured)
- Any project-specific validation scripts

**Wave 2 Gate:** If any check fails → go to Fix Loop.

---

### Fix Loop (triggered when any wave FAILs)

1. **Collect** all FAIL verdicts from the current wave
2. **Enter plan mode** with a targeted fix plan
3. **Wait for user approval** — do not implement before approval
4. **Implement fixes** — targeted only, no scope creep
5. **Re-validate** with `/validate fix`

**Maximum iterations:** 3. After 3 fails → escalate to user.

---

### Completion: Write Sentinel

After ALL waves pass:

```bash
cat > .validation_passed << EOF
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
git_hash=$(git rev-parse HEAD 2>/dev/null || echo "none")
changed_files=$(git diff --name-only HEAD | wc -l | tr -d ' ')
validated_by=validate-skill
EOF

echo ".validation_passed written — git commit is now unblocked"
```

**Then report the full validation summary.**

## Context Management Protocol

Each agent returns max 50 lines. The aggregated report (~50 lines) is all that enters the main context. Do NOT read agent output files into main context.

## Override

If validation is not applicable (e.g., docs-only change):
1. User explicitly says "skip validation for this commit"
2. Document reason in commit message: `[skip-validate: reason]`
