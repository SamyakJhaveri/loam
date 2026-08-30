# Reference agents: VoltAgent/awesome-claude-code-subagents

> Audit for the Loam rebuild ledger.
> Scope: PLANNING-STAGE assets only (plan review, adversarial/spec review, architecture and system design, concept-to-design, technology selection, fleshing out the "how").
> Implementation, testing, ops, and marketing agents were deliberately skipped.
> Source audited: shallow clone at HEAD `c9e51ec0b3d43f5dcdd0b558a6cd28ba6ada97c1` (2026-08-12), 158 agent files across 10 categories.
> Local copy: `/private/tmp/claude-501/-Users-samyakjhaveri-Desktop-loam/eaaa42fa-6d1a-4cdf-9b47-950fec2bc57b/scratchpad/refagents/voltagent`

## Headline finding

The repo is two repos wearing one coat.

**Layer A (roughly 126 of 158 files)** is a machine-generated template.
Every file follows the identical skeleton: a one-paragraph "You are a senior X" preamble, a "When invoked: 1. Query context manager for..." list, then eight to twelve sections of four-to-eight-word noun phrases ("Scalability requirements met confirmed", "Technology maturity", "Wedge analysis"), then a fake JSON "Communication Protocol" addressed to a `context_manager` service that does not exist, then a fabricated "Delivery notification" quoting invented metrics.
These are worthless for Loam: the noun-phrase lists are generic competence any strong model already has, the JSON protocol instructs the model to call a nonexistent service, and the delivery notification actively teaches the model to invent numbers.

**Layer B (32 files)** has been hand-rewritten by someone who understood the failure mode.
Detection: `grep -rL requesting_agent` finds the 32 files with no fake protocol; `grep -rl "Scope and honesty rules"` finds the 8 strongest, all in `09-meta-orchestration/`.
These carry explicit tool-bounded scope, prohibitions on invented metrics, `path:line` evidence requirements, and corroboration thresholds.
This layer is where all the reusable value lives, and almost none of it is where you would look for it (the "architecture" and "review" agents are all Layer A).

## Criteria legend

For each agent: (a) bounds its findings, (b) explicit rubric, (c) fresh-context/blind design, (d) demands evidence, (e) generic competence a strong model already has.

---

## 1. agent-organizer

- Path: `categories/09-meta-orchestration/agent-organizer.md`
- URL: https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/09-meta-orchestration/agent-organizer.md
- Tools: `Read, Write, Edit, Glob, Grep`. Model: sonnet.

**What it does.** Given a task plus a glob of available agent definition files, it decomposes the task into subtasks with completion criteria, reads each candidate agent's actual frontmatter to learn what it can do, assigns subtasks by citing capabilities from the definition file, flags unmatched subtasks as gaps, and writes a Markdown plan naming the explicit handoff files between steps.

**Verbatim excerpts.**

> "Your tools are `Read, Glob, Grep, Write, Edit`. You can read task descriptions and agent definition files, search them, and write Markdown. You cannot run agents, monitor execution, measure response times, track cost, or query a "context manager" service. Do not claim to."

> "Base every agent recommendation on concrete task requirements and on capabilities you can point to in the agent's own definition file - not on invented performance scores or historical metrics you have no access to."

> "There is no message bus, no request/response protocol, and no live service to query. Coordination happens through: **Shared files** - one agent writes an output file [...] that the next agent reads. Name these handoff files explicitly in the plan."

**Judgment.** (a) Yes - scope is bounded by the tool list, and it must ask for the agent glob rather than guess. (b) Partial - a workflow, not a scored rubric. (c) Yes - "Required inputs" is a genuine fresh-context contract; it refuses to proceed without the available-agents scope. (d) Yes, strongly - every assignment must cite a capability in the agent's own file. (e) The decomposition steps are generic; the honesty block and the file-handoff model are not.

**Best-in-repo.** This is the single most useful file in the repo, and the "Scope and honesty rules" block is the transferable technique.

---

## 2. workflow-orchestrator

- Path: `categories/09-meta-orchestration/workflow-orchestrator.md`
- URL: https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/09-meta-orchestration/workflow-orchestrator.md
- Tools: `Read, Write, Edit, Glob, Grep`. Model: inherit.

**What it does.** The closest thing in the repo to "flesh out the how of an implementation plan." It turns a stated process into an explicit state machine: states, transitions with guard conditions, error boundaries with retry/backoff/timeout, saga-style compensating actions paired to each forward step with a defined rollback order, and human-approval gates. It writes a spec, and explicitly does not run it.

**Verbatim excerpts.**

> "Ground every design decision in the requirements or existing files you actually read. Cite `path:line` when a decision follows from an existing definition."

> "For multi-step transactions, pair each forward action with its compensating action and define the rollback order. Note anywhere the requirements leave the behavior undefined, rather than silently choosing one."

**Judgment.** (a) Yes. (b) Yes - the output contract is a real rubric: for each state, its allowed transitions, the guard on each, and what happens on error. That is checkable. (c) Yes - "If the process goal or the target format is not provided, ask - do not guess." (d) Yes - `path:line` citation. (e) The state-machine vocabulary is generic; the *completeness rubric* (every state must declare transitions + guards + error path) is the part a strong model routinely skips and would benefit from being told.

**Relevance to Loam.** The "for each X, these N facts must be explicit or flagged undefined" pattern is exactly what a plan-reviewer needs for plan steps, and Loam does not currently express it that way.

---

## 3. knowledge-synthesizer

- Path: `categories/09-meta-orchestration/knowledge-synthesizer.md`
- URL: https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/09-meta-orchestration/knowledge-synthesizer.md
- Tools: `Read, Write, Edit, Glob, Grep`. Model: sonnet.

**What it does.** Mines logs and session transcripts for recurring patterns and writes an evidence-cited `knowledge.md`. Not a planning agent itself, but it carries the strongest evidence discipline in the repo.

**Verbatim excerpts.**

> "Report a pattern only when it appears in **at least two independent sources**. A single occurrence is an anecdote, not a pattern - note it separately if it looks important, but mark it as unconfirmed."

> "Never fabricate quantities. Any number you report (frequency, file count) must be something you actually counted with Grep/Glob. If you did not count it, do not state it."

> "Resolve the input glob with `Glob`; report how many files matched. If nothing matches, stop and report that - do not proceed on an empty set."

**Judgment.** (a) Yes. (b) Yes - the two-source corroboration threshold is a hard, mechanical rubric. (c) Yes. (d) Yes, the strongest in the repo. (e) No - the corroboration rule and the empty-set stop are precisely the disciplines a confident model skips.

**Relevance to Loam.** This directly answers the Loam verification-monoculture gotcha (five reviewers sharing one flawed `ls -d */`). "Two independent sources or mark it unconfirmed" plus "if you did not count it with a command, do not state it" are the two lines worth stealing verbatim.

---

## 4. context-manager

- Path: `categories/09-meta-orchestration/context-manager.md`
- URL: https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/09-meta-orchestration/context-manager.md
- Tools: `Read, Write, Edit, Glob, Grep`. Model: sonnet.

**What it does.** Designs the shared-file layout a multi-agent workflow uses for state: directory structure, naming conventions, per-file schema, and explicit read/update access rules (append vs. edit-in-place, who owns which file).

**Verbatim excerpt.**

> "You do **not** run a live datastore, cache, or service. There is no database, no cache tier, no replication, no query engine - just files on disk. Do not claim retrieval times, hit rates, availability percentages, consistency scores, or context counts."

**Judgment.** (a) Yes. (b) Partial. (c) Yes - "If the scope is not provided, ask - do not guess which files are authoritative." (d) Partial. (e) Largely yes for Loam specifically - Loam already has a far more developed answer to this in `reassess-context-md-anatomy.md`, including the Skip column, which this file has no equivalent of. **Not worth adopting.** Listed because it demonstrates the same rewrite pattern and confirms the Layer B authorship, and because its "when you are unsure whether a file is the current source of truth, say so" line is a decent one-liner.

---

## 5. first-principles-thinking

- Path: `categories/10-research-analysis/first-principles-thinking.md`
- URL: https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/10-research-analysis/first-principles-thinking.md
- Tools: `Read, Grep, Glob, WebFetch, WebSearch`. No model pin.

**What it does.** A 5-step assumption-demolition method (define precisely, enumerate assumptions, challenge each, extract fundamental truths, rebuild), plus a separate 5D problem-solving loop (Define / Diagnose / Diverge / Decide / Deploy). The closest thing in the repo to a concept-development or frame-breaking asset.

**Verbatim excerpts.**

> "Strip out solution framing and get to the real problem. Weak: "We need a better onboarding flow". Strong: "New users fail to reach their first value moment within 7 days""

> "D4: Decide. Evaluate options on: Impact [...] Effort [...] Risk [...] Reversibility (can we undo this?)"

> "Deliver: [...] 2. List of challenged assumptions with verdict (valid / invalid / partially valid)"

**Judgment.** (a) Partial - the assumption-verdict output format bounds it somewhat, but there is no cap on findings and no severity ordering. (b) Yes - the four decision axes and the three-valued assumption verdict are a real, if light, rubric. (c) No - it assumes a conversational session, not a blind fresh-context handoff. (d) No - nothing requires evidence for a verdict; "Is this actually true? What evidence supports it?" is asked of the *assumption*, not demanded of the *reviewer's own claim*. (e) Mostly yes. The 5-step method is well-known and a strong model applies it unprompted. The weak/strong problem-restatement contrast and the reversibility axis are the only parts that add anything.

**Verdict.** Marginal. Loam's `elegance-reviewer` already covers frame-breaking with more teeth. Steal at most the reversibility axis, which is already in FABLE-BRAIN section 3.

---

## 6. assumption-mapping

- Path: `categories/08-business-product/assumption-mapping.md`
- URL: https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/08-business-product/assumption-mapping.md
- Tools: `Read, Write, Edit, Glob, Grep, WebFetch, WebSearch`. No model pin. 486 words - the tightest file audited.

**What it does.** Extracts hidden assumptions from an idea across four risk categories (Value, Usability, Business viability, Feasibility), scores each on importance x current evidence strength, and ranks the top 3-5 to test first with the cheapest experiment for each.

**Verbatim excerpts.**

> "| High importance + Weak evidence | **Test immediately** - highest priority |
> | Low importance + Weak evidence | Test eventually |
> | High importance + Strong evidence | Monitor |
> | Low importance + Strong evidence | Ignore for now |"

> "For Each Priority Assumption, Define: 1. The assumption stated clearly 2. The riskiest version of this assumption 3. The cheapest/fastest experiment to test it 4. What "validated" looks like (success metric) 5. What "invalidated" means for the product direction"

**Judgment.** (a) **Yes, best in repo.** "Rank and identify the top 3-5 to test first" is a hard cap on output, and the grid explicitly routes low-value findings to "Ignore for now" rather than reporting them. This is the anti-unbounded-critic mechanism Loam's plan-reviewer needs. (b) Yes - a genuine 2x2 with named actions per quadrant. (c) Partial - self-contained method, but written for interactive product work. (d) Partial - "Evidence" is one grid axis, so a finding must be justified by *weak* evidence, but the reviewer is not asked to cite where it looked. (e) The VUBF categories are product-management jargon that does not transfer to a code plan. The **importance x evidence grid and the top-N cap do transfer**, and are not something a model applies unprompted (models default to reporting everything they found).

**Verdict.** The single most portable *mechanism* in the repo, once stripped of its product-strategy vocabulary.

---

## 7. project-idea-validator

- Path: `categories/10-research-analysis/project-idea-validator.md`
- URL: https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/10-research-analysis/project-idea-validator.md
- Tools: `Read, Write, Edit, Glob, Grep, WebFetch, WebSearch`. Model: sonnet.

**What it does.** A Layer A file with a Layer B opening paragraph. Pressure-tests an idea, hunts for the fatal flaw, delivers go/no-go. After the first paragraph it collapses into noun-phrase lists ("Wedge analysis", "Unfair advantage claims"), a fake JSON protocol, and phase headings.

**Verbatim excerpt (the one part worth reading).**

> "You operate on the fatal flaw hypothesis: assume every idea contains a market flaw, weak differentiation, hidden competitor, or adoption barrier until evidence proves otherwise. You strictly forbid sycophancy. You do not validate an idea because it sounds clever. You actively hunt for the mistake [...] If an idea survives scrutiny, give explicit objective credit and shift from flaw-hunting to execution strategy."

**Judgment.** (a) No - unbounded critic by construction; no cap, no severity ordering. (b) No - "Anti-sycophancy protocols: Default skepticism / Fatal flaw hunting / Proof demanding / Assumption destroying" is a list of nouns, not a rubric a reviewer can apply or fail. (c) No - "Query context manager for the core idea" is a nonexistent service. (d) Rhetorically yes ("until evidence proves otherwise"), mechanically no. (e) Yes, mostly.

**One idea worth keeping:** the explicit **exit condition** - "if it survives, give objective credit and shift from flaw-hunting to execution strategy." An adversarial reviewer that cannot ever say "this is fine" produces noise, and most adversarial prompts (including some of Loam's) omit the license to approve.

---

## 8. architect-reviewer (negative exemplar)

- Path: `categories/04-quality-security/architect-reviewer.md`
- URL: https://github.com/VoltAgent/awesome-claude-code-subagents/blob/main/categories/04-quality-security/architect-reviewer.md
- Tools: `Read, Write, Edit, Bash, Glob, Grep`. Model: inherit. 905 words.

**What it does.** Nominally the repo's system-design reviewer, and therefore the file this audit most expected to be useful. It is the purest Layer A specimen.

**Verbatim excerpts.**

> "Architecture review checklist: - Design patterns appropriate verified - Scalability requirements met confirmed - Technology choices justified thoroughly - Integration patterns sound validated"

> "Delivery notification: "Architecture review completed. Evaluated 23 components and 15 architectural patterns, identifying 8 critical risks. Provided 27 strategic recommendations [...] Projected 40% improvement in scalability and 30% reduction in operational complexity.""

**Judgment.** (a) No. (b) No - a "checklist" whose items are adjective-verb pairs ("appropriate verified") cannot be passed or failed. (c) No - step 1 is "Query context manager", a service that does not exist. (d) No - the opposite: the delivery notification is a worked example of fabricating precise metrics ("40% improvement") with no measurement, which is exactly the failure Layer B was written to stop. (e) Yes, entirely - the twelve topic lists are a table of contents for a systems-design textbook and add nothing to a strong model.

**Why it is in this report.** As a cautionary artifact for the ledger. `api-designer.md`, `microservices-architect.md`, `cloud-architect.md`, `llm-architect.md`, `graphql-architect.md`, and `design-bridge.md` are all the same template with different nouns and were checked and rejected on the same grounds. If Loam ever generates agents from a template, this is the failure mode: length that reads as thoroughness while containing no checkable instruction.

---

## Cross-cutting observations

**The recurring VoltAgent failure is unfalsifiable rubrics.** A checklist item like "Scalability requirements met confirmed" cannot be failed, so it constrains nothing. Layer B's items can be failed: "does every state declare its transitions, guards, and error path?" has an answer. A Loam plan-reviewer checklist item should be phrased so a reviewer could return "no" to it.

**Nothing in the repo is designed blind.** Not one agent withholds the author's rationale from the reviewer or takes a path argument as its sole input. Loam's `elegance-reviewer` blind-invocation contract has no analogue here and is ahead of anything in this repo.

**Bounding is nearly absent.** Of 158 agents, `assumption-mapping` is the only one that caps its own output ("top 3-5") and explicitly routes low-value findings to "ignore." Every review agent is an unbounded critic.

**Where the repo does beat Loam:** the "Scope and honesty rules" block ties the prompt to the agent's actual `tools:` list and names the specific fabrications to avoid. Loam's agent definitions declare tools in frontmatter but never tell the model what its tool list implies it *cannot* claim.

---

## Shortlist: what is genuinely worth folding in

1. **The tool-bounded honesty block** (`agent-organizer.md`, and the 8 files matching `grep -rl "Scope and honesty rules"`) - a short opening section that restates the agent's own `tools:` list, names what those tools make it unable to do, and forbids reporting any number it did not compute itself. Fold into the merged blind plan-reviewer; Loam declares tools in frontmatter but never states their implications, and this is the cheapest available guard against a confident reviewer inventing findings.

2. **The importance x evidence grid with a hard top-N cap** (`assumption-mapping.md`) - score each finding on impact-if-wrong against strength-of-evidence, report only the top 3-5, and explicitly discard the low-impact/strong-evidence quadrant. This is the one mechanism in the repo that converts an unbounded critic into a bounded one, which is the exact defect in Loam's current plan-reviewer.

3. **The two-source corroboration rule plus the empty-set stop** (`knowledge-synthesizer.md`) - "report a pattern only when it appears in at least two independent sources; a single occurrence is an anecdote, mark it unconfirmed" and "if the glob matched nothing, stop and report that." Adopt verbatim as reviewer evidence discipline; it is the direct antidote to the verification-monoculture failure already recorded in Loam's known-issues.

Runner-up, worth one line rather than a section: `project-idea-validator`'s **approval exit condition** - state explicitly that a reviewer which finds nothing blocking must say so and stop, rather than manufacturing findings to justify the invocation.

**Do not adopt:** anything in Layer A (any file where `grep -q requesting_agent` succeeds - roughly 126 of 158, including every file with "architect" or "designer" in its name). The whole of `context-manager.md` (Loam's CONTEXT.md anatomy is stronger) and `first-principles-thinking.md` (redundant with `elegance-reviewer` and FABLE-BRAIN).
