# Copier distribution

This template uses [Copier](https://copier.readthedocs.io/) as its only distribution mechanism. The previous shell bootstrap (`bin/init-project.sh`) was removed in v2.0. Copier enables remote bootstrapping (no local clone), built-in three-way merge on updates, and semver versioning via Git tags.

## How it works

The template content lives in `seed/` (`_subdirectory: "seed"` in `copier.yml`). Everything outside `seed/` is invisible to Copier. When you run `copier copy`:

1. Copier clones the template repo (or uses a local path).
2. Asks the three questions: `project_name`, `is_research`, `github_repo`.
3. Renders `.jinja` files, substituting `{{ project_name }}` and other answers.
4. Copies everything from `seed/` into the new project, excluding patterns from `_exclude:`.
5. Runs post-tasks: applies the research flavor if `is_research=true`, removes the `seed/_research/` overlay, creates seed working directories, runs `git init`, makes the initial commit.

## Questions

| Question | Type | Default | Effect |
|----------|------|---------|--------|
| `project_name` | string | (required) | Substituted into top-level `.md.jinja` files and `.mcp.json.jinja` |
| `is_research` | bool | `false` | Overlay `seed/_research/` onto `.claude/` and add research seed-docs |
| `github_repo` | string `owner/name` | `""` | `gh repo create` after init if non-empty |

## Updating a project

```bash
cd my-project
uvx copier update --trust              # apply latest template, three-way merge on conflicts
uvx copier update --trust --pretend    # dry-run; show what would change
```

Copier reads `.copier-answers.yml` to know which template ref the project was last rendered against, fetches the current template, and diffs.

### Migrating a project rendered before v1.0.0

Loam's public repository restarted its git history at **v1.0.0**. A project last rendered against an older ref records a `_commit` in `.copier-answers.yml` that no longer exists upstream, so `copier update` cannot compute its three-way merge and will fail. Re-apply the template once with `recopy`:

```bash
cd my-project
uvx copier recopy --trust gh:samyakjhaveri/loam    # re-render at latest tag; your answers are preserved
git diff                                            # review, then commit
```

`recopy` re-runs the questionnaire (pre-filled from your saved answers) and regenerates from scratch rather than diffing against a missing commit. After this one-time step, ordinary `copier update` works again.

## Versioning

Template versions are Git tags (e.g. `v1.0.0`). **Copier always resolves to the latest tag, not the latest commit on main.** If you push features without tagging, `copier copy` will not include them.

Pin a specific version at bootstrap:

```bash
uvx copier copy --trust --vcs-ref v1.0.0 gh:samyakjhaveri/loam ./my-project
```

New releases via `bin/release.sh`:

```bash
bin/release.sh 3.2.0
```

The script bumps `VERSION`, commits, tags, and pushes.

Before a release (and on any Copier/Loam version bump), run `bin/spike-probes.sh` — a standalone regression guard that re-verifies the mechanism-spike findings (copy/promote/fork/update/conflict behavior) against the current Copier and git. It is intentionally **not** wired into the `/validate` gate or `bin/verify-template.sh` (it clones + runs Copier several times and is slow); run it manually. It exits non-zero if any spike verdict has regressed. At PR #1's pre-fix baseline, assertion #8 is intentionally red; after the timestamp fix lands, any #8 failure is a regression.

> **Gotcha:** Always create a new tag after pushing significant changes. Without a tag update, `copier copy` silently serves the old version. Use `--vcs-ref=HEAD` for testing unreleased changes.

## `.copier-answers.yml`

Created in the project root at bootstrap. Records:

- The user's answers to the questions
- `_src_path` — the template source URL or local path
- `_commit` — the exact commit SHA the project was rendered from

Both `template-sync promote` and `template-sync status` read this file. Do not delete it; `copier update` will fail without it.

## Seed-subdirectory architecture (v3.0)

Template deliverables live in `seed/` (`_subdirectory: "seed"` in `copier.yml`). Everything outside `seed/` is invisible to Copier — safe by default. New files never leak unless explicitly placed in `seed/`.

| Area | Location | Copier visibility |
|------|----------|-------------------|
| Deliverables | `seed/` | Rendered to projects |
| Template docs | `docs/` | Invisible |
| Scripts | `bin/` | Invisible |
| Knowledge base | `soil/` | Invisible |
| Skill staging | `cultivation/` | Invisible |

The `_exclude` list is ~9 generic patterns (`.DS_Store`, `*.pyc`, etc.). No template-machinery exclusions needed.

## Known limitation: flavor files on update

When running `copier update`, the post-tasks unconditionally re-overlay `seed/_research/` files into `.claude/` if `is_research=true`. If you customize a research-flavor file (for example `.claude/rules/research-memory.md`), your edit is overwritten on next update. Copier's built-in three-way merge protects files it directly renders from the template root, not files moved into place by the `_tasks` step.

Workaround: after `copier update`, check `git diff` for unwanted overwrites and restore customizations via `git checkout HEAD -- <file>`. A more principled fix (move the research overlay into a properly-Jinja-rendered tree rather than a `_tasks` shell copy) is open as future work.

## What changed in v3.0

- `_subdirectory` changed from `"."` to `"seed"` — **breaking change** for `copier update` from v2.0 projects (see `docs/MIGRATION-v3.md`)
- Exclusion patterns reduced from 36 to ~9 (template machinery moved outside `seed/`)
- Skills consolidated: 24 → 17 (4 dissolved into AGENTS.md, 3 merged)
- Agents consolidated: 11 → 6 (5 merged into remaining agents)
- Hooks consolidated: 12 → 8 (4 removed/merged)
- Templates consolidated: 14 → 7 (7 now generated on-demand by skills)
