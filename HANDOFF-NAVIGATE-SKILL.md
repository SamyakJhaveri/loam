# HANDOFF: Progressive Disclosure + `/navigate` Skill Implementation

> **Fresh-session kickoff:** paste this entire file into a new Claude Code session opened at `/home/samyak/Desktop/parbench_sam`. Everything needed is inline. Do not explore unless a step fails.
>
> **Starting prompt to paste after this doc:**
> *"Read HANDOFF-NAVIGATE-SKILL.md and execute Part 1 then Part 2. Run the verification steps between each part. Commit atomically per the commit strategy. Do not re-research — the research ground truth is in this doc."*

---

## Goal

Close two gaps in this ParBench Claude Code setup:

1. **Enable L1 discovery for 20 skills.** 20 of 25 ParBench skills at `.claude/skills/` lack YAML frontmatter, so Claude cannot auto-route to them via description matching. Add 4-line frontmatter blocks to all 20.

2. **Create a unified tool recommender.** No single entry point takes "I want to do X" and returns the right tool across the 4 ecosystems (ParBench skills, ParBench agents, GSD commands, superpowers skills). Build a new `/navigate` skill that does this, using the L1/L2/L3 progressive disclosure pattern as its working example (SKILL.md + taxonomy.md + examples.md).

Total scope: edit 20 files (frontmatter only, no body changes) + create 1 new directory with 3 files.

---

## Current Progress

- **Research complete.** All ground truth (paths, line counts, frontmatter examples, agent/GSD/superpowers inventories, real user intention patterns) is baked into the "Research Ground Truth" section below. Do not re-explore.
- **Plan written.** The full implementation plan (Part 1 + Part 2) is inline below, with exact file contents for the 3 new files and exact frontmatter text for the 20 existing files.
- **Nothing has been implemented yet.** The repo is unchanged.

---

## What Worked (so far)

- Running 5 parallel Explore agents to audit: existing routing skills, full skills catalog, hooks/settings, GSD routing mechanisms, and web research on Claude Code skill-discovery patterns. This produced the grounded taxonomy.
- Running 3 more parallel Explore agents to get: exact file sizes + frontmatter state of each skill, agent inventory, GSD + superpowers command lists, and the user's real recurring intentions from memory / git log / HANDOFF.
- Using the `agent-team` skill as the canonical L1/L2/L3 reference — it's the only existing skill in the repo that already practices progressive disclosure (SKILL.md + 3 referenced `.md` files).

## What Didn't Work (avoid repeating)

- **Do NOT re-run broad exploration agents.** The research is complete. Re-running wastes ~50k tokens per agent.
- **Do NOT try to refactor the 14 large skills (>150 lines) into L2/L3 in this session.** That's a separate follow-up. This session is frontmatter-only for existing skills + the new `/navigate` skill.
- **Do NOT modify `workflow-ref`, `gsd-do`, `using-superpowers`, or `model-route`.** They coexist with `/navigate`; no integration needed.
- **Do NOT invent tools.** The `/navigate` skill's taxonomy must reference only real tools in the 4 lists below.

---

## Next Steps

Execute Part 1 → verify → commit → execute Part 2 → verify → commit → optional CLAUDE.md registration commit. Full detail below.

---

# Research Ground Truth (do not re-explore)

## Skills inventory (25 skills at `/home/samyak/Desktop/parbench_sam/.claude/skills/`)

**Skills WITH YAML frontmatter already (5 — do NOT touch):** `agent-team`, `handoff`, `mentoring`, `techdebt`, `workflow-ref`

**Skills MISSING frontmatter — need description added (20):**

| Skill | Current lines | Path to SKILL.md |
|-------|--------------|------------------|
| augment-test | 47 | `.claude/skills/augment-test/SKILL.md` |
| catchup | 144 | `.claude/skills/catchup/SKILL.md` |
| cite-check | 164 | `.claude/skills/cite-check/SKILL.md` |
| dream | 237 | `.claude/skills/dream/SKILL.md` |
| eval-run | 161 | `.claude/skills/eval-run/SKILL.md` |
| feature-dev | 39 | `.claude/skills/feature-dev/SKILL.md` |
| fix-bug | 43 | `.claude/skills/fix-bug/SKILL.md` |
| gen-spec | 58 | `.claude/skills/gen-spec/SKILL.md` |
| grill-research | 167 | `.claude/skills/grill-research/SKILL.md` |
| hypothesis-tree | 152 | `.claude/skills/hypothesis-tree/SKILL.md` |
| interpret-results | 205 | `.claude/skills/interpret-results/SKILL.md` |
| model-route | 141 | `.claude/skills/model-route/SKILL.md` |
| overnight-eval | 326 | `.claude/skills/overnight-eval/SKILL.md` |
| paper-review-sim | 246 | `.claude/skills/paper-review-sim/SKILL.md` |
| post-eval | 197 | `.claude/skills/post-eval/SKILL.md` |
| ralph-loop | 322 | `.claude/skills/ralph-loop/SKILL.md` |
| reflect | 162 | `.claude/skills/reflect/SKILL.md` |
| review | 44 | `.claude/skills/review/SKILL.md` |
| spec-check | 198 | `.claude/skills/spec-check/SKILL.md` |
| validate | 225 | `.claude/skills/validate/SKILL.md` |

## Canonical frontmatter example (reference — do NOT modify this file)

`/home/samyak/Desktop/parbench_sam/.claude/skills/agent-team/SKILL.md` lines 1–4:

```yaml
---
name: creating-agent-teams
description: Creates and launches coordinated agent teams using TeamCreate for multi-teammate tasks requiring cross-talk, shared task lists, and lifecycle management. Use when 2+ workers need to communicate findings to each other, not just report to parent. NOT for independent parallel tasks (use dispatching-parallel-agents instead).
---
```

Target structure: `description` is one line, includes "Use when" trigger conditions and a negative ("NOT for...") to prevent over-matching.

## Existing L1/L2/L3 example in repo

`/home/samyak/Desktop/parbench_sam/.claude/skills/agent-team/` is the only skill already using progressive disclosure:

```
SKILL.md              287 lines  [L1+L2 — frontmatter + body]
advisor-prompt.md      56 lines  [L3 — loaded only when advisor scenario chosen]
scenarios.md          166 lines  [L3 — loaded only when scenario lookup needed]
teammate-prompt.md    156 lines  [L3 — loaded only when spawning teammates]
```

`/navigate` will mirror this structure.

## Agents inventory (14 at `/home/samyak/Desktop/parbench_sam/.claude/agents/`)

`code-simplifier`, `consistency-checker`, `diff-reviewer`, `eval-batcher`, `explorer`, `plan-reviewer`, `regression-checker`, `rodinia-verifier`, `security-scanner`, `self-critic`, `spec-auditor`, `test-synthesizer`, `verification-lead`, `verify-app`

## GSD commands (73 total) — critical ~20 routing targets

`/gsd-do`, `/gsd-next`, `/gsd-progress`, `/gsd-quick`, `/gsd-fast`, `/gsd-debug`, `/gsd-plan-phase`, `/gsd-execute-phase`, `/gsd-discuss-phase`, `/gsd-add-todo`, `/gsd-check-todos`, `/gsd-resume-work`, `/gsd-pause-work`, `/gsd-review-backlog`, `/gsd-code-review`, `/gsd-verify-work`, `/gsd-handoff`, `/gsd-note`, `/gsd-ship`, `/gsd-help`

## Superpowers skills (14 total)

`superpowers:brainstorming`, `superpowers:writing-plans`, `superpowers:executing-plans`, `superpowers:test-driven-development`, `superpowers:systematic-debugging`, `superpowers:verification-before-completion`, `superpowers:dispatching-parallel-agents`, `superpowers:subagent-driven-development`, `superpowers:using-git-worktrees`, `superpowers:finishing-a-development-branch`, `superpowers:requesting-code-review`, `superpowers:receiving-code-review`, `superpowers:writing-skills`, `superpowers:using-superpowers`

## User's real recurring intentions (derived from memory, git log, HANDOFF-LE-GPT54-EVAL.md)

- Launch overnight eval on new model → `/overnight-eval` + `eval-batcher`
- Check pipeline health before commit → `/validate`
- Fix a broken spec/oracle → `/fix-bug` + `/spec-check` + `rodinia-verifier`
- Resume after context switch → `/catchup` or `/gsd-resume-work`
- Plan multi-bucket fix with adversarial review → `/gsd-plan-phase` + `/agent-team` (plan-reviewer + critic + worker)
- Write paper section → `/agent-team` with paper-assembly scenario
- Verify before commit → `/validate` waves 1–3 (pre-commit gate requires it)
- Set model for session → `/model-route`
- Interpret eval results → `/interpret-results`
- Handoff to next session → `/handoff`
- Write new skills → `superpowers:writing-skills`
- Debug systematically → `superpowers:systematic-debugging` or `/gsd-debug`
- Generate new benchmark specs → `/gen-spec`
- Test augmentation transforms → `/augment-test`
- Overnight post-batch cleanup → `/post-eval` + `dashboard-refresher` agent

---

# Part 1: Add YAML Frontmatter to 20 Skills (~30 min)

For each skill below, prepend a YAML frontmatter block to the existing `SKILL.md`. Do NOT modify body content — just add 4 lines at the top plus a blank line before the existing first line.

## Edit protocol for each file

1. `Read` the file to confirm it does NOT already start with `---`.
2. Use `Edit` with `old_string` = the current first line (as-is) and `new_string` = the 4-line frontmatter block + blank line + that same first line.

## Frontmatter blocks to add (exact text, per skill)

### augment-test/SKILL.md
```
---
name: augment-test
description: Augmentation testing workflow for ParBench C-code transforms. Use when testing a new AST transform in c_augmentation/, diagnosing transform failures on a spec, or validating a transform against known-bug ground truth. Runs c_augmentation tests and reports pass/fail per transform.
---
```

### catchup/SKILL.md
```
---
name: catchup
description: Fast 30s session bootstrap briefing. Use when resuming work after any break, at the start of a fresh session, or when unsure of current project state. Reports git status, recent commits, env state, memory staleness, pending tasks, and red flags (uncommitted changes, detached HEAD, stale memory).
---
```

### cite-check/SKILL.md
```
---
name: cite-check
description: Paper citation and claims verifier. Use before submitting a paper, after major eval runs that change numbers, or when reviewing a paper draft. Traces every numeric claim in the paper to a result JSON on disk; flags UNTRACED, MISMATCH, STALE_REF, MISSING_CITE, PHANTOM categories.
---
```

### dream/SKILL.md
```
---
name: dream
description: Memory consolidation for ~/.claude/projects memory files. Use after major milestones, after 5+ sessions without consolidation, when memory feels stale, or before long breaks. Runs 4-phase audit→plan→approval→execute; subcommands `audit` (read-only) and `prune <file>` (targeted).
---
```

### eval-run/SKILL.md
```
---
name: eval-run
description: Launch an LLM evaluation batch. Use for interactive/foreground eval runs — param collection, pre-flight checks, execution via run_eval_batch.py, and post-run analysis. For long-running batches that need tmux isolation, use overnight-eval instead.
---
```

### feature-dev/SKILL.md
```
---
name: feature-dev
description: Feature development workflow — explore, plan, implement, verify. Use when adding a new feature to harness, scripts, visualizations, or any non-trivial code change. NOT for single-file bug fixes (use fix-bug) or trivial edits (use gsd-quick).
---
```

### fix-bug/SKILL.md
```
---
name: fix-bug
description: Bug fix workflow — reproduce, diagnose, plan, fix, verify, record. Use when a test fails, a spec breaks, a harness step fails, or eval results show an unexpected pattern. Mandates reproduction before diagnosis. Integrates with /validate on exit.
---
```

### gen-spec/SKILL.md
```
---
name: gen-spec
description: Guided kernel spec generation wizard for new benchmark suites or kernels. Use when adding a new benchmark (e.g., /gen-spec xsbench), porting a kernel to a new API, or generating specs for an uncharacterized directory of kernels. Validates source, writes generator, standardizes, checks schema, updates manifest, smoke-tests.
---
```

### grill-research/SKILL.md
```
---
name: grill-research
description: Adversarial research interrogation before launching an eval or making a published claim. Use before /overnight-eval, before adding a claim to the paper, or when a reviewer-style stress test is needed. 4 waves: basics, clarifications, deep probes, assessment. Stops you from running expensive batches on shaky premises.
---
```

### hypothesis-tree/SKILL.md
```
---
name: hypothesis-tree
description: Structured hypothesis tree manager for multi-step research investigations. Use when investigating "why X fails" questions that branch into sub-hypotheses, or when you need to track falsifiable claims with linked evidence and timestamps. Subcommands: add, update, review, prune.
---
```

### interpret-results/SKILL.md
```
---
name: interpret-results
description: Hypothesis-first interpretation of eval results. Use after an eval batch completes, after /post-eval populates analyses, or when preparing paper narrative from result JSONs. Phase 1 requires a prior hypothesis (prevents post-hoc rationalization); Phase 2 compares to actual data.
---
```

### model-route/SKILL.md
```
---
name: model-route
description: Advisor for selecting optimal Claude model tier (Opus/Sonnet/Haiku) for a specific task. Use before launching an agent team, before a multi-file refactor, or when deciding whether to switch from Opus to Haiku for transactional work (commits, formatting). Analyzes reasoning depth, blast radius, domain expertise, output length, correctness cost.
---
```

### overnight-eval/SKILL.md
```
---
name: overnight-eval
description: Long-running LLM evaluation campaign with tmux isolation. Use for any eval batch that exceeds ~30 minutes, for canonical Phase 3 + ablation runs, or when the user will be away during the run. Pre-flight → tmux launch → monitor → post-flight analysis → dashboard refresh. For short interactive runs use eval-run instead.
---
```

### paper-review-sim/SKILL.md
```
---
name: paper-review-sim
description: Simulate a NeurIPS/SC/ICSE-style peer review with 5 reviewer personas (HPC, ML, Stats, Reproducibility, Devil's Advocate). Use before paper submission, after major methodology changes, or when stress-testing a draft against expected objections. Each reviewer verifies claims against actual result data.
---
```

### post-eval/SKILL.md
```
---
name: post-eval
description: Post-batch analysis pipeline that runs after an eval batch completes. Use after /eval-run or /overnight-eval finishes. Verifies results → runs analyze_eval.py → classify_pairs.py → refreshes dashboard → writes summary. Does NOT launch new eval runs.
---
```

### ralph-loop/SKILL.md
```
---
name: ralph-loop
description: Stateless iterative task execution loop. Use when you have a task file with N independent tasks that should each run to success with commit after each, forced reflection every 3 iterations, and max 8 retries per task. NOT for interactive multi-step planning (use feature-dev or gsd-plan-phase).
---
```

### reflect/SKILL.md
```
---
name: reflect
description: Structured post-task reflection — surprises, pattern proposals, prompt improvements, gotchas to record. Use at the end of a significant session, after a debugging marathon, or when patterns emerged that should update CLAUDE.md or .claude/rules/.
---
```

### review/SKILL.md
```
---
name: review
description: Multi-agent parallel code review with 4 reviewers (style, correctness, security, performance). Use before merging a feature branch, before committing a non-trivial change, or when a second pair of eyes is needed. Complements /validate (which checks pipeline correctness); review checks code quality.
---
```

### spec-check/SKILL.md
```
---
name: spec-check
description: Single-spec health check — verify source exists, args match source argc, run harness verify, report PASS/FAIL with diagnosis. Use when a single spec is suspected broken, after editing a spec JSON, or as a quick sanity check before adding a spec to an eval batch. For bulk spec audits use spec-auditor agent.
---
```

### validate/SKILL.md
```
---
name: validate
description: Post-session validation loop — 4 waves required before commit. Use before every git commit; pre-commit hook enforces waves 1-3. Wave 1 (schema/diff/security), Wave 2 (tests/regression/specs), Wave 3 (consistency/simplifier), Wave 4 (self-critic, optional). Writes .validation_passed sentinel on success (single-use, clears per commit).
---
```

## Verification after Part 1

```bash
grep -L "^---" /home/samyak/Desktop/parbench_sam/.claude/skills/*/SKILL.md
# Expected: empty output (no files missing frontmatter).

grep -h "^description:" /home/samyak/Desktop/parbench_sam/.claude/skills/*/SKILL.md | wc -l
# Expected: 25
```

## Commit 1

```
feat(skills): add YAML frontmatter to 20 skills for L1 discoverability

Enables description-based auto-routing for skills that previously had no
frontmatter. No body content changed.
```

Run `/validate` before committing (pre-commit hook requires waves 1–3).

---

# Part 2: Create `/navigate` Skill (~45 min)

## Directory layout to create

```
/home/samyak/Desktop/parbench_sam/.claude/skills/navigate/
├── SKILL.md           [L1 + L2 — frontmatter + reasoning loop + brief taxonomy]
├── taxonomy.md        [L3 — full table of ~100 tools, read on demand]
└── examples.md        [L3 — real user intentions mapped to tools]
```

## File 1: `.claude/skills/navigate/SKILL.md`

Write this exact content:

~~~markdown
---
name: navigate
description: Tool recommender for any ParBench session — takes freeform intent ("I want to run evals overnight on Rodinia", "debug a broken spec", "write the methodology section") and returns the top 2-3 matched skills/agents/commands across the ParBench, GSD, superpowers, and built-in ecosystems, with rationale. Use when unsure which tool to invoke next, when onboarding a new contributor, or when a task spans multiple ecosystems.
---

# Navigate: Intent → Right Tool

Takes freeform user intent and returns the best skill/agent/command(s) to use, drawn from a grounded taxonomy of this project's ~100 tools.

## When to use

- You know what you want to do but don't know which tool does it.
- Your task spans ecosystems (e.g., "plan a fix and run validation" crosses GSD + ParBench).
- Onboarding: a contributor asks "how do I X?"

## When NOT to use

- You already know the exact command — just invoke it.
- The task is pure information retrieval (use `/catchup` or read `CLAUDE.md`).
- You need Claude-model selection advice — use `/model-route` instead.

## Invocation

```
/navigate "describe what you want to do in one sentence"
```

If no argument is given, ask the user: "What are you trying to do?"

## Procedure

1. **Classify intent along 3 axes** (do this silently; do not output the classification):
   - **Phase:** orient / explore / plan / implement / verify / eval / research / paper / ops
   - **Domain:** eval-pipeline / spec-oracle / augmentation / paper / infrastructure / session-management / model-selection
   - **Scope:** single-file / multi-file / cross-cutting / overnight-batch

2. **Load taxonomy** by reading `taxonomy.md` in this skill's directory. It has 4 tables:
   - Table A: ParBench skills (25)
   - Table B: ParBench agents (14)
   - Table C: GSD commands (top 20 routing targets)
   - Table D: superpowers skills (14)

3. **Match intent to tools** using the taxonomy's "When to use" columns. Prefer tools whose description explicitly matches the intent phase + domain + scope.

4. **Return structured output** in this exact format:

   ```
   ## Recommended: `<primary tool>`
   Rationale: <one sentence — why this is the best match>
   How to invoke: <exact command or Agent call>

   ## Also consider
   - `<second tool>` — <one-line alternative rationale>
   - `<third tool>` — <one-line alternative rationale>  [omit if no good third match]

   ## Next step
   <One sentence: either invoke the primary tool now, or a clarifying question if the intent is ambiguous>
   ```

5. **If intent is ambiguous** (matches 4+ tools roughly equally): DO NOT guess. Ask ONE clarifying question using AskUserQuestion with 2–4 options drawn from the top matches. Then re-run step 3 with the answer.

6. **If no tool matches** (intent is outside this project's scope): say so explicitly — "No tool in the current setup covers this. Consider doing it manually or creating a new skill with `superpowers:writing-skills`."

## Examples (see examples.md for the full list)

| Intent | Primary | Rationale |
|--------|---------|-----------|
| "run evals overnight on Rodinia CUDA→OMP" | `/overnight-eval` | tmux isolation + pre-flight + monitoring built in |
| "debug why spec X fails" | `/fix-bug` + `/spec-check` | reproduction-first diagnosis |
| "resume after a break" | `/catchup` | 30s bootstrap briefing |
| "write paper methodology section" | `/agent-team` scenario=paper-assembly | multi-agent draft + review loop |
| "check if my changes broke anything before commit" | `/validate` | pre-commit gate waves 1–3 |

Load `examples.md` for the full 20+ intent→tool mapping if the user's intent doesn't immediately match one of the five above.

## Constraints

- Never invent a tool that doesn't exist in `taxonomy.md`. If unsure, say "I don't see a tool for this."
- Never recommend more than 3 tools (primary + 2 alternatives). More than 3 is noise.
- Output stays under ~15 lines unless the user asks for more detail.
- Don't run the recommended tool unprompted — recommend, then let the user invoke.
~~~

## File 2: `.claude/skills/navigate/taxonomy.md`

Write this exact content:

~~~markdown
# Tool Taxonomy — ParBench Claude Code Setup

Grounded reference for `/navigate`. ~100 tools across 4 ecosystems. Each row includes trigger conditions (when to use) so the matcher can route by intent.

---

## Table A: ParBench Skills (25)

All at `/home/samyak/Desktop/parbench_sam/.claude/skills/<name>/SKILL.md`.

| Slash command | Phase | When to use |
|---------------|-------|------------|
| `/creating-agent-teams` (`/agent-team`) | plan/implement | 2+ workers needing cross-talk + shared task list. NOT for independent parallel tasks |
| `/augment-test` | verify | Testing an AST transform, diagnosing transform failures |
| `/catchup` | orient | Any time you resume work after a break or start fresh |
| `/cite-check` | verify/paper | Before paper submission; after major eval runs that change numbers |
| `/dream` | ops | Memory consolidation; after 5+ sessions without it, or when stale |
| `/eval-run` | eval | Interactive eval batch, short/foreground. Use overnight-eval for >30min |
| `/feature-dev` | implement | Adding a new non-trivial feature to harness/scripts/visualizations |
| `/fix-bug` | implement | Test fails, spec breaks, unexpected eval result — reproduce-first |
| `/gen-spec` | implement | Add new benchmark suite or kernel spec |
| `/grill-research` | research | Before /overnight-eval or publishing a claim — adversarial stress-test |
| `/handoff` | ops | Write handoff doc for next session or next agent |
| `/hypothesis-tree` | research | Multi-step "why X fails" investigation with branching hypotheses |
| `/interpret-results` | eval/paper | After eval batch or /post-eval — hypothesis-first interpretation |
| `/mentoring` | research | HPC/SE/research teaching grounded in ParBench context |
| `/model-route` | ops | Selecting Opus/Sonnet/Haiku for a specific task |
| `/overnight-eval` | eval | Long eval campaigns (>30min), canonical + ablation runs |
| `/paper-review-sim` | paper | Simulate peer review of paper draft with 5 personas |
| `/post-eval` | eval | After eval batch — analyze → classify → dashboard refresh |
| `/ralph-loop` | implement | Stateless loop over N independent tasks, commit after each |
| `/reflect` | ops | Post-task reflection; record patterns to CLAUDE.md or rules |
| `/review` | verify | Multi-agent code review (style/correctness/security/perf) |
| `/spec-check` | verify | Single-spec health check — verify source + args + harness |
| `/techdebt` | verify | Scan for duplication, dead code, magic numbers (advisory) |
| `/validate` | verify | Pre-commit gate — 4-wave validation loop |
| `/workflow-ref` | orient | Static reference table for skill/agent decisions |

---

## Table B: ParBench Agents (14)

All at `/home/samyak/Desktop/parbench_sam/.claude/agents/<name>.md`. Spawn with `Agent` tool, `subagent_type=<name>`.

| Agent | Phase | When to use |
|-------|-------|------------|
| `code-simplifier` | verify/cleanup | Post-implementation: duplication, dead code, unclear names |
| `consistency-checker` | verify | Cross-check CLAUDE.md vs code; Wave 3 of /validate |
| `diff-reviewer` | verify | Review git diff for regressions and partial work; Wave 1 |
| `eval-batcher` | eval | Run eval batches with kernel eligibility rules baked in |
| `explorer` | explore | Map files, trace call chains, check coverage in ParBench |
| `plan-reviewer` | plan | Adversarial plan review — find missing assumptions/edge cases |
| `regression-checker` | verify | Compare metrics against baselines (60 Rodinia, 15 tests); Wave 2 |
| `rodinia-verifier` | verify | Run harness verify on Rodinia specs — PASS/FAIL counts |
| `security-scanner` | verify | Scan for secrets, command injection, path traversal; Wave 1 |
| `self-critic` | verify | Opus adversarial self-review of diff; Wave 4 (optional) |
| `spec-auditor` | verify | Audit spec JSONs for correctness; Wave 2 conditional |
| `test-synthesizer` | verify | Write temp test scripts for changed files; Wave 2 |
| `verification-lead` | verify | Hierarchical coordinator — spawns all 4 validation waves |
| `verify-app` | verify | Project health: schema + unit tests + spec integrity; Wave 1 |

---

## Table C: Top GSD Commands (20 of 73)

Global, at `~/.claude/skills/gsd-<name>/SKILL.md`.

| Command | When to use |
|---------|------------|
| `/gsd-do` | Freeform intent that should route to a GSD command |
| `/gsd-next` | Auto-advance to next logical step in active GSD project |
| `/gsd-progress` | Status report + route to next action (richer than gsd-next) |
| `/gsd-quick` | Small atomic task with GSD guarantees (commits, state tracking) |
| `/gsd-fast` | Trivial inline task — no subagents, no planning overhead |
| `/gsd-debug` | Systematic debugging with persistent state across context resets |
| `/gsd-plan-phase` | Create detailed PLAN.md for a phase — with verification loop |
| `/gsd-execute-phase` | Execute all plans in a phase with wave-based parallelization |
| `/gsd-discuss-phase` | Gather phase context before planning |
| `/gsd-add-todo` | Capture idea as todo from conversation context |
| `/gsd-check-todos` | List pending todos and pick one |
| `/gsd-resume-work` | Full context restoration for picking up previous session |
| `/gsd-pause-work` | Write HANDOFF.json when pausing mid-phase |
| `/gsd-review-backlog` | Review backlog parking lot, promote items to active |
| `/gsd-code-review` | Review source files changed during a phase |
| `/gsd-verify-work` | Conversational UAT on built features |
| `/gsd-ship` | Create PR, run review, prepare for merge |
| `/gsd-note` | Zero-friction idea capture |
| `/gsd-handoff` | Pause-work alias that writes context handoff |
| `/gsd-help` | List all GSD commands |

---

## Table D: Superpowers Skills (14)

Global, at `~/.claude/plugins/cache/claude-plugins-official/superpowers/`.

| Skill | When to use |
|-------|------------|
| `superpowers:using-superpowers` | Auto-fires at SessionStart; foundational skill dispatcher |
| `superpowers:brainstorming` | ANY creative work: new feature, component, behavior change |
| `superpowers:writing-plans` | Have spec/requirements for multi-step task, before code |
| `superpowers:executing-plans` | Have a written plan to execute in a session with checkpoints |
| `superpowers:subagent-driven-development` | Execute plan with independent tasks in current session |
| `superpowers:dispatching-parallel-agents` | 2+ independent tasks without shared state. NOT for team work |
| `superpowers:using-git-worktrees` | Feature work needing isolation from current workspace |
| `superpowers:test-driven-development` | Implementing any feature/bugfix before writing impl code |
| `superpowers:systematic-debugging` | Any bug/test failure/unexpected behavior — before proposing fix |
| `superpowers:verification-before-completion` | Before claiming work complete, fixed, or passing |
| `superpowers:finishing-a-development-branch` | Implementation complete, tests pass, deciding merge approach |
| `superpowers:requesting-code-review` | Completing task, implementing major feature, before merge |
| `superpowers:receiving-code-review` | Receiving feedback before implementing suggestions |
| `superpowers:writing-skills` | Creating, editing, or verifying skills |

---

## Cross-ecosystem patterns (key for /navigate matching)

**Eval pipeline governance:** `/overnight-eval` (long) or `/eval-run` (short) → `/post-eval` → `/interpret-results` → `/cite-check` (if paper-bound) + `eval-batcher` agent inside any of these.

**Spec/oracle health:** `/spec-check` (single) or `spec-auditor` agent (bulk) + `rodinia-verifier` for Rodinia-specific + `/fix-bug` when diagnosis needed.

**Session continuity:** `/catchup` (fresh/break) or `/gsd-resume-work` (active GSD phase) + `/handoff` or `/gsd-pause-work` on exit + `/dream` periodic memory consolidation.

**Parallel team work:** `/agent-team` (cross-talk needed) vs `superpowers:dispatching-parallel-agents` (independent tasks). TeamCreate is mandatory for the former per project convention.

**Pre-commit:** `/validate` waves 1–3 (required by pre-commit hook) + optionally `/review` for code quality + `/techdebt` for cleanup scan.

**Paper work:** `/agent-team` scenario=paper-assembly + `/cite-check` + `/paper-review-sim` + `/grill-research` (before claims) + `/interpret-results` (source of claims).

**Planning:** `/gsd-plan-phase` (GSD active) or `superpowers:writing-plans` (general) + `plan-reviewer` agent (adversarial) + `/gsd-discuss-phase` (context gathering first).
~~~

## File 3: `.claude/skills/navigate/examples.md`

Write this exact content:

~~~markdown
# Intent → Tool Examples

Grounded in real ParBench usage (memory files, git log, active Phase 3 work). Loaded by `/navigate` when the user's intent doesn't match one of the 5 headline examples in SKILL.md.

## Eval pipeline

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "run evals overnight on Rodinia CUDA→OMP" | `/overnight-eval rodinia cuda-to-omp` | `eval-batcher` agent |
| "run a quick eval batch interactively" | `/eval-run` | — |
| "an eval batch just finished — now what?" | `/post-eval <model>` | `/interpret-results` |
| "interpret results from the latest batch" | `/interpret-results` | `/cite-check` if paper-bound |
| "stress-test my experimental design before launch" | `/grill-research` | `superpowers:brainstorming` |
| "refresh the dashboard after new eval data" | `dashboard-refresher` agent | `/post-eval` (includes refresh) |

## Spec / oracle / benchmark

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "a spec is broken — fix it" | `/fix-bug` | `/spec-check`, `rodinia-verifier` |
| "check if spec X is healthy" | `/spec-check <name>` | `spec-auditor` agent for bulk |
| "audit all specs for correctness" | `spec-auditor` agent | `/validate` wave 2 |
| "add a new kernel spec" | `/gen-spec <suite>` | `superpowers:writing-plans` first |
| "test my new AST transform" | `/augment-test` | `explorer` agent for c_augmentation |
| "verify all Rodinia specs still PASS" | `rodinia-verifier` agent | `/validate` |

## Planning / implementation

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "plan a new feature" | `/feature-dev` or `/gsd-plan-phase` | `plan-reviewer` agent |
| "trivial one-line change" | `/gsd-fast` | — |
| "small atomic task with guarantees" | `/gsd-quick` | — |
| "multi-phase project work" | `/gsd-execute-phase` | `/gsd-discuss-phase` first |
| "explore an unfamiliar area of the codebase" | `explorer` agent | Glob/Grep direct (surgical) |
| "I want team-based critic loop for a plan" | `/agent-team` (advisor pattern) | `plan-reviewer` + critic |
| "build a skill for X" | `superpowers:writing-skills` | — |
| "debug systematically — where to start" | `superpowers:systematic-debugging` | `/gsd-debug` |
| "loop over N independent tasks overnight" | `/ralph-loop` | — |

## Paper / research

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "draft the methodology section" | `/agent-team` scenario=paper-assembly | — |
| "simulate peer review on the draft" | `/paper-review-sim` | `/grill-research` |
| "verify every claim traces to data" | `/cite-check` | `/interpret-results` |
| "branching investigation of a failure mode" | `/hypothesis-tree` | `superpowers:systematic-debugging` |
| "teach me the HPC/SE context of X" | `/mentoring` | — |

## Session management

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "resumed after a break — orient me" | `/catchup` | `/gsd-progress` if GSD active |
| "resume mid-phase GSD work" | `/gsd-resume-work` | `/catchup` |
| "write handoff for next session" | `/handoff` | `/gsd-pause-work` |
| "capture a stray idea" | `/gsd-note` or `/gsd-add-todo` | — |
| "consolidate memory before a break" | `/dream` | `/reflect` |
| "reflect on what I just learned" | `/reflect` | — |

## Validation / commit / review

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "verify pipeline health before commit" | `/validate` | pre-commit hook enforces waves 1–3 |
| "4-wave validation without manual orchestration" | `verification-lead` agent | `/validate` |
| "code quality review on a change" | `/review` | `code-simplifier` agent |
| "scan for tech debt" | `/techdebt` | — |
| "adversarial self-critique on my diff" | `self-critic` agent | Wave 4 of `/validate` |

## Cross-cutting / ops

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "pick the right model for this session" | `/model-route` | — |
| "what should I use for X?" (meta) | `/navigate` (this skill) | `/workflow-ref` (static table) |
| "route generic text to a GSD command" | `/gsd-do` | `/navigate` (broader scope) |
| "show me all GSD commands" | `/gsd-help` | — |
| "list pending todos and pick one" | `/gsd-check-todos` | — |
| "full git worktree isolation for a feature" | `superpowers:using-git-worktrees` | — |

## Matching rules for /navigate

1. If intent contains "overnight" or mentions >30min → prefer `/overnight-eval` over `/eval-run`.
2. If intent mentions "commit", "before push", "verify nothing broke" → `/validate`.
3. If intent mentions "resume", "coming back", "break" → `/catchup` (or `/gsd-resume-work` if `.planning/STATE.md` has paused_at).
4. If intent mentions "paper", "methodology", "reviewer", "citations" → paper-bound tool (see Paper/research table).
5. If intent mentions "parallel", "multiple agents", "2+ workers" → `/agent-team` unless explicitly independent tasks (`superpowers:dispatching-parallel-agents`).
6. If intent is a single-line/trivial change → `/gsd-fast`; small atomic → `/gsd-quick`; feature-scale → `/feature-dev` or `/gsd-plan-phase`.
~~~

## Verification after Part 2

```bash
ls -la /home/samyak/Desktop/parbench_sam/.claude/skills/navigate/
# Expected: SKILL.md, taxonomy.md, examples.md

head -4 /home/samyak/Desktop/parbench_sam/.claude/skills/navigate/SKILL.md
# Expected: starts with ---\nname: navigate\ndescription: ...\n

awk '/^description:/ {print length($0)}' /home/samyak/Desktop/parbench_sam/.claude/skills/navigate/SKILL.md
# Expected: ~400–800 chars
```

## End-to-end functional test

In the same session after creating the files, test invocation:

```
/navigate "I want to run evals overnight on Rodinia CUDA→OMP"
```

Expected output (approximately):

```
## Recommended: /overnight-eval
Rationale: Long-running batches (>30min) need tmux isolation; overnight-eval wraps pre-flight + tmux launch + monitoring.
How to invoke: /overnight-eval rodinia cuda-to-omp

## Also consider
- /eval-run — if you want interactive control and the batch is short
- eval-batcher agent — if you need custom kernel eligibility rules

## Next step
Invoke /overnight-eval now, or tell me more about the model and kernel subset.
```

Also test: `"resume after a break"` (expect `/catchup`), `"debug a broken spec"` (expect `/fix-bug` + `/spec-check`), `"write paper methodology"` (expect `/agent-team` with paper-assembly scenario).

## Commit 2

```
feat(skills): add /navigate skill with grounded tool taxonomy

New /navigate skill accepts freeform intent and recommends the best tool
across ParBench skills, agents, GSD commands, and superpowers skills.
Uses L1/L2/L3 progressive disclosure (SKILL.md + taxonomy.md + examples.md).
```

Run `/validate` before committing.

---

# Optional: Commit 3 — register `/navigate` in CLAUDE.md

Add one row to the Project Skills table in `/home/samyak/Desktop/parbench_sam/CLAUDE.md` (grep for `## Project Skills` to find the table; it's around line 115):

```markdown
| navigate | Intent → tool recommender across ParBench/GSD/superpowers | `.claude/skills/navigate/SKILL.md` |
```

Commit:

```
docs(claude): register /navigate in CLAUDE.md Project Skills table
```

---

# Out of scope (explicit non-goals)

- Refactoring the 14 large skills (>150 lines) into L2/L3 bodies — frontmatter-only in this session. Body refactor is a follow-up.
- Modifying `workflow-ref`, `gsd-do`, `using-superpowers`, or `model-route` to coordinate with `/navigate`. They coexist; no integration needed.
- Changing hooks. All existing hooks stay as-is.
- Adding new agents. `/navigate` routes to existing agents only.

---

# Pre-flight checklist for the new session

- [ ] `cd /home/samyak/Desktop/parbench_sam`
- [ ] `git status` — working tree should be clean (or only have `HANDOFF-LE-GPT54-EVAL.md` and `.mcp.json` modified, per current state)
- [ ] `source env_parbench/bin/activate`
- [ ] Confirm `.claude/skills/` exists with 25 subdirectories
- [ ] Confirm `.claude/skills/agent-team/` has 4 files (SKILL.md + 3 referenced) — reference pattern

If any checklist item fails: stop and surface to the user before proceeding.
