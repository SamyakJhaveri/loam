# Bootstrap a new project

The only supported way to create a new project from this template is `bin/init-project.sh`.
Manual `git clone` is unsupported because it preserves the template's git identity inside the new project.

## Quick start

```bash
~/Desktop/project_template/bin/init-project.sh ~/code/my-new-project --flavor research
cd ~/code/my-new-project
```

For a software engineering project:

```bash
~/Desktop/project_template/bin/init-project.sh ~/code/my-app --flavor software-eng
```

For a project that combines both:

```bash
~/Desktop/project_template/bin/init-project.sh ~/code/my-research-tool \
  --flavor research --flavor software-eng
```

## Flags

| Flag | Effect |
|------|--------|
| `--flavor <name>` | Apply a flavor pack. Repeatable. Valid: `research`, `software-eng`. |
| `--name <name>`   | Override the project name (defaults to basename of `<project-path>`). |
| `--github <owner/repo>` | Create a GitHub repo and set it as `origin` via `gh repo create`. Requires `gh` CLI. |
| `-h`, `--help`    | Show usage. |

## What `init-project.sh` does

1. Creates the target directory (refuses if non-empty).
2. Copies the generic core (`.claude/`).
3. Materialises empty `seed-folders/` (archive, config, internal_docs, meeting_notes, presentations, results, scripts, submission_artifacts, submission_docs, files_from_team) with `.gitkeep` files.
4. Renders `seed-docs/*.tmpl` and `seed-config/*.tmpl` into the project root, substituting `{{PROJECT_NAME}}`, `{{DATE}}`, `{{YEAR}}`, `{{FLAVORS}}`.
5. Overlays each `--flavor` (skills/agents/hooks/rules merged into `.claude/`; flavor seed-docs added to root).
6. Writes `template-manifest.json` recording the template's commit SHA + applied flavors.
7. `git init`, makes the initial commit.
8. Optionally creates a GitHub repo as `origin` if `--github` is passed.

## What `init-project.sh` does NOT do

- It does NOT add `template` as a git remote on the new project. The template is remembered via `template-manifest.json` only. This makes accidental pushes back to the template impossible.
- It does NOT install dependencies. You handle `pip install`, `npm install`, etc. yourself after init.

## Adding a flavor later

```bash
~/Desktop/project_template/bin/add-flavor.sh software-eng --project ~/code/my-project
```

Refuses to overlay onto locally modified files unless `--force`.

## Verifying success

After init, sanity check:

```bash
cd <project-path>
ls -la                    # see seeded docs and folders
cat template-manifest.json
git log --oneline         # initial commit recorded
git remote -v             # empty unless --github was passed
```
