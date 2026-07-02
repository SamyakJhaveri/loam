# Naming Conventions

> Read when: creating files or directories, authoring CONTEXT.md files, or reviewing
> project structure.

## Load-bearing names

A name is the cheapest documentation you have. `01_research/` packs two facts into a
handful of characters — it runs first, and it holds research — while `stuff/` packs none.
When names encode order, role, and content, the directory tree explains itself and you
write less prose to make up for it. That is the whole game: let the structure do the
documenting so a reader — or a fresh agent — can navigate without a separate guide.

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
