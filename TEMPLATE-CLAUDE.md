# CLAUDE.md — Loam

This repo IS a Copier template AND a Claude Code project (single-tree, v2.0). The author IS a project user — same `.claude/` config that ships to bootstrapped projects is what activates in this repo.

User preferences:
- challenge assumptions or offer corrections anytime
- point out flaws in proposed questions or solutions

## What this is

A personal Claude Code starter that bootstraps every new project and absorbs improvements back via `template-sync promote → PR → copier update`. The bidirectional sync loop is the framework's reason to exist; the Copier template is the carrier.

## How to use

```bash
# Bootstrap a new project (anywhere — no local clone)
uvx copier copy gh:samyakjhaveri/loam ./my-project

# Pull template updates into an existing project
cd my-project && uvx copier update

# Promote a project-built skill back to this template
template-sync promote --layer generic .claude/skills/<name>/SKILL.md
# (or --layer flavor:research for research-only)
```

See `docs/BOOTSTRAP.md`, `docs/SYNC.md`, `docs/FLAVORS.md` for the full flow.

## Layout

| Path | Purpose |
|------|---------|
| `.claude/`               | Claude Code config — used here AND shipped to projects (single-tree) |
| `_research/`             | Optional research-flavor overlay, applied when `is_research=true` |
| `seed-skills/`           | 14 marketplace-candidate skills cut from default core (not shipped) |
| `*.jinja` at root        | Copier-rendered files that become project-root files |
| `copier.yml`             | Copier config: questions, `_exclude:`, `_tasks` |
| `bin/`                   | `template-sync.sh`, `verify-template.sh`, `release.sh` |
| `docs/`                  | Template documentation |
| `VERSION`                | Semver for releases |
| `claude_code_course_files/`, `internal_docs/`, `outputs/` | Reference material; excluded from rendered projects |

## Reference Docs (read on demand)

Always loaded:
- `.claude/rules/workflow.md` — 6-stage session workflow + anti-patterns
- `.claude/rules/known-issues.md` — recurring gotchas

ICM routing vocabulary (v2.0):
- `.claude/rules/L0-budget.md`         — when authoring this or any CLAUDE.md
- `.claude/rules/context-md-anatomy.md` — when authoring a subdirectory CONTEXT.md
- `.claude/rules/stage-contract.md`    — when invoking feature-dev / fix-bug / `/validate`
- `.claude/rules/layer-triage.md`      — when scoping a new task (60/30/10)

Operational:
- `.claude/rules/validation-loop.md`   — when working on hooks or the `validate` skill
- `docs/ASSET-LAYERS.md`               — when adding or moving assets
- `docs/BOOTSTRAP.md`, `docs/SYNC.md`, `docs/COPIER.md`, `docs/FLAVORS.md`, `docs/MEMORY.md`
- `.claude/reference/Claude Code Operational Playbook.md` — when designing new skills/agents

## Pipeline Gate

`/validate` is this project's Pipeline Gate (see workflow.md §6). Critical ordering:

```
Implement → /multi-review → /validate (Pipeline Gate) → commit → push
```

## Rules when editing this template

- Don't add project-specific content. Everything here is generic or scoped to a flavor.
- Don't push to main directly. Use `rework/<topic>` branches + squash-merge.
- Test changes by running `bin/verify-template.sh` — it does a Copier render in both `default` and `is_research=true` variants and asserts invariants (single-tree, agentskills.io schema, no leakage).
- Skills that are useful in ANY project go in `.claude/skills/`. Research-specific go in `_research/skills/`. Marketplace-candidate (cut from default) live in `seed-skills/`.

## Verify before any PR

```bash
bin/verify-template.sh
# Expected: ALL OK
```

Run before any PR that touches `.claude/`, `_research/`, `bin/`, `copier.yml`, or top-level `.jinja` files.
