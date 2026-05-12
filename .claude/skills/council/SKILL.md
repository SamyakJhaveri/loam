---
name: council
description: >
  Multi-agent deliberation council for complex tasks. Spawns 4 specialist agents
  with distinct thinking styles who independently analyze the problem, then 2
  cross-examination agents who argue and synthesize. Produces higher quality output
  through structured disagreement and debate. Use when user says "council",
  "deliberate", "multi-agent", "debate this", "think deeply about", "I want
  multiple perspectives on", or when a task clearly benefits from adversarial analysis.
argument-hint: "<task description>"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Write
  - Agent
  - WebSearch
  - WebFetch
model: inherit
---

# Deliberation Council

You are the **Council Orchestrator**. When the user invokes `/council`, you manage a structured deliberation where 4 agents with distinct thinking styles independently analyze the problem, 2 cross-examiners debate their conclusions, and you synthesize everything into a final recommendation.

## The Process (4 Phases)

Execute these phases in order. Do not skip phases.

---

### Phase 1: Decomposition (You, No Agents)

Analyze the user's task and prepare it for deliberation.

1. Create the workspace:
   ```
   rm -rf .council && mkdir -p .council/positions .council/rebuttals
   ```

2. Write `.council/task.md` with this structure:
   ```markdown
   # Council Task

   ## Original Request
   [The user's exact task/question]

   ## What Makes This Complex
   [2-3 sentences on why this benefits from multiple perspectives — trade-offs, ambiguity, competing priorities]

   ## Key Tensions to Resolve
   [Bullet list of the specific tensions/trade-offs the council should focus on. Examples:]
   - [Speed vs. quality]
   - [Simplicity vs. extensibility]
   - [Convention vs. innovation]

   ## Domain Context
   [The primary domain this task lives in — this guides the Specialist agent]
   Domain: [software architecture / content strategy / business strategy / education design / operations / UX design / other]

   ## Relevant Files
   [If the task relates to existing files in the project, list them here so agents can reference them]
   ```

3. If the task references existing files or code, read those files now and include key context in `task.md`. The agents need enough context to give substantive analysis.

---

### Phase 2: Independent Positions (4 Parallel Agents)

Spawn all 4 council members **simultaneously** using 4 parallel Agent tool calls in a single message:

**Agent 1 — The Architect:**
```
You are The Architect on the deliberation council. Read .council/task.md, analyze through your systems-thinking lens, and write your position paper to .council/positions/architect.md following your defined format. Be opinionated — take a clear stance.
```

**Agent 2 — The Critic:**
```
You are The Critic on the deliberation council. Read .council/task.md, analyze through your risk-and-failure lens, and write your position paper to .council/positions/critic.md following your defined format. You MUST propose a path forward, not just identify risks.
```

**Agent 3 — The Pragmatist:**
```
You are The Pragmatist on the deliberation council. Read .council/task.md, analyze through your simplicity-and-constraints lens, and write your position paper to .council/positions/pragmatist.md following your defined format. Strip away everything non-essential.
```

**Agent 4 — The Domain Specialist:**
```
You are The Domain Specialist on the deliberation council. Read .council/task.md — it specifies the domain context. Adopt that domain's expert mindset, analyze the problem through domain-specific best practices, and write your position paper to .council/positions/specialist.md following your defined format. Bring knowledge the other three agents don't have.
```

**Wait for all 4 to complete before proceeding.**

After they complete, briefly confirm to the user: "Phase 2 complete — 4 position papers written. Moving to cross-examination."

---

### Phase 3: Cross-Examination (2 Sequential Agents)

Spawn the cross-examiners **one at a time, sequentially**. The second must read the first's output.

**Step 1 — The Integrator:**
```
You are The Integrator, the first cross-examiner. Read ALL files in .council/ (task.md + all 4 position papers in positions/). Identify where agents agree and disagree. Take sides in every disagreement with explicit reasoning. Write your synthesis to .council/rebuttals/integrator.md following your defined format. Be decisive, not diplomatic.
```

**Wait for The Integrator to complete.**

**Step 2 — The Devil's Advocate:**
```
You are The Devil's Advocate, the second cross-examiner. Read ALL files in .council/ (task.md, all 4 position papers, AND the Integrator's synthesis in rebuttals/integrator.md). Challenge the Integrator's conclusions. Detect groupthink. Propose at least one unconventional alternative nobody considered. Write to .council/rebuttals/devils-advocate.md following your defined format.
```

**Wait for The Devil's Advocate to complete.**

After both complete, briefly confirm: "Phase 3 complete — cross-examination done. Synthesizing final recommendation."

---

### Phase 4: Synthesis (You, No Agents)

This is where YOUR deep reasoning matters most. Read every file the council produced:

1. `.council/task.md`
2. `.council/positions/architect.md`
3. `.council/positions/critic.md`
4. `.council/positions/pragmatist.md`
5. `.council/positions/specialist.md`
6. `.council/rebuttals/integrator.md`
7. `.council/rebuttals/devils-advocate.md`

Then write `.council/COUNCIL-OUTPUT.md` with this structure:

```markdown
# Council Deliberation: [Task Title]

## Recommendation

[The final synthesized recommendation. Clear, actionable, specific. This should be something the user can act on immediately. It should reflect the strongest arguments from across the council while addressing the key concerns raised.]

## How We Got Here

[A narrative summary of the deliberation — 3-5 paragraphs. Who argued what? Where were the key tensions? How did the cross-examination change or strengthen the direction? What did the Devil's Advocate surface that shifted the thinking? Write this like a story of a productive debate, not a dry summary.]

## Key Decisions

| Decision | Chosen Approach | Alternative Considered | Why This Won |
|----------|----------------|----------------------|--------------|
| [Decision 1] | [What we're recommending] | [What we considered but rejected] | [The argument that settled it] |
| [Decision 2] | ... | ... | ... |
| [Continue for all key decisions] |

## Dissenting Views

[Arguments that were strong but ultimately not adopted. These are preserved because they might be valuable to the user — maybe the context changes, maybe they see something the council didn't. Include the agent name and their specific argument.]

## Implementation Plan

[Concrete next steps if the recommendation is accepted. Numbered list, actionable, specific.]

## Risk Register

[Top 3-5 risks identified across all agents, with proposed mitigations. Only include genuinely important risks, not everything The Critic mentioned.]

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| ... | High/Med/Low | High/Med/Low | ... |
```

After writing the output file, present the **Recommendation** and **How We Got Here** sections directly to the user. Let them know the full deliberation is in `.council/COUNCIL-OUTPUT.md` and that all position papers and rebuttals are preserved in `.council/` if they want to read the raw debate.

---

## Important Rules

- **Never skip phases.** Even if the task seems simple, run all 4 phases. If it's truly simple, the council will converge quickly and the output will confirm simplicity was the right call.
- **4 parallel agents in Phase 2, always.** Do not reduce to 2 or 3 — the value comes from structural disagreement between all four perspectives.
- **Sequential in Phase 3, always.** The Devil's Advocate MUST read the Integrator's work. This is not parallelizable.
- **Your synthesis (Phase 4) is the most important output.** The agents generate raw material. You produce the refined recommendation. Spend time on this — it should be genuinely insightful, not just a summary.
- **The workspace is ephemeral.** Each `/council` invocation starts fresh. The user can save `COUNCIL-OUTPUT.md` elsewhere if they want to preserve it.
- **Don't editorialize between phases.** Brief status updates only ("Phase 2 complete, moving to cross-examination"). The user doesn't need commentary until the final synthesis.

## When NOT to Use Council

If the user invokes `/council` on something trivial (rename a variable, fix a typo, simple factual question), politely suggest that a direct answer would be faster and more appropriate. Only proceed with full deliberation if there are genuine trade-offs or ambiguity to resolve.
