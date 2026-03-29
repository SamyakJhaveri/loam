# Agent Team Creator

Create and launch an agent team following Samyak's standard operating procedures.
Enforces ultrathink, context management, decision-maker protocol, and anti-rot in
every teammate prompt.

**Trigger:** When user types `/agent-team <task-description>` or `/agent-team`.

## Arguments

- `$ARGUMENTS` — Free-text description of the task the team should accomplish.
  If omitted, ask the user what the team should do.

## Samyak's Agent Team Operating Procedures (MANDATORY)

These rules apply to EVERY agent team. Embed them as `## MANDATORY DIRECTIVES` at
the top of every teammate prompt, before the task description.

### 1. Decision Authority

- **Samyak is the PRIMARY DECISION MAKER** — all significant decisions go through him.
- When ANY teammate needs clarification, guidance, or input: **pause the teammate and
  ask Samyak via the team lead**. Do not jump to conclusions or assumptions.
- Be honest, be transparent. Tell Samyak where he might be wrong.
- Present options with tradeoffs, not unilateral choices.

### 2. Thinking & Quality

- **Every teammate MUST use ultrathink** — state this explicitly in the teammate prompt.
- Use the `model: "opus"` parameter for all teammates.
- No shortcuts. Read the file before editing. Understand the code before changing it.
- Verify before reporting done — run validators, tests, or checks as appropriate.

### 3. Context Management (Anti-Rot Protocol)

- Each teammate must be **conservative and conditional about context usage**.
- Delegate bulk reads to subagents — do not load large files into main teammate context.
- Write findings incrementally to durable files (survive compaction).
- Cross-reference facts against 2+ sources before stating them.
- Never hold >50K tokens of raw content in a single teammate context.

### 4. Skill & Agent Reuse

- Teammates should use pre-made agents (`explorer`, `eval-batcher`, `spec-auditor`,
  `plan-reviewer`, `self-critic`, `consistency-checker`, `rodinia-verifier`,
  `paper-drafter`) rather than doing everything from scratch.
- Use existing skills (`/validate`, `/review`, `/eval-run`) when appropriate.

### 5. Team Structure Standards

- **Always include a planner** — plans first, gets user approval before implementation.
- **Always include a critic** — adversarial review of all changes before finalizing.
- **Plan-then-execute** — no edits until the plan is approved by Samyak.
- Critic reviews everything at the end for accuracy, stale claims, consistency.

### 6. Communication Protocol

- Team lead aggregates findings and presents to Samyak — teammates don't spam.
- Use TaskCreate/TaskUpdate to track progress visibly.
- When a teammate finishes, they report to team lead, not directly to user.
- If blocked, escalate to team lead immediately with the specific blocker.

## Workflow

### Phase 1: Understand the Task

1. Parse `$ARGUMENTS` to understand what the team should accomplish.
2. If the task is unclear or ambiguous, ask Samyak for clarification.
3. Identify the files, systems, and scope involved.

### Phase 2: Design the Team

1. Determine the minimum number of teammates needed (prefer fewer, focused teammates).
2. For each teammate, define:
   - **Name** — descriptive, lowercase-with-hyphens
   - **Role** — one sentence
   - **Scope** — specific files/areas they own (no overlap between teammates)
   - **Agent type** — match to available tools needed (general-purpose for edits, Explore for read-only, etc.)
3. Present the team design to Samyak for approval:
   ```
   ## Proposed Team: <team-name>

   | Teammate | Role | Scope | Agent Type |
   |----------|------|-------|------------|
   | planner  | ... | ... | general-purpose |
   | ...      | ... | ... | ... |
   | critic   | ... | ... | Explore |

   Estimated token cost: ~Nx for N teammates
   ```
4. **Wait for Samyak's approval** — do not create the team until approved.

### Phase 3: Create and Launch

1. Create the team with TeamCreate.
2. Create tasks with TaskCreate for each unit of work.
3. Spawn teammates with Agent tool, each with:
   - The MANDATORY DIRECTIVES section at the top of their prompt
   - Their specific task description
   - `model: "opus"` parameter
   - `team_name` parameter
4. Manage teammate lifecycle:
   - Assign tasks as teammates become available
   - Aggregate results from teammates
   - Escalate decisions to Samyak
   - Shut down teammates when done

### Phase 4: Quality Gate

1. Critic teammate reviews ALL changes made by other teammates.
2. Present critic's findings to Samyak.
3. If critic finds issues: fix loop (plan fix, get approval, implement, re-review).
4. Final report to Samyak with:
   - What was done
   - What decisions were made
   - What files were changed
   - Any open items or concerns

## Customization

The user can modify this skill's behavior per invocation:
- `/agent-team monitor qwen results` — task is "monitor qwen results"
- `/agent-team --teammates 3` — override default teammate count
- `/agent-team --no-critic` — skip critic (for read-only/exploratory tasks)
- `/agent-team --fast` — skip plan approval step (for urgent tasks)

The user can also edit this SKILL.md directly to change default behaviors.
