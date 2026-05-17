# project-template

Reusable Claude Code template that serves as both a **bootstrap source** for new projects and a **sync buffer** for propagating Claude Code improvements across projects.

## Quick Start

### Via Copier (recommended)

```bash
# No installation needed — uvx runs copier on-the-fly
uvx copier copy gh:samyakjhaveri/project-seed-framework ./my-project

# Or with a specific version
uvx copier copy --vcs-ref v1.0.0 gh:samyakjhaveri/project-seed-framework ./my-project
```

### Via shell script (fallback)

```bash
# Requires cloning this repo locally
bin/init-project.sh ~/code/my-research --flavor research
bin/init-project.sh ~/code/my-app --flavor software-eng
bin/init-project.sh ~/code/my-tool --flavor research --flavor software-eng
```

## Updating a project

```bash
cd my-project
uvx copier update  # pulls latest template changes, resolves conflicts
```

## What you get

Every new project bootstrapped from this template includes:

- **Claude Code setup** — agents, skills, hooks, rules pre-configured
- **Folder skeleton** — standard directories (results/, scripts/, config/, etc.)
- **Seed docs** — README, CLAUDE.md, HANDOFF.md, MEMORY.md with project name filled in
- **Config files** — .gitignore, .editorconfig, pyproject.toml, .mcp.json
- **Its own git history** — clean, no connection back to this template

## Flavors

| Flavor | Adds | Pick when |
|--------|------|-----------|
| `research` | Hypothesis workflow, paper-writing, citation audit, HPC/CUDA guides, result protection | Research, papers, ML experiments, HPC work |
| `software-eng` | Design records, architecture docs, frontend rules | Building software products, tools, websites |

Flavors stack — pass multiple `--flavor` flags.

## Syncing improvements back

When you build a generally-useful skill/agent/hook in a project, promote it back:

```bash
# Inside your project (requires template-manifest.json or .copier-answers.yml)
/template-sync promote skills/my-new-skill
```

This creates a PR branch in the template repo — never pushes to main directly. See `docs/SYNC.md`.

## Documentation

- [Copier distribution](docs/COPIER.md)
- [Bootstrap guide](docs/BOOTSTRAP.md)
- [Sync mechanism](docs/SYNC.md)
- [Flavors reference](docs/FLAVORS.md)
- [Asset layers](docs/ASSET-LAYERS.md)

## Design principles

1. **Promotion is opt-in only.** No automatic background syncing.
2. **Generic core stays lean.** Domain-specific content belongs in flavors.
3. **Projects don't know their origin.** No git remote back to this template.
4. **The buffer is a gatekeeper, not a dump.** Only proven, generalized assets get promoted.
