# Anthropic engineering sources for the agentic software factory

Research notes behind the factory design in `docs/factory/`, recording what nine Anthropic sources say and nothing else.

## Sources

| URL | Date | What it is | Credibility |
|---|---|---|---|
| https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | 2025-11-26 | Initializer plus coding-agent harness, built by cloning claude.ai autonomously. | First-party, named author, companion code in claude-quickstarts. |
| https://www.anthropic.com/engineering/harness-design-long-running-apps | 2026-03-24 | Planner, generator, and evaluator harness, plus what to delete as models improve. | First-party Anthropic Labs, named author, reports real costs and runtimes. |
| https://www.anthropic.com/engineering/managed-agents | 2026-04-08 | Hosted agent service split into brain, hands, and session. | First-party architecture writeup with measured latency, shaped by one product. |
| https://www.anthropic.com/engineering/april-23-postmortem | 2026-04-23 | Postmortem on three stacked regressions in Claude Code quality. | Highest, a dated incident report with versions and a measured regression. |
| https://www.anthropic.com/engineering/AI-resistant-technical-evaluations | 2026-01-21 | How a hiring take-home was redesigned after models beat it. | Named author, single-team experience, small sample. |
| https://www.anthropic.com/engineering/multi-agent-research-system | 2025-06-13 | Orchestrator-worker research system with delegation and operations detail. | First-party with reported eval method and numbers, oldest agent post. |
| https://www.anthropic.com/engineering/building-effective-agents | 2024-12-19 | Taxonomy of workflow patterns and the case for restraint. | Foundational and widely cited, but predates every current model. |
| https://claude.com/blog/the-ai-native-sdlc-playbook | 2026-08-21 | Six-stage lifecycle where each stage commits an artifact. | Product-marketing venue, substantive structure, needs the marketing stripped. |
| https://github.com/anthropics/cwc-long-running-agents | 2026 | Runnable hooks and an evaluator subagent, Apache-2.0. | Real code, self-described teaching example rather than production. |

## Effective harnesses

Rules we took

- Use a different prompt for the first session than for every session after it, because the first one only builds the environment: "a different prompt for the very first context window" - loop.
- Have the setup session leave behind a start script, a progress log, a feature list, and a baseline commit, with every feature defaulting to "passes: false" - plan, loop.
- Open every session the same way: confirm the directory, read the git log and progress file, pick the highest-priority incomplete item, start the app, and smoke-test it before touching code, because otherwise "each new session begins with no memory of what came before" - loop.
- Forbid test tampering in the prompt itself: "It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality." - loop, verify.
- Keep each session to a single item, which the source calls "critical": "only one feature at a time" - ticket, loop.
- Do not trust code inspection as verification, because "Claude tended to make code changes...but would fail recognize that the feature didn't work end-to-end." - verify.
- Give the agent browser automation so it exercises the app "a human user would", and record the blind spots, such as invisible native alert modals - verify.
- Treat compaction as insufficient on its own and let git carry recovery, since compaction "isn't sufficient" - ops.

Skip: the closing open questions about multi-agent variants and non-web domains, which source two answers with evidence.

## Harness design

Rules we took

- Let the planner be "ambitious about scope" on deliverables and stop short of implementation detail, because "if the planner tried to specify granular technical details upfront and got something wrong, the errors in the spec would cascade" - brief, plan.
- Never let the builder grade itself, because agents keep "confidently praising the work, even when, to a human observer, the quality is obviously mediocre" - judge.
- Put the skepticism in a separate agent, since "tuning a standalone evaluator to be skeptical turns out to be far more tractable than making a generator critical of its own work" - judge.
- Agree on what done means before implementation and grade against it with "hard thresholds", where failing one criterion fails the whole unit - ticket, verify.
- Pass work between stages as files, where "one agent would write a file, another agent would read it and respond either within that file or with a new file" - plan, ticket, loop.
- Reset context rather than compacting when you need a clean slate, because "Compaction preserves continuity, it doesn't give the agent a clean slate" and "context anxiety" survives it - loop.
- Require findings that name code and reproduce, not verdicts, as in a report that a fill function "exists but isn't triggered properly on mouseUp" - judge.
- Tune the judge from its own transcripts: "Read the evaluator's logs, find examples where its judgment diverged from mine" - judge.
- Re-check every harness component against the current model, because "Every component in a harness encodes an assumption about what the model can't do on its own" - ops.

Skip: the retro-game and music-tool demo narratives, which are illustration rather than method.

## Managed agents

Rules we took

- Keep the durable log outside the model, as "a context object that lives outside Claude's context window" - ops, loop.
- Separate storing context from choosing context, and avoid "irreversible decisions to selectively retain or discard context" - ops.
- Make infrastructure failures legible to the agent by surfacing a dead sandbox "as a tool-call error and passed it back to Claude" - ops.
- Let a fresh process resume a session rather than restart it, so a crashed harness is recoverable by design - ops.
- Bundle credentials with the resource so pushes work "without the agent ever handling the token itself" - ops.
- Proxy tool credentials so that "the harness is never made aware of any credentials", because "a prompt injection only had to convince Claude to read its own environment" - ops.
- Delete harness features that outlive their model, since context resets added for one model became "dead weight" on the next - ops.

Skip: the operating-system analogy and the service API listing, which are specific to a hosted product.

## April postmortem

Rules we took

- Expect regressions to stack and mask each other, as a default change, a cache bug, and a prompt line did here - ops.
- Watch one-shot cleanup logic, because a header meant to run once instead dropped reasoning "on every turn for the rest of the session" - ops.
- Do not assume terseness is free, because "keep text between tool calls to ≤25 words" cost three percent of coding quality and was reverted - judge, ops.
- Expect your existing gates to miss this class of bug, since code review, unit tests, end-to-end tests, and dogfooding all did - verify, ops.
- Distrust evals that only partly reproduce a reported problem, which here "initially reproduced the issues" poorly - judge.
- Run broad per-model evaluations for every system prompt change, and keep ablation testing that measures the impact of individual lines - judge, ops.
- Gate model-specific changes to their target model only, and add soak periods and gradual rollout for anything that touches intelligence - ops.
- Make sure the people dogfooding run the same build users run, not an internal variant - ops.

Skip: the usage-limit reset and the developer-communications commitments.

## AI-resistant evaluations

Rules we took

- Assume an evaluation decays on the model-release cadence, since successive models went from beating most applicants to matching the best - judge.
- Distrust any task where the model can lean on prior art, because "Claude has substantial training data to draw on" - judge.
- Distrust any task solvable by "a larger toolbox of experience" rather than by reasoning from first principles - judge.
- Move the task out of distribution when you need separation, using "a tiny, heavily constrained instruction set" - judge.
- Accept the trade this forces: "The original worked because it resembled real work. The replacement works because it simulates novel work." - judge.
- Use several independent sub-problems rather than one, and avoid problems "that hinge on a single insight" - judge, verify.
- Scale the work past what anyone finishes, so scores spread: "strong candidates don't finish everything" - judge.

Skip: the hiring framing and the cycle-count benchmark table.

## Multi-agent research

Rules we took

- Give every delegated task an objective, an output format, tool guidance, and boundaries, or agents "duplicate work, leave gaps, or fail to find necessary information" - ticket.
- Budget the cost before delegating, because multi-agent runs use "about 15× more tokens than chats" - ops.
- Expect spend to drive quality, since token usage explained "80% of the variance" in performance - ops.
- Write explicit effort budgets by task class into the prompt, after the system once spawned fifty subagents for a simple query - ticket, loop.
- Order the work broad to narrow: "Start wide, then narrow down" - loop.
- Invest in tool descriptions, because "Tool design and selection are critical" and bad ones "send agents down completely wrong paths" - loop.
- Score with one call and one rubric, since a "Single LLM call with a single prompt outputting scores...was the most consistent and aligned with human judgements" - judge.
- Start the eval set at roughly twenty real tasks rather than waiting for a large suite - judge.
- Build for recovery, so the system can "resume from where the agent was when errors occurred", and deploy without killing in-flight runs - ops.
- Remember agents are "non-deterministic between runs, even with identical prompts", so single-run comparisons prove little - judge, ops.

Skip: the research-product framing, which needs translating to a code domain.

## Building effective agents

Rules we took

- Prefer workflows "orchestrated through predefined code paths" over agents that "dynamically direct their own processes and tool usage", and confine agency to execution - brief, plan, loop.
- Chain prompts where the task decomposes cleanly into fixed steps, which is what brief to spec to plan is - brief, plan.
- Use voting, "Running the same task multiple times to get diverse outputs", which is the argument for two independent critics rather than one - judge.
- Use orchestrator-workers only for "complex tasks where you can't predict the subtasks needed" - ticket.
- Run an evaluator-optimizer loop only where "clear evaluation criteria" already exist, so write the criteria before the loop - verify, judge.
- Design tools as carefully as a human interface, and "Give the model enough tokens to 'think' before it writes itself into a corner" - loop.
- Make misuse structurally hard: "Change the arguments so that it is harder to make mistakes" - loop.
- Expect tool work to outweigh prompt work, since on one benchmark they "spent more time optimizing tools than the overall prompt" - loop.
- Hold every addition to one bar: "Add complexity only when it demonstrably improves outcomes" - brief, plan, ops.
- Be wary of frameworks that "obscure the underlying prompts and responses, making them harder to debug" - ops.

Skip: nothing is marketing, but treat its capability assumptions as dated by two years.

## AI-native SDLC

Rules we took

- Commit one artifact per stage and let it trigger the next, running intent to spec to plan to pull request to monitoring - brief, plan, ticket, ops.
- Write the request in the requester's own words, capturing "what is wanted, why, and under which constraints" - brief.
- Generate the spec with policy skills already loaded, so brand, security, and compliance conflicts surface before engineering sees it, and "Both phases happen in a single prompted session" - brief, plan.
- Do not start work until a written plan names files, order of work, risks, and proof of completion, and is committed - plan, ticket.
- Keep repository conventions "Under a page", and update them whenever the agent makes the same mistake twice - ops.
- Have the agent verify before a human looks: "Run the tests, run the build, take the screenshot" - verify.
- Write the failing test first on bug fixes, and use hooks to stop the agent editing tests during the fix - verify.
- Keep twenty to fifty real tasks as an eval suite, run it on every change to conventions, skills, or hooks, and add one eval per incident - judge, ops.
- Fix the review passes and severities in one file, separating "Important vs. Nit" and excluding what CI already enforces - judge.
- Give the agent no route to approve, and put allow, ask, and block gates in hooks - ops.
- Escalate monitoring in bands, from logging, to read-only diagnosis, to acting on a pre-approved runbook - ops.
- Track paired leading and lagging metrics per stage, such as first-pass merge rate against rework cycles - ops.

Skip: the product placement and the claim that agents multiply code output.

## cwc-long-running-agents

Rules we took

- Start every criterion false in a results file, so nothing is done until something flips it: "passes": false - verify.
- Block writes to that file unless evidence was opened first, and clear the evidence log after each write so the next claim needs fresh proof - verify.
- Copy the honesty about the gate's limits, which is "a teaching example, not a security boundary" and where "Bash sed/jq can rewrite the file unchecked" - verify.
- Give the judge no write tools and no shared history, so it grades from a context that never saw the build - judge.
- Keep the handoff note in four fixed sections, Done, In progress, Next, and Notes, read at session start and updated at every completion - loop.
- Count a test as passing only after running against the live app, opening the evidence, and confirming it matches - verify.
- Queue interruptions rather than serving them, finishing the current item first - loop.
- Give the operator a stop file that halts tool calls and a steering file whose "OPERATOR STEERING" messages outrank the current plan - ops.
- Exit the loop on any of three conditions: everything passes, a cycle changes nothing, or the budget is spent - loop.
- Watch progress cheaply, including the evidence-read count, which proxies whether verification is really happening - ops.
- Plan to "remove harness pieces after each Claude upgrade" - ops.

Skip: the copy and chmod setup steps.

## Synthesis

1. Default-FAIL is the most repeated mechanism, appearing in three sources, and it means nothing is done because an agent said so.
2. The builder must never grade itself, which two sources state and one implements with a tools-restricted subagent.
3. The judge must be context-blind, because a critic sharing the builder's history inherits its rationalisations.
4. Evidence must be enforced mechanically, since prompt instructions alone failed in the first source and a hook fixed it in the last.
5. Verification means running the thing, because the central failure was code that changed while the feature stayed broken.
6. One unit of work per session, stated as one feature at a time and as queue the interruption and finish first.
7. Stages hand off through committed files, which four sources use and one formalises as a named artifact chain.
8. Plans should fix deliverables, sequence, risks, and proof, and leave implementation to the executor, because premature detail cascades.
9. Delegated tasks need an objective, an output format, tool guidance, and boundaries, which makes ticket text the highest-leverage artifact.
10. Effort budgets belong in the prompt, per task class, and budget exhaustion belongs among the loop exit conditions.
11. Reset context when you want a clean slate, keep the durable record outside the window, and avoid irreversible discarding.
12. Every harness component is a dated bet on a model weakness, so ablate one component at a time on a schedule.
13. Evaluations decay on the model-release cadence and must be versioned, gated, and grown one incident at a time.
14. Prompt changes are production changes, and one twenty-five-word instruction cost three percent of coding quality.
15. Failures must be resumable and legible, whether through session logs and wake calls or through commits and a progress file.

Contradictions

1. One source says multi-agent suits neither shared context nor heavy dependencies and names coding as such a domain, while three others build multi-agent coding harnesses; they parallelise roles over one repository rather than splitting one feature across workers.
2. The measured cost of a terseness instruction sits against the premise of a leanness judge, so cut artifacts after acceptance rather than instructing the builder to be brief mid-task.
3. One source deleted its sprint construct on a newer model and got cheaper and faster, while another keeps a full six-stage chain, because the second optimises for governance and multi-human handoff rather than raw capability.
4. One source says add complexity only when it demonstrably improves outcomes, while another says the useful harness space moves rather than shrinks, and both are satisfied by scheduled ablation instead of assuming a direction.

## Risks

Every page was read through a summarising fetch, so quotations are reliable in substance but not guaranteed character-exact.
Three raw files from the GitHub repository returned summaries rather than verbatim text.
The evaluator subagent definition returned a review verdict instead of its contents, so its tool list and prompt wording here are second-hand.
The 2026 publication dates were not cross-checked against a second source.
The repository layout comes from its README rather than a directory listing.
