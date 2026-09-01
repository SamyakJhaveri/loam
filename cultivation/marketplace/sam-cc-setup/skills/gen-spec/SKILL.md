---
name: gen-spec
description: >
  Guided specification generation wizard. Use when adding a new feature, API
  endpoint, or component, to force a written spec before implementation:
  validates scope, drafts a structured spec against the six required sections,
  runs a five-check health validation, and registers it in the project. Also
  runs standalone as `validate <path>` to health-check an existing spec. NOT
  for: single-file bug fixes, refactors with no new behavior, or
  documentation-only changes.
argument-hint: "<feature-name> | validate <path-to-spec>"
---

# gen-spec

Structured workflow for generating a specification document before writing any implementation code.
Specs-before-code prevents scope drift and makes review cheaper.

## Arguments

`$ARGUMENTS` is one of:

- `<name>` - feature or component name (e.g. `user-auth`, `batch-processor`), which runs the full generation workflow.
- `validate <path>` - run the spec health check on an existing spec and nothing else (Phase 3 only).

## The six required sections

Every spec this skill writes or validates has exactly these sections, in this order.
This is the template; there is no separate conventions file to consult.

1. **Identity** - the spec's name (kebab-case, matching the filename), one-sentence purpose, status (`draft` / `approved` / `implemented`), and links to related specs, ADRs, or design docs.
2. **Inputs** - every input the feature consumes: parameters, files, environment, upstream data, and their types and sources. Name where each comes from.
3. **Behavior** - what the feature does with those inputs, including the ordering that matters, the state it touches, and the error paths. Describe WHAT, not the implementation's HOW.
4. **Outputs** - what leaves the feature: return values, written files, emitted events, side effects, and their shapes.
5. **Constraints** - the boundaries that bind this spec specifically: what it must NOT do, what it must not touch, performance or compatibility limits, and explicit non-goals. Generic filler ("don't write bad code") does not count as a constraint.
6. **Acceptance Criteria** - the checkable conditions for "done". Each criterion is testable, specific, and independent of the others.

## Workflow

### Phase 1: Scope validation

- Confirm the feature or component boundaries with the user.
- Identify dependencies and integration points.
- Search the project for existing specs that overlap, and avoid duplicating them.
- Review any related interface or stage contracts that already exist.
- If a decision inside the scope warrants an ADR, apply the three-part test. Write the ADR only when all three hold: the decision is (1) hard to reverse, (2) surprising to a future reader, and (3) a genuine trade-off with real alternatives. Skip ADRs for trivial or self-evident decisions.

### Phase 2: Draft the spec

- Create `specs/<name>.md`, or the project's established spec location and format (`.yaml` / `.json`) if it has one.
- Write all six required sections above, in order.
- Link to related specs, ADRs, or design docs from the Identity section.

### Phase 3: Validate (spec health check)

Run all five checks.

1. **Structure** - all six required sections are present and non-empty: Identity, Inputs, Behavior, Outputs, Constraints, Acceptance Criteria.
2. **References** - for every file or resource the spec references, verify it exists on disk.
3. **Criteria quality** - each acceptance criterion is testable, specific, and independent. A criterion nobody can check fails this.
4. **Naming** - the filename is kebab-case and the Identity name matches the filename.
5. **Constraints** - the Constraints section is non-empty and carries spec-specific exclusions, not generic boilerplate.

Report exactly this shape:

```
=== SPEC CHECK: <name> ===
Structure:   [PASS/FAIL]
References:  [PASS/FAIL]
Criteria:    [PASS/FAIL]
Naming:      [PASS/FAIL]
Constraints: [PASS/FAIL]
```

Every FAIL gets a one-line diagnosis naming what is missing or wrong.
Fix all failures before proceeding to Phase 4.

### Phase 4: Review

- Run an adversarial plan review over the spec (the `/plan-review` skill, if installed, or a blind reviewer subagent otherwise).
- Address the findings before marking the spec ready.
- Get user sign-off on the final spec.

### Phase 5: Register

- Add the spec to the project's spec index, if one exists.
- Cross-reference it from the routing docs (`CONTEXT.md`, `CLAUDE.md`, or equivalent) for the area it governs.
- The spec is now the source of truth for implementation.

## Validate mode

When `$ARGUMENTS` starts with `validate`, run **only Phase 3** against the named spec file and report PASS/FAIL with diagnosis.
Skip the generation phases entirely; write nothing.

Search order for the spec path: `specs/`, `docs/specs/`, `docs/contracts/`, then the literal path as given.

## Principles

- A spec is a contract, not a wishlist. Every statement should be verifiable.
- Acceptance criteria are the spec's value. If they are vague, the spec is vague.
- The spec drives implementation, not the reverse. Never retrofit a spec to match code already written.
- Keep specs DRY against interface contracts: a spec describes WHAT, a contract describes HOW.
