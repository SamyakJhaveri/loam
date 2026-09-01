# Contributing to Loam

Thanks for your interest! Loam is a Copier template — the things it ships live under
`seed/`, and the repo runs on its own config via the `.claude → seed/.claude` symlink.

## Development setup

```bash
git clone https://github.com/samyakjhaveri/loam && cd loam
bin/verify-template.sh   # renders and checks the complete harness; expect "verify-template: PASSED"
```

Requirements: [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`uvx copier`), `python3`, `bash`, the Claude Code and Codex CLIs, and Ruff.
Missing agent CLIs fail the gate; `LOAM_ALLOW_MISSING_AGENT_CLIS=1` permits a reduced local run (CI never sets it).

**Windows note:** template *development* relies on the `.claude → seed/.claude` symlink.
Use WSL, or enable Developer Mode and `git config core.symlinks true` before cloning.
Rendered projects are unaffected — Copier writes real directories.

## Making changes

- **Docs, content, small fixes** → commit directly to `main` (or open a PR if you're external).
- **Behavior changes** (`seed/` guidance, skills, hooks, policy, `copier.yml`, or release tooling) → branch + PR, always.
- Run `bin/verify-template.sh` before every PR. CI runs it too; a red render blocks merge.
- Before merging any PR, run `bash bin/verify-template.sh && bash bin/ip-sweep.sh`.
  Without `bin/.ip-terms`, the non-strict IP sweep warns that it skips the content
  sweep and can still pass.
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
