# Loop engineering: eleven sources read

Fetched all 11 URLs with WebFetch.
Nine returned content, four failed.
The three most substantive articles (1, 2, 3) I downloaded as raw HTML, stripped to text, and grepped myself, so their quotes are verified verbatim.
Sources 4, 5, and 6 carry quotes as returned by the fetch summarizer and were not verified against raw HTML.

---

## 1. loiane.com - AI Loop Engineering with GitHub PRs and Claude Code

`https://loiane.com/2026/08/ai-loop-engineering-github-pr-claude-code/`
Status: fetched, verified against raw HTML (6,316 words).

### a. Loop shape

One universal shape, stated as: observe state, compare to goal, act to close the gap, check the budget, wait for the cadence, repeat.
Verbatim: "observe the PR, and if every gate is green, stop because it is merge-ready. Otherwise fix the code and push. If we still have iterations left in the budget, wait for the next CI run and observe again."

Six required parts per loop: goal, sensors, action, cadence, bounded budget, guardrails.

Four named shapes: converge-to-green, queue, metric-climb, statistical (flaky-test).

Four loops compose into an issue-to-merged pipeline:

1. Spec-sharpening loop. Run `/spec` on the issue, run `/spec-review`, if PRODUCT DECISION questions remain stop and post them to the human as a numbered list. Human-paced.
2. Build loop. `/plan` decomposes into TDD tasks T-001, T-002. Each runs `/build T-00X`, moving pending to red to green to refactor to done, committing when gates pass. Self-paced.
3. Ship loop. Runs the pr-quality-gate skill on an open PR every ten minutes until green or budget exhausted.
4. Review-response loop. Polls human review activity, resolves actionable comments, never merges.

### b. What verifies, who writes it, when

Deterministic sensors the author wrote in advance, not a model judging.
Verbatim: "Something a script could answer yes or no to: all checks green, coverage at or above 90%, zero new static-analysis issues."

Sensors named: `gh pr checks $1` for gate status, `gh pr view $1 --json statusCheckRollup,mergeable` for the rollup, `gh pr view $1 --json reviews,comments,reviewThreads` for unresolved threads, plus `/validate` and `/review` locally.

Human judgment lands at exactly two points, at the front (answering product questions) and in the middle (deciding a branch is worth a PR).
"A human owns the merge."
Guardrail: "NEVER merge, and NEVER open the PR - that is the human's call."

### c. Keep it simple / against over-checking (verbatim)

- "The two human gates are the smallest they can responsibly be."
- "The answer is that the build loop does not remove human review. It relocates it. The default SDD flow puts a human checkpoint after every task."
- "That is the point where relocating human review from 'after every task' to 'after a handful of tasks' stops being a risk and starts being the natural next step."
- "Match cadence to your sensors and you never pay for a check that cannot tell you anything new."
- "There is no point checking every thirty seconds when the signal you are waiting for only changes once per CI run."
- "Leave should-fix and nit findings in a summary for the human; do not gold-plate."
- "That is the whole point of loop engineering: push the convergence into loops, and spend your attention on the judgment calls no loop should make."

The countervailing caveat, stated in the same section, is important and should not be dropped:

- "But that trust has to be earned first: build your own set of skills before you reach for this loop. Do not skip that step, or you will spend far more time correcting the agent's output than you would have spent reviewing each task yourself."
- "That trade is only safe once the sensors are trustworthy enough to stand in for you on the small stuff. Earning that trust is the prerequisite, and it is not automatic. You graduate into this loop; you do not start here."
- "I want to be honest about something, because it directly contradicts advice I have given before. In my SDD posts I am emphatic that you review every task and give the agent feedback per task."

### d. Separate verifier, fresh context, frozen checks, deterministic gates (verbatim)

- "Your coverage threshold, lint rules, and /review checklist have to fail loudly on the mistakes you care about."
- "Forbid metric-gaming explicitly."
- "Never disable a failing test to make it pass."
- "Guardrails: branch only, never merge, never weaken a test or edit the spec to make /review pass, escalate on low confidence."
- "Your success criteria has to demand meaningful assertions, and your converge-to-green gate (Shape 1) is what keeps the new tests honest, because empty tests still have to pass review and not break the build."
- "A loop without a budget is not autonomous, it is a runaway process."
- "Bound everything. Every loop needs a maximum iteration count, and ideally a wall-clock deadline too."
- "The most valuable thing a loop can do when it is stuck is stop and say so."
- "If the budget is exhausted, stop and escalate to a human instead of looping forever."
- "Spelling out the difference, and forcing an escalation on disagreement, is what keeps the loop from arguing with your reviewer on your behalf."
- "Trusting AI 100% is a disaster waiting to happen: the moment something breaks in production, you need to know exactly what changed and why, not discover that nobody, human or agent, actually understands the code that shipped."
- "When a loop does something wrong on iteration 7, you want to revert one commit, not untangle a squashed mess."

Note: the author does not argue for a separate model as verifier.
The verifier here is scripts and CI, plus one human gate.

### e. Failure modes

- Oscillation. "The classic failure mode is oscillation: the fix for the failing integration test introduces a Checkstyle violation, and the fix for that breaks a unit test."
- Metric gaming. "an agent told to 'increase coverage' will happily write tests that execute code without asserting anything, because that moves the metric."
- Stuck. "The failure mode is getting stuck: one dependency has a breaking change the agent cannot resolve, and a naive loop will hammer it forever."
- False green on flaky tests. "A loop that runs the test once after the fix and sees green will report success on a test that still fails one time in fifty."
- Wrong direction from a vague spec. "a vague spec does not produce vague code, it produces confident, wrong code, faster." And: "A clean spec built on guessed intent is the most expensive failure."
- Overreacting to review comments. "A loop that treats every comment as 'change requested' will dutifully rewrite code in response to a reviewer who was only asking a question, and a loop that treats every comment as a question will ignore real change requests."
- Root-cause diagnosis of loop failure: "Most failed agent loops I have seen fail on the last two." (budget and guardrails) And: "They have a clear goal and good sensors, and then they run away because nobody defined the budget or the guardrails."

### f. Numbers

| Item | Value |
|---|---|
| Ship loop iteration cap | 10, then summarize and stop |
| Ship loop cadence | every 10 minutes |
| Review-fix rounds before escalation | 5 |
| Per-task gate failures before escalation | 2 in a row |
| Coverage success criterion | 90% or above |
| Flaky-test definition | fails 3 of 20 runs |

No cost figures, no success rates, no wall-clock timings.

---

## 2. developersdigest.tech - Loop Engineering: The Definitive Guide

`https://www.developersdigest.tech/blog/loop-engineering-definitive-guide`
Status: fetched, verified against raw HTML (4,632 words). Page states "Last updated: July 29, 2026."

### a. Loop shape

A catalog of about ten shapes rather than one canonical loop.

- Build-test-fix pair. Builder writes code, checker runs tests plus typecheck plus lint, failures come back as the next instruction, fix, stop when green.
- Verifier loop. Work the task list; after each task a separate verifier checks the result against spec and tests; only move on when it passes; "Surface anything the verifier rejects twice."
- Plan-generate-verify-fix. Plan, implement, verify against tests, fix, save state to files each pass, max 5 iterations.
- Quality streak. Run the full suite, fix failures, run again; a new failure resets the count; done "after 10 consecutive clean passes."
- Five-minute repository maintainer. Every 5 minutes make one small improvement, one change one commit, tests must be green.
- Production error sweep. Review the last 24h of production errors, separate actionable from noise, fix each with a regression test, open a PR.
- Overnight PR routine. Watch open PRs, auto-fix build failures, answer review comments in a fresh worktree, rebase stale items, leave ambiguous items for a human.
- Production inbox. Pull emails every 15 minutes, classify, draft routine replies, queue sensitive items for a human, log every decision.
- Human-in-the-loop approval queue. Run the task, pause, send approve/revise/skip.
- Adversarial review. Implement, have a second different model review the diff against the spec, iterate up to 5 rounds, ship only what both models agree is correct.

### b. What verifies, who writes it, when

Always a second entity, never the worker, checked after every turn.

- "It is anything that checks a result against an expected outcome: a compiler, a test runner, a linter, a diff check, a second model as judge, or a human approval gate."
- "After every turn, Claude Code sends the condition plus the transcript to a separate, small, fast model (Haiku by default) that acts as a judge."
- "That judge returns yes or no with a reason."

### c. Keep it simple / against over-checking (verbatim)

Only two sentences in the entire guide, and both are scoping rules rather than warnings about scaffolding:

- "You do not need every pattern above."
- "You do not need it for one-off, judgment-heavy work where you want to stay in the loop yourself."

Adjacent staging advice:

- "Then graduate the watched loops to /goal conditions once you trust the verifier, and move the durable ones to /schedule once you trust the budget."

Nothing in this guide warns against over-checking. It argues the opposite throughout.

### d. Separate verifier, fresh context, frozen checks, deterministic gates (verbatim)

- "This is the single most important idea in the whole field, so it is worth saying plainly: the worker does not grade its own homework."
- "A separate model does."
- "This is the single most important sentence in loop engineering: writing the loop is easy, the verifier inside it is the hard part."
- "An agent grading its own work will delete a failing test and call the task done, because it has no independent signal that its output is actually correct."
- "This is exactly why /goal runs a separate small model as judge instead of letting the worker grade its own work, and why every strong loop in this guide (the verifier loop, the build-test-fix pair, the adversarial review) puts a second, independent set of eyes inside the loop."
- "This is why /goal in Claude Code runs a separate small model as judge rather than trusting the worker's own assessment."
- "The useful rule of thumb is that the verifier should be cheaper and more reliable than the action it checks."
- "A verifier closes the loop."
- "The verifier is the part everyone skips, and without it you are just trusting the agent."
- "The strongest reliability pattern: have one model family review another model family's pull requests before merge, so two independent sets of weights have to agree before code lands."
- "Give each one a budget and a verifier."
- "The loop he describes runs the coding agent plus an advanced model plus a verifier, feeds it tasks, and removes bottlenecks as you go." (attributed to Boris Cherny)

### e. Failure modes

- "An open loop, a loop with no verifier, fails in predictable, expensive ways: compounding errors, hallucinated progress, silent failures, goal drift, and the doom loop where the agent retries the same broken approach with cosmetic variations."
- "A loop that cannot tell good output from bad does not save you work. It produces wrong answers faster."
- Cost runaway: "The community's most-repeated cautionary examples involve a loop with no cap running until tokens ran out." And: "a loop with no ceiling will happily spend until your tokens run out."
- Honesty note on its own evidence: "The figures vary and many are hard to verify independently, but the direction is consistent and the mechanism is obvious."
- Forgotten loops. `/loop` entries auto-expire after seven days in Claude Code.

### f. Numbers

| Item | Value |
|---|---|
| Iteration and round caps cited | 5 iterations, 5 rounds, 20 turns |
| Quality streak victory condition | 10 consecutive clean passes |
| `/goal` condition field cap | 4,000 characters |
| `/loop` minimum interval | 1 minute |
| `/schedule` minimum interval | 1 hour |
| Inbox loop interval | 15 minutes |
| Maintainer loop interval | 5 minutes |
| Forgotten-loop expiry | 7 days |
| Cited cost incident | a $400 overnight bill |
| Cited autonomous run | Claude Opus 4.5, 4 hours 49 minutes, stop hooks plus Ralph loop |
| Shipped in | Claude Code v2.1.139 (`/goal`); Codex CLI v0.128.0 |

---

## 3. michael.roth.rocks - Gate Analysis

`https://michael.roth.rocks/research/gate-analysis/`
Status: fetched, verified against raw HTML (4,250 words). This is the only source with real field data.

### a. Loop shape

- "An orchestrator decomposes the work into bounded tasks, each handled by a fresh agent with a scoped context."
- Four mandatory gates in order: plan, design, code, codereview.
- Rejection sends the task into a revision cycle; repeated failure escalates.
- "The system also decomposes work into bounded tasks, externalizes state into task queues and process docs, and enforces contracts at each gate."

### b. What verifies, who writes it, when

A different model family validates.
"Claude generates work, Gemini validates it through four mandatory review gates."
Gating happens before implementation (plan), after design, during implementation (code), and after all work is complete (codereview), not only at the end.
"Four mandatory review gates: catch errors between tasks, before they compound."

### c. Keep it simple / against over-checking (verbatim)

One trimming sentence in the whole paper:

- "If you only have budget for one review gate, make it plan review."

Supported by: "The plan gate catches the most errors." and "The 61% rejection rate at the plan stage is a positive finding, because this is the least expensive place to catch bugs."

Nothing else argues for less scaffolding. The paper argues for more.

### d. Separate verifier, fresh context, frozen checks, deterministic gates (verbatim)

- "Cross-model review solves that: review the output with a different model, no re-execution needed."
- "Cross-model review is practical ensembling for agents."
- "My data shows cross-model review achieves the same variance reduction without re-executing the task."
- "Each worker starts with a clean context, no accumulated confusion."
- "Consider different agents for revision. A fresh agent may be more effective than having the same agent retry."
- "Decomposition flattens the length-incoherence slope - the same mechanism this system's gates exploit."
- "The gated workflow doesn't just reduce errors, it specifically suppresses the incoherent ones."
- "Gates catch cross-context issues that humans don't surface, likely a harder class of errors."
- "Invest in orchestration, bounded contexts, and review gates."
- "Every one of these 5,109 gate checks is an entry in a trust ledger: empirical evidence about what works, what fails, and where."
- "The paper notes ensembling is impractical for irreversible agentic tasks - real-world action loops can't reset their state."

### e. Failure modes

- The revision handoff is the weak point. "The system decomposes initial work well, but the revision interface, where review feedback must cross into the agent's next attempt, is the weakest link in the pipeline."
- "The revision cycle is the real safety frontier."
- "They fail to incorporate specific feedback and the handoff from review output to revision input loses information."
- "They sometimes fix one issue while introducing another leading to state corruption across the feedback boundary."
- "They lose context about what the reviewer actually wanted."
- Revision rarely works. "Getting it right the first time is far more efficient than revision (only 31% of revisions recover)."
- Escalations were mostly noise. "Most of the 201 ESCALATE decisions were also infrastructure failures rather than genuine quality escalations."

### f. Numbers

| Measure | Value |
|---|---|
| Gate checks analyzed | 5,109 over 97 days |
| Genuine rejections | 1,450 |
| Claude Code session files parsed | 3,119 |
| First-pass approval, all gates | 55% |
| Plan-gate rejection rate | 61% (39% first-pass approval) |
| Recovery after rejection | 31.5% |
| Fail again after rejection | 54.8% |
| Systematic (wrong-approach) errors | 50.8% |
| Omission errors | 40.5% |
| Incoherent errors | 8.7% |
| Release-arc incoherence vs feature arcs | 10% vs 19.8% |
| Concurrent projects | 8 |
| Autonomous hours | 543 |
| Shipped releases | 165 |
| ESCALATE decisions | 201 |
| Independent-validation sessions | 664 public |
| Dual-voted classification precision | 0.965 |

Author's own caveat: the per-gate, per-arc, recovery, and cross-validation breakdowns come from an earlier single-pass Gemini Flash Lite classification over all 1,450 rejections, "directionally consistent, but not re-voted."
Raw session data is not public, but the extraction tool is generic and reproducible on your own logs.

---

## 4. menuagentic.com - AI-Native SDLC Artifact Chain

`https://menuagentic.com/blogs/ai-native-sdlc-artifact-chain/`
Status: fetched. Quotes as returned by the fetch summarizer, not verified against raw HTML.

### a. Loop shape

Six stages, each committing one artifact:
`intent.md` to `spec.md` to `plan.md` to code diff to review findings to incident record, then back to `intent.md`.
Stage names: Plan, Design, Build, Test, Deploy, Maintain.
"The Maintain stage writes its findings as a new `intent.md`, which is what closes the loop."

### b. What verifies, who writes it, when

Different guard on each hop, and three hops with no guard at all.

| Hop | Guard | Author | When |
|---|---|---|---|
| sources to intent.md | product owner reads and commits | human | Stage 1 |
| intent.md to spec.md | skills during authoring, owner reads | human plus model | Stage 2 |
| spec.md to plan.md | plan mode withholds edits until approval | human approves | Stage 3 |
| plan.md to diff | CLAUDE.md conventions, hooks, self-tests | model plus automation | Stage 3 |
| diff to policy | layered agentic review, hooks as gates | model plus human on critical paths | Stage 5 |
| diff back to spec.md | nothing named | none | none |
| config to behaviour | continuous evals gate on pass rate | automation | Stage 4 |
| production to intent.md | control-band script, reviewed at intake | script plus human if attended | Stage 6 to 1 |

### c. Keep it simple / against over-checking (verbatim)

One sentence, and it is a scoping rule for hooks rather than a warning about scaffolding:

- "Everything else can be a review finding."

Paired with: "Reserve hooks for what must never be probabilistic: Credentials in a diff, writes to protected paths, production deploys, anything irreversible."

### d. Separate verifier, fresh context, frozen checks, deterministic gates (verbatim)

- "Hooks are the only genuinely deterministic control in the entire playbook."
- "A hook can deny a call; staying silent does not approve one, and exit code 2 is the one outcome that later JSON cannot override."
- "Hooks tighten policy and can never loosen it."
- "Put the upstream artifact's commit SHA in the downstream artifact's front matter... now the chain is a real graph rather than a sequence."
- "A `PreToolUse` hook can refuse a commit whose front matter points at a SHA that is no longer the head."
- "Give the intent to spec hop a judge, not a reader... Run it as a gate on the Design stage."

### e. Failure modes

Three unchecked hops, each with a named failure:

1. intent to spec. "A requirement the intent never implied, or an open question the spec quietly resolved in the convenient direction, is invisible to everything downstream."
2. diff back to spec. "An agent that built the wrong thing, correctly." Agentic review "catches bugs, vulnerabilities, and convention breaches" but not spec fidelity.
3. production to intent. "An unattended intake turns a closed feedback loop into an open-ended generator of work."

System-level signature, citing DORA 2025: "Throughput up, stability down... the signature of a pipeline whose build stage got faster while its verification stages did not."

### f. Numbers

- "Ninety percent of respondents now use AI at work - up fourteen points year over year."
- "spending a median of two hours a day with it."
- "Twenty-four percent of DORA respondents report high trust in AI output; thirty percent trust it a little or not at all."
- GitHub Spec Kit "passed 130,000 stars, reached v1.0.1 on 2026-08-21."

No cost figures, success rates, or round-trip timings.

---

## 5. waydev.co - Anthropic's AI-Native SDLC Playbook Has a Missing Layer: Measurement

`https://waydev.co/anthropics-ai-native-sdlc-playbook-has-a-missing-layer-measurement/`
Status: fetched. Quotes as returned by the fetch summarizer, not verified against raw HTML.
This is vendor marketing for a measurement product.

### a. Loop shape

The same six stages, with a measurement gate added at each boundary.

1. Plan. "Time from first conversation to a committed intent.md."
2. Design. Measured between "intent.md commit and the spec.md commit."
3. Build. Agent writes code, producing a diff.
4. Test. CI validation and PR review.
5. Deploy. Approval gates and production release.
6. Maintain. "A deterministic monitor watches production, a control band gets breached, Claude diagnoses the issue, and the finding re-enters the pipeline as a new intent.md."

Then "The loop feeds itself."

### b. What verifies, who writes it, when

Git history is the audit trail.
"every stage commits an artifact to git: intent.md, spec.md, plan.md, the diff, the PR findings, the incident record. The chain of commits becomes the audit trail."
Human role changes level: "Human attention moves up a level, from reading every line to judging intent and risk at the gates."
Timing: at each stage transition.

### c. Keep it simple / against over-checking

None. The article argues the opposite, that a measurement layer is missing and must be added.

### d. Separate verifier, fresh context, frozen checks, deterministic gates (verbatim)

- "A deterministic monitor watches production, a control band gets breached, Claude diagnoses the issue."
- "A rolling 30-day baseline with Western Electric rules, which is exactly what the playbook recommends."
- "control band breach to an intent.md in the triage queue."
- "The playbook says human attention shifts to judging intent and risk."

### e. Failure modes

One, and it is the sharpest statement of the risk in any of these sources:

- "Review time per PR drops, approval rates climb, and everyone calls it efficiency. Three months later the change failure rate catches up. Unmeasured autonomy at five times the output is not speed, it's faster entropy."
- "When build stops being the constraint, the human-speed stages around it become the whole cycle time. Measuring only commits and deploys tells you nothing about the part that now dominates."

### f. Numbers

- Build phase collapses "from weeks to hours."
- "Productivity have gone up 30%" (Sovos case study, vendor-sourced).
- "Five times the output" in the failure scenario.
- 30-day rolling baseline.
- "Three months later" as the failure-detection lag.
- "Six stages. Six data sources."

No independent empirical loop-performance data.

---

## 6. port.io - Anthropic's AI-Native SDLC Playbook

`https://www.port.io/blog/anthropic-ai-native-sdlc-playbook`
Status: fetched. Quotes as returned by the fetch summarizer, not verified against raw HTML.

### a. Loop shape

Six stages, described as mostly linear with one closing edge.

1. Plan. intent.md created from signals.
2. Design. intent to spec.md, with policy review.
3. Build. spec to plan.md to code, governed by skills and hooks.
4. Test. Run the eval set.
5. Deploy. PR reviewed against written policy, human approval.
6. Maintain. Detection, diagnosis, new intent.

"Something detects a problem, an agent diagnoses it and writes up what it found as a new intent, and that re-enters the normal process."

### b. What verifies, who writes it, when

A frozen eval suite plus a human who did not write the code.

- "Build twenty to fifty test cases from real past work. Re-run them whenever the context file, a skill, or a hook changes."
- "Every incident adds one, permanently."
- "A human approves, and the agent that wrote the code cannot."
- "Every pull request is reviewed against a written policy."
- The platform "Comments on the PR before a human opens it" with service criticality, blast radius, and incident history.

### c. Keep it simple / against over-checking

None. The article prescribes adding governance, not reducing it.

### d. Separate verifier, fresh context, frozen checks, deterministic gates (verbatim)

- "it decides whether it's safe to hand off using rules the platform team writes down, not the model's judgment that day. For example: not a top-tier service, blast radius is calculated and not high, no open incidents, priority not critical. All must pass. One failure escalates to a human."
- "A human approves, and the agent that wrote the code cannot."
- "Re-run them whenever the context file, a skill, or a hook changes."
- "It also governs the agent layer with a registry of approved skills and approved MCP servers instead of people installing whatever they want."
- "If an engineer edits the skill holding the security policy, it goes to the CISO and holds the new version until they approve."
- "If something looks risky, the product owner sends it to 'the named policy owner.'"

### e. Failure modes

None reported. The article is prescriptive, not empirical.

### f. Numbers

Only one: "Build twenty to fifty test cases from real past work."
No cost, rounds, success rates, or timings.

---

## 7. Hacker News item 49525809 - reachable but off-topic

`https://news.ycombinator.com/item?id=49525809`
Status: fetched successfully. It is not a loop-engineering thread.

Confirmed via the HN Firebase API.
Item 49525809 is a comment by `felixrieseberg` inside submission 49525378, titled "Claude Fable 5.1 and Claude Mythos 5.1", submitted by `denysvitali`, with 1,393 descendants.

The comment body in full: "(I work at Anthropic) Beyond all the benchmarks, I think Fable 5.1 is a big improvement in writing style. It sounds a lot less stereotypically like other Claude models, has (imho) a much more natural style, and responds to my style instructions more reliably. More work to be done (and we will!) but reading better prose makes me so much happier. Another point I expect not to get much attention until it all happens at once is science. People have been correctly excited about the many 'sudden' breakthroughs LLMs are making in Maths, but some of the science benchmarks make me believe we'll soon see similar developments in other scientific domains. Fable 5.1 more than doubled Fable 5's Terminal-Bench-Science score, which I think is meaningful."

Sections a, b, c, d, and f: nothing in the reachable thread content addresses them.

The one loop-adjacent reply the fetch surfaced, from `jaapz`: "My trick is to pass opus and fable's word salad into a haiku agent, then have it check if what haiku makes of it is still correct."

Failure modes discussed in the subthread are about prose verbosity, not loops. Example from `mywittyname`: "It will also inject a tons of information that it shouldn't...subsequent passes will flag those comments and get stuck on the fact that numbers don't match."

If a loop-engineering HN thread was intended, this item ID is wrong.

---

## UNREACHABLE

1. `https://www.reddit.com/r/ClaudeCode/comments/1w71zqx/has_anyone_actually_tried_anthropics_ainative/`
   WebFetch, both attempts: "Claude Code is unable to fetch from www.reddit.com".
   Direct curl to the `.json` endpoint returned Reddit's block page: "whoa there, pardner! Your request has been blocked due to a network policy."

2. `https://www.reddit.com/r/ClaudeCode/comments/1w97lh4/how_are_you_building_so_fast/`
   Same WebFetch error. Retried against `old.reddit.com`: "Claude Code is unable to fetch from old.reddit.com".
   Direct curl to the `.json` endpoint returned the same Reddit block page.

3. `https://x.com/RLanceMartin/status/2095170001175199771`
   WebFetch, both attempts: "The server returned HTTP 402 Payment Required. The response body was not retrieved."
   The xcancel.com mirror failed with "read ECONNRESET".

4. `https://x.com/simas_ch/status/2092873750983201277`
   WebFetch: "The server returned HTTP 402 Payment Required. The response body was not retrieved."

Reddit and X are blocked at the network layer here, not transiently.
A browser session or a different egress path is the only route I can see to those four.

---

## Cross-source read

The two sources with actual field data disagree with the two vendor posts about where effort should go.

Roth's 5,109 gate checks say the plan gate carries the load and the revision handoff is the failure frontier, with only 31.5% of rejected work recovering.
His one trimming recommendation, "If you only have budget for one review gate, make it plan review," is the single most evidence-backed piece of advice across all eleven sources.

Loiane, who actually ran the loops, is the only author who argues for fewer human checkpoints, and does so conditionally.
Relocate review, do not remove it.
Earn the right by building skills through months of manual review first.
"You graduate into this loop; you do not start here."

The developersdigest guide is the strongest statement of the separate-verifier principle and contains almost nothing about restraint.
Its two restraint sentences are about not applying every pattern, not about lighter gates.

Every source arguing hardest for more gates is either prescriptive with no data (port.io, menuagentic) or selling a measurement product (waydev).

On failure modes, the sources converge on five: metric gaming when the target is a number, oscillation when gates conflict, getting stuck and hammering forever without a budget, false green from a single run of a flaky check, and building the wrong thing correctly when nothing checks the diff back against the spec.
Only one source names a cost incident with a figure, the $400 overnight bill, and it flags that figure as hard to verify.

---

## Risks

- Quotes for sources 4, 5, and 6 come from the fetch summarizer, not raw HTML I parsed myself. Sources 1, 2, and 3 I verified against downloaded HTML with my own greps. If exact wording from waydev, port.io, or menuagentic is load-bearing, those three need a raw re-fetch.
- The "none found" answers for section (c) on sources 5 and 6 rest on the summarizer's negative claim. I verified negatives only for sources 1, 2, and 3, where a full-text grep found the small result set in each case.
- Four of eleven URLs returned no content, so the practitioner-sentiment half of the brief (two Reddit threads, two X posts) is entirely missing. Nothing in this report speaks for what practitioners are saying informally.
- The HN item ID appears to be wrong for the intended topic. I did not go looking for the thread that was probably meant.
- Source 3 is a single practitioner's logs from one system, self-classified with a model. It is the best evidence here and still n=1 on setups.
