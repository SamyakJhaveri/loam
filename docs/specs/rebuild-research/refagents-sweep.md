# Broad online sweep: planning-stage agents, skills and prompts

> Research pass for the Loam rebuild, 2026-08-29.
> Scope: adversarial plan review, spec audit, architecture/system-design partners, concept-to-design, technology selection and trade-off analysis.
> Excluded by assignment: VoltAgent/awesome-claude-code-subagents, ZacheryGlass/.claude, vercel-labs/agent-skills, mattpocock/skills, obra/superpowers.
> Method: WebSearch to find candidates, then GitHub API (`gh api .../contents/...`) to read the actual prompt files rather than READMEs.
> Every excerpt below was read from the raw file, not from a summary.

Quality codes used throughout:
(a) bounded findings vs unbounded critic; (b) explicit rubric; (c) fresh-context / blind design; (d) evidence over assertions; (e) generic competence a strong model already has.

---

## 1. github/spec-kit - `/speckit.analyze` (cross-artifact spec audit)

- **URL:** https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md
- **Signal:** 132,180 stars, pushed 2026-08-28. The single highest-traffic spec-driven-development toolkit in the ecosystem.
- **What it does:** A strictly read-only pass over `spec.md`, `plan.md` and `tasks.md` that builds an internal requirements inventory, maps every task to a requirement, and reports duplication, ambiguity, underspecification, constitution violations, coverage gaps and inconsistency, as a severity-ranked table plus a coverage matrix and numeric metrics.

**Best-technique excerpt (verbatim):**

> **Constitution Authority**: The project constitution (`/memory/constitution.md`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks-not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update outside `__SPECKIT_COMMAND_ANALYZE__`.

And the bounded-output rule:

> Focus on high-signal findings. Limit to 50 findings total; aggregate remainder in overflow summary.
> [...] **Deterministic results**: Rerunning without changes should produce consistent IDs and counts

**Judgment:**
- (a) Bounded, and bounded in an unusually explicit way: a hard 50-finding cap with an overflow summary, plus stable per-category finding IDs.
- (b) Yes. Six named detection passes (A-F) and a four-level severity heuristic that says what earns CRITICAL vs HIGH vs MEDIUM vs LOW in this domain specifically, not in the abstract.
- (c) Partially. It reloads artifacts from disk under "progressive disclosure" rather than trusting conversation state, but it is not run in a fresh context and it is not blind to author rationale.
- (d) Strong on traceability (a coverage table mapping requirement key to task IDs, plus a metrics block with coverage %), weaker on execution evidence - it never runs anything.
- (e) Not generic. The coverage-matrix idea - every requirement must map to at least one task, every task must map back to a requirement, and the unmapped ones on both sides are the report - is a mechanical check a strong model will not perform unprompted.

**Caveat:** roughly a third of the file is `.specify/extensions.yml` hook plumbing that is dead weight outside spec-kit. The valuable part is sections 3-7.

---

## 2. github/spec-kit - `/speckit.checklist` ("unit tests for English")

- **URL:** https://github.com/github/spec-kit/blob/main/templates/commands/checklist.md
- **What it does:** Generates a quality checklist that interrogates the *requirements document*, not the implementation. It is the sharpest framing of spec audit I found anywhere in this sweep.

**Best-technique excerpt (verbatim):**

> **Metaphor**: If your spec is code written in English, the checklist is its unit test suite. You're testing whether the requirements are well-written, complete, unambiguous, and ready for implementation - NOT whether the implementation works.

With the anti-example pairing that makes the rule enforceable:

> ❌ **WRONG - These test implementation, not requirements:**
> - [ ] CHK001 - Verify landing page displays 3 episode cards [Spec §FR-001]
> - [ ] CHK002 - Test hover states work correctly on desktop [Spec §FR-003]
>
> ✅ **CORRECT - These test requirements quality:**
> - [ ] CHK001 - Are the number and layout of featured episodes explicitly specified? [Completeness, Spec §FR-001]
> - [ ] CHK006 - Can "visual hierarchy" requirements be objectively measured? [Measurability, Spec §FR-001]

**Judgment:**
- (a) Bounded by category structure (nine named quality dimensions: Completeness, Clarity, Consistency, Acceptance Criteria Quality, Scenario Coverage, Edge Case Coverage, Non-Functional, Dependencies & Assumptions, Ambiguities & Conflicts).
- (b) Yes, and the rubric is a taxonomy plus a matched WRONG/CORRECT pair for each rule - the strongest instructional pattern in the whole sweep.
- (c) No blind-context mechanism.
- (d) Enforced by citation quota: "MINIMUM: ≥80% of items MUST include at least one traceability reference", with `[Spec §X.Y]` for existing requirements and `[Gap]` for missing ones. That single line converts a checklist from opinion into a grounded artifact.
- (e) The *distinction* between testing the spec and testing the build is something a strong model loses within two paragraphs of drafting unless it is pinned. Not generic.

---

## 3. github/spec-kit - `/speckit.clarify` (bounded ambiguity interrogation)

- **URL:** https://github.com/github/spec-kit/blob/main/templates/commands/clarify.md
- **What it does:** Scans a spec against a fixed 10-category taxonomy, marks each category Clear / Partial / Missing, then asks at most five questions chosen by an impact heuristic - and reports what it deliberately did not ask.

**Best-technique excerpt (verbatim):**

> - Maximum of 5 total questions across the whole session.
> - Each question must be answerable with EITHER:
>    - A short multiple-choice selection (2-5 distinct, mutually exclusive options), OR
>    - A one-word / short-phrase answer (explicitly constrain: "Answer in <=5 words").
> - Only include questions whose answers materially impact architecture, data modeling, task decomposition, test design, UX behavior, operational readiness, or compliance validation.
> - Ensure category coverage balance: attempt to cover the highest impact unresolved categories first; avoid asking two low-impact questions when a single high-impact area (e.g., security posture) is unresolved.
> - If more than 5 categories remain unresolved, select the top 5 by (Impact * Uncertainty) heuristic.

Plus the deferral ledger, which is what makes the cap honest:

> - If quota reached with unresolved high-impact categories remaining, explicitly flag them under Deferred with rationale.
> [...] Coverage summary table listing each taxonomy category with Status: Resolved [...], Deferred [...], Clear [...], Outstanding (still Partial/Missing but low impact).

**Judgment:**
- (a) Bounded, hard, with an audit trail for what the bound excluded. This is the correct answer to "bounded findings vs unbounded critic": cap the output *and* publish the overflow so the cap cannot hide a critical item.
- (b) Yes: a 10-category taxonomy with a three-state per-category status and an `Impact * Uncertainty` ranking function.
- (c) No.
- (d) Medium. The coverage map is derived from the document, but nothing is executed or verified externally.
- (e) The taxonomy itself is close to generic - a strong model asked "what's underspecified here" will hit most of those categories. The non-generic parts are the answer-shape constraint (multiple choice or ≤5 words) and the Deferred ledger.

---

## 4. Official Claude Code plan-mode prompts (extracted)

- **URL:** https://github.com/Piebald-AI/claude-code-system-prompts - specifically `system-prompts/system-reminder-plan-mode-phase-2-design.md` and `system-prompts/system-prompt-remote-plan-mode-ultraplan.md`
- **Signal:** 12,504 stars, pushed 2026-08-28, version-tracked per Claude Code release. These are Anthropic's own production planning prompts, verbatim, not a community reimplementation. The closest thing to an "official Anthropic example" that exists for the planning stage.
- **What it does:** Phase 2 of plan mode fans out parallel Plan agents along *named opposing axes*; the remote/ultraplan prompt defines what a reviewable plan looks like.

**Best-technique excerpt (verbatim), from phase-2-design:**

> Example perspectives by task type:
> - New feature: simplicity vs performance vs maintainability
> - Bug fix: root cause vs workaround vs prevention
> - Refactoring: minimal change vs clean architecture

**And from remote-plan-mode-ultraplan, the verifiability standard:**

> A plan should be easy for someone to inspect and verify. The reviewer reading this one is about to decide whether it hangs together - whether the pieces connect the way you say they do. Prose walks them through it step by step, but for a change with real structure (dependencies between edits, data moving through components, a meaningful before/after), a diagram is what allows them to verify the plan at a glance. [...] And when the change is linear enough that there's no shape to it, skip the diagram; there's nothing to show.

Also worth noting, the self-containment standard for a handoff plan:

> Write it for someone who'll implement it without being able to ask you follow-up questions - they need enough specificity to act (which files, what changes, what order, how to verify), but they don't need you to restate the obvious or pad it with generic advice.

**Judgment:**
- (a) Bounded by construction - a fixed small agent count with an explicit "skip agents for truly trivial tasks" escape hatch, which most community fan-out designs lack.
- (b) The perspective table is a rubric of a different kind: it names the *axis of disagreement* per task type rather than a severity scale. That is the part worth stealing.
- (c) Yes, structurally: each Plan agent is a fresh subagent given only exploration results and constraints. Not blind to rationale, but blind to the orchestrator's preferred answer.
- (d) Ties the plan's quality bar to a reader's ability to *verify* it, which is a sharper target than "be thorough".
- (e) The diagram-when-there-is-shape / skip-when-linear rule is exactly the kind of taste a strong model has but does not apply consistently. Worth pinning. The rest of plan mode is largely competence Fable 5 already has.

---

## 5. wan-huiyan/agent-review-panel + plan-review-integrator

- **URL:** https://github.com/wan-huiyan/agent-review-panel - `skills/agent-review-panel/SKILL.md` (2,278 lines) and `skills/plan-review-integrator/SKILL.md` (514 lines)
- **Signal:** 35 stars, pushed 2026-08-11. Low stars, unusually high craft - the repo carries its own design audits under `docs/analysis/` and an archived rejected proposal with the panel verdict that killed it.
- **What it does:** Runs 4-6 auto-selected reviewer personas through a 15-phase debate, then a judge. The companion skill takes that output and integrates it into a plan document with a traceability table.

**Best-technique excerpt (verbatim) - the control-validation gate:**

> **4. THE CONTROL-VALIDATION GATE - the signature step.** Before trusting any Assessment score, calibrate the panel: construct a **degenerate control** - a version of the deliverable made with NO real input (generic template / no research / subject name find-replaced) - and run it through the SAME personas. **A persona is valid only if it scores the control clearly below the real deliverable (rule of thumb: control < 3/10).** A persona that rates the degenerate control as highly as the real one is non-discriminating sycophancy → **drop it and report it.** This is the assessment analogue of the Phase 6 CONSENSAGENT sycophancy check, but it tests the panel against a **known-bad floor** rather than against reviewer agreement - run it whenever scores look suspiciously uniform, in ANY mode.

**Second excerpt - the actionability filter, from plan-review-integrator Phase 5:**

> | **Actionability** | Does this finding identify a specific, objectively verifiable issue with a concrete action? | 0.0 - 1.0 |
> | **Groundedness** | Is the finding supported by code citations, line references, or verifiable claims? | 0.0 - 1.0 |
>
> **Filter rules:**
> - **Drop** findings with actionability < 0.3 (conversational, acknowledgements, vague concerns)
> - **Flag for human review** findings with actionability 0.3-0.5 (valid concern, unclear action)
> - **Pass through** findings with actionability >= 0.5 (specific issue, concrete fix path)
> - Groundedness < 0.3 caps maximum severity at MEDIUM regardless of original rating

**Third excerpt - domain validation of the reviewer, not just of the plan:**

> **Domain validation checklist** - for each finding ask:
> - Does the prescribed fix make sense given domain constraints?
> - Is the reviewer assuming something untrue about the system?
> - Would the fix break something the reviewer doesn't know about?
> - Is the concern already mitigated by a mechanism the reviewer didn't see?
>
> Document cases where the finding is valid but the prescribed fix is wrong.

**Judgment:**
- (a) Bounded on the *consumption* side, which is the rarer and better half: findings are scored and dropped before they reach the plan. The panel itself is closer to unbounded (15 phases, 4-6 personas) and is far too heavy to adopt wholesale.
- (b) Yes - numeric 0-1 scoring on two named dimensions, with epistemic labels (`[VERIFIED]`, `[CONSENSUS]`, `[DISPUTED]`, `[UNVERIFIED]`, `[SINGLE-SOURCE]`) that adjust the score by fixed amounts.
- (c) Yes and this is its strongest structural feature: Phase 7 "Blind Final Assessment" has each reviewer score independently before seeing peers, and the correlated-bias warning states plainly that unanimous agreement among same-base-model reviewers may reflect shared bias rather than truth.
- (d) Groundedness scoring makes citation a scoring input rather than a style preference. That is the mechanism that turns "evidence over assertions" from an exhortation into a gate.
- (e) Not generic. Specifically, the degenerate control is a technique I have not seen elsewhere and a strong model will never invent mid-review.

**Caveat:** the panel skill at 2,278 lines is a research artifact, not something to vendor. Take the three mechanisms, leave the machinery. Note also that its own audit doc (`docs/analysis/2026-06-06-debate-disappearance-audit.md`) records the debate phase silently vanishing in practice - evidence that 15-phase orchestrations degrade.

---

## 6. wshobson/agents - `multi-reviewer-patterns`

- **URL:** https://github.com/wshobson/agents/blob/main/plugins/agent-teams/skills/multi-reviewer-patterns/SKILL.md
- **Signal:** 39,246 stars on the parent marketplace, pushed 2026-08-26. Widely installed.
- **What it does:** 127 lines covering how to allocate review dimensions, deduplicate findings across reviewers, calibrate severity, and format a consolidated report.

**Best-technique excerpt (verbatim) - the merge rules:**

> ### Merge Rules
>
> 1. **Same file:line, same issue** - Merge into one finding, credit all reviewers
> 2. **Same file:line, different issues** - Keep as separate findings
> 3. **Same issue, different locations** - Keep separate but cross-reference
> 4. **Conflicting severity** - Use the higher severity rating
> 5. **Conflicting recommendations** - Include both with reviewer attribution

And the calibration floor rules:

> - Security vulnerabilities exploitable by external users: always Critical or High
> - Performance issues in hot paths: at least Medium
> - Missing tests for critical paths: at least Medium

**Judgment:**
- (a) Neutral - it is a formatting and merging convention, not a critic.
- (b) Yes, a severity table crossing Impact against Likelihood with worked examples, plus five floor rules that prevent severity inflation drift between parallel reviewers.
- (c) No.
- (d) Weak. Nothing here demands citations or execution.
- (e) **Mostly generic.** A strong model handed three review reports will merge duplicates and pick the higher severity without being told. The only non-obvious content is the severity-floor rules, and even those are close to common sense. Low value for Loam; recorded here mainly because it is the most-installed thing in this space and I want the negative result on the record rather than re-searched later.

---

## Considered and rejected

| Asset | Signal | Why rejected |
|---|---|---|
| [45ck/software-architecture-skills](https://github.com/45ck/software-architecture-skills) | 15 stars, stale since 2026-04 | 14 architecture skills (tradeoff-analysis-writer, architecture-option-generator, component-boundary-reviewer, quality-attribute-scenario-writer). Read `tradeoff-analysis-writer/SKILL.md` in full: it is inputs / deliverables / operating principles prose with no rubric, no scoring, no bounds, no evidence rule. Pure (e) - "make assumptions and unknowns visible", "don't recommend an approach because it sounds current" is exactly the competence Fable 5 already has. |
| [ng/adversarial-review](https://github.com/ng/adversarial-review) | 11 stars | The Optimizer/Skeptic split is a real idea and the one line worth remembering is that findings must survive "a second, skeptical pass backed by command output, not reasoning alone" - but that is the same principle as the groundedness gate in #5, expressed less precisely, in a repo with far less signal. |
| [robertoecf/adversarial-review](https://github.com/robertoecf/adversarial-review) | 8 stars | Plan validation is delegated out to a Codex → Grok → Pi model chain. The value is in the cross-model routing, not in the prompt content; irrelevant to a merged blind plan-reviewer that runs in-session. |
| [SuperClaude_Framework](https://github.com/SuperClaude-Org/SuperClaude_Framework) | 23,848 stars | Cognitive-persona configuration framework. High popularity, but the planning content is persona flavor text, not a rubric or a gate. |
| anthropics/skills | Official | Checked the full tree. Nineteen skills, none in the planning/architecture/spec-audit space. The official planning material lives in the Claude Code system prompts instead - see #4. |

---

## Shortlist: what is genuinely worth folding in

Three techniques, in priority order.

**1. Groundedness as a severity cap, not a style note** (from plan-review-integrator, #5; reinforced by spec-kit's ≥80% citation quota in #2).
A finding without a file:line citation or a verifiable claim gets its severity capped at MEDIUM regardless of how alarming it sounds. This is one line of rubric that structurally prevents the failure mode Loam's own history documents - the verification-monoculture episode where five reviewers confidently confirmed a wrong count. A reviewer that cannot cite cannot block.

**2. The degenerate-control calibration gate** (from agent-review-panel, #5).
Before trusting a reviewer's verdict, run it against a known-bad input; if it scores the deliberately-bad artifact as highly as the real one, the reviewer is non-discriminating and its findings are discarded. This is the only technique in the sweep that validates the *reviewer* rather than the artifact, and it is directly applicable as an occasional calibration run on Loam's blind elegance-reviewer and plan-reviewer - not on every invocation, but whenever their verdicts start looking uniformly positive.

**3. Bounded findings with a published overflow ledger** (from `/speckit.clarify` and `/speckit.analyze`, #1 and #3).
Cap the reviewer's output hard - N findings, M questions - but require it to emit a coverage table listing every category it examined with a Resolved / Deferred / Clear / Outstanding status. The cap keeps a critic from becoming an unbounded generator of concerns; the ledger keeps the cap from silently swallowing a critical one. Loam's plan-reviewer currently has neither half.

A fourth, lower-priority note for the plan-*writing* side rather than the review side: the official plan-mode instruction to include a diagram only when the change has structural shape, and to skip it when the change is linear, is a better-calibrated version of the standing "show it visually" preference and is worth quoting verbatim into whatever writes handoff plans.
