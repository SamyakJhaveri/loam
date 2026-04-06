# Agentic Coding with Claude Code: A ParBench Practitioner's Guide

> A comprehensive reference for building and orchestrating AI-assisted development
> workflows in the ParBench project. Grounded in Addy Osmani's agentic coding
> principles, adapted for HPC research software engineering.
>
> Written for: Samyak Jhaveri (PhD candidate, HPC/SE/AI intersection)
> Project: ParBench — LLM-based parallel code translation benchmark (SC26 paper)
> Last updated: 2026-04-01

---

## Table of Contents

1. [Fundamentals — The Orchestrator Mindset](#chapter-1-fundamentals--the-orchestrator-mindset)
2. [Claude Code Agent Primitives](#chapter-2-claude-code-agent-primitives)
3. [Skills Deep Dive](#chapter-3-skills-deep-dive)
4. [Hooks Deep Dive](#chapter-4-hooks-deep-dive)
5. [Custom Agents Deep Dive](#chapter-5-custom-agents-deep-dive)
6. [The Ralph Loop Pattern](#chapter-6-the-ralph-loop-pattern)
7. [Agent Teams in Practice](#chapter-7-agent-teams-in-practice)
8. [Quality Gates](#chapter-8-quality-gates)
9. [The Self-Improving Codebase](#chapter-9-the-self-improving-codebase)
10. [Recipes — Common ParBench Workflows](#chapter-10-recipes--common-parbench-workflows)
11. [Osmani's Anti-Patterns Cheat Sheet](#chapter-11-osmanis-anti-patterns-cheat-sheet)
12. [Quick Reference Card](#chapter-12-quick-reference-card)
13. [The Superpowers Plugin](#chapter-13-the-superpowers-plugin)

---

# Chapter 1: Fundamentals — The Orchestrator Mindset

## 1.1 Conductor vs. Orchestrator

Addy Osmani draws a critical distinction between two mental models for working with
AI coding agents:

**The Conductor** works synchronously with a single agent. You write a prompt, the
agent generates code, you review it, you iterate. This is how most developers use
Claude Code today — and it works well for small, focused tasks. You are personally
reviewing every line, making every decision, and maintaining full context in your head.

**The Orchestrator** works asynchronously with multiple agents. You decompose a large
task into independent subtasks, assign each to a specialized agent, review their
outputs in parallel, and synthesize the results. You stop writing code line-by-line
and start designing work packages.

The shift from conductor to orchestrator is not about writing less code — it's about
spending your cognitive budget differently. Instead of "how do I implement this
function?", you think "what are the 4 independent pieces of this feature, and how do
I verify each one passes?"

`★ Insight ─────────────────────────────────────`
**Orchestrator pattern in ParBench:** The `/validate` skill is a pure orchestrator
workflow. The main session doesn't run schema validation or security scanning itself.
It spawns 10+ specialized agents (verify-app, diff-reviewer, security-scanner, etc.),
each with a narrow focus, and only consumes their structured verdicts. The new
`verification-lead` agent takes this further — the main session spawns ONE agent,
which internally orchestrates all 10+. This is "orchestrating the orchestrator."
`─────────────────────────────────────────────────`

## 1.2 Steve Yegge's 8 Levels of AI-Assisted Development

Steve Yegge identified a progression in how developers use AI:

| Level | Description | What You Do |
|-------|-------------|-------------|
| L1 | Skeptic | Refuse to use AI tools |
| L2 | Tab completer | Accept autocomplete suggestions |
| L3 | Chat user | Ask questions, copy-paste answers |
| L4 | Prompt engineer | Write detailed prompts, iterate on output |
| L5 | Agent user | Use agent tools (Claude Code) for multi-step tasks |
| L6 | Agent customizer | Write skills, hooks, custom agents |
| L7 | Multi-agent orchestrator | Design and run agent teams |
| L8 | Autonomous loop operator | Run overnight agent loops (Ralph pattern) |

Most developers plateau at L3-L4. This guide covers L5-L8 — the levels where you
stop being a "user of AI" and start being a "designer of AI workflows." ParBench's
`.claude/` directory already has infrastructure for L6-L8: 18 custom agents, 18+
skills, 9 hooks, agent team support, and the Ralph loop pattern.

## 1.3 The 80% Problem

Osmani's core insight: **code generation is solved; code verification is the bottleneck.**

Modern LLMs can generate plausible code for ~80% of tasks. But the remaining 20% —
edge cases, integration, correctness — is where the real engineering happens. And
worse: an LLM that generates 80% correct code is not 80% useful, because the 20%
failure rate means *every* output requires human review.

The solution is not better generation — it's better verification infrastructure.
This is why ParBench invests heavily in:
- 10+ validation agents (Wave 1-4 in `/validate`)
- Pre-commit gate hooks (`.validation_passed` sentinel)
- Continuous testing (post-edit hooks)
- Adversarial self-review (self-critic agent with Opus)

The generation is "easy" — Claude writes the code. The engineering is in the
verification pipeline that catches what Claude gets wrong.

`★ Insight ─────────────────────────────────────`
**The 80% problem in ParBench's eval pipeline:** When an LLM translates CUDA to OpenMP,
the generated code compiles ~60% of the time (BUILD_FAIL rate ~40% across models).
Of the code that compiles, it produces correct output only ~50-70% of the time.
This is the 80% problem made concrete: generation looks plausible, but verification
reveals the gap. ParBench's contribution to the SC26 paper is precisely measuring
this gap across models, kernels, and directions — and showing that augmentation
(surface-level code variation) doesn't widen it (level-invariance).
`─────────────────────────────────────────────────`

## 1.4 Your Four New Hats

As an orchestrator, you wear four hats:

1. **Spec Writer** — Define WHAT should be built, not HOW. Write clear task
   descriptions, acceptance criteria, and verification commands. Your spec is your
   leverage: a vague spec multiplies errors at fleet scale (one ambiguity, 5 agents
   all interpret it differently).

2. **Orchestrator** — Decompose work into parallelizable subtasks. Assign file
   ownership. Set kill criteria. Manage the fan-out/fan-in of agent work.

3. **Quality Gate** — Review agent output. Run verification. Catch rationalization
   patterns (agent claims "all tests pass" without running tests). The self-critic
   agent helps, but YOU are the final gate.

4. **Learner** — Extract durable knowledge from each session. Update CLAUDE.md.
   Write memory files. Maintain the self-improving loop. Every mistake should make
   the system smarter, not just be fixed.

## 1.5 "Your Spec Is Your Leverage"

This is Osmani's most practical insight: the quality of your prompt/spec determines
the quality of agent output more than any other factor.

Bad spec: "Fix the failing tests."
Good spec: "The test `test_swap_condition_assignment` in `c_augmentation/test_transforms.py:142`
fails with `AssertionError: expected 'if(!fp)' but got 'if(fp == 0)'. The SwapCondition
transform in `augment_dataset.py:380` incorrectly handles assignment-in-condition patterns
like `fp = fopen(...) == 0`. Fix the transform to skip conditions containing assignment
operators."

The good spec names: the file, the line, the expected behavior, the actual behavior,
the root cause location, and the constraint (skip, don't transform). An agent given this
spec will succeed in one attempt. An agent given the bad spec will spend 5 minutes
exploring the codebase, guess at the wrong test, and produce a generic fix.

---

# Chapter 2: Claude Code Agent Primitives

Claude Code provides four fundamental building blocks for agentic workflows. Understanding
when to use each is critical — they have different cost, context, and communication
characteristics.

## 2.1 Subagents (Agent Tool)

**What:** A fire-and-forget subprocess. You describe a task, the agent runs in an
isolated context window, and returns a text summary. The agent cannot communicate
with other agents — it reports only to its parent.

**When to use:**
- Focused, single-question tasks ("count the specs in this directory")
- Tasks where a summary is sufficient (you don't need the raw data)
- Parallel independent queries (launch 3 agents, each reads a different directory)
- Validation waves (each agent runs independently, reports PASS/FAIL)

**Syntax:**
```
Agent tool call:
  description: "Count Rodinia PASS specs"
  prompt: "List all specs/rodinia-*.json files. For each, check if it's in the
           KNOWN_FAIL list. Report: N total, M KNOWN_FAIL, K eligible."
  subagent_type: "spec-auditor"  (or a custom agent name)
```

**ParBench examples:**
- Every `/validate` wave agent (verify-app, diff-reviewer, etc.)
- The explorer agent for surgical codebase investigation
- The dashboard-refresher for post-eval data regeneration

**Context cost:** Low. Only the summary text enters your context. The agent's full
context (all files it read, all commands it ran) is discarded after completion.

**Limitation:** No cross-talk. If agent A discovers something agent B needs, there's
no way for them to communicate. Agent A returns to the parent, the parent reads it,
and manually passes the info to agent B. For tasks requiring cross-talk, use Agent Teams.

## 2.2 Agent Teams (TeamCreate)

**What:** Persistent agent sessions with their own context windows, shared task lists,
and peer-to-peer messaging. Unlike subagents, teammates accumulate knowledge across
many tool calls and can message each other directly.

**When to use:**
- Tasks requiring context accumulation across many reads (a teammate reads 50+ files)
- Teammates need to discuss findings with each other (not just report to parent)
- Synthesis across multiple data sources (one teammate's findings inform another's)
- Extended analysis sessions (5-30 minutes per teammate)

**Enable:**
```json
// .claude/settings.json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```
This is already enabled in ParBench's settings.json.

**Controls:**
| Key | Action |
|-----|--------|
| `Shift+Down` | Cycle through teammates |
| `Enter` | View selected teammate's session |
| `Escape` | Return to lead |
| `Ctrl+T` | Toggle shared task list overlay |

**ParBench examples:**
- Multi-model eval deep dive (4 teammates, each reads one model's results)
- Paper assembly (3 teammates: data processor, literature scout, methodology expert)
- Failure root cause investigation (3 teammates testing competing hypotheses)

**Context cost:** High. ~Nx for N teammates (each has its own full context window).

**Limitation:** Teammates editing the same file will overwrite each other. Always
assign file ownership (one file, one owner).

## 2.3 Worktrees (EnterWorktree)

**What:** Git worktrees provide filesystem isolation. Each worktree is a separate
checkout of the repository at a specific branch/commit. Agents working in different
worktrees cannot conflict on file edits.

**When to use:**
- Feature work that needs isolation from the current workspace
- Parallel implementation of independent changes (agent A edits file X in worktree 1,
  agent B edits file Y in worktree 2)
- Code review of a branch without disturbing your working directory

**Critical ParBench constraint:**
> **NEVER run evaluations or harness commands in worktrees.**
> Git worktrees do NOT initialize submodules. The `rodinia/rodinia-src/` directory
> will be empty in any worktree, causing all specs to fail with "source not found."
> Only use worktrees for code editing and review — never for running benchmarks.

## 2.4 The Four-Layer Stack

Claude Code's customization system has four layers, each with different characteristics:

```
┌─────────────────────────────────────────────┐
│ Layer 4: AGENTS  (.claude/agents/*.md)      │  Specialized subprocesses
│   - Own context window, focused tools       │  with model + tool
│   - Spawned on demand, return verdicts      │  restrictions
├─────────────────────────────────────────────┤
│ Layer 3: HOOKS   (.claude/hooks/*.sh)       │  Deterministic automation
│   - Guaranteed execution on lifecycle       │  (not advisory — cannot
│   - PreToolUse can BLOCK (exit 2)           │  be ignored by the LLM)
│   - PostToolUse for cleanup/testing         │
├─────────────────────────────────────────────┤
│ Layer 2: SKILLS  (.claude/skills/*/SKILL.md)│  Structured workflows
│   - User-invocable via /command             │  triggered by /command
│   - Multi-step procedures with gates        │  or auto-loaded by
│   - Can spawn agents, run commands          │  file pattern matching
├─────────────────────────────────────────────┤
│ Layer 1: CLAUDE.md + .claude/rules/*.md     │  Advisory context
│   - Read by Claude, may or may not follow   │  (guidance, not
│   - Conditional loading by file patterns    │  enforcement)
│   - Project conventions, known issues       │
└─────────────────────────────────────────────┘
```

The key distinction: **CLAUDE.md is advisory** (Claude reads it and uses judgment),
**hooks are deterministic** (the shell script runs unconditionally, and exit 2 blocks
the action regardless of what Claude wants to do).

`★ Insight ─────────────────────────────────────`
**Why ParBench uses hooks for safety, not CLAUDE.md:** CLAUDE.md says "never modify
existing entries in manifest.jsonl." But an LLM can rationalize why THIS edit is an
exception. The `result-immutability.sh` hook doesn't care about rationale — it checks
the file path against a regex and exits 2 if it matches. Similarly,
`protect-benchmark-sources.sh` blocks writes to `.cu`, `.cpp`, `.c`, `.cl` files inside
benchmark directories. No amount of "but I need to fix this compilation error" overrides
the hook. This is the Trail of Bits pattern: safety-critical rules belong in
deterministic enforcement, not advisory context.
`─────────────────────────────────────────────────`

---

# Chapter 3: Skills Deep Dive

## 3.1 Anatomy of a SKILL.md

Skills live in `.claude/skills/<skill-name>/SKILL.md`. Each is a structured workflow
document that Claude loads and follows when triggered.

**Structure of a typical SKILL.md:**

```markdown
# Skill Title

Description of what the skill does and when to use it.

**Trigger:** When user types `/skill-name` with optional arguments.

## Arguments
- `$ARGUMENTS` — description of expected input

## Prerequisites
- What must be true before running (e.g., venv activated, files saved)

## Workflow

### Phase 1: Setup
[Commands to run first]

### Phase 2: Core Logic
[The main work of the skill]

### Phase 3: Report
[Structured output format]

## Context Management
[How to keep context clean — delegate reads, max output lines]
```

## 3.2 User-Invocable vs. Auto-Triggered

**User-invocable skills** are triggered by typing `/skill-name` in the prompt.
They appear in the system reminder's skill list. Examples from ParBench:

| Command | Skill | Purpose |
|---------|-------|---------|
| `/validate` | validate | 4-wave post-session validation |
| `/review` | review | Multi-agent code review |
| `/eval-run rodinia cuda-to-omp` | eval-run | Launch eval batch with pre-flight |
| `/dream` | dream | Memory consolidation |
| `/session-start 9` | session-start | Sprint session bootstrap |
| `/gen-spec xsbench` | gen-spec | Spec generation wizard |
| `/fix-bug "description"` | fix-bug | Reproduce-diagnose-fix loop |
| `/hypothesis-tree add "H: ..."` | hypothesis-tree | Structured hypothesis management |
| `/grill-research` | grill-research | Adversarial interrogation of claims |
| `/paper-review-sim` | paper-review-sim | SC/ICSE-style peer review simulation |
| `/interpret-results` | interpret-results | Hypothesis-first result interpretation |
| `/catchup` | catchup | Summarize recent changes |
| `/cite-check` | cite-check | Verify paper citations |
| `/overnight-eval rodinia` | overnight-eval | tmux-based long-running eval |
| `/agent-team` | agent-team | Agent team creation with SOPs |

**Auto-triggered skills** are loaded when Claude detects file patterns that match the
skill's description. You don't invoke them — Claude loads them based on the files
you're working with. The `.claude/rules/*.md` files work similarly, loading conditionally
based on which files are in scope.

## 3.3 Writing Effective Skill Prompts

The best skill prompts share these characteristics:

1. **Concrete bash code blocks** — Don't describe what to do abstractly. Write the exact
   commands. Claude will execute them. (See `/validate` which has copy-pasteable bash for
   every step.)

2. **Gate logic** — Each phase should have a clear pass/fail gate. If Phase 1 fails,
   don't proceed to Phase 2. The `/validate` skill gates each wave: "If ANY agent returns
   FAIL -> skip remaining waves, go to Fix Loop."

3. **Structured output format** — Define the exact output format at the end. This ensures
   consistent, parseable reports across runs. Every validation agent returns exactly the
   same format: `AGENT_NAME: PASS/FAIL` followed by structured details.

4. **Context management instructions** — Tell the skill how to handle large outputs.
   "Each agent returns max 50 lines" prevents context bloat. "Delegate bulk reads to
   Explore subagents" keeps the main context clean.

5. **Error paths** — Define what happens when things go wrong. The Fix Loop in `/validate`
   has a clear protocol: collect failures, enter plan mode, wait for approval, implement,
   re-validate, max 3 iterations.

`★ Insight ─────────────────────────────────────`
**Skills as executable documentation:** A well-written SKILL.md serves double duty —
it's both the workflow documentation AND the executable procedure. When you run
`/eval-run rodinia cuda-to-omp`, you're not following a runbook — the skill IS the
runbook. This eliminates the classic "docs drift from code" problem because the docs
ARE the code. Osmani highlights this in his web-quality-skills repo: skills should be
so precise that a new team member can run them on day one without understanding the
codebase.
`─────────────────────────────────────────────────`

## 3.4 ParBench Skill Catalog

| Skill | Phase | Key Feature |
|-------|-------|-------------|
| `/validate` | Verify | 4-wave hierarchical validation with sentinel gate |
| `/review` | Verify | 4-parallel-agent code review (style, correctness, security, perf) |
| `/eval-run` | Execute | Parameter collection, KNOWN_FAIL exclusion, post-batch analysis |
| `/dream` | Record | 4-phase memory consolidation (orient, merge, prune, update) |
| `/session-start` | Orient | Extract session prompt, check prerequisites, surface blockers |
| `/gen-spec` | Implement | Guided spec generation wizard with source exploration |
| `/fix-bug` | Implement | Reproduce -> diagnose -> fix -> verify loop |
| `/feature-dev` | Implement | Explore -> plan -> implement -> verify |
| `/hypothesis-tree` | Plan | Structured hypothesis management with falsifiability |
| `/grill-research` | Verify | Adversarial interrogation of paper claims |
| `/paper-review-sim` | Verify | Multi-reviewer simulation (SC/ICSE style) |
| `/interpret-results` | Analyze | Hypothesis-first result interpretation |
| `/overnight-eval` | Execute | tmux-based long-running eval with monitoring |
| `/catchup` | Orient | Summarize recent git/result changes |
| `/cite-check` | Verify | Check paper citations against source data |
| `/agent-team` | Execute | Agent team creation with SOPs and scenario templates |
| `/augment-test` | Verify | Augmentation testing workflow |
| `/techdebt` | Analyze | Tech debt scanning and cataloging |
| `/reflect` | Record | Structured reflection after task completion |
| `/spec-check` | Verify | Declarative spec verification |
| `/post-eval` | Analyze | Post-eval pipeline (analyze, classify, dashboard refresh) |
| `/model-route` | Plan | Model routing advisor (Opus/Sonnet/Haiku recommendations) |
| `/ralph-loop` | Execute | Stateless iterative task execution (overnight loops) |

---

# Chapter 4: Hooks Deep Dive

Hooks are shell scripts that execute automatically at specific points in Claude Code's
lifecycle. Unlike CLAUDE.md (advisory), hooks are **deterministic** — they run unconditionally
and their exit codes have hard consequences.

## 4.1 Hook Types and Purposes

### PreToolUse — Safety Gates

Runs BEFORE a tool executes. Can BLOCK the action (exit 2).

**When to use:** Preventing dangerous operations — deleting protected files, committing
without validation, writing to read-only directories.

**Key behavior:**
- Exit 0 = allow the tool to proceed
- Exit 2 = BLOCK the tool (stderr is shown to Claude as an error message)
- stdin = JSON with tool input data
- stdout = shown to Claude
- stderr = shown to Claude on exit 2, logged only on exit 0

### PostToolUse — Continuous Automation

Runs AFTER a tool executes. Cannot block (always exit 0).

**When to use:** Auto-formatting, cleanup, invalidating cached state, running tests.

**Key behavior:**
- Exit 0 = always (PostToolUse hooks are advisory, never blocking)
- stdin = JSON with tool input + tool output data
- stdout = shown to Claude
- stderr = logged only (not shown to Claude)

### Stop — Pre-Completion Checklists

Runs when Claude is about to stop responding. Used for checklists and reminders.

**When to use:** Anti-rationalization checklists ("did you actually run /validate?"),
cleanup tasks, notifications.

### Notification — Event-Driven Alerts

Runs on specific events (background task completion, etc.).

**When to use:** Desktop notifications, logging, status updates.

## 4.2 settings.json Hook Configuration

Hooks are configured in `.claude/settings.json` under the `hooks` key:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/hook-script.sh",
            "timeout": 10
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/another-hook.sh",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "inline shell command here"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'reminder text' >&2; exit 0"
          }
        ]
      }
    ]
  }
}
```

**Matcher patterns:** The `matcher` field determines which tool triggers the hook.
- `"Bash"` — matches Bash tool calls
- `"Edit|Write"` — matches Edit OR Write tool calls
- `"Compact"` — matches the Compact operation
- Omitted matcher (in Stop hooks) — runs unconditionally

**Timeout:** Maximum milliseconds the hook can run. Default varies by hook type.
Keep hooks fast (under 10 seconds) to avoid blocking the workflow.

## 4.3 Hook Input Protocol

Hooks receive a JSON object on stdin with the tool input:
```json
{
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/home/samyak/Desktop/parbench_sam/specs/rodinia-bfs-cuda.json",
    "old_string": "...",
    "new_string": "..."
  }
}
```

The `CLAUDE_TOOL_INPUT` environment variable also contains the JSON. You can parse it
with Python or jq:

```bash
# Python parsing (preferred — handles edge cases)
FILE_PATH=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('file_path', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

# Simple grep (for bash-only hooks)
echo "$CLAUDE_TOOL_INPUT" | grep -oP '"command"\s*:\s*"\K[^"]*'
```

## 4.4 ParBench Hook Catalog

### Safety Hooks (PreToolUse)

| Hook | Matcher | Purpose | Blocks On |
|------|---------|---------|-----------|
| `pre-commit-gate.sh` | Bash | Blocks `git commit` without validation | Missing/stale `.validation_passed` sentinel |
| `protect-benchmark-sources.sh` | Edit\|Write | Blocks edits to benchmark `.cu/.cpp/.c/.cl` files | File inside `rodinia/`, `HeCBench-master/`, `xsbench-src/` |
| `protect-cuda-omp-results.sh` | Bash | Blocks deletion/overwrite of CUDA-OMP results | `rm` in `results/evaluation/` matching `*cuda*omp*` |
| `result-immutability.sh` | Edit\|Write | Blocks overwriting existing result JSONs | Existing file in `results/evaluation/*.json` |
| `rm -rf` inline blocker | Bash | Blocks destructive deletions | Any `rm -rf` or `rm -fr` command |
| `file-ownership.sh` | Edit\|Write | Blocks edits to files owned by another teammate | File assigned to a different teammate in agent teams |

### Automation Hooks (PostToolUse)

| Hook | Matcher | Purpose | Effect |
|------|---------|---------|--------|
| `post-edit-test.sh` | Edit\|Write | Runs lightweight tests after edits | Executes tests based on edited file path |
| `context-budget.sh` | Bash | Tracks tool calls and context usage | Nudges for `/compact` at usage thresholds |
| `sentinel-cleanup.sh` | Edit\|Write | Invalidates validation after edits | Deletes `.validation_passed` if it exists |
| Ruff auto-lint (inline) | Edit\|Write | Auto-formats Python files | Runs `ruff check --fix` on `.py` files |
| `post-compact-recovery.sh` | Compact | Recovers context after compaction | Restores essential context references |
| `bash-audit-log.sh` | Bash | Logs all bash commands | Appends to audit log |

### Lifecycle Hooks (Stop)

| Hook | Purpose | Effect |
|------|---------|--------|
| Pre-stop checklist (inline) | Anti-rationalization | Reminds Claude to check: /validate run, tasks finished, evidence for claims |
| `dream-hook.sh` | Memory hygiene | Checks if memory consolidation is due |
| Desktop notification (inline) | Alert | `notify-send` on Linux when Claude stops |

`★ Insight ─────────────────────────────────────`
**Hooks as a verification flywheel:** ParBench's hooks create a self-reinforcing
quality loop. The sentinel-cleanup hook deletes `.validation_passed` whenever ANY
file is edited. The pre-commit-gate hook blocks commits without that sentinel. The
Stop hook reminds Claude to run `/validate`. Together, they make it structurally
impossible to commit unvalidated changes — even if Claude rationalizes "this small
change doesn't need validation." This is defense in depth: multiple independent
mechanisms all pointing toward the same behavior (validate before commit). Breaking
any single hook doesn't break the system, because the others catch it.
`─────────────────────────────────────────────────`

## 4.5 Writing Your Own Hooks

Template for a PreToolUse blocking hook:

```bash
#!/usr/bin/env bash
# my-hook.sh — PreToolUse hook
# Purpose: [one-line description]
# Matcher: [which tool this hooks into]
# Exit 0 = allow, Exit 2 = BLOCK

set -euo pipefail

# Read hook event JSON from stdin
INPUT=$(cat)

# Extract relevant field from tool input
VALUE=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('command', '') or ti.get('file_path', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

# Guard: if no value extracted, allow (fail-open for safety)
if [ -z "$VALUE" ]; then
    exit 0
fi

# Your blocking logic here
if echo "$VALUE" | grep -qE 'pattern_to_block'; then
    echo "BLOCKED: Reason for blocking" >&2
    echo "  Suggestion for alternative approach" >&2
    exit 2
fi

# All checks passed — allow
exit 0
```

**Key practices:**
1. Always `set -euo pipefail` for strict error handling
2. Consume stdin completely (prevent SIGPIPE errors)
3. Fail-open: if you can't parse the input, exit 0 (allow)
4. Keep hooks under 5 seconds — they run on every tool call
5. Write clear error messages to stderr (shown to Claude on exit 2)
6. Make the hook executable: `chmod +x .claude/hooks/my-hook.sh`

---

# Chapter 5: Custom Agents Deep Dive

## 5.1 Agent Definition Files

Custom agents live in `.claude/agents/<agent-name>.md`. Each is a markdown file with
YAML frontmatter that defines the agent's capabilities, followed by a body that describes
its task and output format.

## 5.2 YAML Frontmatter Fields

```yaml
---
name: agent-name           # Lowercase, kebab-case identifier
description: "..."         # One-line description (used for agent selection)
tools: Bash, Read, Glob, Grep  # Comma-separated list of allowed tools
model: opus                # Model to use (always opus for ParBench)
effort: max                # Thinking effort level (optional)
maxTurns: 20               # Maximum tool call iterations
permissionMode: dontAsk    # Optional: skip permission prompts
background: true           # Optional: run in background
---
```

**Field details:**

- **tools:** The agent can ONLY use tools listed here. This is a security and focus
  mechanism. A read-only agent gets `Read, Glob, Grep` (no Bash, no Edit). A
  verification agent gets `Bash, Read, Glob` (can run commands but can't edit files).
  The `Agent` tool lets an agent spawn sub-agents of its own (hierarchical pattern).

- **model:** ParBench policy is always `opus`. The `sonnet` model is faster/cheaper
  but less capable at complex reasoning. Self-critic and plan-reviewer use `opus`
  because adversarial review requires the highest reasoning depth.

- **effort:** `max` enables maximum thinking depth. Use for agents that need deep
  analysis (self-critic, plan-reviewer, paper-drafter). Omit for simpler agents
  (diff-reviewer, regression-checker).

- **maxTurns:** How many tool calls the agent can make. Set this based on task
  complexity: 15 for simple verification, 20-25 for exploration, 30-40 for
  hierarchical agents that spawn sub-agents.

- **permissionMode:** `dontAsk` skips permission prompts for this agent's tool calls.
  Use for trusted agents in the validation pipeline where prompting would break the
  automated flow.

## 5.3 Agent Body Design

The body follows a consistent pattern across ParBench agents:

```markdown
# Agent Name

One-paragraph description of role and purpose.

## Setup (ALWAYS run first)
[bash code block — activate venv, cd to project root]

## Step/Check/Audit N: Description
[bash code block — the actual work]
[Instructions for interpreting results]

## Output Format (max 50 lines)
[Exact template for structured output]
```

**Design principles:**

1. **Setup block first** — Always activate the venv and cd to project root. Agents
   start with no state.

2. **Concrete bash commands** — Don't tell the agent what to do abstractly. Give it
   the exact commands. The spec-auditor doesn't say "validate the spec" — it says
   `python3 scripts/validate_schema.py --spec specs/<name>.json`.

3. **Output format at the end** — Define the exact output structure. This is critical
   for the parent to parse results. Every validation agent uses the same pattern:
   `AGENT_NAME: PASS/FAIL` followed by numbered check results.

4. **50-line output cap** — Keeps the parent context clean. An agent that dumps 200
   lines of test output into the main session is wasting context budget. Agents
   should summarize internally and return only the verdict.

## 5.4 ParBench Agent Catalog

### Validation Agents (used by /validate)

| Agent | Wave | Model | Purpose |
|-------|------|-------|---------|
| `verify-app` | 1 | sonnet | Schema validation, unit tests, spec integrity, manifest check |
| `diff-reviewer` | 1 | sonnet | Git diff analysis for regressions and partial implementations |
| `security-scanner` | 1 | sonnet | Secrets, injection, unsafe patterns in changed files |
| `test-synthesizer` | 2 | sonnet | Writes + runs temporary tests for changed code |
| `regression-checker` | 2 | sonnet | Before/after metric comparison against baselines |
| `spec-auditor` | 2 | sonnet | Full spec JSON audit (conditional — only when specs changed) |
| `consistency-checker` | 3 | sonnet | Documentation vs code cross-check |
| `code-simplifier` | 3 | sonnet | Code quality advisory (non-blocking) |
| `self-critic` | 4 | opus | Adversarial self-review, rationalization detection |
| `plan-reviewer` | 4 | opus | Adversarial plan review (conditional — after fix loop) |

### Orchestration Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `verification-lead` | opus | Hierarchical validation coordinator (spawns all wave agents internally) |
| `paper-assembly-team` | opus | SC26 paper data gathering with 3 parallel sub-agents |

### Domain Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `rodinia-verifier` | sonnet | Harness verify on all Rodinia specs, reports PASS/FAIL table |
| `xsbench-explorer` | opus | Explores XSBench source for spec generation |
| `eval-batcher` | sonnet | Runs LLM evaluation batches with kernel eligibility rules |
| `paper-drafter` | opus | Writes SC26 paper sections from actual data |
| `dashboard-refresher` | sonnet | Regenerates visualization data and fixes stale HTML values |
| `explorer` | sonnet | General codebase exploration specialist |

## 5.5 Osmani's Hierarchical Pattern

Osmani recommends a "teams of teams" structure for complex orchestration:

```
Main Session
  └── verification-lead (1 agent)
        ├── Wave 1 (3 agents in parallel)
        │     ├── verify-app
        │     ├── diff-reviewer
        │     └── security-scanner
        ├── Wave 2 (2-3 agents in parallel)
        │     ├── test-synthesizer
        │     ├── regression-checker
        │     └── spec-auditor (conditional)
        ├── Wave 3 (2 agents in parallel)
        │     ├── consistency-checker
        │     └── code-simplifier
        └── Wave 4 (1-2 agents sequential)
              ├── self-critic
              └── plan-reviewer (conditional)
```

The main session spawns ONE agent (verification-lead), which internally manages 10+
sub-agents across 4 waves. The main session's context cost: ~60 lines (one report).
Without this pattern, the same validation would dump ~500 lines (10+ agent summaries)
into the main context.

`★ Insight ─────────────────────────────────────`
**Hierarchical agents as context management:** The verification-lead agent isn't just
a convenience — it's a context budget optimization. Claude Code's context window is
~200K tokens. A main session that has been implementing features for an hour might
already be at 50% context usage. Dumping 10+ agent summaries (each 50 lines = 500+
lines) pushes toward compaction. But routing through verification-lead costs only ~60
lines in the main context. The sub-agents' full contexts (all the files they read, all
the commands they ran) are fully encapsulated. This is the same principle as
microservice boundaries in distributed systems: each service manages its own state,
and only structured messages cross boundaries.
`─────────────────────────────────────────────────`

---

# Chapter 6: The Ralph Loop Pattern

## 6.1 Origin and Concept

The Ralph Loop pattern was developed by Geoffrey Huntley and Ryan Carson, popularized
by Addy Osmani at CodeCon 2026. Named after the autonomous loop behavior: Claude picks
a task, implements it, validates it, commits it, resets context, and picks the next task.

The key insight: **context resets between tasks are a feature, not a limitation.** Each
task gets a fresh 200K-token context window, preventing the context rot that degrades
quality in long sessions. The loop is durable across resets because state is persisted
in four channels (see below).

## 6.2 Core Cycle

```
                    ┌──────────────────┐
                    │  Read tasks.json │
                    │  Pick next task  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Implement      │
                    │   (code changes) │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Validate       │
                    │   (/validate)    │
                    └────────┬─────────┘
                             │
                    ┌────────▼────────┐         ┌──────────────────┐
                    │   PASS?         │── No ──▶│ Feed error back  │
                    └────────┬────────┘         │ Auto-retry       │
                             │ Yes              │ (max 3 attempts) │
                    ┌────────▼─────────┐        └──────────────────┘
                    │   Commit         │
                    │   (git commit)   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Update state   │
                    │   Reset context  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Next task      │
                    │   or STOP        │
                    └──────────────────┘
```

## 6.3 Four Memory Channels

The loop persists across context resets using four durable channels:

1. **Git commit history** — Each completed task results in a commit. On the next
   iteration, `git log --oneline -10` tells the loop what was already done.
   ```bash
   git log --oneline -10  # "Fixed srad args" → srad is done, skip it
   ```

2. **Progress log** (`docs/ralph-progress.md`) — Append-only log of actions taken,
   decisions made, and errors encountered. Survives context resets because it's on disk.
   ```markdown
   ## Iteration 3 — 2026-04-01T03:42Z
   Task: Fix rodinia-nw-omp run args
   Result: PASS — argc check at needle.cpp:249 requires 3 args
   Commit: a1b2c3d
   ```

3. **Task state** (`tasks.json`) — JSON file tracking task lifecycle:
   ```json
   [
     {"id": 1, "subject": "Fix nw-omp args", "status": "done"},
     {"id": 2, "subject": "Fix hotspot-omp args", "status": "in_progress"},
     {"id": 3, "subject": "Update dashboard", "status": "pending"}
   ]
   ```

4. **CLAUDE.md** — Long-term semantic memory. Updated with new gotchas discovered
   during the loop. Unlike the other three channels, CLAUDE.md is read at session
   start, not per-iteration.

## 6.4 Kill Criteria

Without kill criteria, an autonomous loop will burn tokens indefinitely on a stuck task:

- **MAX_ITERATIONS = 8** — Hard stop after 8 iterations (tasks or retries).
- **Forced reflection every 3 iterations** — The loop pauses and writes a reflection
  entry to the progress log: "What's going well? What's stuck? Should I continue?"
- **Stuck detection** — If the same task fails 3 consecutive times, mark it as `blocked`
  and move to the next task. Don't burn 200K tokens on a task that needs human judgment.
- **Token budget** — Each iteration should stay under the context window. If a task
  requires reading 50+ files, it's too large for the loop — break it up.

## 6.5 Safety Constraints

The Ralph loop runs unsupervised. Safety is paramount:

- **Feature branch only** — Never run on `main`. Create a feature branch before starting.
- **Sandbox execution** — All hook protections still apply (benchmark sources, result
  immutability, etc.). The loop cannot delete files, overwrite results, or modify
  protected directories.
- **No force push** — The `permissions.deny` list in settings.json blocks
  `git push --force` and `git reset --hard` for all sessions, including the loop.
- **Hard token limit** — The loop should not exceed a configured total token budget
  across all iterations.

## 6.6 Overnight Execution with tmux

The Ralph loop is designed for overnight runs on the GPU machine:

```bash
# Start the loop in a detached tmux session
tmux new -d -s ralph 'claude --print "/ralph-loop tasks.json"'

# Check progress in the morning
tmux attach -t ralph

# Or check the progress log without attaching
cat docs/ralph-progress.md
```

## 6.7 Self-Healing

When a task fails, the loop doesn't just retry — it feeds the error back:

```
Iteration 4: Task "Fix hotspot-omp args"
  → BUILD_FAIL: undefined reference to `omp_get_wtime`
  → Error fed back: "Add -lrt to linker flags"
  → Retry: modified Makefile, added -lrt
  → PASS on retry 2
```

But if the same error persists for 3 retries, the loop stops self-healing and marks
the task as `blocked`:

```json
{"id": 2, "subject": "Fix hotspot-omp args", "status": "blocked",
 "blocked_reason": "BUILD_FAIL persists after 3 retries — needs manual investigation"}
```

`★ Insight ─────────────────────────────────────`
**Ralph loop and the research workflow:** The Ralph pattern is especially powerful for
ParBench's eval pipeline. After defining tasks like "run cuda-to-omp evaluation for
models X, Y, Z at levels L0-L2", the loop can execute each eval batch, run
`analyze_eval.py`, update the dashboard, and commit — all overnight. By morning, you
have a complete set of results with git history showing exactly what was run when.
This is the ARIS (Auto-Research-In-Sleep) pattern applied to benchmark evaluation.
The 8-iteration kill and 3-retry stuck detection ensure the loop doesn't burn your
API budget on a single stuck kernel.
`─────────────────────────────────────────────────`

---

# Chapter 7: Agent Teams in Practice

## 7.1 Enabling Agent Teams

Agent teams are an experimental Claude Code feature. Enable them in settings.json:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

This is already set in ParBench's `.claude/settings.json`.

## 7.2 Team Composition

The sweet spot is 3-5 teammates plus the lead. Each teammate should have:

- **A clear role** — "Claude results analyst", not "helper"
- **Non-overlapping file scope** — No two teammates edit the same file
- **Explicit IN SCOPE / OUT OF SCOPE** — Prevents context rot from reading irrelevant files
- **A model assignment** — Always `opus` for ParBench

Osmani's recommended structure:
```
Lead (you or the team lead agent)
  ├── Implementer 1 (owns files A, B, C)
  ├── Implementer 2 (owns files D, E, F)
  ├── Implementer 3 (owns files G, H, I)
  └── Critic (read-only, reviews all changes)
```

## 7.3 The Critic Teammate Pattern

Every ParBench agent team must include a critic. The critic:

1. **Is read-only** — Never edits files. Only reads and sends feedback.
2. **Uses Opus** — Adversarial review requires the highest reasoning depth.
3. **Reviews each deliverable** — After an implementer finishes a task, the critic
   reviews it BEFORE the team moves on.
4. **Sends feedback via SendMessage** — Direct to the implementer, not through the lead.
5. **One critic per 3-4 builders** — More critics add overhead without proportional value.

The implementer+critic loop:
```
Implementer completes task
  → Critic reviews
    → If issues found: Critic sends feedback to Implementer
      → Implementer fixes
        → Critic re-reviews
    → If clean: Critic approves, team moves to next task
```

## 7.4 Shared Task List

Agent teams use a shared task list visible to all teammates:

- **TaskCreate** — Create a new task (lead usually creates, teammates can too)
- **TaskUpdate** — Update status: `pending` -> `in_progress` -> `completed`
- **TaskList** — View all tasks and their statuses
- **Ctrl+T** — Toggle task list overlay in the terminal UI
- **addBlockedBy** — Set task dependencies (task 3 blocked by tasks 1 and 2)

Example workflow:
```
Lead creates tasks:
  #1: "Read eval results for claude-sonnet" → assigned to claude-analyst
  #2: "Read eval results for gemini" → assigned to gemini-analyst
  #3: "Compare results" → blocked by #1 and #2, assigned to comparator

claude-analyst and gemini-analyst work in parallel.
When both complete, comparator is automatically unblocked.
```

## 7.5 Peer-to-Peer Messaging

Teammates communicate via `SendMessage`:

```
SendMessage(to="gemini-analyst", message="Found 0% pass rate on cuda-to-opencl.
Can you check if Gemini shows the same pattern?")
```

- Direct messaging: `to: "teammate-name"` — Only that teammate sees it
- Broadcast: `to: "*"` — All teammates see it (use sparingly, linear cost)
- Messages from teammates are delivered automatically — no inbox polling

## 7.6 File Ownership and Locking

The "one file, one owner" rule prevents overwrite conflicts:

- When designing a team, assign each file to exactly one teammate
- Include file scope in each teammate's prompt (IN SCOPE / OUT OF SCOPE)
- The `file-ownership.sh` hook (when enabled) enforces this at the tool level

Example from the paper-assembly scenario:
```
data-processor  owns: results/evaluation/ (read-only)
lit-reviewer    owns: WebSearch (no files)
methods-reader  owns: c_augmentation/, harness/ (read-only)
```

No overlap = no conflicts.

## 7.7 When Teams Beat Subagents

| Criterion | Use Subagents | Use Agent Teams |
|-----------|--------------|----------------|
| Context accumulation needed | No (summary sufficient) | Yes (many reads, builds up state) |
| Cross-talk needed | No (report to parent only) | Yes (teammates discuss) |
| Synthesis across sources | No (each agent independent) | Yes (one agent's findings inform another) |
| Duration | Short (~30s-2min) | Extended (~5-30min per teammate) |
| Token cost | Lower (summaries only) | Higher (~Nx for N teammates) |
| Task structure | Structured, independent | Requires coordination |

**Subagents win for:** `/validate` waves, `/review`, single-file exploration, quick checks.
**Teams win for:** Multi-model analysis, paper assembly, failure investigation, overnight work.

## 7.8 Pre-Built Scenario Templates

ParBench's `/agent-team` skill includes 6 pre-built scenarios:

| Scenario | Teammates | Purpose |
|----------|-----------|---------|
| `multi-model-eval` | 4 | Compare results across model directories |
| `paper-assembly` | 3 | Parallel data gathering for SC26 paper |
| `failure-investigation` | 3 | Multi-stage pipeline debugging for a kernel |
| `cross-model-taxonomy` | 4 | Build unified failure taxonomy table |
| `post-batch-analysis` | 3 | Post-eval analysis pipeline |
| `augmentation-audit` | 4 | Verify augmentation level-invariance claim |

Launch with: `/agent-team --scenario multi-model-eval`

`★ Insight ─────────────────────────────────────`
**Agent teams as parallel research assistants:** The multi-model-eval scenario is a
direct implementation of the ARIS pattern. Instead of one researcher reading 400+
result files sequentially (burning through the context window), four teammates each
read ~100 files in parallel, build summaries, and then a comparator synthesizes the
findings. The total token cost is ~4x, but the wall-clock time is ~1/4 and the
quality is higher because each teammate maintains focused context on its model's
results. This is the "divide and conquer" of context management — specialized contexts
produce better reasoning than one overloaded context trying to hold everything.
`─────────────────────────────────────────────────`

---

# Chapter 8: Quality Gates

## 8.1 Osmani's Three-Tier Quality System

Osmani identifies three tiers of quality enforcement, ordered by increasing reliability:

### Tier 1: Plan Approval (Human Gate)

Before any non-trivial implementation:
1. Claude enters plan mode
2. Presents the plan to the user
3. User approves, requests changes, or rejects
4. Implementation only proceeds after explicit approval

In ParBench, this is enforced by workflow.md: "Wait for user approval before
implementing" and the `/agent-team` skill: "Wait for Samyak's approval — do not
create the team until approved."

### Tier 2: Hooks (Automated Gate)

Lifecycle hooks that run deterministically on every tool call:
- `pre-commit-gate.sh` blocks commits without validation
- `protect-benchmark-sources.sh` blocks edits to benchmark code
- `result-immutability.sh` blocks overwriting existing results
- `sentinel-cleanup.sh` invalidates validation after any file edit

These cannot be rationalized away. An LLM cannot argue "this edit is safe" if
the hook exits 2.

### Tier 3: CLAUDE.md / Agents (Advisory Gate)

CLAUDE.md rules, custom agent instructions, and memory files guide behavior but
can be overridden by Claude's judgment. This is the weakest tier — useful for
conventions and preferences, but not for safety-critical rules.

**The principle:** Safety-critical rules go in hooks (Tier 2). Conventions and
preferences go in CLAUDE.md (Tier 3). Strategic decisions go through plan approval
(Tier 1).

## 8.2 ParBench's 4-Wave Validation System

The gold standard for quality enforcement in ParBench. Run via `/validate` or
through the `verification-lead` agent.

```
Wave 1 (Fast, ~30s) — "Does it even work?"
  ├── verify-app:       Schema + unit tests + spec integrity + manifest
  ├── diff-reviewer:    Partial impls, accidental changes, removed tests
  └── security-scanner: Secrets, injection, unsafe patterns

Wave 2 (Deep, ~60s) — "Does it work correctly?"
  ├── test-synthesizer:   Runtime test synthesis for changed code
  ├── regression-checker: Metric comparison against baselines
  └── spec-auditor:       Full spec audit (conditional)

Wave 3 (Cross-check, ~45s) — "Is it consistent?"
  ├── consistency-checker: Docs vs code cross-check
  └── code-simplifier:    Quality advisory (non-blocking)

Wave 4 (Adversarial, ~30s) — "Did Claude cut corners?"
  ├── self-critic:    Rationalization patterns, incomplete work
  └── plan-reviewer:  Fix plan review (conditional)
```

**Wave gating:** Each wave must PASS before the next begins. If Wave 1 fails,
Waves 2-4 don't run — no point in deep analysis if schema validation fails.

**Fix loop:** On failure, the system enters a fix loop:
1. Collect all FAIL verdicts
2. Enter plan mode with targeted fixes
3. Wait for user approval
4. Implement fixes (targeted only — no scope creep)
5. Re-validate (failed wave + downstream only)
6. Max 3 iterations before escalating to user

## 8.3 Continuous Verification

Beyond the 4-wave system, ParBench has continuous verification hooks that catch
errors as they're introduced — not just at commit time:

- **Post-edit Ruff lint** — Every Python file is auto-linted after editing
  (PostToolUse hook on Edit|Write with `.py` filter)
- **Sentinel invalidation** — Every file edit deletes `.validation_passed`,
  requiring re-validation before the next commit

## 8.4 The Pre-Commit Gate

The `.validation_passed` sentinel is the single authority on commit readiness:

```
                      ┌─────────────────┐
                      │  /validate      │
                      │  (all 4 waves)  │
                      └────────┬────────┘
                               │ PASS
                      ┌────────▼────────┐
                      │  Write sentinel │
                      │  .validation_   │
                      │  passed         │
                      └────────┬────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
    ┌───────▼───────┐  ┌──────▼──────┐   ┌───────▼────────┐
    │  Edit a file  │  │  git commit │   │  30 min pass   │
    │  (any file)   │  │             │   │  (TTL expires)  │
    └───────┬───────┘  └──────┬──────┘   └───────┬────────┘
            │                 │                   │
    ┌───────▼───────┐  ┌─────▼──────┐   ┌───────▼────────┐
    │  sentinel     │  │  Hook      │   │  Hook checks   │
    │  DELETED      │  │  checks:   │   │  age > 1800s   │
    │  (cleanup     │  │  exists?   │   │  → BLOCKED     │
    │   hook)       │  │  fresh?    │   └────────────────┘
    └───────────────┘  │  4 waves?  │
                       └─────┬──────┘
                             │ All yes
                       ┌─────▼──────┐
                       │  COMMIT    │
                       │  ALLOWED   │
                       └────────────┘
```

The pre-commit-gate.sh hook checks:
1. Sentinel exists
2. Sentinel is less than 30 minutes old (not stale)
3. Sentinel records `waves_passed=4` (not just `/validate quick`)
4. No files were modified after the sentinel was written

## 8.5 The REFLECTION.md Pattern

After every completed task, capture structured learning:

```markdown
## Reflection: [Task Name] — [Date]

### What surprised me?
- [Something unexpected that the agents found or that broke]

### Pattern proposal
- [A new pattern, rule, or hook that would prevent this issue in the future]

### Prompt improvement
- [How to write a better spec/prompt for similar tasks next time]
```

This feeds the self-improving loop (Chapter 9): reflections become memory files,
which become CLAUDE.md updates, which become better agent behavior.

## 8.6 Anti-Patterns in Quality Gates

From Osmani's experience and ParBench's history:

1. **LLM-written CLAUDE.md** — Letting Claude write its own instructions reduces
   success rates by 2-3%. CLAUDE.md should always be human-curated. (The system
   can propose changes via reflection, but a human approves.)

2. **No kill criteria** — Without MAX_ITERATIONS or stuck detection, a validation
   loop burns tokens indefinitely on an unfixable issue.

3. **Hovering** — Checking agent progress every 30 seconds defeats the async model.
   Trust the gates. Check every 5-10 minutes.

4. **Skipping validation** — "This is just a docs change" is how bugs sneak through.
   The pre-commit gate exists for a reason. If validation truly doesn't apply, use
   `[skip-validate: reason]` in the commit message.

---

# Chapter 9: The Self-Improving Codebase

## 9.1 CLAUDE.md Curation

Osmani's discoverability filter: **"Can an agent find this by reading the code?"**

If yes, it doesn't belong in CLAUDE.md. File structure, function signatures, import
paths — these are discoverable by reading the code. CLAUDE.md should contain only:

- **Non-obvious constraints** — "~135 validation errors are expected" (you'd never guess this from the code)
- **Historical context** — "This was changed because of incident X" (not in git log)
- **Cross-cutting rules** — "Never modify existing manifest entries" (applies everywhere)
- **Environment setup** — "NVIDIA HPC SDK is at /opt/nvidia/..." (not in any config file)

ParBench's CLAUDE.md stays under 60 lines. Everything else lives in `.claude/rules/`
(conditional loading by file pattern), `.claude/agents/` (agent-specific context),
or memory files (session-to-session persistence).

## 9.2 Conditional Context Loading

`.claude/rules/*.md` files load automatically when Claude is working with matching files:

| Rule File | Triggers On | Content |
|-----------|------------|---------|
| `known-issues.md` | Always | KNOWN_FAIL specs, build gotchas, spec status |
| `workflow.md` | Always | 6-stage workflow, agent patterns, anti-patterns |
| `mentoring` skill | On-demand (`/mentoring`) | HPC/SE/research teaching framework |
| `spec-conventions.md` | `specs/`, `manifest.jsonl` | Naming rules, run arg verification |
| `evaluation.md` | `scripts/evaluation/` | `--suite` required, result schema |
| `augmentation.md` | `c_augmentation/` | `--project-root` required, transform bugs |
| `python.md` | `*.py` | `python3`, CLI flag ordering |
| `validation-loop.md` | hooks, validation agents | 4-wave protocol, sentinel mechanics |
| `known-issues-archive.md` | `c_augmentation/`, `harness/`, `scripts/`, `results/`, `specs/`, `visualizations/` | Historical fix details, moved guardrails |
| `github-pages.md` | `visualizations/` | URL, staticrypt, data refresh |
| `frontend-design.md` | `visualizations/` | Design system, styling conventions |

This is a scalable alternative to putting everything in CLAUDE.md. Rules files can be
verbose (known-issues.md is ~200 lines) because they only load when relevant.

## 9.3 Memory System

Auto-memory files live in `~/.claude/projects/-home-samyak-Desktop-parbench-sam/memory/`.
They persist across conversations, building up an understanding of the user, project,
and workflow preferences.

**Memory types:**

| Type | Purpose | Example |
|------|---------|---------|
| `user` | User's role, preferences, knowledge | "PhD candidate, HPC/SE/AI intersection" |
| `feedback` | Corrections and validated approaches | "Always Opus, never Sonnet" |
| `project` | Ongoing work, goals, deadlines | "SC26 paper deadline April 8" |
| `reference` | Pointers to external resources | "Pipeline bugs tracked in Linear project INGEST" |

**Memory lifecycle:**
1. Something noteworthy happens in a conversation
2. Claude writes a memory file with frontmatter (name, description, type)
3. Claude adds a one-line pointer to `MEMORY.md` (the index)
4. Future conversations read `MEMORY.md` and load relevant memory files
5. `/dream` consolidation periodically merges, prunes, and updates memories

**What NOT to save:** Code patterns (read the code), git history (use `git log`),
debugging recipes (the fix is in the code), anything in CLAUDE.md (don't duplicate).

## 9.4 The /dream Consolidation Cycle

Memory files grow but never get maintained — they become stale, duplicated, and
contradictory. The `/dream` skill performs periodic consolidation:

```
Phase 1: Orient — Read all memory files, catalog by type and staleness
Phase 2: Analyze — Find duplicates, contradictions, stale entries
Phase 3: Consolidate — Merge overlapping memories, prune stale ones
Phase 4: Update — Write cleaned files, update MEMORY.md index
```

**When to consolidate:**
- After major milestones (sprint completion, eval batch, paper draft)
- After 5+ sessions without consolidation
- Before long breaks (>3 days between sessions)
- When `/session-start` reports memory staleness

## 9.5 Maintaining Comprehension

Osmani's strongest warning:

> "If your ability to read doesn't scale with the agent's ability to output,
> you aren't engineering anymore — you're rubber-stamping."

The self-improving loop only works if YOU understand what the system is doing.
Strategies for maintaining comprehension:

1. **Alternate manual coding** — Don't use agents for everything. Write some code
   yourself to stay sharp on the codebase. If you can't write a spec JSON from
   memory, you've lost too much context.

2. **Request justifications** — Don't just accept agent output. Ask "why did you
   choose this approach?" or "what alternatives did you consider?" The self-critic
   agent does this automatically, but you should too.

3. **Use TDD** — Write the test first, then let the agent write the implementation.
   You control the spec (what should happen), the agent handles the implementation
   (how it happens). You can verify by running the test.

4. **Review diffs, not files** — `git diff` shows exactly what changed. Reading the
   full file after an agent edit is slower and less focused than reading the diff.

`★ Insight ─────────────────────────────────────`
**Comprehension debt is real:** ParBench has 18 custom agents, 18+ skills, and 9 hooks.
If you can't explain what each does from memory, you have comprehension debt. The
quick reference card (Chapter 12) exists to help, but it's not a substitute for
understanding. When an agent team produces unexpected results, your ability to debug
depends on understanding the team structure, the agent prompts, and the hook
interactions. Invest time in reading agent definitions, not just running them.
`─────────────────────────────────────────────────`

---

# Chapter 10: Recipes — Common ParBench Workflows

## Recipe 1: Run an Eval Batch and Process Results

```bash
# 1. Launch the eval batch with pre-flight checks
/eval-run rodinia cuda-to-omp --model claude-sonnet-4-6

# 2. Wait for completion (or use tmux for overnight runs)
# The skill handles API key verification, KNOWN_FAIL exclusion,
# and --resume to protect existing results

# 3. After completion, run post-eval analysis
# analyze_eval.py generates eval_summary.json
# generate_viz_data.py updates dashboard data files
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard --show-gaps

# 4. Refresh dashboard
# Use the dashboard-refresher agent (or run manually)
python3 scripts/generate_viz_data.py \
  --project-root /home/samyak/Desktop/parbench_sam -v

# 5. Reflect on what you learned
/reflect "eval batch results — note any surprising failures"

# 6. Validate and commit
/validate
git add results/evaluation/ visualizations/
git commit -m "Add cuda-to-omp eval results for claude-sonnet"
```

## Recipe 2: Add a New Benchmark Suite

```bash
# 1. Use the spec generation wizard
/gen-spec newsuite

# Follow the interactive wizard:
# - It explores source directories
# - Reads Makefiles for build commands
# - Reads main() for argc parsing (run args)
# - Reads reference output for verify patterns
# - Generates spec JSON files
# - Appends to manifest.jsonl

# 2. Verify each generated spec
/spec-check newsuite-kernel1-cuda

# 3. Run harness verify on the new specs
python3 -m harness -v verify specs/newsuite-kernel1-cuda.json --config correctness

# 4. Full validation before committing
/validate
```

## Recipe 3: Debug a Failing Spec

```bash
# 1. Build a hypothesis tree for the failure
/hypothesis-tree add "H: rodinia-hotspot-omp VERIFY_FAIL because run args are wrong"

# 2. Check the spec health
/spec-check rodinia-hotspot-omp

# 3. If needed, launch a failure investigation team
/agent-team --scenario failure-investigation "rodinia-hotspot-omp VERIFY_FAIL"

# 4. Once root cause is identified, fix it
/fix-bug "hotspot-omp verify failure — source checks argc==8, spec has 6 args"

# 5. Validate the fix
/validate
```

## Recipe 4: Draft a Paper Section from Eval Data

```bash
# Option A: Use the paper-assembly-team agent
# Spawns 3 sub-agents: data processor, lit scout, methodology expert
# Returns structured findings ready for paper writing

# Option B: Use the agent-team scenario
/agent-team --scenario paper-assembly

# Option C: Use the paper-drafter agent directly
# (for writing specific sections after you have the data)
# The paper-drafter reads actual result files and writes academic prose
```

## Recipe 5: Overnight Maintenance Run

```bash
# 1. Create a tasks.json file with maintenance items
cat > tasks.json << 'EOF'
[
  {"id": 1, "subject": "Run cuda-to-opencl eval for claude-sonnet", "status": "pending"},
  {"id": 2, "subject": "Run cuda-to-opencl eval for gemini-flash", "status": "pending"},
  {"id": 3, "subject": "Run analyze_eval.py with --write-dashboard", "status": "pending"},
  {"id": 4, "subject": "Update visualization data files", "status": "pending"}
]
EOF

# 2. Start the Ralph loop in tmux
tmux new -d -s ralph 'claude --print "/ralph-loop tasks.json"'

# 3. Check progress in the morning
tmux attach -t ralph

# Or check the log without attaching:
cat docs/ralph-progress.md
git log --oneline -10
```

## Recipe 6: Multi-Model Eval Comparison

```bash
# Launch the multi-model-eval agent team
/agent-team --scenario multi-model-eval

# This spawns 4 teammates:
# - claude-analyst: reads results/evaluation/claude-sonnet-4-6/
# - gemini-analyst: reads results/evaluation/gemini-2.5-flash-lite/
# - groq-analyst: reads results/evaluation/groq-llama-3.3-70b/
# - comparator: synthesizes findings from the three analysts

# After completion, the lead presents:
# - Pass rate by model
# - Direction asymmetry
# - Per-kernel anomalies (e.g., backprop tier inversion)
# - Unified failure taxonomy
```

## Recipe 7: Full Session Workflow (Orient to Commit)

```bash
# 1. Orient
/session-start 12

# 2. Explore (surgical, ask-first)
# Read specific files mentioned in the session prompt
# Use Glob/Grep for targeted searches
# Only launch Explore agents with permission

# 3. Plan
# Enter plan mode for non-trivial changes
# Get adversarial review via plan-reviewer agent
# Wait for user approval

# 4. Implement
# Work through the plan step by step
# Use subagents for independent subtasks

# 5. Record
# Update CLAUDE.md, known-issues.md, memory files
/reflect "session 12 — what I learned"

# 6. Verify
/validate
# If PASS → commit
# If FAIL → fix loop → re-validate
git commit -m "Session 12: [description]"
```

---

# Chapter 11: Osmani's Anti-Patterns Cheat Sheet

## The Full List with ParBench Examples

### 1. Never Let AI Write CLAUDE.md

**Rule:** CLAUDE.md is human-curated only.
**Why:** Anthropic's research shows a 2-3% success rate reduction when LLMs write
their own instructions. The LLM optimizes for what's easy to follow, not what's
important. Humans optimize for what prevents mistakes.
**ParBench example:** CLAUDE.md was rewritten from 183 to 56 lines (commit `6da0218`)
by a human, not by Claude. Claude proposed the structure; Samyak curated the content.

### 2. Don't Hover Over Agents

**Rule:** Check progress every 5-10 minutes, not continuously.
**Why:** Agents are async by design. Checking every 30 seconds doesn't make them
faster — it wastes your time and breaks your focus. Trust the quality gates.
**ParBench example:** When running `/validate` (10+ agents, ~3 min), do something
else. The sentinel will tell you if it passed.

### 3. Kill Stuck Agents After 3 Iterations

**Rule:** If an agent fails the same task 3 times, stop it.
**Why:** The fourth attempt won't magically succeed. The task needs human judgment,
not more compute.
**ParBench example:** Ralph loop's stuck detection: 3 consecutive failures on the
same task → mark as `blocked`, move to next task.

### 4. One File, One Owner

**Rule:** In agent teams, no two teammates should edit the same file.
**Why:** Last-write-wins creates overwrite conflicts. Agent A's careful edit gets
silently destroyed by Agent B writing to the same file.
**ParBench example:** In the failure-investigation scenario, build-investigator owns
`builder.py`, run-investigator owns `runner.py`, verify-investigator owns `verifier.py`.

### 5. Specs, Not Vibes

**Rule:** Write precise task descriptions with acceptance criteria.
**Why:** A vague prompt multiplied by 5 agents = 5 different interpretations.
**ParBench example:** Bad: "Fix the failing specs." Good: "rodinia-nw-omp at
`needle.cpp:249` checks `argc == 4`. Current spec has 2 args. Add the third arg
(thread count, value `4`). Verify with `python3 -m harness verify ...`."

### 6. The Human Bottleneck Was a Feature

**Rule:** Don't remove all human review just because you can.
**Why:** Human review catches category errors that automated tests miss. "The code
passes all tests but solves the wrong problem" is undetectable by machines.
**ParBench example:** Plan approval in the `/agent-team` skill: "Wait for Samyak's
approval — do not create the team until approved." The human gate prevents teams
from running on misunderstood requirements.

### 7. Fresh-Context Code Review

**Rule:** Review code in a fresh context, not the same session that wrote it.
**Why:** The session that wrote the code has "anchoring bias" — it remembers why
each decision was made and is less likely to question them. A fresh context
approaches the code without preconceptions.
**ParBench example:** The self-critic agent runs in Wave 4 with its own fresh
context window. It reads the git diff without knowing why Claude made each change.

### 8. Abstraction Bloat — "Couldn't You Just...?"

**Rule:** Before accepting an agent's implementation, ask "couldn't this be simpler?"
**Why:** LLMs over-abstract. They add helper functions, utility classes, and
configuration layers that a 3-line inline solution would replace.
**ParBench example:** The code-simplifier agent specifically looks for "over-engineering
— abstractions with only one consumer, premature generalization."

### 9. Comprehension Debt

**Rule:** If you can't write it yourself, you're rubber-stamping.
**Why:** Accepting code you don't understand creates hidden technical debt.
When it breaks, you can't debug it — you can only ask another LLM to fix it,
compounding the comprehension gap.
**ParBench example:** Samyak alternates between using Claude for complex tasks
and writing code manually (spec JSONs, simple scripts) to stay sharp.

### 10. Document Rot

**Rule:** Maintain CLAUDE.md like a living document.
**Why:** Stale docs are worse than no docs — they give false confidence.
**ParBench example:** The `/dream` skill's Phase 2 checks for stale memory files.
The consistency-checker agent verifies CLAUDE.md tables match actual agent/skill files.

## Decision Flowchart

```
New task arrives
  │
  ▼
Is it trivial (< 5 min, single file)?
  ├── Yes → Do it directly. No agents needed.
  └── No  → Write a clear spec with acceptance criteria.
             │
             ▼
           Enter plan mode. Get adversarial review.
             │
             ▼
           How many independent subtasks?
             ├── 1 → Single subagent (Agent tool)
             ├── 2-3, no cross-talk → Parallel subagents
             └── 3+, need cross-talk or synthesis
                  │
                  ▼
                Agent Team (3-5 teammates)
                  ├── Include a critic teammate
                  ├── Assign file ownership (no overlap)
                  ├── Set kill criteria (MAX_ITERATIONS, stuck detection)
                  └── Require plan approval before implementation
                       │
                       ▼
                     Run. Check every 5-10 min.
                       │
                       ▼
                     Review output. /validate. Commit.
```

---

# Chapter 12: Quick Reference Card

## Skills

| Command | Source | Purpose | When to Use |
|---------|--------|---------|-------------|
| `/validate` | ParBench | 4-wave post-session validation | Before every commit |
| `/validate quick` | ParBench | Wave 1 only (fast check) | Quick sanity check during dev |
| `/validate fix` | ParBench | Re-run failed waves only | After fixing validation failures |
| `/review` | ParBench | 4-agent parallel code review | Before merging or after multi-file changes |
| `/eval-run <suite> <dir>` | ParBench | Eval batch with pre-flight | Starting any LLM evaluation |
| `/reflect` | ParBench | Structured reflection | After completing any task |
| `/spec-check <name>` | ParBench | Spec verification | When debugging spec failures |
| `/session-start <N>` | ParBench | Session bootstrap | Starting a sprint session |
| `/gen-spec <suite>` | ParBench | Spec generation wizard | Adding new benchmark suite |
| `/fix-bug "desc"` | ParBench | Reproduce-diagnose-fix loop | Any bug fix |
| `/feature-dev "name"` | ParBench | Explore-plan-implement-verify | New features |
| `/hypothesis-tree "..."` | ParBench | Hypothesis management | Building research claims |
| `/grill-research` | ParBench | Adversarial research interrogation | Stress-testing paper claims |
| `/paper-review-sim` | ParBench | Peer review simulation | Before paper submission |
| `/interpret-results` | ParBench | Result interpretation | After eval batch completes |
| `/overnight-eval <suite>` | ParBench | tmux-based long eval | Overnight eval campaigns |
| `/dream` | ParBench | Memory consolidation | After milestones or 5+ sessions |
| `/dream audit` | ParBench | Memory health report | Checking memory staleness |
| `/catchup` | ParBench | Session catchup briefing | Returning after a break |
| `/cite-check` | ParBench | Citation verification | Before paper submission |
| `/agent-team [desc]` | ParBench | Agent team creation | Multi-agent coordination |
| `/agent-team --scenario X` | ParBench | Pre-built team template | Known workflow patterns |
| `/augment-test` | ParBench | Augmentation testing | After augmentation changes |
| `/techdebt` | ParBench | Tech debt scanning | Periodic maintenance |
| `/post-eval [model]` | ParBench | Post-eval analysis pipeline | After eval batch completes |
| `/model-route "task"` | ParBench | Model routing advisor | When choosing model for a task |
| `/ralph-loop <file>` | ParBench | Stateless iterative task loop | Overnight maintenance runs |
| `brainstorming` | Superpowers | Structured creative exploration | Before any creative/feature work |
| `writing-plans` | Superpowers | Scope → file structure → tasks | After design, before code |
| `executing-plans` | Superpowers | Load plan → execute → finish | Have a written plan to execute |
| `subagent-driven-development` | Superpowers | Fresh subagent per task | Executing plans with independent tasks |
| `dispatching-parallel-agents` | Superpowers | Domain split → dispatch → integrate | 2+ independent tasks, no shared state |
| `test-driven-development` | Superpowers | RED → GREEN → REFACTOR (Iron Law) | Before any implementation code |
| `systematic-debugging` | Superpowers | Root cause → hypothesis → fix (Iron Law) | Any bug, test failure, unexpected behavior |
| `verification-before-completion` | Superpowers | IDENTIFY → RUN → READ → VERIFY (Iron Law) | Before claiming work is done |
| `requesting-code-review` | Superpowers | Get SHAs → dispatch reviewer → act | After task completion, before merge |
| `receiving-code-review` | Superpowers | READ → UNDERSTAND → VERIFY → RESPOND | When receiving review feedback |
| `using-git-worktrees` | Superpowers | Detect → create worktree → verify baseline | Feature work needing isolation |
| `finishing-a-development-branch` | Superpowers | Verify → determine base → merge/rebase | Implementation complete, tests pass |
| `writing-skills` | Superpowers | TDD for docs (Iron Law) | Creating or editing skills |
| `using-superpowers` | Superpowers | Skill relevance check → invoke → follow | Every session start (auto via hook) |

## Hooks

| Hook File | Type | Matcher | Purpose |
|-----------|------|---------|---------|
| `pre-commit-gate.sh` | PreToolUse | Bash | Blocks commit without `.validation_passed` |
| `protect-benchmark-sources.sh` | PreToolUse | Edit\|Write | Blocks edits to `.cu/.cpp/.c/.cl` in benchmark dirs |
| `protect-cuda-omp-results.sh` | PreToolUse | Bash | Blocks deletion of CUDA-OMP eval results |
| `result-immutability.sh` | PreToolUse | Edit\|Write | Blocks overwriting existing result JSONs |
| `rm -rf blocker` (inline) | PreToolUse | Bash | Blocks destructive `rm -rf` / `rm -fr` |
| `file-ownership.sh` | PreToolUse | Edit\|Write | Blocks edits to files owned by another teammate |
| `sentinel-cleanup.sh` | PostToolUse | Edit\|Write | Deletes `.validation_passed` after file edits |
| `post-edit-test.sh` | PostToolUse | Edit\|Write | Runs tests based on edited file path |
| `context-budget.sh` | PostToolUse | Bash | Context budget reminders at tool call thresholds |
| Ruff auto-lint (inline) | PostToolUse | Edit\|Write | Auto-formats Python files with `ruff check --fix` |
| `post-compact-recovery.sh` | PostToolUse | Compact | Recovers context references after compaction |
| `bash-audit-log.sh` | PreToolUse | Bash | Logs all bash commands to audit trail |
| Anti-rationalization checklist (inline) | Stop | -- | Reminds Claude to check: /validate, tasks, evidence |
| `dream-hook.sh` | Stop | -- | Checks if memory consolidation is due |
| Desktop notification (inline) | Stop | -- | `notify-send` alert when Claude stops |
| Superpowers SessionStart (plugin) | SessionStart | startup\|clear\|compact | Injects `using-superpowers` skill into every session |

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `verification-lead` | opus | Hierarchical validation coordinator (spawns 10+ agents internally) |
| `paper-assembly-team` | opus | SC26 paper data gathering (3 parallel sub-agents) |
| `verify-app` | sonnet | Schema validation, unit tests, spec integrity |
| `diff-reviewer` | sonnet | Git diff analysis for regressions |
| `security-scanner` | sonnet | Secrets, injection, unsafe patterns |
| `test-synthesizer` | sonnet | Runtime test synthesis for changed code |
| `regression-checker` | sonnet | Metric comparison against baselines |
| `spec-auditor` | sonnet | Full spec JSON audit |
| `consistency-checker` | sonnet | Documentation vs code cross-check |
| `code-simplifier` | sonnet | Code quality advisory (non-blocking) |
| `self-critic` | opus | Adversarial self-review |
| `plan-reviewer` | opus | Adversarial plan review |
| `rodinia-verifier` | sonnet | Harness verify on all Rodinia specs |
| `xsbench-explorer` | opus | XSBench source exploration |
| `eval-batcher` | sonnet | LLM evaluation batch runner |
| `paper-drafter` | opus | SC26 paper section writer |
| `dashboard-refresher` | sonnet | Visualization data regeneration |
| `explorer` | sonnet | General codebase exploration |
| `code-reviewer` | inherit | Plan-alignment + code quality review (Superpowers plugin) |

## Agent Team Controls

| Key | Action |
|-----|--------|
| `Shift+Down` | Cycle through teammates |
| `Enter` | View selected teammate's session |
| `Escape` | Return to lead |
| `Ctrl+T` | Toggle shared task list overlay |

## Agent Team Scenarios

| Scenario Name | Teammates | Use Case |
|---------------|-----------|----------|
| `multi-model-eval` | 4 | Compare eval results across models |
| `paper-assembly` | 3 | Gather data for SC26 paper sections |
| `failure-investigation` | 3 | Debug a failing kernel (build/run/verify) |
| `cross-model-taxonomy` | 4 | Build unified failure taxonomy |
| `post-batch-analysis` | 3 | Post-eval analysis pipeline |
| `augmentation-audit` | 4 | Verify augmentation level-invariance |

## Session Workflow Quick Reference

```
1. Orient    →  /session-start N
2. Explore   →  Surgical reads (Glob, Grep, Read). Ask before broad sweeps.
3. Plan      →  Plan mode + plan-reviewer agent. Wait for approval.
4. Implement →  Work the plan. Subagents for independent subtasks.
5. Record    →  /reflect. Update CLAUDE.md, known-issues.md, memory.
6. Verify    →  /validate (4 waves). Fix loop if needed. Commit when PASS.
```

## Critical Rules (Always Remember)

1. `manifest.jsonl` is **append-only** — never modify existing entries
2. Result JSONs are **immutable** — use `--resume` to skip existing
3. **Never run evals in worktrees** — submodules are empty
4. **Never change spec run args** without reading the source's `argc` check
5. ~135 `validate_schema.py` errors are **expected** — do not fix
6. 8 KNOWN_FAIL specs — **always exclude** from eval batches
7. Always `python3`, never `python`
8. Harness CLI: `-v` flag goes **before** the subcommand
9. **Opus everywhere** — never use Sonnet or Haiku for main work
10. **/validate before every commit** — pre-commit hook enforces this

## "I Want To..." Situation Lookup

| I want to... | Use This | Source |
|--------------|----------|--------|
| Start a session | `/session-start <N>` + `using-superpowers` (auto) | ParBench + Superpowers |
| Design a new feature | `brainstorming` → `writing-plans` → `/feature-dev` | Superpowers → ParBench |
| Implement a plan | `executing-plans` or `subagent-driven-development` | Superpowers |
| Fix a bug | `/fix-bug` + `systematic-debugging` (guides diagnostic phase) | ParBench + Superpowers |
| Run LLM evaluations | `/eval-run` or `/overnight-eval` | ParBench |
| Review code | `/review` + `requesting-code-review` / `receiving-code-review` | ParBench + Superpowers |
| Validate before commit | `/validate` + `verification-before-completion` (discipline) | ParBench + Superpowers |
| Finish a feature branch | `finishing-a-development-branch` | Superpowers |
| Write paper sections | `paper-assembly-team` agent or `paper-drafter` agent | ParBench |
| Manage memory | `/dream` or `/catchup` | ParBench |
| Run overnight tasks | `/ralph-loop` or `/overnight-eval` | ParBench |
| Create new skills | `writing-skills` | Superpowers |
| Run parallel independent tasks | `dispatching-parallel-agents` | Superpowers |
| Coordinate multi-agent work | `/agent-team` | ParBench |
| Stress-test paper claims | `/grill-research` or `/paper-review-sim` | ParBench |
| Add a new benchmark suite | `/gen-spec <suite>` | ParBench |
| Write tests first | `test-driven-development` | Superpowers |
| Isolate work in a worktree | `using-git-worktrees` | Superpowers |

## Decision Trees

### Which agent pattern?

```
Need to delegate work?
├── Single focused question about one area?
│   └── One surgical subagent (Explore type)
├── 2+ independent tasks, each <2 min?
│   └── Parallel subagents (dispatching-parallel-agents)
├── Tasks need shared findings / cross-talk?
│   └── Agent team (/agent-team)
├── Need repo isolation (parallel edits)?
│   └── Worktree subagent (isolation: "worktree")
└── Extended coordinated work (5-30 min)?
    └── Agent team with scenario template
```

### Which skill for this task?

```
What are you doing?
├── Fixing a bug
│   ├── /fix-bug (ParBench outer workflow)
│   └── systematic-debugging (Superpowers diagnostic discipline)
│       └── test-driven-development (write regression test first)
├── Building a feature
│   ├── brainstorming (explore the design space)
│   ├── writing-plans (create implementation plan)
│   ├── executing-plans (work through the plan)
│   └── /feature-dev (ParBench orchestrator)
├── Running evaluations
│   ├── /eval-run (single batch)
│   ├── /overnight-eval (long campaign via tmux)
│   └── /post-eval (analysis after completion)
├── Writing the paper
│   ├── paper-assembly-team (data gathering)
│   ├── paper-drafter (section writing)
│   ├── /grill-research (stress-test claims)
│   └── /cite-check (verify citations)
└── Finishing up
    ├── verification-before-completion (claim discipline)
    ├── /validate (concrete 4-wave check)
    ├── finishing-a-development-branch (merge/rebase)
    └── /dream (memory consolidation)
```

---

# Chapter 13: The Superpowers Plugin

## 13.1 What Is Superpowers

[obra/superpowers](https://github.com/obra/superpowers) is a Claude Code plugin by Jesse
Vincent that provides **14 process-discipline skills** and **1 custom agent**. These are
project-agnostic engineering workflows — TDD, systematic debugging, verification discipline,
code review protocols — that complement ParBench's domain-specific skills.

**The distinction:**
- **ParBench skills** (23 skills in `.claude/skills/`) = domain-specific workflows for
  HPC benchmarking, eval pipelines, spec generation, paper writing
- **Superpowers skills** (14 skills in plugin) = engineering discipline that applies to
  any codebase — how to debug, how to plan, how to verify

They layer, not compete. ParBench's `/fix-bug` is the *what* (reproduce → diagnose → fix
a ParBench bug). Superpowers' `systematic-debugging` is the *how* (root cause investigation
methodology). Both fire on the same task; they compose naturally.

**Version:** 5.0.6 (check `~/.claude/plugins/marketplaces/superpowers-dev/package.json`)

## 13.2 Installation & Configuration

Superpowers is installed through Claude Code's plugin marketplace system:

**User-level** (`~/.claude/settings.json`):
```json
"extraKnownMarketplaces": {
  "superpowers-dev": {
    "url": "https://github.com/obra/superpowers.git"
  }
}
```

**Project-level** (`.claude/settings.json`):
```json
"enabledPlugins": {
  "superpowers@superpowers-dev": true
}
```

**Plugin files live at:** `~/.claude/plugins/marketplaces/superpowers-dev/`

The plugin also provides a **SessionStart hook** (`hooks/hooks.json`) that fires on
`startup|clear|compact` events. This hook injects the `using-superpowers` skill content
into every new session, which is how the plugin bootstraps itself without explicit user
invocation — Claude learns about available skills at session start and checks for relevance
before every response.

## 13.3 Invocation Model

ParBench skills and superpowers skills use the same `Skill` tool but have different
activation patterns:

| Aspect | ParBench Skills | Superpowers Skills |
|--------|----------------|-------------------|
| Trigger | User types `/skill-name` | Claude invokes via Skill tool when relevant |
| Discovery | User knows the command | SessionStart hook bootstraps awareness |
| Threshold | Explicit request | "Even 1% chance → invoke" (per `using-superpowers`) |
| Format | SKILL.md loaded as workflow | SKILL.md loaded as process discipline |

**Deprecated commands:** `/brainstorm`, `/write-plan`, `/execute-plan` are stubs that
redirect to the superpowers skill versions (`brainstorming`, `writing-plans`,
`executing-plans`).

**Instruction priority** (from `using-superpowers` SKILL.md):
1. **User's explicit instructions** (CLAUDE.md, direct requests) — highest priority
2. **Superpowers skills** — override default system behavior
3. **Default system prompt** — lowest priority

This means ParBench's CLAUDE.md rules (e.g., "Opus everywhere", "never modify manifest
entries") always win over any superpowers skill guidance.

## 13.4 Rigid vs. Flexible & The Iron Laws

Superpowers classifies its skills into two enforcement levels:

**Rigid** (12 of 14): Follow exactly as written. These have mandatory phases with explicit
sequencing — skipping steps breaks the discipline they enforce.

**Flexible** (2 of 14): `dispatching-parallel-agents` and `requesting-code-review`. These
describe principles and patterns to adapt to context rather than strict phase sequences.

### Iron Law Skills

Four rigid skills share an elevated enforcement pattern called the **Iron Law**:

| Skill | Iron Law | Gate |
|-------|----------|------|
| `test-driven-development` | No production code without a failing test | RED must fail before GREEN |
| `systematic-debugging` | No fix without root cause | Must complete investigation before implementing |
| `verification-before-completion` | No done claim without evidence | Must RUN and READ output, not assume |
| `writing-skills` | No skill without failing test (TDD for docs) | Pressure scenario must fail first |

Each Iron Law skill includes:
- **Mandatory phases** that cannot be skipped or reordered
- **An explicit "you cannot proceed without completing Phase N" gate**
- **A rationalization-prevention section** listing thoughts that signal you're about to cheat

`★ Insight ─────────────────────────────────────`
**Anti-rationalization as a design pattern:** The Iron Law skills and ParBench's `self-critic`
agent (Wave 4 of `/validate`) attack the same failure mode from opposite directions.
The skills prevent Claude from *starting* to rationalize during execution ("I don't need
to run the test, the code is obviously correct"). The self-critic catches rationalization
*after the fact* in the git diff ("this claim says X is done but no test output exists").
This is defense-in-depth applied to cognitive discipline — Trail of Bits' anti-rationalization
patterns operationalized for agentic coding workflows.
`─────────────────────────────────────────────────`

## 13.5 Process Skills Catalog

| Skill | Type | Trigger Condition | Key Phases | ParBench Usage |
|-------|------|-------------------|------------|----------------|
| `brainstorming` | Rigid | Before any creative/feature work | Explore → questions → approaches → design doc → self-review | Before `/feature-dev`, new spec suites |
| `writing-plans` | Rigid | After design, before code | Scope check → file structure → bite-sized tasks → self-review | Generates plan files for sprint sessions |
| `executing-plans` | Rigid | Have a written plan to execute | Load plan → execute tasks → finish branch | Drives `/ralph-loop` task execution |
| `subagent-driven-development` | Rigid | Executing plans with independent tasks | Fresh subagent per task → spec review → quality review | Multi-task sprint sessions |
| `dispatching-parallel-agents` | Flexible | 2+ independent tasks, no shared state | Identify domains → create focused tasks → dispatch → integrate | Validation waves, multi-model analysis |
| `test-driven-development` | Rigid (Iron Law) | Before any implementation code | RED (failing test) → verify RED → GREEN → verify GREEN → REFACTOR | Transform tests in `test_transforms.py` |
| `systematic-debugging` | Rigid (Iron Law) | Any bug, test failure, unexpected behavior | Root cause investigation → pattern analysis → hypothesis → implement | Spec failure debugging, pipeline bugs |
| `verification-before-completion` | Rigid (Iron Law) | Before claiming work is done | IDENTIFY command → RUN → READ output → VERIFY claim | Enforced by `/validate` and pre-commit gate |
| `requesting-code-review` | Flexible | After task completion, before merge | Get SHAs → dispatch code-reviewer → act on feedback | Used within `subagent-driven-development` |
| `receiving-code-review` | Rigid | When receiving review feedback | READ → UNDERSTAND → VERIFY → EVALUATE → RESPOND → IMPLEMENT | PR reviews, agent team critic feedback |
| `using-git-worktrees` | Rigid | Feature work needing isolation | Detect project → create worktree → setup → verify baseline | Sprint session isolation (NOT for evals) |
| `finishing-a-development-branch` | Rigid | Implementation complete, tests pass | Verify tests → determine base → present 4 options → execute → cleanup | End of every feature branch |
| `writing-skills` | Rigid (Iron Law) | Creating or editing skills | TDD for docs: pressure scenario (RED) → write skill (GREEN) → close loopholes (REFACTOR) | Built all 23 ParBench skills |
| `using-superpowers` | Rigid | Every conversation start (auto via SessionStart hook) | Check skill relevance → invoke Skill tool → announce → follow | Bootstraps all other superpowers skills |

## 13.6 Composition Chains

Skills compose into natural chains for common workflows:

**New feature:**
```
brainstorming → writing-plans → using-git-worktrees → executing-plans
  → verification-before-completion → finishing-a-development-branch
```

**Bug fix:**
```
systematic-debugging → test-driven-development → verification-before-completion
```

**Code review cycle:**
```
requesting-code-review → receiving-code-review
```

**New skill creation:**
```
writing-skills (internally uses test-driven-development RED→GREEN→REFACTOR pattern)
```

## 13.7 Overlap Resolution

ParBench skills and superpowers skills layer — they don't compete. The ParBench skill
provides the domain-specific *what*, and the superpowers skill provides the engineering
*how*:

| ParBench Skill | Superpowers Skill | How They Compose |
|----------------|-------------------|------------------|
| `/fix-bug` | `systematic-debugging` | `/fix-bug` is the outer workflow; `systematic-debugging` guides the diagnostic phase within it |
| `/validate` | `verification-before-completion` | `/validate` is the concrete tool; `verification-before-completion` is the discipline that demands you run it |
| `/review` | `requesting-code-review` + `receiving-code-review` | `/review` dispatches 4 parallel agents; the superpowers skills guide how to request and respond to their feedback |
| `/feature-dev` | `brainstorming` + `writing-plans` | `brainstorming` runs first for design; `writing-plans` generates the plan; `/feature-dev` executes it |

**Rule of thumb:** If both a ParBench skill and a superpowers skill apply, the ParBench
skill determines *what* to do (which files, which pipeline stages, which verification
commands). The superpowers skill determines *how* to approach it (investigate before fixing,
test before implementing, verify before claiming done).

## 13.8 Rationalization Prevention

The `using-superpowers` skill includes a red-flags table — thoughts that indicate Claude
is about to skip a skill it should invoke:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE exploration. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

`★ Insight ─────────────────────────────────────`
**Metacognitive monitoring in agentic systems:** This red-flags table is a form of
*metacognitive monitoring* — the system watches its own thought patterns for signatures
of process shortcuts. This is the same principle behind ParBench's `self-critic` agent
(which catches rationalization in git diffs) and Trail of Bits' anti-rationalization
checklists. The insight is that LLM agents fail most often not from lack of capability
but from *motivated reasoning* to skip discipline when a task looks simple. The
superpowers plugin addresses this at the earliest possible point — before the first
tool call — while ParBench's validation loop catches what slips through later.
`─────────────────────────────────────────────────`

---

## Further Reading

- Addy Osmani, "The Agentic Coding Workflow" (CodeCon 2026 keynote)
- Osmani's web-quality-skills repo — model for skill packaging
- Trail of Bits, "Secure Claude Code Configuration" — hook patterns
- Anthropic, "Agent Teams Documentation" — official reference
- Geoffrey Huntley & Ryan Carson, "The Ralph Loop" — autonomous coding cycles
- Steve Yegge, "8 Levels of AI-Assisted Development" — progression model
- ARIS: Auto-Research-In-Sleep — paper quality improvement through overnight runs
- obra/superpowers (v5.0.6) — Claude Code plugin providing 14 process-discipline skills
  (brainstorming, TDD, systematic debugging, verification, code review, worktrees, etc.)
  and 1 custom agent (code-reviewer). By Jesse Vincent.
  Marketplace: https://github.com/obra/superpowers.git
  Installed at: `~/.claude/plugins/marketplaces/superpowers-dev/`
  See [Chapter 13](#chapter-13-the-superpowers-plugin) for full documentation.
