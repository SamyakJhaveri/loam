---
name: to-issues
description: >
  Decompose a plan, spec, or PRD into independently-grabbable GitHub issues
  using tracer-bullet vertical slices. Classifies each as HITL or AFK.
  Use after /gen-spec produces a spec, or when a plan needs decomposition.
  NOT for: writing specs (use /gen-spec), implementing features (use /feature-dev).
auto-activate: false
---

# Plan to Issues

Convert plans, specs, or PRDs into independently-grabbable issues using tracer-bullet vertical slices.

## Arguments

`$ARGUMENTS` — path to spec/plan file, or issue/PR URL to decompose

## Core Principle

Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests). A completed slice is demoable or verifiable on its own. Never decompose horizontally (all models first, then all views, then all tests).

## Workflow

### Phase 1: Gather Context

- Read the spec/plan/PRD (if `$ARGUMENTS` is a file path, read it; if a URL, fetch it)
- If no spec exists, suggest running `/gen-spec` first
- Explore the codebase to understand current state and conventions

### Phase 2: Draft Vertical Slices

For each slice, draft:

- **Title** — short, action-oriented (e.g., "Add user signup endpoint with validation")
- **Scope** — what this slice touches across ALL layers
- **Acceptance criteria** — specific, testable conditions
- **Classification:**
  - **HITL** (Human In The Loop) — requires human judgment: architectural decisions, design reviews, access permissions
  - **AFK** (Away From Keyboard) — can be implemented and merged autonomously. Preferred when scope is clear and testable.
- **Blocking** — which other slices must complete first (if any)

### Phase 3: Quiz the User

Present the slices and ask:
- Is the granularity right? (Too big = hard to review. Too small = overhead.)
- Are dependencies correctly identified?
- Are HITL/AFK classifications correct?
- Any slices that should be merged or split?

### Phase 4: Publish

Publish issues in dependency order using the project's issue tracker. Each issue includes:

```
## Scope
<what this slice touches>

## Acceptance Criteria
- [ ] <criterion 1>
- [ ] <criterion 2>

## Classification: AFK | HITL
<reason for classification>

## Blocks / Blocked By
- Blocks: #<issue>
- Blocked by: #<issue>
```

## Rules

1. Every slice must be a vertical tracer bullet — never a horizontal layer
2. Completed slices must be independently verifiable
3. Prefer AFK classification when the scope is unambiguous
4. Publish in dependency order so blocked issues are created after their blockers
