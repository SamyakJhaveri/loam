# Feature Development Workflow

Structured workflow for implementing a new feature in ParBench.

## Arguments
- `$ARGUMENTS` — feature name/description

## Workflow

### Phase 1: Explore
Use 3-5 parallel subagents to explore the areas of the codebase relevant to this feature.
Do NOT read code directly in the main context — delegate to subagents.
Summarize findings before proceeding.

### Phase 2: Spec
Enter plan mode. Draft the implementation plan:
- Files to create/modify
- Dependencies affected
- Test strategy
- Risk assessment

Present the plan and **wait for user approval** before proceeding.

### Phase 3: Implement
- Work through the plan step by step
- Use subagents for independent subtasks (with worktree isolation if needed)
- Verify each step compiles/passes before moving on
- Run relevant tests after each significant change

### Phase 4: Verify
Launch verification subagents in parallel:
1. **Correctness** — do the changes work as intended?
2. **Edge cases** — what could break?
3. **Quality** — code style, naming, complexity
4. **Integration** — `python3 scripts/validate_schema.py --all` still passes?

### Phase 5: Record
- Update CLAUDE.md if any new conventions or gotchas were discovered
- Summarize what was done and any follow-up items
