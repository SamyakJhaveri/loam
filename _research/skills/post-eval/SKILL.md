---
name: post-eval
description: >
  Post-batch analysis pipeline that runs after an eval batch completes. Use after
  /eval-run or /overnight-eval finishes. Verifies results, runs analysis scripts,
  refreshes dashboard, writes summary. Does NOT launch new eval runs.
auto-activate: false
---

# Post-Eval Pipeline

After an eval batch completes, run the full post-processing chain: verify results,
analyze, classify, refresh dashboard, and generate a summary. Each stage validates
the previous stage's output before proceeding.

**Trigger:** When user types `/post-eval` or `/post-eval <model-name>`

## Arguments

- `$ARGUMENTS` — optional model name filter. If omitted, analyze all models.

## Critical Rules

1. **Ground truth is result files, not summaries.** Always verify claims against
   the actual result files on disk.
2. **Exclusion list is non-negotiable.** Apply known-failing exclusions consistently.
3. **Never assume "all clean" without spot-checking.** Check 5-10 results manually.
4. **Classify failures granularly.** Different failure types have different root causes
   and implications for the paper.
5. **Check experiment configuration explicitly.** Don't assume parameters are correct.

## Workflow

### Step 0: Pipeline Integrity Check

Before running analysis, verify the evaluation operated correctly:
1. Status consistency across result fields
2. Configuration verification (parameters match expectations)
3. Coverage check (expected tasks all present)
4. Exclusion list applied correctly

If any check fails, report before proceeding.

### Step 1: Verify Results Exist

Count result files per model/configuration. If no results, stop.

### Step 2: Run Analysis Scripts

Execute the project's analysis pipeline. Verify outputs were created.

### Step 3: Classification (if applicable)

Run any classification or categorization scripts. Verify output.

### Step 4: Refresh Dashboard (if applicable)

Update any visualization or dashboard files with new results.

### Step 5: Generate Summary

Write a structured summary to the project's docs directory:
- Overall pass rates by model
- Configuration breakdown
- Notable findings and anomalies
- Gaps in coverage

### Step 6: Report & Suggest Next Steps

```
=== POST-EVAL PIPELINE COMPLETE ===

Step 0: Integrity check  - PASS / FAIL
Step 1: Results verified  - <N> models, <N> total files
Step 2: Analysis          - PASS / FAIL
Step 3: Classification    - PASS / FAIL / SKIP
Step 4: Dashboard         - PASS / FAIL / NO_CHANGES
Step 5: Summary written   - <path>

Suggested next steps:
  [ ] Review summary for anomalies
  [ ] Run /validate before committing
  [ ] Update paper sections if relevant
```

## Error Handling

If any step fails:
1. Report the specific error
2. Mark that step as FAIL
3. Continue to next step if possible (steps are mostly independent after Step 2)
4. Do NOT retry automatically — let the user decide
