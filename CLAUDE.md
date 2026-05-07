# CLAUDE.md — project-template

Reusable Claude Code template: bootstrap source + sync buffer for all projects.

## What this is

This is NOT a project — it's the **template** that bootstraps new projects. It contains:
- Generic Claude Code agents, skills, hooks, and rules (`.claude/`)
- Stackable flavor packs (`flavors/research/`, `flavors/software-eng/`, `flavors/ml/`, `flavors/hpc/`)
- Seed docs and folder skeletons (`seed-docs/`, `seed-folders/`, `seed-config/`)
- Bootstrap + sync scripts (`bin/`)

## How to use

```bash
# Create a new project
bin/init-project.sh ~/code/my-project --flavor research

# Add a flavor to an existing project
bin/add-flavor.sh ml --project ~/code/my-project

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

## Rules when editing this template

- **Don't add project-specific content.** Everything here must be generic or scoped to a flavor.
- **Don't push to main directly.** Use feature branches + PRs.
- **Test changes** by bootstrapping a test project: `bin/init-project.sh /tmp/test --flavor research`
- Detailed rules in `.claude/rules/workflow.md`
