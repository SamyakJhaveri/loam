---
name: model-route
description: >
  Advisor for selecting optimal Claude model tier (Opus/Sonnet) for a specific task.
  Use before launching an agent team, before a multi-file refactor, or when deciding
  model allocation for subagents. Analyzes reasoning depth, blast radius, domain
  expertise, output length, correctness cost. Always uses ultrathink.
---

# Model Route Advisor

Recommend the optimal Claude model for a given task. Two tiers only: Opus and Sonnet.
Always use ultrathink. Never use Haiku.

**Trigger:** When user types `/model-route` or `/model-route "<task description>"`

## Arguments

- `$ARGUMENTS` — optional task description in quotes. If omitted, prompt the user
  to describe what they want to do.

## Policy

- **Opus** is the default for all work. Use Opus 4.6 or Opus 4.7.
- **Sonnet** is acceptable for well-scoped subagent work where the plan is already clear.
- **Haiku is never used.** Not for commits, not for lookups, not for anything.
- **ultrathink is always on.** Every task gets deep reasoning.

## Routing Matrix

### Tier 1: Opus (default — use for everything unless Sonnet clearly suffices)

**Route to Opus when the task involves:**
- Architecture decisions or system design
- Complex debugging across multiple files
- Security review or adversarial analysis
- Planning and plan-reviewer verification
- Technical writing requiring deep domain reasoning
- Interpreting complex results or research claims
- Self-critic and validation waves
- Any task where a wrong answer is expensive to fix
- Commit message generation and git operations
- Any task you're unsure about — default to Opus

**Token estimate:** 10K-50K per task (high reasoning depth)

### Tier 2: Sonnet (for well-defined subagent work only)

**Route to Sonnet when ALL of these are true:**
- Implementing a well-defined plan (code already designed by Opus)
- The task is mechanical with clear patterns (no judgment calls)
- It's subagent work with structured output requirements
- A wrong answer is cheap to detect and retry

Examples: routine refactoring with explicit instructions, data format conversion,
adding tests where the test patterns are already established, bulk file reads
delegated from a lead agent.

**Token estimate:** 5K-20K per task (less reasoning, more generation)

## Workflow

### Step 1: Analyze the Task

Parse the task description and classify it along these dimensions:

| Dimension | Low | High |
|-----------|-----|------|
| **Reasoning depth** | Mechanical, pattern-following | Novel, requires inference |
| **Blast radius** | Single file, reversible | Multi-file, hard to undo |
| **Domain expertise** | Generic programming | Domain-specific knowledge |
| **Output length** | Short (< 500 tokens) | Long (> 2K tokens) |
| **Correctness cost** | Easy to verify, cheap to retry | Hard to verify, expensive if wrong |

**If ANY dimension is "High" → Opus.** Sonnet only when ALL dimensions are "Low".

### Step 2: Generate Recommendation

Present the recommendation in this format:

```
=== MODEL ROUTE: <task summary> ===

Recommended: <MODEL> (with ultrathink)

Reasoning:
  - <dimension 1>: <assessment> -> <model implication>
  - <dimension 2>: <assessment> -> <model implication>
  - <dimension 3>: <assessment> -> <model implication>

Token estimate: ~<N>K tokens
```

### Step 3: Suggest Parallelization (if applicable)

If the task can be decomposed, suggest splitting:

```
Parallelization opportunity:
  Instead of 1 Opus call (~40K tokens):
  - Opus lead + 3 Sonnet subagents (~15K each)
  - Each handles: <subtask description>
  - Savings: ~<N>% cost, ~<N>x faster (parallel execution)
  - Note: All agents use ultrathink
```

Only suggest parallelization when subtasks are genuinely independent and don't
need shared state or sequential reasoning. The lead/advisor is always Opus.

### Step 4: Note Alternatives

If the task sits at the Opus/Sonnet boundary:

```
Alternative approaches:
  a) Opus everywhere: <tradeoff> (safest, higher cost)
  b) Opus lead + Sonnet workers: <tradeoff> (advisor pattern, good for parallel work)
  c) All Opus parallel: <tradeoff> (when workers need deep reasoning too)
```

## Context Management

This skill is pure analysis — no file reads, no subagents, no bash commands.
It analyzes the task description and produces a recommendation. Total output: ~20 lines.
