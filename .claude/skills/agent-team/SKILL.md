---
name: creating-agent-teams
description: Creates and launches coordinated agent teams using TeamCreate for multi-teammate tasks requiring cross-talk, shared task lists, and lifecycle management. Use when 2+ workers need to communicate findings to each other, not just report to parent. NOT for independent parallel tasks (use dispatching-parallel-agents instead).
---

# Creating Agent Teams

Launch coordinated agent teams for tasks requiring persistent cross-talk, shared
state, and teammate lifecycle management.

**Trigger:** `/agent-team <task-description>` or `/agent-team`

## Arguments

- `$ARGUMENTS` — Free-text task description. If omitted, ask the user.
- `--scenario <name>` — Use a pre-built template from [scenarios.md](scenarios.md).
  Skips Phase 2 (team design). Still requires user approval before launching.
  Valid: `multi-model-eval`, `paper-assembly`, `failure-investigation`,
  `cross-model-taxonomy`, `post-batch-analysis`, `augmentation-audit`,
  `advisor-guided-implementation`.
- `--teammates N` — Override default teammate count.
- `--all-opus` — Use Opus for all teammates (no advisor pattern). For tasks where
  Sonnet workers aren't sufficient (complex architecture, deep reasoning).
- `--no-critic` — Skip critic review (read-only/exploratory tasks only).
- `--fast` — Skip plan approval (urgent tasks only).

## When to Use

```dot
digraph when_to_use {
    "Complex task needing\nmultiple workers?" [shape=diamond];
    "Workers need to\ncommunicate findings?" [shape=diamond];
    "Tasks fully\nindependent?" [shape=diamond];
    "Single agent or subagent" [shape=box];
    "dispatching-parallel-agents" [shape=box];
    "creating-agent-teams" [shape=box style=filled fillcolor=lightgreen];

    "Complex task needing\nmultiple workers?" -> "Single agent or subagent" [label="no"];
    "Complex task needing\nmultiple workers?" -> "Workers need to\ncommunicate findings?" [label="yes"];
    "Workers need to\ncommunicate findings?" -> "Tasks fully\nindependent?" [label="no"];
    "Workers need to\ncommunicate findings?" -> "creating-agent-teams" [label="yes"];
    "Tasks fully\nindependent?" -> "dispatching-parallel-agents" [label="yes"];
    "Tasks fully\nindependent?" -> "creating-agent-teams" [label="no — shared state\nor synthesis needed"];
}
```

**Use agent teams when:**
- Teammates must share findings with each other (not just report to parent)
- One teammate's output feeds another's input (synthesis)
- Extended work (~5-30 min per teammate) with context accumulation
- Shared task list tracking is needed

**Don't use when:**
- Tasks are fully independent → use `dispatching-parallel-agents`
- Quick structured verdicts (~30s-2min) → use subagents
- Single-file edits → teammate overhead exceeds benefit
- Eval batches in worktrees → submodules won't initialize
- Two teammates would edit the same file → overwrite conflicts

## Workflow

### Phase 1: Understand the Task

1. Parse `$ARGUMENTS` for what the team should accomplish.
2. If unclear, ask Samyak for clarification.
3. Identify files, systems, and scope involved.
4. If `--scenario` used, load template from [scenarios.md](scenarios.md), skip to Phase 3.

### Phase 2: Design the Team

1. Determine minimum teammates (prefer fewer, focused teammates).
2. For each teammate define:
   - **Name** — descriptive, lowercase-with-hyphens
   - **Role** — one sentence
   - **Scope** — specific files/areas they own (NO overlap between teammates)
   - **Skills/Agents** — which pre-made agents or skills they should use
3. Default team includes an **advisor** (Opus) as first teammate. Workers default to
   `model: "sonnet"`, critic defaults to `model: "sonnet"`. For analytically heavy tasks
   (failure investigation, complex debugging), consider `--all-opus` or promoting specific
   workers to Opus.

4. Present to Samyak:

```
## Proposed Team: <team-name>

| Teammate | Model  | Role | Scope | Skills/Agents |
|----------|--------|------|-------|---------------|
| advisor  | opus   | Strategic reviewer | All areas (read-only) | — |
| planner  | sonnet | ... | ... | /writing-plans |
| ...      | sonnet | ... | ... | ... |
| critic   | sonnet | ... | ... | self-critic |

Estimated cost: ~Nx (see Cost table below)
```

5. **Wait for Samyak's approval.** Do NOT proceed until approved.

### Phase 3: Create and Launch

Execute these steps in exact order:

**Step 1 — TeamCreate.** Always the first action.
```
TeamCreate(team_name="<descriptive-name>")
```
If you find yourself about to call Agent without `team_name`, STOP.
Agent calls without `team_name` create isolated subagents that cannot cross-talk,
do not appear as teammates, and miss all coordination benefits.

**Step 2 — Create tasks** with TaskCreate for each unit of work.

**Step 2.5 — Spawn advisor FIRST** (skip if `--all-opus`):
```
Agent(
  prompt="<filled advisor-prompt.md>\n\n## YOUR TASK\n<advisor scope>",
  model="opus",
  team_name="<team-name-from-step-1>",
  name="advisor"
)
```
Read [advisor-prompt.md](advisor-prompt.md) and fill all `[FILL]` placeholders.
**Wait for advisor's "ADVISOR READY" message before spawning any workers.**

**Step 3 — Compose teammate prompts.** For EVERY worker/critic teammate:
1. Read [teammate-prompt.md](teammate-prompt.md)
2. Fill in ALL `[FILL]` placeholders with the teammate's specific scope, skills, etc.
3. Append the teammate's task description after the directives block

**Step 4 — Spawn workers** with Agent tool:
```
Agent(
  prompt="<filled teammate-prompt.md>\n\n## YOUR TASK\n<task description>",
  model="sonnet",
  team_name="<team-name-from-step-1>",
  name="<teammate-name>"
)
```
Every `Agent` call MUST include `team_name`.
Use `model="sonnet"` by default. Use `model="opus"` only if `--all-opus` was specified
or if the scenario recommends Opus for specific workers (see [scenarios.md](scenarios.md)).

**Step 5 — Manage lifecycle:**
- Assign tasks as teammates become available
- Aggregate results and present to Samyak
- Escalate decisions to Samyak (teammates don't contact user directly)
- Watch for handoff signals (teammate-prompt.md Section 5)
- When a teammate signals context relay: spawn child, pass handoff summary, confirm
- Shut down teammates when their work is done

**Advisor Coordination** (skip if `--all-opus`):
1. After each worker milestone -> forward summary to advisor via `SendMessage(to="advisor")`
2. Advisor returns guidance -> relay to relevant worker via `SendMessage(to="worker-N")`
3. If worker reports "consulted advisor: no" -> ask worker to justify or consult
4. Before Phase 4 -> `SendMessage(to="advisor", message="PRE-REVIEW: <summary of all work>")`
5. If worker stuck (2 failed attempts) -> escalate to advisor
6. During advisor relay handoff: pause milestone forwarding, wait for new advisor READY signal

### Phase 4: Quality Gate

Skip this phase only if `--no-critic` was specified.

1. **Sonnet critic reviews ALL changes** by other teammates (cheaper first pass). Checks:
   - Factual accuracy — claims match actual data files
   - Stale references — files, functions, numbers that don't exist
   - Consistency — no contradictions between teammate outputs
   - Completeness — all assigned tasks actually done
   - Scope compliance — no unauthorized file changes

2. **Escalate complex findings to advisor** (skip if `--all-opus`):
   - Ambiguous or borderline issues where the critic is unsure
   - Cross-cutting concerns that span multiple workers' outputs
   - Advisor provides final strategic sign-off before presenting to user

3. Present critic findings (+ advisor arbitration if applicable) to Samyak.

4. If issues found -> fix loop:
   a. Plan which teammate owns the fix
   b. Get Samyak's approval
   c. Teammate implements fix
   d. Critic re-reviews
   e. Max 3 iterations, then escalate to Samyak

5. Final report to Samyak:
   - What was done (with file paths)
   - What decisions were made (and why)
   - What files were changed
   - Any open items or concerns

## Available Agents & Skills for Teammates

Teammates should reuse these rather than building from scratch:

| Agent/Skill | Use for |
|------------|---------|
| `explorer` agent | Read-only codebase exploration |
| `paper-drafter` agent | Writing paper sections (always reads data first) |
| `eval-batcher` agent | Running LLM evaluation batches |
| `spec-auditor` agent | Auditing spec JSON files |
| `plan-reviewer` agent | Adversarial plan review |
| `self-critic` agent | Adversarial self-review |
| `consistency-checker` agent | Cross-checking docs vs code |
| `/writing-plans` skill | Creating implementation plans |
| `/validate` skill | Post-session validation |
| `/review` skill | Multi-agent code review |

## `--all-opus` Behavior

When `--all-opus` is specified:
- All teammates spawn with `model: "opus"`
- No advisor teammate is created
- `advisor-prompt.md` is NOT used
- Workers use `teammate-prompt.md` without Section 7 (Section 7 says "skip if --all-opus")
- Phase 4 critic is Opus (no escalation needed)
- Phase 3 Step 2.5 is skipped entirely

## Cost Estimation

**Default (advisor pattern):**

| Team | Mix | Cost vs All-Opus |
|------|-----|-----------------|
| Advisor + 1W + critic | 1 Opus + 2 Sonnet | ~45-55% |
| Advisor + 2W + critic | 1 Opus + 3 Sonnet | ~35-45% |
| Advisor + 3W + critic | 1 Opus + 4 Sonnet | ~30-40% |

Note: Opus is 5x Sonnet per token. Advisor uses fewer tokens than workers (guidance
only, no file editing). Ranges account for varying advisor utilization.

**`--all-opus` (legacy):**

| Team Size | Token Multiplier | When to Use |
|-----------|-----------------|-------------|
| Lead + 1 | ~2x | Simple comparison tasks |
| Lead + 2 | ~3x | Most analysis (paper, debugging) |
| Lead + 3 | ~4x | Multi-model analysis |
| Lead + 4+ | ~5x+ | Rare; 4+ model comparison only |

## Known Limitations

- **Delegate mode bug:** Teammates may not receive all tool results. Workaround:
  `claude --teammate-mode in-process`.
- **Worktrees + submodules:** Teammates in worktrees can't access benchmark sources.
  Never run eval-related teammates in worktrees.
- **File conflicts:** Two teammates editing the same file causes overwrites. Assign
  explicit file ownership in Phase 2.
- **Context exhaustion:** Large directories (160+ files) fill context fast. Teammates
  MUST follow the context relay protocol in [teammate-prompt.md](teammate-prompt.md) Section 5.

## Controls Cheat Sheet

| Action | How |
|--------|-----|
| Cycle through teammates | `Shift+Down` |
| View a teammate's session | `Enter` on selected |
| Message teammate directly | Type while viewing |
| Return to lead | `Escape` |
| Toggle shared task list | `Ctrl+T` |
| Shut down one teammate | Tell lead: "Ask {name} to shut down" |
| Clean up entire team | Tell lead: "Clean up the team" |
| Force in-process mode | `claude --teammate-mode in-process` |

## Example: Appendix Figures Team

**Task:** "Add figures from `analysis/visualizations/` into the paper appendix,
using data from `analysis/data/`, with `/writing-plans` and `paper-drafter` agent."

**Phase 2 output:**
```
## Proposed Team: appendix-figures

| Teammate    | Model  | Role                    | Scope                              | Skills/Agents    |
|-------------|--------|-------------------------|--------------------------------------|------------------|
| advisor     | opus   | Strategic reviewer      | All areas (read-only)                | —                |
| planner     | sonnet | Plan appendix structure | analysis/visualizations/, analysis/data/, docs/paper/appendix_*.md | /writing-plans |
| writer      | sonnet | Draft appendix content  | docs/paper/appendix_*.md             | paper-drafter    |
| critic      | sonnet | Review accuracy         | All teammate outputs (read-only)     | self-critic      |

Estimated cost: ~35-45% of all-Opus equivalent
```

**Phase 3:** TeamCreate -> TaskCreate (3 tasks) -> Spawn advisor (Opus), wait for
READY -> Spawn planner (Sonnet) with filled teammate-prompt.md -> Planner consults
advisor on structure -> Planner produces plan -> Samyak approves -> Spawn writer
(Sonnet) with plan + teammate-prompt.md -> Writer drafts appendix sections, sends
milestones to lead -> Lead forwards to advisor -> Spawn critic (Sonnet) -> Critic
reviews, escalates ambiguities to advisor -> Advisor signs off -> Present findings -> Done.
