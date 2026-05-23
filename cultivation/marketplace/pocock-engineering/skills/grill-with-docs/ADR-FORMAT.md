# ADR Format

Architecture Decision Records live in `docs/adr/` with sequential naming (`0001-slug.md`, `0002-slug.md`). Create the directory only when the first ADR is needed.

## Three-Part Test

An ADR warrants creation only when ALL three conditions apply:

1. **Difficult reversal** — meaningful cost to changing course later
2. **Non-obvious reasoning** — future readers would question the approach
3. **Genuine trade-offs** — real alternatives existed and specific reasons drove the choice

Skip ADRs for: trivial decisions, immediately obvious choices, decisions with no reasonable alternatives.

## Minimal Template

```md
# ADR-NNNN: {Title}

{A single paragraph covering: the context, the decision made, and the reasoning.}
```

## Optional Sections

Add only when genuinely useful:

- **Status:** proposed | accepted | deprecated | superseded by ADR-NNNN
- **Considered Options:** when rejected alternatives are valuable to document
- **Consequences:** when downstream effects are non-obvious

## What Warrants an ADR

- Architectural patterns (e.g., event sourcing over CRUD)
- Integration approaches between systems
- Technology selections with switching costs
- Ownership boundaries
- Intentional departures from convention
- Non-code constraints (legal, compliance, performance SLAs)
- Subtle rejections of reasonable alternatives
