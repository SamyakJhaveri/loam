---
name: improve-codebase-architecture
description: >
  Surface architectural friction and propose deepening opportunities using
  Ousterhout's vocabulary (Module, Interface, Seam, Depth, Leverage, Locality).
  Generates an HTML report with before/after diagrams. Use for periodic
  architectural review or after fixing a bug with architectural root cause.
  NOT for: surface-level tech debt (use /techdebt), code style review (use /multi-review).
auto-activate: false
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones.

## Glossary

Use these terms exactly. Full definitions in `LANGUAGE.md`.

- **Module** — anything with an interface and an implementation
- **Interface** — everything a caller must know (types, invariants, error modes, config)
- **Depth** — leverage at the interface: lots of behavior behind a small interface
- **Seam** — where behavior can be altered without editing in place
- **Adapter** — a concrete thing satisfying an interface at a seam
- **Leverage** — what callers get from depth
- **Locality** — what maintainers get from depth (change concentrated in one place)

Key principles:
- **Deletion test**: imagine deleting the module. If complexity vanishes, it was a pass-through. If it reappears across N callers, it was earning its keep.
- **The interface is the test surface.**
- **One adapter = hypothetical seam. Two adapters = real seam.**

This skill is informed by the project's domain model. If `DOMAIN.md` exists, read it — the domain language gives names to good seams. If ADRs exist, read them — they record decisions this skill should not re-litigate.

## Process

### 1. Explore

Read the project's `DOMAIN.md` and any ADRs first.

Then use the Agent tool with `subagent_type=Explore` to walk the codebase. Note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?

Apply the **deletion test** to anything you suspect is shallow.

### 2. Present Candidates as an HTML Report

Write a self-contained HTML file to the OS temp directory. Resolve from `$TMPDIR` (falling back to `/tmp`), write to `<tmpdir>/architecture-review-<timestamp>.html`. Open it for the user (`open <path>` on macOS).

The report uses **Tailwind via CDN** for styling and **Mermaid via CDN** for diagrams. See `HTML-REPORT.md` for the full scaffold.

For each candidate:

- **Files** — which files/modules are involved
- **Problem** — why the architecture is causing friction
- **Solution** — plain English description of the change
- **Benefits** — in terms of locality and leverage, and how tests would improve
- **Before / After diagram** — side-by-side, illustrating the shallowness and deepening
- **Recommendation strength** — `Strong`, `Worth exploring`, or `Speculative`

End with a **Top recommendation** section.

Use `DOMAIN.md` vocabulary for domain concepts and `LANGUAGE.md` vocabulary for architecture. If a candidate contradicts an existing ADR, only surface it if the friction warrants reopening.

Do NOT propose interfaces yet. Ask: "Which of these would you like to explore?"

### 3. Grilling Loop

Once the user picks a candidate, walk the design tree:

- **New concept not in glossary?** Add to `DOMAIN.md` (see `../grill-with-docs/DOMAIN-FORMAT.md`). Create lazily if needed.
- **Sharpening a fuzzy term?** Update `DOMAIN.md`.
- **User rejects with a load-bearing reason?** Offer an ADR (three-part test from `../grill-with-docs/ADR-FORMAT.md`).
- **Exploring alternative interfaces?** See `INTERFACE-DESIGN.md`.
