# Claude Code Operational Playbook
## Drop-in Workflow Guide — Works Alongside Your CLAUDE.md

> **What this file is:** An actionable session-by-session playbook for getting maximum output from Claude Code. Drop this into any project root or keep it at `~/.claude/` for global access. It does NOT replace your `CLAUDE.md` — it complements it. Your `CLAUDE.md` tells Claude *about the project*. This file tells *you and Claude* how to *work together*.
>
> **Sourced from:** Boris Cherny (creator of Claude Code, @bcherny), Cat Wu (Anthropic), Thariq Shihipar (Anthropic), Jacqueline Lee (Anthropic), Adam Wolff (Anthropic), official Anthropic docs at code.claude.com/docs, and documented power users including Shrivu Shankar and the shanraisshan/claude-code-best-practice community repo. See the companion reference at `claude-code-mastery.md` for full attribution and deep-dive explanations.

---

## How to Use This Playbook

Every session follows six stages. Each stage has **exact prompts, commands, and file templates** you can copy-paste. The stages are:

```
STAGE 1 → Setup & Orient       (30 seconds)
STAGE 2 → Explore & Understand (subagents explore in parallel)
STAGE 3 → Plan & Architect     (plan mode, ultrathink, adversarial review)
STAGE 4 → Implement            (auto-accept mode, worktree isolation)
STAGE 5 → Record & Learn       (update CLAUDE.md, task notes)
STAGE 6 → Verify & Validate    (2–6 subagents stress-test the work)
```

---

## STAGE 1 — Setup & Orient

**Goal:** Start the session with clean context, the right model, and a named session.

### 1.1 Launch

```bash
# Standard launch (opens in current repo)
claude

# Launch in an isolated worktree (for parallel work)
claude --worktree feat-auth

# Launch in worktree + tmux (each agent gets its own pane)
claude --worktree feat-auth --tmux

# Resume the last session in this directory
claude --continue

# Pick from all past sessions
claude --resume
```

### 1.2 First 30 Seconds of Every Session

```bash
# 1. Set the model to highest capability
/model
# → Select: opus with high effort

# 2. Name this session immediately (you WILL forget later)
/rename payment-refund-logic

# 3. Check context usage (should be near 0%)
/context
```

### 1.3 Parallel Session Setup (Boris's Primary Workflow)

Boris runs 5–15 parallel sessions. His setup:

```bash
# Create 3-5 worktrees from main
git worktree add .claude/worktrees/feat-a origin/main
git worktree add .claude/worktrees/feat-b origin/main
git worktree add .claude/worktrees/analysis origin/main

# Add shell aliases for one-keystroke switching
# (add to your .bashrc or .zshrc)
alias za="cd $(git rev-parse --show-toplevel)/.claude/worktrees/feat-a && claude"
alias zb="cd $(git rev-parse --show-toplevel)/.claude/worktrees/feat-b && claude"
alias zc="cd $(git rev-parse --show-toplevel)/.claude/worktrees/analysis && claude"

# Enable system notifications so you know when a session finishes
/terminal-setup
# → Select: Enable iTerm2/system notifications
```

### 1.4 Status Line (Always Know Where You Stand)

```bash
/statusline
# Generates something like:
# [Opus 4.7] 📁 myrepo | 🌿 feat-auth | ████░░ 42% | $1.23 | 🕐 14m
```

The **context percentage is the most important number on your screen.** When it hits 50%, run `/compact`. When switching tasks, run `/clear`.

---

## STAGE 2 — Explore & Understand

**Goal:** Before touching any code, have Claude build a complete mental model of the relevant codebase areas. Use parallel subagents to keep the main context clean.

### 2.1 The Exploration Prompt (Copy-Paste Ready)

```
I need to [describe what you want to build/fix].

Before we write any code:
1. Use 5 parallel subagents to explore the codebase
2. Assign each subagent a different area:
   - Subagent 1: Entry points and routing relevant to this feature
   - Subagent 2: Data models and database schema involved
   - Subagent 3: Existing tests covering this area
   - Subagent 4: Related utilities, helpers, and shared code
   - Subagent 5: Configuration, environment variables, and deployment concerns
3. Each subagent should report: file paths, key functions, dependencies, and gotchas
4. Do NOT write any code yet

Use ultrathink for this analysis.
```

### 2.2 Targeted Exploration Prompts

```
# Explore a specific module deeply
Use a subagent to thoroughly explore the authentication module.
Read every file in src/auth/, trace the token refresh flow end-to-end,
and report: entry points, middleware chain, error handling, and test coverage gaps.

# Explore git history for context (Boris's technique)
Look through the git history of src/payments/ and summarize
how the API evolved over the last 20 commits. What patterns were
tried and abandoned? Why?

# Explore for a bug
Use 3 subagents to investigate this error: [paste error].
Subagent 1: trace the stack trace to find the root cause file.
Subagent 2: search for similar patterns in the codebase that might have the same bug.
Subagent 3: check if there are existing tests that should have caught this.
```

### 2.3 Important: Subagents Keep Your Context Clean

From official docs: exploration fills context fast. A single 500-line file read may never leave your context window. By delegating exploration to subagents, only the *summary* returns to your main session. This is not optional for large codebases — it is the primary context management strategy.

```
# If you already explored manually and context is cluttered:
/compact "focus on the auth token refresh logic we discussed"

# If context is beyond saving:
/clear
# Start fresh with a focused prompt referencing docs/tasks/[task].md
```

---

## STAGE 3 — Plan & Architect

**Goal:** Produce a detailed, reviewed plan BEFORE any implementation. This is where most of the intellectual work happens. A good plan lets Claude 1-shot the implementation.

### 3.1 Enter Plan Mode

```
Shift+Tab → Shift+Tab    (press twice to enter Plan mode)
```

Or launch directly:

```bash
claude --permission-mode plan
```

In Plan mode, Claude will NOT write code. It will only read files and reason.

### 3.2 The Planning Prompt (Copy-Paste Ready)

```
Based on the exploration findings, plan the implementation for [feature/fix].

Use ultrathink. Structure the plan as:

1. GOAL: One sentence, concrete and measurable
2. FILES TO TOUCH: Exact paths, what changes in each
3. DEPENDENCIES: New packages needed (if any — prefer none)
4. IMPLEMENTATION STEPS: Ordered, each step small enough to verify
5. VERIFICATION PLAN: Exact commands to prove each step works
6. RISKS: What could go wrong, rollback strategy
7. EDGE CASES: What inputs/states could break this

Write the plan to docs/tasks/[task-name].md so we have a reset point.

Do NOT implement yet. Show me the plan for approval.
```

### 3.3 Adversarial Plan Review (Boris's Staff Engineer Pattern)

Once Claude presents a plan, challenge it before approving:

```
# Have a second subagent review the plan adversarially
Use a subagent (Opus model) to review this plan as a staff engineer.
Find: unstated assumptions, security risks, scalability concerns,
edge cases not covered, and simpler alternatives.
Be adversarial — the goal is to find every flaw before we build.
```

Or if you have the `plan-reviewer` agent set up:

```
# .claude/agents/plan-reviewer.md triggers automatically
Review this plan. Challenge every assumption. Find the flaws.
```

### 3.4 Plan Mode Escape Hatch

**Critical rule from Boris's team:** The moment implementation goes sideways — the INSTANT something doesn't work as planned — switch back to Plan mode and re-plan. Do NOT keep pushing.

```
# When things go wrong mid-implementation:
Shift+Tab → Shift+Tab    (back to Plan mode)

"Stop. This approach isn't working because [reason].
Re-plan from scratch. Knowing everything you know now,
what's the elegant solution? Don't be anchored to the failed approach."
```

### 3.5 Spec-Based Development (Thariq Shihipar's Technique)

For new features, front-load specification quality by having Claude interview you:

```
Read @docs/SPEC.md and interview me in detail using the AskUserQuestionTool
about literally anything: technical implementation, UI & UX, concerns, tradeoffs.
Make sure the questions are not obvious. Be very in-depth and continue
interviewing me continually until it's complete, then write the spec to the file.
```

This forces you to articulate decisions you'd otherwise skip, producing a spec that Claude can implement with far fewer mistakes.

---

## STAGE 4 — Implement

**Goal:** Execute the approved plan. Switch to auto-accept mode and let Claude work. One behavior change per session.

### 4.1 Switch to Auto-Accept Mode

```
Shift+Tab    (cycle to auto-accept mode)
```

Or for truly autonomous long-running tasks:

```bash
claude --permission-mode dontAsk
# Only after your .claude/settings.json has proper allow/deny lists
```

### 4.2 The Implementation Prompt

```
The plan is approved. Implement it now.

Follow the plan in docs/tasks/[task-name].md exactly.
After each step, run the verification command for that step.
If any verification fails, stop and tell me — do not proceed.

Use subagents for any independent subtasks that can run in parallel.
```

### 4.3 Test-Driven Implementation (Anthropic's Favorite Pattern)

```
# Step 1: Write tests first
Write tests for [feature] based on these expected inputs and outputs:
- Input: X → Expected output: Y
- Input: A → Expected output: B
Do NOT create mock implementations. Do NOT write the feature code yet.

# Step 2: Confirm tests fail
Run the tests. Confirm they fail (they should — the feature doesn't exist yet).

# Step 3: Implement
Now write the code that makes all tests pass.
Do NOT modify the tests.

# Step 4: Verify
Run the full test suite. Run typecheck. Run lint.
```

### 4.4 Parallel Implementation with Worktree Isolation

For large changes touching many files:

```
Migrate all files in src/services/ from callback-style to async/await.
Batch into groups of 3 files. One subagent per group.
Each subagent: implement, run tests, report results.
Use worktree isolation so agents don't conflict.
```

Or use the built-in `/batch` command:

```bash
/batch migrate src/components/ from class components to functional components
# Each agent gets its own worktree, runs tests, opens its own PR
```

### 4.5 Mid-Implementation Course Corrections

```bash
# Stop Claude mid-action (preserves context)
Esc

# Undo the last action and try a different approach
Esc + Esc    # or /rewind
# Select the checkpoint to restore to

# Push Claude to do better after a mediocre first attempt
"Knowing everything you know now, scrap this and implement the elegant solution."
```

---

## STAGE 5 — Record & Learn

**Goal:** Persist everything valuable from this session so future sessions (and future you) benefit. This is what compounds your productivity over time.

### 5.1 Update CLAUDE.md After Every Mistake

Boris's exact instruction — use this verbatim after every correction:

```
Update your CLAUDE.md so you don't make that mistake again.
```

Claude will write a precise rule for itself. Example: if Claude used `enum` when you prefer literal unions, it will add `Never use enum; prefer string literal unions: type S = 'a' | 'b'`.

### 5.2 Update Task Notes

```
Write a summary of this session to docs/tasks/[task-name].md.
Include: what was done, key decisions made, gotchas encountered,
verification results, and what's left to do.
```

### 5.3 The Self-Improvement Loop (Boris's Team Pattern)

```
# At end of every session:
Review what happened this session. What went well?
What went wrong? What would you do differently?
Write a diary entry to docs/tasks/[task-name]-diary.md.
Then distill any reusable learnings into CLAUDE.md.
```

### 5.4 Record Working Style Preferences

After a few sessions, you'll notice patterns in how you prefer to work. Tell Claude to record them:

```
Add to CLAUDE.md under "User Working Style":
- Always explore before implementing
- Plan approval required before any code changes
- Use parallel subagents (3-5) for exploration
- Use ultrathink for complex analysis
- Never skip verification steps
- Record learnings after every session
```

This is exactly what was done in the companion `claude_code_power_use` note — formalize it into your CLAUDE.md so it persists.

### 5.5 Periodic CLAUDE.md Pruning

Every 1-2 weeks:

```
Review the CLAUDE.md. Remove anything that is:
- Stale (no longer applies)
- Duplicated (said twice in different ways)
- Too specific (belongs in a rule file, not the global constitution)
- Contradictory (conflicting instructions degrade ALL instruction-following)
Keep it under 200 lines. Move detailed rules to .claude/rules/ files.
```

---

## STAGE 6 — Verify & Validate

**Goal:** Never trust implementation output without independent verification. This is Boris's #1 tip: give Claude a feedback loop and quality 2-3x's.

### 6.1 Basic Verification (Every Single Session)

Always have these commands in your CLAUDE.md (Claude runs them automatically):

```bash
# Example for a TypeScript project:
bun run typecheck                          # After every change
bun run test -- -t "test name"             # Specific test
bun run lint && bun run typecheck && bun run test  # Full pre-PR

# Example for a Python project:
python3 -m pytest tests/ -v               # Run tests
python3 -m mypy src/                       # Type check
python3 -m ruff check src/                 # Lint
```

### 6.2 Multi-Subagent Verification (Copy-Paste Ready)

After implementation, spawn 2-6 verification subagents:

```
The implementation is complete. Before we merge, verify it thoroughly.

Use 4 subagents in parallel:

Subagent 1 (Correctness): Run the full test suite. Run typecheck.
Run lint. Report any failures with exact error messages.

Subagent 2 (Edge Cases): Review the implementation for edge cases
not covered by tests. Write new tests for any gaps found. Run them.

Subagent 3 (Code Quality): Review for code smells, duplicated logic,
magic numbers, unclear naming, missing error handling.
Compare against CLAUDE.md conventions.

Subagent 4 (Security): Check for injection vulnerabilities,
exposed secrets, improper auth checks, insecure data handling.

Each subagent: report findings with file:line references.
Do NOT auto-fix — report only. I will decide what to fix.
```

### 6.3 Boris's Code Review Pattern

From his Every.to podcast description — multi-layered adversarial review:

```
Review this PR as if you were 5 different senior engineers.
Agent 1: Check style guidelines and CLAUDE.md compliance.
Agent 2: Check project history — does this change contradict past decisions?
Agent 3: Find bugs — trace every code path, check error handling.
Agent 4: Check performance — any O(n²) where O(n) would work?
Agent 5: Poke holes in agents 1-4's findings — which are false positives?

Only report the findings that survive agent 5's scrutiny.
```

### 6.4 Proof-of-Work Prompts

```
# Force Claude to demonstrate correctness
Prove to me this works. Diff the behavior between main and this branch.
Show exactly what changed, run the tests, explain why the old behavior was wrong.

# Adversarial grilling before merge
Grill me on these changes. Ask me hard questions.
Don't let me make a PR until I pass your test.

# Force elegance check
Before we merge: is there a simpler way to achieve the same result?
Would a senior engineer look at this and say "why didn't you just..."?
```

### 6.5 Post-Verification Commit

```
# Only after all verification passes:
/commit
/pr

# Or the combined flow:
All verification passed. Commit with a conventional commit message,
push, and open a PR. Include the verification results in the PR body.
```

---

## Custom Skills to Create (File Templates)

Drop these files into your project's `.claude/` directory.

### Feature Development Skill

```markdown
# .claude/skills/feature-dev/SKILL.md
---
name: feature-dev
description: >
  Structured feature development. Use when user says "build",
  "implement", "create feature", or "new feature".
model: opus
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Use ultrathink for this task.

## Phase 1: Understand
- Ask me exactly what I want built
- Use subagents to explore related code areas
- Report: what exists, what's missing, what needs to change

## Phase 2: Specify
- Write a spec to docs/tasks/$ARGUMENTS.md
- Include: goal, files to touch, verification commands, risks
- Present for my approval. Do NOT proceed without "go ahead"

## Phase 3: Implement
- Follow the approved spec step by step
- Run verification after each step
- If anything fails, stop and re-plan

## Phase 4: Verify
- Use 3 subagents: correctness, edge cases, code quality
- Report all findings before committing

## Phase 5: Record
- Update CLAUDE.md with any new learnings
- Update docs/tasks/$ARGUMENTS.md with session diary
```

### Bug Fix Skill

```markdown
# .claude/skills/fix-bug/SKILL.md
---
name: fix-bug
description: >
  Structured bug fixing. Use when user says "fix", "debug",
  "broken", "error", or pastes a stack trace.
model: opus
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

Use ultrathink.

## Phase 1: Reproduce
- Identify the exact reproduction steps
- Run them and confirm the bug exists
- Capture the exact error output

## Phase 2: Diagnose
- Use 3 subagents to investigate root cause from different angles:
  1. Trace the stack trace / error path
  2. Search for similar patterns that might have the same issue
  3. Check git blame — what changed recently in this area?
- Synthesize findings into a root cause hypothesis

## Phase 3: Plan Fix
- Present the fix plan for approval
- Include: what changes, why, what could go wrong
- Write a regression test BEFORE fixing

## Phase 4: Fix & Verify
- Implement the fix (do NOT modify the test)
- Run the regression test — must pass
- Run full test suite — no regressions
- If anything fails, re-diagnose

## Phase 5: Record
- Update CLAUDE.md if the bug revealed a convention violation
- Document the bug and fix in docs/tasks/ for future reference
```

### Code Review Skill

```markdown
# .claude/skills/multi-review/SKILL.md
---
name: multi-review
description: >
  Multi-agent code review. Use when user says "review",
  "check this", "is this ready to merge", or "PR review".
model: opus
context: fork
---

<staged_diff>
!`git diff --cached 2>/dev/null || git diff HEAD~1`
</staged_diff>

Review this diff using 5 parallel subagents:

1. **Style & Conventions**: Check against CLAUDE.md rules. Flag violations.
2. **Correctness**: Trace logic paths. Find bugs, race conditions, null refs.
3. **Security**: Injection, auth bypass, exposed secrets, insecure defaults.
4. **Performance**: Unnecessary allocations, O(n²), missing indexes, N+1 queries.
5. **Skeptic**: Review findings from agents 1-4. Which are false positives? Remove them.

Output: Only findings that survived agent 5's scrutiny.
Format: file:line | severity (critical/warning/nit) | description | suggested fix
```

---

## Custom Subagents to Create (File Templates)

### Plan Reviewer (Adversarial)

```markdown
# .claude/agents/plan-reviewer.md
---
name: plan-reviewer
description: >
  Adversarial plan review. Use when user says "review this plan"
  or "challenge this design". Plays staff engineer finding flaws.
model: opus
tools: Read, Glob, Grep
---

You are a staff engineer reviewing a proposed plan. Your job is adversarial:
1. Find unstated assumptions
2. Identify security and scalability risks
3. Point out edge cases not accounted for
4. Challenge timeline estimates
5. Suggest simpler alternatives if they exist

Be direct. Do not be diplomatic. The goal is to surface every flaw
before implementation begins — not after.
```

### Verification Agent

```markdown
# .claude/agents/verify-app.md
---
name: verify-app
description: >
  End-to-end verification agent. Use after implementation to validate
  correctness before merging. Runs tests, checks types, reviews output.
model: opus
tools: Read, Bash, Grep, Glob
---

You are a QA engineer performing pre-merge verification.

1. Run the full test suite. Report any failures with exact output.
2. Run type checking. Report any errors.
3. Run linting. Report any violations.
4. Check that all files touched have corresponding test coverage.
5. Verify the changes match the spec in docs/tasks/ (if it exists).
6. Look for: hardcoded values, missing error handling, TODO/FIXME comments.

Report everything. Do NOT auto-fix. The human decides what to address.
```

### Code Simplifier

```markdown
# .claude/agents/code-simplifier.md
---
name: code-simplifier
description: >
  Post-implementation cleanup. Use after code changes to reduce
  complexity, remove duplication, and improve readability.
model: sonnet
tools: Read, Edit, Bash, Grep, Glob
---

Review recently changed files (git diff --name-only HEAD~3).
For each file, look for:
1. Duplicated logic that should be a shared function
2. Nested conditionals >3 levels (refactor with early returns)
3. Magic numbers/strings (extract to named constants)
4. Unused imports or dead code
5. Unclear variable/function names

Apply improvements. Run typecheck and tests after each change.
If any test fails, revert that specific change and move on.
```

---

## Hooks Configuration

Drop this into `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'formatted' || true"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf|rm -fr'; then echo 'BLOCKED: rm -rf not allowed' && exit 2; fi"
          }
        ]
      },
      {
        "matcher": "Bash(git push*--force*)",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'BLOCKED: force push not allowed.' && exit 2"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude finished\" with title \"Claude Code\" sound name \"Ping\"' 2>/dev/null || true"
          }
        ]
      }
    ]
  },
  "permissions": {
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(rm -fr:*)",
      "Bash(git push --force:*)",
      "Bash(git reset --hard:*)"
    ]
  }
}
```

**Adapt the `PostToolUse` formatter** to your project:

```json
// For JavaScript/TypeScript:
"command": "npx prettier --write . || true"

// For Python:
"command": "ruff format . || true"

// For Rust:
"command": "cargo fmt || true"
```

---

## Quick Reference: Session Commands

```bash
# ── MODES ─────────────────────────────────────────────────
Shift+Tab              # Cycle: Normal → Auto-Accept → Plan
Shift+Tab × 2          # Jump to Plan mode directly

# ── CONTEXT MANAGEMENT (most important discipline) ────────
/clear                 # Reset. Use between unrelated tasks
/compact               # Compress context. Do at 50%, NOT 100%
/compact "focus on X"  # Guided compression
/context               # Show context usage as visual grid
Esc                    # Stop mid-action, keep context
Esc + Esc              # Rewind menu (undo to any checkpoint)

# ── SESSION MANAGEMENT ────────────────────────────────────
/rename                # Name the session NOW
claude --continue      # Resume last session in this directory
claude --resume        # Pick from all sessions
/teleport              # Hand off to web/desktop

# ── SKILLS & TOOLS ───────────────────────────────────────
/commit                # Conventional commit
/pr                    # Push + open PR
/simplify              # Parallel code quality pass (built-in)
/batch [desc]          # Parallel migration with per-agent PRs
/techdebt              # Session-end cleanup scan
/feature-dev [name]    # Structured feature development
/fix-bug [desc]        # Structured bug fixing
/multi-review          # Multi-agent code review

# ── MODEL & THINKING ─────────────────────────────────────
/model                 # Switch model (use Opus + High)
# In prompts: "think" < "think hard" < "think harder" < "ultrathink"
# Use ultrathink for: architecture, security, complex planning

# ── CONFIGURATION ─────────────────────────────────────────
/permissions           # Pre-approve safe commands
/hooks                 # Configure lifecycle hooks
#                      # Press # mid-session to add to CLAUDE.md
/memory                # View/edit auto-memory
```

---

## Quick Reference: Essential Prompts

```
# ── EXPLORATION ───────────────────────────────────────────
Use 5 subagents to explore [area]. Do not write code yet.
Use a subagent to trace [function] end-to-end. Report all callers and callees.
Look through git history of [path] and explain how the API evolved.

# ── PLANNING ──────────────────────────────────────────────
Plan the implementation. Use ultrathink. Write plan to docs/tasks/[name].md.
Do NOT implement yet — show me the plan for approval.
Use a subagent to review this plan as a staff engineer. Find every flaw.

# ── IMPLEMENTATION ────────────────────────────────────────
The plan is approved. Implement it. Run verification after each step.
Use subagents for independent subtasks that can run in parallel.
Write tests first. Run them. Confirm they fail. Then implement.

# ── COURSE CORRECTION ─────────────────────────────────────
Stop. This isn't working. Re-plan from scratch with what we know now.
Knowing everything you know now, scrap this and do it the elegant way.
Before implementing: is there a simpler approach? Pause and think.

# ── VERIFICATION ──────────────────────────────────────────
Use 4 subagents: correctness, edge cases, code quality, security.
Prove to me this works. Diff behavior between main and this branch.
Grill me on these changes. Don't make a PR until I pass your test.

# ── RECORDING ─────────────────────────────────────────────
Update CLAUDE.md so you don't make that mistake again.
Write a session diary to docs/tasks/[name]-diary.md.
Review CLAUDE.md. Remove anything stale or duplicated.
```

---

## File Tree: What to Create in Your Project

```
your-project/
├── CLAUDE.md                              ← Project constitution (< 200 lines)
├── .mcp.json                              ← Shared MCP config (check into git)
│
├── .claude/
│   ├── settings.json                      ← Permissions + hooks (check into git)
│   │
│   ├── agents/
│   │   ├── plan-reviewer.md               ← Adversarial plan review
│   │   ├── verify-app.md                  ← Pre-merge verification
│   │   └── code-simplifier.md             ← Post-implementation cleanup
│   │
│   ├── skills/
│   │   ├── feature-dev/SKILL.md           ← Structured feature workflow
│   │   ├── fix-bug/SKILL.md               ← Structured bug fix workflow
│   │   ├── review/SKILL.md                ← Multi-agent code review
│   │   ├── commit/SKILL.md                ← Conventional commit
│   │   └── pr/SKILL.md                    ← Push + open PR
│   │
│   ├── rules/                             ← Path-scoped rules (auto-load)
│   │   └── python.md                      ← Loads only for *.py files
│   │
│   └── worktrees/                         ← Parallel session isolation
│
├── docs/
│   └── tasks/                             ← Per-task plans + session diaries
│       └── [task-name].md
│
└── CLAUDE_CODE_PLAYBOOK.md                ← This file
```

---

## Thinking Levels: When to Use What

| Level | Keyword | Use For |
|-------|---------|---------|
| Minimal | `think` | Simple lookups, formatting, small edits |
| Moderate | `think hard` | Multi-file changes, debugging |
| Substantial | `think harder` | Architectural decisions, complex refactors |
| Maximum | `ultrathink` | Security analysis, system design, complex planning, writing CLAUDE.md rules |

Include `ultrathink` in any skill's content to automatically enable maximum reasoning for that skill.

---

## Cost Awareness

| Model | Input/Output per 1M tokens | Best For |
|-------|---------------------------|----------|
| Opus 4.7 | $5 / $25 | Planning, architecture, complex implementation |
| Sonnet 4.6 | $3 / $15 | Day-to-day coding, subagent tasks |
| Haiku 4.5 | ~$0.80 / $4 | Commits, formatting, simple lookups |

Boris's advice: don't optimize cost at the start. Use Opus for everything. The time saved from less steering and fewer mistakes more than pays for the token cost. Average daily cost is ~$6/developer.

Monitor with `/cost`. Set limits with `/usage`.

---

## Anti-Patterns to Avoid

**❌ Implementing without a plan.** You will waste tokens on the wrong approach.

**❌ Exploring in the main session.** Use subagents. Your main context fills up permanently with every file read.

**❌ Pushing forward when something breaks.** Switch to Plan mode immediately. Re-plan. Boris's team: "Don't keep pushing."

**❌ Bundling multiple behavior changes.** One change per session. "Add retry logic" + "redesign the UI" = entangled diffs nobody can review.

**❌ Skipping verification.** Every unverified change is a bug waiting to ship. Verification 2-3x's output quality.

**❌ Not recording mistakes.** If Claude makes a mistake and you don't update CLAUDE.md, it WILL make the same mistake in the next session.

**❌ Massive CLAUDE.md files.** Over 200 lines and ALL instruction-following degrades. Be ruthless about pruning. Move details to `.claude/rules/` with path-scoping.

**❌ Using `--dangerously-skip-permissions` as a default.** Use `/permissions` to pre-approve safe commands instead. Boris almost never uses the dangerous flag.

---

## Sources

- **Boris Cherny** (@bcherny) — Creator of Claude Code. Jan 2, Jan 31, Feb 11, Feb 20, Feb 27, Mar 7, 2026 X/Threads posts. [howborisusesclaudecode.com](https://howborisusesclaudecode.com). Lenny's Podcast (Jan 2026). Every.to podcast.
- **Anthropic Official Docs** — [code.claude.com/docs](https://code.claude.com/docs): best-practices, sub-agents, skills, hooks, common-workflows, memory, permissions, agent-teams
- **Anthropic Engineering Blog** — [anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- **Cat Wu** (Anthropic) — Every.to podcast on plan mode and MCP usage
- **Thariq Shihipar** (Anthropic, @trq212) — AskUserQuestionTool technique for spec development
- **Jacqueline Lee** (Anthropic) — On-call playbook as slash commands pattern
- **Shrivu Shankar** — [blog.sshh.io](https://blog.sshh.io/p/how-i-use-every-claude-code-feature) (feature-by-feature walkthrough)
- **shanraisshan/claude-code-best-practice** — 8.7k⭐ community repo compiling team tips
- **Companion Reference** — See `claude-code-mastery.md` for the full 1700+ line deep-dive with complete attribution
