# Community research: agentic software factory

Practitioner evidence from three Reddit threads, five videos, and eight written sources, gathered 2026-09-07 for the request-to-brief-to-plan-to-tickets-to-loop-to-verification-to-judges design.

## Retrieval status

Reddit was reachable only through the user's Chrome browser on old.reddit.com.
WebFetch refuses both reddit.com and old.reddit.com.
Direct curl gets HTTP 403 with a "blocked by network security" body on the JSON API, and a JavaScript-only shell on the HTML page.
Mirrors including redlib, safereddit, and r.jina.ai time out at the egress proxy.
WebSearch returns "domains not accessible to our user agent" for reddit.com.
The modern reddit.com page also defeats text extraction, so old.reddit.com is the only working path even inside the browser.
All three threads were then captured in full.

YouTube transcripts are unavailable for every video.
Caption tracks are listed in the page data, but the timedtext endpoint returns HTTP 200 with a zero-byte body.
Inside Chrome the transcript panel opened but rendered empty in both the accessibility tree and the page text.
Video 6 has no caption tracks at all, so its gap is not a fetching problem.
No transcript content was invented.
Video claims come from creator-written descriptions, verified twice: once by scraping the watch page, once by expanding the description in Chrome.

## Reddit threads

### Has anyone actually tried Anthropic's AI-Native SDLC playbook in a real project?

r/ClaudeCode, by Interesting-Yard-684, posted 2026-09-04, 40 points, 26 comments.
https://www.reddit.com/r/ClaudeCode/comments/1w71zqx/

The OP argues the playbook is a synthesis rather than an invention, naming a 2024 AI-native SDLC paper, GitHub Spec Kit, a Microsoft AI-led SDLC, OpenAI's AGENTS.md workflows, and older practice such as TDD, GitOps, and policy-as-code.
His central worry is the sharpest line in the thread: an agent can check a change against a specification, but the specification, implementation, tests, and review may all share the same wrong assumption.
Adding more agent passes does not automatically produce independent verification.

Itchy_Champion_86 (10 points) is the only first-hand full attempt.
He had Opus turn the playbook into a markdown written for an agent, then started in plan mode with that plus a requirements doc.
His honest admission is that the result covers maybe 45 percent of the playbook.

Excellent_Chest_5896 (2 points) adds a backlog that becomes an implementation ledger, versioned docs so you know which version was built, and docs placed in the directories where the implementation lives and linked from CLAUDE.md or AGENTS.md.

mrothro (3 points) gives the strongest evidence, from a metered pipeline across a large brownfield monorepo.
His key is that each stage's output must be an artifact you can check deterministically, with structure increasing as you move from natural language toward formal language.
He pairs deterministic checks with LLM reviewers on a different model, citing arxiv 2604.06996 for the finding that judges wrongly pass their own work even on objective rubrics.
He has metered gate catch rates but never tracked escape rate.
Measurements: https://michael.roth.rocks/research/gate-analysis/

andrerom (3 points) runs a size classifier the agent applies first.
Track A covers three files or fewer with no API or migration change: plan in chat, failing test first, implement, verify gate, and the commit body is the spec.
Track B covers features: interview skill, numbered acceptance criteria, HTML prototype approved before code if UI, test-first per criterion, then the spec frozen into an implemented folder.

Counterpoints.
This-Establishment26 (6 points) says even specify-plan-implement did not work well, with too many ceremonies for small incremental features.
alonsonetwork calls the artifact set a mess but says the independent reviewer is an absolute must-have.
rajeevku02 deliberately runs small changes through the heavy path anyway, to keep the knowledge base current.

Tools named: GitHub Spec Kit, AGENTS.md, beadhive.ai, agentic-sdlc-showcase, coreforged.com/resources, grill-me.

### Anthropic published an AI-native SDLC playbook

r/ClaudeAI, by Forward_Mind6886, posted 2026-08-27, 104 points, 53 comments.
https://www.reddit.com/r/ClaudeAI/comments/1vzl6kk/

The OP cites Faros AI telemetry across 10,000 developers and 1,255 teams: 98 percent more PRs merged, review time up 91 percent, PR size up 154 percent.
None of these figures were independently verified.

Khavel_dev (7 points) gives the most directly useful answer in all three threads.
He runs a subagent with a fresh context and the test suite against every PR, plus a protected-paths hook blocking auth, billing, and migrations unless a human approves.
The combination catches more than he did reading line by line.
What still slips through is architectural drift, where an agent adds a fourth way to do something when three exist and each works in isolation.
His partial fix is a PATTERNS.md the agent is pointed at.

Wonderful-Match-6256 (1 point) gives the best verification insight found anywhere, from a small production Django app.
He replaced line-by-line review with roughly 2,100 guard tests asserting against the rendered page rather than the code.
His rule is that a test which reads its expected value from the module it tests, tests nothing, so the expectation must be an independent artifact.
His bot filter classified his own test client as a bot, so a whole measurement feature was green in CI while doing nothing in production.
He now treats a green run that never had a chance to fail as a red run, and counter-proves each guard by breaking the feature and watching the test go red.

fuckme (1 point, building https://assay.guide/) contributes the closest external analogue to a software factory.
Risk is an explicit dimension, where riskier means a stronger model and less automation.
Work decomposes into t-shirt-sized stories, hundreds open at once, each carrying its own dependencies and verification.

Counterpoints.
zeefer (26 points) asks how quickly a non-enforced artifact becomes a file nobody reads, and Double_Ebb4130 proposes keeping the hook with a one-line human accept.
gileze33 (4 points) notes human review is embedded in ISO, PCI, and GDPR change-management requirements.

Tools named: assay.guide, KitTools, lattice-app-works, Spec Kit, AGENTS.md.
Credibility: high signal in the minority of comments that answer the question, with named failure modes attached.

### How are you building so fast?

r/ClaudeCode, by Equal_Animator7440, posted 2026-09-06, 31 points, 47 comments.
https://www.reddit.com/r/ClaudeCode/comments/1w97lh4/

A Pro-plan user on day six with 51 percent of usage left asks why others burn credits in hours, and the consensus is that his premise is wrong.

kemalios (2 points) states it most directly.
The OP said he does not know what he wants until he sees output, which is a spec problem no multi-agent setup fixes.
Speed comes from the spec, not from running agents in parallel.

Main-Transition-6 (17 points) says to build a detailed implementation plan with verification loops explaining how each task can be verified, then run a goal.

UnidentifiedBlobject (8 points) makes it concrete: unit tests, e2e tests, screenshot diffs, type checking, and linting.
His distinctive move is having agents extend the linting with custom rules, so a pattern the agent keeps producing despite documentation becomes a deterministic failure.

spinje_dev (1 point) talks only to a main orchestrator that never reads code, which writes specs and manages planwriters, task orchestrators, PR closers, and lane implementers.
He claims one hour of conversation yields three implemented features and five fixed issues eight hours later.

T3hJ3hu (1 point) gives the honest downside of scale.
The work you create generates more work, and a PR queue problem can send every agent to burn tokens on the same problem simultaneously.

Counterpoints.
supernovice007 (15 points, best received) warns that running multi-agent does not mean producing production quality, and it is easy to write a prompt that spawns agents and does nothing.

Tools named: fork-sandbox, clodex, KitTools, lattice-app-works, Graphify, worktrees, Whisper.
Credibility: mostly opinion, but the spec-over-parallelism consensus is broad and the skeptics are the best-received voices.

## Videos

All video claims are outline-derived from creator-written descriptions, not transcripts.

### Every Level Of Claude Code Loop Engineering Explained

AI LABS, 2026-08-18, 21,456 views.
https://www.youtube.com/watch?v=PLyRe6Zk--8

Outline-derived: loop engineering means handing the checking step to the agent and keeping only the decision of whether it is done.
Outline-derived: never loop your MVP, and build the first version by hand.
Outline-derived: /loop runs on a timer and /goal runs until a condition is met, and the shared slash menu is called a naming trap.
Outline-derived: /goal verifies by having a smaller model read the turn and decide continue or stop.
Outline-derived: the rule that matters most is that the agent doing the work never verifies the work.
Outline-derived: a subagent builds on a branch, an adversarial review agent assumes there is a bug, and the main agent loops until the queue row is ticked.
Outline-derived: a feature-batch skill and a queue.md table run several features as one queue until nothing is left in todo or building.
Outline-derived: build a clickable prototype first, both to learn whether you wanted the thing and to give the loop something to verify against.
Outline-derived: a 38-minute unattended run left one error no screenshot could catch, a blinking mascot.

Tools named: Paseo, mattpocock/skills, GSAP skills, Vercel agent-skills, Supabase agent-skills.
Credibility: monetized channel funneling to a paid community, single project, no measurements, but negative results are stated.

### GitHub's number one trending author's new Claude skill

AI LABS, 2026-08-20, 81,555 views.
https://www.youtube.com/watch?v=c47uqR7XB_c

Outline-derived: agent laziness takes two forms, claiming done when it is not, and quietly shrinking the job while omitting it from the summary.
Outline-derived: three earlier fixes are dismissed, the Ralph loop's text marker, /goal judging the conversation instead of the work, and their own loops where the agent still graded itself.
Outline-derived: a depth number sets solo mode at 3 and under and orchestrated mode at 4 and up.
Outline-derived: a ticked box with "pending" still under it counts as worse than an empty box.
Outline-derived: their first run took three to four hours and produced only a login page, because tasks were handed out one at a time.
Outline-derived: editing the skill to use ten parallel agents produced a full working app in roughly two hours.
Outline-derived: the version demoed is a privately refined fork, not the public repo.

Primary, verified against https://github.com/Leonxlnx/unlazy:
Install with npx skills add Leonxlnx/unlazy, or clone into ~/.claude/skills/unlazy or ~/.codex/skills/unlazy.
The gate format is CHECK for a shell command, EXPECT for success marker text, optional CWD, and EVIDENCE.
A runnable gate passes only when the exit code is 0 and the EXPECT text matches combined stdout and stderr.
Evidence carries a versioned SHA-256 digest of the CHECK, EXPECT, and CWD definitions, plus the exit code and an output fingerprint.
An agent that edits a check after the fact therefore invalidates its own pass, and such evidence is treated as stale and unmet.
Leaf gates are atomic tasks with disjoint repository-relative OWNS paths, which is what makes parallel subagents safe.
The stated order is: write acceptance criteria first, execute reviewed checks, reverify returned work, report only supported evidence.

Credibility: promotional video, but the repo is inspectable and its mechanism is specific.
The digest-bound evidence is the most transferable idea in this research.

### Designing with Claude: From prompt to production

Claude, Anthropic's own channel, 2026-05-21, 126,268 views.
https://www.youtube.com/watch?v=Uvl-tRga98g

This source yielded nothing usable, with no caption tracks and a three-sentence description carrying no links or chapters.
Credibility: first-party vendor marketing with no independent evidence value.

### Build $10,000 Websites using Claude Code

Metics Media, 2026-05-29, 1,040,722 views.
https://www.youtube.com/watch?v=VMvZuhcDdnw

Outline-derived: an 8-pillar checklist serves as the quality rubric, re-evaluated after the polish pass rather than only at the start.
Outline-derived: avoiding generic output takes a strong brief plus explicit design references, not a better prompt.

Tools named: Frontend Design skill, UI/UX Pro Max skill, 21st.dev, Dribbble, Awwwards, Pinterest.
Credibility: affiliate-monetized beginner content about marketing sites, so only checklist-as-rubric and reference-driven briefs transfer.

### Insane Claude Design Skills

AI LABS, 2026-08-24, 165,896 views.
https://www.youtube.com/watch?v=Ysr7oNDajJI

Outline-derived: most design skills fail to move the model off its default look and only a few deliver, though the description does not say which lost.
Outline-derived: a distinct category of review skills scores a design and says what to fix.

Tools named: Emil Kowalski skills, garden-skills, ai-design-skills, Meng To Skills, Jakub Krehel skills, tastemaker, designer-skills.
Credibility: sponsored and SEO-stuffed, but a bake-off admitting failures beats a showcase.

Three of the five videos come from AI LABS, so the loop material approximates one opinion.
That channel contradicts itself two days apart on whether /goal's conversation-reading verification is adequate, and the later position is that it is not.

## Playbook and critiques

The AI-Native SDLC playbook, Louis Claxton, Anthropic, 2026-08-21.
https://claude.com/blog/the-ai-native-sdlc-playbook
Six stages each commit an artifact the next reads, from intent.md through to monitoring that loops back into a new intent.md.
Bug fixes require a pre-existing failing test that agents may not modify, which is the cleanest anti-slop rule in the document.
Hooks enforce deterministic controls at the action level and can block until a named person signs off.
Sessions verify their own work before engineer review, which is the exact practice every practitioner source calls insufficient alone.

Three unchecked links, Agentic AI Wiki, 2026-08-22.
https://menuagentic.com/blogs/ai-native-sdlc-artifact-chain/
intent.md to spec.md is checked only by a human reading two markdown files, and the fix proposed is an LLM judge with a fixed rubric verifying the spec answers every open question and adds no unstated requirements.
diff to spec.md is unchecked because agentic PR review compares the diff to policy, not to the spec, and the fix is a mechanical check surfacing plans that touch undocumented files or omit specified subsystems.
production to intent.md is the only hop where an artifact enters with no human author, and the fix is draft status, assigned ownership, expiry dates, and measuring acceptances rather than creations.

The missing measurement layer, Alex Circei, Waydev, 2026-08-24.
https://waydev.co/anthropics-ai-native-sdlc-playbook-has-a-missing-layer-measurement/
Metrics named: time to committed intent, intent acceptance rate, intent-to-spec elapsed time, requirements rework cycles, first-pass merge share, first-pass CI success, time to first review, and defects caught pre-merge versus post-production.

Requirements engineering, Simon Martinelli.
https://x.com/simas_ch/status/2092873750983201277
Requirements engineering is reduced to one prompt, with no use cases, no domain model, and no explicit non-functional requirements.
An agent that generates 5,000 lines from a bad spec produces 5,000 lines of wrong code.

Platform prerequisites, Yonatan Boguslavski, Port, 2026-08-28.
https://www.port.io/blog/anthropic-ai-native-sdlc-playbook
There is no mechanism turning raw signals into structured intent, so "fix login bug" cannot select a repo.
Governance drift is the subtlest failure, where skills and hooks silently diverge from real policy and the tell is that nothing is failing.

Four loops, Loiane Groner, 2026-08-09.
https://loiane.com/2026/08/ai-loop-engineering-github-pr-claude-code/
Every loop is framed with six parts: goal, sensors, action, cadence, budget, guardrails.
The ship loop runs on a ten-minute cadence with a ten-iteration budget and hard-stops at merge-ready, never merging, approving, or closing.
She states the build loop required months of manual tuning before auto-commit was safe.

Loop engineering guides.
https://www.developersdigest.tech/blog/loop-engineering-definitive-guide states the worker does not grade its own homework, a separate model does, and documents $400-plus overnight bills from uncapped loops.
https://claude.com/blog/getting-started-with-loops adds codebase entropy, where the loop faithfully follows whatever poor patterns already exist in the repo.

## Ten points of practitioner agreement

1. Separate the builder from the verifier structurally, and give the verifier a fresh context.
2. Use a different model as judge, not merely a different session, because models wrongly pass their own work even on objective rubrics.
3. A gate is a command plus an expected string plus tamper-evident evidence, never a checkbox.
4. The expected value must be an independent artifact, and a green run that never had a chance to fail should be treated as red.
5. More agent passes do not create independent verification, because spec, code, tests, and review can share one wrong assumption.
6. Loops need explicit budgets and, more importantly, explicit negative guardrails naming what the loop may never do.
7. Speed comes from the spec, not from parallelism, because the expensive part is deciding.
8. Size-classify the work first, because applying the full artifact chain to every change is what makes people abandon it.
9. Tickets should be a priority queue of sized units with disjoint ownership, with bugs and features on one path and risk as an explicit dimension.
10. What escapes is architectural drift, and it needs a non-test control such as a patterns file or agent-extended lint rules.

## Slop tells

These four constructions got a post roasted in r/ClaudeAI, with the top detection comment at 143 points.
The not-X-but-Y inversion, such as "the interesting part isn't the six stages, it's what replaces line-by-line review".
The "the part I keep coming back to is" opener.
A false-profundity historical analogy, in that case an unearned comparison to 1957 compiler skepticism.
Ending on a rhetorical question addressed to the reader.

## Tools index

Claude Code, https://claude.com/product/claude-code, the agent runtime every source builds on.
/goal, /loop, /schedule, built-in commands where goal runs to a condition, loop runs on a timer, and schedule runs unattended.
claude --worktree and claude -p, parallel session isolation and non-interactive CI invocation.
Unlazy, https://github.com/Leonxlnx/unlazy, gate files with runnable checks and digest-bound evidence.
skills CLI, npx skills add owner/repo, the installer used by Unlazy and mattpocock/skills.
mattpocock/skills, https://github.com/mattpocock/skills, the richest factory-shaped skill set, named in both a video and Reddit.
GitHub Spec Kit, specify-plan-tasks-implement, cited repeatedly as the prior art the playbook resembles.
AGENTS.md, cross-vendor agent instructions, recommended by both a video and Reddit so the repo is not vendor-locked.
Anthropic skills, https://github.com/anthropics/skills, including frontend-design.
Paseo, https://paseo.sh/, runs Claude Code locally with a phone window, preserving skills and slash commands.
fork-sandbox, https://github.com/mgalgs/fork-sandbox, sandboxed parallel agents without permission dialogs.
clodex, https://github.com/avirtual/clodex, multiple agents that talk to one another with visibility.
KitTools, https://github.com/WashingBearLabs/KitTools, spec-driven development with implementation and validation loops.
lattice-app-works, https://github.com/jo90-afk/lattice-app-works-platform-agnostic, truths in a database with the frontier re-derived per task.
beadhive.ai, https://beadhive.ai/, requests decomposed into beads.
assay.guide, https://assay.guide/, risk classification, sized stories, priority queue, adversarial review, and drives.
gate-analysis, https://michael.roth.rocks/research/gate-analysis/, metered gate catch rates from a real production pipeline.
coreforged.com/resources, https://coreforged.com/resources, a rated list of open-source resources and papers.
agentic-sdlc-showcase, https://olafkfreund.github.io/agentic-sdlc-showcase/, a proof of concept in customer environments.
Vercel agent-skills, https://github.com/vercel-labs/agent-skills, auto-invoking deploy skills.
Supabase agent-skills, https://github.com/supabase/agent-skills, auto-invoking database skills.
GSAP skills, https://github.com/greensock/gsap-skills, animation skills.
21st.dev, https://21st.dev, pre-made components.
Frontend Design, https://github.com/anthropics/skills/tree/main/skills/frontend-design, Anthropic's design skill.
UI/UX Pro Max, https://github.com/nextlevelbuilder/ui-ux-pro-max-skill, third-party design skill.
Design skill bake-off entrants, all third-party style skills tested in one video: https://github.com/emilkowalski/skills, https://github.com/ConardLi/garden-skills, https://github.com/elayadesign/ai-design-skills, https://github.com/MengTo/Skills, https://github.com/jakubkrehel/skills, https://github.com/codeswithroh/tastemaker, https://github.com/Owl-Listener/designer-skills.

Project-local artifacts named as patterns rather than downloads: design.functional.md, a features folder holding a spec plus an empty verification folder, a mocks folder, queue.md, PATTERNS.md, and .tdd-state.json.
Sensors named in loop guardrails: CI checks, coverage reports, Sonar API, checkstyle, screenshot diffs, type checking, custom lint rules, browser console errors, and e2e suites.

## Risks

Video claims are description-derived marketing copy, and nothing about on-screen behavior was verified.
Reddit vote counts signal popularity, not correctness, and the two best verification insights scored 7 and 1 points.
Unverified figures include the Faros telemetry, the DORA characterization, arxiv 2604.06996, the 60,000-repo count, the $400 bills, and every self-reported timing.
Several factory-shaped tools were posted by their own authors in threads asking what works, so treat them as leads rather than validated options.
Nobody in any source reported an escape rate or a total cost including remediation, and the one practitioner with a metered pipeline says he never measured escape rate.
That gap is the strongest argument for instrumenting the factory from day one rather than trusting reported practice.

## Appendix: surprise-me panel tables

Three fresh-context Fable 5.1 agents ran the `surprise-me` skill in panel mode on 2026-09-07 against this judge sentence: a first-time operator takes a voice note through brief, tickets, an unattended loop, and independent Fable grading to a merged PR on Loam or any Loam-seeded project, with fewer stalled loops and fewer hand edits than lean-v3.
The disposition column records the main session's decision; the reasons are in `../factory/ARCHITECTURE.md` and `LOOP.md`.

### Dormant assets

| # | idea | cost | disposition |
|---|---|---|---|
| 1 | reuse the Codex plugin's `review-output.schema.json` and adversarial prompt for the Codex review stage | 0 | adopted |
| 2 | run every grader with `--tools Read,Grep,Glob --no-session-persistence` | 1 flag | adopted |
| 3 | parse the worker stream-json with `summarize_sample.py` for denials per round in `status` | 20 min | adopted |
| 4 | parked `worktree-status` logic as the readiness half of `status` and the stale-worktree detector | 30 min | adopted |
| 5 | run the lint fixture regression in CI, which already installs claude and codex | 1 line | adopted |
| 6 | lift the parked `unknowns` question list into the brief | 15 min | adopted |
| 7 | gate plugin bumps on always-on token weight with `bin/skill_listing_weight.py` | 1 line | adopted |
| 8 | `bin/loam-attach.sh` as the seeded-project path for graders before F8 | 0 | adopted |
| 9 | `claude ultrareview --json <PR>` for high-risk PRs, run by the manager | billed | committed for later |
| 10 | seed `bin/factory eval` from the retired `bin/harness-smoke.sh` at `8d567f3` | read 105 lines | adopted |

Proof run: `codex exec review --help` shows `--output-schema`, `--json`, `-o`; the schema's verdict enum is `approve` and `needs-attention`; `loop.sh` line 160 passes no `--tools` to any grader.

### Reframings

| # | idea | disposition |
|---|---|---|
| 1 | per-ticket Do-not-touch deny list instead of a Files-owned allow list; scope becomes a judge finding | adopted |
| 2 | done checks (pass or fail only) versus a human merge checklist; no skip | adopted |
| 3 | the loop reads addenda from issue comments | rejected; addenda are body edits, one home, GitHub keeps history |
| 4 | the supervisor runs Rows measured and assembles the PR body; the worker writes code and decisions only | adopted |
| 5 | round 0 on the runner: checks on main plus a read-only Opus low doability probe | adopted |
| 6 | Track B goes voice note to ticket in one `/brief` session; design and `to-tickets` are Track C only | adopted |
| 7 | run directory keyed by the ticket hash; no freeze-once, no `rm frozen` | adopted |
| 8 | delete the fixer role; every round is a worker round with the previous failures appended | adopted |
| 9 | merge is the launch: `Closes #N` plus a runner timer over the `ready-for-agent` frontier | committed for later (F9) |
| 10 | cut the judge's `green` row, proven by replay | adopted |

Proof run: every lean-v3 ticket mirror is duplicated verbatim in its worker prompt (31/31, 33/33, 39/39, 37/37, 25/25 lines); issue #24's addendum is a comment, so the GitHub body has 29 lines and the frozen mirror 37; bash check names appear zero times in any ticket text.

### Adversary

| # | hole and closure | disposition |
|---|---|---|
| 1 | scope judged by reading the diff; close with `git diff --name-only` against the deny list before any grader | adopted |
| 2 | no environment exit and a fail-open reviewer fallback; close with `stopped-environment`, fail-closed graders, `notify.failed` | adopted |
| 3 | rotating nits never trip the stuck rule; close with a two-round grader cap and written precedence | adopted |
| 4 | Loam-only paths and repo names on the runner; close by proving a seeded-project run as an F1 done check | adopted |
| 5 | worker-authored measurements grade three judge rows; close by running Rows measured in the supervisor | adopted |
| 6 | loop contract unfrozen, fixed fence string, frozen dir writable by the worker; close by freezing `_common.md`, a random fence, and a separate write scope | adopted |
| 7 | a worker can rewrite its own ticket; close with deny rules on `gh issue edit` and `gh api`, and no issue-body execution on the operator's machine | adopted |
| 8 | the cannot-fail lint rejects regression guards and ignores skips; close with a `guard` prefix and the merge checklist | adopted |
| 9 | the Mac `gh` has two failures, keyring and TLS; a shim must rewrite `--body-file` to stdin | adopted (F0) |
| 10 | tracks by file count leak security changes into ungraded sessions; close with tracks by blast radius | adopted |

Proof run: `grep -nEi 'auth|login|subtype|no-result|is_error' loop.sh` shows the supervisor logs a failed model call and never branches on it; `gh auth status` on the Mac reports a keyring failure and `gh api rate_limit` a TLS failure.
