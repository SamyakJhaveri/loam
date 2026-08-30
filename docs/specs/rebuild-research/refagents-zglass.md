# Reference-agent audit: ZacheryGlass/.claude

> Source: https://github.com/ZacheryGlass/.claude (shallow clone, HEAD at audit time 2026-08-29).
> Scope: PLANNING-STAGE assets only - plan review, adversarial/spec review, architecture and system design, concept-to-design, technology selection, fleshing out the "how" of an implementation plan.
> Implementation, testing, and ops assets (test-runner, git-cherry-pick-orchestrator, github-issue-creator, perf, UI, hooks, statusline) are deliberately excluded.

## Repo shape

A personal `~/.claude` config: 12 agents, 7 slash commands, 6 skills, 3 hooks, a Go statusline, and a 21-line CLAUDE.md whose only content is "no emojis", "no Claude as commit author", and a documentation-brevity rule.
Nothing here is a template; there is no versioning, no distribution mechanism, no tests over the prompt assets.

The important structural fact for our purposes: **this repo has no plan reviewer and no spec reviewer.**
Every review agent it ships fires *after* code exists (structural completeness, bug hunting, C safety, compatibility, performance, UI, docs).
The one genuinely planning-shaped body of work is the *setup phase* of the `parallel-phases` skill plus its five reference documents, and the `generate-goal` skill.
So the planning value in this repo is concentrated in "how do I decompose work and write a brief an amnesiac agent can execute", not in "how do I criticize a design".

## The planning workflow, end to end

```
user has N loosely-specified tasks
  |
  v
/parallel-phases  (SETUP, interactive)
  1. identify tasks            <- AskUserQuestion on scope / priority / constraints
  2. gather code intelligence  <- Explore agents collect real paths, line numbers, excerpts
  3. conflict analysis         <- references/conflict-analysis.md   (merge-risk, 4 mitigations)
  4. phase grouping            <- references/dependency-analysis.md (4-dimension independence test)
  5. write enriched prompts    <- references/prompt-template.md     (self-contained brief)
  6. emit PLAN.md + STATE.md   <- references/plan-format.md, plan-template.md
  7. APPROVAL GATE             <- AskUserQuestion: begin / edit PLAN.md / cancel
  |
  v ( human approves; PLAN.md is immutable from here )
/parallel-phases  (EXECUTION, autonomous, /clear-resilient via file-backed state)
  worktree agents -> /review-gauntlet per task -> auto-fix -> phase merge + test gate -> doc agent
```

Two side channels feed the same pipeline:

- `/arch-review` -> `architecture-reviewer` agent. Standalone design review of a path or of the current diff. Not wired into parallel-phases.
- `generate-goal` skill. Compresses a converged conversation into one self-contained `/goal` directive under 4000 characters. Same "brief a cold agent" philosophy as `prompt-template.md`, aimed at the built-in `/goal` loop instead of at worktree agents.

The notable seam: **the human gate sits between planning and execution, and the plan is frozen after it.**
"Re-planning means deleting `<state-dir>` and starting over."
That is a real design commitment - it buys idempotent, `/clear`-survivable execution at the cost of any mid-run replanning.

There is no reviewer of the plan itself. The approval gate is a human reading a generated PLAN.md. That is the single largest gap versus what Loam is rebuilding.

---

## Asset 1 - `parallel-phases` setup phase

- **Path:** `skills/parallel-phases/SKILL.md` (377 lines; setup phase is roughly the first 130)
- **What it does:** turns a loose task list into a phased, conflict-analyzed, prompt-enriched PLAN.md plus a STATE.md dashboard, then stops at an explicit approval gate before any autonomous work.

Verbatim, the step that does the real work:

> "**2. Gather code intelligence** - For each task, spawn an `Explore` agent (or read directly for small scopes) to collect: Exact file paths and line numbers for code that will be read or modified; Current function signatures and short code excerpts at modification points; Existing test patterns [...]; Build system structure [...]. This is the critical step that makes prompts self-contained. Without it, agents waste time rediscovering the codebase or make incorrect assumptions."

And the stated principle:

> "**Gather, don't guess.** Read the actual code to get line numbers and excerpts. Don't assume line numbers from memory or conversation context - they drift."

**Judgment**

- (a) Bounded: yes, structurally. The setup phase has 7 numbered steps with defined outputs (PLAN.md, STATE.md), not an open-ended "analyze the work".
- (b) Rubric: partial. The rubric lives in the reference files (independence test, conflict checklist), not in the skill body.
- (c) Fresh-context/blind: not applicable to setup, but the *product* of setup is explicitly designed for zero-context consumers, which is the same discipline pointed outward.
- (d) Evidence over assertions: **strong**. Step 2 is a hard requirement to read the code before writing the plan, with a named failure mode (line numbers drift).
- (e) Generic competence: mostly no. A strong model will decompose tasks unprompted, but it will not reliably (i) refuse to write a plan before collecting real line numbers, or (ii) stop at a gate. Steps 1, 4 and 7 are close to generic; step 2 and the freeze semantics are not.

## Asset 2 - `references/prompt-template.md`

- **Path:** `skills/parallel-phases/references/prompt-template.md` (61 lines)
- **What it does:** specifies the exact anatomy of a task brief handed to an agent with zero conversation context: restrictions, files-to-read-first with line ranges, step-by-step instructions carrying current-state excerpts, acceptance criteria, verification commands, and literal commit recipes.

> "- **Be specific about what to read first.** List 3-8 files with line ranges. Don't say 'read the codebase' - say 'read src/foo.h lines 10-50 for the Foo struct.'
> - **Include code excerpts at modification points.** The agent needs to locate the exact insertion/replacement point. 3-5 lines of surrounding context is enough.
> - **Include verification that proves correctness**, not just compilation."

The anti-pattern list is the sharper half:

> "**Anti-patterns** - Vague scope: 'Refactor the module' - which functions? which files? / Missing line numbers: 'Update the struct' - there are 50 structs in the file / No commit instructions [...] / Assumed context: 'As discussed above' - the agent has no 'above' / Missing restrictions: agent spawns network calls or reads real credentials"

**Judgment**

- (a) Bounded: yes - a fixed section list, and a closed set of five anti-patterns.
- (b) Rubric: yes, and it is falsifiable. "3-8 files with line ranges" is checkable; "verification that proves correctness, not just compilation" is checkable.
- (c) Blind: n/a (authoring aid, not a reviewer).
- (d) Evidence: yes - every guideline forces a concrete artifact (path, line number, excerpt, command) instead of a description.
- (e) Generic competence: **partially yes, and this is the honest caveat.** A strong model asked to "write a self-contained brief" will produce most of this. The parts it will *not* reliably produce are the quantified floor (3-8 files, 3-5 lines of context), the "verification must prove correctness not compilation" distinction, and the "as discussed above" trap. Those three are the residue worth keeping; the rest is restating competence.

This file is a near-exact match for the Loam memory `feedback_plan_quality` ("handoff plans must be self-contained and execution-ready: explicit paths, exact paste-content, per-step verification, skills inline"). It is independent convergent evidence for that standard, and it adds the quantified floor Loam's version lacks.

## Asset 3 - `references/dependency-analysis.md`

- **Path:** `skills/parallel-phases/references/dependency-analysis.md` (92 lines)
- **What it does:** decides which planned tasks may run concurrently. A four-dimension independence test, a greedy grouping loop, granularity guidance, and a worked decision table.

> "Two tasks can go in the same phase if and only if they are **independent** by all of these dimensions: 1. **File overlap** [...] 2. **Resource overlap** - neither consumes an external resource the other does (EC2 instance, CI runner slot, live broker session, shared database, etc.). 3. **Output dependency** [...] 4. **Semantic dependency** - neither assumes the other has landed."

And the asymmetric-cost tiebreak, which is the best sentence in the file:

> "When scope is ambiguous, **serialize**. Worktree merges fail on file-level overlap, and fixing the phase mid-run costs more than splitting it upfront. [...] the cost of a too-serial plan is slower wall-clock; the cost of a too-parallel plan is merge conflicts that block the phase."

The decision table gives seven concrete calls (`"fix bug in parser" + "refactor parser"` -> 2 phases, same file; `"paper smoke on EC2" + "live smoke on EC2"` -> 2 phases, same resource).

**Judgment**

- (a) Bounded: yes - four dimensions, exhaustive by construction.
- (b) Rubric: yes, the strongest explicit rubric in the repo, plus calibration examples.
- (c) Blind: n/a.
- (d) Evidence: yes - grouping is driven off each task's declared `scope` field, and the check is a mechanical prefix/glob overlap test rather than a vibe.
- (e) Generic competence: **no for dimensions 2 and 4.** A strong model asked to parallelize will check file overlap and output dependency on its own; it will routinely miss shared external resources and "assumes the other has landed". The asymmetric-cost rule is also genuinely non-obvious - the default model instinct is to maximize parallelism.

## Asset 4 - `references/conflict-analysis.md`

- **Path:** `skills/parallel-phases/references/conflict-analysis.md` (62 lines)
- **What it does:** names where parallel plans actually break (single-line build-config variable lists, shared type headers, shared test fixtures) and gives four ranked mitigations, each with its tradeoff stated.

> "Single-line variable lists are the #1 conflict source: **Makefile**: `SRCS = ...` [...] **package.json**: `dependencies`, `scripts` objects [...] Two tasks appending to the same variable/section will always conflict."

> "**Strategy 1: Designate a config owner** - One task in the phase owns ALL build-config changes. [...] Tradeoff: config-owner task must know sibling tasks' output filenames in advance. Use when filenames are predictable.
> **Strategy 4: Serialize into separate phases** - Tradeoff: loses parallelism. Use ONLY as last resort."

**Judgment**

- (a) Bounded: yes - three named risk sources, four numbered mitigations.
- (b) Rubric: yes, and unusually each option carries an explicit tradeoff and a "use when" trigger, which is exactly the shape a design-option table should have.
- (c) Blind: n/a.
- (d) Evidence: partial - the analysis checklist ("List every file each task will modify") is evidence-driven, but the risk list is asserted from the author's own C/Makefile domain rather than derived.
- (e) Generic competence: no. The tradeoff-per-strategy format is a genuinely transferable pattern for *any* design-option enumeration, and the specific "config owner" trick is the kind of thing a model proposes only after being burned.

Caveat: the content is heavily biased toward C/Makefile projects. The *format* travels; the risk list does not.

## Asset 5 - `references/plan-format.md` + `plan-template.md`

- **Paths:** `skills/parallel-phases/references/plan-format.md` (79 lines), `plan-template.md` (144 lines)
- **What it does:** fixes PLAN.md as a machine-readable artifact - YAML frontmatter (`target_branch`, `test_command`, `state_dir`, `total_phases`, `generated_at`, `source`), phase sections carrying a `Rationale:` line, and per-task records with `agent_type` / `model` / `isolation` / `scope` / `prompt`. STATE.md is a separate mutable dashboard with an eleven-value status enum.

> "PLAN.md is written once during setup, reviewed by the user, and treated as immutable during execution. Re-planning means deleting `<state-dir>` and starting over."

> "`scope` | recommended | - | File-path prefixes or module names. Used by the orchestrator to predict merge conflicts."

**Judgment**

- (a) Bounded: yes.
- (b) Rubric: yes for structure, no for quality - the format says what fields exist, never what makes a plan good.
- (c) Blind: n/a.
- (d) Evidence: the `Rationale:` line is a required justification slot per phase, which forces the planner to state *why* a grouping is safe rather than just asserting the grouping. That is a small but real evidence hook.
- (e) Generic competence: the separation of immutable PLAN from mutable STATE, and the `scope` field existing specifically so a downstream step can mechanically check it, are both non-generic. The YAML boilerplate is generic.

The idea worth stealing is narrow: **a required per-decision `Rationale:` field, and a machine-checkable `scope` declaration that a later step actually consumes.** A plan field nothing reads is decoration; `scope` is read by the conflict analyzer, which is why it stays honest.

## Asset 6 - `generate-goal` skill

- **Path:** `skills/generate-goal/SKILL.md` (52 lines) + `scripts/check_goal_length.py`
- **What it does:** distills a converged conversation into a single self-contained `/goal` directive - Directive, Context, Constraints, COMPLETION - under a hard 4000-character cap, verified by script rather than by eye.

> "**End with a measurable completion condition.** `/goal` runs turn after turn until a small evaluator model confirms the condition holds. The evaluator reads the transcript; it does not run commands. So the condition must be provable from what the agent *surfaces* (files exist and are committed, a test result is reported, a stated number/verdict appears)."

> "Weak (unverifiable / open-ended): `improve the backtest realism`, `make the tests better`. Strong (one end state + stated check): `COMPLETION: bin/backtest builds, make test reports 4/4 byte-identical pins, and docs/state/BACKTEST_REALISM.md has a new changelog row with the OFF-vs-ON per-market PnL. No change to canonical defaults.`"

> "**Stay under the 4000-character limit.** [...] Always verify with the script in step 4 before outputting - do not eyeball it."

**Judgment**

- (a) Bounded: yes - four named sections, one output, no files on disk.
- (b) Rubric: yes, with a weak/strong contrast pair, which is the cheapest effective calibration device in the repo.
- (c) Blind: n/a.
- (d) Evidence: **best in repo.** The length constraint is enforced by a script with an explicit "do not eyeball it" instruction, and the completion condition is constrained by what the *evaluator can actually observe* (transcript text, not command execution). That second constraint is a genuinely sharp piece of reasoning about the verifier's capabilities, not the agent's.
- (e) Generic competence: **no.** "Write an acceptance criterion an evaluator that cannot run commands can check from the transcript" is a specific, learned constraint. A strong model writes completion conditions that assume the checker can run the test suite.

Note: the script path is hardcoded to `C:\Users\zache\.claude\...`. Not portable as-is.

## Asset 7 - `architecture-reviewer` agent

- **Path:** `agents/architecture-reviewer.md` (49 lines), driven by `commands/arch-review.md`
- **What it does:** a Principal-Architect persona reviewing a path or a diff against four pillars - Separation of Concerns / modularity, SOLID, scalability and resilience, maintainability and testability - and emitting Executive Summary / Strengths / Critical Risks / Areas for Improvement.

> "You must think like an engineer who will inherit this codebase in two years and has to build 20 new features on top of it."

> "**Leaking Abstractions:** Does the business logic layer have direct knowledge of the database schema or HTTP request/response objects? (e.g., a service function that takes `(req, res)` as arguments)."

> "You MUST evaluate the code based on the following pillars. For each point, provide evidence from the code."

**Judgment**

- (a) Bounded: **no.** The checklist enumerates topics, not a finding cap or a severity budget. Output tiers exist (Critical Risks vs Areas for Improvement) but nothing constrains how many items land in each, and "provide specific file paths, line numbers, and code snippets" is the only brake on invention.
- (b) Rubric: nominally yes, four pillars with sub-bullets - but they are textbook headings. A reviewer with this checklist will produce a textbook report.
- (c) Blind: no. The command feeds it the diff and the paths, never withholding author rationale; there is no fresh-context or blind-design provision anywhere in the repo.
- (d) Evidence: asserted ("For each point, provide evidence from the code") but not enforced - no verification step, no requirement to prove a claimed risk is reachable.
- (e) Generic competence: **yes, and this is the disqualifying verdict.** SOLID, SoC, DRY, DI, N+1 queries, stateless services, config-in-source - a strong model produces this list unprompted from the words "architecture review". Reciting it costs context and buys nothing. The two-year-inheritor framing is the only line with any lift, and even that is common.

Do not adopt. Recorded here as a negative result: a long checklist of canonical principles is the most common way a review asset looks rigorous while adding zero information.

## Asset 8 - `compatibility-reviewer` agent (contract-boundary technique only)

- **Path:** `agents/compatibility-reviewer.md` (259 lines, of which roughly 130 are a verbatim copy of the stock persistent-agent-memory boilerplate)
- **What it does:** post-change reviewer that enumerates every modified interface (env vars, JSON/HTTP shapes, state file formats, CLI flags, header exports, config formats, WebSocket message shapes, log formats) and greps the whole repo for consumers, classifying each as UPDATED / NOT UPDATED / PARTIALLY UPDATED with CRITICAL/HIGH/MEDIUM/LOW severity and a PASS/FAIL verdict.

Included here despite being post-implementation because its core move is a *design-contract inventory*, which is directly reusable at planning time - "what contracts does this plan change, and who consumes them?"

> "**Identify the change surface**: List every modified symbol, env var, flag, endpoint, format, struct field, or define. **For each modified item**: Use grep/ripgrep across the ENTIRE repository to find all consumers."

> "Never assume a consumer is updated just because it's in the same commit. Verify explicitly. [...] If you cannot determine whether a consumer is broken (e.g., dynamic usage), flag it as NEEDS MANUAL REVIEW rather than assuming it's fine."

> "Silent breakage - where code compiles and tests pass but runtime behavior is wrong - is your primary adversary."

**Judgment**

- (a) Bounded: yes in an unusual and useful way. The finding set is bounded by an *enumerated change surface* computed first - you cannot report a finding that does not trace to a listed changed item. That is a real anti-invention mechanism, better than any severity cap.
- (b) Rubric: yes - eight categories, four severity levels with concrete definitions ("HIGH: Silent wrong behavior (e.g., reading stale field, using wrong units)"), fixed output schema, explicit PASS/FAIL.
- (c) Blind: no.
- (d) Evidence: **strong.** Every finding must name file and line; "Never assume a consumer is updated just because it's in the same commit"; an explicit NEEDS MANUAL REVIEW escape hatch instead of guessing; and "If no breaking changes are found, still list what you checked and confirm PASS" - which makes the *absence* of findings auditable too.
- (e) Generic competence: mixed. A strong model will grep for renamed symbols. It will not, unprompted, treat documentation examples, `.env.example`, log-format-parsing scripts, and C struct field *offsets* as contract surfaces, nor will it default to NEEDS MANUAL REVIEW over a confident guess.

Caveats: heavily C/Docker/React-specific; and roughly half the file is boilerplate that has nothing to do with review. The transferable core is about 40 lines.

---

## Cross-cutting observations

1. **No blind review anywhere.** Every reviewer receives the diff plus whatever framing the caller supplies. There is no equivalent of Loam's blind elegance pass, and no asset withholds the author's rationale. This repo is not a source for that technique.
2. **No plan review at all.** The only gate on a plan is a human reading it. Confirms the gap Loam is filling rather than offering a solution to copy.
3. **The strongest single idea is "brief the amnesiac".** It appears twice, independently derived, in `prompt-template.md` and `generate-goal`. Both insist the consumer has zero context and both convert that into concrete required content.
4. **Enumerate-the-surface-first is the best bounding mechanism in the repo** (`compatibility-reviewer` step 1). It bounds findings by construction rather than by a numeric cap, which is strictly better: a cap forces arbitrary triage, an enumerated surface forces traceability.
5. **The weakest assets are the persona-plus-canonical-checklist ones** (`architecture-reviewer`, and `structural-completeness-reviewer` in the same mold). They read impressively and encode nothing a capable model lacks.
6. **Fix-without-asking is a deliberate stance.** `/review-gauntlet` step 3: "Immediately implement fixes for all Critical and Should-Fix items. Do not ask for permission - just fix them." Paired with "Do NOT re-run the full gauntlet. Trust the fixes unless the build fails." Worth noting as a cost-control precedent, though it is an execution-stage policy, not planning.
7. **Portability is poor.** Windows-absolute script paths, Makefile/C assumptions, and a hardcoded agent-memory directory. Nothing is liftable verbatim.

---

## Shortlist - worth folding into Loam

1. **The evaluator-aware completion condition** (`generate-goal`, plus its weak/strong contrast pair and the script-enforced length check). Fold into the plan-reviewer's output contract: every plan must end with an acceptance criterion provable from what the run *surfaces*, and the reviewer should reject plans whose completion condition assumes a checker that can run commands. This is the one technique in the repo that a strong model does not already have.

2. **Enumerate-the-change-surface-first as a finding bound** (`compatibility-reviewer` methodology step 1 plus its NEEDS MANUAL REVIEW escape hatch). Adopt in the merged blind plan-reviewer: list every contract the plan touches before reporting anything, and require each finding to trace to a listed item. Bounds output by traceability rather than by an arbitrary cap, and the escape hatch stops the reviewer converting uncertainty into a confident finding.

3. **The four-dimension independence test with its asymmetric-cost tiebreak** (`dependency-analysis.md`), packaged as an on-demand planning skill for decomposing multi-task work. Resource overlap and semantic "assumes the other has landed" are the two dimensions models reliably miss, and "when scope is ambiguous, serialize" is a non-obvious default that inverts the model's instinct to maximize parallelism. Take the tradeoff-per-strategy table format from `conflict-analysis.md` with it; leave its C/Makefile risk list behind.

Explicitly NOT recommended: `architecture-reviewer` (canonical-principle recital, generic competence), `structural-completeness-reviewer` (same mold, post-implementation), and the persona preambles throughout.
