# HANDOFF — Distbench Bootstrap (Revised)

> Working state for the next session. Last updated: 2026-05-18T~23:00Z
> **Start here.** Read this entire document, then execute the plan phase-by-phase.

## Goal

Bootstrap a new distributed systems benchmarking project ("distbench") from the Loam Copier template. Four sequential phases: commit pending fixes, rename framework to "Loam", port skills from parbench, render distbench.

## Current Progress

- [x] Original plan authored (`docs/multi_session_prompts/2026-05-18-distbench-bootstrap.md`)
- [x] Plan adversarially reviewed (plan-reviewer agent found 14 issues: 1 critical, 4 high, 4 medium)
- [x] All issues addressed in revised plan (see below)
- [x] User decisions locked in (rename=Loam, single commit, port+merge, is_research=true)
- [x] Parbench skill catalog verified against actual filesystem (all claimed files exist)
- [x] Framework state verified (19 core skills, 13 research skills, 7 agents)
- [x] Research skill overlap identified (10 of 15 "port" targets already exist — must compare, not overwrite)
- [ ] **Phase 1: Pre-flight commit** — NOT STARTED
- [ ] **Phase 2: Rename to Loam** — NOT STARTED
- [ ] **Phase 3: Port + merge parbench skills** — NOT STARTED
- [ ] **Phase 4: Render distbench** — NOT STARTED

## The Revised Plan

**Location:** `.claude/plans/read-the-plan-at-crystalline-waffle.md` (full step-by-step with exact file paths, commands, and verification)

**Also read the original plan for context:** `docs/multi_session_prompts/2026-05-18-distbench-bootstrap.md`

### Phase summary with time estimates

| # | Phase | ~Time | Key constraint |
|---|-------|-------|----------------|
| 1 | Pre-flight: commit 9 pending files | 15 min | Single bundled commit; do NOT edit files between /validate and git commit |
| 2 | Rename framework to Loam (14 files) | 30 min | Rename local dir + GitHub repo OUTSIDE Claude Code |
| 3 | Port + merge skills from parbench | 90-120 min | Run /compact between CORE and RESEARCH batches |
| 4 | Render distbench + bootstrap | 60 min | MUST include `--vcs-ref HEAD` in Copier command |

### Critical bugs fixed from original plan

1. **`--vcs-ref HEAD` missing from Phase 4 Copier command** — without it, rendered distbench silently drops files like `session-start.sh`. The revised plan includes it.
2. **4 sequential commits fought the sentinel-cleanup hook** — `sentinel-cleanup.sh` (PostToolUse on Edit/Write) deletes `.validation_passed` after any file change. Revised to single bundled commit.
3. **`git add --patch` is interactive and fragile in Claude Code** — eliminated by using single commit.
4. **`mv` of working directory crashes Claude Code** — revised plan does `mv` and `gh repo rename` outside Claude Code session.
5. **Plan claimed `waves_passed` is fail-closed but code is fail-open** — corrected: `pre-commit-gate.sh:93-95` is explicitly fail-open for backward compat. Tracked as tech debt, not a blocker.
6. **Research skill overlap not detected** — 10 of 15 research skills already exist in `_research/skills/`. Revised plan separates NEW (copy) from MERGE (compare-and-merge) items.

## What Worked (from the review session)

- Three parallel agents (Explore parbench, Explore framework, plan-reviewer) provided comprehensive coverage in one pass
- Cross-referencing parbench's actual filesystem against the plan's classification tables caught the research overlap problem
- Reading `pre-commit-gate.sh` directly disproved the plan's claim about fail-closed behavior

## What Didn't Work / Traps to Avoid

- **The original plan's skill count math was wrong** — it counted agents and rules as skills. Actual core skill increase is 19→~25 (+6 new skill dirs), not 19→31.
- **`sentinel-cleanup.sh` is invisible but powerful** — it fires on EVERY Edit/Write PostToolUse. Any file edit between `/validate` pass and `git commit` invalidates the sentinel. Never edit files in that window.
- **Don't rename the working directory while Claude Code is running** — shell CWD becomes invalid. Do it in a separate terminal, then open a fresh session.
- **Don't blindly copy research skills** — most already exist in the framework. Always diff before copying.

## Next Steps (for the executing session)

1. Read the full revised plan at `.claude/plans/read-the-plan-at-crystalline-waffle.md`
2. Also read these framework rules (required pre-reading):
   - `.claude/rules/workflow.md` — 6-stage workflow, anti-patterns
   - `.claude/rules/stage-contract.md` — L2 contract format
   - `.claude/rules/layer-triage.md` — 60/30/10 framework
   - `.claude/rules/validation-loop.md` — 3-wave Pipeline Gate
3. Execute Phase 1 (pre-flight commit)
4. `/clear` between each phase
5. Execute Phases 2-4 in order
6. Don't push to remote until Phase 4 succeeds

## Hot Files

**Phase 1 (commit these):**
- `.claude/agents/self-critic.md` — modified
- `.claude/agents/verification-lead.md` — modified
- `.claude/hooks/pre-commit-gate.sh` — modified (waves_passed check)
- `.claude/rules/validation-loop.md` — modified (3-wave structure)
- `.claude/skills/validate/SKILL.md` — modified
- `.github/workflows/test.yml` — modified (dead shellcheck globs)
- `CLAUDE.md.jinja` — modified (template-sync experimental)
- `CONTEXT.md.jinja` — modified (L1 skeleton rewrite)
- `PROJECT-BACKGROUND.md.jinja` — NEW (prose split from CONTEXT.md)
- `bin/verify-template.sh` — modified (CONTEXT.md checks, template-sync WARN)
- `.write-probe`, `.claude/.write-probe` — DELETE (sandbox artifacts)

**Phase 2 (rename in these 14 files):**
See the revised plan for the exact file+line table.

**Phase 3 (read from parbench, write to framework):**
- Source: `~/Desktop/parbench_sam/.claude/` (READ-ONLY)
- Target: `.claude/skills/`, `.claude/agents/`, `.claude/rules/`, `_research/skills/`, `_research/agents/`

**Phase 4 (render + bootstrap):**
- `copier.yml` — template config
- `bin/verify-template.sh:106` — reference for `--vcs-ref HEAD` flag
- Output: `~/Desktop/distbench/`

## Blockers

None. All decisions are locked in. All source files verified to exist.

## Open Tech Debt (document, don't fix now)

- `pre-commit-gate.sh:93-95` — `waves_passed` check is fail-open. If sentinel lacks the field, gate allows commit. Backward-compat by design, but should eventually be fail-closed.
