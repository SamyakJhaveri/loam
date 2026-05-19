---
name: spec-check
description: >
  Single-spec health check — verifies a spec document has required sections, references
  valid files, follows naming conventions, and has testable acceptance criteria. Use after
  editing a spec, before implementation begins, or as a quick sanity check. For bulk
  audits use the spec-auditor agent.
---

# Spec Health Check

Declarative verification for a single specification document. Reads the spec, checks
structure and references, and reports PASS/FAIL with diagnosis.

**Trigger:** `/spec-check <spec-name>`

## Arguments

- `$ARGUMENTS` — **required**: the spec name (e.g., `user-auth`, `batch-processor`)

If no argument is provided, prompt the user for a spec name.

## Workflow

### Step 1: Locate the Spec

Search for the spec document:
```bash
find specs/ docs/specs/ docs/contracts/ -name "*${ARGUMENTS}*" 2>/dev/null
```

If not found, report and suggest creating one with `/gen-spec`.

### Step 2: Structure Check

Verify the spec contains all required sections per `spec-conventions.md`:
- Identity (name, owner, status)
- Inputs (data sources, prerequisites)
- Behavior (what the feature/component does)
- Outputs (artifacts, side effects)
- Constraints (what it must NOT do)
- Acceptance Criteria (verifiable conditions)

### Step 3: Reference Check

For every file or resource referenced in the spec:
- Verify the file exists on disk
- Verify referenced APIs or interfaces exist in the codebase
- Flag broken references

### Step 4: Acceptance Criteria Quality

Check each acceptance criterion:
- Is it testable? (Can you write a test or command that verifies it?)
- Is it specific? (No "should work well" or "be fast enough")
- Is it independent? (Doesn't depend on other unwritten specs)

### Step 5: Naming Convention

Verify the spec filename and identity:
- Filename uses kebab-case (e.g., `user-auth.md`, not `userAuth.md`)
- Name in the Identity section matches the filename
- No special characters beyond hyphens

### Step 6: Constraint Completeness

Verify the "Constraints" or "Must NOT" section:
- Section exists and is non-empty
- Constraints are specific to this spec (not generic "don't do bad things")
- Constraints prevent documented failure modes, not hypothetical ones

### Step 7: Report

```
=== SPEC CHECK: <spec-name> ===
Status: PASS / FAIL

Structure:    [PASS/FAIL] — missing sections: <list>
References:   [PASS/FAIL] — broken refs: <list>
Criteria:     [PASS/FAIL] — vague criteria: <list>
Naming:       [PASS/FAIL] — kebab-case violations: <list>
Constraints:  [PASS/FAIL] — missing or generic constraints: <list>

Result: N PASS, M FAIL, K WARN
```

## Context Management

This skill runs synchronously in the main session. No subagents needed — it's a
single-spec check that completes quickly.
