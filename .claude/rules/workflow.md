# Session Workflow & Patterns

> Always loaded. Defines how Claude Code should approach work in this project.
> Based on Boris Cherny's patterns and the Claude Code Operational Playbook.

## 6-Stage Session Workflow

### 1. Orient
- Check context and set model appropriately
- Review relevant `.claude/rules/` files for the task area

### 2. Explore
- Use 3-5 parallel subagents to explore relevant code areas
- Do NOT read files directly in main context — delegate to subagents
- Summarize findings before proceeding

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

### 6. Verify
- Launch 2-4 parallel verification subagents
- Run `python3 scripts/validate_schema.py --all`
- Run relevant unit tests

## Context Management

- `/compact` at ~50% context usage (don't wait until 100%)
- `/clear` between unrelated tasks
- Subagents keep main context clean — only summaries return
- `/compact "focus on X"` for guided compression
- After 2+ corrections on same issue → `/clear` and restart with better prompt

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
| Exploration | 3-5 subagents, each covers a different angle |
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
