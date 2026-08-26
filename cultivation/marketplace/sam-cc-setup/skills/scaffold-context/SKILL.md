---
name: scaffold-context
description: >
  Author a CONTEXT.md routing file for a specified project subdirectory using
  the canonical ICM anatomy (inlined below; richer if the authoring-context-docs
  skill is installed). Use when adding a new high-traffic area whose routing logic
  the root CLAUDE.md cannot describe economically. Skip for trivial directories.
  NOT for: editing existing CONTEXT.md files, authoring CLAUDE.md, or documenting project architecture - only new L1 routing files.
---

# scaffold-context

Generate a CONTEXT.md for a specified subdirectory following the canonical ICM
(Information Context Map) anatomy. The skill exists because authoring per-area
CONTEXT.md files by hand often produces stubs that violate ICM's own constraints -
empty Skip columns, vague "Use when needed" triggers, sizes outside the 25-80 line band.

## When to fire

User names a subdirectory and requests a CONTEXT.md, with phrasings such as:
- "Author a CONTEXT.md for `src/payments/`"
- "scaffold-context for `experiments/2026-05-baseline`"
- "Add ICM routing to `tests/integration/`"

Skip if:
- The subdirectory has fewer than ~5 files and one obvious purpose (over-routing).
- The routing is identical to the root CLAUDE.md (CONTEXT.md adds no information).
- The user has not named the target subdirectory and refuses to name one when asked.

## CONTEXT.md anatomy (canonical)

A CONTEXT.md is an L1 routing file: it tells an agent entering this subdirectory
what to load and what to skip for the tasks done here. Required sections, in order:

1. **What this area is** - 1-2 sentences.
2. **What to Load** - table: `Task | Load These | Skip These`. The Skip column must be
   non-empty for at least one row (skipping is the point of routing).
3. **Folder** - this area's own directory layout, NOT the whole project tree.
4. **The Process** - numbered steps for the dominant workflow, ending with a
   `Done looks like:` line (one verifiable sentence).
5. **Skills & Tools** (optional) - table: `Skill/Tool | When | Purpose`. Omit entirely
   if nothing wires here; never fill it with placeholders. Every `When` must be a real
   condition ("Before the test suite runs", "After every edit to `src/payments/`"),
   never "Available" or "Use when you need".
6. **What NOT to Do** - specific anti-patterns for this area.

Target 25-80 lines of real content.

**If the `authoring-context-docs` skill is installed, load it first** and follow its Part 2
template - it is the fuller source for this anatomy. Otherwise the six sections above are
sufficient.

## Process

1. If `<subdir>/CONTEXT.md` already exists, STOP and tell the user: this skill
   authors new routing files only (edit an existing one directly).
2. If the `authoring-context-docs` skill is available, invoke it and read its Part 2.
   Otherwise use the inlined anatomy above.
3. Walk the target subdirectory: enumerate files, identify workflow boundaries (e.g.,
   `output/`, `intermediate/`, `raw/`, `tests/`), note dominant file types.
4. Classify the dominant tasks performed in this area. If unclear from the file inventory,
   **ask the user before drafting** - do not invent tasks.
5. Ask the user: "What does successful work in this area look like? (One verifiable sentence.)"
   Include their answer as a `Done looks like:` line at the end of "The Process" section.
6. Identify which skills (from the project's `.claude/skills/` or installed plugins) wire to
   this area and under what trigger condition. If none, omit the Skills table; do not fill
   it with placeholders.
7. Identify reference files this area should explicitly **Skip** - older directories, raw data
   already summarized, sibling areas with overlapping content. The Skip column must be
   non-empty for at least one task row.
8. Draft `<subdir>/CONTEXT.md` with the six required sections in the order above.
9. Target 25-80 lines. If the area genuinely needs more, split into multiple CONTEXT.md files
   for distinct sub-areas rather than bloating one.
10. Print the drafted CONTEXT.md to the user as a diff/preview.
11. Ask the user to review before writing to disk. On approval, write to `<subdir>/CONTEXT.md`.

## Must NOT include

- **Empty stubs.** ICM constraint: CONTEXT.md must be 25-80 lines of real content. Stubs invite
  the model to read them as authoritative when they are not.
- **Mirrored content from root CLAUDE.md.** If the routing is identical, the subdirectory should
  not have its own CONTEXT.md.
- **Vague "When" triggers.** Each Skill row must have a condition like "Before validate runs" or
  "After every edit to `src/payments/`". Triggers like "Available", "Useful for X", "Use when you
  need" are rejected.
- **Folder section that duplicates the project tree.** The Folder section is for *this area's*
  layout only.

## Done looks like

- `<subdir>/CONTEXT.md` exists, between 25 and 80 lines.
- All six required sections present (with Skills & Tools optional).
- Skip column non-empty for at least one task row.
- Every Skill row has a non-trivial When trigger.
- "The Process" section ends with a `Done looks like:` line from the user.
- The user has acknowledged the draft.
