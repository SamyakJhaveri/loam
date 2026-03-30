# Agent Team Creator

Create and launch an agent team following Samyak's standard operating procedures.
Enforces ultrathink, context management, decision-maker protocol, and anti-rot in
every teammate prompt.

**Trigger:** When user types `/agent-team <task-description>` or `/agent-team`.

## Arguments

- `$ARGUMENTS` — Free-text description of the task the team should accomplish.
  If omitted, ask the user what the team should do.
- `--scenario <name>` — Use a pre-built scenario template (see Scenario Templates
  section below). Skips Phase 2 (team design) and uses the template's teammate
  definitions. Still requires user approval before launching.
  Valid scenarios: `multi-model-eval`, `paper-assembly`, `failure-investigation`,
  `cross-model-taxonomy`, `post-batch-analysis`, `augmentation-audit`.

## Samyak's Agent Team Operating Procedures (MANDATORY)

These rules apply to EVERY agent team. Embed them as `## MANDATORY DIRECTIVES` at
the top of every teammate prompt, before the task description.

### 1. Decision Authority

- **Samyak is the PRIMARY DECISION MAKER** — all significant decisions go through him.
- When ANY teammate needs clarification, guidance, or input: **pause the teammate and
  ask Samyak via the team lead**. Do not jump to conclusions or assumptions.
- Be honest, be transparent. Tell Samyak where he might be wrong.
- Present options with tradeoffs, not unilateral choices.

### 2. Thinking & Quality

- **Every teammate MUST use ultrathink** — state this explicitly in the teammate prompt.
- Use the `model: "opus"` parameter for all teammates.
- No shortcuts. Read the file before editing. Understand the code before changing it.
- Verify before reporting done — run validators, tests, or checks as appropriate.

### 3. Context Management (Anti-Rot Protocol)

- Each teammate must be **conservative and conditional about context usage**.
- Delegate bulk reads to subagents — do not load large files into main teammate context.
- Write findings incrementally to durable files (survive compaction).
- Cross-reference facts against 2+ sources before stating them.
- Never hold >50K tokens of raw content in a single teammate context.

### 4. Skill & Agent Reuse

- Teammates should use pre-made agents (`explorer`, `eval-batcher`, `spec-auditor`,
  `plan-reviewer`, `self-critic`, `consistency-checker`, `rodinia-verifier`,
  `paper-drafter`) rather than doing everything from scratch.
- Use existing skills (`/validate`, `/review`, `/eval-run`) when appropriate.

### 5. Team Structure Standards

- **Always include a planner** — plans first, gets user approval before implementation.
- **Always include a critic** — adversarial review of all changes before finalizing.
- **Plan-then-execute** — no edits until the plan is approved by Samyak.
- Critic reviews everything at the end for accuracy, stale claims, consistency.

### 6. Communication Protocol

- Team lead aggregates findings and presents to Samyak — teammates don't spam.
- Use TaskCreate/TaskUpdate to track progress visibly.
- When a teammate finishes, they report to team lead, not directly to user.
- If blocked, escalate to team lead immediately with the specific blocker.

## Workflow

### Phase 1: Understand the Task

1. Parse `$ARGUMENTS` to understand what the team should accomplish.
2. If the task is unclear or ambiguous, ask Samyak for clarification.
3. Identify the files, systems, and scope involved.

### Phase 2: Design the Team

1. Determine the minimum number of teammates needed (prefer fewer, focused teammates).
2. For each teammate, define:
   - **Name** — descriptive, lowercase-with-hyphens
   - **Role** — one sentence
   - **Scope** — specific files/areas they own (no overlap between teammates)
   - **Agent type** — match to available tools needed (general-purpose for edits, Explore for read-only, etc.)
3. Present the team design to Samyak for approval:
   ```
   ## Proposed Team: <team-name>

   | Teammate | Role | Scope | Agent Type |
   |----------|------|-------|------------|
   | planner  | ... | ... | general-purpose |
   | ...      | ... | ... | ... |
   | critic   | ... | ... | Explore |

   Estimated token cost: ~Nx for N teammates
   ```
4. **Wait for Samyak's approval** — do not create the team until approved.

### Phase 3: Create and Launch

1. Create the team with TeamCreate.
2. Create tasks with TaskCreate for each unit of work.
3. Spawn teammates with Agent tool, each with:
   - The MANDATORY DIRECTIVES section at the top of their prompt
   - Their specific task description
   - `model: "opus"` parameter
   - `team_name` parameter
4. Manage teammate lifecycle:
   - Assign tasks as teammates become available
   - Aggregate results from teammates
   - Escalate decisions to Samyak
   - Shut down teammates when done

### Phase 4: Quality Gate

1. Critic teammate reviews ALL changes made by other teammates.
2. Present critic's findings to Samyak.
3. If critic finds issues: fix loop (plan fix, get approval, implement, re-review).
4. Final report to Samyak with:
   - What was done
   - What decisions were made
   - What files were changed
   - Any open items or concerns

## Customization

The user can modify this skill's behavior per invocation:
- `/agent-team monitor qwen results` — task is "monitor qwen results"
- `/agent-team --teammates 3` — override default teammate count
- `/agent-team --no-critic` — skip critic (for read-only/exploratory tasks)
- `/agent-team --fast` — skip plan approval step (for urgent tasks)

The user can also edit this SKILL.md directly to change default behaviors.

## Scenario Templates

Pre-built team configurations for common ParBench workflows. Use with
`/agent-team --scenario <name>` to skip the design phase and launch immediately
(still requires user approval of the pre-filled plan).

### `multi-model-eval`

**Purpose:** Deep-dive comparison across model result directories.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| claude-analyst | Claude results analyst | `results/evaluation/claude-sonnet-4-6/` | Read all result JSONs. Compute pass rate by direction, per-kernel failure patterns, self-repair stats (attempts[]), token usage. |
| gemini-analyst | Gemini results analyst | `results/evaluation/gemini-2.5-flash-lite/` | Same analysis as claude-analyst for Gemini results. |
| groq-analyst | Groq results analyst | `results/evaluation/groq-llama-3.3-70b/` | Same analysis as claude-analyst for Groq results. |
| comparator | Cross-model comparator | Read-only across all result dirs | After analysts report: compute deltas, identify per-kernel anomalies (e.g., backprop tier inversion), rank models by direction. |

**Estimated cost:** ~4x token multiplier.

### `paper-assembly`

**Purpose:** Parallel data gathering for SC26 paper section drafting.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| data-processor | Eval data processor | `results/evaluation/` | Build complete data tables: pass rates, failure taxonomy, per-kernel tiers, direction asymmetry. Output as markdown tables. |
| lit-reviewer | Related work searcher | WebSearch + `docs/` | Search for SWE-bench, HumanEval, TransCoder, LASSI, CodeRosetta, HPC-Coder-v2, OMPify, HPCorpus. Summarize each with differentiation from ParBench. |
| methods-reader | Methodology documenter | `c_augmentation/`, `results/augmentation/`, `harness/` | Document augmentation methodology, transform catalog, level-invariance evidence, harness pipeline stages. |

**Estimated cost:** ~3x token multiplier.

### `failure-investigation`

**Purpose:** Multi-stage pipeline debugging for a specific kernel failure.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| build-investigator | Build stage analyst | `harness/builder.py`, spec's `build` section, Makefiles in source dirs | Trace build commands, check compiler flags, identify missing headers or API mismatches. |
| run-investigator | Run stage analyst | `harness/runner.py`, spec's `run` section, source argc parsing | Verify run args match source's init()/argc check. Test with reference executable. |
| verify-investigator | Verify stage analyst | `harness/verifier.py`, spec's `verify` section, reference output | Check verify config (stdout_pattern, exit_code), compare actual vs expected output. |

**Usage:** `/agent-team --scenario failure-investigation "rodinia-hotspot-omp VERIFY_FAIL"`

**Estimated cost:** ~3x token multiplier.

### `cross-model-taxonomy`

**Purpose:** Build unified failure taxonomy table across all models for the paper.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| claude-classifier | Claude failure classifier | `results/evaluation/claude-sonnet-4-6/` | Read every non-PASS result JSON. Classify by: error category (BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/EXTRACTION_FAIL), root cause (missing header, wrong API call, segfault, timeout, wrong output), affected kernels. |
| gemini-classifier | Gemini failure classifier | `results/evaluation/gemini-2.5-flash-lite/` | Same classification for Gemini results. |
| groq-classifier | Groq failure classifier | `results/evaluation/groq-llama-3.3-70b/` | Same classification for Groq results. |
| taxonomy-synthesizer | Cross-model synthesizer | Read-only across all result dirs | Merge per-model classifications into unified taxonomy table. Identify model-specific vs universal failure patterns. |

**Estimated cost:** ~4x token multiplier.

### `post-batch-analysis`

**Purpose:** Parallel post-eval analysis pipeline after a batch completes.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| analyzer | Eval summary generator | `scripts/evaluation/analyze_eval.py`, `results/evaluation/` | Run analyze_eval.py with --write-dashboard --show-gaps. Verify eval_summary.json correctness. |
| classifier | Translation classifier | `scripts/evaluation/classify_translation_pairs.py`, `results/evaluation/` | Run classify_translation_pairs.py. Verify translation_complexity.csv output. |
| viz-refresher | Dashboard data refresher | `scripts/generate_viz_data.py`, `visualizations/` | Run generate_viz_data.py. Verify all data JS files updated. Check hardcoded counts in HTML files. |

**Estimated cost:** ~3x token multiplier.

### `augmentation-audit`

**Purpose:** Verify augmentation level-invariance claim against actual data.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| phase3-reader | Phase 3 results reader | `results/augmentation/phase3_*.json` | Read all phase 3 augmentation result files. Extract per-spec, per-level pass/fail. |
| phase4-reader | Phase 4 results reader | `results/augmentation/phase4_*.json` | Same for phase 4 results. |
| phase5-reader | Phase 5 results reader | `results/augmentation/phase5_*.json`, `results/augmentation/full_aug_results.json` | Same for phase 5 + combined results. |
| retest-reader | Retest results reader | `results/augmentation/retest_post_m9.json`, `results/augmentation/retest_post_session2.json` | Read retest results. Cross-check against phase results for consistency. |

After all readers report, the lead verifies the level-invariance claim:
54/60 Rodinia PASS at all L1-L4, 6 KNOWN_FAIL excluded.

**Estimated cost:** ~4x token multiplier.

## Cost Estimation

| Team Size | Token Multiplier | When to Use |
|-----------|-----------------|-------------|
| Lead + 1 teammate | ~2x | Simple comparison tasks |
| Lead + 2 teammates | ~3x | Most analysis scenarios (paper-assembly, failure-investigation) |
| Lead + 3 teammates | ~4x | Multi-model analysis (multi-model-eval, cross-model-taxonomy) |
| Lead + 4+ teammates | ~5x+ | Rare; only for augmentation-audit or 4+ model comparison |

All teammates use Opus. Fast mode only for implementation-heavy teammates, never
for research or analysis.

## Known Limitations

- **Delegate mode bug:** Agent teammates spawned in delegate mode may not receive
  all tool results correctly. If a teammate reports "tool call failed" or returns
  incomplete data, retry with in-process mode (`claude --teammate-mode in-process`).
- **Git worktrees + submodules:** Teammates running in worktrees cannot access
  Rodinia/XSBench sources (submodule not initialized). Never run eval-related
  teammates in worktrees.
- **File conflict risk:** Two teammates editing the same file will overwrite each
  other. The scenario templates above are designed with non-overlapping scopes to
  prevent this. If creating custom teams, explicitly assign file ownership.
- **Context window pressure:** Each teammate has its own context window, but
  large result directories (160+ JSON files) can exhaust it. Teammates should
  use subagents for bulk reads and only retain summaries in their main context.
