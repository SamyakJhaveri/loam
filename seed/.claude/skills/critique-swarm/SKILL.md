---
name: critique-swarm
auto-activate: false
description: >
  Parallel adversarial critique with 4 specialized agents plus synthesis. Use before
  merging a feature branch, before committing a complex plan, or when you want
  independent multi-angle review of a plan or implementation. Complements /multi-review
  (which reviews code quality) by reviewing plan/scope quality. NOT for single-file
  trivial changes (use /validate), standard code review (use /multi-review), or
  post-implementation shipping (use /ship).
argument-hint: "[path to plan file, defaults to current diff]"
---

# Critique Swarm: Parallel Adversarial Review

Launches 4 parallel Agent invocations, each with a distinct adversarial mandate,
then a 5th synthesis agent that deduplicates findings and ranks them.

## When to Use

- Before approving a complex implementation plan
- Before merging a feature branch with cross-cutting changes
- When you want independent multi-angle critique beyond what `/multi-review` provides
- After a port/transplant operation to catch fidelity loss

## When NOT to Use

- Single-file trivial edits → use `/validate`
- Code-level quality review → use `/multi-review`
- Ready to ship → use `/ship` (which includes `/session-critique`)

## Procedure

### Step 1: Identify the review target

If `$ARGUMENTS` contains a file path, review that file. Otherwise, review the
current session's changes via `git diff HEAD`.

### Step 2: Launch 4 parallel critique agents

Spawn all 4 agents in a **single message** (parallel launch) using the Agent tool.
Each agent receives the review target and its specific mandate.

**Agent 1 — Security & Correctness:**
> Review the changes for security vulnerabilities, correctness regressions, broken
> invariants, and unsafe patterns. Check for: command injection, path traversal,
> missing input validation at system boundaries, race conditions, and any behavior
> change that could break existing consumers. Report findings with file:line references.

**Agent 2 — Scope Creep & Over-Engineering:**
> Review the changes for scope creep and over-engineering. Check for: unnecessary
> abstractions, features not requested in the spec, extra deliverables beyond what
> was asked, verbose preambles, premature generalization, and any "while we're here"
> cleanup that wasn't part of the task. Flag anything that could be removed without
> affecting the stated goal.

**Agent 3 — Fidelity Loss:**
> Review the changes for fidelity loss during porting or transplanting content. Check
> for: dropped sections, missing taglines or sub-groups, altered meaning during
> rewording, references that point to moved/renamed files, and any content that was
> in the source but is absent from the output. Compare source and destination line
> by line where applicable.

**Agent 4 — Test & Validation Gaps:**
> Review the changes for missing tests and validation gaps. Check for: untested code
> paths, missing edge case coverage, assertions that don't verify the actual behavior,
> test files that exist but don't run, and validation steps mentioned in the plan but
> not implemented. Flag any change that modifies behavior without a corresponding test.

### Step 3: Synthesize findings

After all 4 agents complete, launch a 5th synthesis agent:

> You have received findings from 4 independent critique agents reviewing the same
> changes. Your job: (1) deduplicate findings that appear in multiple reports,
> (2) rank all unique findings by severity (HIGH/MEDIUM/LOW), (3) mark any false
> positives with reasoning for why they're false, (4) produce a single ordered list
> of recommended fixes — minimal set only. Do not implement any fixes. Output format:
>
> ```
> === CRITIQUE SWARM VERDICT ===
> Reviewed: [target]
> Agents: 4 (security, scope, fidelity, tests)
>
> ## Findings (ranked by severity)
> | # | Severity | Category | File:Line | Issue | Fix |
> |---|----------|----------|-----------|-------|-----|
>
> ## False Positives Dismissed
> | # | Category | Reason |
>
> ## Recommended Action
> [Fix N issues before proceeding / Clean — no blocking issues found]
> ```

### Step 4: Present verdict to user

Display the synthesis report. Do NOT implement any fixes automatically. The user
decides which fixes to apply.

## Relationship to Other Skills

| Skill | Reviews | Use Together? |
|-------|---------|---------------|
| `/multi-review` | Code quality (style, correctness, security, performance) | Yes — complementary |
| `/session-critique` | Session work — **decision-aware** (the session's in-conversation decisions + regressions, scope, dangling refs) | Either/or — use `/session-critique` when you need decision-adherence; critique-swarm for cold scope review |
| `/validate` | Deterministic + rule-based checks | Yes — different layer |
