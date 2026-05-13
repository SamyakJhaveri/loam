# Research Memory Conventions

> Always loaded for research-flavored projects. Documents how to persist
> research learnings across sessions.

## [LEARN:tag] Convention

When something surprising, wrong, or non-obvious is discovered during research,
save it to MEMORY.md with a tag prefix:

| Tag | When to use |
|-----|-------------|
| `[LEARN:method]` | A methodological correction — "we thought X approach works but Y is better" |
| `[LEARN:data]` | A data handling surprise — "this column has nulls we didn't expect" |
| `[LEARN:tool]` | A tool/environment gotcha — "nvc++ rejects this valid OpenMP pragma" |
| `[LEARN:claim]` | A claim that turned out wrong — "we said X but the data shows Y" |
| `[LEARN:metric]` | A metric definition change — "pass_rate now excludes KNOWN_FAIL pairs" |
| `[LEARN:experiment]` | An experiment design evolution — "added temperature sweep after v1 showed sensitivity" |

## When to Save vs. Not Save

**Save:** Corrections, surprises, things that contradict expectations, methodology changes.
These are the things a future session needs to avoid repeating mistakes.

**Don't save:** Routine results, expected outcomes, raw data summaries.
These belong in EXPERIMENTS.md and results/, not memory.

## MEMORY.md Sections for Research Projects

Organize research memory with these sections:

- **Key Facts** — cluster name, environment details, tool versions, dataset sizes
- **Active Experiments** — what's currently being tested, current spec versions
- **Learnings** — `[LEARN:tag]` entries, grouped by tag
