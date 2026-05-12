# Flavors

Flavors are opt-in packs that layer additional skills/agents/hooks/rules and seed-docs onto the generic core at bootstrap time. They stack — pass multiple `--flavor` flags.

## Available flavors

| Flavor | Adds | Pick when |
|--------|------|-----------|
| `research`     | Hypothesis workflow, paper-writing, citation audit, result protection, CUDA/OpenMP guides, HPC code review | Research projects, papers, ML experiments, HPC work |
| `software-eng` | Design records, architecture docs, frontend rules | Building software products, tools, websites |

## Usage examples

| Project type | Recommended flavors |
|--------------|---------------------|
| ML/HPC research with paper    | `research` |
| Greenfield SaaS               | `software-eng` |
| Personal tool with research   | `research --flavor software-eng` |

## What each flavor adds

See each flavor's `README.md`:

- `flavors/research/README.md`
- `flavors/software-eng/README.md`

## Layering semantics

When `init-project.sh` applies multiple flavors, they're overlaid in the order passed. Same-path collisions: later overlays win, with a warning. In practice, the two flavors don't collide today (they touch disjoint skill/agent/hook names).

If you discover a collision while developing flavors, prefer renaming over silently letting one win — overlap usually means a skill should live in `generic` instead of any specific flavor.

## Promoting a new flavor-specific asset

When you build a skill/agent/hook in a project that's clearly flavor-specific, promote it via:

```
template-sync promote <relpath>
```

Pick the target layer when prompted. Don't promote into `generic` to "save effort" — flavors exist to keep the generic core lean.
