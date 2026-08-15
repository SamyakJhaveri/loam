---
name: validate
description: "Deterministic pre-commit validation - two waves (Deterministic / Rule-based) run on demand. Use when a change is risky and before every substantive commit. Enforcement is a native git pre-commit hook, not a sentinel. NOT for: ad-hoc test runs, code review, or implementation work."
---

# Deterministic validation

**Trigger:** When user types `/validate` or `/validate fix`

Runs a two-wave validation pass after implementation, before commit. Both waves are LLM-free.
Deep adversarial review is not part of this pass - invoke a reviewer agent manually when you want it.

Enforcement model: a native git pre-commit hook (installed by `/bootstrap-cc-setup` at
`.git/hooks/pre-commit`) runs the fast deterministic checks on every commit and fails the
commit if any fail. There is no sentinel file and no PreToolUse commit gate. This skill is
the on-demand superset of what the hook enforces.

## Arguments

- (none) → both waves
- `fix` → after a targeted repair, re-run the same waves

## Prerequisites

1. All implementation work for the session is complete (files saved)
2. Files are NOT yet committed (`git diff HEAD` shows your changes)

## Workflow

### Step 0: Snapshot

```bash
echo "=== PRE-VALIDATION SNAPSHOT ==="
git diff --name-only HEAD
```

If no files changed → report "nothing to validate" and exit.

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

**Wave 1 Gate:** Any check fails → skip Wave 2, go to Fix Loop.

### WAVE 2 — Rule-based (~30–90s)

```bash
# Unit tests
[ -d tests ] && uv run pytest tests/ -v 2>&1 | tail -20

# Project-specific validation scripts
[ -x bin/validate.sh ] && bin/validate.sh 2>&1 | tail -10
```

**Wave 2 Gate:** Any check fails → go to Fix Loop. LLM-free.

### Fix Loop (triggered when any wave FAILs)

1. **Record** the exact failed check and evidence
2. **Write** the smallest targeted repair plan
3. **Obtain approval** when the repair changes the agreed scope
4. **Implement** the repair and re-run `/validate fix`

**Maximum iterations:** 3. After 3 fails on the same issue → stop and escalate.
Never bypass a failing check.

### Completion

Report every check with its exit status. No sentinel is written; the native pre-commit
hook independently re-runs the fast checks at commit time.
