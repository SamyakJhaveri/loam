---
name: multi-review
description: "Multi-agent parallel code review with 4 reviewers (style, correctness, security, performance). Use before merging a feature branch, before committing a non-trivial change, or when a second pair of eyes is needed. Complements /validate (which checks pipeline correctness); review checks code quality. NOT for: single-line trivial changes, commit-message review, or replacing /validate — use both, not either."
---

# Multi-Agent Code Review

Structured code review using parallel subagents for thorough coverage.

## Arguments
- `$ARGUMENTS` — optional: file paths or commit range to review (default: staged changes)

## Workflow

### Phase 1: Identify Scope
- If arguments specify files/commits, use those
- Otherwise, review staged changes (`git diff --cached`)
- If nothing is staged, review unstaged changes (`git diff`)

### Phase 2: Parallel Review
Launch 4 subagents simultaneously, each reviewing the same changes:

1. **Style Agent** — naming, formatting, consistency with existing code
2. **Correctness Agent** — logic errors, off-by-one, null/undefined risks
3. **Security Agent** — injection, path traversal, secret exposure, OWASP top 10
4. **Performance Agent** — unnecessary allocations, O(n²) where O(n) is possible

### Phase 3: Synthesize
- Collect all findings
- Deduplicate overlapping concerns
- Prioritize by severity: critical > high > medium > low

### Phase 4: Report
Present findings grouped by severity:

```
## Critical
- [issue + file:line + suggestion]

## High
- ...

## Medium / Low
- ...

## Summary
N issues found (X critical, Y high, Z medium/low)
Recommendation: APPROVE / NEEDS CHANGES
```
