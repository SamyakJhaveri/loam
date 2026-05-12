# Asset layers

Every Claude Code asset (agent / skill / hook / rule) belongs to exactly one of three layers.

| Layer | Where it lives in the template | Where it lives in a project |
|-------|--------------------------------|-----------------------------|
| `generic`           | `.claude/`                          | `.claude/` (always present) |
| `flavor:<name>`     | `flavors/<name>/`                   | `.claude/` (only if that flavor was applied) |
| `project-local`     | (does not exist in template)        | `.claude/` (added by the project, never promoted up) |

## How `template-sync` decides the layer

`template-sync` does NOT auto-decide. It always asks. The classification is your call.

But the skill suggests a layer based on what the asset references:

- Mentions `--api`, `requests.post`, web frameworks → likely `generic` or `software-eng`
- Mentions LaTeX, `bibtex`, citations → likely `flavor:research`
- Mentions experiments, hypothesis, ablation → likely `flavor:research`
- Mentions training loops, eval, model checkpoints → likely `flavor:research`
- Mentions CUDA, OpenMP, MPI, kernel → likely `flavor:research`
- References the project name from `template-manifest.json` → likely `project-local` (don't promote)

## When to promote into `generic` vs a flavor

Default to a flavor. The generic core should stay lean. An asset belongs in `generic` only if **every** project, regardless of domain, would benefit from it.

Examples of correctly-`generic` assets:

- Session bootstrap (`catchup`)
- Bug-fix workflow (`fix-bug`)
- Plan reviewer (adversarial review of plans)
- Validation loop (`validate`)
- Code review (`review`)
- Memory consolidation (`dream`)

Examples of correctly-flavor assets:

- Paper rebuttal pipeline → `research` (most projects don't write papers)
- Hypothesis tree → `research` (most projects don't track hypotheses)
- CUDA/OpenMP translator → `research` (HPC work is research in this context)
- Python style rules (`python.md`, `tech-stack.md`) → both flavors (research + software-eng)
- Architecture/frontend rules → `software-eng` (formal architecture is a product concern)

## Project-local assets

Assets that only make sense for one project should stay in that project's `.claude/` and never be promoted.

The skill's safety scan flags promotion candidates that contain the project name or other obvious local references. If you intentionally want to promote a localized version (rare), generalize it first — replace local references with placeholders or environment variables.

## The `asset_overrides` field

`template-manifest.json` has an `asset_overrides` map for cases where you want to mark an asset as `project-local` even though its filename matches a `generic` or flavor asset. This is rare; use it when you've heavily customized a generic skill for project-specific workflows and don't want `template-sync sync-from-buffer` to overwrite it.
