# CONTEXT.md anatomy (L1)

> Read when: authoring a `CONTEXT.md` for a project subdirectory, or generating one via the `scaffold-context` skill.

## What CONTEXT.md is

In the context-routing model (L0/L1/L2), a `CONTEXT.md` is the L1 routing file for a specific subdirectory. It answers: **where do I go inside this area?** Target budget: ~300 tokens, 25-80 lines. Above 80 lines, suspect bloat. Above 120 lines, split or move detail to `docs/`.

A subdirectory does not need a `CONTEXT.md`. Add one only when the area has its own routing logic — distinct skills, distinct load rules, distinct process — that the root `CLAUDE.md` cannot economically describe in a single map row.

## Six required sections

```markdown
# CONTEXT.md — <area name>

## What this area is
<one or two sentences>

## What to Load

| Task | Load These | Skip These |
|------|------------|------------|
| <task A> | path/foo.md, path/bar.md | path/baz.md, path/quux.md |
| <task B> | ... | ... |

## Folder
<this area's directory layout — NOT the project tree>

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

This is the part most authors get wrong. Deciding what to load is the easy half; the harder, higher-value half is deciding what to withhold. Every file kept out of context is tokens reclaimed and one fewer chance for the model to anchor on something irrelevant. That deliberate exclusion is what makes the table earn its keep over an unconstrained Read tool.

Examples of useful Skip entries:
- "Skip: the legacy `./old/` directory — superseded by `./current/` in v2."
- "Skip: `experiments/<id>/raw/` — already summarized in `experiments/<id>/findings.md`; reading raw inflates context without new signal."

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
| <15 | Too thin — likely missing the Process or What-NOT sections |
| 25-80 | Right |
| 80-120 | Bloated — move detail to sibling docs |
| >120 | Split into two CONTEXT.md files for distinct sub-areas |

Stable knowledge — design docs, architecture rationale, glossaries — belongs in `docs/`. The CONTEXT.md is routing and process, not encyclopedia.

## Routing tables vs. reference tables

Task routing tables (`Task | Go to | Read | Skills`) are an L1 pattern.
They belong in CONTEXT.md files, not in the root CLAUDE.md.

CLAUDE.md uses a *reference* routing table (`File | Read when`) that points
to on-demand docs. This is navigation (L0), not task routing (L1).

If you find yourself adding task-specific routing to CLAUDE.md, move it to the
relevant subdirectory's CONTEXT.md instead.
