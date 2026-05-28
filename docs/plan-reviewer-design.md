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

2. REPOSITORY RULES: Read CLAUDE.md, any linter configs, test conventions, and CI scripts in this repo. Does the plan follow them? If not, list the corrective actions.

3. OVER-ENGINEERING: For each task, ask: "Is this the simplest change that solves the stated problem?" Flag any unnecessary abstractions, premature generalizations, new files that could be avoided, or flexibility that wasn't requested. Opus 4.6 tends to overengineer — actively look for this.

4. MISSING DECISIONS: Are there design choices the plan made silently that should have been my call? List them and stop to ask me before proceeding.

5. SIMPLER ALTERNATIVE: Before writing the final plan, pause. Is there a more direct approach that achieves the same outcome with fewer files touched, fewer abstractions, or a well-known pattern? If yes, present it as a counter-proposal with tradeoffs. Search the web for established patterns or solutions if the task domain warrants it.

6. COMPLETENESS: Does each task have (a) the exact files to modify/create, (b) what the change is, and (c) a verification command or test to confirm it worked? If any task is missing these, add them.

7. ORDERING AND DEPENDENCIES: Are tasks sequenced so each one can be verified independently before moving to the next? Flag circular dependencies or tasks that can't be tested in isolation.
</review_checklist>

<handoff_requirements>
I will be pasting the final plan to a new Claude Code session with fresh context. That session will have zero knowledge of this conversation, the decisions we made, or the files we looked at. It should not have to waste time or tokens searching for files or rediscovering what needs to be done. This means:

- Every file path must be absolute or repo-relative — no "the file we discussed earlier."
- Every task must state exactly what to do, which files to touch, and how to verify the result succeeded before moving on.
- Include which skills and agent teams the new session should load and use for each task.
- Include the repo's relevant rules and conventions inline so the new session doesn't have to rediscover them from CLAUDE.md or config files.
- The instructions must be specific, explicit, and crystal clear so the executing session can work autonomously without ambiguity.
</handoff_requirements>

<final_output>
Use the /writing-plans skill to create the final plan verbatim to hand off to a new Claude Code session. Alongside the plan, include a detailed breakdown and explanation of your findings — what you investigated, what you changed from the original plan and why, what tradeoffs you considered, and what decisions you deferred to me. This must be intuitive to read and provide enough context to take the right decisions based on it. No summarization. Complete context.
</final_output>
```

---

## What Changed and Why

### Changes grounded in the official Anthropic prompting docs for Opus 4.6

**1. Added the `<investigate_before_answering>` block from Anthropic's recommended patterns.**

The official best practices page includes this exact pattern as a recommended prompt snippet for Opus 4.6, specifically designed to "minimize hallucinations in agentic coding." Your original prompt said "explore and research first and then ground this plan in the actual codebase" — which is directionally correct but vague. Opus 4.6 interprets vague exploration mandates as license to do broad, expensive context-gathering. The `<investigate_before_answering>` pattern is sharper: it says "don't talk about code you haven't opened," which is a constraint rather than an invitation to explore everything. This is a meaningful distinction because at "high" effort, Opus 4.6 will happily read dozens of files if you give it an open-ended exploration mandate, burning tokens on files that aren't relevant to the plan.

**2. Replaced motivational language with a concrete checklist.**

Your original had "be critical. be honest. be transparent." The Anthropic docs say: "Be specific about the desired output format and constraints" and "Think of Claude as a brilliant but new employee who lacks context on your norms and workflows." Opus 4.6 doesn't modulate its honesty based on encouragement — it needs a specific list of what to check for. The seven-point `<review_checklist>` gives it exactly that. Each check has a pass/fail gate, which makes the output verifiable rather than subjective. This also helps *you* evaluate whether the review was thorough: you can scan seven findings instead of parsing a wall of prose trying to figure out if the model actually challenged the plan or just said "looks good" with extra words.

**3. Removed the blanket "search for inspiration online" instruction and scoped it.**

The docs explicitly warn: "Claude Opus 4.6 does significantly more upfront exploration than previous models. If your prompts previously encouraged the model to be more thorough, you should tune that guidance." And separately: "Remove over-prompting. Tools that undertriggered in previous models are likely to trigger appropriately now." Your original said to "find inspiration from existing documentation, AI research papers and projects on github online" — at "high" effort, this is a recipe for Opus 4.6 spending thousands of tokens on web searches before it even reads your plan. The rewrite limits web research to checklist item #5: "Search the web for established patterns or solutions if the task domain warrants it." This scopes it to a specific decision point (is there a simpler alternative?) rather than a blanket mandate to go research broadly. If the plan is implementing a well-known pattern like OAuth or a state machine, Opus 4.6 will search. If the plan is renaming a set of files, it won't waste time searching for "best practices for file renaming."

**4. Used XML tags for structure instead of prose bullets.**

The docs recommend: "XML tags help Claude parse complex prompts unambiguously, especially when your prompt mixes instructions, context, examples, and variable inputs." Your original prompt was a single block of prose with dashes. The rewrite uses four distinct XML blocks — `<investigate_before_answering>`, `<review_checklist>`, `<handoff_requirements>`, and `<final_output>` — to separate the four distinct concerns: investigation behavior, review criteria, output constraints for the next session, and the final deliverable format. This matters because Opus 4.6 processes these as separate instruction sets rather than trying to hold one long paragraph in working memory. When it gets to the output phase, the `<handoff_requirements>` block reads as a standalone spec rather than something it has to extract from the middle of a run-on instruction.

**5. Explicitly called out Opus 4.6's over-engineering tendency as a review criterion.**

The docs say: "Claude Opus 4.5 and Claude Opus 4.6 have a tendency to overengineer by creating extra files, adding unnecessary abstractions, or building in flexibility that wasn't requested." This is listed as checklist item #3 with the note "Opus 4.6 tends to overengineer — actively look for this" and with specific things to flag: unnecessary abstractions, premature generalizations, new files that could be avoided, or flexibility that wasn't requested. Your original prompt mentioned "make sure the plan is NOT over-engineering" but didn't anchor it to specific patterns to look for. Telling Opus 4.6 *what* over-engineering looks like in concrete terms is much more effective than telling it not to over-engineer in the abstract.

**6. Preserved the handoff context as a motivation block, not just a spec.**

Your original text about "the new claude code session should not have to waste time or tokens looking for files" is doing something important: it's explaining *why* the output needs to be precise. The Anthropic docs specifically recommend this under "Add context to improve performance" — providing the motivation behind an instruction helps Claude understand the goal and deliver more targeted responses. I kept this framing in `<handoff_requirements>` and then listed the concrete requirements that follow from it. The original version had the motivation and the spec interleaved in prose; the rewrite separates the "why" (opening sentence) from the "what" (bullet list), which is cleaner for Opus 4.6 to parse.

**7. Preserved the /writing-plans instruction as a distinct final step.**

Your original instruction to "use the /writing-plans skill to create the final plan verbatim" is a specific tool invocation — it's telling the model *how* to produce the output, not just what the output should contain. In my first version I folded this into the generic output requirements, which lost the explicit skill reference and the "verbatim" constraint. The `<final_output>` block now preserves the full instruction, including the requirement for a detailed breakdown of findings alongside the plan, and the "no summarization, complete context" constraint. Keeping this as a separate tagged block ensures Opus 4.6 treats it as the final action to take after completing the review, not as one more bullet in a list of things to remember.

### What was removed and why

**"you can find inspiration from existing documentation, AI research papers and projects on github online"** — Replaced with the scoped trigger in checklist item #5. The blanket version caused unnecessary token burn at "high" effort. The scoped version still gets you web research when it matters (comparing approaches, finding established patterns) without the model doing speculative research on every task in the plan.

**"be critical. be honest. be transparent."** — Removed because it's motivational rather than instructional. Opus 4.6 doesn't modulate its critical thinking based on encouragement. The seven-point checklist provides the actual critical framework, and the pass/fail requirement on each check ensures the model can't hand-wave through the review.

**"make sure that you explore and research first"** — Replaced with `<investigate_before_answering>`, which is Anthropic's own recommended pattern for this exact behavior. The replacement is both shorter and more precise: instead of "explore and research" (which Opus 4.6 interprets as "read everything you can find"), it says "read the actual files the plan references before critiquing them" (which scopes the investigation to what's relevant).

### A workflow note worth considering

Your current workflow is: create plan in session → review plan in same session → copy reviewed plan to new session. This works, and the structured checklist in the rewrite mitigates the main risk (the model defending its own earlier reasoning instead of truly challenging it). But if you're working on high-stakes changes, consider a three-session approach: Session 1 creates the plan and exports it to a file. Session 2 (fresh context) receives only the plan file and runs the review prompt. Session 3 (fresh context) receives the reviewed plan and executes.

The reason this matters comes from the Claude Code docs: "LLM performance degrades as context fills" and "Claude's context window holds your entire conversation, including every message, every file Claude reads, and every command output." By the time you ask for the review in Session 1, the context already holds the full planning conversation. The model is reviewing its own reasoning while still holding that reasoning in memory, which biases it toward defending rather than challenging earlier decisions. A fresh Session 2 has no sunk-cost attachment to the plan's approach and can be genuinely adversarial.

That said, the checklist structure helps significantly even in a single-session workflow because it forces the model through specific pass/fail gates rather than open-ended self-reflection. The gates create external structure that partially compensates for the internal bias.