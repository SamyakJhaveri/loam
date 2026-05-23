---
name: prototype
description: >
  Build throwaway prototypes to answer specific design or logic questions.
  Two branches — logic (terminal apps) and UI (multiple radical variations).
  Delete when done. Use before committing to a full implementation when the
  design space is uncertain. NOT for: production code, features, or bug fixes.
auto-activate: false
---

# Prototype

Disposable code designed to answer a specific question before committing to full implementation.

## Arguments

`$ARGUMENTS` — the question this prototype should answer

## Phase 1: Identify the Question

State the specific question this prototype will answer. If the question is vague ("should we use X?"), sharpen it ("does X handle concurrent writes without data loss?").

## Phase 2: Choose Branch

### Logic Branch
For state machines, business logic, algorithms, or data transformations:
- Build a tiny interactive terminal app
- Push the logic through cases that are hard to reason about on paper
- Display full state after each action so changes are visible
- Keep state in memory — no persistence unless that's what you're testing

### UI Branch
For visual design, layout, or interaction patterns:
- Generate multiple UI variations on a single route
- Toggle between variations via URL parameters and a floating control bar
- Make variations radically different, not incremental tweaks
- Side-by-side comparison reveals which approach works

## Rules

1. Mark prototypes as throwaway from the start — locate them in a `prototype/` directory near the code they test
2. Provide a single command to run the prototype without additional setup
3. Keep state in memory; no persistence unless explicitly testing persistence
4. Skip polish — no tests, error handling, or abstractions beyond running
5. Skip confirmation for in-memory and filesystem-local prototype execution. Still confirm before network calls, database writes, or external API requests — even in throwaway code.

## Phase 3: After Testing

1. Document the question and answer somewhere permanent (commit message, ADR, or notes file)
2. Delete the prototype code — do not let it decay in the repository
3. If the answer changes the implementation approach, update the spec or plan accordingly
