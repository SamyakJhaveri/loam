# Session Workflow & Patterns

> Always loaded. Defines how Claude Code should approach work in this project.

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
- **Wait for user approval before implementing**

#### Plan Review Sub-Workflow

For non-trivial plans (especially those intended for cross-session execution):

1. **Draft** — Create the plan in plan mode
2. **Review** — In a fresh session, run `/plan-review-invoke <path-to-plan>`. The skill loads the canonical reference prompt from `seed/plan-reviewer-design.md` and invokes the `plan-reviewer` agent. The agent will:
   - Run the 6-point generic checklist + 6-point plan-review addendum
   - Execute the mandatory Elegance Gate (searches for better approaches)
   - Produce an APPROVE / APPROVE WITH CHANGES / REJECT verdict + handoff plan via `/writing-plans`
3. **Incorporate** — Address REJECT or CHANGES feedback, re-review if needed
4. **Handoff** (if executing in a fresh session) — Use `/writing-plans` to produce the final handoff plan. The plan must be self-contained:
   - Every file path must be repo-relative — no "the file we discussed"
   - Every task must state what to do, which files to touch, and how to verify
   - Include which skills the new session should use for each task
   - Include relevant repo rules inline so the new session doesn't rediscover them

For same-session execution: skip step 4, proceed directly to Stage 4 (Implement).

For high-stakes changes: use a fresh session for step 2 — genuine adversarial
review without sunk-cost bias from the planning session.

### 4. Implement
- Work through the plan step by step
- Use subagents for independent subtasks (worktree isolation for parallel changes)
- Verify each step before moving on
- For non-trivial changes, pause before presenting: "Is there a simpler or more elegant approach?"
- If a fix feels hacky, reconsider with full context — don't present the first thing that works
- Skip this for obvious, straightforward fixes — don't over-think simple changes
- If anything breaks, STOP — re-enter plan mode and re-plan

### 5. Record
- Update CLAUDE.md or `.claude/rules/` after discovering new conventions/gotchas
- Write session notes for complex multi-step work
- "Update your CLAUDE.md so you don't make that mistake again"

### 6. Verify (Post-Session Validation Loop — the Pipeline Gate)

`/validate` is this project's **Pipeline Gate**, in the sense of JVC's skill-wiring patterns (`_examples/02-skill-integration-patterns.md`). A Pipeline Gate is a skill that MUST run before work transitions to the next stage — here, between implement and commit. It is non-negotiable, not a suggestion. The pre-commit hook enforces it.

Differences from JVC's content-pipeline Pipeline Gate:
- The gate is **iterative**: on FAIL → fix loop → re-validate, up to 3 iterations. Content pipelines run a gate once per transition; engineering loops run it N times until pass.
- If `/validate` fails after 3 iterations on the same task, the issue is the **stage contract**, not the implementation. Stop iterating; revisit `Inputs / Process / Output / Must NOT / Done` per `.claude/rules/stage-contract.md`.

Mechanics:
- On PASS → `.validation_passed` sentinel written → `git commit` unblocked
- On any file edit after PASS → sentinel deleted → next commit re-runs the gate
- See `.claude/rules/validation-loop.md` for the wave-by-wave protocol

**Critical ordering:** Implement → `/validate` (Pipeline Gate) → `/commit` → `/pr`. `/session-critique` is optional — invoke it manually when you want adversarial review. `/ship` runs critique → validate → commit → PR when you choose to use it.

**Unattended / long runs — the `/goal` rung.** The commit-time gate and the turn-end `stop-verify-gate.sh` Stop hook are not the only verification options. For runs you walk away from, set a [`/goal` condition](https://code.claude.com/docs/en/goal) so a separate evaluator re-checks it after every turn and Claude keeps working until it holds — the best-practices "across a session" rung. Use it for autonomous campaigns alongside `/overnight-eval`.

## Context Management

- `/compact` at ~50% context usage (don't wait until 100%)
- `/clear` between unrelated tasks
- Subagents keep main context clean — only summaries return
- `/compact "focus on X"` for guided compression
- After 2+ corrections on same issue → `/clear` and restart with better prompt

## Model Selection

Single **Opus** model for primary reasoning — **Opus 4.8** — differentiated by **effort**, not by version (Sonnet only for delegated mechanical work, per the bullets below). (`opus` resolves to Opus 4.8 on the Anthropic API; aliases roll forward on other providers.)

- **Planning / brainstorming** → `opus` at `xhigh` effort (deepest reasoning for hard plans). Set with `/effort xhigh`.
- **Execution** → `opus` at `medium` or `high` effort. Lower effort here is a feature: the model scopes to what was asked instead of expanding scope (anti-over-engineering).
- **Minimal / simple execution** → `opusplan` (Opus 4.8 plans, Sonnet 4.6 executes — automatic phase switch, cost-efficient). Use when the plan is explicit and the work is mechanical.
- **Subagents / agent teams**: advisor pattern — Opus advisor + Sonnet workers. Use `--all-opus` when every teammate needs deep reasoning.
- **Never Haiku.** **Ultrathink stays on** for one-off deep reasoning (a per-turn keyword; it does not change the session effort level).

Why effort over versions: `low`, `medium`, `high`, `xhigh`, and `max` are all available on Opus 4.8, so capability is a dial on one model — no need to pin older Opus versions. See Anthropic's [effort docs](https://platform.claude.com/docs/en/build-with-claude/effort) and [model-config](https://code.claude.com/docs/en/model-config).

## Subagent Patterns

| Phase | Pattern |
|-------|---------|
| Exploration | Surgical (Glob/Grep/Read) by default; agents only with user permission (see §2) |
| Planning | plan-reviewer agent for adversarial review |
| Implementation | Subagents for independent subtasks, worktree isolation |
| Verification | Subagents for correctness, edge cases, quality, integration |

## Anti-Patterns (avoid these)

1. Don't implement without a plan — always plan first, get approval
2. Don't explore in main session — use subagents to keep context clean
3. Don't push forward when something breaks — stop and re-plan
4. Don't bundle multiple behavior changes in one session
5. Don't skip verification — always run validators and tests
6. Don't skip recording — update docs after discovering gotchas
7. Keep CLAUDE.md under 200 lines — move details to `.claude/rules/`
8. **Don't treat documentation as ground truth for code behavior.**
   The source code and test outputs are authoritative. If documentation contradicts
   source, verify against the source and update the documentation, never the reverse.
9. **Don't commit without running `/validate`** — the pre-commit gate hook requires validation.
   If tempted to skip validation, that's a signal the session scope is too large.
10. **Don't rationalize incomplete work as complete** — if something isn't done, say so
    explicitly: "X is not yet done because Y." Never frame partial work as sufficient.
11. **Don't frontload plan-mode with broad exploration sweeps.** Surgical exploration
    (Glob, Grep, targeted Read, single focused agent) is fine. Deep exploration is fine
    when the task warrants it — but ASK the user before launching 2+ Explore agents.
    Never open a plan-mode conversation by silently burning 50k tokens on "understand
    the codebase." The decision flowchart in §2 is a HARD gate — run it every time.
