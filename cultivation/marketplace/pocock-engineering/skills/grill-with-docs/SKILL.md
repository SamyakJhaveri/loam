---
name: grill-with-docs
description: >
  Stress-test plans against the project's domain model through relentless
  questioning. Updates DOMAIN.md glossary and creates ADRs inline as decisions
  crystallize. Use before implementation when the domain language is fuzzy
  or the plan has implicit assumptions. NOT for: code review (use /multi-review),
  spec generation (use /gen-spec), or editing CONTEXT.md routing files.
auto-activate: false
---

# Grill With Docs

Stress-test plans against existing domain models and documentation through relentless questioning.

## Arguments

`$ARGUMENTS` — the plan, proposal, or design to grill (free-form description or file path)

## Workflow

### Phase 1: Load Domain Context

- Look for existing `DOMAIN.md` or `DOMAIN-MAP.md` at the project root or in the relevant subdirectory
- Check for ADRs in `docs/adr/` if the directory exists
- Read the relevant codebase area to understand current behavior

**Important:** This skill works with `DOMAIN.md` for domain glossary. It does NOT read or write `CONTEXT.md`, which is reserved for ICM L1 routing.

### Phase 2: Grill

Ask one question at a time. Wait for feedback before proceeding.

- Challenge vague terminology against the glossary: "Your glossary defines 'cancellation' as X, but you seem to mean Y"
- Probe edge cases with concrete scenarios, not abstract "what ifs"
- Surface contradictions between stated intent and code behavior
- Explore the codebase when answers are available there instead of asking the user

### Phase 3: Capture (inline, as decisions crystallize)

**Naming a concept not in the glossary?** Add the term to `DOMAIN.md` with a definition and _Avoid_ aliases. Create `DOMAIN.md` lazily if it doesn't exist — see `DOMAIN-FORMAT.md` for the structure.

**Sharpening a fuzzy term?** Update the definition in `DOMAIN.md` right there.

**User rejects a direction with a load-bearing reason?** Offer an ADR:
> "Want me to record this as an ADR so future reviews don't re-suggest it?"

Only offer when the reason would be needed by a future explorer. Skip ephemeral reasons ("not worth it right now") and self-evident ones. See `ADR-FORMAT.md` for the format and the three-part test.

## Rules

1. One question at a time — never a batch of questions
2. Never write to `CONTEXT.md` — domain glossary lives in `DOMAIN.md`
3. Create files lazily — only when there's content to capture
4. ADRs only when the decision is hard to reverse, surprising, AND a genuine trade-off (three-part test)
