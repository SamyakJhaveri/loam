# project-template

Reusable Claude Code template that serves as both a **bootstrap source** for new projects and a **sync buffer** for propagating Claude Code improvements across projects.

## Quick Start

```bash
# Bootstrap a new research project
~/Desktop/project_template/bin/init-project.sh ~/code/my-research --flavor research

# Bootstrap a software engineering project
~/Desktop/project_template/bin/init-project.sh ~/code/my-app --flavor software-eng

# Stack multiple flavors
~/Desktop/project_template/bin/init-project.sh ~/code/my-hpc-paper \
  --flavor research --flavor hpc
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
| `research` | Hypothesis workflow, paper-writing skills, result protection hooks | Research projects, papers |
| `software-eng` | Design records, architecture docs | Building software products |
| `ml` | ML run ledger, experiment tracking | Training models, ML pipelines |
| `hpc` | CUDA/OpenMP translation guides, parallel review | Parallel-computing work |

Flavors stack — pass multiple `--flavor` flags.

## Syncing improvements back

When you build a generally-useful skill/agent/hook in a project, promote it back:

```bash
# Inside your project (requires template-manifest.json)
/template-sync promote skills/my-new-skill
```

This creates a PR branch in the template repo — never pushes to main directly. See `docs/SYNC.md`.

## Documentation

- [Bootstrap guide](docs/BOOTSTRAP.md)
- [Sync mechanism](docs/SYNC.md)
- [Flavors reference](docs/FLAVORS.md)
- [Asset layers](docs/ASSET-LAYERS.md)

## Design principles

1. **Promotion is opt-in only.** No automatic background syncing.
2. **Generic core stays lean.** Domain-specific content belongs in flavors.
3. **Projects don't know their origin.** No git remote back to this template.
4. **The buffer is a gatekeeper, not a dump.** Only proven, generalized assets get promoted.
