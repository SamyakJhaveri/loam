# Usage Report Implementation — Design Spec

**Date:** 2026-05-20
**Source:** Claude Code Insights report (529 messages, 54 sessions, 2026-05-07 to 2026-05-20)
**Goal:** Implement the report's recommendations as routing-first artifacts in the Loam seed template, organized in three tiers.

## Context

The usage report identified three categories of friction:
1. **Premature execution** — Claude commits/pushes before running requested critiques
2. **Over-engineering** — Inflated solutions with extra deliverables and verbose preambles
3. **Unsanctioned edits** — Settings.json reverts and dropped content during ports

The report also identified the user's strongest pattern: a disciplined **execute → critique → validate → commit → PR** pipeline that, when followed, produces clean results. The friction occurs when the ordering slips.

**Design principle:** Route to existing skills and agents. Use report prompts verbatim. No reimplementation of existing behavior.

---

## Phase 1: Session Guardrails (Tier 1)

### Artifact: `seed/.claude/rules/session-guardrails.md`

Always-loaded rules file. Five behavioral constraints derived from the report's CLAUDE.md suggestions.

| # | Guardrail | Addresses |
|---|-----------|-----------|
| 1 | **Workflow ordering** — Run session-critique BEFORE commit/push. Never commit until critique + validation pass. | Premature execution friction |
| 2 | **Plan vs Execute** — When asked for a plan or handoff, do NOT begin executing or creating task lists until the user explicitly approves. | Premature execution friction |
| 3 | **Avoid over-engineering** — Prefer the simplest solution. No extra deliverables, subcommands, or verbose preambles unless asked. Ask before expanding scope. | Over-engineering friction |
| 4 | **Settings protection** — Never modify or revert settings.json beyond what a plan explicitly specifies. Never re-apply changes without asking. | Unsanctioned edits friction |
| 5 | **Skill placement** — Workflow skills go in the git repo (not user-level). Default to generic-core rather than duplicating across flavors. | Skill placement confusion |

**Applies to:**
- Loam itself (via `.claude → seed/.claude` symlink)
- All bootstrapped projects (shipped through Copier)

**Verification:** After creating, confirm the file loads by running a test session and checking that the guardrails are visible in the system prompt context.

---

## Phase 2: The `/ship` Orchestrator (Tier 2)

### Artifact: `seed/.claude/skills/ship/SKILL.md`

A strict-ordering orchestrator that enforces the execute → critique → validate → commit → PR pipeline as a single command. Auto-activate: true (core workflow skill).

**Stages:**

1. **Session Critique** — Invoke `/session-critique`. Spawns adversarial subagents reviewing for regressions, over-engineering, dangling references, scope hygiene. Fix all HIGH/MEDIUM findings before proceeding.

2. **Validate** — Invoke `/validate` (full 3-wave, not quick). Must produce `.validation_passed` sentinel with `waves_passed=3`. On failure, enter fix loop per `validation-loop.md`.

3. **Commit** — Invoke `/commit`. Split by scope if multiple logical changes. Never bundle unrelated changes.

4. **PR** — Invoke `/pr`. Push and open GitHub PR with summary and test plan.

**Hard rules:**
- Never skip or reorder stages
- If stage 1 or 2 fails, do NOT proceed to stage 3
- Each stage uses the existing skill's full logic — no reimplementation
- User can pass `/ship` with no args (all 4 stages) or `/ship critique-only` (stage 1 only — runs session-critique without proceeding to validate/commit/PR, useful for mid-session quality checks)

**Verification:** Run `/ship` after a test implementation. Confirm stages execute in order, failures halt the pipeline, and the final PR is clean.

---

## Phase 3: Ambitious Patterns (Tier 3)

Three specialized skills (auto-activate: false — user-invoked). Each composes existing agents and uses report prompts verbatim.

### 3a. `/critique-swarm` — Parallel Adversarial Critique

**Artifact:** `seed/.claude/skills/critique-swarm/SKILL.md`

Launches 4 parallel Agent invocations + 1 synthesis agent.

**Agent mandates:**
1. Security and correctness regressions
2. Scope creep and over-engineering
3. Fidelity loss when porting/transplanting content
4. Missing tests or validation gaps

**Synthesis:** Reconcile all 4 reports into one ranked list, mark false positives with reasoning, recommend minimal fixes. Does not implement.

**Verbatim prompt from report:**
> "Review PLAN.md by spawning 4 parallel critique subagents, each with one mandate: (1) security and correctness regressions, (2) scope creep and over-engineering, (3) fidelity loss when porting/transplanting content, (4) missing tests or validation gaps. Run them concurrently, then synthesize their findings into one ranked list, mark any false positives with reasoning, and recommend the minimal set of fixes. Do not implement yet—just deliver the verdict."

**Relationship to `/multi-review`:** Complementary. `/multi-review` reviews code quality (style, correctness, security, performance). `/critique-swarm` reviews plan/scope quality. Use both.

### 3b. `/render-gate` — TDD Template Rendering Gates

**Artifact:** `seed/.claude/skills/render-gate/SKILL.md`

TDD loop for Copier template development:
1. Write E2E rendering assertions (or use existing `bin/verify-template.sh`)
2. Render every flavor into temp dir from committed git state
3. Run bootstrap, assert answers file, choices mappings, YAML scalars
4. Iteratively fix template until all tests pass
5. Never commit on a red suite

**Verbatim prompt from report:**
> "I'm editing a Copier template. First, write an E2E test suite that renders every flavor into a temp dir from committed git state, runs the bootstrap, and asserts the answers file, choices mappings, and YAML scalars are correct. Then iteratively fix the template until all tests pass—re-running the full suite after each edit and never committing on a red suite. Report each failure you hit and the fix you applied."

**Note:** Most useful in Loam itself. Ships in seed for template-of-template scenarios.

### 3c. `/auto-phase` — Autonomous Multi-Phase Release Loops

**Artifact:** `seed/.claude/skills/auto-phase/SKILL.md`

Reads PHASE-PLAN.md (stages 1-N). Executes autonomously per stage:
1. Implement the stage's changes
2. Run validation pipeline + session-critique subagent
3. Fix HIGH/MEDIUM findings
4. Commit with clean scope hygiene
5. Update TASKS.md with status, write next-stage context
6. Advance to next stage

**Stopping conditions:**
- Validation gate fails twice on same stage → halt, ask user
- Critique surfaces unresolvable issue → halt, ask user
- All stages complete → report summary

**Verbatim prompt from report:**
> "Read PHASE-PLAN.md which contains stages 1-N. Execute them autonomously one stage at a time: for each stage, implement the changes, run the validation pipeline and a session-critique subagent, fix any HIGH/MEDIUM findings, then commit with clean scope hygiene before advancing. After each stage, update TASKS.md with status and write the next-stage context inline. Only stop and ask me if a validation gate fails twice or a critique surfaces an issue you cannot resolve. Do not bundle unrelated changes into commits."

---

## Implementation Order

| Phase | Artifacts | Effort | Dependencies |
|-------|-----------|--------|--------------|
| 1 | `session-guardrails.md` | ~30 min | None |
| 2 | `ship/SKILL.md` | ~1 hr | Phase 1 (guardrails inform the skill's behavior) |
| 3a | `critique-swarm/SKILL.md` | ~45 min | None (independent of Phase 2) |
| 3b | `render-gate/SKILL.md` | ~45 min | None (independent) |
| 3c | `auto-phase/SKILL.md` | ~1 hr | Phase 2 (uses /ship pattern per stage) |

**Total:** ~4 hours estimated. Phases 3a-3c are independent of each other and can be parallelized.

## Verification Plan

After each phase:

1. **Phase 1:** Start a fresh session, confirm guardrails appear in loaded rules. Test by asking Claude to "commit this" without running critique — it should refuse per guardrail #1.
2. **Phase 2:** Run `/ship` after a test change. Confirm 4-stage ordering, failure halting, and clean PR output.
3. **Phase 3a:** Run `/critique-swarm` on a test plan. Confirm 4 parallel agents launch, synthesis produces ranked findings.
4. **Phase 3b:** Run `/render-gate` while editing a Copier template. Confirm TDD loop runs, red suite blocks commit.
5. **Phase 3c:** Create a 2-stage PHASE-PLAN.md, run `/auto-phase`. Confirm per-stage execution, halting on failure, TASKS.md updates.

## Files Modified/Created

| Action | Path |
|--------|------|
| CREATE | `seed/.claude/rules/session-guardrails.md` |
| CREATE | `seed/.claude/skills/ship/SKILL.md` |
| CREATE | `seed/.claude/skills/critique-swarm/SKILL.md` |
| CREATE | `seed/.claude/skills/render-gate/SKILL.md` |
| CREATE | `seed/.claude/skills/auto-phase/SKILL.md` |
| UPDATE | `seed/.claude/rules/known-issues.md` (add skill tiering entries for new skills) |
| UPDATE | `seed/CLAUDE.md.jinja` (add one-line pointer to session-guardrails.md in reference docs) |

No existing files are rewritten. No existing skill logic is duplicated.
