---
name: auto-phase
disable-model-invocation: true
description: >
  Autonomous multi-phase release execution. Reads a PHASE-PLAN.md with stages 1-N
  and executes them end-to-end, running validation per stage and session critique at the
  end of the plan (per stage when a stage touches seed/, hooks, or copier.yml), committing
  with clean scope, and advancing automatically. Halts only when a validation gate
  fails twice or a critique surfaces an unresolvable issue. Use for multi-stage
  release plans, phased restructures, or any numbered-phase execution. NOT for
  single-stage work (use /ship), plan creation (use brainstorming), or work without
  a written phase plan. Use when you have a numbered-phase plan ready for execution.
argument-hint: "[path to phase plan, defaults to PHASE-PLAN.md]"
---

# Auto-Phase: Autonomous Multi-Stage Execution

Reads a phase plan and executes stages autonomously, one at a time, with
validation and critique gates between each stage.

**Requires the `ship` and `session-critique` skills** (plus `validate`, which
`ship` also depends on). If they are not installed, stop and say so rather than
improvising the gates.

## When to Use

- You have a PHASE-PLAN.md (or similar) with numbered stages 1-N
- Each stage is self-contained and can be validated independently
- You want autonomous execution with human oversight only on failures

## When NOT to Use

- Single-stage work -> use `/ship`
- No written phase plan exists -> write one first (use brainstorming + writing-plans)
- Exploratory or uncertain work -> plan first, then auto-phase

## Prerequisites

1. A phase plan file exists (default: `PHASE-PLAN.md` in project root)
2. Each stage in the plan specifies: what to implement, expected output, done criteria
3. The project has `/validate` and `/session-critique` available

## Procedure

### Step 1: Read and parse the phase plan

```bash
PLAN_FILE="${ARGUMENTS:-PHASE-PLAN.md}"
[ -f "$PLAN_FILE" ] && echo "Plan found: $PLAN_FILE" || echo "ERROR: $PLAN_FILE not found"
```

Parse the plan to identify:
- Total number of stages
- Each stage's scope, files, and done criteria
- Dependencies between stages (if any)

Present the parsed stage list to the user for confirmation before starting.

### Step 2: Execute stages autonomously

For each stage (1 through N):

#### 2a. Announce stage start

```
=== STAGE K/N: [Stage Title] ===
Status: STARTING
```

#### 2b. Implement the stage's changes

Follow the stage's instructions from the plan. Make the code changes, create
files, modify configurations, whatever the stage specifies.

#### 2c. Run validation pipeline

Invoke `/validate`. If validation fails:

- **First failure:** Fix the issues and re-run `/validate`.
- **Second failure on same stage:** HALT. Report the failure and ask the user.

```
=== STAGE K/N: VALIDATION FAILED (attempt 2/2) ===
Failure: [description]
Action: Halting for user input. The stage contract may need revision.
```

#### 2d. Run session critique when the stage is template-facing

Run `/session-critique` for this stage's changes only when the stage touched `seed/`,
`.claude/hooks/`, `.codex/`, or `copier.yml` (check `git diff --name-only HEAD`).
Otherwise skip; the end-of-plan critique in Step 3 covers it. If critique surfaces
HIGH/MEDIUM findings:

- Attempt to fix automatically if the fix is clear and contained.
- If the fix requires judgment or scope expansion: HALT and ask the user.

#### 2e. Commit with clean scope

Commit inline with git. The commit must contain ONLY this stage's changes.
Never bundle changes from other stages.

```bash
git status --short
git add <this stage's paths>
git commit -m "<type>: <stage K subject>"
git rev-parse --short HEAD
```

If the native pre-commit hook rejects the commit, treat it as a validation
failure for this stage and return to step 2c.

#### 2f. Update progress tracking

After successful commit, update `TASKS.md` (create if it doesn't exist):

```markdown
## Auto-Phase Progress

| Stage | Status | Commit | Notes |
|-------|--------|--------|-------|
| 1 | DONE | abc1234 | [summary] |
| 2 | DONE | def5678 | [summary] |
| 3 | IN PROGRESS | - | - |
```

#### 2g. Advance to next stage

```
=== STAGE K/N: COMPLETE ===
Commit: [hash]
Advancing to Stage K+1...
```

### Step 3: End-of-plan critique

Invoke `/session-critique` once over all stages' changes
(`git diff --name-only <first stage's parent commit>..HEAD`). Handle findings as
in 2d; a fix lands as its own follow-up commit, never by amending a stage commit.

### Step 4: Completion report

After all stages complete:

```
=== AUTO-PHASE COMPLETE ===
Plan: [plan file]
Stages: N/N completed
Commits: [list of hashes]
Total changes: [file count summary]

All stages passed validation; the end-of-plan critique ran.
```

## Stopping Conditions

| Condition | Action |
|-----------|--------|
| Validation fails twice on same stage | HALT, ask user, stage contract likely needs revision |
| Critique finds unresolvable issue | HALT, present issue and ask user |
| Plan file not found | HALT, report error immediately |
| Stage instructions are ambiguous | HALT, ask user to clarify before implementing |
| All stages complete | Report summary, pipeline done |

## Hard Rules

1. **One stage at a time.** Never start stage K+1 before stage K is committed.
2. **Never bundle cross-stage changes.** Each commit contains exactly one stage.
3. **Never skip validation or the end-of-plan critique.** Every stage passes the
   validation gate; template-facing stages also pass a per-stage critique.
4. **Halt on ambiguity.** If a stage's instructions are unclear, ask, don't guess.
5. **Track progress.** Update TASKS.md after every stage so a fresh session can resume.
