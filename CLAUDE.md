# CLAUDE.md — project-template

Reusable Claude Code template: bootstrap source + sync buffer for all projects.

- challenge assumptions or offer corrections anytime you get a chance
- point out any flaws in the questions or solutions I suggest

## What this is

This is NOT a project — it's the **template** that bootstraps new projects. It contains:
- Copier template subdirectory with generic core (`template/.claude/`)
- Stackable flavor packs (`flavors/`, `template/_research/`, `template/_software-eng/`)
- Seed docs and folder skeletons (`seed-docs/`, `seed-folders/`, `seed-config/`)
- Bootstrap + sync scripts (`bin/`)

## How to use

### Via Copier (recommended)

```bash
# Bootstrap — no local clone needed
uvx copier copy gh:samyakjhaveri/project-seed-framework ./my-project

# Update an existing project from latest template
cd my-project && uvx copier update
```

### Via shell scripts (fallback)

```bash
# Create a new project (requires local clone)
bin/init-project.sh ~/code/my-project --flavor research

# Add a flavor to an existing project
bin/add-flavor.sh research --project ~/code/my-project
```

### Promote assets back

```bash
# From inside a project — works with both Copier and shell-bootstrapped projects
/template-sync promote <asset>
```

## Key documentation

| Doc | What |
|-----|------|
| `docs/BOOTSTRAP.md` | How to create a new project |
| `docs/SYNC.md` | How the sync skill works |
| `docs/FLAVORS.md` | What each flavor adds |
| `docs/ASSET-LAYERS.md` | Generic vs flavor vs project-local |
| `docs/MEMORY.md` | 3-layer memory architecture |

## Layout

| Path | Purpose |
|------|---------|
| `.claude/` | Template-dev Claude Code config (NOT distributed to projects) |
| `template/` | Copier template subdirectory — generic core + flavor overlays |
| `template/.claude/` | Generic core distributed to projects (agents, skills, hooks, rules) |
| `copier.yml` | Copier template configuration |
| `VERSION` | Semver version for releases |
| `flavors/` | Stackable flavor packs (source of truth; copied into `template/`) |
| `seed-docs/` | Template docs rendered at bootstrap (shell fallback) |
| `seed-config/` | Template config files rendered at bootstrap (shell fallback) |
| `seed-folders/` | Empty dirs created at bootstrap |
| `bin/` | Bootstrap + sync + release scripts |
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
- **Generic vs flavor skills:** If a skill is useful in ANY project (regardless of domain), put it in `.claude/skills/` (generic core). Do NOT duplicate it across flavor directories — that creates drift risk. Only put a skill in `flavors/<name>/skills/` if it's truly domain-specific to that flavor. See `docs/ASSET-LAYERS.md`.
- Detailed rules in `.claude/rules/workflow.md`

## Verify

```bash
bin/verify-template.sh
# Expected: ALL OK (bootstraps all flavors, validates JSON, shellchecks if available)
# Run before any PR that touches bin/, .claude/, flavors/, or seed-*/.
```
