# HANDOFF — Usage Report Implementation

> Session: 2026-05-20. Author: Opus brainstorming + plan-review session.
> Next session: implement the plan at `docs/superpowers/plans/2026-05-20-usage-report-implementation.md`

---

## Goal

Implement recommendations from a Claude Code Insights report (529 messages, 54 sessions, 2026-05-07 to 2026-05-20) as routing-first artifacts in the Loam seed template. The report identified three friction categories — premature execution, over-engineering, and unsanctioned edits — and recommended guardrails, a pipeline orchestrator, and three ambitious automation patterns.

**What "routing-first" means:** Every new artifact orchestrates existing skills/agents rather than reimplementing behavior. Report prompts are used verbatim — they're battle-tested across 54 sessions.

## Current Progress

**Completed (this session — planning only, zero code changes):**

1. Read and analyzed the full usage report (`~/.claude/usage-data/report-2026-05-20-091052.html`)
2. Brainstormed design with user — 4 design decisions made (see Decisions below)
3. Wrote design spec: `docs/superpowers/specs/2026-05-20-usage-report-implementation-design.md`
4. Wrote implementation plan (v1): `docs/superpowers/plans/2026-05-20-usage-report-implementation.md`
5. Ran adversarial plan-reviewer agent — found **13 issues** (2 critical, 5 high, 4 medium, 2 low)
6. Rewrote the plan (v2) incorporating all 13 fixes
7. Verified critical findings against actual files (skill counts, pipeline ordering, verify-template.sh invariants)

**Not completed:**
- Zero code changes made. Working tree is clean on `main`.
- No branch created yet (plan instructs creating `rework/usage-report-implementation`).

## What Worked

- **Plan-reviewer agent caught 2 critical issues** the original plan missed:
  1. Pipeline ordering contradiction — 3 always-loaded files would have contradicted the new guardrails
  2. `verify-template.sh` would have failed because it enforces skill count in `session-start.sh` matching actual directories
- **Asking user design decisions before writing the plan** — prevented the ordering contradiction from being baked in
- **Auditing actual `auto-activate` status** — revealed the known-issues.md tiering list was already inaccurate (5 skills listed as "core" actually have `auto-activate: false`)

## What Didn't Work (Do NOT Re-propose)

| Item | Why Cut/Changed |
|------|-----------------|
| Per-task commits (7 separate commits) | Pre-commit gate blocks commits without `.validation_passed`. Changed to single commit at end. |
| Settings.json protection hook (PreToolUse block) | User changes settings often mid-session. Changed to behavioral rule in guardrails instead. |
| Guardrail #5 (skill placement) as a standalone concern | Template-author-specific, ships to all projects where it's meaningless. Kept per user preference but noted as cross-ref. |
| Creating a new always-loaded file for guardrails | User chose to keep all 5 guardrails with cross-refs to workflow.md, despite partial duplication. Intentional reinforcement. |

## Decisions (Already Made by User)

1. **Approach**: Routing-first (Approach A) — orchestrate existing skills, no reimplementation
2. **Pipeline ordering**: Replace old ordering (`/multi-review → /validate → commit → push`) with new `/ship` ordering (`/session-critique → /validate → /commit → /pr`) across ALL sources of truth
3. **Commit strategy**: Single commit at end after `/validate`, on a rework branch
4. **Guardrails scope**: Keep all 5 guardrails with cross-references, despite partial overlap with workflow.md
5. **Tier 3 skills**: All three (critique-swarm, render-gate, auto-phase) included in spec, each as `auto-activate: false`
6. **Settings protection**: Behavioral rule only (guardrail #4), no hook enforcement

---

## Next Steps — Implementation

### How to Start

```bash
cd /Users/samyakjhaveri/Desktop/loam
```

Then invoke the plan using one of these approaches:

**Option A (recommended):** Paste this into Claude Code:
```
Read the implementation plan at docs/superpowers/plans/2026-05-20-usage-report-implementation.md and execute it task-by-task using superpowers:subagent-driven-development. The plan has 10 tasks (Task 0-9). All design decisions are already made — do not re-ask. Use /validate before the final commit. Run bin/verify-template.sh as the definitive verification gate.
```

**Option B:** Paste this for inline execution:
```
Read the implementation plan at docs/superpowers/plans/2026-05-20-usage-report-implementation.md and execute it task-by-task using superpowers:executing-plans. Start at Task 0 (branch setup). All design decisions are already made — do not re-ask.
```

### What the Plan Creates (10 tasks)

| Task | What | Key Files |
|------|------|-----------|
| 0 | Branch setup | `git checkout -b rework/usage-report-implementation` |
| 1 | Session guardrails rule | CREATE `seed/.claude/rules/session-guardrails.md` |
| 2 | `/ship` orchestrator skill | CREATE `seed/.claude/skills/ship/SKILL.md` |
| 3 | `/critique-swarm` skill | CREATE `seed/.claude/skills/critique-swarm/SKILL.md` |
| 4 | `/render-gate` skill | CREATE `seed/.claude/skills/render-gate/SKILL.md` |
| 5 | `/auto-phase` skill | CREATE `seed/.claude/skills/auto-phase/SKILL.md` |
| 6 | Pipeline ordering (4 files) | MODIFY `workflow.md:74`, `session-start.sh:26`, `CLAUDE.md.jinja`, `CLAUDE.md` |
| 7 | Skill count + tiering (3 files) | MODIFY `session-start.sh:16-22`, `known-issues.md:8-10`, `CLAUDE.md.jinja:54` |
| 8 | Guardrails pointer | MODIFY `seed/CLAUDE.md.jinja` Reference Docs table |
| 9 | E2E verification + commit + PR | `/validate`, `bin/verify-template.sh`, single commit, PR |

### Critical Verification Points

The plan has built-in verification at each task, but these are the make-or-break gates:

1. **Task 7 Step 4**: `session-start.sh` skill count must match actual directories (21). If mismatched, `bin/verify-template.sh` FAILS.
2. **Task 9 Step 3**: Pipeline ordering must be consistent across all 4 files. If contradictory, fresh sessions get confused.
3. **Task 9 Step 6**: `bin/verify-template.sh` is the definitive gate. It checks skill count, YAML frontmatter, JSON validity, and Copier rendering. Must show `ALL OK`.

### Actual Skill Counts (verified this session)

| Metric | Value |
|--------|-------|
| Current skill directories | 17 |
| After plan executes | 21 (17 + ship + critique-swarm + render-gate + auto-phase) |
| Core (auto-activate default/true) | 13 (agent-team, catchup, commit, feature-dev, fix-bug, gen-spec, handoff, multi-review, pr, scaffold-context, session-critique, ship, validate) |
| Specialized (auto-activate false) | 8 (auto-phase, create-skill, critique-swarm, dream, render-gate, researcher, techdebt, template-sync) |

### Files the Plan Does NOT Touch

These exist but are intentionally left alone:
- `HANDOFF.md` (root) — belongs to a different task (code review cleanup)
- `seed/.claude/settings.json` — user changes settings mid-session; no hook enforcement
- `seed/.claude/skills/multi-review/` — `/multi-review` remains as an optional complement to `/session-critique`

---

## Adversarial Review Summary

The plan-reviewer found 13 issues. All were fixed in plan v2. Key fixes:

| # | Critical Issue | How Fixed |
|---|---------------|-----------|
| 1 | Pipeline ordering contradicts across 3 files | Added Task 6 (update all 4 sources of truth) |
| 2 | verify-template.sh guaranteed failure (skill count) | Added to Task 7 (update session-start.sh count 17→21) |
| 7 | Per-task commits blocked by pre-commit gate | Changed to single commit at end after /validate |
| 13 | Plan commits directly to main (violates convention) | Added Task 0 (branch creation) |

Full issue table is at the bottom of the plan file.

## Blockers

None. All design decisions resolved. Working tree is clean on `main`. The plan is execution-ready.

---

## Reference Files

| File | Purpose |
|------|---------|
| `docs/superpowers/specs/2026-05-20-usage-report-implementation-design.md` | Design spec (the "what and why") |
| `docs/superpowers/plans/2026-05-20-usage-report-implementation.md` | Implementation plan (the "how", task-by-task) |
| `~/.claude/usage-data/report-2026-05-20-091052.html` | Original usage report (source of all recommendations) |
| `HANDOFF.md` | UNRELATED — belongs to a code review cleanup task, do not modify |
