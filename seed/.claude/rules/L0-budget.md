# L0 — CLAUDE.md token budget

> Read when: authoring or refactoring a project's root `CLAUDE.md` or considering moving content between routing layers.

## What L0 is

In the ICM routing model (JVC `constraints/03-context-hygiene.md:48-55`), L0 is the always-loaded entry file at the project root. For Claude Code, that file is `CLAUDE.md`. It answers exactly one question: **where am I?** It is a map, not a manual.

## Budget

Target: **~800 tokens** (roughly 60-100 lines of dense Markdown, depending on table density). Hard ceiling: 200 lines per `docs/MEMORY.md` cap.

Every additional token in `CLAUDE.md` is paid by every session, including ones that never use the information. The cost compounds across long-running agents and parallel subagents.

## What `CLAUDE.md` must contain

1. **What this project is** — one or two sentences. Not marketing.
2. **Folder map** — top-level layout, with one-line purpose per entry. Treat as a navigation table, not a description.
3. **Reference doc index** — `.claude/rules/*.md` and `docs/*.md` pointers with a single-clause description of when to read each. Use a "load on demand" framing.
4. **Workflow anchor** — one sentence stating the canonical sequence (e.g., "implement → /session-critique → /validate → /commit → /pr") and where the full version lives.

## What `CLAUDE.md` must NOT contain

- Detailed instructions on how to do anything (those live in `.claude/rules/` or skills)
- Architectural decisions in narrative form (those live in `docs/` or ADRs)
- Code style rules (those live in path-scoped `.claude/rules/python.md`, `.claude/rules/architecture.md`, etc.)
- Worked examples (those live in skill `examples.md` or `reference.md`)
- Project history, session logs, or "what we tried" notes (those live in `docs/plans/` or session handoffs)

## When `CLAUDE.md` is over budget

The fix is never to delete content. The fix is to move it to the right layer:

| If the content is… | Move to |
|---|---|
| Authoring rules for a specific file type | `.claude/rules/<lang>.md`, path-scoped |
| A repeating workflow with steps | `.claude/skills/<name>/SKILL.md` |
| Reference material consulted occasionally | `docs/<topic>.md` |
| State / decisions / current status | A status block in `CLAUDE.md` (≤10 lines) plus an ADR file |
| Per-subdirectory routing | A `CONTEXT.md` in that subdirectory (L1) |

Replace the moved content in `CLAUDE.md` with a single line: "See `.claude/rules/X.md` (when working on Y)."

## L0 vs L1 vs L2

| Layer | File | Question | Load timing | Budget |
|---|---|---|---|---|
| L0 | `CLAUDE.md` | Where am I? | Always | ~800 tokens |
| L1 | `<subdir>/CONTEXT.md` | Where do I go inside this area? | On entry | ~300 tokens |
| L2 | Stage contract | What do I do for this task? | Per task | 200-500 tokens |

If you find yourself writing a section in `CLAUDE.md` that answers "what do I do when…" rather than "where do I look for…", that section belongs in L1 or L2, not L0.

## Source

JVC `constraints/03-context-hygiene.md` lines 48-83 (ICM layers + token-budget heuristic); `_examples/03-context-md-anatomy.md` (companion anatomy for L1 files).
