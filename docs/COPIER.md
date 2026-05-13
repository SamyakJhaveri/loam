# Copier Distribution

This template uses [Copier](https://copier.readthedocs.io/) as its primary distribution mechanism. Copier enables remote bootstrapping (no local clone needed), built-in downstream sync, and semver versioning via Git tags.

## How it works

The template content lives in `template/` (a Copier subdirectory). When you run `copier copy`, Copier:

1. Clones the template repo (or uses a local path)
2. Asks interactive questions (project name, flavors, GitHub repo)
3. Renders `.jinja` files with your answers (substituting `{{ project_name }}`, etc.)
4. Copies everything from `template/` into your new project
5. Runs post-tasks: merges selected flavor overlays into `.claude/`, creates seed folders, initializes git

## Questions

| Question | Type | Default | Description |
|----------|------|---------|-------------|
| `project_name` | string | (required) | Project name, used in docs and config |
| `flavors` | multiselect | `[research]` | Which flavor packs to include |
| `github_repo` | string | `""` | GitHub repo (owner/repo) to create via `gh` |

## Updating a project

```bash
cd my-project
uvx copier update           # pull latest template changes
uvx copier update --pretend # dry-run: see what would change
```

Copier tracks the template version in `.copier-answers.yml`. On update, it diffs between the version you generated from and the current template, applies changes, and lets you resolve conflicts.

## Versioning

Template versions are Git tags (e.g., `v1.0.0`). To pin a version:

```bash
uvx copier copy --vcs-ref v1.0.0 gh:samyakjhaveri/project-seed-framework ./my-project
```

New releases are created via `bin/release.sh`:

```bash
bin/release.sh 1.1.0  # updates VERSION, commits, tags, pushes
```

## `.copier-answers.yml`

Copier creates this file in your project root. It records:
- Your answers to the questions
- The template source (`_src_path`)
- The template commit (`_commit`)

This is the Copier equivalent of `template-manifest.json`. Both `template-sync promote` and `template-sync status` work with either file.

## Migration from shell-bootstrapped projects

```bash
cd my-existing-project

# Re-initialize with Copier (preserves existing files, adds .copier-answers.yml)
uvx copier copy --overwrite gh:samyakjhaveri/project-seed-framework .

# Future updates
uvx copier update
```

## Relationship to shell scripts

| Shell script | Copier equivalent |
|---|---|
| `bin/init-project.sh` | `copier copy` |
| `bin/template-sync.sh pull` | `copier update` |
| `bin/template-sync.sh sync-from-buffer` | `copier update` |
| `bin/template-sync.sh status` | `copier update --pretend` |
| `bin/add-flavor.sh` | `copier update --data` (approximate — re-runs all post-tasks) |

Shell scripts remain functional as fallback for environments without Copier/Python.

## Known limitation: flavor files on update

When running `copier update`, the post-tasks unconditionally re-copy flavor files (rules, hooks, agents, skills) into `.claude/`. If you have customized a flavor-originated file (e.g., `.claude/rules/python.md`), your changes will be overwritten. Copier's built-in merge only protects files it directly copies from `template/`, not files moved by post-tasks.

**Workaround:** After `copier update`, check `git diff` for unwanted overwrites and restore your customizations via `git checkout HEAD -- <file>`.
