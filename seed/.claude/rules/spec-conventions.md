---
paths:
  - "specs/**"
  - "docs/specs/**"
  - "docs/contracts/**"
---

# Spec & Contract Conventions

> Auto-loaded when working on spec documents or contracts.

## Spec Document Structure

Every specification document must contain these sections:

| Section | Purpose |
|---------|---------|
| **Identity** | Name, owner, status (draft/ready/implemented/deprecated) |
| **Inputs** | Data sources, prerequisites, dependencies |
| **Behavior** | What the feature/component does — the functional description |
| **Outputs** | Artifacts produced, side effects, state changes |
| **Constraints** | What it must NOT do — specific exclusions, not generic |
| **Acceptance Criteria** | Verifiable conditions that define "done" |

## Naming Convention

- Filenames: kebab-case, descriptive (e.g., `user-authentication.md`, `batch-processor.yaml`)
- Identity name must match the filename (without extension)
- Use the format appropriate to the project (markdown for prose, YAML/JSON for structured)

## Acceptance Criteria Rules

Criteria must be:
- **Verifiable**: Can you write a test, run a command, or check a file to confirm it?
- **Specific**: No "should be fast" — use "responds in <200ms at p95"
- **Independent**: Each criterion is testable on its own
- **Atomic**: One condition per criterion, not compound statements

## The Stranger Test

Before finalizing any spec or task description, apply this gate: could a stranger
(or a fresh Claude Code session with zero context) start working on this without
asking follow-up questions? If not, the spec is incomplete. Check:

- Can you describe the expected output in one sentence?
- Are acceptance criteria verifiable by reading the output alone?
- Would removing any section cause ambiguity about what "done" means?

Source: JVC Constraint 02 ("If you cannot describe your expected output in one
sentence, the model cannot hit it") and Foundation Course 1.3 (the stranger test).

## Spec Lifecycle

1. **Draft** — created via `/gen-spec`, not yet validated
2. **Ready** — passed `/spec-check`, reviewed by plan-reviewer (spec audit mode), approved by user
3. **Implemented** — code exists that satisfies all acceptance criteria
4. **Deprecated** — superseded by a newer spec or no longer relevant

## Relationship to Stage Contracts

Specs describe WHAT to build. Stage contracts (`.claude/rules/stage-contract.md`) describe
HOW to build it in a single implementation pass. A spec may spawn multiple stage contracts
if the implementation is multi-phase. Don't duplicate — reference.
