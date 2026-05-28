---
name: scaffold-context
description: >
  Author a CONTEXT.md routing file for a specified project subdirectory using
  the canonical ICM anatomy (.claude/rules/context-md-anatomy.md). Use when
  adding a new high-traffic area whose routing logic the root CLAUDE.md cannot
  describe economically. Skip for trivial directories.
  NOT for: editing existing CONTEXT.md files, authoring CLAUDE.md, or documenting project architecture — only new L1 routing files.
auto-activate: true
---

# scaffold-context

Generate a CONTEXT.md for a specified subdirectory following the canonical anatomy in `.claude/rules/context-md-anatomy.md`. The skill exists because authoring per-area CONTEXT.md files by hand often produces stubs that violate ICM's own constraints — empty Skip columns, vague "Use when needed" triggers, sizes outside the 25-80 line band.

## When to fire

User names a subdirectory and requests a CONTEXT.md, with phrasings such as:
- "Author a CONTEXT.md for `src/payments/`"
- "scaffold-context for `experiments/2026-05-baseline`"
- "Add ICM routing to `tests/integration/`"

Skip if:
- The subdirectory has fewer than ~5 files and one obvious purpose (over-routing).
- The routing is identical to the root CLAUDE.md (CONTEXT.md adds no information).
- The user has not named the target subdirectory and refuses to name one when asked.

## Process

1. Read `.claude/rules/context-md-anatomy.md` if not already in context.
2. Walk the target subdirectory: enumerate files, identify workflow boundaries (e.g., `output/`, `intermediate/`, `raw/`, `tests/`), note dominant file types.
3. Classify the dominant tasks performed in this area. If unclear from the file inventory, **ask the user before drafting** — do not invent tasks.
4. Ask the user: "What does successful work in this area look like? (One verifiable sentence.)" Include their answer as a `Done looks like:` line at the end of "The Process" section in the generated CONTEXT.md.
5. Identify which skills (from `.claude/skills/`) wire to this area and under what trigger condition. If none, the Skills table can be omitted; do not fill it with placeholders.
6. Identify reference files this area should explicitly **Skip** — older directories, raw data already summarized, sibling areas with overlapping content. The Skip column must be non-empty for at least one task row.
7. Draft `<subdir>/CONTEXT.md` with all six required sections in this order:
   - What this area is (1-2 sentences)
   - What to Load (table: Task | Load These | Skip These)
   - Folder (this area's directory layout — NOT the project tree)
   - The Process (numbered steps for the dominant workflow)
   - Skills & Tools (table: Skill/Tool | When | Purpose) — omit entirely if no skills wire here
   - What NOT to Do (specific anti-patterns)
8. Target 25-80 lines. If the area genuinely needs more, split into multiple CONTEXT.md files for distinct sub-areas rather than bloating one.
9. Print the drafted CONTEXT.md to the user as a diff/preview.
10. Ask the user to review before writing to disk. On approval, write to `<subdir>/CONTEXT.md`.

## Must NOT include

- **Empty stubs.** ICM constraint: CONTEXT.md must be 25-80 lines of real content. Stubs invite the model to read them as authoritative when they are not.
- **Mirrored content from root CLAUDE.md.** If the routing is identical, the subdirectory should not have its own CONTEXT.md.
- **Vague "When" triggers.** Each Skill row must have a condition like "Before validate runs" or "After every edit to `src/payments/`". Triggers like "Available", "Useful for X", "Use when you need" are rejected.
- **Folder section that duplicates the project tree.** The Folder section is for *this area's* layout only.

## Done looks like

- `<subdir>/CONTEXT.md` exists, between 25 and 80 lines.
- All six required sections present (with Skills & Tools optional).
- Skip column non-empty for at least one task row.
- Every Skill row has a non-trivial When trigger.
- "The Process" section ends with a `Done looks like:` line from the user.
- The user has acknowledged the draft.

## Source

`.claude/rules/context-md-anatomy.md` (canonical template); JVC `_examples/03-context-md-anatomy.md` (the source ICM document this skill operationalizes).
