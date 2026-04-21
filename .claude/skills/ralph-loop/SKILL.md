---
name: ralph-loop
description: Stateless iterative task execution loop. Use when you have a task file with N independent tasks that should each run to success with commit after each, forced reflection every 3 iterations, and max 8 retries per task. NOT for interactive multi-step planning (use feature-dev or gsd-plan-phase).
---

# Ralph Loop — Stateless Iterative Task Execution

The Ralph Loop pattern (via Geoffrey Huntley/Ryan Carson, popularized by Osmani).
Executes a sequence of tasks from a JSON file, committing after each success,
with built-in retry limits, forced reflection, and context management. Designed
for overnight or long-running autonomous work on a feature branch.

**Trigger:** When user types `/ralph-loop <tasks-file>` or `/ralph-loop`

## Arguments

- `$ARGUMENTS` — path to tasks JSON file (e.g., `docs/ralph-tasks.json`,
  `tasks.json`). If omitted, prompt the user for the file path.

## Prerequisites

- Project root: `{{PROJECT_ROOT}}`
- Venv: `source {{PROJECT_ROOT}}/env_parbench/bin/activate`
- Must be on a **feature branch** — NEVER run on `main`
- Tasks file must exist and be valid JSON

## Constants

```
MAX_ITERATIONS = 8        # Max retry attempts per task
REFLECT_EVERY  = 3        # Force reflection every N iterations on same task
PROJECT_ROOT   = {{PROJECT_ROOT}}
PROGRESS_LOG   = docs/ralph-progress.md
```

## Tasks File Format

The tasks file is a JSON array of task objects:

```json
[
  {
    "id": 1,
    "task": "Fix the build error in rodinia-srad-omp spec",
    "status": "pending",
    "file": "specs/rodinia-srad-omp.json"
  },
  {
    "id": 2,
    "task": "Update eval_summary.md with new pass rates",
    "status": "pending",
    "file": "results/evaluation/eval_summary.md",
    "depends_on": 1
  },
  {
    "id": 3,
    "task": "Refresh dashboard numbers",
    "status": "blocked",
    "depends_on": 2
  }
]
```

Field definitions:
- `id` — unique integer identifier
- `task` — human-readable description of what to do
- `status` — one of: `"pending"`, `"blocked"`, `"in_progress"`, `"done"`, `"failed"`, `"skipped"`
- `file` — optional: primary file the task operates on
- `depends_on` — optional: ID of task that must complete first (single int or array of ints)

## Workflow

### Phase 0: Pre-flight Checks

Before entering the loop, verify safety invariants:

```bash
cd {{PROJECT_ROOT}}

# SAFETY: Must be on a feature branch, not main
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "ABORT: Ralph Loop refuses to run on $BRANCH. Create a feature branch first."
  echo "  git checkout -b ralph/<task-description>"
  exit 1
fi
echo "Branch: $BRANCH (OK — not main)"

# Verify tasks file exists
if [ ! -f "$TASKS_FILE" ]; then
  echo "ABORT: Tasks file not found: $TASKS_FILE"
  exit 1
fi

# Validate JSON
python3 -c "import json; json.load(open('$TASKS_FILE'))" 2>&1 || {
  echo "ABORT: Tasks file is not valid JSON"
  exit 1
}

# Show task summary
python3 -c "
import json
tasks = json.load(open('$TASKS_FILE'))
for t in tasks:
    dep = t.get('depends_on', '-')
    print(f\"  [{t['id']}] {t['status']:12s} {t['task'][:60]}  (dep: {dep})\")
"
```

**Gate:** If on main, STOP. If tasks file is invalid, STOP. Otherwise, proceed.

### Phase 1: Read Memory Channels

At the start of each loop iteration, read all four memory channels:

```bash
cd {{PROJECT_ROOT}}

echo "=== MEMORY CHANNEL 1: Git History ==="
git log --oneline -5

echo "=== MEMORY CHANNEL 2: Progress Log ==="
cat docs/ralph-progress.md 2>/dev/null || echo "(no progress log yet)"

echo "=== MEMORY CHANNEL 3: Task State ==="
python3 -c "
import json
tasks = json.load(open('$TASKS_FILE'))
for t in tasks:
    print(f\"  [{t['id']}] {t['status']:12s} {t['task'][:60]}\")
"

echo "=== MEMORY CHANNEL 4: CLAUDE.md ==="
head -30 CLAUDE.md
```

### Phase 2: Select Next Task

Find the next actionable task:

```python
import json

tasks = json.load(open(TASKS_FILE))

# Unblock tasks whose dependencies are done
done_ids = {t["id"] for t in tasks if t["status"] == "done"}
for t in tasks:
    deps = t.get("depends_on", [])
    if isinstance(deps, int):
        deps = [deps]
    if t["status"] == "blocked" and all(d in done_ids for d in deps):
        t["status"] = "pending"

# Find next pending task (lowest ID first)
next_task = None
for t in sorted(tasks, key=lambda x: x["id"]):
    if t["status"] == "pending":
        next_task = t
        break

if next_task is None:
    # All done or all failed/blocked
    remaining = [t for t in tasks if t["status"] not in ("done", "failed", "skipped")]
    if remaining:
        print("STUCK: remaining tasks are all blocked or failed")
    else:
        print("ALL TASKS COMPLETE")
```

If no task is available, go to Phase 6 (Completion).

### Phase 3: Execute Task

Mark the task as `"in_progress"` in the tasks file, then execute it:

1. **Read the target file** (if `file` is specified in the task)
2. **Understand the task** — what needs to change and why
3. **Implement the change** — edit files, run commands as needed
4. **Validate the change:**
   - If the task involves specs: run `python3 -m harness -v verify specs/<name>.json`
   - If the task involves Python: run `python3 -m pytest` on relevant tests
   - If the task involves scripts: run the script and check output
   - If no specific validation exists: verify the file was modified as expected

Track the iteration count for this task. Initialize to 1 on first attempt.

### Phase 4: Evaluate Result

**On SUCCESS (validation passes):**

1. Mark task as `"done"` in tasks file
2. Write tasks file back to disk
3. Commit the change (feature branch only!):
   ```bash
   cd {{PROJECT_ROOT}}
   git add -A
   git commit -m "$(cat <<'EOF'
   ralph-loop: <task description> (task #<id>)

   Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
   EOF
   )"
   ```
4. Append to progress log:
   ```bash
   echo "- [$(date -u +%Y-%m-%dT%H:%M:%SZ)] Task #<id> DONE: <task description>" >> docs/ralph-progress.md
   ```
5. Go to Phase 1 (next iteration)

**On FAILURE (validation fails or error occurs):**

1. Increment iteration count for this task
2. If iteration count is a multiple of REFLECT_EVERY (3, 6):
   - **Forced reflection pause.** Before retrying, answer these three questions:
     ```
     FORCED REFLECTION (iteration <N> on task #<id>):
     1. What specifically failed? <error message or test output>
     2. What would fix it? <concrete hypothesis, not "try again">
     3. Am I repeating myself? <compare to previous attempts>
     ```
   - If the answer to #3 is YES, try a fundamentally different approach
3. If iteration count >= MAX_ITERATIONS (8):
   - Mark task as `"failed"` in tasks file
   - Append to progress log:
     ```bash
     echo "- [$(date -u +%Y-%m-%dT%H:%M:%SZ)] Task #<id> FAILED after $MAX_ITERATIONS iterations: <last error>" >> docs/ralph-progress.md
     ```
   - Do NOT commit failed work — revert uncommitted changes:
     ```bash
     git checkout -- .
     ```
   - Go to Phase 2 (try next task)
4. Otherwise: retry from Phase 3 with the new approach from reflection

### Phase 5: Context Management

After completing or failing each task, run `/compact` to reset the context window:

```
/compact "Ralph Loop: completed task #<id>, moving to next task"
```

This is essential for long-running loops — without compaction, the context fills up
and quality degrades. The four memory channels (Phase 1) restore necessary context
after compaction.

### Phase 6: Completion

When all tasks are done, failed, or blocked:

```bash
cd {{PROJECT_ROOT}}

echo "=== RALPH LOOP COMPLETE ==="
python3 -c "
import json
tasks = json.load(open('$TASKS_FILE'))
done = sum(1 for t in tasks if t['status'] == 'done')
failed = sum(1 for t in tasks if t['status'] == 'failed')
blocked = sum(1 for t in tasks if t['status'] == 'blocked')
skipped = sum(1 for t in tasks if t['status'] == 'skipped')
total = len(tasks)
print(f'  Done:    {done}/{total}')
print(f'  Failed:  {failed}/{total}')
print(f'  Blocked: {blocked}/{total}')
print(f'  Skipped: {skipped}/{total}')
"

echo ""
echo "Progress log: docs/ralph-progress.md"
echo "Tasks file:   $TASKS_FILE"
echo ""
echo "Git log (ralph commits):"
git log --oneline --grep="ralph-loop" | head -10
```

Present the final summary and suggest:
```
Suggested next steps:
  [ ] Review commits: git log --oneline --grep="ralph-loop"
  [ ] Check failed tasks in $TASKS_FILE
  [ ] Run /validate before merging to main
  [ ] Run /reflect to capture learnings from the loop
```

## Safety Invariants

1. **NEVER commit to main** — pre-flight check enforces this. If somehow on main, ABORT.
2. **NEVER force-push** — commits are additive only.
3. **NEVER modify files outside the task scope** — each task's `file` field defines scope.
4. **Revert on failure** — uncommitted changes from failed tasks are reverted.
5. **MAX_ITERATIONS is a hard limit** — no exceptions. If 8 attempts fail, the task fails.
6. **Forced reflection prevents blind retry loops** — every 3 iterations, the loop MUST
   pause and reason about why it's failing before trying again.
7. **Context compaction after each task** — prevents context window exhaustion.

## Progress Log Format

`docs/ralph-progress.md` is append-only during a loop run:

```markdown
# Ralph Loop Progress

Started: YYYY-MM-DDTHH:MM:SSZ
Tasks file: <path>
Branch: <feature-branch-name>

## Log

- [2026-04-01T10:00:00Z] Task #1 DONE: Fix srad-omp spec build error
- [2026-04-01T10:05:00Z] Task #2 DONE: Update eval_summary.md
- [2026-04-01T10:12:00Z] Task #3 FAILED after 8 iterations: dashboard refresh script error
- [2026-04-01T10:12:30Z] Loop complete: 2/3 done, 1/3 failed
```

## Anti-Patterns

1. **Don't skip forced reflection** — the 3-iteration reflection is load-bearing. Without it,
   the loop degenerates into "retry the same thing 8 times."
2. **Don't increase MAX_ITERATIONS** — 8 is already generous. If it can't be solved in 8
   tries, it needs human intervention.
3. **Don't skip context compaction** — the loop WILL degrade without it. Each task should
   start with a fresh context window.
4. **Don't run on main** — this is non-negotiable. Feature branches only.
5. **Don't batch commits** — commit after EACH successful task. This makes rollback granular.
