# Copier distribution

This template uses [Copier](https://copier.readthedocs.io/) as its only forward-distribution mechanism: remote bootstrapping, three-way merge on updates, and semver versioning via git tags.

## How it works

Template content lives in `seed/` (`_subdirectory: "seed"` in `copier.yml`); everything outside `seed/` is invisible to Copier. `copier copy`:

1. Clones the template repo (or uses a local path) at the latest TAG.
2. Asks the questions below.
3. Renders `.jinja` files and copies `seed/` into the new project (`_preserve_symlinks: true` keeps the `.claude/skills/*` symlinks as symlinks).
4. Runs `_tasks` (git init, optional GitHub setup) - which is why `--trust` is mandatory.

## Questions

| Question | Type | Default | Effect |
|----------|------|---------|--------|
| `project_name` | string | (required) | Substituted into the top-level `.jinja` files |
| `github_repo` | string `owner/name` | `""` | `gh repo create` after init if non-empty |
| `project_kind` | choice | `python` | Gates `pyproject.toml` and the pyright-lsp plugin (python, research, mixed get both) |

## Updating a project

```bash
cd my-project
uvx copier update --trust              # apply latest tag, three-way merge on conflicts
uvx copier update --trust --pretend    # dry-run
```

Copier reads `.copier-answers.yml` (answers, `_src_path`, `_commit`) to compute the diff. Do not delete that file.

### Migrating a project rendered before v1.0.0

The public repo restarted history at v1.0.0, so older `_commit` refs no longer resolve. Re-apply once with `uvx copier recopy --trust gh:samyakjhaveri/loam`, review `git diff`, commit. Ordinary `copier update` works afterwards.

## Versioning

**Copier always resolves the latest tag, never main's HEAD.** Push without tagging and nothing ships.

```bash
bin/release.sh 5.0.0    # verify gate + IP sweep, bump VERSION, commit, tag, push
uvx copier copy --trust --vcs-ref v5.0.0 gh:samyakjhaveri/loam ./proj   # pin a version
```

Use `--vcs-ref=HEAD` against a local clone to test unreleased changes (this is what `bin/verify-template.sh` does).

## Copier visibility map

| Area | Location | Rendered to projects? |
|------|----------|----------------------|
| Deliverables | `seed/` | Yes |
| Template docs | `docs/` | No |
| Scripts | `bin/` | No |
| Knowledge base | `soil/` | No |
| Skill staging / marketplace | `cultivation/` | No |
