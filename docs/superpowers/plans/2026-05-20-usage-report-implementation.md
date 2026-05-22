# Usage Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the Claude Code Insights report recommendations as routing-first artifacts in the Loam seed template — guardrails rule, `/ship` orchestrator, three ambitious-pattern skills, plus pipeline ordering updates across all sources of truth.

**Architecture:** All new artifacts route to existing skills/agents rather than reimplementing behavior. The guardrails rule is always-loaded with cross-refs to `workflow.md`. `/ship` is a core orchestrator calling `/session-critique` → `/validate` → `/commit` → `/pr`. The three Tier 3 skills (`/critique-swarm`, `/render-gate`, `/auto-phase`) are specialized (auto-activate: false), each composing existing agents with report prompts used verbatim.

**Tech Stack:** Markdown (SKILL.md, rules), YAML frontmatter, Jinja2 (CLAUDE.md.jinja), Bash (session-start.sh, verification)

**Branch:** All work happens on `rework/usage-report-implementation`. Single commit at end after `/validate`. Squash-merge to main via PR.

**Design spec:** `docs/superpowers/specs/2026-05-20-usage-report-implementation-design.md`

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| CREATE | `seed/.claude/rules/session-guardrails.md` | Always-loaded behavioral constraints (5 guardrails with cross-refs) |
| CREATE | `seed/.claude/skills/ship/SKILL.md` | Orchestrator: critique → validate → commit → PR |
| CREATE | `seed/.claude/skills/critique-swarm/SKILL.md` | 4 parallel adversarial agents + synthesis |
| CREATE | `seed/.claude/skills/render-gate/SKILL.md` | TDD loop for Copier template rendering |
| CREATE | `seed/.claude/skills/auto-phase/SKILL.md` | Autonomous multi-stage plan execution |
| MODIFY | `seed/.claude/rules/workflow.md` (line 74) | Update pipeline ordering to match /ship |
| MODIFY | `seed/.claude/rules/known-issues.md` (lines 8-10) | Update skill tiering for 4 new skills |
| MODIFY | `seed/.claude/hooks/session-start.sh` (lines 16-20, 26) | Update skill count (17→21) and pipeline ordering |
| MODIFY | `seed/CLAUDE.md.jinja` (lines 36, 54) | Add guardrails pointer + fix skill count |

**Pre-existing skills referenced by /ship (verify these exist before writing /ship):**
- `seed/.claude/skills/session-critique/SKILL.md`
- `seed/.claude/skills/validate/SKILL.md`
- `seed/.claude/skills/commit/SKILL.md`
- `seed/.claude/skills/pr/SKILL.md`

---

### Task 0: Branch Setup

- [ ] **Step 1: Create the rework branch**

```bash
git checkout -b rework/usage-report-implementation
```

The project convention (from CLAUDE.md) is: "Don't push to main directly. Use `rework/<topic>` branches + squash-merge."

- [ ] **Step 2: Verify clean starting state**

```bash
git status
git diff --stat HEAD
```

Expected: Clean working tree, no uncommitted changes.

---

### Task 1: Create the Session Guardrails Rule

**Files:**
- Create: `seed/.claude/rules/session-guardrails.md`

- [ ] **Step 1: Write the guardrails rule file**

Write this exact content to `seed/.claude/rules/session-guardrails.md`:

```markdown
# Session Guardrails

> Always loaded. Behavioral constraints derived from usage-report analysis (2026-05-20).
> These address the three most common friction categories: premature execution,
> over-engineering, and unsanctioned edits.

## 1. Workflow Ordering

Run `/session-critique` BEFORE committing or pushing. Never commit until both
critique and `/validate` have passed. The correct sequence is:

**Implement → `/session-critique` → `/validate` → `/commit` → `/pr`**

If `/ship` is available, use it — it enforces this ordering automatically.

See also: `workflow.md` §6 (Pipeline Gate) for the validation loop protocol.

## 2. Plan vs Execute

When asked to produce a plan or handoff document, do NOT begin executing tasks
or creating task lists until the user explicitly approves execution. "Write a plan"
means ONLY write the plan. Do not create TaskCreate calls, do not start implementing,
do not scaffold files. Stop after presenting the plan and wait.

See also: `workflow.md` anti-pattern #1.

## 3. Avoid Over-Engineering

Prefer the simplest solution that meets the requirement. Do not add extra
deliverables, subcommands, or verbose surgical-change preambles unless asked.
When in doubt, ask before expanding scope. One clean solution beats three options
with tradeoff matrices.

## 4. Settings Protection

Never modify or revert the user's `settings.json` beyond what a plan explicitly
specifies. Never re-apply settings changes without asking. If a direct JSON edit
tool fails, use a `python3 -c` workaround rather than silently reverting to a
prior state.

## 5. Skill Placement

Place `/commit`, `/pr`, and other repo workflow skills inside the git repo
(under `.claude/skills/`), not at user level (`~/.claude/skills/`). Default to
generic-core placement rather than duplicating skills across flavors.
```

- [ ] **Step 2: Verify the file**

```bash
head -3 seed/.claude/rules/session-guardrails.md
wc -l seed/.claude/rules/session-guardrails.md
```

Expected: Starts with `# Session Guardrails`, ~45-55 lines. No YAML frontmatter (rules files don't use frontmatter).

---

### Task 2: Create the `/ship` Orchestrator Skill

**Files:**
- Create: `seed/.claude/skills/ship/SKILL.md`

- [ ] **Step 1: Verify the 4 skills that /ship calls exist**

```bash
for skill in session-critique validate commit pr; do
  [ -f "seed/.claude/skills/$skill/SKILL.md" ] && echo "OK: $skill" || echo "MISSING: $skill"
done
```

Expected: All 4 show `OK`. If any is MISSING, stop and report.

- [ ] **Step 2: Create directory and write the SKILL.md**

```bash
mkdir -p seed/.claude/skills/ship
```

Write this exact content to `seed/.claude/skills/ship/SKILL.md`:

```markdown
---
name: ship
description: >
  Orchestrates the full shipping pipeline in strict order. Runs session-critique,
  then validate (full 3-wave), then commit, then PR. Use when work is complete
  and ready to ship. Enforces ordering to prevent premature commits and skipped
  critiques. Accepts optional argument 'critique-only' to run just the critique
  step. NOT for mid-implementation checks (use /validate), code review without
  shipping (use /multi-review), or committing without the full pipeline (use
  /commit directly only if critique + validate already passed).
argument-hint: "[critique-only]"
---

# Ship Pipeline

Strict-ordering orchestrator. Runs four stages in sequence, halting on failure.

## Arguments

- `/ship` (no args) → all 4 stages
- `/ship critique-only` → stage 1 only (session-critique without proceeding to validate/commit/PR — useful for mid-session quality checks)

## Hard Rules

1. **Never skip or reorder stages.** The sequence is: critique → validate → commit → PR.
2. **If stage 1 or 2 fails, do NOT proceed to stage 3.** Fix findings first.
3. **Each stage uses the existing skill's full logic.** Do not reimplement any step inline — invoke the skill.
4. **Report status between stages.** After each stage completes, state what passed and what's next.

## Pipeline

### Stage 1: Session Critique

Invoke `/session-critique`.

This spawns an advisor-pattern agent team that adversarially reviews all work in the current session. It surfaces findings for regressions, over-engineering, dangling references, and scope hygiene.

**Gate:** All HIGH and MEDIUM findings must be resolved (fixed or explicitly dismissed by user) before proceeding. If the user dismisses a finding, record the dismissal reason.

**If `critique-only` was passed:** Stop here. Report findings and exit. Do not proceed to Stage 2.

### Stage 2: Validate

Invoke `/validate` (full — all 3 waves, NOT quick).

This runs the three-wave validation loop: deterministic checks, rule-based tests, probabilistic review. Must produce `.validation_passed` sentinel with `waves_passed=3`.

**Gate:** All waves must pass. On failure, enter the fix loop per `.claude/rules/validation-loop.md`. Max 3 iterations. After 3 fails, halt and escalate to user.

### Stage 3: Commit

Invoke `/commit`.

**Pre-check:** Confirm `.validation_passed` exists and `waves_passed=3` before proceeding. If sentinel is missing or stale, return to Stage 2.

Split commits by scope if the session produced multiple logical changes. Never bundle unrelated changes into a single commit.

### Stage 4: PR

Invoke `/pr`.

Push to remote and open a GitHub PR with summary and test plan.

**Post-check:** Report the PR URL. Pipeline complete.

## Failure Handling

| Failure | Action |
|---------|--------|
| Stage 1 finds HIGH/MEDIUM issues | Fix findings, re-run Stage 1 |
| Stage 2 validation fails | Enter fix loop (max 3 iterations), re-run Stage 2 |
| Stage 3 commit blocked by pre-commit gate | Return to Stage 2 (sentinel likely stale) |
| Stage 4 push fails | Report error, do NOT force push |
| Any stage fails 3 times | Halt pipeline, escalate to user |
```

- [ ] **Step 3: Verify YAML frontmatter parses**

```bash
python3 -c "
import yaml, sys
with open('seed/.claude/skills/ship/SKILL.md') as f:
    content = f.read()
parts = content.split('---', 2)
if len(parts) >= 3:
    data = yaml.safe_load(parts[1])
    print('name:', data.get('name'))
    print('argument-hint:', data.get('argument-hint'))
    desc = data.get('description', '')
    print('description starts:', desc[:60])
    print('YAML: OK')
else:
    print('ERROR: no frontmatter found'); sys.exit(1)
"
```

Expected: `name: ship`, `argument-hint: [critique-only]`, description starts with `Orchestrates`, `YAML: OK`.

---

### Task 3: Create the `/critique-swarm` Skill

**Files:**
- Create: `seed/.claude/skills/critique-swarm/SKILL.md`

- [ ] **Step 1: Create directory and write the SKILL.md**

```bash
mkdir -p seed/.claude/skills/critique-swarm
```

Write this exact content to `seed/.claude/skills/critique-swarm/SKILL.md`:

```markdown
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
| `/session-critique` | Session work (regressions, scope, dangling refs) | Either/or — critique-swarm is more specialized |
| `/validate` | Deterministic + rule-based + probabilistic checks | Yes — different layer |
```

- [ ] **Step 2: Verify YAML frontmatter**

```bash
python3 -c "
import yaml, sys
with open('seed/.claude/skills/critique-swarm/SKILL.md') as f:
    content = f.read()
parts = content.split('---', 2)
if len(parts) >= 3:
    data = yaml.safe_load(parts[1])
    assert data['name'] == 'critique-swarm', f'Wrong name: {data[\"name\"]}'
    assert data['auto-activate'] == False, f'Wrong auto-activate: {data[\"auto-activate\"]}'
    print('YAML: OK — name=critique-swarm, auto-activate=False')
else:
    print('ERROR: no frontmatter'); sys.exit(1)
"
```

Expected: `YAML: OK — name=critique-swarm, auto-activate=False`

---

### Task 4: Create the `/render-gate` Skill

**Files:**
- Create: `seed/.claude/skills/render-gate/SKILL.md`

- [ ] **Step 1: Create directory and write the SKILL.md**

```bash
mkdir -p seed/.claude/skills/render-gate
```

Write this exact content to `seed/.claude/skills/render-gate/SKILL.md`:

```markdown
---
name: render-gate
auto-activate: false
description: >
  TDD rendering gate for Copier template development. Writes E2E assertions first,
  then iteratively fixes the template until all flavors render cleanly. Never commits
  on a red suite. Use when editing Copier template files (copier.yml, .jinja files,
  flavor overlays). NOT for non-template projects, runtime code changes, or
  general testing (use /validate).
---

# Render Gate: TDD Template Rendering

A test-driven development loop for Copier template work. The agent writes rendering
assertions first, then iterates until every flavor passes.

## When to Use

- Editing `copier.yml`, `*.jinja` files, or flavor overlays
- Adding a new Copier question or choice
- Modifying the `_subdirectory`, `_tasks`, or `_templates_suffix` config
- After any change that could affect how the template renders

## When NOT to Use

- Non-template projects → use `/validate`
- Runtime code changes that don't affect template rendering
- Documentation-only edits

## Procedure

### Step 1: Establish the test baseline

Check if `bin/verify-template.sh` exists and what it covers:

```bash
[ -x bin/verify-template.sh ] && echo "verify-template.sh exists" || echo "no verify script"
cat bin/verify-template.sh 2>/dev/null | head -30
```

### Step 2: Write or extend E2E assertions

If `bin/verify-template.sh` exists, use it as the base. If it doesn't cover the
current change, extend it. The assertions must verify:

1. **Every flavor renders** — each combination of Copier choices produces output
2. **Answers file is valid** — `.copier-answers.yml` exists and contains expected keys
3. **Choices mappings are correct** — conditional includes/excludes match the choices
4. **YAML scalars are well-formed** — no unquoted colons, no broken folded scalars
5. **Jinja syntax is valid** — no unclosed tags, no undefined variables

Render from **committed git state** (not working tree) to match Copier's behavior:

```bash
TMPDIR=$(mktemp -d)
uvx copier copy --vcs-ref HEAD --defaults . "$TMPDIR/test-default" 2>&1
echo "Exit code: $?"
ls -la "$TMPDIR/test-default/"
```

### Step 3: Run the full suite and record failures

```bash
bin/verify-template.sh 2>&1
echo "Exit code: $?"
```

### Step 4: Iterative fix loop

For each failure:
1. Read the error output
2. Identify the root cause in the template source
3. Fix the template file
4. Re-run the **full suite** (not just the failing test)
5. Report: what failed, what you fixed, current pass/fail status

**Hard rule:** Never commit while any test is failing. The loop continues until
exit code 0.

### Step 5: Final verification

After all tests pass:

```bash
bin/verify-template.sh 2>&1
echo "Final exit code: $?"
```

Only proceed to commit if exit code is 0. Report the full pass summary.

## Common Failure Patterns

| Symptom | Likely Cause |
|---------|-------------|
| `copier copy` fails with "not a git repo" | Need `--vcs-ref HEAD`; template must be committed |
| YAML parse error in rendered output | Unquoted colon in a Jinja variable or description field |
| Missing file in rendered output | Conditional include/exclude doesn't match the flavor choices |
| `.copier-answers.yml` missing keys | New question added to `copier.yml` without a default |
| Jinja `UndefinedError` | Variable name mismatch between `copier.yml` and template |
```

- [ ] **Step 2: Verify YAML frontmatter**

```bash
python3 -c "
import yaml, sys
with open('seed/.claude/skills/render-gate/SKILL.md') as f:
    content = f.read()
parts = content.split('---', 2)
if len(parts) >= 3:
    data = yaml.safe_load(parts[1])
    assert data['name'] == 'render-gate', f'Wrong name: {data[\"name\"]}'
    assert data['auto-activate'] == False, f'Wrong auto-activate: {data[\"auto-activate\"]}'
    print('YAML: OK — name=render-gate, auto-activate=False')
else:
    print('ERROR: no frontmatter'); sys.exit(1)
"
```

Expected: `YAML: OK — name=render-gate, auto-activate=False`

---

### Task 5: Create the `/auto-phase` Skill

**Files:**
- Create: `seed/.claude/skills/auto-phase/SKILL.md`

- [ ] **Step 1: Create directory and write the SKILL.md**

```bash
mkdir -p seed/.claude/skills/auto-phase
```

Write this exact content to `seed/.claude/skills/auto-phase/SKILL.md`:

```markdown
---
name: auto-phase
auto-activate: false
description: >
  Autonomous multi-phase release execution. Reads a PHASE-PLAN.md with stages 1-N
  and executes them end-to-end, running validation + critique per stage, committing
  with clean scope, and advancing automatically. Halts only when a validation gate
  fails twice or a critique surfaces an unresolvable issue. Use for multi-stage
  release plans, phased restructures, or any numbered-phase execution. NOT for
  single-stage work (use /ship), plan creation (use brainstorming), or work without
  a written phase plan.
argument-hint: "[path to phase plan, defaults to PHASE-PLAN.md]"
---

# Auto-Phase: Autonomous Multi-Stage Execution

Reads a phase plan and executes stages autonomously, one at a time, with
validation and critique gates between each stage.

## When to Use

- You have a PHASE-PLAN.md (or similar) with numbered stages 1-N
- Each stage is self-contained and can be validated independently
- You want autonomous execution with human oversight only on failures

## When NOT to Use

- Single-stage work → use `/ship`
- No written phase plan exists → write one first (use brainstorming + writing-plans)
- Exploratory or uncertain work → plan first, then auto-phase

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
files, modify configurations — whatever the stage specifies.

#### 2c. Run validation pipeline

Invoke `/validate` (full 3-wave). If validation fails:

- **First failure:** Fix the issues and re-run `/validate`.
- **Second failure on same stage:** HALT. Report the failure and ask the user.

```
=== STAGE K/N: VALIDATION FAILED (attempt 2/2) ===
Failure: [description]
Action: Halting for user input. The stage contract may need revision.
```

#### 2d. Run session critique

Invoke `/session-critique` for the current stage's changes only. If critique
surfaces HIGH/MEDIUM findings:

- Attempt to fix automatically if the fix is clear and contained.
- If the fix requires judgment or scope expansion: HALT and ask the user.

#### 2e. Commit with clean scope

Invoke `/commit`. The commit must contain ONLY this stage's changes. Never
bundle changes from other stages.

#### 2f. Update progress tracking

After successful commit, update `TASKS.md` (create if it doesn't exist):

```markdown
## Auto-Phase Progress

| Stage | Status | Commit | Notes |
|-------|--------|--------|-------|
| 1 | DONE | abc1234 | [summary] |
| 2 | DONE | def5678 | [summary] |
| 3 | IN PROGRESS | — | — |
```

#### 2g. Advance to next stage

```
=== STAGE K/N: COMPLETE ===
Commit: [hash]
Advancing to Stage K+1...
```

### Step 3: Completion report

After all stages complete:

```
=== AUTO-PHASE COMPLETE ===
Plan: [plan file]
Stages: N/N completed
Commits: [list of hashes]
Total changes: [file count summary]

All stages passed validation and critique gates.
```

## Stopping Conditions

| Condition | Action |
|-----------|--------|
| Validation fails twice on same stage | HALT — ask user, stage contract likely needs revision |
| Critique finds unresolvable issue | HALT — present issue and ask user |
| Plan file not found | HALT — report error immediately |
| Stage instructions are ambiguous | HALT — ask user to clarify before implementing |
| All stages complete | Report summary, pipeline done |

## Hard Rules

1. **One stage at a time.** Never start stage K+1 before stage K is committed.
2. **Never bundle cross-stage changes.** Each commit contains exactly one stage.
3. **Never skip validation or critique.** Every stage passes both gates.
4. **Halt on ambiguity.** If a stage's instructions are unclear, ask — don't guess.
5. **Track progress.** Update TASKS.md after every stage so a fresh session can resume.
```

- [ ] **Step 2: Verify YAML frontmatter**

```bash
python3 -c "
import yaml, sys
with open('seed/.claude/skills/auto-phase/SKILL.md') as f:
    content = f.read()
parts = content.split('---', 2)
if len(parts) >= 3:
    data = yaml.safe_load(parts[1])
    assert data['name'] == 'auto-phase', f'Wrong name: {data[\"name\"]}'
    assert data['auto-activate'] == False, f'Wrong auto-activate: {data[\"auto-activate\"]}'
    print('YAML: OK — name=auto-phase, auto-activate=False')
else:
    print('ERROR: no frontmatter'); sys.exit(1)
"
```

Expected: `YAML: OK — name=auto-phase, auto-activate=False`

---

### Task 6: Update Pipeline Ordering Across All Sources of Truth

**Why this task exists:** The existing canonical pipeline is `Implement → /multi-review → /validate → commit → push`. The new `/ship` skill uses `session-critique → validate → commit → PR`. Without updating ALL sources, a fresh session sees contradictory instructions from always-loaded files. There are exactly 3 locations to update.

**Files:**
- Modify: `seed/.claude/rules/workflow.md` (line 74)
- Modify: `seed/.claude/hooks/session-start.sh` (line 26)
- Modify: `seed/CLAUDE.md.jinja` (the pipeline anchor line)

- [ ] **Step 1: Update workflow.md line 74**

Read `seed/.claude/rules/workflow.md` and find line 74:
```
**Critical ordering:** Implement → `/multi-review` → `/validate` (Pipeline Gate) → commit → push
```

Replace with:
```
**Critical ordering:** Implement → `/session-critique` → `/validate` (Pipeline Gate) → `/commit` → `/pr` (or use `/ship` to enforce this automatically)
```

- [ ] **Step 2: Update session-start.sh line 26**

Read `seed/.claude/hooks/session-start.sh` and find line 26:
```
  Implement → /multi-review → /validate (Pipeline Gate) → commit → push
```

Replace with:
```
  Implement → /session-critique → /validate (Pipeline Gate) → /commit → /pr
  Use /ship to enforce this ordering automatically.
```

- [ ] **Step 3: Update CLAUDE.md.jinja pipeline anchor**

Read `seed/CLAUDE.md.jinja` and find the line (near the bottom of the `## Quality` section):
```
Implement → /multi-review → /validate (Pipeline Gate) → commit → push
```

Replace with:
```
Implement → /session-critique → /validate (Pipeline Gate) → /commit → /pr (or `/ship`)
```

- [ ] **Step 4: Also update the root CLAUDE.md**

The root `CLAUDE.md` has the same pipeline text at line 61. Read it and make the same replacement:

Find:
```
Implement → /multi-review → /validate (Pipeline Gate) → commit → push
```

Replace with:
```
Implement → /session-critique → /validate (Pipeline Gate) → /commit → /pr (or `/ship`)
```

- [ ] **Step 5: Verify consistency across all 4 files**

```bash
echo "=== Pipeline ordering in all sources ==="
grep -n "Implement.*validate.*commit" seed/.claude/rules/workflow.md
grep -n "Implement.*validate.*commit" seed/.claude/hooks/session-start.sh
grep -n "Implement.*validate.*commit" seed/CLAUDE.md.jinja
grep -n "Implement.*validate.*commit" CLAUDE.md
```

Expected: All 4 lines show the new ordering with `/session-critique` and `/ship`.

---

### Task 7: Update Skill Count and Tiering

**Files:**
- Modify: `seed/.claude/hooks/session-start.sh` (lines 16-22)
- Modify: `seed/.claude/rules/known-issues.md` (lines 8-10)
- Modify: `seed/CLAUDE.md.jinja` (line ~54)

- [ ] **Step 1: Update session-start.sh skill count and categories**

Read `seed/.claude/hooks/session-start.sh`. Find lines 16-22:

```
CORE SKILLS (.claude/skills/ — 17 total):
  Daily loop:    catchup, feature-dev, fix-bug, multi-review, validate, commit, pr, handoff
  Knowledge:     researcher, dream
  Framework:     create-skill, template-sync, scaffold-context
  Quality gate:  session-critique, techdebt
  Spec workflow: gen-spec
  Agent tooling: agent-team
```

Replace with:

```
CORE SKILLS (.claude/skills/ — 21 total):
  Daily loop:    catchup, feature-dev, fix-bug, multi-review, validate, commit, pr, handoff
  Ship pipeline: ship (orchestrates critique→validate→commit→PR)
  Knowledge:     researcher, dream
  Framework:     create-skill, template-sync, scaffold-context
  Quality gate:  session-critique, techdebt
  Spec workflow: gen-spec
  Agent tooling: agent-team
  Specialized:   critique-swarm, render-gate, auto-phase (invoke with /name)
```

- [ ] **Step 2: Update known-issues.md skill tiering**

Read `seed/.claude/rules/known-issues.md`. Find the `**Do:**` line (line ~9):

```
**Do:** Core workflow skills (agent-team, catchup, commit, create-skill, dream, feature-dev, fix-bug, gen-spec, handoff, multi-review, pr, researcher, scaffold-context, session-critique, techdebt, template-sync, validate) keep default. Specialized skills use `auto-activate: false` — user invokes with `/skill-name`.
```

Replace with:

```
**Do:** Core workflow skills (agent-team, catchup, commit, feature-dev, fix-bug, gen-spec, handoff, multi-review, pr, scaffold-context, session-critique, ship, validate) keep default. Specialized skills (auto-phase, create-skill, critique-swarm, dream, render-gate, researcher, techdebt, template-sync) use `auto-activate: false` — user invokes with `/skill-name`.
```

Note: This corrects the existing inaccuracy where skills with `auto-activate: false` (create-skill, dream, researcher, techdebt, template-sync) were listed as core. The updated list reflects actual `auto-activate` status.

- [ ] **Step 3: Update CLAUDE.md.jinja skill count**

Read `seed/CLAUDE.md.jinja`. Find the line (in `## Project skills`):

```
See `.claude/skills/` (19 core skills).
```

Replace with:

```
See `.claude/skills/` (21 skills — 13 core, 8 specialized). Use `/skill-name` to invoke specialized skills.
```

(Actual count: 17 existing + 4 new = 21 total. Core with auto-activate default/true: 13. Specialized with auto-activate false: 8.)

- [ ] **Step 4: Verify session-start.sh skill count matches actual**

```bash
ACTUAL=$(find seed/.claude/skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
BRIEF=$(grep -oE '[0-9]+ total' seed/.claude/hooks/session-start.sh | grep -oE '[0-9]+')
echo "Actual directories: $ACTUAL"
echo "session-start.sh says: $BRIEF"
[ "$ACTUAL" = "$BRIEF" ] && echo "MATCH" || echo "MISMATCH — fix session-start.sh"
```

Expected: Both show `21`, `MATCH`.

---

### Task 8: Add Guardrails Pointer to CLAUDE.md.jinja

**Files:**
- Modify: `seed/CLAUDE.md.jinja` (Reference Docs table)

- [ ] **Step 1: Add the pointer**

Read `seed/CLAUDE.md.jinja`. Find the Reference Docs table. After the `known-issues.md` row:

```
| `known-issues.md`          | Always — recurring gotchas |
```

Insert a new row immediately after it:

```
| `session-guardrails.md`    | Always — behavioral constraints (workflow ordering, plan vs execute, elegance) |
```

- [ ] **Step 2: Verify the pointer appears**

```bash
grep "session-guardrails" seed/CLAUDE.md.jinja
```

Expected: One line containing `session-guardrails.md` in the Reference Docs table.

---

### Task 9: End-to-End Verification

- [ ] **Step 1: Verify all 5 new files exist**

```bash
echo "=== New files ==="
for f in \
  seed/.claude/rules/session-guardrails.md \
  seed/.claude/skills/ship/SKILL.md \
  seed/.claude/skills/critique-swarm/SKILL.md \
  seed/.claude/skills/render-gate/SKILL.md \
  seed/.claude/skills/auto-phase/SKILL.md; do
  [ -f "$f" ] && echo "OK: $f" || echo "MISSING: $f"
done
```

Expected: All 5 show `OK`.

- [ ] **Step 2: Verify all YAML frontmatter**

```bash
echo "=== YAML frontmatter ==="
for f in ship critique-swarm render-gate auto-phase; do
  python3 -c "
import yaml, sys
path = 'seed/.claude/skills/$f/SKILL.md'
with open(path) as fh:
    parts = fh.read().split('---', 2)
if len(parts) >= 3:
    d = yaml.safe_load(parts[1])
    aa = d.get('auto-activate', 'default-true')
    print(f'OK: {path} → name={d[\"name\"]}, auto-activate={aa}')
else:
    print(f'FAIL: {path}'); sys.exit(1)
" 2>&1
done
```

Expected: ship=default-true, others=False.

- [ ] **Step 3: Verify pipeline ordering consistency**

```bash
echo "=== Pipeline ordering ==="
grep "session-critique.*validate" seed/.claude/rules/workflow.md && echo "workflow.md: OK"
grep "session-critique.*validate" seed/.claude/hooks/session-start.sh && echo "session-start.sh: OK"
grep "session-critique.*validate" seed/CLAUDE.md.jinja && echo "CLAUDE.md.jinja: OK"
grep "session-critique.*validate" CLAUDE.md && echo "CLAUDE.md: OK"
```

Expected: All 4 show the new ordering, all OK.

- [ ] **Step 4: Verify skill count matches**

```bash
ACTUAL=$(find seed/.claude/skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
BRIEF=$(grep -oE '[0-9]+ total' seed/.claude/hooks/session-start.sh | grep -oE '[0-9]+')
echo "Actual: $ACTUAL, session-start.sh: $BRIEF"
[ "$ACTUAL" = "$BRIEF" ] && echo "MATCH" || echo "MISMATCH"
```

Expected: `21`, `MATCH`.

- [ ] **Step 5: Verify symlink makes new files accessible from project root**

```bash
ls .claude/rules/session-guardrails.md && echo "Guardrails: accessible"
ls .claude/skills/ship/SKILL.md && echo "Ship: accessible"
```

Expected: Both accessible via the `.claude → seed/.claude` symlink.

- [ ] **Step 6: Run bin/verify-template.sh**

```bash
bin/verify-template.sh
```

Expected: `ALL OK` — this validates skill count match, YAML frontmatter, JSON validity, and Copier rendering. This is the definitive gate.

- [ ] **Step 7: Run /validate and commit**

After verify-template.sh passes, run `/validate` (full 3-wave) to produce the `.validation_passed` sentinel. Then commit all changes as a single commit on the rework branch:

```bash
git add \
  seed/.claude/rules/session-guardrails.md \
  seed/.claude/skills/ship/SKILL.md \
  seed/.claude/skills/critique-swarm/SKILL.md \
  seed/.claude/skills/render-gate/SKILL.md \
  seed/.claude/skills/auto-phase/SKILL.md \
  seed/.claude/rules/workflow.md \
  seed/.claude/rules/known-issues.md \
  seed/.claude/hooks/session-start.sh \
  seed/CLAUDE.md.jinja \
  CLAUDE.md

git commit -m "feat: add /ship orchestrator, /critique-swarm, /render-gate, /auto-phase skills and session guardrails

Implements recommendations from Claude Code Insights report (2026-05-20):
- Session guardrails rule (5 behavioral constraints)
- /ship orchestrator (critique→validate→commit→PR pipeline)
- /critique-swarm (4-agent parallel adversarial review)
- /render-gate (TDD template rendering loop)
- /auto-phase (autonomous multi-stage execution)
- Pipeline ordering updated across all sources of truth
- Skill count corrected (21 total: 13 core + 8 specialized)"
```

- [ ] **Step 8: Open PR for squash-merge to main**

```bash
git push -u origin rework/usage-report-implementation
gh pr create --title "feat: usage report implementation — /ship, guardrails, ambitious patterns" --body "$(cat <<'EOF'
## Summary
- Adds session-guardrails.md rule (5 always-loaded behavioral constraints)
- Adds /ship orchestrator skill (critique→validate→commit→PR)
- Adds 3 specialized skills: /critique-swarm, /render-gate, /auto-phase
- Updates pipeline ordering in workflow.md, session-start.sh, CLAUDE.md.jinja, CLAUDE.md
- Corrects skill count and tiering in known-issues.md and session-start.sh

## Test plan
- [ ] verify-template.sh passes (skill count, YAML frontmatter, Copier render)
- [ ] /validate full 3-wave passes
- [ ] Pipeline ordering consistent across all 4 sources
- [ ] New skills visible via .claude symlink
EOF
)"
```

---

## Rollback

If implementation fails at any task, all prior tasks' work is uncommitted (single commit strategy). To abandon:

```bash
git checkout main
git branch -D rework/usage-report-implementation
```

No cleanup needed since nothing was committed.

---

## Summary of Changes from Adversarial Review

The plan-reviewer surfaced 13 issues. These fixes were applied:

| # | Issue | Fix Applied |
|---|-------|-------------|
| 1 | Pipeline ordering contradicts across 3 files | Added Task 6 to update all sources of truth |
| 2 | session-start.sh skill count breaks verify-template.sh | Added to Task 7 with exact old/new strings |
| 3 | session-start.sh pipeline ordering also contradicts | Included in Task 6 |
| 4 | known-issues.md edit under-specified | Exact old/new strings with line references |
| 5 | CLAUDE.md.jinja skill count already wrong | Corrected to actual count (21 = 13 core + 8 specialized) |
| 6 | /ship has no explicit auto-activate | Intentional — convention is omit=true. Plan notes this |
| 7 | Per-task commits trigger pre-commit gate | Changed to single commit at end after /validate |
| 8 | Task 7 missing line numbers | Added line references to all edit instructions |
| 9 | Guardrails partially duplicate workflow.md | Added cross-refs ("See also: workflow.md §6") |
| 10 | YAML colon handling | Confirmed: all skills use folded scalar correctly. No fix needed |
| 11 | No rollback instructions | Added Rollback section |
| 12 | argument-hint not validated | Added to YAML verification checks |
| 13 | Plan commits directly to main | Added Task 0: branch creation |
