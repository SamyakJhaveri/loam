# Render

A user runs `copier copy` and gets a project that is already a git repository with one commit, carries the agent harness, and passes its own `bin/check`.

## Sub-features

- `render-copy` renders the template into a new directory with no prompts when data is given.
- `render-git` initializes git and makes the commit `Initial commit from loam`.
- `render-kind` gates `pyproject.toml` and the pyright-lsp plugin on `project_kind` (python, research, mixed get both).
- `render-check` makes the rendered `bin/check` pass on the fresh project.
- `render-exclude` keeps Loam-only files (`.claude/stale-counts.json`, `.claude/skills/verify-loam`) out of the render.

## How to get to it (user POV)

- `uvx copier copy --trust gh:samyakjhaveri/loam ./my-project` (released tag).
- `uvx copier copy --trust --vcs-ref HEAD <loam checkout> ./my-project` (unreleased work).

## Driving it with control-loam

Preconditions:

- `copier` or `uvx` is on PATH.

- **Copy.** Run `$C render --run r1`. JSON has `"ok": true` and a `render` path.
- **Git.** Run `$C doctor r1`. The check `render is a git repo with the initial commit` passes.
- **Kind.** Run `$C render --run r2 --kind typescript`. `<root>/r2/render/pyproject.toml` does not exist, and `enabledPlugins` in its `.claude/settings.json` has no `pyright-lsp@claude-plugins-official`. With the default kind, both are present.
- **Check.** Run `$C check r1`. `"last_line": "check: PASSED"`, exit 0.
- **Exclude.** List `<root>/r1/render/.claude/skills/`. It holds `catchup`, `fable-prompting`, `hypothesis-tree` and no `verify-loam`.

## Gotchas

- `--ref HEAD` on a dirty checkout renders the working tree as a copier WIP commit (`_commit` reads one past `git describe HEAD`). Commit first if you need the exact HEAD.
- A `--ref` other than HEAD ignores uncommitted edits.
- Released projects come from tags, not `main`; render the tag to reproduce a user's project.
