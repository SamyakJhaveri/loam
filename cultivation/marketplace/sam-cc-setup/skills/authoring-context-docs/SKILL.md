---
name: authoring-context-docs
description: >
  Sizing and anatomy rules for the two routing layers - the root CLAUDE.md (L0)
  and a subdirectory CONTEXT.md (L1). Use when authoring or refactoring the root
  CLAUDE.md, when it is over budget, when deciding whether content belongs in
  CLAUDE.md vs a rule file vs a skill, or when hand-writing a CONTEXT.md. To
  *generate* a CONTEXT.md from scratch, use /scaffold-context instead - it
  operationalizes Part 2 of this skill. NOT for: writing the project's
  architecture, design, or API documentation; authoring a skill body; or editing
  an existing CONTEXT.md whose shape is already settled.
---

# Authoring context docs (L0 + L1)

Both parts below are authoring rules. They are a skill rather than an always-loaded rule file
because they are only ever relevant while writing these documents - the body loads on
invocation instead of in every session. The caveat at the end of Part 1 explains why a rule
file could not have done this.

`/scaffold-context` generates a `CONTEXT.md` and cites Part 2 below as its canonical anatomy.
Read this skill when you are writing by hand or deciding where content belongs; use that skill
when you want a file produced for you.

---

# Part 1 - L0: the `CLAUDE.md` token budget

> Read when: authoring or refactoring a project's root `CLAUDE.md`, or considering moving content between routing layers.

## What L0 is

L0 is the always-loaded entry file at the project root. For Claude Code, that file is
`CLAUDE.md`. It answers exactly one question: **where am I?** It is a map, not a manual.

## Budget

Target: **~800 tokens** (roughly 60-100 lines of dense Markdown, depending on table density). Hard ceiling: 200 lines.

Every additional token in `CLAUDE.md` is paid by every session, including ones that never use the information. The cost compounds across long-running agents and parallel subagents.

## What `CLAUDE.md` must contain

1. **What this project is** - one or two sentences. Not marketing.
2. **Folder map** - top-level layout, with one-line purpose per entry. Treat as a navigation table, not a description.
3. **Reference doc index** - `.claude/rules/*.md` and `docs/*.md` pointers with a single-clause description of when to read each. Use a "load on demand" framing.
4. **Workflow anchor** - one sentence stating the canonical sequence (e.g., "implement → /validate → commit → review") and where the full version lives.

## What `CLAUDE.md` must NOT contain

- Detailed instructions on how to do anything (those live in `.claude/rules/` or skills)
- Architectural decisions in narrative form (those live in `docs/` or ADRs)
- Code style rules (those live in path-scoped `.claude/rules/python.md`, `.claude/rules/tech-stack.md`, etc.)
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

## A caveat the rule file could not state

An unscoped file in `.claude/rules/` is loaded in **every** session, exactly like `CLAUDE.md` - only files carrying `paths:` frontmatter are conditional. And `paths:` fires on **read**, not write (claude-code#23478), so a rule whose trigger is *authoring* a file can never be made conditional that way. A skill is the only real lazy-loading mechanism for authoring guidance. That is why this file is a skill.

---

# Part 2 - L1: `CONTEXT.md` anatomy

> Read when: authoring a `CONTEXT.md` for a project subdirectory, or generating one via `/scaffold-context`.

## What CONTEXT.md is

A `CONTEXT.md` is the L1 routing file for a specific subdirectory. It answers: **where do I go
inside this area?** Target budget: ~300 tokens, 25-80 lines. Above 80 lines, suspect bloat.
Above 120 lines, split or move detail to `docs/`.

A subdirectory does not need a `CONTEXT.md`. Add one only when the area has its own routing logic - distinct skills, distinct load rules, distinct process - that the root `CLAUDE.md` cannot economically describe in a single map row.

## Six required sections

```markdown
# CONTEXT.md - <area name>

## What this area is
<one or two sentences>

## What to Load

| Task | Load These | Skip These |
|------|------------|------------|
| <task A> | path/foo.md, path/bar.md | path/baz.md, path/quux.md |
| <task B> | ... | ... |

## Folder
<this area's directory layout - NOT the project tree>

## The Process
<1-N numbered steps for the dominant workflow in this area>

## Skills & Tools

| Skill / Tool | When | Purpose |
|--------------|------|---------|
| `/validate` | Before commit | Pipeline gate |
| `<tool>` | <condition> | <purpose> |

## What NOT to Do
- <specific anti-pattern>
- <specific anti-pattern>
```

## The Skip column is load-bearing

This is the part most authors get wrong. Loading the right thing is good; **not** loading the
wrong thing is critical - it saves tokens and prevents confusion. The Skip column is what makes
the table earn its keep over an unconstrained Read tool.

Examples of useful Skip entries:
- "Skip: the legacy `./old/` directory - superseded by `./current/` in v2."
- "Skip: `experiments/<id>/raw/` - already summarized in `experiments/<id>/findings.md`; reading raw inflates context without new signal."

## "When" triggers must be conditions, not statuses

The Skills column needs a real trigger. "Available" is not a trigger. "Useful for X" is not a trigger.

| Bad trigger | Good trigger |
|-------------|--------------|
| "Available for testing" | "Before the validate gate runs" |
| "Use when you need" | "After every edit to `src/<module>/`" |
| "For complex tasks" | "When the task requires N>3 file edits across distinct subsystems" |

If you cannot write a trigger that another reader (or the model in a fresh session) would reliably classify, the skill probably doesn't belong in this area's routing.

## Sizing discipline

| Lines | Diagnosis |
|-------|-----------|
| <15 | Too thin - likely missing the Process or What-NOT sections |
| 25-80 | Right |
| 80-120 | Bloated - move detail to sibling docs |
| >120 | Split into two CONTEXT.md files for distinct sub-areas |

Stable knowledge - design docs, architecture rationale, glossaries - belongs in `docs/`. The CONTEXT.md is routing and process, not encyclopedia.

## Routing tables vs. reference tables

Task routing tables (`Task | Go to | Read | Skills`) are an L1 pattern.
They belong in CONTEXT.md files, not in the root CLAUDE.md.

CLAUDE.md uses a *reference* routing table (`File | Read when`) that points
to on-demand docs. This is navigation (L0), not task routing (L1).

If you find yourself adding task-specific routing to CLAUDE.md, move it to the
relevant subdirectory's CONTEXT.md instead.
