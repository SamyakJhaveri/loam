# Flavor: hpc

Adds tooling for parallel-computing work: CUDA / OpenMP / OpenCL / MPI / parallel performance.

## Adds to `.claude/`

### Rules
- `rules/python.md`     — Python style, testing, naming (loads on `*.py`)
- `rules/tech-stack.md` — Python 3.12+, pip, pyproject.toml (loads on Python/build files)

### Skills
- `skills/cuda-omp-translator/`  — CUDA↔OpenMP translation pattern guide
- `skills/hpc-code-reviewer/`    — parallel-correctness checklist (data races, memory model, atomics)

## Seeds at project root

- (none — add domain-specific docs as patterns emerge)

## When to pick

- Working on CUDA / OpenMP / OpenCL / MPI code.
- Reviewing or generating parallel kernel translations.
- HPC benchmark work.

## When NOT to pick

- General software engineering with incidental parallelism — pick `software-eng` instead.

## Stacks well with

- `research` (HPC research / benchmarks)
- `ml` (large-scale model training across GPUs)
- `paper-writing` (HPC paper)
