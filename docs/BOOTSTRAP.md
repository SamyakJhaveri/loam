# Bootstrap a new project

`loam` is a Copier template. Bootstrapping is one command from anywhere; no local clone needed.

## New project

```bash
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project
cd ./my-project
```

> **`--trust` is required.** The template runs `_tasks` after rendering (git init, optional GitHub setup). Without `--trust`, Copier skips them silently and the project comes out incomplete.

Copier asks two questions: `project_name` and `github_repo` (blank skips GitHub setup).

## What you get

- `CLAUDE.md` importing `AGENTS.md` (the one prose home), both with fill-in placeholders.
- `.claude/`: settings (model pin, permissions), 3 hooks (bash audit log, concurrent-checkout guard, stop verify gate).
- `.agents/skills/catchup/`: session-bootstrap skill shared by Claude Code (via symlink) and Codex.
- `.codex/`: config + execution rules. Inert until you trust the project in Codex and review hooks via `/hooks`.

## After bootstrap

1. Fill in the placeholders in `AGENTS.md` and `CLAUDE.md` (purpose, commands, conventions).
2. Optionally install the `sam-cc-setup` plugin for the review agents and planning skills.

## Update an existing project

```bash
cd my-project && uvx copier update --trust
```

Copier resolves TAGS, not HEAD: an update only sees the latest released tag.
