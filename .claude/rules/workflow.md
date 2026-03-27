# Session Workflow & Patterns

> Always loaded. Defines how Claude Code should approach work in this project.
> Based on Boris Cherny's patterns and the Claude Code Operational Playbook.

## 6-Stage Session Workflow

### 1. Orient
- Check context and set model appropriately
- Review relevant `.claude/rules/` files for the task area

### 2. Explore (scale to task scope — don't front-load)
- **Skip entirely** when all target files are already known (single-file edit, doc update,
  running a known command, spec field change)
- **1 agent** for targeted tasks touching 1–3 known files where you need surrounding
  context (callers, tests, imports)
- **2–3 agents** for cross-cutting tasks where scope is uncertain or multiple subsystems
  are involved (pipeline changes, new feature, architecture decisions)
- Do NOT read files directly in main context — delegate to subagents; only summaries return
- Summarize findings before proceeding
- **Just-in-time, not just-in-case:** if a problem surfaces during implementation that
  needs broader understanding, launch an explorer agent then — not upfront "just in case"

### 3. Plan
- Enter plan mode for non-trivial changes
- Use ultrathink for complex analysis
- Get adversarial review via `plan-reviewer` agent
- **Wait for user approval before implementing**

### 4. Implement
- Work through the plan step by step
- Use subagents for independent subtasks (worktree isolation for parallel changes)
- Verify each step before moving on
- If anything breaks, STOP — re-enter plan mode and re-plan

### 5. Record
- Update CLAUDE.md or `.claude/rules/` after discovering new conventions/gotchas
- Write session notes for complex multi-step work
- "Update your CLAUDE.md so you don't make that mistake again" (Boris's rule)

### 6. Verify (Post-Session Validation Loop)
- **Run `/validate`** — full 4-wave validation loop (10+ agents, ~3 min)
- Wave 1 (parallel, ~30s): verify-app + diff-reviewer + security-scanner
- Wave 2 (parallel, ~60s): test-synthesizer + regression-checker + spec-auditor
- Wave 3 (parallel, ~45s): consistency-checker + code-simplifier
- Wave 4 (sequential, ~30s): self-critic (Opus) + plan-reviewer
- On FAIL → fix loop: plan mode → user approval → implement → re-validate (max 3 iterations)
- On PASS → `.validation_passed` sentinel written → `git commit` unblocked
- **Pre-commit hook enforces this** — `git commit` is blocked without a valid sentinel
- See `.claude/rules/validation-loop.md` for full protocol

## Skill & Agent Quick Reference

Use these at the right phase — don't skip them, don't over-invoke them.

| When | Skill / Agent | Command | What it does |
|------|--------------|---------|-------------|
| After any code/spec change | `/validate` | `/validate` (full) or `/validate quick` | 4-wave validation; writes sentinel; required before commit |
| Before merging or after multiple file changes | `/review` | `/review` | 4-agent parallel code review (style, correctness, security, perf) |
| Launching an eval batch | `/eval-run` | `/eval-run rodinia cuda-to-omp` | Param collection → pre-flight → execute → analyze |
| After eval completes OR spec count changes | `dashboard-refresher` agent | Invoke via Agent tool | Fixes hardcoded numbers in all 12 viz files |
| Starting a sprint session | `/session-start` | `/session-start 9` | Extracts prompt, checks git, verifies prerequisites |
| New benchmark suite | `/gen-spec` | `/gen-spec xsbench` | Full guided spec generation wizard |
| Bug fix workflow | `/fix-bug` | `/fix-bug "description"` | Reproduce → diagnose → fix → verify loop |
| New feature | `/feature-dev` | `/feature-dev "name"` | Explore → plan → implement → verify |

**Critical ordering:** Implement → `/review` → `/validate` → commit → push → `dashboard-refresher` (if eval or spec data changed)

## Context Management

- `/compact` at ~50% context usage (don't wait until 100%)
- `/clear` between unrelated tasks
- Subagents keep main context clean — only summaries return
- `/compact "focus on X"` for guided compression
- After 2+ corrections on same issue → `/clear` and restart with better prompt

## Memory Hygiene

Memory files are write-only by default — they grow but never get maintained.
Use `/dream` to consolidate periodically.

- **`/dream audit`** — Read-only health report (run weekly or when memory feels stale)
- **`/dream`** — Full 4-phase consolidation with user approval gate
- **`/dream prune <file>`** — Targeted cleanup of one file

### When to consolidate
- After major milestones (sprint phase completion, paper draft, eval batch)
- After 5+ sessions without consolidation
- When `/session-start` reports memory staleness
- Before long breaks (>3 days between sessions)

### Memory file conventions
- MEMORY.md: index only, <200 lines, no content — just `- [Title](file.md) — hook`
- Topic files: proper frontmatter (name, description, type)
- Prefer cross-references over duplication (point to `.claude/rules/` for canonical content)
- Convert all dates to absolute (YYYY-MM-DD) — relative dates rot immediately
- Staleness tiers: permanent (1) > active (2) > completed (3) > historical (4) > stale (5)

## Thinking Levels

| Level | When to use |
|-------|-------------|
| `think` | Simple lookups, single-file edits |
| `think hard` | Multi-file changes, debugging |
| `think harder` | Architecture decisions, complex refactors |
| `ultrathink` | Security review, complex planning, adversarial analysis |

## Model Selection

- **Plan mode** → uses Opus (deep reasoning for architecture)
- **Execution mode** → uses Sonnet (fast implementation)
- Use Haiku only for quick triage (which specs are ready? quick counts)

## Subagent Patterns

| Phase | Pattern |
|-------|---------|
| Exploration | 0–3 subagents, scaled to task uncertainty (see §2 above) |
| Planning | plan-reviewer agent for adversarial review |
| Implementation | Subagents for independent subtasks, worktree isolation |
| Verification | 2-4 subagents: correctness, edge cases, quality, integration |

## Agent Teams (Experimental)

> Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json `env`.
> Research: multi-agent outperforms single by 90% on complex queries (Anthropic),
> +81% on parallelizable tasks (Google arXiv:2512.08296).

Agent Teams spawn independent Claude Code sessions (teammates) with persistent context
windows. Unlike subagents (fire-and-forget, return summary), teammates accumulate
knowledge across many tool calls and communicate bidirectionally with each other.

### Agent Teams vs. Subagents — Decision Matrix

| Criterion | Use Subagents | Use Agent Teams |
|-----------|--------------|----------------|
| Context needs | Summary is sufficient | Must retain context across many reads |
| Communication | Report to parent only | Teammates discuss with each other |
| Task structure | Independent, structured verdict | Requires synthesis across sources |
| Duration | Quick (~30s–2min) | Extended (~5–30min per teammate) |
| Token cost | Lower (results summarized) | Higher (~Nx for N teammates) |

**Keep using subagents for:** `/validate` waves, `/review`, exploration, single-file work.
**Use agent teams for the 12 scenarios below.**

### Scenario Catalog

#### Research & Analysis (high-value, low-risk)

**1. Multi-Model Eval Deep Dive**
Each teammate reads one model's full result directory (161 JSON files for claude-sonnet,
gemini, groq; 17 for azure-gpt) and builds a complete picture: pass rate by direction,
per-kernel failure patterns, self-repair statistics, token usage. Teammates then compare
findings and surface cross-model anomalies (e.g., backprop tier inversion).
```
Create a team with 4 teammates. Each reads one model directory in results/evaluation/
and builds a full statistical summary. Then have them compare pass rates, failure
taxonomies, and per-kernel anomalies across models.
```

**2. Paper Section Assembly Line** *(inspired by ARIS Auto-Research-In-Sleep)*
One teammate processes eval data, another searches related work (WebSearch for SWE-bench,
HumanEval, TransCoder, OMPify, HPCorpus comparisons), a third reads augmentation results.
Lead synthesizes into paper sections. The ARIS project improved paper quality from
4/10 to 8.5/10 in overnight autonomous runs using this pattern.
```
Create a team with 3 teammates for SC26 paper drafting:
- Teammate 1: Read all files in results/evaluation/ and build complete data tables
- Teammate 2: Search the web for related work on LLM code translation benchmarks
- Teammate 3: Read results/augmentation/ and c_augmentation/ for methodology details
Require plan approval before they start. I'll coordinate the writing.
```

**3. Failure Root Cause Investigation** *(adversarial hypothesis testing)*
Spawn teammates each testing a different failure hypothesis. They must actively try to
disprove each other's theories — this fights anchoring bias from sequential investigation.
```
rodinia-hotspot-omp gets VERIFY_FAIL across all models. Create a team with 3 teammates:
- Teammate 1: Read the LLM translation outputs and diff against reference OMP
- Teammate 2: Check spec run args against actual argc parsing in hotspot_openmp.cpp
- Teammate 3: Build and run the reference OMP code, capture exact stdout
Have them share findings and challenge each other's explanations.
```

**4. Augmentation Baseline Audit**
Four teammates each read one phase's augmentation results (phase3, phase4, phase5,
retests), then the lead verifies the level-invariance claim (54/60 PASS at all L1-L4)
against actual data, not documentation.
```
Create a team with 4 teammates to audit augmentation results:
- Teammate 1: Read results/augmentation/phase3_*.json (3 files, per-API)
- Teammate 2: Read results/augmentation/phase4_*.json
- Teammate 3: Read results/augmentation/phase5_*.json + full_aug_results.json
- Teammate 4: Read retest_post_m9.json and retest_post_session2.json
Verify the claim that augmentation is level-invariant (54/60 PASS at all levels).
```

**5. Cross-Model Error Taxonomy Builder**
Teammates each classify failures for one model using the BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/
EXTRACTION_FAIL taxonomy, reading actual error snippets from `build_error_snippet` and
`run_stderr_snippet` fields. Lead merges into a unified taxonomy table for the paper.
```
Create a team with 4 teammates. Each reads one model's result JSONs in
results/evaluation/{model}/ and classifies every failure by: (a) error category,
(b) root cause (missing header, wrong API call, segfault, timeout), (c) which
kernels are affected. Then synthesize a cross-model error taxonomy table.
```

#### Development & Debugging (medium-value, medium-risk)

**6. Cross-Suite Spec Expansion** *(parallel exploration)*
When adding a new benchmark suite, one teammate explores sources, another reads existing
specs for pattern reference. No file overlap — each writes to its own suite directory.
```
Create a team with 2 teammates for new suite onboarding:
- Teammate 1: Explore the new suite's source tree (Makefiles, main files, verify methods)
- Teammate 2: Read 5 existing Rodinia specs + schema/spec_schema.json for conventions
Report findings so I can write the generator script.
```

**7. Harness Pipeline Debugging** *(multi-stage trace)*
The build → run → verify pipeline has three distinct failure stages. Teammates each own
one stage: one reads build logs and Makefiles, another traces run args and environment,
a third checks verify logic and reference outputs.
```
Create a team with 3 teammates to debug why {kernel} fails in the harness:
- Teammate 1: Read harness/builder.py + the spec's build commands + build error logs
- Teammate 2: Read harness/runner.py + the spec's run args + check source argc parsing
- Teammate 3: Read harness/verifier.py + the spec's verify config + reference output
Have them share findings to identify the failing stage.
```

**8. Transform Development with Parallel Testing** *(inspired by VibeCodeHPC)*
When adding a new augmentation transform, one teammate implements the transform class,
another writes unit tests, a third tests against multiple specs. VibeCodeHPC used
separate Parallelization Generators per technique + a Code Debugger.
```
Create a team with 3 teammates to add a new augmentation transform:
- Teammate 1: Implement the transform class in c_augmentation/augment_dataset.py
- Teammate 2: Write unit tests for the new transform in test_transforms.py
- Teammate 3: Test existing transforms on 5 diverse specs to establish baseline
Require plan approval from all before implementation.
```

#### Evaluation & Batch Analysis (high-value, require care)

**9. Post-Batch Analysis Pipeline** *(parallel aggregation)*
After `run_eval_batch.py` completes, analysis can be parallelized: one teammate runs
`analyze_eval.py`, another runs `classify_translation_pairs.py`, a third regenerates
dashboard data via `generate_viz_data.py`.
```
Create a team with 3 teammates for post-batch analysis:
- Teammate 1: Run analyze_eval.py and verify eval_summary.json is correct
- Teammate 2: Run classify_translation_pairs.py and check translation_complexity.csv
- Teammate 3: Run generate_viz_data.py and verify visualizations/ data files updated
Report any discrepancies between summary numbers and individual result files.
```

**10. Multi-Direction Eval Comparison**
With 11 translation directions, each teammate analyzes 2-3 directions and identifies
direction-specific patterns (e.g., "omp-to-cuda is harder than cuda-to-omp because...").
```
Create a team with 3 teammates to analyze translation directionality:
- Teammate 1: Read all cuda-to-omp and omp-to-cuda results, compare asymmetry
- Teammate 2: Read all cuda-to-opencl and opencl-to-cuda results
- Teammate 3: Read all omp-to-opencl and opencl-to-omp results
For each direction pair, report: pass rate difference, which kernels flip, why.
```

**11. Augmentation Level Impact Study**
Each teammate reads results at one augmentation level (L0-L4) across all models and
reports how augmentation affects pass rates. Lead synthesizes the augmentation curve.
```
Create a team with 3 teammates to analyze augmentation level impact:
- Teammate 1: Compare L0 vs L1 results across all models (read *-L0.json, *-L1.json)
- Teammate 2: Compare L2 vs L3 results across all models
- Teammate 3: Compare L3 vs L4 results and identify the saturation point
Build the augmentation-effectiveness curve for the SC26 paper.
```

#### Long-Running Autonomous Workflows (advanced)

**12. Overnight Eval Analysis Sprint** *(inspired by Anthropic's long-running Claude)*
Deploy a team inside tmux on the GPU machine. One teammate runs the eval batch, others
begin pre-analysis of completed results as they stream in. Anthropic used this pattern
for multi-day Boltzmann solver implementations with git commits per unit of work.
```
Create a team with 2 teammates in tmux for overnight eval:
- Teammate 1: Run the eval batch (run_eval_batch.py) and report progress
- Teammate 2: As results appear in results/evaluation/, begin aggregating stats
I'll check in periodically. Write progress to docs/overnight_log.md.
```

### Cost Control Guidelines

| Team Size | Token Multiplier | When to Use |
|-----------|-----------------|-------------|
| Lead + 1 teammate | ~2x | Simple comparison tasks |
| Lead + 2 teammates | ~3x | Most analysis scenarios |
| Lead + 3 teammates | ~4x | Multi-model analysis, paper drafting |
| Lead + 4+ teammates | ~5x+ | Rare; only for 4-model comparison |

- **Default teammate model:** Tell lead "Use Sonnet for teammates" for data-gathering work
- **Reserve Opus for:** Lead's synthesis, paper drafting, adversarial review
- **Kill early:** If a teammate finishes its analysis, shut it down rather than letting it idle

### Controls Cheat Sheet

| Action | How |
|--------|-----|
| Cycle through teammates | `Shift+Down` (in-process mode) |
| View a teammate's session | `Enter` on selected teammate |
| Message teammate directly | Type while viewing that teammate |
| Return to lead | `Escape` |
| Toggle shared task list | `Ctrl+T` |
| Shut down one teammate | Tell lead: "Ask {name} to shut down" |
| Clean up entire team | Tell lead: "Clean up the team" |
| Force in-process mode | `claude --teammate-mode in-process` |
| Force tmux split panes | `claude --teammate-mode tmux` |
| Require plan approval | "Spawn {name} and require plan approval" |

### Safety: All Existing Hooks Propagate

Teammates inherit every safety mechanism from project settings.json:
- `protect-benchmark-sources.sh` — blocks Edit/Write to benchmark source directories
- `pre-commit-gate.sh` — blocks commit without `.validation_passed` sentinel
- `rm -rf` blocker — blocks destructive deletions for all teammates
- `git push --force` / `git reset --hard` — denied for all teammates
- `sentinel-cleanup.sh` — any teammate's file edit invalidates validation sentinel
- Ruff auto-lint — Python files auto-linted after any teammate's edits

### Anti-Patterns for Agent Teams

1. **Don't use teams for `/validate` waves** — subagents are faster, cheaper, already structured
2. **Don't use teams for single-file edits** — teammate overhead exceeds benefit
3. **Don't let teammates edit the same file** — creates overwrite conflicts
4. **Don't run eval batches in agent team worktrees** — submodules won't initialize
5. **Don't forget to clean up** — always tell lead to "clean up the team" when done
6. **Don't scale to 4+ teammates without justification** — token costs are multiplicative

## Anti-Patterns (avoid these)

1. Don't implement without a plan — always plan first, get approval
2. Don't explore in main session — use subagents to keep context clean
3. Don't push forward when something breaks — stop and re-plan
4. Don't bundle multiple behavior changes in one session
5. Don't skip verification — always run validators and tests
6. Don't skip recording — update docs after discovering gotchas
7. Keep CLAUDE.md under 200 lines — move details to `.claude/rules/`
8. **Don't treat documentation as ground truth for code behavior.**
   `known-issues.md` and sprint docs record human observations — they can be wrong.
   The source code and test outputs are authoritative. If documentation contradicts
   source, verify against the source and update the documentation, never the reverse.
9. **Don't change spec run args without reading the actual source's argc check.**
   See Run Argument Verification Protocol in `spec-conventions.md`. This rule exists
   because of a real incident where "fixes" based on documentation caused 2 specs to
   silently fail for weeks. The evidence is always in the source and the baseline stdout.
10. **Don't commit without running `/validate`** — the pre-commit gate hook will block it
    anyway. If tempted to skip validation, that's a signal the session scope is too large.
    Split the work into smaller sessions instead of bypassing quality gates.
11. **Don't rationalize incomplete work as complete** — the self-critic agent (Opus) will
    catch it. If something isn't done, say so explicitly: "X is not yet done because Y."
    Never frame partial work as sufficient to avoid running the full validation loop.

## Atomic Task Decomposition (for multi-step plans)

When facing a large plan (fix N issues, retest, update dashboard, push):

1. **Audit first** — Evaluate what's actually done vs. claimed. Check with real data.
2. **Decompose** — Each session gets ONE objective with concrete acceptance criteria.
3. **Map dependencies** — Which sessions are sequential? Which can run in parallel?
4. **Write session plan files** — Store in `docs/session_plans/session_N_<desc>.md`. Each must include:
   - Copy-pasteable Claude Code prompt (self-contained, all context included)
   - Files reference table (paths, line numbers, current content, what changes)
   - Cross-reference sources (so the session verifies against source, not docs)
   - Verification commands with expected output
   - Commit message template
   - Troubleshooting guide for likely failures
   - Success criteria checklist
5. **`/clear` between sessions** — Fresh context for each atomic task.
6. **Gate on verification** — Don't commit until verification passes with ACTUAL data.

**Why this works:** Context management IS quality management. A session doing 1 thing well
uses all its context budget on that thing. Errors don't compound across sessions. Each
commit is one verified, complete unit of work. Independent sessions can run in parallel.

## Course Correction

When implementation goes wrong, don't keep pushing. Instead:
> "Stop. This isn't working. Re-plan from scratch knowing what we know now."

Re-enter plan mode, reassess assumptions, and get approval for the new approach.
