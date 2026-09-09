# Anthropic loop and harness sources: primary-source report

Fetched 2026-09-08. All eight URLs returned HTTP 200.
Method: `WebFetch` first, then raw `curl` + HTML strip for each page, so every quote below is
verified against the actual page text rather than a summarizer's paraphrase.

---

## 1. https://claude.com/blog/getting-started-with-loops

"Loop engineering: Getting started with loops", by Delba de Oliveira and Michael Segner.

### a. Loop shape

Defines four loop types.
"we define loops as agents repeating cycles of work until a stop condition is met."
Categorized by how they are triggered, how they are stopped, which Claude Code primitive is used,
and which task type fits.

- **Turn-based.** Triggered by a user prompt.
  "Claude gathers context, takes action, checks its work, repeats if needed, and responds."
  Stop criteria: Claude judges it has completed the task or needs additional context.
- **Goal-based (`/goal`).** Triggered by a manual prompt in real time.
  "Each time Claude tries to stop, an evaluator model checks your condition and sends it back to
  work until the goal is met or a number of turns you define is reached."
  Stop criteria: goal achieved OR maximum number of turns reached.
- **Time-based (`/loop`, `/schedule`).** Triggered by a time interval.
  Stop criteria: "You cancel it, or the work completes (the PR merges, the queue is empty)."
  "`/loop` runs on your computer, so if you turn it off, it stops."
- **Proactive.** Triggered by an event or schedule, with no human in real time.
  "Each task exits when its goal is met. The routine itself runs until you turn it off."

### b. What verifies the work

The user, until the user encodes the check as a skill.
"You can improve the verification step by encoding your manual steps as a SKILL.md so Claude can
check more of its own work, end-to-end."
"This should include tools or connectors to allow Claude to see, measure or interact with the
result. The more quantitative the checks are, the easier it is for Claude to self-verify."

The human writes the skill up front. The example skill starts the dev server, interacts with the
control, screenshots before and after, requires zero new console errors, runs a Core Web Vitals
trace, and ends:
"If any step fails, fix the issue and rerun from step 1 — do not hand back partially verified work."

### c. Keep it simple / get out of the way (verbatim)

- "Not all tasks require complex loops; start with the simplest solution and use these patterns
  selectively."
- "Choose the right primitive and model for the job: Smaller tasks don't need multiple agents or
  loops. Some tasks can use cheaper and faster models."
- "Use scripts for deterministic work: Running a script is cheaper than reasoning through the steps."
- "Don't run routines more often that you need to: Match the interval to how often the thing you're
  watching changes"

### d. Separate verifier / fresh context / deterministic gate (verbatim)

- "Use a second agent for code reviews: A reviewer with fresh context is less biased and not
  influenced by the main agent's reasoning."
- "Loops that write code need loops that check it"
- "When you define the success criteria, Claude doesn't have to make a determination on what is
  'good enough' and end the loop early."
- "This is why deterministic criteria, such as number of tests passed or clearing a certain score
  threshold, are so effective."
- Example composite prompt: "When fixing a bug, use a workflow to explore three solutions in
  parallel worktrees and have a judge adversarially review them."

### e. Wrong or gamed check

No gaming discussion. Closest sentence:
"When an individual result doesn't meet the standard, don't stop at fixing the individual issue, try
to encode it to improve the system for all future iterations."

### f. Concrete numbers

Only the example turn cap "stop after 5 tries" and the example Lighthouse target of 90.
No costs, no success rates, no line counts.

---

## 2. https://claude.com/blog/the-ai-native-sdlc-playbook

### a. Loop shape

Six SDLC stages, each producing a version-controlled artifact that fires the next stage.
"First, you prompt each step by hand with the end state being a loop in which each accepted artifact
fires the next gate. Human attention concentrates at the gates, reviewing what the agent flagged
rather than starting each stage from scratch."

- Stage 1 Plan: product owner accepts `intent.md`.
- Stage 2 Design: `spec.md` accepted.
- Stage 3 Build: engineer approves `plan.md`, implementation runs with hooks firing on edits.
- Stage 4 Test: the session's own feedback loop, plus an eval suite gating configuration changes.
- Stage 5 Deploy: Claude PR review, hooks as approval gates, human code owner approval.
- Stage 6 Maintain: headless monitoring writes a new `intent.md`, which re-enters Stage 1.
  "at which point the loop starts feeding itself."

### b. What verifies the work

Two distinct mechanisms, and the post is emphatic they are different things.

The in-task feedback loop, set up by the engineer running the session:
"Always give Claude a way to verify its own work, whether tests, a build, or a screenshot diff."
"Claude iterates until the check passes, so what reaches the engineer has already passed it."
"Setting the loop up falls to the engineer running the session."

Separately, evals written by a platform engineer regression-test the agent configuration:
"Evals are the AI-native equivalent of stage-gate QA. In practice that means a suite that runs
whenever the agent's configuration changes."
"Gate configuration changes on the results. A skill change that drops the pass rate gets reviewed
before it merges."

PR review is performed by Claude; approval stays human.
"Findings do not approve or block a PR on their own, and branch protection still requires approval
from a code owner."

### c. Keep it simple / get out of the way (verbatim)

- "Keep it under a page, because Claude reads all of it at the start of a session and anything stale
  is taking up context for no benefit." (about `CLAUDE.md`)
- "A working rule helps here. When Claude makes a mistake twice, the correction goes into CLAUDE.md."
- "A hook that asks a human for approval belongs with the gates in Stage 5: Deploy, because an
  approval prompt during the build puts a person back on the critical path of all the sessions
  running in parallel."
- "Two or three sessions is a sensible starting point. The practical ceiling is how many streams one
  person can review properly, so add sessions only while review is keeping up."
- "Report at most five nits per review; summarize the rest as a count."

### d. Separate verifier / fresh context / frozen check / deterministic gate (verbatim)

- "The feedback loop should not be confused with a verifier subagent (Stage 3: Build). The feedback
  loop runs through the whole task as many times as the work. The verifier subagent, on the other
  hand, is one way to package the final check by running a fresh context window once the session
  believes the work is done. This way the verdict is not colored by the assumptions that produced
  the code."
- "A skill is a control, though an advisory one. It makes Claude likely to apply the policy while the
  code is written, and nothing forces a session to comply with it. A policy that must always hold
  needs something deterministic behind the skill, such as a hook that blocks the action or a review
  pass that re-checks the policy at the PR. The skill makes violations rare and the hook makes them
  close to impossible."
- "A skill is an advisory control while a hook is the deterministic layer behind it."
- "The script is version controlled and unit tested, and detection stays entirely deterministic, with
  no model involved."
- "The deterministic checks stay in CI, and the model-driven scan covers the context-dependent
  vulnerabilities those checks are not built to find."
- "Stage 6: Maintenance runs headless, with an independent confidence gate between stages, a
  deterministic check or an adversarial reviewing agent, deciding whether the previous stage's
  output continues or is escalated to a human."
- "The agent that proposed the fix has no route to approve it."
- "The governing principle is that the agent may act up to the production gate and cannot pass it."
- "Hooks are the approval gates. The gate condition is enforced every time, for everyone."
- "allowManagedHooksOnly means the approval gates from this play are the only hooks that run; nothing
  local can add to or replace them."

### e. Wrong or gamed check

The only page in the set that names check-gaming directly and fixes it structurally.

- "Finally, the loop itself needs protecting, because an agent fixing code must not be able to
  weaken the check on that code. A hook that blocks edits to test files during a fix task does this.
  The alternative is to check the diff in review and reject any change that touches a test."
- "For bug fixes, write the failing test first. Ask Claude to reproduce the bug as a test, run it,
  and confirm it fails for the reason you expect. Commit that test. Only then ask Claude to make it
  pass without editing the test, with the test-file hook from the final step enforcing the
  restriction. A test that existed before the fix, and that the agent couldn't rewrite, is proof the
  bug is gone."
- "hooks can block edits to migrations and infra without a change ticket during Stage 3: Build, and
  stop the agent editing test files during a fix task in Stage 4: Test."
- For noisy detection: "Dismissals tune the bands and help to reduce noise."

### f. Concrete numbers

| Item | Value |
|---|---|
| Eval suite seed | "20 to 50 real tasks from recent work" |
| Parallel sessions | "Two or three sessions is a sensible starting point" |
| UI screenshot iterations | "Two or three rounds is normal" |
| PR review nit cap | at most five, rest summarized as a count |
| Control bands | 1σ log only, 2σ Claude read-only diagnosis, 3σ Claude may act via PR or pre-approved runbook |
| Security scan cadence | weekly default for actively developed services |

---

## 3. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

Published Nov 26, 2025. Written by Justin Young.

### a. Loop shape

Two prompts, one agent harness.

Initializer agent, first context window only:
"The very first agent session uses a specialized prompt that asks the model to set up the initial
environment: an init.sh script, a claude-progress.txt file that keeps a log of what agents have
done, and an initial git commit that shows what files were added."

Coding agent, every subsequent session, prompted to run a fixed bearings sequence:
"Run pwd to see the directory you're working in."
"Read the git logs and progress files to get up to speed on what was recently worked on."
"Read the features list file and choose the highest-priority feature that's not yet done to work on."
Then run `init.sh`, do a basic end-to-end test of existing functionality, implement exactly one
feature, test it, commit with a descriptive message, update the progress file.

Footnote on the two "agents":
"We refer to these as separate agents in this context only because they have different initial user
prompts. The system prompt, set of tools, and overall agent harness was otherwise identical."

Termination: when every feature in the JSON list is marked `"passes": true`.

### b. What verifies the work

The same agent verifies itself, through browser automation.
"Claude mostly did well at verifying features end-to-end once explicitly prompted to use browser
automation tools and do all testing as a human user would."
"Providing Claude with these kinds of testing tools dramatically improved performance, as the agent
was able to identify and fix bugs that weren't obvious from the code alone."

The check list is written by the initializer agent from the user's prompt, before any feature code
exists, with every feature initially marked failing.

### c. Keep it simple

Nothing. The post argues the other direction.
"However, compaction isn't sufficient. Out of the box, even a frontier coding model like Opus 4.5
running on the Claude Agent SDK in a loop across multiple context windows will fall short of
building a production-quality web app if it's only given a high-level prompt."

### d. Separate verifier / frozen check (verbatim)

No separate verifier agent. It does describe a frozen check, meaning a check the working agent must
not be able to edit:

- "We prompt coding agents to edit this file only by changing the status of a passes field, and we
  use strongly-worded instructions like 'It is unacceptable to remove or edit tests because this
  could lead to missing or buggy functionality.'"
- "After some experimentation, we landed on using JSON for this, as the model is less likely to
  inappropriately change or overwrite JSON files compared to Markdown files."

Multi-agent is left open as future work:
"it's still unclear whether a single, general-purpose coding agent performs best across contexts, or
if better performance can be achieved through a multi-agent architecture. It seems reasonable that
specialized agents like a testing agent, a quality assurance agent, or a code cleanup agent, could
do an even better job at sub-tasks across the software development lifecycle."

### e. Wrong or gamed check

Names the premature-completion failure mode and fixes it structurally.
"A second failure mode would often occur later in a project. After some features had already been
built, a later agent instance would look around, see that progress had been made, and declare the
job done."
"One final major failure mode that we observed was Claude's tendency to mark a feature as complete
without proper testing. Absent explicit prompting, Claude tended to make code changes, and even do
testing with unit tests or curl commands against a development server, but would fail recognize that
the feature didn't work end-to-end."

Acknowledges the check has blind spots:
"Claude can't see browser-native alert modals through the Puppeteer MCP, and features relying on
these modals tended to be buggier as a result."

### f. Concrete numbers

"over 200 features" in the claude.ai clone feature list. Nothing else. No cost, rounds, or rates.

---

## 4. https://www.anthropic.com/engineering/harness-design-long-running-apps

Published Mar 24, 2026. Written by Prithvi Rajasekaran, Labs team.
This is the most load-bearing page in the set for the simple-versus-checked question.

### a. Loop shape

**V1, on Claude Opus 4.5, three agents, GAN-inspired.**
1. Planner turns a 1-4 sentence prompt into a full product spec. Prompted to be ambitious on scope
   and to stay at product and high-level technical design, not granular implementation, because
   "if the planner tried to specify granular technical details upfront and got something wrong, the
   errors in the spec would cascade into the downstream implementation."
2. Before each sprint the generator and evaluator negotiate a sprint contract: "agreeing on what
   'done' looked like for that chunk of work before any code was written." The generator proposes
   what it will build and how success will be verified; the evaluator reviews; they iterate until
   they agree.
3. Generator implements one feature per sprint on React, Vite, FastAPI, SQLite (later PostgreSQL),
   with git, and self-evaluates at the end of each sprint before handoff.
4. Evaluator drives the running app through Playwright MCP "the way a user would, testing UI
   features, API endpoints, and database states," then grades against the contract plus criteria
   covering product depth, functionality, visual design, and code quality.
   "Each criterion had a hard threshold, and if any one fell below it, the sprint failed and the
   generator got detailed feedback on what went wrong."
5. Communication between agents is by files.

**V2, on Claude Opus 4.6.** Sprints removed, context resets removed, one continuous generator
session with the SDK's automatic compaction, evaluator moved to a single pass at the end, then build
and QA rounds iterate.

The earlier frontend-design experiment ran generator and evaluator over "5 to 15 iterations per
generation", with the generator instructed "to make a strategic decision after each evaluation:
refine the current direction if scores were trending well, or pivot to an entirely different
aesthetic if the approach wasn't working."

### b. What verifies the work

A separate evaluator agent with live browser access. Self-evaluation is explicitly distrusted.
Criteria are written by the human up front and calibrated:
"I calibrated the evaluator using few-shot examples with detailed score breakdowns. This ensured the
evaluator's judgment aligned with my preferences, and reduced score drift across iterations."

Sample evaluator findings quoted in the post are specific enough to act on directly, for example:
"FAIL — Delete key handler at LevelEditor.tsx:892 requires both selection and selectedEntityId to be
set, but clicking an entity only sets selectedEntityId."
"FAIL — PUT /frames/reorder route defined after /{frame_id} routes. FastAPI matches 'reorder' as a
frame_id integer and returns 422."

### c. Keep it simple / stress-test the scaffolding (verbatim)

- "every component in a harness encodes an assumption about what the model can't do on its own, and
  those assumptions are worth stress testing, both because they may be incorrect, and because they
  can quickly go stale as models improve."
- "Our blog post Building Effective Agents frames the underlying idea as 'find the simplest solution
  possible, and only increase complexity when needed,' and it's a pattern that shows up consistently
  for anyone maintaining an agent harness."
- "The first set of harness results was encouraging, but it was also bulky, slow, and expensive. The
  logical next step was to find ways to simplify the harness without degrading its performance."
- "for tasks within that boundary, the evaluator became unnecessary overhead"
- "The practical implication is that the evaluator is not a fixed yes-or-no decision. It is worth the
  cost when the task sits beyond what the current model does reliably solo."
- "when a new model lands, it is generally good practice to re-examine a harness, stripping away
  pieces that are no longer load-bearing to performance and adding new pieces to achieve greater
  capability that may not have been possible before."
- "In some cases, that will mean the scaffold surrounding the model matters less over time, and
  developers can wait for the next model and see certain problems solve themselves."

**Important counterweight. Cutting too much at once failed:**
- "In my first attempt to simplify, I cut the harness back radically and tried a few creative new
  ideas, but I wasn't able to replicate the performance of the original. It also became difficult to
  tell which pieces of the harness design were actually load-bearing, and in what ways. Based on
  that experience, I moved to a more methodical approach, removing one component at a time and
  reviewing what impact it had on the final result."
- Also: the planner stayed because removing it hurt. "Without the planner, the generator
  under-scoped: given the raw prompt, it would start building without first speccing its work, and
  end up creating a less feature-rich application than the planner did."

### d. Separate verifier / fresh context (verbatim)

- "When asked to evaluate work they've produced, agents tend to respond by confidently praising the
  work—even when, to a human observer, the quality is obviously mediocre. This problem is
  particularly pronounced for subjective tasks like design, where there is no binary check
  equivalent to a verifiable software test."
- "However, even on tasks that do have verifiable outcomes, agents still sometimes exhibit poor
  judgment that impedes their performance while completing the task. Separating the agent doing the
  work from the agent judging it proves to be a strong lever to address this issue."
- "The separation doesn't immediately eliminate that leniency on its own; the evaluator is still an
  LLM that is inclined to be generous towards LLM-generated outputs. But tuning a standalone
  evaluator to be skeptical turns out to be far more tractable than making a generator critical of
  its own work, and once that external feedback exists, the generator has something concrete to
  iterate against."
- "'Is this design beautiful?' is hard to answer consistently, but 'does this follow our principles
  for good design?' gives Claude something concrete to grade against."
- On fresh context: "Some models also exhibit 'context anxiety,' in which they begin wrapping up work
  prematurely as they approach what they believe is their context limit. Context resets—clearing the
  context window entirely and starting a fresh agent, combined with a structured handoff that
  carries the previous agent's state and the next steps—addresses both these issues."
- "While compaction preserves continuity, it doesn't give the agent a clean slate, which means
  context anxiety can still persist. A reset provides a clean slate, at the cost of the handoff
  artifact having enough state for the next agent to pick up the work cleanly."
- Cost of that choice, stated plainly: "This solves the core issue, but adds orchestration
  complexity, token overhead, and latency to each harness run."

### e. Wrong or gamed check

The evaluator itself is treated as the thing that goes wrong. The fix is human tuning against logs.

- "Getting the evaluator to perform at this level took work. Out of the box, Claude is a poor QA
  agent. In early runs, I watched it identify legitimate issues, then talk itself into deciding they
  weren't a big deal and approve the work anyway. It also tended to test superficially, rather than
  probing edge cases, so more subtle bugs often slipped through. The tuning loop was to read the
  evaluator's logs, find examples where its judgment diverged from mine, and update the QAs prompt to
  solve for those issues. It took several rounds of this development loop before the evaluator was
  grading in a way that I found reasonable."
- Residual failure after tuning: "small layout issues, interactions that felt unintuitive in places,
  and undiscovered bugs in more deeply nested features that the evaluator hadn't exercised
  thoroughly. There was clearly more verification headroom to capture with further tuning."
- A check that physically cannot work: "Claude can't actually hear, which made the QA feedback loop
  less effective with respect to musical taste."
- Criteria wording steers output in unintended ways: "The wording of the criteria steered the
  generator in ways I didn't fully anticipate. Including phrases like 'the best designs are museum
  quality' pushed designs toward a particular visual convergence."
- Score trajectory is not monotonic: "While scores generally improved over iterations, the pattern
  was not always cleanly linear. Later implementations tended to be better as a whole, but I
  regularly saw cases where I preferred a middle iteration over the last one. Implementation
  complexity also tended to increase across rounds."

### f. Concrete numbers

| Item | Value |
|---|---|
| Frontend design loop | 5 to 15 iterations per generation; full runs up to 4 hours |
| V1 solo baseline (game maker) | 20 min, $9 |
| V1 full harness | 6 hr, $200, "over 20x more expensive" |
| V1 planner output | 16-feature spec across ten sprints |
| Sprint 3 contract criteria | 27 |
| V2 total (browser DAW) | 3 hr 50 min, $124.70 |
| V2 planner | 4.7 min, $0.46 |
| V2 build round 1 / 2 / 3 | 2 hr 7 min $71.08 / 1 hr 2 min $36.89 / 10.9 min $5.88 |
| V2 QA round 1 / 2 / 3 | 8.8 min $3.24 / 6.8 min $3.09 / 9.6 min $4.06 |
| Continuous generator run, no sprints | "over two hours" |

---

## 5. https://www.anthropic.com/engineering/building-effective-agents

### a. Loop shapes

Augmented LLM as the base building block, then, in increasing complexity: prompt chaining with
programmatic gates between steps; routing; parallelization (sectioning and voting);
orchestrator-workers; evaluator-optimizer; and autonomous agents.

For agents:
"Agents begin their work with either a command from, or interactive discussion with, the human user.
Once the task is clear, agents plan and operate independently, potentially returning to the human
for further information or judgement. During execution, it's crucial for the agents to gain 'ground
truth' from the environment at each step (such as tool call results or code execution) to assess its
progress. Agents can then pause for human feedback at checkpoints or when encountering blockers. The
task often terminates upon completion, but it's also common to include stopping conditions (such as
a maximum number of iterations) to maintain control."

### b. What verifies the work

Automated tests for code, plus human review.
"Code solutions are verifiable through automated tests; Agents can iterate on solutions using test
results as feedback"
"However, whereas automated testing helps verify functionality, human review remains crucial for
ensuring solutions align with broader system requirements."

### c. Keep it simple (verbatim). This page is the origin of that norm.

- "Consistently, the most successful implementations weren't using complex frameworks or specialized
  libraries. Instead, they were building with simple, composable patterns."
- "When building applications with LLMs, we recommend finding the simplest solution possible, and
  only increasing complexity when needed. This might mean not building agentic systems at all.
  Agentic systems often trade latency and cost for better task performance, and you should consider
  when this tradeoff makes sense."
- "For many applications, however, optimizing single LLM calls with retrieval and in-context examples
  is usually enough."
- "However, they often create extra layers of abstraction that can obscure the underlying prompts and
  responses, making them harder to debug. They can also make it tempting to add complexity when a
  simpler setup would suffice."
- "We suggest that developers start by using LLM APIs directly: many patterns can be implemented in a
  few lines of code. If you do use a framework, ensure you understand the underlying code. Incorrect
  assumptions about what's under the hood are a common source of customer error."
- "To repeat: you should consider adding complexity only when it demonstrably improves outcomes."
- "Success in the LLM space isn't about building the most sophisticated system. It's about building
  the right system for your needs. Start with simple prompts, optimize them with comprehensive
  evaluation, and add multi-step agentic systems only when simpler solutions fall short."
- "Maintain simplicity in your agent's design."
- "Frameworks can help you get started quickly, but don't hesitate to reduce abstraction layers and
  build with basic components as you move to production."

### d. Separate verifier / deterministic gate (verbatim)

- "Implementing guardrails where one model instance processes user queries while another screens them
  for inappropriate content or requests. This tends to perform better than having the same LLM call
  handle both guardrails and the core response."
- "For complex tasks with multiple considerations, LLMs generally perform better when each
  consideration is handled by a separate LLM call, allowing focused attention on each specific
  aspect."
- "Reviewing a piece of code for vulnerabilities, where several different prompts review and flag the
  code if they find a problem."
- "Evaluating whether a given piece of content is inappropriate, with multiple prompts evaluating
  different aspects or requiring different vote thresholds to balance false positives and negatives."
- "In the evaluator-optimizer workflow, one LLM call generates a response while another provides
  evaluation and feedback in a loop."
- "This workflow is particularly effective when we have clear evaluation criteria, and when iterative
  refinement provides measurable value. The two signs of good fit are, first, that LLM responses can
  be demonstrably improved when a human articulates their feedback; and second, that the LLM can
  provide such feedback."
- Prompt chaining is described as adding "programmatic checks (see 'gate' in the diagram) on any
  intermediate steps."

### e. Wrong or gamed check

Not addressed. Nearest sentence:
"The autonomous nature of agents means higher costs, and the potential for compounding errors. We
recommend extensive testing in sandboxed environments, along with the appropriate guardrails."

### f. Concrete numbers

None. SWE-bench Verified is referenced with no figure attached.

---

## 6. https://www.anthropic.com/engineering/AI-resistant-technical-evaluations

Published Jan 21, 2026. Written by Tristan Hume, lead on the performance optimization team.
About hiring evaluations, not agent loops, but it is the sharpest page in the set on check design
and check decay.

### a. Loop shape

No agent loop. A take-home in which candidates optimize code for a simulated accelerator, with a
hot-reloading Perfetto trace showing every instruction, scored continuously by cycle count. Three
versions over roughly two years, each redesigned after a Claude model beat it.

Version 3 is a sequence of Zachtronics-style puzzles on a tiny constrained instruction set,
optimizing for minimal instruction count.

### b. What verifies the work

A deterministic simulator. Score is cycle count from the simulated machine, no human reviewer per
submission. In version 3, tooling is deliberately withheld:
"Unlike Zachtronics games, I intentionally provided no visualization or debugging tools. The starter
code only checks whether solutions are valid. Building debugging tools is part of what's being
tested: you can either insert well-crafted print statements or ask a coding model to generate an
interactive debugger in a few minutes. Judgment about how to invest in tooling is part of the
signal."

The check is written by the human designer, once, in advance, and rewritten when it stops
discriminating.

### c. Keep it simple

No such sentences. The design direction is added depth. The closest thing to a
cut-what-does-not-earn-its-place rule:
"I wrote cleaner starter code, added new machine features for more depth, and removed multicore
(which Claude had already solved, and which only slowed down development loops without adding
signal)."

Related design principles, quoted verbatim:
- "High signal: The take-home should avoid problems that hinge on a single insight and ensure
  candidates have many chances to show their full abilities — leaving as little as possible to
  chance. It should also have a wide scoring distribution, and ensure enough depth that even strong
  candidates don't finish everything."
- "No specific domain knowledge: People with good fundamentals can learn specifics on the job."

### d. Separate verifier / frozen check / deterministic gate

No sentences arguing for a separate model verifier. The entire design leans on a deterministic
scorer rather than judgment, precisely because judgment-based checks were not testable objectively:
"Nowadays performance engineers at Anthropic still have lots of work to do, but it looks more like
tough debugging, systems design, performance analysis, figuring out how to verify the correctness of
our systems, and figuring out how to make Claude's code simpler and more elegant. Unfortunately
these things are tough to test in an objective way without a lot of time or common context."

### e. Wrong or gamed check

The whole post is about a check going stale, the closest analogue in this set to a check that no
longer measures what it claims.

- "A take-home that distinguishes well between human skill levels today may be trivially solved by
  models tomorrow—rendering it useless for evaluation."
- "By May 2025, Claude 3.7 Sonnet had already crept up to the point where over 50% of candidates
  would have been better off delegating to Claude Code entirely."
- "I had a problem. We were about to release a model where the best strategy on our take-home would
  be delegating to Claude Code."
- Attempt 1 failed because the problem was in-distribution: "In hindsight, this wasn't the right
  problem to try. Engineers across many platforms have struggled with data transposition and bank
  conflicts, so Claude has substantial training data to draw on. While I'd found my solution from
  first principles, Claude could draw on a larger toolbox of experience."
- He nearly shipped a broken check and caught it only by pushing harder: "It seemed like I had my new
  problem, now I just had to hope human candidates could get it fast enough. But I had some nagging
  doubt, so I double-checked using Claude Code's 'ultrathink' feature with longer thinking budgets
  ... and it solved it."
- He rejects banning the tool: "Some colleagues suggested banning AI assistance. I didn't want to do
  this."
- He rejects simply raising the bar, because it degrades the human's role: "The concern here was that
  Claude works fast. ... The dominant strategy might become sitting back and watching."
- Validation of the replacement check was done by humans other than the author: "I filled out more
  puzzles and had colleagues verify that people less steeped in the problem than me could still
  outperform Claude."
- Closing trade: "The original worked because it resembled real work. The replacement works because
  it simulates novel work."

### f. Concrete numbers

| Item | Value |
|---|---|
| Candidates completed | over 1,000 |
| Hires | dozens, most of the current performance engineering team |
| Time limit | 4 hours, later cut to 2 |
| Delegation crossover | over 50% of candidates better off delegating to Claude Code by May 2025 |
| 2164 cycles | Claude Opus 4 after many hours in the test-time compute harness |
| 1790 cycles | Claude Opus 4.5 in a casual Claude Code session, ~ best human in 2 hours |
| 1579 cycles | Claude Opus 4.5 after 2 hours in the test-time compute harness |
| 1548 cycles | Claude Sonnet 4.5 after many more than 2 hours of test-time compute |
| 1487 cycles | Claude Opus 4.5 after 11.5 hours in the harness |
| 1363 cycles | Claude Opus 4.5 in an improved harness after many hours |

Best human given unlimited time "substantially exceeds what Claude has achieved even with extensive
test-time compute", with no number given.

---

## 7. https://www.anthropic.com/engineering/managed-agents

"Scaling Managed Agents: Decoupling the brain from the hands", published Apr 08, 2026.
By Lance Martin, Gabe Cemaj, and Michael Cohen.

### a. Loop shape

A meta-harness built from three virtualized interfaces:
"a session (the append-only log of everything that happened), a harness (the loop that calls Claude
and routes Claude's tool calls to the relevant infrastructure), and a sandbox (an execution
environment where Claude can run code and edit files)."

Runtime flow: the orchestration layer pulls pending events from the session log, the harness calls
Claude, tool calls go out uniformly as `execute(name, input) → string`, results come back as
strings, and the harness records durable events with `emitEvent(id, event)`. On harness crash, a new
one reboots with `wake(sessionId)`, calls `getSession(id)` for the event log, and resumes from the
last event. `getEvents()` lets the brain re-read positional slices of history.

No termination criterion is stated beyond task completion.

### b. What verifies the work

Nothing. There is no verification, QA, evaluator, or test content on this page at all.

### c. Keep it simple

No simplicity sentences, but the strongest statement in the set on scaffolding going stale:

- "A common thread across this work is that harnesses encode assumptions about what Claude can't do
  on its own. However, those assumptions need to be frequently questioned because they can go stale
  as models improve."
- "As just one example, in prior work we found that Claude Sonnet 4.5 would wrap up tasks prematurely
  as it sensed its context limit approaching—a behavior sometimes called 'context anxiety.' We
  addressed this by adding context resets to the harness. But when we used the same harness on Claude
  Opus 4.5, we found that the behavior was gone. The resets had become dead weight."
- On a security mitigation that encodes the same kind of expiring assumption: "Narrow scoping is an
  obvious mitigation, but this encodes an assumption about what Claude can't do with a limited
  token—and Claude is getting increasingly smart. The structural fix was to make sure the tokens are
  never reachable from the sandbox where Claude's generated code runs."
- "We're opinionated about the shape of these interfaces, not about what runs behind them."

### d. Separate verifier / frozen check / deterministic gate

None for work quality. The one structural argument concerns irreversible context decisions:
"But irreversible decisions to selectively retain or discard context can lead to failures. It is
difficult to know which tokens the future turns will need."
"We separated the concerns of recoverable context storage in the session and arbitrary context
management in the harness because we can't predict what specific context engineering will be
required in future models."

### e. Wrong or gamed check

Not applicable. The nearest adversarial content is prompt injection reaching credentials, fixed
structurally by moving tokens out of the sandbox rather than by adding a check.

### f. Concrete numbers

"our p50 TTFT dropped roughly 60% and p95 dropped over 90%." Nothing else.

---

## 8. https://code.claude.com/docs/en/hooks (Stop hook and goal/verification parts only)

### a. Stop hook definition (verbatim)

"Runs when the main Claude Code agent has finished responding. Does not run if the stoppage occurred
due to a user interrupt. API errors fire StopFailure instead."

A blocking Stop hook is the mechanism that turns a single turn into a loop.

### b. `/goal` (verbatim)

"The /goal command is a built-in shortcut for a session-scoped prompt-based Stop hook. Use it when
you want Claude to keep working toward a condition without writing hook configuration."

### c. What can verify at Stop

Three hook types are supported at Stop: a shell command, a prompt-based hook, and an agent hook.

- Prompt hooks "use an LLM to evaluate whether to allow or block an action".
- Agent hooks: "Instead of a single LLM call, an agent hook spawns a subagent that can read files,
  search code, and inspect the codebase to verify conditions."
- "Agent hooks are useful when verification requires inspecting actual files or test output, not just
  evaluating the hook input data alone."
- Documented agent-hook example prompt: "Verify that all unit tests pass. Run the test suite and
  check the results. $ARGUMENTS"
- Documented prompt-hook example: "This Stop hook asks the LLM to evaluate whether all tasks are
  complete before allowing Claude to finish."

### d. Stop input fields (verbatim)

"In addition to the common input fields, Stop hooks receive stop_hook_active, last_assistant_message,
background_tasks, and session_crons."

"The last_assistant_message field contains the text content of Claude's final response, so hooks can
access it without parsing the transcript file. For hooks that act on the just-completed turn, such
as read-aloud or notification hooks, use this field rather than reading transcript_path: the
transcript file isn't guaranteed to include the final message at Stop time on all versions."

"The background_tasks and session_crons arrays let hooks distinguish 'session is done' from 'session
is paused waiting for background work to wake it back up'."

### e. Stop decision control (verbatim)

Correction worth noting: the decision value is `"block"`, not `continue`/`allow`. A first-pass
summarizer got this wrong; the raw doc says:

- `decision`: "'block' prevents Claude from stopping. Omit to allow Claude to stop"
- `reason`: "Required when decision is 'block'. Tells Claude why it should continue"
- `hookSpecificOutput.additionalContext`: "Non-error feedback for Claude. The conversation continues
  so Claude can act on it, but unlike decision: 'block' it is shown in the transcript as hook
  feedback rather than a hook error"
- Exit code 2: "A hook that blocks by exiting 2 routes the same way as reason: Claude receives the
  stderr message as the explanation for why it should continue."
- Exit-code table row: "Stop | Yes | Prevents Claude from stopping, continues the conversation"

### f. Infinite-loop protection. This is the deterministic gate on the gate.

- "The stop_hook_active field is true when Claude Code is already continuing as a result of a stop
  hook. Check this value or process the transcript to avoid blocking on a condition that will never
  resolve. Claude Code overrides the hook and ends the turn after 8 consecutive blocks."
- "Use additionalContext when the hook is working as designed and giving Claude guidance, such as
  'run the test suite before finishing'. It keeps the conversation going through the same loop
  protections as decision: 'block', namely the stop_hook_active input and the 8-consecutive-
  continuation cap, but the transcript labels it Stop hook feedback and no hook error notification
  is shown"
- Prompt hooks can declare a check unsatisfiable via the `impossible` field: "The model returns it
  with ok: false when it judges the condition can never be satisfied. On Stop and SubagentStop,
  Claude Code then lets the turn end instead of feeding the reason back. Agent hooks and other events
  ignore it"

### g. SubagentStop (verbatim)

- Exit-code table row: "SubagentStop | Yes | Prevents the subagent from stopping"
- "In addition to the common input fields, SubagentStop hooks receive stop_hook_active, agent_id,
  agent_type, agent_transcript_path, and last_assistant_message. The agent_type field is the value
  used for matcher filtering."
- "SubagentStop hooks use the same decision control format as Stop hooks ... Returning decision:
  'block' with a reason keeps the subagent running and delivers reason to the subagent as its next
  instruction."
- "To inject context into the parent session after a subagent returns, use a PostToolUse hook on the
  Agent tool instead."
- In skill or agent frontmatter: "Claude Code converts a Stop hook here to SubagentStop, the event it
  fires when a subagent completes."

### h. Concrete numbers

8 consecutive continuations, then Claude Code overrides the hook and ends the turn regardless.

---

## Cross-page synthesis

**The simplicity norm and its one recorded failure mode.** Building Effective Agents supplies the
canonical rule: simplest solution first, complexity only when it demonstrably improves outcomes.
Managed Agents supplies the reason components should be re-examined at all: every harness component
encodes an assumption about model weakness, and those assumptions expire. But the Mar 2026 harness
post is the only source that reports what happens when you act on the rule aggressively: cutting the
harness back radically at once both lost the performance and destroyed the ability to attribute it.
The working method was one component removed at a time, measured. That is the operational form of
the rule, and it is stronger evidence than the rule stated abstractly.

**Self-evaluation is the failure the separate verifier exists to fix.** Three independent sources
converge. The Nov 2025 post: a later agent "would look around, see that progress had been made, and
declare the job done," and Claude marks features complete without end-to-end testing. The Mar 2026
post: agents "confidently praising the work" they produced. The SDLC playbook: a fresh context window
so "the verdict is not colored by the assumptions that produced the code." The Mar 2026 post gives
the sharpest tractability argument: making the generator self-critical is harder than making a
standalone evaluator skeptical.

**Only two sources handle a gamed check.** The SDLC playbook is explicit and structural: a hook
blocks test-file edits during a fix, and the test is committed before the fix so the agent cannot
rewrite it. The Nov 2025 post does the same thing informally: the feature list may only be edited by
flipping a `passes` field, and JSON was chosen over Markdown because the model overwrites it less
readily. The Mar 2026 post handles a different failure, a lenient checker rather than a gamed one,
and the fix is a human reading evaluator logs over several rounds and rewriting the QA prompt.

**Check decay is the under-covered risk.** The evals post is the only source that studies a check
that stops discriminating over time, and its lesson generalizes past hiring: a check the model has
seen the shape of before will be beaten, doubt about a check should be resolved by pushing harder
against it rather than shipping it, and validation by someone other than the check's author caught
what the author's familiarity hid.

**Deterministic beats model judgment where it is available.** The loops post: "This is why
deterministic criteria, such as number of tests passed or clearing a certain score threshold, are so
effective." The SDLC playbook: skills are advisory, hooks are the deterministic layer behind them,
and detection "stays entirely deterministic, with no model involved." The evals post picks a cycle
counter over a rubric. The hooks docs put a deterministic 8-continuation cap behind even a
model-based Stop check, which is the only mechanism in the set that bounds a check that will never
be satisfied.

---

## UNREACHABLE URLs

None. All eight returned HTTP 200.
