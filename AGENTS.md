# AGENTS.md — Loam

> The shared prose home for agents working on Loam.
> Claude Code imports this file from `CLAUDE.md`. Codex reads it directly.
> Every line loads in every session, so keep only guidance that prevents a real mistake.

## What this repo is

Loam is a Copier template and an agent-harness project. Everything under `seed/`
renders into a generated project. The root `.claude/` symlink points to
`seed/.claude/`, so the shipped Claude harness also runs while developing Loam.

## Working style

- Challenge assumptions and correct false premises.
- Point out flaws in proposed questions or solutions.
- Offer a concrete repair when you find a flaw.

## Common commands

```bash
# Bootstrap from the latest release tag.
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project

# Pull the latest released template into an existing project.
cd my-project && uvx copier update --trust

# Verify Loam before a commit or release.
bin/verify-template.sh
```

## Layout

| Path | Purpose |
|------|---------|
| `seed/` | Copier source. Everything here renders into projects. |
| `seed/.agents/skills/` | Skills shared by Claude Code and Codex. |
| `seed/.claude/` | Claude Code hooks and settings. |
| `seed/.codex/` | Codex configuration, hook policy, and execution rules. |
| `cultivation/marketplace/` | Optional plugin agents, skills, hooks, and bundles. |
| `cultivation/wip/` | Staging for assets with no placement verdict. New files are ignored by default; some parked research assets remain tracked. |
| `bin/` | Verification, release, and intellectual-property checks. |
| `docs/` | Current template documentation and historical design records. |
| `copier.yml` | Copier questions, exclusions, and post-render tasks. |
| `VERSION` | Template release version. |

## Rules when editing Loam

1. Use the hybrid branch policy. Docs, content, and small fixes may go directly to
   `main`. Changes to seed behavior, hooks, `copier.yml`, or releases use a branch
   and pull request.
2. Keep rendered content generic. Project-specific material stays outside `seed/`.
3. Run `bin/verify-template.sh` before every commit. Require
   `verify-template: PASSED`.
4. Treat source and command output as authority. Repair prose when it disagrees.
5. Keep one behavior change per session.
6. Keep one directive in one home. Read `docs/ASSET-LAYERS.md` before placing a
   new asset.

## Gotchas

- Copier resolves release tags, not the current `main` branch.
- Verification searches must be case-insensitive and repository-wide.
- Count skills by finding `SKILL.md` files. Support directories are not skills.
- Quote YAML description strings that contain colons.

## Read on demand

| Resource | Read when |
|----------|-----------|
| `bin/rendered_harness_contract.py`, `bin/tests/test_rendered_harness_contract.py` | Changing the Rendered Harness Contract. |
| `docs/ASSET-LAYERS.md` | Deciding where an agent asset belongs. |
| `docs/SYNC.md` | Updating projects or promoting a reusable asset. |
| `docs/BOOTSTRAP.md`, `docs/COPIER.md` | Changing bootstrap or update behavior. |
| `docs/specs/rebuild-structure-design.md` | Needing the rationale for the current tree. |
| `docs/specs/rebuild-research/` | Checking the research behind the rebuild. |
