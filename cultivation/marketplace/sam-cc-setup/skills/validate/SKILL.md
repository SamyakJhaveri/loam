---
name: validate
description: "Post-session validation loop — two-wave checks (Deterministic / Rule-based) before commit. Use before every git commit. Writes .validation_passed sentinel with waves_passed field on success. NOT for: ad-hoc test runs, code review, or implementation work — only the Pipeline Gate between implement and commit."
---

# Post-Session Validation Loop

**Trigger:** When user types `/validate`, `/validate quick`, or `/validate fix`

Runs a two-wave validation loop after implementation, before commit. Wave layers follow `.claude/rules/layer-triage.md` (60/30/10): deterministic first, rule-based second. Both waves are LLM-free. Deep adversarial review (the probabilistic Layer 3) is not part of the gate — invoke `/session-critique` manually when you want it.

## Arguments

- (none) or `full` → both waves (recommended)
- `quick` → Wave 1 only (~30s deterministic; writes `waves_passed=1` — INSUFFICIENT for commit)
- `fix` → re-run failed waves only (after implementing fixes)

## Prerequisites

1. All implementation work for the session is complete (files saved)
2. Files are NOT yet committed (`git diff HEAD` shows your changes)

## Workflow

### Step 0: Snapshot (before any wave)

```bash
echo "=== PRE-VALIDATION SNAPSHOT ==="
echo "Changed files: $(git diff --name-only HEAD | wc -l)"
git diff --name-only HEAD
```

If no files changed → write sentinel with `waves_passed=2` and exit (nothing to validate).

---

### WAVE 1 — Deterministic (~10–30s)

Pure tooling. **Zero LLM calls.**

```bash
# Lint
uv run ruff check . 2>&1 | tail -20

# Type check
command -v mypy >/dev/null && mypy . 2>&1 | tail -20

# Whitespace and conflict markers
git diff --check 2>&1 | tail -10

# New TODO/FIXME/XXX added in diff (informational unless policy)
git diff HEAD | grep -nE '^\+.*\b(TODO|FIXME|XXX)\b' || true

# Shell syntax on changed .sh files
for f in $(git diff --name-only HEAD | grep '\.sh$'); do
    [ -f "$f" ] && bash -n "$f" 2>&1 || echo "SYNTAX ERROR: $f"
done
```

**Wave 1 Gate:** Any check fails → skip remaining waves, go to Fix Loop.

---

### WAVE 2 — Rule-based (~30–90s)

**Skip if `/validate quick` was requested.**

```bash
# Unit tests
[ -d tests ] && uv run pytest tests/ -v 2>&1 | tail -20

# Project-specific validation scripts
[ -x bin/validate.sh ] && bin/validate.sh 2>&1 | tail -10
```

**Wave 2 Gate:** Any check fails → go to Fix Loop. LLM-free.

---

### Fix Loop (triggered when any wave FAILs)

1. **Collect** all FAIL verdicts from the current wave
2. **Enter plan mode** with a targeted fix plan
3. **Wait for user approval** — do not implement before approval
4. **Implement fixes** — targeted only, no scope creep
5. **Re-validate** with `/validate fix`

**Maximum iterations:** 3. After 3 fails → escalate to user; the L2 stage contract is probably the issue.

---

### Completion: Write Sentinel

After waves pass, write the sentinel with `waves_passed` set to the highest wave that passed:

```bash
# WAVES_PASSED is set by the wave executor:
#   quick                 → 1
#   full (both waves green) → 2
WAVES_PASSED=${WAVES_PASSED:-2}

cat > .validation_passed << SENTINEL
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
git_hash=$(git rev-parse HEAD 2>/dev/null || echo "none")
changed_files=$(git diff --name-only HEAD | wc -l | tr -d ' ')
waves_passed=$WAVES_PASSED
validated_by=validate-skill
SENTINEL

echo ".validation_passed written (waves_passed=$WAVES_PASSED)"
if [ "$WAVES_PASSED" -lt 2 ]; then
    echo "Note: commit gate requires waves_passed>=2 — run full /validate before commit"
fi
```

**Then report the full validation summary.**

## No commit-message override

`pre-commit-gate.sh` enforces the gate solely via the `.validation_passed` sentinel — it does NOT parse the commit message, so there is no `[skip-validate]` escape hatch. The gate is intentionally unconditional.

Even a change that seems to need no checks (e.g., a docs-only edit) must pass full `/validate` (both waves) before committing: the gate requires `waves_passed>=2`, so anything short of both waves (e.g., `/validate quick`) leaves the commit blocked. To bypass deliberately, disable the hook in `settings.json` — there is no per-commit skip flag.
