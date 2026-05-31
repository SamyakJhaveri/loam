# Flavors

In v3.0 the framework has a default seed (engineering-oriented) and one opt-in flavor (`research`). The previous `software-eng` flavor is folded into the default — its rules and seed-docs ship to every project regardless of choice.

## Toggle

The `is_research` boolean question in `copier.yml` decides at bootstrap whether the research overlay applies. Default is `false`.

```bash
# Engineering project — default
uvx copier copy --trust gh:samyakjhaveri/loam ./my-app

# Research project — opt-in
uvx copier copy --trust --data "is_research=true" gh:samyakjhaveri/loam ./my-paper
```

## What the default seed includes

Loaded into every project, research or not:

- The 26 core skills (`.claude/skills/`)
- The 6 core agents (`.claude/agents/`)
- All hooks including the SessionStart brief
- All four ICM routing rules (`L0-budget.md`, `context-md-anatomy.md`, `stage-contract.md`, `layer-triage.md`)
- Engineering-oriented path-scoped rules (`architecture.md`, `python.md`, `tech-stack.md`, `frontend-design.md`)
- Top-level docs `ARCHITECTURE.md` and `DESIGN.md` (generated on-demand by skills, not seeded)

## What the research flavor adds

When `is_research=true`, the Copier `_tasks` step overlays the contents of `seed/_research/` onto the rendered project, then removes `seed/_research/` itself. Specifically:

| Path | Contents | What |
|------|----------|------|
| `.claude/skills/` (additions) | `augment-test`, `auto-paper-improvement-loop`, `citation-audit`, `cite-check`, `cuda-omp-translator`, `eval-grader`, `eval-run`, `experiment`, `grill-research`, `hpc-code-reviewer`, `hypothesis-tree`, `interpret-results`, `overnight-eval`, `paper-claim-audit`, `paper-review-sim`, `paper-write`, `post-eval`, `rebuttal`, `shared-references/` | Research and paper-writing skills |
| `.claude/agents/` (additions) | `eval-batcher.md`, `paper-assembly-team.md`, `regression-checker.md` | Research-specific agents |
| `.claude/hooks/` (additions) | `protect-results.sh`, `validate-experiment-config.sh` | Result-protection and experiment-config validation |
| `.claude/rules/` (addition) | `research-memory.md` | Research-specific memory conventions |
| Project root (additions) | `REFERENCES.md`, `EXPERIMENT-PROTOCOL.md`, `EXPERIMENTS.md`, `FINDINGS.md`, `RESULTS.md`, `CHANGELOG.research.md` | Paper-writing seed-docs |
| `.claude/settings.json` | Deep-merged hooks | `protect-results.sh` and `validate-experiment-config.sh` registered |

## Promotion target for new flavor-specific assets

If you build a skill in a project that's clearly research-only:

```bash
template-sync promote --layer flavor:research <relpath>
```

This writes to `seed/_research/<relpath-stripped>` in the template (e.g., `.claude/skills/foo/SKILL.md` → `seed/_research/skills/foo/SKILL.md`). If the skill is general enough to belong in the default seed, use `--layer generic` instead — that writes to `seed/.claude/<relpath>`.

Default to `generic` only when the skill is useful regardless of project type. The flavor exists to keep the default seed lean.

## Why software-eng was folded

The audit established that the previous `software-eng` flavor carried 4 rule files, 3 seed-docs templates, and 0 skills / agents / hooks — a thin layer whose entire content was useful to almost every engineering project. The cost of the abstraction (two parallel template directories, a "must-stay-identical" duplication guard for `python.md` and `tech-stack.md`) was higher than the value of keeping it optional. Folding it into the default removes the dual-tree maintenance burden.

The research flavor remains a flavor: 18 skills + 3 agents + 2 hooks + 2 rules + 6 docs is substantial, and not every engineering project wants citation auditing or HPC code review.
