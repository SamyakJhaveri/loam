---
name: spec-validator
description: >
  Validates spec documents against project conventions defined in spec-conventions.md.
  Use when creating or modifying specs, before implementation begins, or as a pre-flight
  check. Checks naming, structure, cross-references, and acceptance criteria quality.
  More thorough than a manual review — enforces conventions that are easy to miss.
---

# Spec Validator

Validates specification documents against project conventions. Goes beyond structural
checks to enforce the project's rules about naming, cross-references, and quality.

**Trigger:** `/spec-validator <spec-name>` or when creating/modifying specs.

## Arguments

- `$ARGUMENTS` — spec name (e.g., `user-auth`)
- If no argument, validate all specs in the project's spec directory.

## Validation Checks

### 1. Naming Convention (MUST PASS)
- Spec filename uses kebab-case: `<name>.md` or `<name>.yaml`
- Name in the Identity section matches the filename
- No special characters beyond hyphens

### 2. Required Sections (MUST PASS)
- All sections from spec-conventions.md are present
- Sections are non-empty (no placeholder text like "TBD" or "TODO")

### 3. Acceptance Criteria Quality (MUST PASS)
- Each criterion is a concrete, verifiable statement
- Criteria don't use vague language: "should be fast", "works well", "handles edge cases"
- At least one criterion per spec

### 4. Cross-References
- Referenced specs exist
- Referenced files exist on disk
- Referenced APIs or interfaces exist in the codebase

### 5. Constraint Completeness
- The "Constraints" or "Must NOT" section exists and is non-empty
- Constraints are specific to this spec (not generic "don't do bad things")

## Output Format

```
=== SPEC VALIDATION: <spec-name> ===

[PASS] Naming — follows kebab-case convention
[PASS] Structure — all required sections present
[FAIL] Criteria — criterion 3 uses vague language ("should be efficient")
       Fix: Replace with measurable criterion (e.g., "responds in <200ms at p95")
[PASS] Cross-refs — all references resolve
[PASS] Constraints — specific and actionable

Result: 4 PASS, 1 FAIL
```

## Integration

- Runs as pre-flight before implementation begins
- Complements spec-auditor agent (which does bulk validation)
- Complements /spec-check (which also checks individual specs)
- Feeds into /gen-spec as post-generation validation
