# Session Workflow & Patterns

> Always loaded. Defines how Claude Code should approach work in this project.
> Based on Boris Cherny's patterns and the Claude Code Operational Playbook.

## 6-Stage Session Workflow

### 1. Orient
- Check context and set model appropriately
- Review relevant `.claude/rules/` files for the task area

### 2. Explore (surgical, ask-first — NO upfront sweeps)

> **The problem is not exploration itself — it's unsolicited broad sweeps.**
> Surgical exploration (Glob, Grep, targeted Read) is always fine.
> Deep exploration is fine too — but ASK the user before launching it.
> Agent teams explore freely (that's their purpose).
> NEVER frontload a plan-mode conversation with 2–3 Explore agents burning 50k tokens.

#### What's always allowed (no permission needed)
- **Direct reads**: `Read`, `Glob`, `Grep` on files named or implied by the task
- **Targeted single-file agents**: 1 agent with a specific question about a specific directory
- **Agent team exploration**: Teams are designed for deep exploration — use them freely

#### What requires asking the user first
- **Any Explore agent at plan-mode conversation start** — don't frontload; ask which files matter
- **2+ Explore agents in a single turn** — ask first, explain what you need to find and why
- **Broad "understand the codebase" sweeps** — never. Ask the user instead.

#### Decision Flowchart (run this before launching Explore agents)

1. Did the user name specific files? → **Read those directly. No agent.**
2. Can a single Glob or Grep find what you need? → **Do that directly. No agent.**
3. Do you need deeper context on 1 specific area? → **1 surgical agent** with a focused query (not "explore the codebase" but "find the function that handles X in directory Y").
4. Do you need broad cross-cutting exploration? → **Ask the user first.** Say what you need to find and why. They'll either point you to the right files or approve the exploration.

#### Why This Rule Exists
Broad upfront exploration burns ~50k tokens before any real work begins. That context is
then NOT available for implementation quality. The user reviews all output line-by-line.
**Surgical exploration is productive. Speculative sweeps are wasteful. When in doubt, ask.**

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

Full skill/agent reference table: use `/workflow-ref` skill.

**Critical ordering:** Implement → `/review` → `/validate` → commit → push → `dashboard-refresher` (if eval or spec data changed)

## Context Management

- `/compact` at ~50% context usage (don't wait until 100%)
- `/clear` between unrelated tasks
- Subagents keep main context clean — only summaries return
- `/compact "focus on X"` for guided compression
- After 2+ corrections on same issue → `/clear` and restart with better prompt

## Model Selection

- **All modes** → use Opus exclusively. Exception: user may switch to Haiku for commit/push (faster, cheaper for transactional git ops).
- **Fast mode** → enable only during implementation (Stage 4). Disable for reading,
  exploration, planning, and verification — these benefit from full reasoning depth.
- Subagents and agent team teammates: always Opus. Specify `model: "opus"` explicitly.

## Subagent Patterns

| Phase | Pattern |
|-------|---------|
| Exploration | Surgical (Glob/Grep/Read) by default; agents only with user permission (see §2) |
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
12. **Don't frontload plan-mode with broad exploration sweeps.** Surgical exploration
    (Glob, Grep, targeted Read, single focused agent) is fine. Deep exploration is fine
    when the task warrants it — but ASK the user before launching 2+ Explore agents.
    Never open a plan-mode conversation by silently burning 50k tokens on "understand
    the codebase." The decision flowchart in §2 is a HARD gate — run it every time.

Additional reference material (agent teams, thinking levels, memory hygiene, atomic task
decomposition, course correction): use `/workflow-ref` skill.
