# Contributing to Loam

Thanks for your interest! Loam is a Copier template — the things it ships live under
`seed/`, and the repo runs on its own config via the `.claude → seed/.claude` symlink.

## Development setup

```bash
git clone https://github.com/samyakjhaveri/loam && cd loam
bin/verify-template.sh   # renders and checks the complete harness; expect "verify-template: PASSED"
```

Requirements: [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`uvx copier`), `python3`, `bash`.

**Windows note:** template *development* relies on the `.claude → seed/.claude` symlink.
Use WSL, or enable Developer Mode and `git config core.symlinks true` before cloning.
Rendered projects are unaffected — Copier writes real directories.

## Making changes

- **Docs, content, small fixes** → commit directly to `main` (or open a PR if you're external).
- **Behavior changes** (`seed/` guidance, skills, hooks, policy, `copier.yml`, or release tooling) → branch + PR, always.
- Run `bin/verify-template.sh` before every PR. CI runs it too; a red render blocks merge.
- Before merging any PR: `bash bin/verify-template.sh && bash bin/ip-sweep.sh` (non-strict;
  the identity WARNs are known - see the release blocker note in any open consolidation PR.
  As of 2026-08-10 check 1 also FAILs on pre-existing term hits in `cultivation/marketplace/
  sam-cc-setup/` - a standing finding awaiting an owner ruling, not a new-PR regression).
- Skills follow the [agentskills.io](https://agentskills.io/specification) SKILL.md format.
  A skill that must reach every rendered project goes in `seed/.agents/skills/`.
  Reusable optional skills go in the appropriate marketplace plugin.
- Read `CLAUDE.md` for current repository gotchas. Read `docs/ASSET-LAYERS.md` before placing a new asset.

## Promoting a skill from your project

If you built a broadly useful skill in a Loam-bootstrapped project, you can promote it
by hand into the plugin marketplace. See `docs/SYNC.md` for the current route.
Promotion PRs should state which project battle-tested the skill and what it was used for.

## Releases (maintainers)

Copier resolves from **git tags**, not HEAD. After merging significant changes:

```bash
bin/release.sh <version>   # bumps VERSION, tags, pushes — CI verifies and publishes the release
```

## Reporting issues

Open a GitHub issue with your Copier version and the output of
`bin/verify-template.sh` if the template fails to render.
