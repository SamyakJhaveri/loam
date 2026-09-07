---
name: validate
description: "Use when completed changes need deterministic pre-commit validation or an existing content-bound validation receipt needs checking. NOT for ad-hoc focused tests, code review, or implementation work."
---

# Deterministic validation

**Trigger:** When user types `/validate` or `/validate fix`

Runs one deterministic validation owner after implementation. Deep adversarial review is
separate. A valid receipt can be reused across turns. Changed source, Git state, command
definitions, or runtime identity require a new run.

Projects rendered from Loam share `.agents/lib/validation.py` between Claude and Codex.
It writes a versioned JSON receipt to `.validation_passed`. The commit adapter checks the
receipt against current contents. A native plugin pre-commit hook may remain as a fallback
in projects that do not ship the shared validator.

## Arguments

- (none) → run the gate
- `fix` → after a targeted repair, re-run the gate

## Prerequisites

1. All implementation work for the session is complete (files saved)
2. The intended source changes are staged but not committed (`git diff --cached` shows
   exactly the inputs for the next commit). Staging after validation changes the source
   fingerprint and invalidates the receipt.

## Workflow

### Step 0: Select the owner

```bash
if [ -f .agents/lib/validation.py ]; then
  VALIDATOR=.agents/lib/validation.py
elif [ -f seed/.agents/lib/validation.py ]; then
  VALIDATOR=seed/.agents/lib/validation.py
else
  VALIDATOR=
fi
```

The root form supports Loam template development. Do not run both forms.

Custom projects configure `.agents/validation.json` with `schema: 1` and a
`checks` list of `{name, argv}` objects. Shell checks also require
`runtime_dependencies`: executable names or paths for every external tool they
use. Declare `[]` only for checks that use shell builtins alone. These declarations
define the runtime evidence; the validator does not infer arbitrary program
dependencies. Loam receipt reuse requires a directly installed Copier executable
and all required native CLIs, without diagnostic skip overrides.

### Step 1: Reuse or run

When `$VALIDATOR` is set, check the existing receipt first:

```bash
python3 "$VALIDATOR" check --root .
```

Exit 0 means the receipt matches the current validation inputs. Report that receipt and
do not rerun its commands. Exit 1 means evidence is absent or invalid. Run the owner once:

```bash
python3 "$VALIDATOR" run --root . --label validate
```

When no shared validator exists, spawn one `sam-cc-setup:build-validator` agent. That is a
fallback owner, not an additional pass. Give it the changed file list and print its report.

**Gate:**
- `VERDICT: PASS` → go to Completion.
- `VERDICT: FAIL` → go to the Fix Loop.
- `VERDICT: BLOCKED` → report the agent's reason to the user and stop.

### Fix Loop (triggered when the gate verdict is FAIL)

1. **Record** the exact failed check, exit code, and focused evidence
2. **Write** the smallest targeted repair plan
3. **Obtain approval** when the repair changes the agreed scope
4. **Implement** the repair, run the focused failing check, then re-run `/validate fix`

**Maximum iterations:** 3. After 3 fails on the same issue → stop and escalate.
Never bypass a failing check.

### Completion

Report every check with its exit status and the receipt fingerprint when present. Do not
run a standalone full test suite beside a configured full gate that already includes it.
Do not rerun a valid receipt to make it newer. Content validity, not age, controls reuse.
