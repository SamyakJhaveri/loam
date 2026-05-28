# Plan Reviewer Prompt — Rewritten for Claude Opus 4.6

## The Prompt

Copy everything between the `---` markers below and use it as your plan-review prompt in Claude Code.

---

```
Use the plan-reviewer agent. Your role: adversarial reviewer of the plan I just created in this session.

<investigate_before_answering>
Before critiquing any part of the plan, read the actual files it references. Never critique code you haven't opened. Never assume a file's contents — read it first. If the plan references a pattern, convention, or architecture, verify it exists in the codebase before accepting the plan's claims about it.
</investigate_before_answering>

<review_checklist>
Work through each check in order. For each, state your finding and whether the plan passes or fails.

1. CODEBASE GROUNDING: Does every task in the plan reference specific, real file paths? Read those files. Does the plan accurately describe what's there? Flag any task that operates on assumptions instead of verified code.

2. REPOSITORY RULES: Read every file in `.claude/rules/`, then read CLAUDE.md, linter configs, test conventions, and CI scripts. These define the project's enforceable conventions — folder structure, naming, patterns, and constraints. Check two things separately: (a) Does the plan conform to these rules? (b) Does any implementation already done in this session violate them? For each violation, list the specific rule broken and the corrective action needed.

3. OVER-ENGINEERING: For each task, ask: "Is this the simplest change that solves the stated problem?" Flag any unnecessary abstractions, premature generalizations, new files that could be avoided, or flexibility that wasn't requested. Opus 4.6 tends to overengineer — actively look for this.

4. MISSING DECISIONS: Are there design choices the plan made silently that should have been my call? List them and stop to ask me before proceeding.

5. COMPLETENESS: Does each task have (a) the exact files to modify/create, (b) what the change is, and (c) a verification command or test to confirm it worked? If any task is missing these, add them.

6. ORDERING AND DEPENDENCIES: Are tasks sequenced so each one can be verified independently before moving to the next? Flag circular dependencies or tasks that can't be tested in isolation.
</review_checklist>

<elegance_gate>
This step is mandatory. Do it after the checklist and before writing the final plan.

Pause. Step back from the plan entirely. Forget the current approach for a moment and look at the underlying problem the plan is trying to solve. Ask yourself:

- Is the plan solving the right problem, or has it drifted into solving a side-effect?
- Is there a completely different approach — a different architecture, a built-in framework feature, an existing library, a well-known pattern — that would make most of this plan unnecessary?
- Would an experienced engineer look at this plan and say "why not just do X instead?"

Search the web for how others have solved this class of problem. Look at existing documentation, established open-source patterns, and projects on GitHub. The goal is not to validate the current plan — it is to discover whether a fundamentally better approach exists that the planning session didn't consider.

If you find a more elegant approach, present it as a concrete counter-proposal: what the alternative is, why it's better, what its tradeoffs are, and what it would replace in the current plan. If after genuine investigation the current approach is the best one, say so and explain why the alternatives you considered were worse.

Do not skip this step. Do not treat it as a formality.
</elegance_gate>

<handoff_requirements>
I will be pasting the final plan to a new Claude Code session with fresh context. That session will have zero knowledge of this conversation, the decisions we made, or the files we looked at. It should not have to waste time or tokens searching for files or rediscovering what needs to be done. This means:

- Every file path must be absolute or repo-relative — no "the file we discussed earlier."
- Every task must state exactly what to do, which files to touch, and how to verify the result succeeded before moving on.
- Include which skills and agent teams the new session should load and use for each task.
- Include the repo's relevant rules and conventions inline so the new session doesn't have to rediscover them from CLAUDE.md or config files.
- The instructions must be specific, explicit, and crystal clear so the executing session can work autonomously without ambiguity.
</handoff_requirements>

<final_output>
Use the /writing-plans skill to create the final plan verbatim to hand off to a new Claude Code session. Alongside the plan, include a detailed breakdown and explanation of your findings — what you investigated, what you changed from the original plan and why, what alternatives you considered in the elegance gate and why you chose or rejected them, and what decisions you deferred to me. This must be intuitive to read and provide enough context to take the right decisions based on it. No summarization. Complete context.
</final_output>
```

---

## What Changed From Version 1 and Why

### The elegance gate: what was wrong and what's different now

**The problem with v1:** Checklist item #5 in the first version read: "SIMPLER ALTERNATIVE: Before writing the final plan, pause. Is there a more direct approach that achieves the same outcome with fewer files touched, fewer abstractions, or a well-known pattern?" This was a *simplicity* check — it only asked whether the same approach could be made leaner. It did not ask the model to step outside the current approach and reconsider the problem from scratch.

This matters in practice. Consider a plan that implements custom retry logic across four service files. A simplicity check might trim it to three files and remove an unnecessary abstraction. An elegance check would recognize that the HTTP client library already has a built-in retry mechanism and the entire plan should be replaced with a three-line configuration change. The first optimizes within the frame; the second breaks the frame. These are fundamentally different cognitive operations for the model.

**What changed:** The elegance check is now a standalone `<elegance_gate>` block, separated from and sequenced after the review checklist. This matters for three reasons:

1. **Sequencing.** The original prompt said "Before you write the final plan: is there a more elegant approach?" — this is a positional instruction that says "do this as the last analytical step before producing output." Burying it as item #5 of 7 in a checklist lost that sequencing. The `<elegance_gate>` block is now positioned between `<review_checklist>` and `<handoff_requirements>`, which preserves the original's intent: finish your review, then pause and reconsider, then write the output.

2. **Scope of thinking.** The block now explicitly tells the model to "forget the current approach for a moment and look at the underlying problem." This is important for Opus 4.6 because by the time it reaches this step, it has just done a detailed seven-point review of the plan — it's deep in the details. Without an explicit instruction to step back, it will naturally continue optimizing within the current frame. The instruction to "step back from the plan entirely" forces a context switch.

3. **Active research.** The original prompt said "you can find inspiration from existing documentation, AI research papers and projects on github online." In v1, I scoped this down to "search the web if the task domain warrants it" — which effectively made it optional. The v1 reasoning was that Opus 4.6 at "high" effort would over-explore if given an open research mandate. But the original prompt's web research instruction isn't about broad exploration — it's specifically about discovering whether a better approach exists. The `<elegance_gate>` now includes an explicit web search step: "Search the web for how others have solved this class of problem." This is scoped to the elegance check (not the entire review) and has a specific purpose (find alternatives, not gather general context), which addresses the over-exploration concern while preserving the original intent.

4. **Non-skippable.** The block ends with "Do not skip this step. Do not treat it as a formality." This is necessary because Opus 4.6 at "high" effort can sometimes rush through steps that feel like they won't change the outcome — especially when the preceding checklist already produced a "looks good" result. The explicit non-skip instruction forces the model to actually do the work.

### The three questions in the elegance gate

The gate asks three specific questions rather than the open-ended "is there a more elegant approach?":

- **"Is the plan solving the right problem, or has it drifted into solving a side-effect?"** — This catches plans that started with a clear goal but drifted during the planning session. Common with Opus 4.6, which explores broadly and can accidentally redefine the problem scope during exploration.

- **"Is there a completely different approach — a different architecture, a built-in framework feature, an existing library, a well-known pattern — that would make most of this plan unnecessary?"** — This is the core elegance question. It explicitly names the categories of alternatives to look for, which prevents the model from doing a surface-level "I considered alternatives and the current approach is best" without actually investigating.

- **"Would an experienced engineer look at this plan and say 'why not just do X instead?'"** — This reframes the question from the model's perspective to an external perspective, which helps counteract the bias toward its own earlier reasoning.

### Other changes from v1

**Checklist item #2 now explicitly targets `.claude/rules/` as the primary source of project conventions.** The original prompt's "repository's rules" specifically means the rule files in `.claude/rules/` — these are Claude Code's contextual rule files that define enforceable conventions per file-pattern (folder structure, naming, patterns, constraints). They're more prescriptive than CLAUDE.md, which is broad guidance. v1 said "read CLAUDE.md, linter configs, test conventions, and CI scripts" — a generic list that didn't mention `.claude/rules/` at all. The updated version reads `.claude/rules/` *first*, then CLAUDE.md and other config files. It also separates the two checks explicitly: (a) does the plan conform, and (b) does implementation already done in this session violate the rules. Each violation must cite the specific rule and corrective action, not just flag a generic "doesn't follow conventions."

### What was preserved from v1

Everything else from v1 remains unchanged. The `<investigate_before_answering>` block, the XML structure, the concrete over-engineering criteria, the `<handoff_requirements>` motivation-then-spec pattern, and the `<final_output>` block with the /writing-plans skill invocation all carry forward. The analysis of why those changes were made (documented in v1) still applies.

### Structural overview of the final prompt

The prompt now has five distinct phases, each in its own XML block:

1. `<investigate_before_answering>` — Sets the ground rule: read before you speak.
2. `<review_checklist>` — Six concrete pass/fail checks on the plan's quality.
3. `<elegance_gate>` — Step back, reconsider the whole approach, research alternatives.
4. `<handoff_requirements>` — Constraints on the output format for the next session.
5. `<final_output>` — How to produce and deliver the final plan.

This sequencing mirrors the original prompt's intended workflow: investigate → critique → rethink → format → deliver. The XML tags make this sequence explicit for Opus 4.6, which processes tagged sections as distinct instruction sets rather than trying to hold a single long paragraph in working memory.

### Workflow note (unchanged from v1)

Your current workflow is: create plan in session → review plan in same session → copy reviewed plan to new session. The structured checklist and elegance gate mitigate the main risk (the model defending its own earlier reasoning), but for high-stakes changes, consider: Session 1 creates the plan → Session 2 (fresh context) reviews it → Session 3 (fresh context) executes it. A fresh session doing the review has no sunk-cost attachment to the plan's approach and can be more genuinely adversarial, especially during the elegance gate.