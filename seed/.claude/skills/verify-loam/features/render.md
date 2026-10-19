# Render

A user runs `copier copy` and gets a project that is already a git repository with one commit, carries the agent harness, and passes its own `bin/check`.

## Sub-features

- `render-copy` renders the template into a new directory with no prompts when data is given.
- `render-git` initializes git and makes the commit `Initial commit from loam`.
- `render-kind` gates `pyproject.toml` and the pyright-lsp plugin on `project_kind` (python, research, mixed get both).
- `render-check` passes the rendered `bin/check` on the fresh project and fails it on a committed defect.
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
- **Check.** Run `$C check r1`. `last_line` starts with `check: PASSED`, `"pristine": true`, exit 0. Alone this proves little: a fresh render has no `tests/`, so pytest does not run.
- **Exclude.** List `<root>/r1/render/.claude/skills/`. It holds `catchup`, `fable-prompting`, `hypothesis-tree` and no `verify-loam`.
- **Check can fail.** Commit a defect in the render: `printf 'trailing space \n' > <root>/r1/render/defect.txt && git -C <root>/r1/render add defect.txt && git -C <root>/r1/render -c user.name=verify -c user.email=verify@example.invalid commit -qm defect`. Run `$C check r1`. Exit 1, `"last_line": "check: FAILED"`, and `check.txt` contains `defect.txt:1: trailing whitespace.` and `FAIL: whitespace or conflict markers`. A pass here means the check is broken.
- **Clean up.** Run `$C cleanup r1` and `$C cleanup r2`.

## Gotchas

- `--ref HEAD` on a dirty checkout renders the working tree as a copier WIP commit (`_commit` reads one past `git describe HEAD`). Commit first if you need the exact HEAD.
- A `--ref` other than HEAD ignores uncommitted edits.
- Released projects come from tags, not `main`; render the tag to reproduce a user's project.
- Commit the defect: the scan that must catch it is the one over committed files (`git diff --check` from the empty tree to `HEAD`), which is what CI's clean checkout sees.
- Each `$C check` overwrites `check.txt` and the `check` record in `run.json`. After the defect step `r1` is no longer pristine, so no later check of it can satisfy the `bin/release.sh` gate; use a separate run for that.
