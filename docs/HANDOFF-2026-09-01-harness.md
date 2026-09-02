# Handoff: Loam harness quality, next session

> Written 2026-09-01 by the harness-quality session. For a fresh session with no context.
> Everything below is either shipped (v2.1.0) or a clearly-scoped next task.

## What shipped this session (v2.1.0, on main)

1. Closed a force-push bypass class in `seed/.codex/hooks/pre-tool-policy.py`.
   Indirect forms (`$(...)`, `$VAR`, `${VAR}`, path-prefixed git, `sh -c`/`eval`,
   `command`/`env` wrappers) that executed a push while the policy said "allow"
   now deny. Deep nesting fails closed. The test that blessed them was flipped.
2. Removed `Bash(sed:*)` from the seed allowlist (`sed -i` bypassed edit hooks).
3. Replaced the fake `auto-activate` field with `disable-model-invocation` and
   added a verify-template stage-6 check so it cannot return.
4. Fixed the stop gate's silent ruff skip on uv/brew installs.
5. Guarded `vet-skill.sh --out` against wiping a non-empty directory.
6. Built the rig: `bin/harness-smoke.sh` (render + contract + Score B, plus a
   `--live` hook-dispatch proof) and `bin/skill_listing_weight.py`, wired as
   verify-template stage 8 (a no-growth ratchet at 2800 tokens).

## Onboarding guides (visual, for a new teammate)

Two independent web guides explain the repo layout, how you use Loam, and what
fires during a session. Same three diagrams, two separate readings.

1. Claude's field guide (green): https://claude.ai/code/artifact/58db0156-3ac1-4917-a334-d47a855ce009
2. Codex's field guide (blue blueprint): https://claude.ai/code/artifact/d7e60e60-1e61-41d5-bbaa-e3e8a9e35a3d

Source files live in the session scratchpad (`loam-field-guide.html` and
`loam-codex-guide.html`). They are artifacts, not committed to the repo. Re-open
from the Claude Code terminal with `/artifacts`, or the two URLs above.

## Key measured findings

1. Seed skill-listing weight is 101 tokens (lean). The sam-cc-setup plugin
   listing is 2,695 tokens (1.35% of a 200k window). Research target is ~1%.
2. Routing eval (7 probes, Opus 4.8 workers, Fable judge): 7/7 correct. The old
   E5 precision misses did NOT reproduce. So consolidating skills is not urgent.
   Residual ambiguity is only in the review family and survives on NOT-clauses
   and manual-only markers. Keep those verbatim. Do not add a fifth review skill.

## Open tasks, in priority order

### 1. Deferred: seed-to-project sync repair
Samyak deferred this in the 2026-09-01 session to focus on harness quality.
- distbench is pinned to `v3.6.2`, a tag lineage that no longer exists (Loam
  tags are now v1.0.0..v2.1.0), so `copier update` cannot resolve a path.
  Decide: manual re-render, or a deliberate fork. distbench is dormant.
- No rendered project has a staleness signal. Candidate fix: a red flag in the
  `catchup` skill comparing `.copier-answers.yml` `_commit` against the template
  tags. (Harness-side, so it can be done without the full sync engine.)
- Two reframings worth weighing: R5 (move most of seed to the plugin so it gets
  in-place updates), R6 (use `vet-skill` as a two-way promotion valve). See the
  plan file's reframing-hunter section.

### 2. Routing quick win, pending a compatibility check
The research recommended setting `disable-model-invocation: true` on `ship`,
`auto-phase`, `critique-swarm`, `gen-spec` (side-effect skills that were E5
misses). This was REVERTED this session because the repo records that the field
also breaks the `/slash` command on some Claude Code versions (issues #26251,
#38969). Before applying: verify on the current Claude Code version whether the
field breaks manual `/ship` invocation. If it does not, apply it (saves ~500
listing tokens and blocks auto-fire). If it does, leave the descriptions as they
are (routing is already 7/7).

### 3. align-prompt auto-wiring (a standing request, still open)
Samyak asked twice (rebuild-session-brief.md:46, rebuild-ledger.md:15) to wire
`align-prompt` into a workflow or hook for automatic use. Never done. Decide the
trigger and wire it.

### 4. Opportunity wave (each item is user-gated)
- `/goal` adoption note in `seed/AGENTS.md.jinja` (the long-loop primitive; the
  repo has zero references to it today).
- A `SessionStart` hook with the `compact` matcher (the documented fix for
  post-compaction decay; E2 only tested the per-turn form, which is different).
- The research-lane marketplace bundle (ml-paper-writing, research-writing,
  rigor, experiment-loop) gated by `vet-skill`, plus a `project_kind` copier
  question and the five clean research doc templates in
  `cultivation/wip/research-assets/seed-docs/`.
- Soften `brainstorming`'s "You MUST use this before any creative work" line
  (the routing eval flagged it as the one description likely to cause a miss).

### 5. Recheck the +28.2 citation
`docs/specs/rebuild-research/clief-claims-verdicts.md` leans on a "+28.2 points,
~38k trajectories" figure (arXiv 2606.17819) that could not be reconfirmed from
the paper's abstract. Read the full PDF and confirm or correct it. This is
load-bearing for the D2 grow-skills decision.

## How to verify anything here

1. `bin/verify-template.sh` must print `verify-template: PASSED` (8 stages).
2. `bin/harness-smoke.sh` (fast lane) or `bin/harness-smoke.sh --live` (proves
   hooks dispatch in a real headless session).
3. Routing eval: `Workflow({scriptPath: "bin/harness-routing-eval.workflow.js"})`
   (needs explicit opt-in; Opus workers + Fable judge).

## Model and process rules for this repo

- Subagents: Opus 4.8 only. Rig workers at high/xhigh; Fable leads/advises.
- Codex second-opinion: cap at ~2 rounds; take realistic fixes, document niche
  residuals, move on.
- Seed behavior, hooks, copier.yml, releases: branch + PR. Docs: direct to main.
- `bin/verify-template.sh` green before every commit. Copier resolves tags, so
  tag a release or nothing ships.
