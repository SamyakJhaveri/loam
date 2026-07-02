# Contributing to Loam

Thanks for your interest! Loam is a Copier template — the things it ships live under
`seed/`, and the repo runs on its own config via the `.claude → seed/.claude` symlink.

## Development setup

```bash
git clone https://github.com/samyakjhaveri/loam && cd loam
bin/verify-template.sh   # renders both flavors and runs all checks — expect "ALL OK"
```

Requirements: [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`uvx copier`), `python3`, `bash`.

**Windows note:** template *development* relies on the `.claude → seed/.claude` symlink.
Use WSL, or enable Developer Mode and `git config core.symlinks true` before cloning.
Rendered projects are unaffected — Copier writes real directories.

## Making changes

- **Docs, content, small fixes** → commit directly to `main` (or open a PR if you're external).
- **Behavior changes** (`seed/` skills/hooks/rules, `copier.yml`, release tooling) → branch + PR, always.
- Run `bin/verify-template.sh` before every PR. CI runs it too; a red render blocks merge.
- Skills follow the [agentskills.io](https://agentskills.io/specification) SKILL.md format.
  Generic skills go in `seed/.claude/skills/`, research-only skills in `seed/_research/skills/`.
- Check `seed/.claude/rules/known-issues.md` first — many gotchas (YAML colons in
  descriptions, `--trust` requirement, tag-based Copier resolution) are already documented.

## Promoting a skill from your project

If you built a broadly useful skill in a Loam-bootstrapped project, you can promote it
back to the template — see `docs/SYNC.md` for the `template-sync promote` workflow.
Promotion PRs should state which project battle-tested the skill and what it was used for.

## Releases (maintainers)

Copier resolves from **git tags**, not HEAD. After merging significant changes:

```bash
bin/release.sh <version>   # bumps VERSION, tags, pushes — CI verifies and publishes the release
```

## Reporting issues

Open a GitHub issue with: your Copier version, the flavor (`is_research` true/false),
and the output of `bin/verify-template.sh` if the template fails to render.
