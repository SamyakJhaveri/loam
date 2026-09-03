---
name: writing-plans
description: Use when an approved design or complete requirements need a multi-step implementation plan, before touching code
---

# Writing Plans

## Overview

Turn an approved design into a complete implementation plan. Assume the implementer is
skilled but has no prior context for the repository or problem. Give them exact paths,
interfaces, code, checks, expected results, and small tasks. Use DRY, YAGNI, test-driven
development, and frequent commits.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Input:** An approved design document or complete requirements.

**Save plans to:** `docs/plans/YYYY-MM-DD-<feature-name>.md`

User instructions for the plan location override this default.

## Scope Check

If the design covers independent subsystems, propose separate plans. Each plan must produce
working, testable software on its own. Do not hide unresolved design choices inside an
implementation task. Return unresolved choices to `brainstorming`.

## Map Files and Interfaces First

Before defining tasks, map every file to create, modify, test, or delete. State what each file
owns. Follow repository patterns. Keep units focused and give every boundary an explicit
interface.

For each task, state:

- What it consumes from earlier tasks, with exact names and signatures.
- What it produces for later tasks, with exact names and types.
- Which runnable check proves the task is complete.

## Task Size

A task is the smallest unit with its own test cycle and useful review gate. Fold setup,
configuration, documentation, and scaffolding into the task whose deliverable needs them.
Split tasks only when a reviewer could accept one and reject the other.

Each checklist step is one action. Use this order for behavior changes:

1. Write the failing test.
2. Run it and record the expected failure.
3. Write the minimal implementation.
4. Run the focused test and record the expected pass.
5. Run the wider relevant check.
6. Commit the verified task.

## Plan Header

Every plan starts with this structure:

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** Implement this plan task by task. Use checkbox
> (`- [ ]`) syntax for tracking. Run each task's checks before starting the next task.

**Goal:** [One sentence describing the completed behavior]

**Architecture:** [Two or three sentences describing the approach and boundaries]

**Tech Stack:** [Languages, frameworks, and tools verified in the repository]

## Global Constraints

[Copy each project-wide requirement from the approved design with its exact value.]

---
```

## Task Structure

Use this structure for every task:

````markdown
### Task N: [Testable Deliverable]

**Files:**

- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:line`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**

- Consumes: [exact names, signatures, and types from earlier tasks]
- Produces: [exact names, signatures, and types later tasks use]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input_value)
    assert result == expected_value
```

- [ ] **Step 2: Run the test and verify RED**

Run: `pytest tests/path/test.py::test_specific_behavior -v`

Expected: FAIL because `function` does not implement the required behavior.

- [ ] **Step 3: Write the minimal implementation**

```python
def function(input_value):
    return expected_value
```

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `pytest tests/path/test.py::test_specific_behavior -v`

Expected: PASS.

- [ ] **Step 5: Run the wider relevant check**

Run: `[exact repository test, lint, or build command]`

Expected: `[exact success marker or pass summary]`.

- [ ] **Step 6: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific behavior"
```
````

Use real code from the approved design and repository. The sample above defines structure,
not content to copy unchanged.

## No Placeholders

Every task must contain what the implementer needs. A plan is incomplete if it contains:

- `TBD`, `TODO`, "implement later", or "fill in details".
- "Add validation", "handle errors", or "write tests" without exact behavior and code.
- "Similar to Task N" instead of repeated context needed by that task.
- A code-changing step without the relevant code.
- A function, type, flag, command, or path not verified in the repository or defined by the plan.

## Self-Review

After writing the plan, review it against the approved design:

1. Map every design requirement to a task. Add any missing task.
2. Search for placeholders and vague steps. Replace them with exact content.
3. Check that names, signatures, and types match across tasks.
4. Check that each command exists and each expected result is specific.
5. Check that every task ends in a runnable verification and a commit.

Fix findings in the plan before handoff.

## Execution Handoff

After saving the plan, inspect what execution methods the current host and repository actually
provide. Offer only available choices, in this order:

1. **Repository subagent workflow:** Use the repository's documented subagent process when it
   exists. Dispatch one task at a time and review between tasks.
2. **Current session:** Execute small checked batches here. Stop at the review checkpoints in
   the plan.
3. **Fresh implementation session:** Start a new session with the saved plan and implement it
   task by task.

Name the saved `docs/plans/<filename>.md` path in the handoff. Do not require an execution skill
or command that is absent from the current host.
When the plan will be handed to a fresh session, run `/align-prompt fable-plan <path>` before writing the handoff.
