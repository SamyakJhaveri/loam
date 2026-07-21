# Syncing assets between a project and the template

The buffer pattern: when you build a generally-useful agent / skill / hook / rule in a project, you can promote it back to the template so future bootstraps and `copier update`s pick it up.

## The two flows

```
                   copier update
project/.claude/  ◀──────────────  template (git tags)
                  ──────────────▶
                   template-sync promote (PR-based)
```

Upstream pull uses Copier directly. Downstream promotion uses the `template-sync` skill, which opens a PR rather than writing to `main`.

## Hard rule

**Promotion is opt-in only.** No background hooks. No file watchers. No side-effects from other skills. The `template-sync` skill runs only when you explicitly invoke it. Auto-deciding what deserves promotion is exactly how a buffer rots into a dump folder.

## How to promote

From inside a Copier-bootstrapped project, in Claude Code:

```
template-sync promote --layer generic .claude/skills/<name>/SKILL.md
# or
template-sync promote --layer flavor:research .claude/skills/<name>/SKILL.md
```

> Copier renders only `seed/` into a project, so a bootstrapped project has no `bin/`. The skill drives `bin/template-sync.sh` from a local `loam` clone with the project as the working directory (e.g. `bash ~/Desktop/loam/bin/template-sync.sh promote …`), not a copy shipped into the project.

Choose the layer deliberately:

- `--layer generic` writes to `seed/.claude/<relpath>` in the template — ships to every future project. Use when the skill is useful regardless of project type.
- `--layer flavor:research` writes to `seed/_research/<relpath-stripped>` in the template — ships only when `is_research=true`. Use for skills tied to papers, experiments, citations, HPC, etc.

The skill walks a ten-step flow:

1. Validates `.copier-answers.yml` (or legacy `template-manifest.json`) exists.
2. Resolves the template path (`$TEMPLATE_PATH` → `_src_path` from `.copier-answers.yml` → manifest entry → default `~/Desktop/loam`).
3. Verifies the template's working tree is clean.
4. Scans the asset for project-specific names, hardcoded paths, secrets, legacy references.
5. Maps the asset to its template path via `template_path_for` (`.claude/X` for generic, `_<flavor>/X-stripped` for flavor:NAME).
6. Creates a branch `sync/<project>/<asset-slug>/<timestamp>` in the template repo.
7. Copies the asset.
8. Commits with a structured message: `promote($layer): $tpl_relpath from $pname`.
9. Pushes the branch to `origin`.
10. Prints the `gh pr create` command.

The asset lands in the template only when you merge the PR.

## How to pull

After a PR merges into the template's `main`, propagate to existing projects:

```bash
cd <my-project>
uvx copier update --trust
```

Copier renders the new template against the recorded answers, diffs against current project state, and offers a three-way merge for any conflict. Local changes that don't conflict are preserved. `.copier-answers.yml` records the new ref.

The legacy `template-sync sync-from-buffer` (file-by-file `cp`) is still available for projects that don't have `.copier-answers.yml` but pre-date Copier, but `copier update` is the preferred path.

## How to inspect

```bash
template-sync status              # classify each .claude/ file as unchanged / modified / local-only / template-only
template-sync diff <relpath>      # unified diff vs the template
```

## What the safety net checks at promote time

Before writing to the template branch, the skill scans the asset for:

- The project's own name (from `.copier-answers.yml` `project_name`)
- Absolute paths under `/Users/...` or `/home/...`
- Secret-like strings (API keys, tokens, OAuth bearers)
- Machine-local toolchain paths

Each hit stops the flow and asks: abort / generalize the asset / promote anyway. You decide.

## What the skill must not do

- Promote as a side effect of any other skill (`/validate`, `/fix-bug`, etc.).
- Push to template `main` directly. Always a branch + PR.
- Promote `.env`, `secrets/`, or matching files without explicit override.
- Run from a project without `.copier-answers.yml` (or, in legacy projects, `template-manifest.json`).

## v3.0 changes to sync

- The previous `template/.claude/` mirror is gone. `template_path_for "generic" "<relpath>"` now returns `seed/<relpath>` directly.
- Flavor promotion target changed: `flavors/<NAME>/<relpath-stripped>` is now `seed/_<NAME>/<relpath-stripped>`. Only `seed/_research/` exists today; `_software-eng/` is gone (folded into default).
- The default template path is `~/Desktop/loam`, not `~/Desktop/project_template`.
- Status of the promote workflow as of v3.0 release: zero promote commits exist in `main` history. The workflow is wired but unproven end-to-end. Dogfood it once with a real skill before relying on it.
