---
name: eval-run
description: >
  Launch a model evaluation batch. Use for interactive/foreground eval runs — parameter
  collection, pre-flight checks, execution, and post-run analysis. For long-running
  batches that need tmux isolation, use overnight-eval instead.
---

# Eval Batch Launcher

Launch a model evaluation batch with automatic parameter collection, exclusion
checks, API key verification, and post-batch analysis.

**Trigger:** When user types `/eval-run` with optional arguments.

## Arguments

- `$ARGUMENTS` — optional shorthand or explicit flags for the eval script.
  Omit entirely to be prompted interactively.

## Workflow

### Phase 1: Parse & Collect

Extract parameters from `$ARGUMENTS`. Prompt for missing required values.

| Parameter      | Notes                                        |
|----------------|----------------------------------------------|
| Suite/dataset  | Which benchmark suite or dataset to evaluate |
| Configuration  | Model config, direction, or task variant     |
| Models         | Which models to evaluate                     |
| Samples        | Number of samples per task                   |
| Resume         | Whether to resume from previous partial run  |

### Phase 2: Pre-flight

1. Verify project environment is active (venv, dependencies)
2. Verify API keys are set for selected models
3. Verify dataset/benchmark files exist
4. Check for known-failing cases to exclude
5. Display pre-flight summary and **wait for user confirmation**

```
=== EVAL BATCH PRE-FLIGHT ===
Dataset:      <name>
Models:       <model1>, <model2>, ...
Config:       <config details>
Exclusions:   <N> known-failing cases excluded
Total tasks:  <N models> x <N tasks> = <total>
API keys:     all verified / <which missing>

Proceed? (yes / no / modify params)
```

### Phase 3: Execute

Run the evaluation script with collected parameters.
Monitor live output. If many consecutive failures appear, surface them
to the user and confirm before continuing.

### Phase 4: Analyze & Report

After batch completes:
1. Run analysis scripts to generate summary
2. Display results table (pass rates per model, failure breakdown)
3. Surface notable failures or unexpected patterns
4. Suggest next steps (dashboard refresh, commit results)

## Integration

- Pairs with `/post-eval` for full post-processing pipeline
- Pairs with `/overnight-eval` for long-running campaigns
- Pairs with `/eval-grader` for result classification
