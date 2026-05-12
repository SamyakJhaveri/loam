# CLAUDE.md — project-template

Reusable Claude Code template: bootstrap source + sync buffer for all projects.

- challenge assumptions or offer corrections anytime you get a chance
- point out any flaws in the questions or solutions I suggest

## What this is

This is NOT a project — it's the **template** that bootstraps new projects. It contains:
- Generic Claude Code agents, skills, hooks, and rules (`.claude/`)
- Stackable flavor packs (`flavors/research/`, `flavors/software-eng/`)
- Seed docs and folder skeletons (`seed-docs/`, `seed-folders/`, `seed-config/`)
- Bootstrap + sync scripts (`bin/`)

## How to use

```bash
# Create a new project
bin/init-project.sh ~/code/my-project --flavor research

# Add a flavor to an existing project
bin/add-flavor.sh research --project ~/code/my-project

# Promote a reusable asset back to this template (from inside a project)
/template-sync promote <asset>
```

## Key documentation

| Doc | What |
|-----|------|
| `docs/BOOTSTRAP.md` | How to create a new project |
| `docs/SYNC.md` | How the sync skill works |
| `docs/FLAVORS.md` | What each flavor adds |
| `docs/ASSET-LAYERS.md` | Generic vs flavor vs project-local |

## Layout

| Path | Purpose |
|------|---------|
| `.claude/` | Generic core (agents, skills, hooks, rules) |
| `flavors/` | Stackable flavor packs |
| `seed-docs/` | Template docs rendered at bootstrap |
| `seed-config/` | Template config files rendered at bootstrap |
| `seed-folders/` | Empty dirs created at bootstrap |
| `bin/` | Bootstrap + sync scripts |
| `docs/` | Template documentation |

## Reference Docs (Read When Relevant)

Path-scoped rules in `.claude/rules/` load only when matching files are touched.
Read these on demand:

- Workflow + anti-patterns: `.claude/rules/workflow.md` *(always loaded)*
- Known gotchas: `.claude/rules/known-issues.md` *(always loaded)*
- Validation protocol: `.claude/rules/validation-loop.md` *(when working on hooks/validate skill)*
- Asset layering: `docs/ASSET-LAYERS.md` *(when adding or moving template assets)*
- Bootstrap mechanics: `docs/BOOTSTRAP.md` *(when editing `bin/init-project.sh`)*
- Sync mechanics: `docs/SYNC.md` *(when promoting an asset)*
- Operational playbook: `.claude/reference/Claude Code Operational Playbook.md` *(when designing new skills/agents)*

## Rules when editing this template

- **Don't add project-specific content.** Everything here must be generic or scoped to a flavor.
- **Don't push to main directly.** Use feature branches + PRs.
- **Test changes** by bootstrapping a test project: `bin/init-project.sh /tmp/test --flavor research`
- Detailed rules in `.claude/rules/workflow.md`

## Verify

```bash
bin/verify-template.sh
# Expected: ALL OK (bootstraps all 4 flavors, validates JSON, shellchecks if available)
# Run before any PR that touches bin/, .claude/, flavors/, or seed-*/.
```
