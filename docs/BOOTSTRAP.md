# Bootstrap a new project

`loam` is a Copier template. Bootstrapping a new project is one command from anywhere on your machine — no local clone required. The previous shell bootstrap (`init-project.sh`) was removed in v2.0; Copier is the only path.

## New project from the latest template

```bash
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project
cd ./my-project
```

> **`--trust` is required.** This template uses `_tasks` in `copier.yml` for post-generation steps (research flavor overlay, `git init`, seed directories). Without `--trust`, Copier skips all tasks silently, producing an incomplete project.

To pin to a specific version:

```bash
uvx copier copy --trust --vcs-ref v3.1.0 gh:samyakjhaveri/loam ./my-project
```

To run non-interactively:

```bash
uvx copier copy --trust --defaults \
  --data "project_name=my-project" \
  --data "is_research=true" \
  gh:samyakjhaveri/loam ./my-project
```

Copier writes `.copier-answers.yml` at the project root recording the template ref applied; do not delete it. It is what `copier update` reads to diff against newer template revisions.

## The three questions Copier asks

| Question | Type | Effect |
|----------|------|--------|
| `project_name` | string (required) | Substituted into `CLAUDE.md`, `README.md`, `.mcp.json`, and other rendered top-level files. |
| `is_research` | bool, default `false` | If `true`, the research flavor merges in: `seed/_research/{skills,agents,hooks,rules}/*` overlays onto `.claude/{skills,agents,hooks,rules}/`, `seed/_research/seed-docs/*.md.jinja` becomes paper-writing seed-docs at project root (`REFERENCES.md`, `EXPERIMENT-PROTOCOL.md`, `EXPERIMENTS.md`, `FINDINGS.md`, `RESULTS.md`, `CHANGELOG.research.md`), and `seed/_research/settings-hooks.json` deep-merges into `.claude/settings.json`. Then `seed/_research/` itself is removed from the rendered project. |
| `github_repo` | string `owner/repo`, default empty | If set, creates (as private) or connects to the GitHub repo after init. Handles existing repos (adds remote + push), strips trailing `.git`, checks `gh` auth. Skipped on `copier update` if origin is already configured. |

## What you get

After Copier finishes, the project has:

- **L0 entry**: `CLAUDE.md` (sized to the ~800-token L0 budget; see `.claude/rules/L0-budget.md`)
- **Top-level docs**: `README.md`, `AGENTS.md`
- **Research-only docs** (if `is_research=true`): `REFERENCES.md`, `EXPERIMENT-PROTOCOL.md`, `EXPERIMENTS.md`, `FINDINGS.md`, `RESULTS.md`, `CHANGELOG.research.md`
- **`.claude/`**: 24 core skills, 6 agents, 7 hooks, 13 rule files, `settings.json` with the SessionStart hook wired
- **MCP**: `.mcp.json` registers CodeGraphContext, Semble, the Knowledge-Graph Memory MCP, and draw.io (diagram editor)
- **Config**: `.gitignore`, `.editorconfig`, `pyproject.toml`, `.copier-answers.yml`
- **Seed working directories**: `archive/`, `config/`, `files_from_team/`, `internal_docs/`, `meeting_notes/`, `presentations/`, `results/`, `scripts/`, `submission_artifacts/`, `submission_docs/` (each with `.gitkeep`)
- **First commit**: "Initial commit from loam"

## Pull future template updates into an existing project

```bash
cd ./my-project
uvx copier update --trust
```

Copier renders the latest template against the recorded answers, diffs against the current project state, and offers a three-way merge for conflicts. Local edits that don't conflict are preserved. The `.copier-answers.yml` is updated to record the new ref.

> **v2.0 projects:** `copier update` will not work across the v2.0 → v3.0 boundary. Re-bootstrap instead — see `docs/MIGRATION-v3.md`.

## What gets excluded from the rendered project

The exclusion list lives in `copier.yml` (`_exclude:`). Reasons content does not propagate, grouped:

- **Framework machinery** — `bin/`, `docs/`, `copier.yml`, `VERSION`, `LICENSE`. These run the template, not the rendered project.
- **Template-author working files** — root `CLAUDE.md`, `README.md`, `.gitignore`, `.claudeignore`, `template-manifest.schema.json`, `.github/`. The Jinja-suffixed versions of CLAUDE.md/README.md ship instead.
- **Internal references** — `IMG_*`. Reference material the template author studies; not part of what every project inherits.
- **Marketplace candidates** — `cultivation/marketplace/` (skills cut from default core). Available for reference; install via plugin marketplace post-bootstrap if needed.
- **Local-only Claude Code state** — `.claude/audit.log`, `.claude/.local-paths`, `.claude/settings.local.json`, `.claude/worktrees/`.

## Verifying the template

Before any PR that touches `.claude/`, `seed/_research/`, `bin/`, `copier.yml`, or top-level `.jinja` files:

```bash
bin/verify-template.sh
```

Asserts: single-tree invariant (no `template/` subdir), valid JSON in `settings.json`, agentskills.io schema for every `SKILL.md` (name + description present in front-matter), Copier render produces a valid project in both `default` and `is_research=true` variants, no template-author files leak. Exits non-zero on any violation.

## Post-release smoke test

After tagging and pushing a new release, verify the full Copier flow produces a working project:

```bash
tmpdir=$(mktemp -d)
uvx copier copy --trust \
  -d project_name=smoke-test \
  -d is_research=false \
  -d github_repo="" \
  gh:samyakjhaveri/loam "$tmpdir/smoke-test"

cd "$tmpdir/smoke-test"

# Core assertions
ls .claude/skills/diagrams/SKILL.md && echo "OK: diagrams skill present" || echo "FAIL: diagrams missing"
python3 -c "import json; d=json.load(open('.mcp.json')); assert 'drawio' in d['mcpServers']; print('OK: drawio MCP wired')"
python3 -c "import json; d=json.load(open('.mcp.json')); assert 'codegraphcontext' in d['mcpServers']; print('OK: CGC MCP wired')"
ls .claude/settings.json && echo "OK: settings.json present" || echo "FAIL: settings missing"
test -d .git && echo "OK: git initialized" || echo "FAIL: git not initialized"

# Clean up
cd - && rm -r "$tmpdir"
```

> **Common failure:** If assertions fail but `copier copy` reported a valid version, check that the git tag points to HEAD — Copier resolves the latest tag, not the latest commit. See `.claude/rules/known-issues.md` for details.

## After bootstrap — first session

1. Open the project in Claude Code. The `SessionStart` hook fires and injects the framework brief (24 core skills, Pipeline Gate ordering, four ICM routing layers).
2. Replace placeholder content in `CLAUDE.md` with project specifics. Stay within ~800 tokens (`.claude/rules/L0-budget.md`).
3. Run `cgc index .` after the first non-trivial commit to build the code graph index.
