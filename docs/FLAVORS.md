# Flavors

Flavors are opt-in packs that layer additional skills/agents/hooks/rules and seed-docs onto the generic core at bootstrap time. They stack — pass multiple `--flavor` flags.

## The five flavors

| Flavor | Adds | Pick when |
|--------|------|-----------|
| `research`     | Hypothesis-driven workflow skills, results discipline | Research projects, applied investigations |
| `paper-writing`| Drafting / citation audit / rebuttal skills          | Submitting a paper or technical report |
| `software-eng` | Design records, architecture docs                    | Building software products |
| `ml`           | ML run ledger, results index                         | Training models, ML pipelines |
| `hpc`          | CUDA/OpenMP/OpenCL pattern guides, parallel review   | Parallel-computing work |

## Stack examples

| Project type | Recommended flavors |
|--------------|---------------------|
| ML research with paper          | `research --flavor ml --flavor paper-writing` |
| HPC research with paper         | `research --flavor hpc --flavor paper-writing` |
| Greenfield SaaS                 | `software-eng` |
| ML-powered product              | `software-eng --flavor ml` |
| Pure paper / rebuttal cycle     | `paper-writing` |

## What each flavor adds

See each flavor's `README.md`:

- `flavors/research/README.md`
- `flavors/paper-writing/README.md`
- `flavors/software-eng/README.md`
- `flavors/ml/README.md`
- `flavors/hpc/README.md`

## Layering semantics

When `init-project.sh` applies multiple flavors, they're overlaid in the order passed. Same-path collisions: later overlays win, with a warning. In practice, flavors don't collide today (they touch disjoint skill/agent/hook names).

If you discover a collision while developing flavors, prefer renaming over silently letting one win — overlap usually means a skill should live in `generic` instead of any specific flavor.

## Promoting a new flavor-specific asset

When you build a skill/agent/hook in a project that's clearly flavor-specific, promote it via:

```
template-sync promote <relpath>
```

Pick the target layer when prompted. Don't promote into `generic` to "save effort" — flavors exist to keep the generic core lean.
