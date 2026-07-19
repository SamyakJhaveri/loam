# template-sync-promote-generic-user

> Spec derived from the mechanism spike (Part 0.5 of the Phase-1 campaign).
> Evidence: `~/.claude/plans/2026-07-19-mechanism-spike-findings.md` §1 (Probe 1, "PARTIAL"), §5 Item 0.
> Generated via `/gen-spec`, 2026-07-19. **Status: ready (grilled 2026-07-19; Part B deferred to the ADR).**
> **Partially gated:** the architecture-independent skill/doc fixes are decided and safe now; the PR-target retargeting is DEFERRED to Part 2 (`three-tier-divergence-decision.md`).

## Identity

- **Name:** template-sync-promote-generic-user
- **Owner:** Sam
- **Status:** ready — Part A (grilled 2026-07-19); Part B deferred to the ADR (`three-tier-divergence-decision.md`)
- **Scope:** Make the documented `template-sync` **promote** (upward contribute-back) path (a) consistent between the skill and the script, and (b) usable by a non-Sam user — for the parts that do **not** depend on the fork-vs-data decision. The PR-target hardcode is explicitly deferred.
- **Related:** blocks/blocked-by `three-tier-divergence-decision.md` (the deferred half); assertion #2 of `mechanism-spike-regression-test.md` guards this behavior.

## Inputs (all Verified in the spike, findings §1)

- `seed/.claude/skills/template-sync/SKILL.md` — `:3` description "Refuses to operate without template-manifest.json"; `:25` pre-flight demands `template-manifest.json` and cites `init-project.sh`; `:26` defaults the template path to `~/Desktop/project_template`.
- `bin/template-sync.sh` — `:31-34` `require_manifest()` accepts **either** `template-manifest.json` **or** `.copier-answers.yml`; `:40-48` prefers the copier answers' `_src_path`; `:54` default `~/Desktop/loam`; `:292-296` PR repo = manifest's `template.repo`, **else hardcoded `samyakjhaveri/loam`**.
- `docs/COPIER.md:3`, `docs/BOOTSTRAP.md:3` — `init-project.sh` (the manifest's only creator) was **removed in v2.0**; a repo-wide grep finds **no writer** of `template-manifest.json`, only readers.
- A copier-bootstrapped project has `.copier-answers.yml` and **no** `bin/` (only `seed/` renders), so the promote script is not shipped into projects.
- **Baseline truth:** zero promote commits have ever existed (`docs/SYNC.md:93`; `git log --all | grep promote(` empty). The spike was the first end-to-end run.

## Behavior

### Part A — architecture-independent fixes (DECIDED; implement now)

1. **Align the skill's pre-flight with the working script.** In `SKILL.md`:
   - Accept **either** `template-manifest.json` **or** `.copier-answers.yml` as the precondition (mirror `require_manifest()`), instead of refusing without the manifest.
   - Remove the dead `init-project.sh` sentence (`:25`).
   - Correct the template-path resolution text (`:26`) to match the script: prefer `$TEMPLATE_PATH`, then `.copier-answers.yml` `_src_path`, then `~/Desktop/loam` — delete `~/Desktop/project_template`.
2. **Fix the skill `description` frontmatter** so it no longer claims "Refuses to operate without template-manifest.json" (which contradicts the script and would refuse every copier-bootstrapped project).
3. **Document how a project without a shipped script runs promote.** Since projects get no `bin/`, add a short note (in `SKILL.md` and/or `docs/SYNC.md`): run `bin/template-sync.sh` from a local `loam` clone with the project as CWD. (Shipping a `bin/` shim into projects is a larger change tied to Part 2 — do not do it here.)

### Part B — DEFERRED to Part 2 (do NOT implement until the fork-vs-data decision)

- `bin/template-sync.sh:295` hardcodes the PR target to `samyakjhaveri/loam` when no manifest exists. For a **forked** personal Loam, promote must target the fork's own canonical, not Sam's repo. How to derive the target (from the `github_repo` answer? from the template clone's `origin` URL? from a new persisted answer?) depends on whether the personal tier is fork-based — which is exactly the Part 2 decision (`three-tier-divergence-decision.md`, Agenda Item 0/1/2). Cross-reference it; do not guess a mechanism now.

## Outputs

- **Modified (Part A):** `seed/.claude/skills/template-sync/SKILL.md` (pre-flight + description frontmatter); optionally `docs/SYNC.md` (the "run from a clone" note).
- **Explicitly NOT modified now:** `bin/template-sync.sh:295` (Part B, deferred).

## Constraints (must NOT)

- MUST NOT change `bin/template-sync.sh:295` PR-target logic until Part 2 decides the divergence model — that change's correct shape is unknown until then.
- MUST NOT reintroduce a `template-manifest.json` requirement anywhere — `init-project.sh` is gone; `.copier-answers.yml` is the project metadata.
- MUST NOT make promote auto-run, hook-triggered, or a side effect of any other skill — the skill's "no auto-promotion, no file watchers" invariant (SKILL.md:11, :112-115) stays intact.
- MUST NOT break Sam's currently-working path (running `bin/template-sync.sh promote` from a local `loam` clone).
- MUST NOT weaken the promote generality/secret scan (SKILL.md step 3).

## Acceptance Criteria

1. A copier-bootstrapped project (only `.copier-answers.yml`, no manifest) satisfies the SKILL.md documented pre-flight — the text names `.copier-answers.yml` as a sufficient precondition and contains no "skill cannot operate" refusal path for that case.
2. `grep -n 'init-project.sh' seed/.claude/skills/template-sync/SKILL.md` → no match.
3. `grep -n 'project_template' seed/.claude/skills/template-sync/SKILL.md` → no match.
4. The SKILL.md `description:` frontmatter no longer contains "Refuses to operate without template-manifest.json."
5. `SKILL.md` (or `docs/SYNC.md`) states how to run promote from a project that has no `bin/` (run the script from a local clone).
6. `bin/verify-template.sh` → `ALL OK` (both flavors).
7. **Deferred item is provably untouched:** `git diff` shows no change to `bin/template-sync.sh`, and the spec cross-references `three-tier-divergence-decision.md` for the PR-target work.
