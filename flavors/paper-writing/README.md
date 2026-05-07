# Flavor: paper-writing

Adds tooling for drafting, auditing, reviewing, and rebutting academic papers.

## Adds to `.claude/`

- `skills/paper-write/`               — section-by-section LaTeX drafting
- `skills/citation-audit/`            — verify every bib entry exists & is correctly attributed
- `skills/cite-check/`                — trace every numeric claim back to source data
- `skills/paper-claim-audit/`         — zero-context audit of paper numbers ↔ raw results
- `skills/paper-review-sim/`          — simulate peer review with multiple reviewer personas
- `skills/rebuttal/`                  — rebuttal drafting workflow
- `skills/auto-paper-improvement-loop/` — cross-model iterative review→fix→recompile
- `agents/paper-drafter.md`           — paper section drafter agent
- `agents/paper-assembly-team.md`     — multi-agent paper assembly team

## Seeds at project root

- `REFERENCES.md` — bibliographic backbone

## When to pick

- Submitting a paper to a conference / journal / workshop.
- Writing a research report for external readers.
- Preparing a rebuttal.

## Stacks well with

- `research` (the typical combo: research project → paper)

## When NOT to pick alone

- For a paper without underlying research artifacts you should still pair this with `research` so you have `EXPERIMENTS.md` / `FINDINGS.md` / `RESULTS.md`.
