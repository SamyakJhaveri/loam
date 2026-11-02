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
| `memory` | bool | `true` | Gates the session-memory system: the `mem-*` hooks, their registration in `.claude/settings.json` and `.codex/hooks.json`, Codex's `features.hooks`, `bin/memsearch`, `bin/mem-inspect`, `bin/mem-weekly.sh`, `THIRD_PARTY_NOTICES`, and the memory prose in `AGENTS.md`, `.gitignore`, `docs/HARNESS.md` and `docs/WORKERS.md`; with `false` the handoff is `HANDOFF.md` |

## Updating a project

```bash
cd my-project
uvx copier update --trust              # apply latest tag, three-way merge on conflicts
uvx copier update --trust --pretend    # dry-run
```

Copier reads `.copier-answers.yml` (answers, `_src_path`, `_commit`) to compute the diff. Do not delete that file.

### First update from v3.0.0

A plain `copier update` runs the old version's `_tasks` in Copier's temporary render of that version, which has no `.git` and no `origin`.
v3.0.0's tasks run `git init` and `_gh_setup.sh` there whenever `github_repo` is set.
With `gh` logged in, that is one `git push -u origin` of the temporary render's initial commit to the project's GitHub repo and one ruleset `POST` to the GitHub API (and `gh repo create` when the repo does not exist).
This affects the first update off v3.0.0, or off any Loam commit before 47caead3 (19 Oct 2026); from 47caead3 on, those two tasks run on `copy` only.
Run that first update in one of two safe ways:

```bash
GH_CONFIG_DIR="$(mktemp -d)" env -u GH_TOKEN -u GITHUB_TOKEN uvx copier update --trust   # gh sees no login, so _gh_setup.sh exits before the push
uvx copier update --trust --skip-tasks && rm -f _gh_setup.sh                                 # no task runs anywhere
```

`--skip-tasks` also skips the settings strip (task 1), so with a non-Python `project_kind` or `memory=false` read `.claude/settings.json` in the diff before you commit.
DistBench takes releases only through `bin/sync-project` ([SYNC.md](SYNC.md)), which skips tasks and deletes `_gh_setup.sh`.

### Migrating a project rendered before v1.0.0

The public repo restarted history at v1.0.0, so older `_commit` refs no longer resolve. Re-apply once with `uvx copier recopy --trust gh:samyakjhaveri/loam`, review `git diff`, commit. Ordinary `copier update` works afterwards.

## Versioning

**Copier always resolves the latest tag, never main's HEAD.** Push without tagging and nothing ships.

```bash
bin/release.sh 5.0.0    # main's ruleset requires verify and stub-sweep + green CI + a verify-loam render of HEAD with doctor and rendered check ok (no sessions) + IP sweep; bump VERSION, commit, tag, push, render the tag
uvx copier copy --trust --vcs-ref v5.0.0 gh:samyakjhaveri/loam ./proj   # pin a version
```

Use `--vcs-ref=HEAD` against a local clone to test unreleased changes (this is what the render smoke in `bin/check` does).

## Copier visibility map

| Area | Location | Rendered to projects? |
|------|----------|----------------------|
| Deliverables | `seed/` | Yes |
| Template docs | `docs/` | No |
| Scripts | `bin/` | No |
| Knowledge base | `soil/` | No |
| Skill staging / marketplace | `cultivation/` | No |
