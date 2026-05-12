---
name: process-optimizer
description: >
  Analyzes existing workflows and processes to find inefficiencies, bottlenecks, and
  optimization opportunities. Goes beyond automation to improve the process itself.
  Use when user says "optimize my process", "find bottlenecks", "why is this slow",
  "improve this workflow", "process audit", or "efficiency review".
auto-activate: false
---

# Process Optimizer — Find and Fix Bottlenecks

Analyzes workflows not just for automation opportunities, but for process improvement — eliminating unnecessary steps, reducing handoffs, parallelizing work, and fixing the root cause of inefficiency.

## How It Works

### Step 1: Receive the Process

Accept a workflow in any format:
- Output from `/workflow-mapper`
- Numbered step list
- Free-form description
- "Here's how we handle [X]..."

### Step 2: Run the 5-Layer Analysis

For each step in the process, evaluate against these 5 lenses:

**1. Necessity Check**: Does this step need to exist at all?
- Is it redundant with another step?
- Is it legacy (existed for a reason that no longer applies)?
- Would removing it break anything?

**2. Sequence Check**: Is this step in the right place?
- Could it happen earlier (preventing downstream waste)?
- Could it happen in parallel with other steps?
- Is it blocking something it shouldn't be?

**3. Handoff Check**: Does this step involve unnecessary handoffs?
- Does work pass between people/tools unnecessarily?
- Could one person/tool handle adjacent steps?
- Is there a wait time between handoff and pickup?

**4. Error Check**: Where does this step fail?
- What are the common errors or rework triggers?
- Is there a validation step, or do errors propagate downstream?
- What's the cost of failure at this step?

**5. Automation Check**: Can technology handle this?
- Same as the GREEN/YELLOW/RED framework from workflow-mapper
- But also considers partial automation (AI assists, human decides)

### Step 3: Generate the Optimization Report

```markdown
# Process Optimization: [Process Name]

## Current State
- **Steps**: [X]
- **Estimated time per occurrence**: [X min/hours]
- **Handoffs**: [X between people/tools]
- **Known pain points**: [from user's description]

## Findings

### Eliminate (Steps That Don't Need to Exist)
| Step | Reason to Remove | Time Saved |
|------|-----------------|------------|
| [Step X] | [Redundant with Step Y] | [X min] |

### Resequence (Steps in the Wrong Order)
| Step | Current Position | Recommended Position | Why |
|------|-----------------|---------------------|-----|
| [Step X] | After Step Y | Before Step Y | [Prevents Z rework] |

### Parallelize (Steps That Can Run Simultaneously)
| Steps | Currently | Recommended | Time Saved |
|-------|-----------|-------------|------------|
| [X + Y] | Sequential (20 min) | Parallel (10 min) | 10 min |

### Reduce Handoffs
| Handoff | Current Flow | Recommended | Why |
|---------|-------------|-------------|-----|
| [Step X → Y] | [Person A → Person B] | [Person A handles both] | [Eliminates 2hr wait] |

### Automate
[Use GREEN/YELLOW/RED framework — reference /workflow-mapper output if available]

## Optimized Process
[Rewritten process with all improvements applied — numbered steps, clean and clear]

## Impact Summary
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total steps | [X] | [Y] | -[Z] steps |
| Time per occurrence | [X min] | [Y min] | -[Z]% |
| Handoffs | [X] | [Y] | -[Z] |
| Error-prone steps | [X] | [Y] | -[Z] |
| **Time saved per week** | — | **[X hours]** | — |
```

### Step 4: Implementation Recommendations

Provide a prioritized list:
1. **Do now** (no-cost, no-tool changes — just resequence/eliminate)
2. **Do this week** (simple automation or tool configuration)
3. **Do this month** (requires building, setup, or team training)

## Rules

- Don't just find things to automate. The biggest wins often come from REMOVING steps, not automating them.
- Question every handoff. Each handoff introduces wait time and context loss.
- Before and after must be concrete. Show the math.
- Respect institutional knowledge. If a step looks unnecessary but exists for regulatory, legal, or safety reasons, flag it as "verify with stakeholder" rather than recommending removal.
