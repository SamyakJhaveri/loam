# sam-cc-setup

The portable core of Sam's Claude Code setup.
Cut to three skills in v3.0.0 under design law 7: the burden of proof is on keeping, and everything with zero recorded use is parked, not shipped.
Since v3.0.0 it has gained the `brief` skill and the factory grader agents `judge` and `reviewer`.

**Audience:** repositories that want optional planning-review and cross-model review skills.
This includes projects rendered by [Loam](https://github.com/SamyakJhaveri/loam).

## What the plugin exposes after installation

- **Skills (7), all manual-only, so type `/<name>`:** `brief` (turns a raw request into a factory brief and ticket), `codex-review` (read-only cross-model second opinion on a diff; requires the Codex CLI), `factory-watch` (one read of `bin/factory status` per call, reporting stopped runs, opened PRs and failing preconditions; for a loop, type the plain prompt the skill's description gives, since a `/loop` fire cannot run a manual-only skill), `plan-review` (blind merged plan review: correctness checklist plus elegance gate in one unit), `research-gap` (research questions and literature gap checks ending in one cheap validation, with a reading log whose quotes are checked against the PDFs; its scripts need Python 3 and poppler's `pdftotext`), `run-spec` (a spec's ticket graph as one branch and PR, parallel workers in worktrees), `surprise-me` (ranked, evidence-backed unsolicited ideas).
- **Agents (4):** `plan-reviewer`, used by `plan-review`; `lean-critic`, a read-only Opus 5.5 critic that cuts verbosity from code and prose another model wrote; `judge` and `reviewer`, the fresh-context graders the Loam factory runs on each ticket (`docs/factory/LOOP.md`).
- Regenerate both counts with `find cultivation/marketplace/sam-cc-setup -name SKILL.md | wc -l` and `ls cultivation/marketplace/sam-cc-setup/agents`.
- **Hooks:** none. The plugin installs no hook on any tool matcher (design law 3).
- **Workflows:** none.

Everything else that used to ship here now sits unmodified in `cultivation/parked/sam-cc-setup/`, preserving its subpaths: 23 skills, 5 agents, the `hooks/` directory (`protect-paths`, `check_stale_counts`, `generated-file-guard`, `concurrent-checkout-guard`, `codex-review-reminder`, `pre-commit`, and their control suites), the `plan-review-fanout` workflow, and `THIRD_PARTY_LICENSES/`.
Parked assets are kept for reference and can be promoted again when a real project uses one.

## What it cannot ship

Plugins cannot inject always-loaded context (`CLAUDE.md`, `.claude/rules/*.md`).
A Loam-rendered project already carries that layer.
The `bootstrap-cc-setup` skill that wrote it for non-Loam repos is parked.

## Versioning

Semver in `.claude-plugin/plugin.json`, kept equal to the `sam-cc-setup` entry in `cultivation/marketplace/.claude-plugin/marketplace.json`.
Bump both by hand when plugin content changes, and record the change in `cultivation/marketplace/UPGRADING.md`.
`bin/release.sh` writes only the top-level `VERSION` (the Copier template version) and never touches either plugin version field.
