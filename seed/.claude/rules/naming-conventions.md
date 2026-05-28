# Naming Conventions

> Read when: creating files or directories, authoring CONTEXT.md files, or reviewing
> project structure.

## Load-bearing names

Naming conventions are load-bearing documentation (JVC Constraint 08). A folder called
`01_research` tells you two things: this is the first stage, and it contains research.
A folder called `stuff` tells you nothing. Consistent, descriptive naming reduces the
need for external documentation because the structure self-documents.

## Patterns

| Pattern | When to use | Example |
|---------|-------------|---------|
| Numbered prefix (`01_`, `02_`) | Encode execution order in sequential workflows | `01_research/`, `02_analysis/` |
| Underscore prefix (`_config`) | Mark support files (not workflow stages) | `_prompts/`, `_reference/` |
| Date prefix (`YYYY-MM-DD`) | Chronological files (logs, plans, handoffs) | `2026-05-27-gap-closure.md` |
| Status suffix (`_draft`, `_final`) | Track lifecycle state | `proposal_draft.md` |
| Kebab-case | Multi-word file and directory names | `scaling-vs-automating.md` |

## Anti-patterns

- Generic names: `stuff/`, `misc/`, `temp/`, `new_file.md`, `test.py`
- Acronyms without context: `pba/` (what does PBA stand for?)
- Mixed conventions in the same directory level
- CamelCase for non-code files (use kebab-case for markdown, configs, docs)

## Source

JVC `constraints/08-handoff-readiness.md` (naming as self-documenting structure).
