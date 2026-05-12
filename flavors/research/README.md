# Flavor: research

Adds tooling for research-style projects: hypothesis-driven investigation, experiment tracking, results discipline, and paper writing.

## Adds to `.claude/`

### Rules
- `rules/python.md`     — Python style, testing, naming (loads on `*.py`)
- `rules/tech-stack.md` — Python 3.12+, pip, pyproject.toml (loads on Python/build files)

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
- `skills/aris-shared-references/`      — academic writing standards and protocols

### Agents
- `agents/paper-assembly-team.md` — multi-agent paper drafting team

### Hooks
- `hooks/protect-results.sh` — guards `results/` from accidental mutation

## Seeds at project root

- `EXPERIMENTS.md` — running ledger of experiments
- `FINDINGS.md`    — distilled insights from experiments
- `RESULTS.md`     — index of result artifacts (immutable)
- `REFERENCES.md`  — bibliography and reference tracking

## When to pick

- Research projects, applied research, exploratory analysis.
- Any project producing a paper or technical report.
- Any project where "what experiment have I run?" and "what did it tell me?" are recurring questions.

## When NOT to pick

- A standard SaaS feature build — pick `software-eng` instead.

## Stacks well with

- `ml` (ML research specifically)
- `hpc` (HPC research / parallel computing experiments)
