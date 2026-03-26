# Session Workflow & Patterns

> Always loaded. Defines how Claude Code should approach work in this project.
> Based on Boris Cherny's patterns and the Claude Code Operational Playbook.

## 6-Stage Session Workflow

### 1. Orient
- Check context and set model appropriately
- Review relevant `.claude/rules/` files for the task area

### 2. Explore (scale to task scope — don't front-load)
- **Skip entirely** when all target files are already known (single-file edit, doc update,
  running a known command, spec field change)
- **1 agent** for targeted tasks touching 1–3 known files where you need surrounding
  context (callers, tests, imports)
- **2–3 agents** for cross-cutting tasks where scope is uncertain or multiple subsystems
  are involved (pipeline changes, new feature, architecture decisions)
- Do NOT read files directly in main context — delegate to subagents; only summaries return
- Summarize findings before proceeding
- **Just-in-time, not just-in-case:** if a problem surfaces during implementation that
  needs broader understanding, launch an explorer agent then — not upfront "just in case"

### 3. Plan
- Enter plan mode for non-trivial changes
- Use ultrathink for complex analysis
- Get adversarial review via `plan-reviewer` agent
- **Wait for user approval before implementing**

### 4. Implement
- Work through the plan step by step
- Use subagents for independent subtasks (worktree isolation for parallel changes)
- Verify each step before moving on
- If anything breaks, STOP — re-enter plan mode and re-plan

### 5. Record
- Update CLAUDE.md or `.claude/rules/` after discovering new conventions/gotchas
- Write session notes for complex multi-step work
- "Update your CLAUDE.md so you don't make that mistake again" (Boris's rule)

### 6. Verify (Post-Session Validation Loop)
- **Run `/validate`** — full 4-wave validation loop (10+ agents, ~3 min)
- Wave 1 (parallel, ~30s): verify-app + diff-reviewer + security-scanner
- Wave 2 (parallel, ~60s): test-synthesizer + regression-checker + spec-auditor
- Wave 3 (parallel, ~45s): consistency-checker + code-simplifier
- Wave 4 (sequential, ~30s): self-critic (Opus) + plan-reviewer
- On FAIL → fix loop: plan mode → user approval → implement → re-validate (max 3 iterations)
- On PASS → `.validation_passed` sentinel written → `git commit` unblocked
- **Pre-commit hook enforces this** — `git commit` is blocked without a valid sentinel
- See `.claude/rules/validation-loop.md` for full protocol

## Skill & Agent Quick Reference

Use these at the right phase — don't skip them, don't over-invoke them.

| When | Skill / Agent | Command | What it does |
|------|--------------|---------|-------------|
| After any code/spec change | `/validate` | `/validate` (full) or `/validate quick` | 4-wave validation; writes sentinel; required before commit |
| Before merging or after multiple file changes | `/review` | `/review` | 4-agent parallel code review (style, correctness, security, perf) |
| Launching an eval batch | `/eval-run` | `/eval-run rodinia cuda-to-omp` | Param collection → pre-flight → execute → analyze |
| After eval completes OR spec count changes | `dashboard-refresher` agent | Invoke via Agent tool | Fixes hardcoded numbers in all 12 viz files |
| Starting a sprint session | `/session-start` | `/session-start 9` | Extracts prompt, checks git, verifies prerequisites |
| New benchmark suite | `/gen-spec` | `/gen-spec xsbench` | Full guided spec generation wizard |
| Bug fix workflow | `/fix-bug` | `/fix-bug "description"` | Reproduce → diagnose → fix → verify loop |
| New feature | `/feature-dev` | `/feature-dev "name"` | Explore → plan → implement → verify |

**Critical ordering:** Implement → `/review` → `/validate` → commit → push → `dashboard-refresher` (if eval or spec data changed)

## Context Management

- `/compact` at ~50% context usage (don't wait until 100%)
- `/clear` between unrelated tasks
- Subagents keep main context clean — only summaries return
- `/compact "focus on X"` for guided compression
- After 2+ corrections on same issue → `/clear` and restart with better prompt

## Memory Hygiene

Memory files are write-only by default — they grow but never get maintained.
Use `/dream` to consolidate periodically.

- **`/dream audit`** — Read-only health report (run weekly or when memory feels stale)
- **`/dream`** — Full 4-phase consolidation with user approval gate
- **`/dream prune <file>`** — Targeted cleanup of one file

### When to consolidate
- After major milestones (sprint phase completion, paper draft, eval batch)
- After 5+ sessions without consolidation
- When `/session-start` reports memory staleness
- Before long breaks (>3 days between sessions)

### Memory file conventions
- MEMORY.md: index only, <200 lines, no content — just `- [Title](file.md) — hook`
- Topic files: proper frontmatter (name, description, type)
- Prefer cross-references over duplication (point to `.claude/rules/` for canonical content)
- Convert all dates to absolute (YYYY-MM-DD) — relative dates rot immediately
- Staleness tiers: permanent (1) > active (2) > completed (3) > historical (4) > stale (5)

## Thinking Levels

| Level | When to use |
|-------|-------------|
| `think` | Simple lookups, single-file edits |
| `think hard` | Multi-file changes, debugging |
| `think harder` | Architecture decisions, complex refactors |
| `ultrathink` | Security review, complex planning, adversarial analysis |

## Model Selection

- **Plan mode** → uses Opus (deep reasoning for architecture)
- **Execution mode** → uses Sonnet (fast implementation)
- Use Haiku only for quick triage (which specs are ready? quick counts)

## Subagent Patterns

| Phase | Pattern |
|-------|---------|
| Exploration | 0–3 subagents, scaled to task uncertainty (see §2 above) |
| Planning | plan-reviewer agent for adversarial review |
| Implementation | Subagents for independent subtasks, worktree isolation |
| Verification | 2-4 subagents: correctness, edge cases, quality, integration |

## Anti-Patterns (avoid these)

1. Don't implement without a plan — always plan first, get approval
2. Don't explore in main session — use subagents to keep context clean
3. Don't push forward when something breaks — stop and re-plan
4. Don't bundle multiple behavior changes in one session
5. Don't skip verification — always run validators and tests
6. Don't skip recording — update docs after discovering gotchas
7. Keep CLAUDE.md under 200 lines — move details to `.claude/rules/`
8. **Don't treat documentation as ground truth for code behavior.**
   `known-issues.md` and sprint docs record human observations — they can be wrong.
   The source code and test outputs are authoritative. If documentation contradicts
   source, verify against the source and update the documentation, never the reverse.
9. **Don't change spec run args without reading the actual source's argc check.**
   See Run Argument Verification Protocol in `spec-conventions.md`. This rule exists
   because of a real incident where "fixes" based on documentation caused 2 specs to
   silently fail for weeks. The evidence is always in the source and the baseline stdout.
10. **Don't commit without running `/validate`** — the pre-commit gate hook will block it
    anyway. If tempted to skip validation, that's a signal the session scope is too large.
    Split the work into smaller sessions instead of bypassing quality gates.
11. **Don't rationalize incomplete work as complete** — the self-critic agent (Opus) will
    catch it. If something isn't done, say so explicitly: "X is not yet done because Y."
    Never frame partial work as sufficient to avoid running the full validation loop.

## Atomic Task Decomposition (for multi-step plans)

When facing a large plan (fix N issues, retest, update dashboard, push):

1. **Audit first** — Evaluate what's actually done vs. claimed. Check with real data.
2. **Decompose** — Each session gets ONE objective with concrete acceptance criteria.
3. **Map dependencies** — Which sessions are sequential? Which can run in parallel?
4. **Write session plan files** — Store in `docs/session_plans/session_N_<desc>.md`. Each must include:
   - Copy-pasteable Claude Code prompt (self-contained, all context included)
   - Files reference table (paths, line numbers, current content, what changes)
   - Cross-reference sources (so the session verifies against source, not docs)
   - Verification commands with expected output
   - Commit message template
   - Troubleshooting guide for likely failures
   - Success criteria checklist
5. **`/clear` between sessions** — Fresh context for each atomic task.
6. **Gate on verification** — Don't commit until verification passes with ACTUAL data.

**Why this works:** Context management IS quality management. A session doing 1 thing well
uses all its context budget on that thing. Errors don't compound across sessions. Each
commit is one verified, complete unit of work. Independent sessions can run in parallel.

## Course Correction

When implementation goes wrong, don't keep pushing. Instead:
> "Stop. This isn't working. Re-plan from scratch knowing what we know now."

Re-enter plan mode, reassess assumptions, and get approval for the new approach.
