# AGENTS.md - Loam

> Loads in every interactive Claude Code and Codex session and in factory Codex runs (factory Claude runs use `--setting-sources user` and skip it); keep only what prevents a real mistake.

Loam is a Copier template: everything under `seed/` renders into generated projects.
The root `.claude/` and `.codex/` are symlinks to `seed/.claude/` and `seed/.codex/`, so editing either path changes the shipped harness, which also runs in Loam's own sessions.
Challenge false premises and flawed proposals, and offer a concrete repair.

## Rules when editing Loam

1. Docs, content and small fixes may go straight to `main`; changes to seed behavior, hooks, `copier.yml` or releases go on a branch and pull request.
2. Keep rendered content generic; project-specific material stays outside `seed/`.
3. Run `bin/check` before every commit and require `check: PASSED`.
4. Source and command output outrank prose; repair prose that disagrees.
5. Keep one behavior change per session.
6. Read `docs/ASSET-LAYERS.md` before placing a new asset or directive, or to learn why the tree is laid out as it is: each directive has one home.
7. In parallel work, one integration owner holds the final snapshot and one validation owner runs the single full `bin/check` on it; other workers run focused checks and return bounded reports.

## Gotchas

- Copier resolves release tags, not `main`: an untagged push ships nothing.
- Verification searches must be case-insensitive and repository-wide.
- Count skills by `SKILL.md` files; support directories are not skills.
- Quote YAML description strings that contain colons.

## Read on demand

- `seed/docs/HARNESS.md.jinja`, then `docs/HARNESS-LOAM.md` (Loam-only notes and Claude Code hook gotchas): changing hooks, rules, settings or the deny lists, or needing the accepted risks.
- `docs/RULES.md`: which check enforces each rule; update it after a correction.
- `.claude/skills/verify-loam/SKILL.md`: proving a seed, hook, settings or `copier.yml` change in a real rendered project before shipping it.
- `docs/SYNC.md`: `bin/sync-project`, updating projects, or promoting a reusable asset.
- `docs/BOOTSTRAP.md`, `docs/COPIER.md`: bootstrapping a project, or changing bootstrap or update behavior.
- `docs/factory/ARCHITECTURE.md`: running or changing the loop factory (brief, tickets, `bin/factory`, graders).

## Agent skills

### Issue tracker

GitHub Issues for `SamyakJhaveri/loam`, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five default labels. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: root `CONTEXT.md` plus `docs/adr/`. See `docs/agents/domain.md`.
