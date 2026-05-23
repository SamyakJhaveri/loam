---
name: tdd
description: >
  Red-green-refactor TDD with vertical slices. Write one test, make it pass,
  repeat. Anti-horizontal-slice discipline — never write all tests upfront.
  Use when implementing any feature or bugfix where tests are appropriate.
  Coexists with superpowers:test-driven-development — this skill emphasizes
  anti-horizontal-slice discipline and explicit Pipeline Gate integration.
  NOT for: exploratory prototyping (use /prototype), legacy code without test infrastructure.
auto-activate: false
---

# Test-Driven Development

Red-green-refactor with vertical slices. One test at a time, minimal implementation, refactor only after green.

## Arguments

`$ARGUMENTS` — feature or behavior to implement

## Core Principle

Tests verify behavior through public interfaces, not implementation details. A good test survives internal refactoring without modification. A bad test breaks when internals change despite unchanged behavior.

## Critical Anti-Pattern: Horizontal Slicing

Never write all tests upfront before implementation. Tests written before any implementation verify imaginary behavior and data shapes, not real functionality. Instead, use vertical slices: one test paired with minimal implementation, repeated.

## Workflow

### Phase 1: Plan

- Confirm interfaces and prioritized behaviors with the user
- List behaviors to implement in priority order
- Do NOT write any tests or code yet

### Phase 2: Tracer Bullet

Write ONE test for the highest-priority behavior. Run it — watch it fail (red). Write the minimal code to make it pass (green). This validates the end-to-end path.

### Phase 3: Incremental Loop

For each remaining behavior:

1. **Red** — Write one test that describes the next behavior. Run it. It must fail.
2. **Green** — Write only the code necessary to pass this test. No more.
3. **Check** — Verify all previous tests still pass.
4. Repeat.

### Phase 4: Refactor

Only after ALL tests pass:
- Remove duplication
- Deepen modules (consolidate complexity behind clean interfaces)
- Extract only when a pattern appears 3+ times
- Run all tests after each refactor step

### Per-Cycle Validation

After each red-green cycle, verify:
- Does the test describe observable behavior (not implementation)?
- Does the test use only public interfaces?
- Would this test survive internal refactoring?

If any answer is "no," rewrite the test before proceeding.

## Integration with Loam

After all tests pass, run `/validate` before committing. The TDD cycle feeds into the Pipeline Gate:

```
TDD cycles → all green → /validate → /commit
```

## Mocking Guidelines

- Mock at system boundaries (external APIs, databases, file systems)
- Never mock the code under test or its direct collaborators
- If mocking makes the test hard to write, the design may need improvement — that's a signal, not a problem to work around
