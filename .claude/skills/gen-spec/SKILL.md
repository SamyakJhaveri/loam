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
- `$ARGUMENTS` — feature or component name (e.g., "user-auth", "batch-processor")

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

### Phase 3: Validate
- Run `/spec-check <name>` to check against conventions
- Verify all referenced files and resources exist
- Ensure acceptance criteria are verifiable (not vague)

### Phase 4: Review
- Run the spec-auditor agent for adversarial review
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
