# Flavor: ml

Adds scaffolding for ML training and evaluation work.

## Adds to `.claude/`

### Rules
- `rules/python.md`     — Python style, testing, naming (loads on `*.py`)
- `rules/tech-stack.md` — Python 3.12+, pip, pyproject.toml (loads on Python/build files)

## Seeds at project root

- `EXPERIMENTS.md` — training/eval run ledger
- `RESULTS.md`     — index of run artifacts

## When to pick

- Training models, running ML experiments, building ML pipelines.

## When NOT to pick

- Inference-only product integration — pick `software-eng` instead.

## Stacks well with

- `research` (ML research with broader hypothesis tracking)
- `paper-writing` (ML paper)
- `hpc` (HPC-scale ML training)

## Note

This flavor is intentionally lean today. Promote ML-specific skills back from your projects via `template-sync promote --layer flavor:ml ...` as patterns emerge.
