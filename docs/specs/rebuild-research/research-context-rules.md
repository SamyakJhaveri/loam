# Context Engineering Rules for Claude 5-Generation Harnesses

> Research pass, official Anthropic sources only, fetched 2026-08-28.
> Purpose: give the asset ledger a defensible criterion for whether each harness asset (rule file, skill, hook, agent, validation gate) EARNS ITS PLACE.
> Every principle below carries a quote or close paraphrase, its source URL, and a one-line TEST usable as a ledger verdict.

## Sources fetched

| # | Title | URL | Date/status |
|---|-------|-----|-------------|
| S1 | The new rules of context engineering for Claude 5 generation models | https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models | Primary source for this task |
| S2 | Effective context engineering for AI agents | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | Anthropic Engineering |
| S3 | Best practices for Claude Code | https://code.claude.com/docs/en/best-practices | Official docs (the old `anthropic.com/engineering/claude-code-best-practices` 308-redirects here) |
| S4 | Extend Claude Code (match features to your goal) | https://code.claude.com/docs/en/features-overview | Official docs |
| S5 | Extend Claude with skills | https://code.claude.com/docs/en/skills | Official docs |
| S6 | Steering Claude Code: when to use CLAUDE.md, skills, hooks, and subagents | https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more | Claude blog |
| S7 | Equipping agents for the real world with Agent Skills | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | Anthropic Engineering |
| S8 | Building effective agents | https://www.anthropic.com/engineering/building-effective-agents | Anthropic Engineering |
| S9 | Writing effective tools for agents | https://www.anthropic.com/engineering/writing-tools-for-agents | Anthropic Engineering |
| S10 | How we built our multi-agent research system | https://www.anthropic.com/engineering/multi-agent-research-system | Anthropic Engineering |

Caveat on fidelity: the fetch layer refused verbatim full-article reproduction and returned attributed short quotes plus summary.
Quotes marked with `"` below are reported as exact by the fetch of that URL; anything unquoted is a close paraphrase and is labelled as such.
Nothing here is drawn from a third-party blog.

---

## Part 1 - The load-bearing principle

### P1. Context is a finite resource with diminishing returns

Quote: "Context, therefore, must be treated as a finite resource with diminishing marginal returns." (S2)
Quote: "Good context engineering means finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome." (S2)
Supporting: S2 names "context rot" - as token count rises, recall accuracy falls, across all models.
Supporting: S3 states the entire best-practices document rests on one constraint - context fills fast and performance degrades as it fills.

TEST: **DELETE any asset whose tokens are not among the smallest high-signal set needed for the outcome it claims to protect.**

### P2. Anthropic deleted 80% of its own system prompt and lost nothing measurable

Quote: "removed over 80% of Claude Code's system prompt for models like Claude Opus 5 and Claude Fable 5 with no measurable loss" (S1)
Paraphrase (S1): the constraints existed because older models needed them; newer models make the same calls from surrounding context and judgement.

TEST: **DEFAULT TO DELETE. The burden of proof is on keeping an asset, not on cutting it; a 5x cut was the measured-neutral outcome on Anthropic's own harness.**

---

## Part 2 - The six shifts (S1)

### P3. Rules -> judgement

Before (S1, quoted from the old prompt): "default to writing no comments. Never write multi-paragraph docstrings or multi-line comment blocks - one short line max"
After (S1): "Write code that reads like the surrounding code: match its comment density, naming, and idiom."
Paraphrase (S1): the fix was to "delete many of them and let the model use surrounding context and judgement instead."

TEST: **DELETE a rule that hard-codes a choice the model can make from surrounding context; REWRITE it as a one-line statement of the standard, not a prohibition list.**

### P4. Conflicting instructions make the model overthink

Quote: "conflicting messages in a single request like 'leave documentation as appropriate,' or 'DO NOT add comments' as our system prompt, skills, and user requests clash" (S1)
Quote: "Claude must think more carefully about these overlapping and conflicting messages before deciding what to do" (S1)

TEST: **DELETE any asset that restates, softens, or contradicts a directive already present in another layer; one directive, one home.**

### P5. Examples -> interface design

Quote: "giving examples actually constrains them to a certain exploration space" (S1)
Paraphrase (S1): instead of tool-usage examples, design expressive parameters and enumerations whose names hint at the usage pattern.
Tension to record honestly: S2 (written pre-Claude-5) still recommends "we recommend working to curate a set of diverse, canonical examples that effectively portray the expected behavior." S1 supersedes S2 for Claude 5-generation models; the reconciliation is that a few canonical examples of *taste* are still fine, while examples that enumerate *how to call a tool* are now a constraint on exploration.

TEST: **DELETE example blocks that demonstrate mechanics the interface can express by itself; KEEP at most one canonical example per asset, and only when it conveys taste rather than syntax.**

### P6. Everything upfront -> progressive disclosure

Quote: "load the right context at the right times" (S1)
Concrete case (S1): detailed verification and code-review guidance was moved out of the system prompt into optional skills.
Mechanism (S1): "'deferred loading,' which means the agent must search for their full definitions using ToolSearch before using them. This allows us to have more tools ... that don't take up context until they're needed"
Same idea in S2 as "just in time" retrieval - keep lightweight identifiers, load the payload through a tool call.
Same idea in S7 as three levels - name plus description at startup, SKILL.md body when relevant, bundled files only as needed.

TEST: **DEMOTE any always-loaded asset that is needed in under ~1 session in 3; it becomes an on-demand skill or a referenced file, not a rule.**

### P7. Repetition -> one description, in the right place

Quote: "put instructions on how to use tools in the tool descriptions rather than the system prompt" (S1)

TEST: **DELETE the duplicate copy; guidance about using a thing lives with the thing, never in the always-loaded layer.**

### P8. Manual CLAUDE.md memory -> auto-memory

Quote: "Claude now automatically saves memories that are relevant to the work and to you" (S1)

TEST: **DELETE hand-maintained memory scaffolding whose only job is to persist facts the auto-memory layer now captures.**

### P9. Simple specs -> rich references

Quote: "Claude can handle increasingly more complicated references" (S1)
Paraphrase (S1): plans can now be HTML artifacts, code specs, test suites, and rubrics rather than markdown prose.
Quote: "Rubrics allow Claude to try and verify your taste in a particular field ... by using dynamic workflows and spinning up verifier agents" (S1)

TEST: **UPGRADE a prose asset that describes a standard into an executable or checkable artifact (test, rubric, script); DELETE the prose once the artifact exists.**

---

## Part 3 - Layer-by-layer earn-its-place tests

### P10. CLAUDE.md - the removal test

Quote: "Keep it concise. For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it." (S3)
Quote: "Bloated CLAUDE.md files cause Claude to ignore your actual instructions!" (S3)
Quote (S1): "Keep your CLAUDE.md lightweight and briefly describe what your repo is for, but spend most of the tokens on gotchas inside of the codebase"
Quote (S1): "Avoid stating 'the obvious' things Claude should know by looking at your file system or your repo."
Include/exclude table (S3): include bash commands Claude cannot guess, style rules that differ from defaults, test runners, repo etiquette, project-specific architectural decisions, env quirks, non-obvious gotchas. Exclude anything derivable by reading code, standard conventions the model knows, detailed API docs, frequently-changing information, long explanations, file-by-file descriptions, self-evident practices.
Size rule (S4, S6): "Keep CLAUDE.md under 200 lines, give it an owner, and review changes to it like code."
Emphasis rule (S3): "If you emphasize many lines, none of them stands out."
Failure signal (S3): if Claude keeps violating a rule that exists, the file is too long and the rule is getting lost.

TEST: **DELETE a CLAUDE.md line unless removing it would cause a mistake; DELETE anything derivable from the repo; if the file exceeds 200 lines, cut before adding.**
TEST: **COUNT the IMPORTANT/ALWAYS/NEVER markers - if more than a couple exist, the emphasis is self-cancelling and must be reduced to the single rule that most needs it.**

### P11. The explicit "delete or convert" instruction

Quote (S3, failure pattern "The over-specified CLAUDE.md"): "Ruthlessly prune. If Claude already does something correctly without the instruction, delete it or convert it to a hook."

TEST: **DELETE a rule the model already follows unprompted; if the behavior must be guaranteed rather than encouraged, CONVERT it to a hook instead of leaving it as prose.**
This is the cleanest single ledger criterion in the corpus: the ablation is "would the model do this anyway?"

### P12. Rules files - path scoping earns its place, otherwise it is CLAUDE.md

Paraphrase (S4): `.claude/rules/` load every session, or only when matching files are opened via `paths` frontmatter; use rules to keep CLAUDE.md focused, and scope them so unrelated work does not pay for them.
Paraphrase (S6): path-scoped rules exist to avoid loading irrelevant instructions across unrelated work.

TEST: **A rule file that is always-loaded and not path-scoped must justify itself on CLAUDE.md's terms (P10); otherwise SCOPE it with `paths` or DELETE it.**

### P13. Skills - on-demand knowledge, priced per recurring line

Quote (S5): "Create a skill when you keep pasting the same instructions, checklist, or multi-step procedure into chat, or when a section of CLAUDE.md has grown into a procedure rather than a fact."
Quote (S5): "Keep the body itself concise. Once a skill loads, its content stays in context across turns, so every line is a recurring token cost."
Quote (S5): "Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files."
Quote (S1): "Think of skills as lightweight guides to let Claude find information when needed. Avoid making them overconstrained, except in highly important areas"
Quote (S1) on long skills: "divide it into many files and split them out"
Quote (S7): "When the `SKILL.md` file becomes unwieldy, split its content into separate files and reference them."
Origin test (S7): find "specific gaps in your agents' capabilities by running them on representative tasks and observing where they struggle or require additional context."

TEST: **KEEP a skill only if it encodes a procedure or team-specific taste the model demonstrably gets wrong without it; DELETE a skill that restates general competence.**
TEST: **SPLIT any SKILL.md over ~500 lines; the body is a router, the detail is a bundled file loaded on demand.**

### P14. Skill descriptions compete for a hard budget - more skills is not free

Paraphrase and figures (S5): every skill's name and description sit in a listing loaded into context each request; the listing budget "scales at 1% of the model's context window"; when it overflows, Claude Code "drops descriptions starting with the skills you invoke least," and each entry is capped at 1,536 characters regardless of budget.
Diagnostic (S5): `/doctor` estimates the listing's context cost and names its biggest contributors; the Skills row of `/context` reports the post-budget size.
Selection failure (S4): "If descriptions are vague or overlap, Claude may load the wrong skill or miss one that would help."

TEST: **DELETE or set `disable-model-invocation: true` on any skill that has not been invoked in recent real sessions - a rarely-used skill's description is starving the descriptions of the skills that matter.**
TEST: **DELETE the weaker of any two skills whose descriptions overlap; overlap degrades selection for both.**

### P15. Skills can be measured, so measure before defending one

Paraphrase (S5, skill-creator eval loop): isolated per-test-case subagent runs recording tokens and duration; a benchmark that "aggregates pass rate, time, and tokens for with-skill versus without-skill ... so you can compare the pass-rate improvement against the token and time overhead"; blind A/B between two skill versions; description tuning that measures should-trigger versus should-not-trigger hit rate.

TEST: **A contested skill is not argued about, it is ablated: run the representative task with and without it and keep it only if pass rate improves enough to pay for its tokens.**

### P16. Hooks - the only layer that is a guarantee

Quote (S4): "Put guardrails in hooks. An instruction like 'never edit `.env`' in CLAUDE.md or a skill is a request, not a guarantee. A `PreToolUse` hook that blocks the edit is enforcement. If a rule must hold every time, make it a hook rather than a prompt instruction."
Quote (S3): "Use hooks for actions that must happen every time with zero exceptions." Hooks "are deterministic and guarantee the action happens," unlike advisory CLAUDE.md instructions.
Quote (S6): "Use hooks for anything that should happen deterministically: running linters after edits, posting to Slack on completion, or blocking specific commands"
Why prose is not enough (S6): "Claude will follow the instruction most of the time, but when under pressure, in a long session or an ambiguous situation ... the model can fail."
Cost (S4): hook context cost is "Zero, unless the hook returns output that gets added as messages to your conversation."
Boundary (S4): "Use a hook when the action must happen the same way every time and doesn't need Claude to think."

TEST: **CONVERT to a hook any prose rule that must hold 100% of the time; DELETE a hook that encodes a judgement call, because a hook cannot think and will misfire on the exception.**
TEST: **A hook that returns chatty output is paying context rent - trim its output to the signal the model must act on, or make it silent-on-pass.**

### P17. Subagents - context isolation is the whole justification

Quote (S3): "Since context is your fundamental constraint, subagents are one of the most powerful tools available."
Mechanism (S2): a subagent explores widely and returns "only a condensed, distilled summary of its work (often 1,000-2,000 tokens)."
Design rationale (S10): the orchestrator-worker split gives "separation of concerns - distinct tools, prompts, and exploration trajectories - which reduces path dependency and enables thorough, independent investigations."
Cost gate (S10): multi-agent is justified when "the value of the task is high enough to pay for the increased performance," and is unsuitable for domains "that require all agents to share the same context or involve many dependencies between agents."
Coordination style (S10): give subagents "frameworks for collaboration that define the division of labor" rather than "strict instructions," because "small changes to the lead agent can unpredictably change how subagents behave."

TEST: **KEEP an agent definition only if it (a) isolates context the main session should never see, or (b) supplies a distinct role the main session cannot hold simultaneously; DELETE agents that merely rename the main loop.**
TEST: **DELETE a multi-agent gate whose members must share the same context to do their job - that is a single-agent task paying N times the tokens.**

### P18. Tools and MCP - do not wrap what already works

Quote (S9): "More tools don't always lead to better outcomes. A common error we've observed is tools that merely wrap existing software functionality or API endpoints."
Quote (S2): "One of the most common failure modes we see is bloated tool sets that cover too much functionality."
Quote (S9): "Tool implementations should take care to return only high signal information back to agents. They should prioritize contextual relevance over flexibility."
Quote (S9): "Even small refinements to tool descriptions can yield dramatic improvements."
Consolidation (S9): prefer one tool that performs several underlying calls over several thin tools; namespace related tools with a common prefix.
Preference for CLI (S3): "CLI tools are the most context-efficient way to interact with external services."

TEST: **DELETE any tool, script, or MCP server that wraps something the agent can already invoke directly; KEEP only tools that consolidate a multi-step workflow or return higher-signal output than the raw call.**

---

## Part 4 - Verification design

### P19. The verifier must not be the author

Quote (S3): a second-opinion check means "a fresh model try to refute the result, so the agent doing the work isn't the one grading it."
Quote (S3): "A reviewer running in a fresh subagent context sees only the diff and the criteria you give it, not the reasoning that produced the change, so it evaluates the result on its own terms."
Quote (S3): "A fresh context improves code review since Claude won't be biased toward code it just wrote."
Corroboration (S8): the evaluator-optimizer pattern separates evaluation from generation into distinct calls, and works "when responses demonstrably improve with feedback and the evaluator can provide meaningful critiques."
Corroboration (S10): a dedicated CitationAgent, separate from the researcher, attributes claims to sources before results are returned.

TEST: **DELETE any validation gate that grades work using the same context that produced it; a gate earns its place only if the checker is blind to the author's reasoning.**

### P20. Prefer a deterministic check to an opinion

Quote (S3): "Claude stops when the work looks done. Without a check it can run, 'looks done' is the only signal available, and you become the verification loop."
Ladder of enforcement (S3), weakest to strongest: ask for the check in the prompt; set it as a `/goal` condition re-evaluated by a separate evaluator after every turn; make it a Stop hook that blocks the turn from ending until it passes (overridden after 8 consecutive blocks); or get a second opinion from a verification subagent or dynamic workflow.
Quote (S3): "Each step trades setup for attention."
Evidence rule (S3): "Have Claude show evidence rather than asserting success: the test output, the command it ran and what it returned, or a screenshot."
Failure pattern (S3): "The trust-then-verify gap ... Fix: Always provide verification (tests, scripts, screenshots). If you can't verify it, don't ship it."

TEST: **REPLACE a prose "remember to check X" rule with the cheapest mechanism on the ladder that actually closes the loop; if a deterministic check exists, the prose rule is redundant and gets DELETED.**
TEST: **A gate that emits an assertion rather than evidence (command run plus output) is not a gate - fix it or delete it.**

### P21. Judge against a rubric, not against vibes

Quote (S10): the team used "an LLM judge that evaluated each output against criteria in a rubric: factual accuracy, citation accuracy, completeness, source quality, and tool efficiency," and a single LLM call proved most consistent with human judgment.
Quote (S1): "Rubrics allow Claude to try and verify your taste in a particular field ... by using dynamic workflows and spinning up verifier agents"

TEST: **KEEP a review agent only if it carries an explicit rubric; a reviewer without stated criteria produces noise, and noise is DELETE-able.**

### P22. Adversarial reviewers over-report by construction

Quote (S3): "A reviewer prompted to find gaps will usually report some, even when the work is sound, because that is what it was asked to do. Chasing every finding leads to over-engineering: extra abstraction layers, defensive code, and tests for cases that can't happen. Tell the reviewer to flag only gaps that affect correctness or the stated requirements, and treat the rest as optional."

TEST: **REWRITE any critique asset that does not bound what counts as a finding; an unbounded critic manufactures work and is a net negative.**
This is the direct counterweight to stacking more review waves: each added critic raises the false-positive rate.

---

## Part 5 - Complexity budget

### P23. Add complexity only when it demonstrably improves outcomes

Quote (S8): "you should consider adding complexity only when it demonstrably improves outcomes."
Paraphrase (S8): find the simplest solution first; agentic systems trade latency and cost for capability, so skip them when a simpler approach works.
Quote (S8) on frameworks: they "often create extra layers of abstraction that can obscure the underlying prompts ... making them harder to debug."
Three implementation principles (S8): simplicity, transparency (show planning steps explicitly), and investing in the agent-computer interface as seriously as a human-computer interface.

TEST: **DELETE any layer of the harness for which no one can name the outcome it demonstrably improved.**

### P24. Build the asset at the moment its trigger fires, not before

Trigger table (S4), abbreviated: Claude gets a convention wrong twice -> CLAUDE.md. You keep typing the same prompt -> user-invocable skill. You paste the same playbook a third time -> skill. You keep copying from a system Claude cannot see -> MCP. A side task floods the conversation -> subagent. You want something to happen every time without asking -> hook. A second repo needs the same setup -> plugin.
Quote (S4): "You don't need to configure everything up front."
Quote (S4): "The same triggers tell you when to update what you already have."

TEST: **DELETE any asset that cannot name the concrete repeated failure or repeated prompt that caused it to exist; speculative assets are the default deletion candidate.**

### P25. Every feature has a stated context cost - use the published table

From S4's cost table: CLAUDE.md loads full content every request. Skills load descriptions at start and full content when used. MCP loads tool names at start with schemas deferred. Subagents are isolated from the main session. Hooks cost zero unless they return output.
Quote (S4): "Too much can fill up your context window, but it can also add noise that makes Claude less effective; skills may not trigger correctly, or Claude may lose track of your conventions."

TEST: **PRICE each asset by its loading tier before defending it - an always-loaded asset must clear a far higher bar than an on-demand one, and the cheapest fix for a marginal asset is demotion, not deletion.**

---

## Part 6 - The ledger criteria, condensed

Apply in order. The first one that fires decides the verdict.

| # | Criterion | Verdict |
|---|-----------|---------|
| 1 | The model already does this correctly without the asset (S3, P11) | DELETE |
| 2 | The content is derivable by reading the repo (S1, P10) | DELETE |
| 3 | It duplicates or conflicts with a directive in another layer (S1, P4/P7) | DELETE the copy |
| 4 | It hard-codes a choice better made from surrounding context (S1, P3) | REWRITE as a standard, or DELETE |
| 5 | It wraps functionality the agent can already invoke (S9, P18) | DELETE |
| 6 | It grades work using the context that produced it (S3, P19) | DELETE or re-seat the verifier |
| 7 | It is a critic with no bounded definition of a finding (S3, P22) | REWRITE or DELETE |
| 8 | It cannot name the repeated failure that caused it to exist (S4, P24) | DELETE |
| 9 | No one can name the outcome it demonstrably improved (S8, P23) | DELETE |
| 10 | It is needed rarely but is always loaded (S1, P6) | DEMOTE to on-demand |
| 11 | It is over ~200 lines (CLAUDE.md) or ~500 lines (SKILL.md) (S4, S5) | SPLIT |
| 12 | It must hold every time and is currently prose (S4, P16) | CONVERT to a hook |
| 13 | It describes a standard that could be executed or checked (S1, P9) | UPGRADE to test/rubric/script |
| 14 | It survives all of the above | KEEP, and record the outcome it protects |

## What the corpus does NOT say

Recorded so the ledger does not over-claim.

- S1 gives no guidance on hooks or validation gates at all; the hook and gate criteria above come from S3, S4, and S6, which are official docs but not the Claude 5 blog post.
- No source states a numeric ceiling on skill count, agent count, or rule count. The nearest quantitative constraints are the 200-line CLAUDE.md rule of thumb (S4/S6), the 500-line SKILL.md tip (S5), and the skill-listing budget of 1% of the context window (S5).
- No source claims that deleting assets improves quality in general. The strongest available claim is the specific measured one: over 80% of Claude Code's system prompt was removed "with no measurable loss" (S1). Absence of loss is the evidenced result, not a gain.
- S2's advice to curate canonical examples predates the Claude 5 generation and is partly superseded by S1's "examples constrain the exploration space." Where they conflict, S1 governs for Claude 5-generation models.
