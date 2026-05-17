# Copier distribution

This template uses [Copier](https://copier.readthedocs.io/) as its only distribution mechanism. The previous shell bootstrap (`bin/init-project.sh`) was removed in v2.0. Copier enables remote bootstrapping (no local clone), built-in three-way merge on updates, and semver versioning via Git tags.

## How it works

The template content lives at the repo root (`_subdirectory: "."` in `copier.yml`). When you run `copier copy`:

1. Copier clones the template repo (or uses a local path).
2. Asks the three questions: `project_name`, `is_research`, `github_repo`.
3. Renders `.jinja` files, substituting `{{ project_name }}` and other answers.
4. Copies everything from the template root into the new project, excluding patterns from `_exclude:`.
5. Runs post-tasks: applies the research flavor if `is_research=true`, removes the `_research/` overlay, creates seed working directories, runs `git init`, makes the initial commit.

## Questions

| Question | Type | Default | Effect |
|----------|------|---------|--------|
| `project_name` | string | (required) | Substituted into top-level `.md.jinja` files and `.mcp.json.jinja` |
| `is_research` | bool | `false` | Overlay `_research/` onto `.claude/` and add research seed-docs |
| `github_repo` | string `owner/name` | `""` | `gh repo create` after init if non-empty |

## Updating a project

```bash
cd my-project
uvx copier update                # apply latest template, three-way merge on conflicts
uvx copier update --pretend      # dry-run; show what would change
```

Copier reads `.copier-answers.yml` to know which template ref the project was last rendered against, fetches the current template, and diffs.

## Versioning

Template versions are Git tags (e.g. `v2.0.0`). Pin a specific version at bootstrap:

```bash
uvx copier copy --vcs-ref v2.0.0 gh:samyakjhaveri/project-seed-framework ./my-project
```

New releases via `bin/release.sh`:

```bash
bin/release.sh 2.1.0
```

The script bumps `VERSION`, commits, tags, and pushes.

## `.copier-answers.yml`

Created in the project root at bootstrap. Records:

- The user's answers to the questions
- `_src_path` — the template source URL or local path
- `_commit` — the exact commit SHA the project was rendered from

Both `template-sync promote` and `template-sync status` read this file. Do not delete it; `copier update` will fail without it.

## Single-tree structure (v2.0)

The repo IS the Copier template. The previous `template/` subdirectory was deleted in v2.0; everything Copier ships now lives at root. The `_exclude:` list in `copier.yml` keeps framework machinery (`bin/`, `docs/`, `copier.yml`, `VERSION`, `LICENSE`) and template-author working files (root `CLAUDE.md`, `README.md`, `HANDOFF.md`) from propagating.

See `docs/ASSET-LAYERS.md` for the layer-by-layer breakdown of what ships and where.

## Known limitation: flavor files on update

When running `copier update`, the post-tasks unconditionally re-overlay `_research/` files into `.claude/` if `is_research=true`. If you customize a research-flavor file (for example `.claude/rules/research-memory.md`), your edit is overwritten on next update. Copier's built-in three-way merge protects files it directly renders from the template root, not files moved into place by the `_tasks` step.

Workaround: after `copier update`, check `git diff` for unwanted overwrites and restore customizations via `git checkout HEAD -- <file>`. A more principled fix (move the research overlay into a properly-Jinja-rendered tree rather than a `_tasks` shell copy) is open as future work.

## What changed in v2.0

- `_subdirectory: template` → `_subdirectory: "."` (single-tree)
- `flavors` multi-select → `is_research` boolean
- `_software-eng` flavor folded into the default seed
- Removed `bin/init-project.sh`, `bin/add-flavor.sh`, `seed-docs/`, `seed-config/`, `seed-folders/` (shell bootstrap deleted)
- `_exclude:` expanded to handle the larger surface area now at repo root
