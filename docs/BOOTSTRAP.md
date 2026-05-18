# Bootstrap a new project

`project_seed_framework` is a Copier template. Bootstrapping a new project is one command from anywhere on your machine — no local clone required. The previous shell bootstrap (`init-project.sh`) was removed in v2.0; Copier is the only path.

## New project from the latest template

```bash
uvx copier copy gh:samyakjhaveri/project-seed-framework ./my-project
cd ./my-project
```

To pin to a specific version:

```bash
uvx copier copy --vcs-ref v2.0.0 gh:samyakjhaveri/project-seed-framework ./my-project
```

To run non-interactively:

```bash
uvx copier copy --defaults \
  --data "project_name=my-project" \
  --data "is_research=true" \
  gh:samyakjhaveri/project-seed-framework ./my-project
```

Copier writes `.copier-answers.yml` at the project root recording the template ref applied; do not delete it. It is what `copier update` reads to diff against newer template revisions.

## The three questions Copier asks

| Question | Type | Effect |
|----------|------|--------|
| `project_name` | string (required) | Substituted into `CLAUDE.md`, `README.md`, `MEMORY.md`, `HANDOFF.md`, `.mcp.json`, and other rendered top-level files. |
| `is_research` | bool, default `false` | If `true`, the research flavor merges in: `_research/{skills,agents,hooks,rules}/*` overlays onto `.claude/{skills,agents,hooks,rules}/`, `_research/docs/*.md.jinja` becomes paper-writing seed-docs at project root (`REFERENCES.md`, `EXPERIMENT-PROTOCOL.md`, `EXPERIMENTS.md`, `FINDINGS.md`, `RESULTS.md`), and `_research/settings-hooks.json` deep-merges into `.claude/settings.json`. Then `_research/` itself is removed from the rendered project. |
| `github_repo` | string `owner/name`, default empty | If set, runs `gh repo create --private --source=. --remote=origin --push` after init. Skip if you'll add the remote manually. |

## What you get

After Copier finishes, the project has:

- **L0 entry**: `CLAUDE.md` (sized to the ~800-token L0 budget; see `.claude/rules/L0-budget.md`)
- **Top-level docs**: `README.md`, `MEMORY.md`, `HANDOFF.md`, `AGENTS.md`, `CONTEXT.md`, `SCRIPTS_DIRECTORY.md`, plus `ARCHITECTURE.md` and `DESIGN.md`
- **Research-only docs** (if `is_research=true`): `REFERENCES.md`, `EXPERIMENT-PROTOCOL.md`, `EXPERIMENTS.md`, `FINDINGS.md`, `RESULTS.md`
- **`.claude/`**: 19 core skills, 7 agents, 11 hooks (including the new `session-start.sh`), 11 rule files (the four ICM routing rules `L0-budget.md`, `context-md-anatomy.md`, `stage-contract.md`, `layer-triage.md`, plus `workflow.md`, `known-issues.md`, `validation-loop.md`, and the path-scoped `architecture.md`, `python.md`, `tech-stack.md`, `frontend-design.md`), `settings.json` with the SessionStart hook wired
- **MCP**: `.mcp.json` registers Graphify and the Knowledge-Graph Memory MCP
- **Config**: `.gitignore`, `.editorconfig`, `pyproject.toml`, `.copier-answers.yml`
- **Seed working directories**: `archive/`, `config/`, `files_from_team/`, `internal_docs/`, `meeting_notes/`, `presentations/`, `results/`, `scripts/`, `submission_artifacts/`, `submission_docs/` (each with `.gitkeep`)
- **First commit**: "Initial commit from project-seed-framework"

## Pull future template updates into an existing project

```bash
cd ./my-project
uvx copier update
```

Copier renders the latest template against the recorded answers, diffs against the current project state, and offers a three-way merge for conflicts. Local edits that don't conflict are preserved. The `.copier-answers.yml` is updated to record the new ref.

## What gets excluded from the rendered project

The exclusion list lives in `copier.yml` (`_exclude:`). Reasons content does not propagate, grouped:

- **Framework machinery** — `bin/`, `docs/`, `copier.yml`, `VERSION`, `LICENSE`. These run the template, not the rendered project.
- **Template-author working files** — root `CLAUDE.md`, `README.md`, `HANDOFF.md`, `.gitignore`, `.claudeignore`, `template-manifest.schema.json`, `.github/`. The Jinja-suffixed versions of CLAUDE.md/README.md/HANDOFF.md ship instead.
- **Internal references** — `claude_code_course_files/`, `internal_docs/`, `outputs/`, `IMG_*`. Reference material the template author studies; not part of what every project inherits.
- **Marketplace candidates** — `seed-skills/` (14 skills cut from default core in v2.0). Available for reference; install via plugin marketplace post-bootstrap if needed.
- **Local-only Claude Code state** — `.claude/audit.log`, `.claude/.local-paths`, `.claude/settings.local.json`, `.claude/worktrees/`.

## Verifying the template

Before any PR that touches `.claude/`, `_research/`, `bin/`, `copier.yml`, or top-level `.jinja` files:

```bash
bin/verify-template.sh
```

Asserts: single-tree invariant (no `template/` subdir), valid JSON in `settings.json`, agentskills.io schema for every `SKILL.md` (name + description present in front-matter), Copier render produces a valid project in both `default` and `is_research=true` variants, no template-author files leak. Exits non-zero on any violation.

## After bootstrap — first session

1. Open the project in Claude Code. The `SessionStart` hook fires and injects the framework brief (19 core skills, Pipeline Gate ordering, four ICM routing layers).
2. Replace placeholder content in `CLAUDE.md` with project specifics. Stay within ~800 tokens (`.claude/rules/L0-budget.md`).
3. If using the Knowledge-Graph Memory MCP, let the model populate `.claude-memory/knowledge-graph.json` during sessions; the `/know-me` skill writes structured facts.
4. If using Graphify, run `graphify .` after the first non-trivial commit to seed the codebase map.
