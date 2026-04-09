# Agent Teams for ParBench: A Complete Guide

> **Created:** 2026-03-26
> **Audience:** Samyak Jhaveri (PhD candidate, SC26 paper sprint)
> **Prerequisite:** Claude Code v2.1.32+ with the configuration changes from this session applied

---

## Table of Contents

1. [What Changed in This Session](#1-what-changed-in-this-session)
2. [Understanding Agent Teams](#2-understanding-agent-teams)
3. [Getting Started: Your First Team](#3-getting-started-your-first-team)
4. [Display Modes: In-Process vs. Split Panes](#4-display-modes-in-process-vs-split-panes)
5. [Keyboard Shortcuts & Controls Reference](#5-keyboard-shortcuts--controls-reference)
6. [The 12 ParBench Scenarios](#6-the-12-parbench-scenarios)
7. [Cost Management](#7-cost-management)
8. [Safety & Hooks](#8-safety--hooks)
9. [Quality Gate Hooks (Advanced)](#9-quality-gate-hooks-advanced)
10. [Troubleshooting](#10-troubleshooting)
11. [Known Limitations](#11-known-limitations)
12. [When NOT to Use Agent Teams](#12-when-not-to-use-agent-teams)
13. [Research References](#13-research-references)

---

## 1. What Changed in This Session

Three files were modified to enable and document Agent Teams:

| File | What Changed |
|------|-------------|
| `~/.claude/settings.json` | Added `"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}` (line 20-22) |
| `.claude/rules/workflow.md` | Added ~218-line Agent Teams section with 12 scenarios, decision matrix, controls, anti-patterns (line 123-340) |
| `CLAUDE.md` | Added 2-line pointer to workflow.md section (lines 173-174) |

**No other files were changed.** Your existing hooks, permissions, deny rules, and MCP servers
are untouched. They all propagate to teammates automatically.

### How to Verify the Setup

Start a **new** Claude Code session (the env var loads at session start):

```bash
# Option A: Start fresh outside tmux (in-process mode)
claude

# Option B: Start inside tmux (gets split panes automatically)
tmux new-session -s parbench
claude
```

Then type:

```
Can you create an agent team?
```

Claude should offer to spawn teammates. If it doesn't recognize agent teams, check that `~/.claude/settings.json` has the `env` key.

---

## 2. Understanding Agent Teams

### What Are They?

Agent Teams spawn **multiple independent Claude Code sessions** that work together. One
session is the **lead** (your main session), and it coordinates **teammates** — each of
which is a full Claude Code instance with its own context window.

### How They Differ from Subagents

ParBench already uses subagents extensively (16 custom agents, 4-wave `/validate`, parallel
`/review`). Here's the critical difference:

```
SUBAGENTS (existing):
  You ──spawn──> Agent A ──returns summary──> You
  You ──spawn──> Agent B ──returns summary──> You
  (A and B never talk to each other. Context is destroyed after return.)

AGENT TEAMS (new):
  You (Lead) ──spawn──> Teammate A ◄──messages──► Teammate B
                   ▲                                    │
                   └────── shared task list ─────────────┘
  (A and B have persistent context. They can discuss findings.)
```

### The HPC Analogy

| Parallelism Level | HPC Equivalent | ParBench Equivalent |
|-------------------|----------------|---------------------|
| Subagents | OpenMP threads (shared memory, fork-join) | `/validate` waves, `/review`, exploration |
| Agent Teams | MPI processes (message passing, persistent) | Multi-model analysis, paper drafting, debugging |
| Manual tmux | Multi-node cluster jobs (fully independent) | Long-running eval batches on GPU machine |

### Architecture

| Component | Role |
|-----------|------|
| **Team lead** | Your main Claude Code session. Creates the team, spawns teammates, coordinates. |
| **Teammates** | Separate Claude Code instances. Each has its own context window. |
| **Task list** | Shared work items. Tasks can be pending, in-progress, or completed. Tasks can have dependencies. |
| **Mailbox** | Message passing system. Teammates can message each other or broadcast to all. |

### Decision Matrix: When to Use What

| Criterion | Use Subagents | Use Agent Teams |
|-----------|--------------|----------------|
| Context needs | Summary is sufficient | Must retain context across many reads |
| Communication | Report to parent only | Teammates discuss with each other |
| Task structure | Independent, structured verdict | Requires synthesis across sources |
| Duration | Quick (~30s-2min) | Extended (~5-30min per teammate) |
| Token cost | Lower (results summarized) | Higher (~Nx for N teammates) |

**Rule of thumb:** If you can describe what you need back in one paragraph, use a subagent.
If the worker needs to read 50+ files and build a statistical picture, use a teammate.

---

## 3. Getting Started: Your First Team

### Step 1: Start Claude Code

```bash
claude
```

### Step 2: Ask for a Team

Use natural language. Be specific about what each teammate should do:

```
Create a team with 2 teammates.
Teammate 1: Read results/evaluation/eval_summary.json and summarize the pass rates by model.
Teammate 2: Read results/evaluation/eval_summary.md and summarize the tables.
Then compare their findings.
```

### Step 3: Watch the Team Work

- **In-process mode** (default outside tmux): The lead's terminal lists all teammates and
  their status. Use `Shift+Down` to cycle through them.
- **Split-pane mode** (inside tmux): Each teammate gets its own tmux pane. You can see
  everyone working simultaneously.

### Step 4: Interact with Teammates

You can message any teammate directly:

- **In-process:** Press `Shift+Down` to select a teammate, then type your message and press Enter
- **Split panes:** Click into a teammate's pane and type

### Step 5: Clean Up

When the team is done:

```
Ask all teammates to shut down, then clean up the team.
```

**Always clean up.** If you forget, orphaned tmux sessions may persist. Check with `tmux ls`.

---

## 4. Display Modes: In-Process vs. Split Panes

### Auto Mode (Default — Recommended)

Your setup uses `"auto"` mode (the default). This means:

- **Inside a tmux session** → automatic split panes (each teammate gets a pane)
- **Outside tmux** → in-process mode (all in one terminal)

### Forcing a Specific Mode

```bash
# Force in-process (all in one terminal)
claude --teammate-mode in-process

# Force tmux split panes
claude --teammate-mode tmux
```

Or set permanently in settings:

```json
// In ~/.claude/settings.json or project settings.local.json
{
  "teammateMode": "in-process"
}
```

### Which Mode to Use

| Scenario | Recommended Mode |
|----------|-----------------|
| Quick 2-teammate analysis | In-process (less overhead) |
| 3+ teammates doing extended work | Split panes via tmux |
| SSH session to GPU machine | tmux (survives disconnects) |
| Overnight eval sprint | tmux (must survive disconnects) |

### Starting in tmux for Split Panes

```bash
# Create a named tmux session
tmux new-session -s parbench-team

# Start Claude Code inside it
claude

# Now any team you create will get split panes automatically
```

---

## 5. Keyboard Shortcuts & Controls Reference

### In-Process Mode Controls

| Action | Shortcut |
|--------|----------|
| Cycle through teammates | `Shift+Down` (wraps back to lead after last) |
| View a teammate's full session | `Enter` (on selected teammate) |
| Interrupt teammate's current turn | `Escape` (while viewing) |
| Toggle the shared task list | `Ctrl+T` |
| Return to lead | `Escape` |

### Split-Pane Mode Controls

| Action | How |
|--------|-----|
| Switch to a teammate | Click into their tmux pane |
| View teammate output | Each pane shows its own session in real-time |
| Message a teammate | Click pane, type, press Enter |
| Return to lead | Click the lead's pane |

### Natural Language Commands (Tell the Lead)

| Action | What to Say |
|--------|-------------|
| Create a team | "Create a team with N teammates to [task]" |
| Specify teammate models | "Use Sonnet for each teammate" |
| Require plan approval | "Spawn [name] and require plan approval before making changes" |
| Assign a task | "Give the [task] to [teammate name]" |
| Message a specific teammate | "Tell [name] to [instruction]" |
| Broadcast to all | "Tell all teammates to [instruction]" |
| Shut down one teammate | "Ask [name] teammate to shut down" |
| Shut down all + cleanup | "Ask all teammates to shut down, then clean up the team" |
| Check progress | "What's the status of all tasks?" |
| Wait for teammates | "Wait for your teammates to complete their tasks before proceeding" |

### CLI Flags

| Flag | Description |
|------|-------------|
| `--teammate-mode <mode>` | Override mode for this session (`in-process`, `tmux`, `auto`) |
| `--dangerously-skip-permissions` | If set on lead, all teammates inherit this (use with caution) |

---

## 6. The 12 ParBench Scenarios

These are organized by risk level. **Start with Scenarios 1-5** (read-only analysis, zero risk)
before attempting write scenarios.

### Tier 1: Research & Analysis (Low Risk, High Value)

These scenarios only **read** data. No files are modified. Safe to run anytime.

---

#### Scenario 1: Multi-Model Eval Deep Dive

**What it does:** Each teammate reads one model's full result directory and builds a
comprehensive statistical summary. Then they compare findings across models.

**Your data:** 500 result JSON files across 4 model directories:
- `results/evaluation/azure-gpt-4.1/` (17 files)
- `results/evaluation/claude-sonnet-4-6/` (161 files)
- `results/evaluation/gemini-2.5-flash-lite/` (161 files)
- `results/evaluation/groq-llama-3.3-70b-versatile/` (161 files)

**Team size:** 4 teammates (one per model) | **Token cost:** ~5x

**Copy-paste this prompt:**
```
Create a team with 4 teammates. Each reads one model directory in results/evaluation/
and builds a full statistical summary: pass rate by direction, per-kernel failure
patterns, self-repair statistics (how many passed on retry), and token usage.
Then have them compare pass rates, failure taxonomies, and per-kernel anomalies
across models. Use Sonnet for teammates.
```

**What to look for in results:**
- Claude Sonnet should lead at ~70.2% pass rate
- Azure GPT at ~52.9%
- Groq at ~18.6%, Gemini at ~10.6%
- The backprop tier anomaly: Gemini passes but GPT fails (domain-specific strength)

---

#### Scenario 2: Paper Section Assembly Line

**What it does:** Parallelizes research for SC26 paper writing. One teammate processes
eval data, another finds related work via web search, a third reads augmentation methodology.

**Inspired by:** [ARIS (Auto-Research-In-Sleep)](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
which improved paper quality from 4/10 to 8.5/10 using cross-model adversarial review.

**Team size:** 3 teammates | **Token cost:** ~4x

**Copy-paste this prompt:**
```
Create a team with 3 teammates for SC26 paper research:
- Teammate 1: Read all files in results/evaluation/ including eval_summary.json,
  eval_summary.md, and batch_*.json files. Build complete data tables showing
  pass rates by model, direction, kernel, and augmentation level.
- Teammate 2: Search the web for related work on LLM code translation benchmarks.
  Find and summarize: SWE-bench, HumanEval, TransCoder, OMPify, HPCorpus.
  Focus on what metrics they use and how ParBench differs.
- Teammate 3: Read results/augmentation/ and c_augmentation/augment_dataset.py.
  Summarize the augmentation methodology: what transforms exist, how levels work,
  what the baseline results show.
Require plan approval before they start. I'll coordinate the writing.
```

---

#### Scenario 3: Failure Root Cause Investigation

**What it does:** Three teammates each investigate a different hypothesis for why a kernel
fails. They actively try to disprove each other's theories.

**Why this works:** Google's research ([arXiv 2512.08296](https://arxiv.org/abs/2512.08296))
found that adversarial hypothesis testing outperforms sequential investigation because
it prevents anchoring bias.

**Team size:** 3 teammates | **Token cost:** ~4x

**Copy-paste this prompt** (replace `{kernel}` with the actual failing kernel):
```
rodinia-srad-omp gets BUILD_FAIL across most models. Create a team with 3 teammates:
- Teammate 1: Read the LLM translation outputs in results/evaluation/claude-sonnet-4-6/
  for srad-related files. Compare the translated code to the reference OMP source
  in rodinia/rodinia-src/openmp/srad/
- Teammate 2: Read specs/rodinia-srad-omp.json and check the run args against actual
  argc parsing in the source code. Also check build commands and flags.
- Teammate 3: Read the build_error_snippet fields in ALL model results for srad.
  Categorize the errors: missing headers? Wrong API calls? Syntax errors?
Have them share findings and challenge each other's explanations.
```

---

#### Scenario 4: Augmentation Baseline Audit

**What it does:** Four teammates each read one phase of augmentation results, then
verify the level-invariance claim (54/60 PASS at all L1-L4) against actual data.

**Your data:** `results/augmentation/` contains phase3/4/5 results, retests, and master files.

**Team size:** 4 teammates | **Token cost:** ~5x

**Copy-paste this prompt:**
```
Create a team with 4 teammates to audit augmentation results:
- Teammate 1: Read results/augmentation/phase3_cuda.json, phase3_omp.json,
  phase3_opencl.json. Report per-API pass counts.
- Teammate 2: Read results/augmentation/phase4_cuda.json, phase4_omp.json,
  phase4_opencl.json. Report per-API pass counts.
- Teammate 3: Read results/augmentation/full_aug_results.json and
  rodinia_aug_results.json. Report overall pass rate and any ERROR entries.
- Teammate 4: Read results/augmentation/retest_post_m9.json and
  retest_post_session2.json. Check if every spec that PASSes at L1 also PASSes
  at L2, L3, and L4 (level-invariance verification).
Compare findings. Does the data support "54/60 PASS at all levels L1-L4"?
```

---

#### Scenario 5: Cross-Model Error Taxonomy Builder

**What it does:** Teammates classify failures for each model by reading actual error
snippets, then merge into a unified taxonomy for the paper.

**Team size:** 4 teammates | **Token cost:** ~5x

**Copy-paste this prompt:**
```
Create a team with 4 teammates for error taxonomy analysis. Each reads one model's
result JSONs in results/evaluation/{model}/:
- Teammate 1: azure-gpt-4.1/ (17 files)
- Teammate 2: claude-sonnet-4-6/ (161 files)
- Teammate 3: gemini-2.5-flash-lite/ (161 files)
- Teammate 4: groq-llama-3.3-70b-versatile/ (161 files)
For each file, extract: overall_status, build_error_snippet, run_stderr_snippet.
Classify every non-PASS result by: (a) failure stage (BUILD/RUN/VERIFY/EXTRACTION),
(b) root cause category (missing header, wrong API call, segfault, timeout, etc.),
(c) which kernels are affected.
Then synthesize a cross-model error taxonomy table.
Use Sonnet for all teammates.
```

---

### Tier 2: Development & Debugging (Medium Risk)

These scenarios may involve writing files. Use `plan approval` for safety.

---

#### Scenario 6: Cross-Suite Spec Expansion

**When to use:** Adding a new benchmark suite (beyond Rodinia/XSBench).

**Team size:** 2 teammates | **Token cost:** ~3x

**Copy-paste this prompt** (replace `{suite}` and `{path}`):
```
Create a team with 2 teammates for new suite onboarding:
- Teammate 1: Explore the {suite} source tree at {path}. Report: what kernels exist,
  what APIs (CUDA/OMP/OpenCL), what build system (Makefile flags, dependencies),
  how to verify correctness (exit codes, stdout patterns, reference outputs).
- Teammate 2: Read 5 existing Rodinia specs (rodinia-bfs-cuda.json, rodinia-hotspot-omp.json,
  rodinia-pathfinder-opencl.json, rodinia-srad-cuda.json, rodinia-backprop-omp.json) plus
  schema/spec_schema.json. Summarize the spec conventions and required fields.
Report findings so I can write the generator script. Do not write any files.
```

---

#### Scenario 7: Harness Pipeline Debugging

**When to use:** A spec fails in the build/run/verify pipeline and you don't know which stage.

**Team size:** 3 teammates | **Token cost:** ~4x

**Copy-paste this prompt** (replace `{kernel}` and `{api}`):
```
Create a team with 3 teammates to debug why rodinia-{kernel}-{api} fails:
- Teammate 1 (Build stage): Read harness/builder.py and specs/rodinia-{kernel}-{api}.json.
  Check the build commands, compiler flags, and working directory. Read any relevant
  Makefile in rodinia/rodinia-src/.
- Teammate 2 (Run stage): Read harness/runner.py and the spec's run arguments.
  Check the actual source code's argc parsing (the init() or main() function).
  Compare spec run args to what the source expects.
- Teammate 3 (Verify stage): Read harness/verifier.py and the spec's verify config.
  Check the verify_strategy (exit_code vs stdout_pattern vs numeric). Read the
  reference output if one exists.
Have them share findings to pinpoint the failing stage. Do not modify any files.
```

---

#### Scenario 8: Transform Development with Parallel Testing

**When to use:** Adding a new augmentation transform to `c_augmentation/`.

**Team size:** 3 teammates | **Token cost:** ~4x

**Copy-paste this prompt:**
```
Create a team with 3 teammates to add a new augmentation transform:
- Teammate 1: Implement the transform class in c_augmentation/augment_dataset.py
  following the pattern of existing transforms (ArithmeticTransform, SwapCondition, etc.)
- Teammate 2: Write unit tests for the new transform in c_augmentation/test_transforms.py
  following the existing test patterns.
- Teammate 3: Run the existing 15 unit tests (python3 -m pytest c_augmentation/test_transforms.py -v)
  and test augment_verify.py on 3 diverse specs to establish baseline.
Require plan approval from all teammates before they make any changes.
```

---

### Tier 3: Evaluation & Batch Analysis (Higher Value, Requires Care)

---

#### Scenario 9: Post-Batch Analysis Pipeline

**When to use:** After `run_eval_batch.py` completes a batch and you need to regenerate all analysis.

**Team size:** 3 teammates | **Token cost:** ~4x

**Copy-paste this prompt:**
```
Create a team with 3 teammates for post-batch analysis:
- Teammate 1: Run python3 scripts/evaluation/analyze_eval.py and verify that
  eval_summary.json numbers match the individual result files.
- Teammate 2: Run python3 scripts/analysis/classify_translation_pairs.py and
  verify translation_complexity.csv is up to date.
- Teammate 3: Run python3 scripts/generate_viz_data.py and verify the
  visualizations/ data files (eval_results_data.js, results_data.js) are updated.
Report any discrepancies between the summary and the raw data.
```

---

#### Scenario 10: Multi-Direction Eval Comparison

**When to use:** Analyzing translation direction asymmetry (is CUDA-to-OMP easier than OMP-to-CUDA?).

**Team size:** 3 teammates | **Token cost:** ~4x

**Copy-paste this prompt:**
```
Create a team with 3 teammates to analyze translation directionality:
- Teammate 1: Read all cuda-to-omp and omp-to-cuda result files across all models.
  Compare: which direction has higher pass rate? Which kernels pass in one direction
  but fail in the other?
- Teammate 2: Read all cuda-to-opencl and opencl-to-cuda result files.
  Same analysis: asymmetry, kernel-level flips.
- Teammate 3: Read all omp-to-opencl and opencl-to-omp result files.
  Same analysis.
For each direction pair, build a table: direction | pass_rate | kernels_that_flip | why.
Use Sonnet for all teammates.
```

---

#### Scenario 11: Augmentation Level Impact Study

**When to use:** Building the augmentation-effectiveness curve for the paper.

**Team size:** 3 teammates | **Token cost:** ~4x

**Copy-paste this prompt:**
```
Create a team with 3 teammates to analyze augmentation level impact:
- Teammate 1: Read all L0 and L1 result files (files without -L suffix are L0,
  files with -L1.json suffix are L1) across all models. Report pass rates at
  each level for each model.
- Teammate 2: Read all L2 and L3 result files. Same analysis.
- Teammate 3: Read all L3 and L4 result files. Identify if there's a saturation
  point where additional augmentation stops helping (or starts hurting).
Build a table: model | L0_rate | L1_rate | L2_rate | L3_rate | L4_rate.
```

---

### Tier 4: Long-Running Autonomous (Advanced)

---

#### Scenario 12: Overnight Eval Sprint in tmux

**When to use:** Running a multi-hour eval batch with real-time progress monitoring.

**Prerequisites:** Must be inside a tmux session on the GPU machine.

**Team size:** 2 teammates | **Token cost:** ~3x

```bash
# First, set up tmux
tmux new-session -s overnight-eval

# Start Claude Code
claude
```

**Then paste this prompt:**
```
Create a team with 2 teammates for an overnight eval run:
- Teammate 1: Run the following eval batch and report progress every 10 tasks:
  python3 scripts/evaluation/run_eval_batch.py --suite rodinia --direction cuda-to-omp
  --models claude-sonnet-4-20250514 --augment-levels 2 3 4
  --project-root /home/samyak/Desktop/parbench_sam --resume -v
- Teammate 2: Monitor results/evaluation/ for new files. As results appear,
  compute running pass rate and failure counts. Write progress updates to
  docs/overnight_eval_log.md every 15 minutes.
I'll check in periodically. Don't shut down until the batch is complete.
```

**Important:** You can detach from tmux (`Ctrl+B` then `D`) and the team keeps running.
Reattach later with `tmux attach -t overnight-eval`.

---

## 7. Cost Management

### Token Cost by Team Size

Each teammate is a full Claude Code session with its own context window.

| Configuration | Token Multiplier | Monthly Impact (rough) |
|--------------|-----------------|----------------------|
| Single session (no teams) | 1x | Baseline |
| Lead + 1 teammate | ~2x | 2x baseline |
| Lead + 2 teammates | ~3x | 3x baseline |
| Lead + 3 teammates | ~4x | 4x baseline |
| Lead + 4 teammates | ~5x | 5x baseline |

### Cost Reduction Strategies

1. **Use Sonnet for teammates, Opus for lead:**
   ```
   Create a team with 3 teammates. Use Sonnet for each teammate.
   ```
   This saves significantly — Sonnet is cheaper per token, and data-gathering teammates
   don't need Opus-level reasoning.

2. **Shut down teammates early:**
   If a teammate finishes its analysis in 3 minutes, shut it down immediately.
   Every idle second still has the context window open.
   ```
   Ask the [name] teammate to shut down.
   ```

3. **Start small, scale up:**
   Begin with Lead + 1 teammate. If you need more parallelism, add teammates
   incrementally. Don't start with 4 teammates for a task that might only need 2.

4. **Use subagents for structured tasks:**
   If you just need a summary (e.g., "count the PASS results"), a subagent is faster
   and cheaper. Reserve agent teams for tasks requiring context retention.

5. **Batch your team sessions:**
   Run one team session per analysis question. Don't keep a team alive while you
   think about what to ask next — clean up and create a new team when ready.

### When Agent Teams Are Worth the Cost

| Worth it | Not worth it |
|----------|-------------|
| Reading 161 JSON files per model (context retention) | Reading 1 file (use Read tool directly) |
| Cross-model comparison (teammates discuss) | Single-model summary (subagent) |
| Adversarial debugging (hypotheses compete) | Known-cause bug fix (single session) |
| Paper research (multiple data sources) | Doc update (single file edit) |

---

## 8. Safety & Hooks

All your existing ParBench safety hooks propagate to every teammate automatically.
You don't need to configure anything extra.

### Hooks That Protect Teammates

| Hook | What It Does | When It Fires |
|------|-------------|---------------|
| `protect-benchmark-sources.sh` | Blocks Edit/Write to `rodinia-src/`, `xsbench-src/`, `HeCBench-master/` | PreToolUse on Edit\|Write |
| `rm -rf` blocker | Blocks `rm -rf` and `rm -fr` commands | PreToolUse on Bash |
| Ruff auto-lint | Auto-fixes Python style issues after edits | PostToolUse on Edit\|Write |
| Pre-stop checklist | Shows validation checklist when stopping | Stop |

### Deny Rules (Also Propagate)

These commands are blocked for ALL teammates:
- `git push --force`
- `git reset --hard`
- `rm -rf` / `rm -fr`

### Verifying Hook Propagation

To confirm hooks are working for teammates, test with a deliberate violation:

```
Have a teammate try to edit rodinia/rodinia-src/common/make.config
```

The `protect-benchmark-sources.sh` hook should block it with an error message.

---

## 9. Quality Gate Hooks (Advanced)

Claude Code provides three team-specific hooks you can add later if needed. These are
**not configured by default** — add them to `.claude/settings.json` if you want them.

### TeammateIdle Hook

Fires when a teammate is about to go idle (finished its work). Use to send it more work
or enforce that it checked something before stopping.

```json
{
  "hooks": {
    "TeammateIdle": [
      {
        "hooks": [{
          "type": "command",
          "command": "echo 'Did you verify your findings against actual data? Check at least 3 result files.' >&2 && exit 2"
        }]
      }
    ]
  }
}
```

Exit code 2 sends the stderr message to the teammate and keeps it working.

### TaskCompleted Hook

Fires when a task is being marked complete. Use to enforce quality checks.

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [{
          "type": "command",
          "command": "echo 'Task completion blocked: run /validate quick first' >&2 && exit 2"
        }]
      }
    ]
  }
}
```

Exit code 2 prevents the task from being marked complete and sends feedback.

### TaskCreated Hook

Fires when a task is being created. Use to enforce task naming conventions.

**Note:** These hooks are optional. Start without them and add if you find teammates
cutting corners or creating poorly-defined tasks.

---

## 10. Troubleshooting

### "Agent teams not recognized"

**Symptom:** Claude doesn't offer to create a team when asked.

**Fix:** Verify the env var is set:
```bash
cat ~/.claude/settings.json | grep AGENT_TEAMS
```
Should show: `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"`

If it's there, start a **new** session (env vars load at session start).

### Teammates Not Appearing

**In in-process mode:** Teammates may be running but not visible. Press `Shift+Down` to
cycle through them.

**In split-pane mode:** Verify tmux is installed:
```bash
which tmux
```

### Lead Starts Working Instead of Delegating

Sometimes the lead starts implementing tasks itself instead of waiting for teammates.

**Fix:** Tell it explicitly:
```
Wait for your teammates to complete their tasks before proceeding.
Do not do any analysis yourself — only coordinate.
```

### Teammate Stops on Error

Teammates may stop after encountering an error instead of recovering.

**Fix:** Select the teammate (`Shift+Down` or click pane) and give additional instructions:
```
That error is expected. Skip that file and continue with the remaining files.
```

Or spawn a replacement:
```
The [name] teammate stopped. Spawn a replacement to continue its work.
```

### Tasks Appear Stuck (Dependencies Not Unblocking)

Teammates sometimes fail to mark tasks as completed, blocking dependent tasks.

**Fix:** Tell the lead:
```
Check if [task name] is actually done. If so, mark it complete and unblock the next task.
```

### Orphaned tmux Sessions

After team cleanup, check for leftover sessions:

```bash
tmux ls
```

If you see orphaned sessions:
```bash
tmux kill-session -t <session-name>
```

### Team Won't Clean Up ("Active Teammates")

Cleanup fails if teammates are still running.

**Fix:** Shut down all teammates first:
```
Ask ALL teammates to shut down. Wait for each to confirm. Then clean up the team.
```

---

## 11. Known Limitations

1. **No session resumption:** `/resume` and `/rewind` do not restore in-process teammates.
   After resuming, spawn new teammates.

2. **One team per session:** Clean up the current team before starting a new one.

3. **No nested teams:** Teammates cannot spawn their own teams.

4. **Lead is fixed:** The session that creates the team stays as lead forever. Cannot transfer.

5. **Permissions set at spawn:** All teammates inherit the lead's permissions. Can change
   individually after spawning, but not at spawn time.

6. **Slow shutdown:** Teammates finish their current tool call before shutting down.

7. **Split panes require tmux:** Not supported in VS Code integrated terminal or Windows Terminal.

8. **No worktree eval batches:** Git worktrees don't initialize submodules. The `rodinia/`
   submodule will be empty. **Never run LLM evaluations in worktrees.**

9. **Experimental status:** The feature is experimental. Behavior may change between versions.

---

## 12. When NOT to Use Agent Teams

Keep using your existing tools for these tasks:

| Task | Use Instead |
|------|-------------|
| `/validate` (4-wave validation) | Already parallelized with subagents |
| `/review` (code review) | Already parallelized with 4 subagents |
| Single-file edits | Direct editing in main session |
| Quick spec field change | Direct editing in main session |
| Running `harness verify` | Single bash command |
| Exploration (finding files) | Explore subagent or Glob/Grep tools |
| `run_eval_batch.py` (single batch) | tmux session (it's one long process) |
| Doc updates | Direct editing in main session |

**The golden rule:** If the task doesn't benefit from persistent teammate context or
inter-teammate communication, a subagent or direct tool use is faster and cheaper.

---

## 13. Research References

These papers and posts informed the design of the 12 scenarios:

| Source | Key Finding | Scenario It Informed |
|--------|-------------|---------------------|
| [Anthropic Multi-Agent System](https://www.anthropic.com/engineering/multi-agent-research-system) | Opus lead + Sonnet workers outperforms single Opus by 90.2%. Token usage explains 80% of performance. | Cost strategy: Opus lead + Sonnet teammates |
| [Google Agent Scaling (arXiv:2512.08296)](https://arxiv.org/abs/2512.08296) | +81% on parallel tasks, -39% on sequential. 87% accuracy predicting optimal architecture. | Decision matrix for when to use teams vs. subagents |
| [ARIS Auto-Research-In-Sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | Paper quality 4/10 to 8.5/10 with cross-model adversarial review overnight. | Scenario 2 (Paper Assembly Line) |
| [MARCO Multi-Agent HPC (arXiv:2505.03906)](https://arxiv.org/html/2505.03906v3) | 51.9% improvement on hard HPC problems with web-search agent. | Scenario 2 (related work via WebSearch) |
| [VibeCodeHPC (arXiv:2510.00031)](https://arxiv.org/html/2510.00031v2) | 7-agent system: 4 Parallelization Generators + PM + SE + Debugger. | Scenario 8 (Transform Development) |
| [Long-Running Claude](https://www.anthropic.com/research/long-running-Claude) | Multi-day autonomous runs with git commits per unit of work. | Scenario 12 (Overnight Eval Sprint) |
| [30 Tips for Agent Teams](https://getpushtoprod.substack.com/p/30-tips-for-claude-code-agent-teams) | 5-6 tasks per teammate optimal. Start with research tasks. | Tier progression (Tier 1 first) |
| [Academic Workflow Template](https://github.com/pedrohcgs/claude-code-my-workflow) | 10 specialized review agents + adversarial QA + quality gates. | Scenario 5 (Error Taxonomy) |

---

## Quick Start Cheat Sheet

```
                    AGENT TEAMS QUICK REFERENCE
    ┌──────────────────────────────────────────────┐
    │  START:  "Create a team with N teammates..."  │
    │  NAVIGATE: Shift+Down (cycle teammates)       │
    │  VIEW:    Enter (see teammate session)         │
    │  ESCAPE:  Escape (back to lead)                │
    │  TASKS:   Ctrl+T (toggle task list)            │
    │  STOP:    "Ask [name] to shut down"            │
    │  CLEANUP: "Clean up the team"                  │
    │  CHECK:   tmux ls (find orphaned sessions)     │
    └──────────────────────────────────────────────┘

    RECOMMENDED FIRST RUN:
    "Create a team with 2 teammates. Use Sonnet.
     Teammate 1: Read results/evaluation/eval_summary.json
     Teammate 2: Read results/evaluation/eval_summary.md
     Compare findings."
```
