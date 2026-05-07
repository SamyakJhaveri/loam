# Flavor: research

Adds tooling for research-style projects: hypothesis-driven investigation, experiment tracking, results discipline.

## Adds to `.claude/`

- `skills/grill-research/`        — adversarial pre-experiment interrogation
- `skills/hypothesis-tree/`       — branching hypothesis manager
- `skills/interpret-results/`     — hypothesis-first interpretation of results
- `skills/mentoring/`             — research/HPC/SE teaching framework
- `agents/regression-checker.md`  — baseline regression detector
- `hooks/protect-results.sh`      — guards `results/` from accidental mutation

## Seeds at project root

- `EXPERIMENTS.md` — running ledger of experiments
- `FINDINGS.md`    — distilled insights from experiments
- `RESULTS.md`     — index of result artifacts (immutable)

## When to pick

- ML research projects, applied research, exploratory analysis.
- Any project where "what experiment have I run?" and "what did it tell me?" are recurring questions.

## When NOT to pick

- A pure paper-writing or rebuttal effort with no new experiments — pick `paper-writing` instead.
- A standard SaaS feature build — pick `software-eng` instead.

## Stacks well with

- `paper-writing` (research project that's also producing a paper)
- `ml` (ML research specifically)
- `hpc` (HPC research / parallel computing experiments)
