# Asset layers

Every Claude Code asset (agent / skill / hook / rule) belongs to exactly one of three layers. In v2.0, the layers are simpler than they were under the dual-tree (`.claude/` + `template/.claude/`) regime — there is no separate generic-core mirror; the template's own `.claude/` IS what ships.

| Layer | Where it lives in the template | Where it lives in a rendered project |
|-------|--------------------------------|--------------------------------------|
| `generic`         | `.claude/<relpath>` (template root) | `.claude/<relpath>` (always) |
| `flavor:research` | `_research/<relpath-stripped>`      | `.claude/<relpath>` (only if `is_research=true` at bootstrap) |
| `project-local`   | (does not exist in the template)    | `.claude/<relpath>` (added by the project, never promoted up) |
| `marketplace-candidate` | `seed-skills/<name>/`         | Not shipped — install post-bootstrap via plugin marketplace |

## How `template-sync` decides the layer

`template-sync` does not auto-decide. It always asks. The classification is your call. The skill provides a suggestion based on what the asset references:

- LaTeX, BibTeX, citation handling → `flavor:research`
- Experiments, hypotheses, ablations → `flavor:research`
- Training loops, model checkpoints, eval suites → `flavor:research`
- CUDA, OpenMP, MPI, kernel-level code → `flavor:research`
- References the project's own name from `.copier-answers.yml` → `project-local` (do not promote)
- Otherwise (general workflow, language-agnostic, applicable to non-research projects) → `generic`

## When to promote into `generic` vs `flavor:research`

Default to the flavor. The generic core stays lean precisely because flavors absorb domain-specific content. An asset belongs in `generic` only if every project — including a fresh greenfield SaaS that has nothing to do with research — would benefit.

Examples of correctly-`generic` assets in v2.0:

- Session bootstrap (`catchup`)
- Bug-fix workflow (`fix-bug`)
- Plan reviewer agent
- Validation Pipeline Gate (`validate`)
- Multi-reviewer code review (`multi-review`)
- Memory consolidation (`dream`)
- The four ICM routing rules (`L0-budget`, `context-md-anatomy`, `stage-contract`, `layer-triage`)
- The SessionStart hook
- The `know-me` skill (user-preference recall is universally useful)

Examples of correctly-`flavor:research` assets:

- Paper rebuttal pipeline
- Hypothesis tree
- CUDA / OpenMP translator
- Citation audit
- Experiment-config validation hook

Note on path-scoped rules: `python.md`, `tech-stack.md`, `architecture.md`, `frontend-design.md` all live in `generic` (`.claude/rules/`). They are path-scoped, so they only load when matching files are touched. A research project with no frontend code never pays the cost of `frontend-design.md`. Path-scoping is the cheaper alternative to a flavor.

## Project-local assets

Assets that only make sense for one project stay in that project's `.claude/` and are never promoted. The promote-time safety scan flags candidates containing the project name or absolute paths. If you intentionally want to promote a localized version (rare), generalize it first — replace local references with placeholders or environment variables.

## `seed-skills/` — marketplace-candidate layer

A new layer in v2.0. Fourteen skills were cut from the default `.claude/skills/` set during the v2.0 rework (audit traces: skill bloat, false-positive auto-activation, business-process focus, meta-meta function). They live in `seed-skills/` in the template repo for two reasons:

1. **Reference**: if a future project needs one, copy it back into `.claude/skills/` or install as a plugin.
2. **Future plugin marketplace**: Phase-4 of the rework wires `seed-skills/` as an installable plugin marketplace via `.claude-plugin/marketplace.json`. Projects then `/plugin install <name>` on demand rather than carrying every skill at bootstrap.

`seed-skills/` is in the Copier `_exclude` list — it does not ship to rendered projects.

## The `asset_overrides` field (legacy)

The legacy `template-manifest.json` had an `asset_overrides` map for marking an asset as `project-local` even when its filename matched a `generic` asset. Use under Copier: the equivalent is editing the asset locally in the project; `copier update` will show the diff on the next pull and you choose whether to accept the upstream version or keep yours.
