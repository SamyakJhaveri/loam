# Flavor: research

Adds tooling for research-style projects: hypothesis-driven investigation, experiment tracking, results discipline, paper writing, and HPC/parallel-computing support.

## Adds to `.claude/`

### Rules
- `rules/python.md`          — Python style, testing, naming (loads on `*.py`)
- `rules/tech-stack.md`      — Python 3.12+, pip, pyproject.toml (loads on Python/build files)
- `rules/research-memory.md` — [LEARN:tag] memory convention for research corrections (always loaded)

### Skills
- `skills/hypothesis-tree/`              — branching hypothesis manager
- `skills/interpret-results/`            — hypothesis-first interpretation of results
- `skills/paper-write/`                  — LaTeX section drafting with citation fetching
- `skills/citation-audit/`              — bibliographic verification
- `skills/cite-check/`                  — numeric claim tracing to raw results
- `skills/paper-claim-audit/`           — paper numbers vs raw result verification
- `skills/paper-review-sim/`            — conference-style peer review simulation
- `skills/rebuttal/`                    — reviewer rebuttal pipeline
- `skills/auto-paper-improvement-loop/` — iterative review-fix-recompile loop
- `skills/shared-references/`           — academic writing standards and protocols
- `skills/cuda-omp-translator/`         — CUDA↔OpenMP translation pattern guide
- `skills/hpc-code-reviewer/`           — parallel-correctness checklist (data races, memory model, atomics)
- `skills/experiment/`                  — experiment lifecycle orchestrator (init, plan, run, evolve)

### Agents
- `agents/paper-assembly-team.md` — multi-agent paper drafting team
- `agents/regression-checker.md`  — regression detection agent

### Hooks
- `hooks/protect-results.sh`             — guards `results/` from accidental mutation
- `hooks/validate-experiment-config.sh`   — reproducibility gate for experiment config.json

### Bootstrap config
- `seed-config/settings-hooks.json` — registers `validate-experiment-config.sh` in `.claude/settings.json` at bootstrap

## Seeds at project root

- `EXPERIMENTS.md`  — running ledger of experiments
- `FINDINGS.md`     — distilled insights from experiments
- `RESULTS.md`      — index of result artifacts (immutable)
- `REFERENCES.md`   — bibliography and reference tracking
- `ARCHITECTURE.md` — system architecture documentation
- `DESIGN.md`       — design decisions and rationale
- `EXPERIMENT-PROTOCOL.md` — experiment workflow guide and quick-start

## When to pick

- Research projects, applied research, exploratory analysis.
- Any project producing a paper or technical report.
- ML training, experiments, evaluation pipelines.
- HPC/parallel-computing work (CUDA, OpenMP, OpenCL, MPI).
- Any project where "what experiment have I run?" and "what did it tell me?" are recurring questions.

## When NOT to pick

- A standard SaaS feature build — pick `software-eng` instead.
- Pure product work with no research component.

## Stacks well with

- `software-eng` (research tool that's also a product)
