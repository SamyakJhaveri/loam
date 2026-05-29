# CLAUDE.md — Loam

This repo IS a Copier template AND a Claude Code project (v3.1). The `.claude/` symlink points to `seed/.claude/`, so the same config that ships to bootstrapped projects activates here.

User preferences:
- Challenge assumptions or offer corrections anytime
- Point out flaws in proposed questions or solutions

## How to use

```bash
# Bootstrap a new project
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project

# Pull template updates into an existing project
cd my-project && uvx copier update --trust

# Promote a project-built skill back to this template
template-sync promote --layer generic .claude/skills/<name>/SKILL.md
```

## Layout

| Path | Purpose |
|------|---------|
| `seed/`                  | Copier `_subdirectory` — ALL deliverables rendered to projects |
| `seed/.claude/`          | Skills, agents, hooks, rules, settings (shipped to projects) |
| `seed/_research/`        | Research-flavor overlay (applied when `is_research=true`) |
| `seed/*.jinja`           | Copier-rendered files (CLAUDE.md, AGENTS.md, README.md, etc.) |
| `.claude → seed/.claude` | Symlink for local dev experience |
| `cultivation/`           | Skill staging: `wip/`, `marketplace/` (cut from default), `retired/` |
| `soil/`                  | Knowledge base: `jvc/`, `foundation/`, `playbooks/`, `reference/` |
| `bin/`                   | `verify-template.sh`, `template-sync.sh`, `lint-skill-descriptions.sh`, `release.sh` |
| `docs/`                  | Template documentation |
| `docs/plans/`            | Session plans and handoffs |
| `docs/specs/`            | Design specifications |
| `copier.yml`             | Copier config: `_subdirectory: "seed"`, questions, `_tasks` |
| `VERSION`                | Semver for releases |

## Reference Docs (read on demand)

Always loaded:
- `.claude/rules/workflow.md` — 6-stage session workflow + anti-patterns
- `.claude/rules/known-issues.md` — recurring gotchas

ICM routing:
- `.claude/rules/L0-budget.md` — when authoring CLAUDE.md
- `.claude/rules/context-md-anatomy.md` — when authoring CONTEXT.md
- `.claude/rules/stage-contract.md` — when invoking feature-dev / fix-bug / `/validate`
- `.claude/rules/layer-triage.md` — when scoping a new task (60/30/10)

Operational:
- `.claude/rules/scaling-vs-automating.md` — when creating new skills or deciding whether to automate
- `.claude/rules/naming-conventions.md` — when creating files/directories or authoring CONTEXT.md
- `.claude/rules/validation-loop.md` — when working on hooks or the `validate` skill
- `docs/ASSET-LAYERS.md` — when adding or moving assets
- `docs/BOOTSTRAP.md`, `docs/SYNC.md`, `docs/COPIER.md`, `docs/FLAVORS.md`, `docs/MEMORY.md`
- `.claude/reference/Claude Code Operational Playbook.md` — when designing new skills/agents
- `docs/plan-reviewer-design.md` — when invoking the plan-reviewer agent (full reference prompt)

## Pipeline Gate

`/validate` is this project's Pipeline Gate. Critical ordering:

```
Implement → /session-critique → /validate (Pipeline Gate) → /commit → /pr (or `/ship`)
```

## Rules when editing this template

- Don't add project-specific content. Everything here is generic or scoped to a flavor.
- Commit directly to main. Only use branches when explicitly requested.
- Test changes by running `bin/verify-template.sh`.
- Skills for ANY project go in `seed/.claude/skills/`. Research-specific go in `seed/_research/skills/`. Cut skills go in `cultivation/marketplace/`.

## Verify before any PR

```bash
bin/verify-template.sh
# Expected: ALL OK
```
