---
name: gen-spec
description: >
  Guided specification generation wizard. Use when adding a new feature, API endpoint,
  or component — forces a written spec before implementation. Validates scope, drafts
  a structured spec, checks it against conventions, and registers it in the project.
---

# Spec Generation Workflow

Structured workflow for generating a specification document before writing any
implementation code. Specs-before-code prevents scope drift and makes review cheaper.

## Arguments
- `$ARGUMENTS` — one of:
  - `<name>` — feature or component name (e.g., "user-auth", "batch-processor") → full generation workflow
  - `validate <path>` — run spec health check on an existing spec (former `/spec-check`)

## Workflow

### Phase 1: Scope Validation
- Confirm the feature/component boundaries with the user
- Identify dependencies and integration points
- Check for existing specs that overlap (avoid duplication)
- Review related stage contracts if any exist

### Phase 2: Draft Spec
- Create `specs/<name>.md` (or `.yaml` / `.json` per project convention)
- Follow the spec template from `.claude/rules/spec-conventions.md`
- Required sections: Identity, Inputs, Behavior, Outputs, Constraints, Acceptance Criteria
- Link to related specs, ADRs, or design docs

### Phase 3: Validate (inline spec health check)

Run the full validation checklist (formerly `/spec-check`):

1. **Structure check** — verify all required sections per `spec-conventions.md`:
   Identity, Inputs, Behavior, Outputs, Constraints, Acceptance Criteria
2. **Reference check** — for every file or resource referenced, verify it exists on disk
3. **Acceptance criteria quality** — each criterion must be testable, specific, and independent
4. **Naming convention** — filename uses kebab-case, Identity name matches filename
5. **Constraint completeness** — Constraints section is non-empty with spec-specific exclusions
   (not generic "don't do bad things")

Report as:
```
=== SPEC CHECK: <name> ===
Structure:   [PASS/FAIL]
References:  [PASS/FAIL]
Criteria:    [PASS/FAIL]
Naming:      [PASS/FAIL]
Constraints: [PASS/FAIL]
```

If any check fails, fix before proceeding.

### Phase 4: Review
- Run the plan-reviewer agent for adversarial review
- Address any findings before marking the spec as ready
- Get user sign-off on the final spec

### Phase 5: Register
- Add the spec to the project's spec index (if one exists)
- Cross-reference in relevant CONTEXT.md files
- The spec is now the source of truth for implementation

## Principles
- A spec is a contract, not a wishlist — every statement should be verifiable
- Acceptance criteria are the spec's value — if they're vague, the spec is vague
- The spec drives implementation, not the reverse — don't retrofit specs to match code
- Keep specs DRY with stage contracts — a spec describes WHAT, a stage contract describes HOW

---

## Validate Mode (`/gen-spec validate <path>`)

When `$ARGUMENTS` starts with `validate`, run only Phase 3 (spec health check) against
the specified spec file. Skip generation phases. Report PASS/FAIL with diagnosis.

Search order for the spec: `specs/`, `docs/specs/`, `docs/contracts/`, then literal path.
