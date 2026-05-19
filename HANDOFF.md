# HANDOFF — Loam v3.0 Phase 1: Repository Restructure

> Last updated: 2026-05-19
> Status: **Phase 1 complete** — structural migration done, verified, ready for Phase 2

## Goal

Migrate Loam from `_subdirectory: "."` (27 `_exclude` patterns, leak-by-default) to `_subdirectory: "seed"` (safe-by-default — only `seed/` contents render). Phase 1 is structural only: move files, update scripts, verify renders. All 24 skills, 11 agents, and 12 hooks remain intact; only their file locations change.

Phase 2 (skill consolidation: 24 → 17) and Phase 3 (release + tag v3.0.0) are separate future sessions.

## Current Progress

- [x] Full spec written: `docs/superpowers/specs/2026-05-19-loam-v3-architecture-design.md`
- [x] Adversarial plan review (plan-reviewer agent): 17 issues found, all addressed
- [x] Copier `_subdirectory` research: symlink behavior, `_exclude` gotcha, `_tasks` interaction
- [x] Exhaustive path inventory: 28 critical breaking path references identified across all bin/ scripts and hooks
- [x] User design decisions captured (flatten soil/jvc/, plain mv, remove TEMPLATE-CLAUDE.md injection)
- [x] Final execution plan written with per-step verification
- [x] **Phase 1 execution** — completed 2026-05-19, verify-template.sh ALL OK, 3-wave validation PASS

## Execution Plan

The step-by-step plan with exact commands, file paths, and verification checks is in the plan file. **Read this first:**

**Plan file:** `.claude/plans/read-users-samyakjhaveri-desktop-loam-do-starry-piglet.md`

It contains 16 steps. The most critical are:
- **Step 3** (ATOMIC move+symlink): `mv .claude seed/.claude && ln -s seed/.claude .claude` — must be a single command
- **Step 9** (copier.yml): `_subdirectory: "seed"` + explicit `_exclude` (Copier clears defaults!)
- **Step 11** (verify-template.sh rewrite): ~15 line changes, detailed table in plan
- **Step 15** (verification): 9 checks (V1-V9) including Copier render tests

## What Worked (Planning Phase)

- **Parallel adversarial review**: Running plan-reviewer + Copier research + path inventory agents simultaneously caught 17 issues that the initial plan missed
- **Spec-first approach**: The detailed spec at `docs/superpowers/specs/2026-05-19-loam-v3-architecture-design.md` has everything — directory tree, file-by-file changes, verification commands, rollback strategy
- **Atomic move+symlink**: The plan-reviewer caught that `.claude/` disappearing (even briefly) between `mv` and `ln -s` would break all 9 registered hooks. The fix: combine both into one `&&`-chained command

## What Didn't Work / Gotchas Found

1. **Initial plan missed the TEMPLATE-CLAUDE.md injection block** in `session-start.sh` (lines 49-57). Deleting TEMPLATE-CLAUDE.md without removing its injection block causes a silent failure — the framework map stops appearing in sessions. Fixed: plan Step 10 removes the block entirely since Claude Code auto-loads root `CLAUDE.md`.

2. **Initial plan missed verify-template.sh render assertions** for deleted `.jinja` files. Lines 131-137 assert HANDOFF.md, CONTEXT.md, PROJECT-BACKGROUND.md render from `.jinja` templates — but those templates are deleted. Fixed: plan Step 11 table lists each line to remove.

3. **Copier clears default `_exclude` when `_subdirectory` is set**. The standard exclusions (`.DS_Store`, `*.pyc`, `__pycache__`, `.git`) are NOT applied automatically. Every exclusion must be explicit in `copier.yml`. This is documented in plan Step 9.

4. **Spec's V8 verification command was wrong**: `test -f "seed/$hook_path"` doesn't match `.claude/hooks/...` paths stored in settings.json. Fixed: plan Step 15 V8 uses a for-loop checking `.claude/hooks/$hook` (via symlink).

## Critical Research Findings

### Copier `_subdirectory` Behavior
- Symlink at repo root (`.claude -> seed/.claude`) is **invisible to Copier** — Copier only walks files inside `seed/`
- Files without `.jinja` suffix are copied **verbatim** (not processed through Jinja) — critical for `_copier_merge_hooks.py`
- `_tasks` run in the **rendered project directory**, not the template — all `_research/` paths in tasks work unchanged
- Recommended Copier version: **>= 9.14.1** (fixes symlink teleportation CVE)

### Symlink Strategy
All hooks in `settings.json` use paths like `.claude/hooks/pre-commit-gate.sh`. These resolve via the symlink `.claude -> seed/.claude`. This means:
- **Template repo**: works via symlink
- **Rendered projects**: `.claude/` is a real directory (Copier dereferences symlinks by default), works directly
- **If symlink breaks**: all 9 hooks fail. `bin/verify-template.sh` should check `test -L .claude`

### Files That DON'T Need Changes (verified)
The plan includes a "Files NOT Modified" table explaining why each untouched file is safe. Key: all hooks use `git rev-parse --show-toplevel` → repo root, then `.claude/...` via symlink. Self-relative hooks (`$HOOK_DIR/should-dream.sh`) are unaffected.

## Next Steps

1. **Start a fresh Claude Code session** in `~/Desktop/loam`
2. Load `/karpathy-guidelines` skill (behavioral guard)
3. Read the plan file: `.claude/plans/read-users-samyakjhaveri-desktop-loam-do-starry-piglet.md`
4. Execute Steps 1-16 sequentially, verifying after each step
5. If `bin/verify-template.sh` fails after 3 fix attempts → re-read the spec and re-plan (stop condition from spec §8)
6. After Phase 1 commit succeeds → Phase 2 can begin (skill consolidation, separate session)

## Key File References

| File | Purpose |
|------|---------|
| `docs/superpowers/specs/2026-05-19-loam-v3-architecture-design.md` | Full v3.0 spec (Phases 1-3) |
| `.claude/plans/read-users-samyakjhaveri-desktop-loam-do-starry-piglet.md` | Phase 1 execution plan (16 steps) |
| `copier.yml` | Core config: `_subdirectory`, `_exclude`, `_tasks` |
| `bin/verify-template.sh` | Main verification script (needs rewrite) |
| `bin/template-sync.sh` | Sync script (needs path updates) |
| `bin/lint-skill-descriptions.sh` | Skill linter (needs path update on line 70) |
| `.claude/hooks/session-start.sh` | Session brief (needs TEMPLATE-CLAUDE.md block removed) |
| `.claude/settings.json` | Hook registrations (NO changes needed — symlink handles it) |

## Open Tech Debt (carried from prior session)

- `pre-commit-gate.sh:93-95` — `waves_passed` check is fail-open
- `eval-grader/post-eval` minor classification overlap
- `advisor-guided-implementation` scenario in agent-team/scenarios.md is a no-op alias
