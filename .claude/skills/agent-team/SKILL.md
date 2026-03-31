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

## CRITICAL: TeamCreate Is Required — No Exceptions

This skill MUST use **TeamCreate** to create a proper agent team. NEVER use standalone
`Agent` tool calls without the `team_name` parameter. The entire purpose of `/agent-team`
is team infrastructure: TeamCreate for setup, SendMessage for cross-talk, shared task
list, teammate lifecycle management. Standalone subagents (Agent without `team_name`)
**cannot cross-talk, do not appear as teammates, and miss all coordination benefits**.
If you find yourself about to call Agent without `team_name`, STOP — you are violating
this skill's core contract. Use TeamCreate first, then spawn teammates with `team_name`.

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
- Never hold >30K tokens of raw file content in a single teammate context.

### 3a. Context Discipline Protocol

Every teammate prompt MUST enforce these rules to prevent context rot (loading
irrelevant data that degrades reasoning quality):

**File Budget Rule:** Each teammate prompt specifies an explicit IN SCOPE and
OUT OF SCOPE list. IN SCOPE names the exact files, directories, or glob patterns
the teammate may read. OUT OF SCOPE names areas that are adjacent but irrelevant.
No open-ended "read everything in X/" instructions — always specify file patterns.

**Read Strategy — Grep-First, Range-Read Second:**
1. Use Grep to locate relevant sections/fields before reading any file.
2. Use Read with `offset` and `limit` parameters — never read an entire file >200
   lines without explicit justification in the teammate's task description.
3. When reading JSON result files, specify which fields to extract (e.g.,
   `overall_status`, `build_error_snippet`, `attempts[]`, `model_id`), not
   "read the whole file." Use Grep for field extraction where possible.

**Subagent Delegation Rule:** Bulk reads (>5 files or >500 total lines) MUST be
delegated to Explore subagents. Only summaries return to the teammate's main
context. A teammate's main context is for reasoning, not storage.

**Context Ceiling:** No teammate should hold >30K tokens of raw file content.
If approaching this limit, stop and summarize accumulated data into a structured
findings block before reading more files.

**Conditional Loading:** Only load additional context when a specific question
demands it. Do not pre-load files "just in case" they might be relevant. If a
teammate's task says "read X if needed to answer Y," the teammate should first
attempt to answer Y without X, and only load X when stuck.

**Copy-paste these rules into every teammate prompt as part of MANDATORY DIRECTIVES:**
```
## CONTEXT RULES (enforced)
- IN SCOPE: [list specific files/globs/fields]
- OUT OF SCOPE: [list adjacent but irrelevant areas]
- Grep first, then Read with line ranges. Never read >200 lines without justification.
- For JSON results: extract specific fields, don't read whole files.
- Delegate bulk reads (>5 files or >500 lines) to Explore subagents.
- Stay under 30K tokens of raw file content. Summarize before reading more.
- Only load additional files when a specific question demands it.
```

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
| claude-analyst | Claude results analyst | `results/evaluation/claude-sonnet-4-6/` | Delegate file reads to Explore subagent. Extract fields: `overall_status`, `build_error_snippet`, `run_stderr_snippet`, `attempts[]`, `model_id`, `direction`, `tokens_used`. Compute pass rate by direction, per-kernel failure patterns, self-repair stats, token usage. |
| gemini-analyst | Gemini results analyst | `results/evaluation/gemini-2.5-flash-lite/` | Same analysis and field extraction as claude-analyst for Gemini results. |
| groq-analyst | Groq results analyst | `results/evaluation/groq-llama-3.3-70b/` | Same analysis and field extraction as claude-analyst for Groq results. |
| comparator | Cross-model comparator | Read-only: analyst summaries only | After analysts report: compute deltas, identify per-kernel anomalies (e.g., backprop tier inversion), rank models by direction. Does NOT re-read result files — works from analyst summaries. |

**Context scoping per teammate:**
- **claude-analyst** — IN SCOPE: `results/evaluation/claude-sonnet-4-6/*.json` (fields: `overall_status`, `build_error_snippet`, `attempts`, `model_id`, `direction`). OUT OF SCOPE: all other model directories, `results/augmentation/`, `specs/`, `c_augmentation/`.
- **gemini-analyst** — IN SCOPE: `results/evaluation/gemini-2.5-flash-lite/*.json` (same fields). OUT OF SCOPE: all other model directories.
- **groq-analyst** — IN SCOPE: `results/evaluation/groq-llama-3.3-70b/*.json` (same fields). OUT OF SCOPE: all other model directories.
- **comparator** — IN SCOPE: summaries from the three analysts (no raw file reads). OUT OF SCOPE: all `results/evaluation/` files directly.

**Estimated cost:** ~4x token multiplier.

### `paper-assembly`

**Purpose:** Parallel data gathering for SC26 paper section drafting.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| data-processor | Eval data processor | `results/evaluation/` | Delegate per-model reads to Explore subagents. Extract fields: `overall_status`, `direction`, `kernel_name`, `attempts[]`. Build pass rates, failure taxonomy, per-kernel tiers, direction asymmetry. Output as markdown tables. |
| lit-reviewer | Related work searcher | WebSearch + `docs/` | Search for SWE-bench, HumanEval, TransCoder, LASSI, CodeRosetta, HPC-Coder-v2, OMPify, HPCorpus. Summarize each with differentiation from ParBench. |
| methods-reader | Methodology documenter | `c_augmentation/`, `results/augmentation/` | Document augmentation methodology, transform catalog, level-invariance evidence, harness pipeline stages. |

**Context scoping per teammate:**
- **data-processor** — IN SCOPE: `results/evaluation/*/*.json` (fields: `overall_status`, `direction`, `kernel_name`, `attempts`). OUT OF SCOPE: `results/augmentation/`, `specs/`, source code directories.
- **lit-reviewer** — IN SCOPE: WebSearch results, `docs/related_work/` if it exists. OUT OF SCOPE: all `results/`, `specs/`, `c_augmentation/`, source directories.
- **methods-reader** — IN SCOPE: `c_augmentation/augment_dataset.py` (transform classes only, use Grep), `results/augmentation/full_aug_results.json` (summary fields), `harness/__init__.py` (pipeline overview). OUT OF SCOPE: `results/evaluation/`, `specs/`, individual augmentation phase files (delegate to subagent if needed).

**Estimated cost:** ~3x token multiplier.

### `failure-investigation`

**Purpose:** Multi-stage pipeline debugging for a specific kernel failure.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| build-investigator | Build stage analyst | `harness/builder.py`, spec's `build` section, Makefiles in source dirs | Grep for build command construction in builder.py. Read only the spec's `build` section (not full spec). Check compiler flags and missing headers. |
| run-investigator | Run stage analyst | `harness/runner.py`, spec's `run` section, source argc parsing | Grep for arg handling in runner.py. Read spec's `run` section only. Read source's main()/init() argc check (Grep first, then targeted Read). |
| verify-investigator | Verify stage analyst | `harness/verifier.py`, spec's `verify` section, reference output | Grep for verify logic in verifier.py. Read spec's `verify` section only. Compare actual vs expected output patterns. |

**Context scoping per teammate:**
- **build-investigator** — IN SCOPE: `harness/builder.py` (Grep for build command functions), the failing spec's `build` section, Makefile in the specific source dir. OUT OF SCOPE: `harness/runner.py`, `harness/verifier.py`, `results/`, other specs.
- **run-investigator** — IN SCOPE: `harness/runner.py` (Grep for run/execute functions), the failing spec's `run` section, source file's argc/argv parsing (Grep for `argc`). OUT OF SCOPE: `harness/builder.py`, `harness/verifier.py`, `results/`, other specs.
- **verify-investigator** — IN SCOPE: `harness/verifier.py` (Grep for verify/check functions), the failing spec's `verify` section, reference output file if specified. OUT OF SCOPE: `harness/builder.py`, `harness/runner.py`, `results/`, other specs.

**Usage:** `/agent-team --scenario failure-investigation "rodinia-hotspot-omp VERIFY_FAIL"`

**Estimated cost:** ~3x token multiplier.

### `cross-model-taxonomy`

**Purpose:** Build unified failure taxonomy table across all models for the paper.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| claude-classifier | Claude failure classifier | `results/evaluation/claude-sonnet-4-6/` | Delegate file reads to Explore subagent with field filter: `overall_status`, `build_error_snippet`, `run_stderr_snippet`, `direction`, `kernel_name`. Classify non-PASS results by: error category, root cause, affected kernels. |
| gemini-classifier | Gemini failure classifier | `results/evaluation/gemini-2.5-flash-lite/` | Same field extraction and classification for Gemini results. |
| groq-classifier | Groq failure classifier | `results/evaluation/groq-llama-3.3-70b/` | Same field extraction and classification for Groq results. |
| taxonomy-synthesizer | Cross-model synthesizer | Classifier summaries only | Merge per-model classifications into unified taxonomy table. Does NOT re-read result files — works from classifier summaries. |

**Context scoping per teammate:**
- **claude-classifier** — IN SCOPE: `results/evaluation/claude-sonnet-4-6/*.json` (fields: `overall_status`, `build_error_snippet`, `run_stderr_snippet`, `direction`, `kernel_name`). OUT OF SCOPE: other model directories, `specs/`, `results/augmentation/`.
- **gemini-classifier** — IN SCOPE: `results/evaluation/gemini-2.5-flash-lite/*.json` (same fields). OUT OF SCOPE: other model directories.
- **groq-classifier** — IN SCOPE: `results/evaluation/groq-llama-3.3-70b/*.json` (same fields). OUT OF SCOPE: other model directories.
- **taxonomy-synthesizer** — IN SCOPE: summaries from the three classifiers only. OUT OF SCOPE: all `results/evaluation/` files directly.

**Estimated cost:** ~4x token multiplier.

### `post-batch-analysis`

**Purpose:** Parallel post-eval analysis pipeline after a batch completes.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| analyzer | Eval summary generator | `scripts/evaluation/analyze_eval.py`, `results/evaluation/` | Run analyze_eval.py with --write-dashboard --show-gaps. Verify eval_summary.json correctness against result file count. |
| classifier | Translation classifier | `scripts/evaluation/classify_translation_pairs.py`, `results/evaluation/` | Run classify_translation_pairs.py. Verify translation_complexity.csv output. |
| viz-refresher | Dashboard data refresher | `scripts/generate_viz_data.py`, `visualizations/` | Run generate_viz_data.py. Verify data JS files updated. Grep for hardcoded counts in HTML files. |

**Context scoping per teammate:**
- **analyzer** — IN SCOPE: `scripts/evaluation/analyze_eval.py` (Grep for CLI args), `results/evaluation/eval_summary.json` (output verification). OUT OF SCOPE: individual result JSONs (the script reads them), `visualizations/`, `c_augmentation/`.
- **classifier** — IN SCOPE: `scripts/evaluation/classify_translation_pairs.py` (Grep for CLI args), `results/evaluation/translation_complexity.csv` (output verification). OUT OF SCOPE: individual result JSONs, `visualizations/`.
- **viz-refresher** — IN SCOPE: `scripts/generate_viz_data.py` (Grep for output paths), `visualizations/*.js` (verify timestamps), `visualizations/*.html` (Grep for hardcoded counts). OUT OF SCOPE: `results/evaluation/` individual files, `scripts/evaluation/`.

**Estimated cost:** ~3x token multiplier.

### `augmentation-audit`

**Purpose:** Verify augmentation level-invariance claim against actual data.

| Teammate | Role | Scope | Task |
|----------|------|-------|------|
| phase3-reader | Phase 3 results reader | `results/augmentation/phase3_*.json` | Extract per-spec, per-level pass/fail from phase 3 files. Use Grep for `"status"` fields, then targeted Read for failures only. |
| phase4-reader | Phase 4 results reader | `results/augmentation/phase4_*.json` | Same extraction for phase 4 results. |
| phase5-reader | Phase 5 results reader | `results/augmentation/phase5_*.json`, `full_aug_results.json` | Same for phase 5. For `full_aug_results.json`: extract only `status` and `spec_id` fields per entry (file may be large). |
| retest-reader | Retest results reader | `results/augmentation/retest_post_m9.json`, `retest_post_session2.json` | Extract `status` and `spec_id` from retest files. Cross-check against phase results for consistency. |

**Context scoping per teammate:**
- **All readers** — IN SCOPE: only the specific phase files listed in their scope column (fields: `status`, `spec_id`, `level`, `error_message` for failures). OUT OF SCOPE: `results/evaluation/`, `specs/`, `c_augmentation/`, other phase files.
- **phase5-reader** — `full_aug_results.json` may be large. Grep for field names first, then Read with line ranges. Do not load the entire file.

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
- **Open-ended read instructions cause context rot:** Never give teammates
  instructions like "read all files in X/" or "read the entire directory."
  Always specify: file glob patterns, which JSON fields to extract, and line
  budgets. Open-ended reads fill context with irrelevant data and degrade
  reasoning quality on the actual task. Use the IN SCOPE / OUT OF SCOPE
  template from §3a instead.
