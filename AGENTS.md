# AGENTS.md — Loam

> Bridge file for OpenAI Codex (and any AGENTS.md-aware agent) working **on the Loam repo**.
> Claude Code reads `CLAUDE.md` + `.claude/rules/*.md`; this file points non-Claude agents at the
> same conventions and surfaces the hard rules inline. This file lives at the repo root only — it is
> **not** under `seed/`, so it does **not** ship to bootstrapped projects.

## What this repo is

Loam is simultaneously a **Copier template** and a **Claude Code project** (v3.1). Bootstrapping a
project renders everything under `seed/` into the new project. The repo's own `.claude/` is a
symlink to `seed/.claude/`, so editing one edits both.

## Folder map

| Path | Purpose |
|------|---------|
| `seed/`          | Copier `_subdirectory` — **everything here ships to bootstrapped projects** |
| `seed/.claude/`  | Skills, agents, hooks, rules, settings (shipped) |
| `seed/_research/`| Research-flavor overlay (applied when `is_research=true`) |
| `seed/*.jinja`   | Copier-rendered files (CLAUDE.md, AGENTS.md, README.md, …) |
| `cultivation/`   | Skill staging: `wip/`, `marketplace/`, `retired/` |
| `soil/`          | Knowledge base: `jvc/`, `foundation/`, `playbooks/` |
| `docs/`          | Template docs; `docs/plans/` (session plans), `docs/specs/` (design specs), `docs/diagrams/` |
| `bin/`           | `verify-template.sh`, `template-sync.sh`, `release.sh`, lint scripts |
| `_archive/`      | Human-only reference; **not** loaded into agent context |
| `copier.yml`     | Copier config (`_subdirectory: "seed"`, questions, `_tasks`) |
| `VERSION`        | Semver for releases |

## Full conventions live elsewhere — read them

The complete rules are in **`CLAUDE.md`** (project map) and **`.claude/rules/*.md`** (the detail).
Start with `.claude/rules/workflow.md` (6-stage session workflow) and
`.claude/rules/known-issues.md` (recurring gotchas). Caveat: `CLAUDE.md` and the skills reference
Claude-Code-only features (the `Skill` tool, `/slash-commands`, claude.ai-hosted MCP servers) that
Codex cannot invoke — read them for the *conventions*, not for tools you can run.

## Hard rules (non-negotiable)

1. **Commit directly to `main`.** No branches unless the user explicitly asks.
2. **Only `seed/` ships.** Never put project-specific content in `seed/` — everything there must be
   generic or scoped to a flavor. This `AGENTS.md` and `.codex/` stay at the root, never in `seed/`.
3. **Verify before any commit:** run `bin/verify-template.sh` and expect `ALL OK`.
4. **Source is ground truth, not docs.** If a doc contradicts the code, trust the code and fix the doc.
5. **One behavior change per session.** Don't bundle unrelated edits.

### Diagram-specific rules (the `diagrams` skill / Yoshida renders)

- **Never commit copyrighted Yoshida scans.** `yoshida_hiroshi/` is gitignored (style refs, local-only).
- **Never commit hero renders.** `docs/diagrams/loam-hero-*.png` is gitignored. (Committed
  `*.drawio.png` vector diagrams are unaffected — the ignore is scoped to `loam-hero-*`.)
- Renders are named `loam-hero-<NN>-<concept>-c<idx>.png` (e.g. `loam-hero-03-context-routing-c1.png`),
  written by `seed/.claude/skills/diagrams/scripts/render-yoshida.py`.
- **Positive framing in all image prompts** — describe what you *want*, never "no/without/avoid X".
  Gemini image models treat negations poorly and garble rendered text.
- YAML in skill files: quote or fold (`>`) any description containing a colon; keep specialized
  skills at `auto-activate: false`; use kebab-case for filenames.

### MCP caveat for Codex

The repo's diagram MCP servers (drawio, excalidraw, tldraw) are **claude.ai-hosted and authed
through Claude** — they do not port to Codex. The Codex-drivable path is **Track B** (direct Gemini
API via `render-yoshida.py`, which needs `GEMINI_API_KEY` + network access).
