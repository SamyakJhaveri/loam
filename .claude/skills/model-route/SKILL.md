---
name: model-route
description: Advisor for selecting optimal Claude model tier (Opus/Sonnet/Haiku) for a specific task. Use before launching an agent team, before a multi-file refactor, or when deciding whether to switch from Opus to Haiku for transactional work (commits, formatting). Analyzes reasoning depth, blast radius, domain expertise, output length, correctness cost.
---

# Model Route Advisor

Recommend the optimal Claude model for a given task based on Osmani's multi-model
routing principle. Analyzes task complexity, token budget, and parallelization
opportunities to suggest the best model allocation.

**Trigger:** When user types `/model-route` or `/model-route "<task description>"`

## Arguments

- `$ARGUMENTS` — optional task description in quotes. If omitted, prompt the user
  to describe what they want to do.

## ParBench Policy Context

**This project uses Opus everywhere** (see CLAUDE.md and workflow.md). The routing
recommendation is advisory — it shows what the optimal allocation WOULD be under a
cost-optimized policy. The user decides whether to follow it or stick with Opus.

Exception: Haiku is used for commit/push operations per project policy (CLAUDE.md
"Model selection" section).

## Routing Matrix

### Tier 1: Opus (highest capability, highest cost)

**Route to Opus when the task involves:**
- Architecture decisions or system design
- Complex debugging across multiple files
- Security review or adversarial analysis
- Planning and plan-reviewer verification
- Paper writing, scientific argumentation
- Interpreting eval results or research claims
- Self-critic and validation waves
- Any task where a wrong answer is expensive to fix

**Token estimate:** 10K-50K per task (high reasoning depth)

### Tier 2: Sonnet (strong capability, moderate cost)

**Route to Sonnet when the task involves:**
- Implementing a well-defined plan (code already designed)
- Writing boilerplate or mechanical code changes
- Routine refactoring with clear patterns
- Data migration or format conversion scripts
- Adding tests for existing code (test patterns clear)
- Subagent work with structured output requirements

**Token estimate:** 5K-20K per task (less reasoning, more generation)

### Tier 3: Haiku (fast, lowest cost)

**Route to Haiku when the task involves:**
- Commit message generation
- File formatting and linting
- Simple lookups (find a function, check a value)
- Mechanical git operations (push, tag, branch)
- Generating structured data from templates
- Simple text transformations

**Token estimate:** 1K-5K per task (minimal reasoning needed)

## Workflow

### Step 1: Analyze the Task

Parse the task description and classify it along these dimensions:

| Dimension | Low | High |
|-----------|-----|------|
| **Reasoning depth** | Mechanical, pattern-following | Novel, requires inference |
| **Blast radius** | Single file, reversible | Multi-file, hard to undo |
| **Domain expertise** | Generic programming | HPC/CUDA/research-specific |
| **Output length** | Short (< 500 tokens) | Long (> 2K tokens) |
| **Correctness cost** | Easy to verify, cheap to retry | Hard to verify, expensive if wrong |

### Step 2: Generate Recommendation

Present the recommendation in this format:

```
=== MODEL ROUTE: <task summary> ===

Recommended: <MODEL> (<tier>)

Reasoning:
  - <dimension 1>: <assessment> -> <model implication>
  - <dimension 2>: <assessment> -> <model implication>
  - <dimension 3>: <assessment> -> <model implication>

Token estimate: ~<N>K tokens
Cost estimate: ~$<X.XX> (at current pricing)

ParBench policy: Opus everywhere (this recommendation is advisory)
```

### Step 3: Suggest Parallelization (if applicable)

If the task can be decomposed, suggest splitting:

```
Parallelization opportunity:
  Instead of 1 Opus call (~40K tokens, ~$X.XX):
  - 3 Sonnet subagents (~15K each, ~$X.XX total)
  - Each handles: <subtask description>
  - Savings: ~<N>% cost, ~<N>x faster (parallel execution)
```

Only suggest parallelization when subtasks are genuinely independent and don't
need shared state or sequential reasoning.

### Step 4: Note Alternatives

If the task sits at a boundary between tiers:

```
Alternative approaches:
  a) <Model A>: <tradeoff> (e.g., "Opus for safety, +$0.50")
  b) <Model B>: <tradeoff> (e.g., "Haiku for speed, risk of shallow analysis")
  c) <Split>: <tradeoff> (e.g., "Opus for planning + Sonnet for implementation")
```

## ParBench-Specific Routing Rules

These override the general matrix for this project:

| Task | Always Use | Reason |
|------|-----------|--------|
| Eval pipeline changes (`llm_evaluate.py`) | Opus | Wrong changes invalidate all results |
| Spec arg verification | Opus | Requires reading source argc + understanding semantics |
| Paper section writing | Opus | Scientific argumentation requires deep reasoning |
| Dashboard refresh | Sonnet/subagent | Mechanical: read JSON, update HTML numbers |
| Commit + push | Haiku | Per project policy (CLAUDE.md) |
| `/validate` waves | Opus | Self-critic requires adversarial reasoning |
| Augmentation transforms | Opus | AST manipulation requires precise reasoning |
| `/catchup` briefing | Haiku | Mechanical: run git commands, format output |

## Context Management

This skill is pure analysis — no file reads, no subagents, no bash commands.
It analyzes the task description and produces a recommendation. Total output: ~20 lines.
