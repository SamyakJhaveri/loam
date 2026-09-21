# Bootstrap a new project

`loam` is a Copier template. Bootstrapping is one command from anywhere; no local clone needed.

## New project

```bash
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project
cd ./my-project
```

> **`--trust` is required.** The template runs `_tasks` after rendering (git init, optional GitHub setup). Without `--trust`, Copier skips them silently and the project comes out incomplete.

Copier asks three questions: `project_name`, `github_repo` (blank skips GitHub setup), and `project_kind` (gates `pyproject.toml` and the pyright-lsp plugin; python, research, mixed get both).

## What you get

- `CLAUDE.md` importing `AGENTS.md` (the one prose home), both with fill-in placeholders.
- `.claude/`: Claude Code settings (deny list, sandbox) and the lifecycle hook scripts: the Fable session brief and post-compaction reminder, plus the zero-model memory layer (`mem-capture.sh` on SessionEnd/PreCompact/Stop copies each transcript to the per-user store; `mem-recall.sh` on SessionStart injects the last few sessions). Companion tools `bin/memsearch` and `bin/mem-weekly.sh` search the store and report recurring errors. See `docs/HARNESS.md`.
- `.agents/skills/`: three skills shared by Claude Code (via symlink) and Codex: `catchup` (session bootstrap), `fable-prompting` (index over the Fable 5.1 guide), `hypothesis-tree` (persistent investigation tree).
- `.codex/`: Codex configuration and execution rules (`rules/loam.rules`, the same deny families), plus `.codex/hooks.json`, which registers the memory hooks; `features.hooks` is on. All of it is inert until you trust the project in Codex.
- `.loam/runtime/`: the qualification runtime; see `docs/runtime/SETUP.md`.

## After bootstrap

1. Fill in the placeholders in `AGENTS.md` and `CLAUDE.md` (purpose, commands, conventions).
2. Optionally install the `sam-cc-setup` plugin for the review agents and planning skills.

## Update an existing project

```bash
cd my-project && uvx copier update --trust
```

Copier resolves TAGS, not HEAD: an update only sees the latest released tag.
