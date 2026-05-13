---
name: experiment
description: >
  Generic experiment lifecycle orchestrator with reproducibility tracking and
  evolution support. Use when running any structured experiment. Integrates with
  /grill-research (pre-flight), /interpret-results (post-analysis), and
  /hypothesis-tree (evidence tracking). Subcommands — init, plan, run, evolve.
auto-activate: false
---

ultrathink

# Experiment Lifecycle Orchestrator

Use when designing, running, tracking, or evolving structured experiments.
Enforces hypothesis validation, reproducibility, and evolution tracking.
Domain-agnostic — works for LLM evals, HPC benchmarks, statistical analyses,
anything structured.

**Trigger:** When user types `/experiment` with a subcommand.

## Iron Law

```
NO EXPERIMENT WITHOUT A HYPOTHESIS. NO RUN WITHOUT A PLAN. NO EVOLUTION WITHOUT A RATIONALE.
```

## Arguments

- `$ARGUMENTS` — subcommand and parameters:
  - `init <name>` — create new experiment with directory structure + spec
  - `plan <name>` — mandatory pre-flight + batch planning (stops for approval)
  - `run <name>` — execute approved plan with reproducibility enforcement
  - `evolve <name>` — update spec with rationale + version bump
  - No argument or `help` — display usage summary

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "Just run it quick" | Pre-flight exists because poorly-designed experiments waste more time than the 5 minutes of validation |
| "I'll document the changes later" | Later never comes. The version history IS the documentation |
| "The results speak for themselves" | Results without a prior hypothesis are unfalsifiable post-hoc stories |
| "I just need to tweak one parameter" | That's an evolution. Record what changed and why, or in 3 months you won't know which version produced which results |
| "I'll add the config later" | The hook will block you. Config is written at run start, not after |

## Red Flags — STOP and Restart

- Running an experiment without completing `/grill-research` pre-flight
- Overwriting an existing run directory (runs are immutable, append-only)
- Claiming results without citing actual file paths
- Evolving a spec without stating what changed and why
- Running without user-approved plan
- Writing config.json without all reproducibility fields

If any red flag triggers: STOP. Return to the appropriate phase.

## Experiment Spec Template

When creating a new spec via `init`, use this format:

```markdown
# Experiment: <name>

## Current Version: v1 (<today's date>)

**Hypothesis:** <what you expect and why>
**Null hypothesis:** <what result would disprove your expectation>
**Parameters:**
  - <param1>: <value1>
  - <param2>: <value2>
**Metrics:** [<metric1>, <metric2>]
**Eval Script:** experiments/eval-scripts/<script>.py (or "manual")
**Parent Version:** none

## Version History

### v1 (<today's date>) — Initial design
- Created after /grill-research pre-flight
```

## Reproducibility Config Schema

Every run writes a `config.json` to its run directory. This schema is validated
by the `validate-experiment-config.sh` hook.

```json
{
  "schema_version": 1,
  "experiment_name": "...",
  "spec_version": "v1",
  "timestamp": "2026-05-12T14:30:00Z",
  "git_commit": "<current HEAD SHA>",
  "config_hash": "<SHA-256 of the spec file>",
  "seed": 42,
  "parameters": { "...copied from spec..." },
  "metrics": ["pass_rate", "build_fail_rate"],
  "eval_script": "experiments/eval-scripts/eval_baseline.py",
  "environment": {
    "python_version": "3.12.4",
    "os": "Linux 6.1"
  }
}
```

**Required fields** (hook rejects writes missing any of these):
`schema_version`, `experiment_name`, `spec_version`, `timestamp`, `git_commit`, `config_hash`, `seed`

**Recommended fields** (not hook-enforced, but should be included):
`parameters`, `metrics`, `eval_script`, `environment`

## Workflow

### Phase 1: Parse Subcommand

Extract the subcommand from `$ARGUMENTS`:
- `init` — go to Phase 2a
- `plan` — go to Phase 2b
- `run` — go to Phase 2c
- `evolve` — go to Phase 2d
- No argument or `help` — display usage summary with subcommand descriptions

### Phase 2a: `/experiment init <name>`

1. Parse the experiment name from arguments
2. Create directory structure (if `experiments/` doesn't exist yet):
   ```
   experiments/
   ├── registry.md      ← master index of all experiments
   ├── specs/            ← versioned experiment specs
   ├── runs/             ← timestamped, immutable run directories
   └── eval-scripts/     ← user-written deterministic eval scripts
   ```
3. Create `experiments/registry.md` if it doesn't exist, with header:
   ```markdown
   # Experiment Registry

   | Experiment | Current Version | Status | Last Run | Spec Path |
   |------------|----------------|--------|----------|-----------|
   ```
4. Create spec from the Experiment Spec Template at `experiments/specs/<name>.md`
5. Add entry to `experiments/registry.md`
6. **Verification gate:** Read back the spec file and confirm it was written correctly
7. Report what was created and suggest `/experiment plan <name>` as next step

### Phase 2b: `/experiment plan <name>`

1. Read the spec at `experiments/specs/<name>.md` — confirm it exists
2. **Pre-flight (MANDATORY — cannot be skipped):**
   - Invoke `/grill-research` to validate the hypothesis, null hypothesis, and success criteria
   - If user tries to skip, redirect to the Anti-Rationalization Table
   - **Verification gate:** Pre-flight must complete before proceeding
3. **Planning:** Use ultrathink to decompose the experiment into executable batches:
   - What specific commands or scripts will each batch run?
   - What inputs does each batch need?
   - What outputs does each batch produce?
   - How long will each batch take (estimate)?
   - Can batches run in parallel or must they be sequential?
4. Write plan to `experiments/runs/<YYYY-MM-DD-name-vN>/plan.md`
5. Display the plan to the user
6. **STOP for user approval** — do NOT proceed to run without explicit approval
7. **Verification gate:** Confirm plan.md was written and contains batch definitions

### Phase 2c: `/experiment run <name>`

1. Read the spec at `experiments/specs/<name>.md` — confirm it exists
2. Verify an approved plan exists (a `plan.md` in the target run directory)
3. Create the run directory if not already created by `plan`:
   `experiments/runs/<YYYY-MM-DD-name-vN>/`
4. Write `config.json` with all reproducibility fields:
   - `schema_version`: 1
   - `experiment_name`: from spec
   - `spec_version`: current version from spec
   - `timestamp`: current ISO 8601 timestamp
   - `git_commit`: current HEAD SHA (via `git rev-parse --short HEAD`)
   - `config_hash`: SHA-256 of the spec file (via `sha256sum`)
   - `seed`: from spec parameters (default 42)
   - `parameters`: copied from spec
   - `metrics`: from spec
   - `eval_script`: from spec (path or null)
   - `environment`: python version, OS
   - The `validate-experiment-config.sh` hook will validate this write
5. Execute batches from the plan:
   - For multiple independent batches: use agent team for parallel execution
   - For sequential batches: execute in order
   - Each batch writes results to the run directory
6. After all batches complete:
   - Run eval script if specified in spec (must exist at the stated path)
   - Aggregate results across batches
7. Write `report.md` with analysis summary in the run directory
8. Update `experiments/registry.md` with run date and status
9. Append entry to `EXPERIMENTS.md` ledger (if it exists at project root)
10. Suggest next steps:
    - `/interpret-results` for deep hypothesis-first analysis
    - `/hypothesis-tree update` to record evidence for/against
11. **Verification gate:** Confirm config.json and report.md exist, registry was updated

### Phase 2d: `/experiment evolve <name>`

1. Read current spec at `experiments/specs/<name>.md` — confirm it exists
2. Display current version, hypothesis, parameters, and metrics
3. Ask user: **What changed?** (one or more of: parameters, metrics, hypothesis, eval script)
4. Ask user: **Why?** (must provide rationale — "because" is not a reason)
   - If rationale is vague, push back: "What specific observation or insight prompted this change?"
5. Bump version number (v1 → v2, v2 → v3, etc.)
6. Update the spec file:
   - Update "Current Version" line with new version and today's date
   - Update "Parent Version" to the previous version
   - Update the changed fields (parameters, metrics, hypothesis, eval script)
   - Append a new entry to the Version History section:
     ```markdown
     ### vN (<today's date>) — <short description of change>
     - <what changed>
     - **Rationale:** <why it changed>
     ```
7. Update `experiments/registry.md` with new version
8. Suggest `/experiment plan <name>` to plan the next run with the updated spec
9. **Verification gate:** Read back spec, confirm version bumped and changelog appended

## The Pipeline (How Everything Connects)

```
  /hypothesis-tree add ──── "I have a hypothesis"
          │
          ▼
  /grill-research ───────── "Is it testable?"
          │
          ▼
  /experiment init ──────── "Set up the experiment"
          │
          ▼
  /experiment plan ──────── "Plan the batches" (ultrathink)
          │                    ↓ user approves plan
          ▼
  /experiment run ───────── "Run it" (agent teams)
          │                    ↓ validate-experiment-config.sh (GATE)
          │                    ↓ result-immutability hooks (GATE)
          ▼
  /interpret-results ────── "Analyze results" (hypothesis-first)
          │
          ▼
  /hypothesis-tree update ── "Update evidence"
          │
          ├──→ EXPERIMENTS.md ─── ledger entry
          ├──→ FINDINGS.md ────── distilled insight
          └──→ MEMORY.md ─────── [LEARN:tag] corrections

  ── When understanding changes: ──

  /experiment evolve ────── "Update spec + rationale"
          │
          └──→ back to /experiment plan
```

## Excluded by Design

These were considered and explicitly rejected:
- `/experiment compare` — just diff two reports manually
- `/experiment status` — just read registry.md
- `/experiment list` — just `ls experiments/specs/`
- Separate metrics registry — metrics tracked per-spec; a global registry drifts
- Per-run evolution.md — spec's version history already captures this
