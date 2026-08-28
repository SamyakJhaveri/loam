# CLAUDE.md — Loam

This repo IS a Copier template AND a Claude Code project. The `.claude/` symlink points to `seed/.claude/`, so the same config that ships to bootstrapped projects activates here.

**REBUILD EPOCH (since 2026-08-28, commit 317b961):** the harness was deliberately gutted to a baseline.
`reassess-`/`rewrite-` filename prefixes mark assets awaiting a keep/remove/rewrite verdict.
The decision ledger is `docs/specs/rebuild-ledger.md`; the template is non-functional on main until the rebuild lands (the last release tag keeps serving Copier users).
Deleted files remain readable via `git show 317b961^:<old-path>`.

User preferences:
- Challenge assumptions or offer corrections anytime
- Point out flaws in proposed questions or solutions
- Offer solutions to flaws

## How to use

```bash
# Bootstrap a new project (resolves the last release TAG, not main)
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project

# Pull template updates into an existing project
cd my-project && uvx copier update --trust
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
| `soil/`                  | Local-only knowledge base (gitignored; incl. `loam-rebuild-checkpoint/`) |
| `_archive/`              | Human-only reference docs; not loaded into Claude context |
| `reassess-bin/`          | Parked scripts awaiting ledger verdicts (was `bin/`; `bin/` is empty) |
| `docs/`                  | Template documentation (partially stale during the rebuild) |
| `docs/specs/`            | Design specifications + the rebuild ledger |
| `copier.yml`             | Copier config: `_subdirectory: "seed"`, questions, `_tasks` |
| `VERSION`                | Semver for releases |

## Reference Docs (read on demand)

Always loaded:
- `.claude/rules/reassess-rewrite-known-issues.md` — recurring gotchas (awaiting rewrite)
- `.claude/rules/architecture.md`

Context-routing:
- `.claude/rules/reassess-context-md-anatomy.md` — when authoring a CONTEXT.md
- `docs/specs/rebuild-ledger.md` — when deciding any asset's fate
- `docs/ASSET-LAYERS.md`, `docs/BOOTSTRAP.md`, `docs/SYNC.md`, `docs/COPIER.md`, `docs/FLAVORS.md`, `docs/MEMORY.md` — stale in parts; verify against the tree before trusting
- plan-reviewer design rationale: deleted in the teardown; read via `git show 317b961^:seed/plan-reviewer-design.md` when redesigning the plan-reviewer

## Rules when editing this template

- Don't add project-specific content. Everything here is generic or scoped to a flavor.
- **Hybrid branch policy:** commit directly to main for docs, content, and small fixes; branch + PR for `seed/` behavior changes, hooks, `copier.yml`, and releases.
- Skills for ANY project go in `seed/.claude/skills/`. Research-specific go in `seed/_research/skills/`. Cut skills go in `cultivation/marketplace/`.
- `reassess-bin/verify-template.sh` is currently BROKEN against the gutted seed; CI repair is a ledger row. Do not tag a release until it passes again.
