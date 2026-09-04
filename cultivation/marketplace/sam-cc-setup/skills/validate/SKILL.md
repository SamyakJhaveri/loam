---
name: validate
description: "Deterministic pre-commit validation on demand: runs the build-validator agent as the single command-running gate, then a bounded fix loop. Use when a change is risky and before every substantive commit. Enforcement is a native git pre-commit hook. NOT for: ad-hoc test runs, code review, or implementation work."
---

# Deterministic validation

**Trigger:** When user types `/validate` or `/validate fix`

Runs the command-running validation gate after implementation, before commit. Deep
adversarial review is not part of this pass - invoke a reviewer agent manually when you
want it.

Enforcement model: a native git pre-commit hook (installed by `/bootstrap-cc-setup` at
`.git/hooks/pre-commit`) runs the fast deterministic checks on every commit and fails the
commit if any fail. There is no sentinel file and no PreToolUse commit gate. This skill is
the on-demand superset of what the hook enforces.

## Arguments

- (none) → run the gate
- `fix` → after a targeted repair, re-run the gate

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

### Step 1: Run the gate

Spawn the build-validator agent (Agent tool, subagent type `sam-cc-setup:build-validator`).
Give it the changed file list from Step 0. Print its report verbatim.

This skill runs no checks inline. Every command lives in the agent, so there is one place
to change them.

**Gate:**
- `VERDICT: PASS` → go to Completion.
- `VERDICT: FAIL` → go to the Fix Loop.
- `VERDICT: BLOCKED` → report the agent's reason to the user and stop.

### Fix Loop (triggered when the gate verdict is FAIL)

1. **Record** the exact failed check and evidence
2. **Write** the smallest targeted repair plan
3. **Obtain approval** when the repair changes the agreed scope
4. **Implement** the repair and re-run `/validate fix`

**Maximum iterations:** 3. After 3 fails on the same issue → stop and escalate.
Never bypass a failing check.

### Completion

Report every check with its exit status. No sentinel is written; the native pre-commit
hook independently re-runs the fast checks at commit time.
