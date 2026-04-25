---
name: post-eval
description: Post-batch analysis pipeline that runs after an eval batch completes. Use after /eval-run or /overnight-eval finishes. Verifies results → runs analyze_eval.py → classify_pairs.py → refreshes dashboard → writes summary. Does NOT launch new eval runs.
---

# Post-Eval Pipeline

After an eval batch completes, run the full post-processing chain: analyze results,
classify translation complexity, refresh the dashboard, and generate a summary for
the paper. Inspired by Osmani's Factory Model — a deterministic pipeline where each
stage validates the previous stage's output before proceeding.

**Trigger:** When user types `/post-eval` or `/post-eval <model-name>`

## Arguments

- `$ARGUMENTS` — optional model name filter (e.g., `claude-sonnet`, `together-qwen-3.5`).
  If omitted, analyze all models in `results/evaluation/`.

## Prerequisites

- Project root: `{{PROJECT_ROOT}}`
- Venv: `source {{PROJECT_ROOT}}/env_parbench/bin/activate`
- An eval batch must have completed (result JSONs exist in `results/evaluation/`)

## Critical Rules

1. **Ground truth is result JSONs, not summaries or documentation.** Always verify claims
   against the actual JSON files on disk. `eval_summary.json` is derived — check it.
2. **KNOWN_FAIL exclusion is non-negotiable.** Exclude results where EITHER source OR
   target is a KNOWN_FAIL spec. The 8 KNOWN_FAIL specs are in `known-issues.md`.
   `analyze_eval.py` handles this (line 89-92, `EXCLUDED_SPECS`), but always verify.
3. **Never assume "all clean" without spot-checking.** Schema validation catches structural
   issues but not semantic ones (wrong verification mode, header confusion BUILD_FAILs,
   status derivation errors). Always spot-check 5-10 results manually.
4. **BUILD_FAIL is not a monolith.** Classify BUILD_FAILs into: model translation errors,
   OMP-specific errors, linker errors, header/file confusion, and uncategorized. Some
   BUILD_FAILs (header confusion) are partially attributable to prompt design, not purely
   model quality. Quantify this for the paper.
5. **Check experiment configuration explicitly.** Verify: temperature, thinking_enabled,
   max_retries (zero-shot vs self-repair), seed uniqueness, num_samples, augment_level
   correctness. Don't assume these are right — confirm from the data.
6. **KNOWN_FAIL PASS results are interesting signal.** When a KNOWN_FAIL-involved pair
   achieves PASS, note it in findings (LLM may "fix" broken source during translation).
   Still exclude from statistics.
7. **Use subagents for deep analysis.** Pipeline integrity audits benefit from parallel
   agents checking: (a) schema/field completeness, (b) pipeline status consistency,
   (c) canonical coverage, (d) ablation coverage/filter compliance, (e) anomaly detection.

## Workflow

### Step 0: Pipeline Integrity Check (NEW — run before analysis)

Before running analysis scripts, verify the harness operated correctly:

```python
# Quick integrity checks (run as inline Python or dispatch to agents)
# 1. Status consistency: overall_status matches build/run/verify status
# 2. Attempts sync: total_attempts == len(attempts), last attempt matches top-level
# 3. Config verification: temperature, thinking_enabled, max_retries, seeds
# 4. Coverage: expected pairs × samples all present
# 5. KNOWN_FAIL pollution: count results involving KNOWN_FAIL specs
```

If any check fails, report the specific issue before proceeding. Don't run
`analyze_eval.py` on data with structural integrity issues — fix first.

Write findings to `docs/eval-findings/YYYY-MM-DD-<model>-pipeline-audit.md`.

### Step 1: Verify Results Exist

```bash
source {{PROJECT_ROOT}}/env_parbench/bin/activate
cd {{PROJECT_ROOT}}

echo "=== RESULT FILES ==="
for dir in results/evaluation/*/; do
  if [ -d "$dir" ]; then
    count=$(ls "$dir"*.json 2>/dev/null | wc -l)
    echo "  $(basename $dir): $count result files"
  fi
done
```

If `$ARGUMENTS` specifies a model, verify that model's directory exists:
```bash
ls results/evaluation/$ARGUMENTS/ 2>/dev/null | head -5 || echo "ERROR: No results for model $ARGUMENTS"
```

**Gate:** If no result files exist, stop and report: "No eval results found. Run /eval-run first."

### Step 2: Run analyze_eval.py

```bash
source {{PROJECT_ROOT}}/env_parbench/bin/activate
cd {{PROJECT_ROOT}}

python3 scripts/evaluation/analyze_eval.py \
  --project-root {{PROJECT_ROOT}} \
  --write-dashboard \
  --show-gaps
```

If `$ARGUMENTS` specifies a model, add `--model <model-name>`.

**Gate:** Verify outputs were created:
```bash
ls -la results/evaluation/eval_summary.json results/evaluation/eval_summary.md 2>&1
```

If either file is missing or empty, report the error and skip downstream steps.

### Step 3: Run classify_translation_pairs.py

```bash
source {{PROJECT_ROOT}}/env_parbench/bin/activate
cd {{PROJECT_ROOT}}

python3 scripts/analysis/classify_translation_pairs.py \
  --project-root {{PROJECT_ROOT}}
```

**Gate:** Verify output:
```bash
ls -la results/evaluation/translation_complexity.csv 2>&1
wc -l results/evaluation/translation_complexity.csv
```

If the CSV is missing or has 0 rows, report and continue (complexity data is optional).

### Step 4: Refresh Dashboard

Invoke the `dashboard-refresher` agent with this prompt:

> "Refresh the ParBench dashboard at {{PROJECT_ROOT}}.
> New eval data just completed post-processing. Run generate_viz_data.py if it exists,
> then fix all hardcoded counts in visualizations/*.html.
> Canonical correct values: 60 Rodinia specs, 54/60 PASS, 6 KNOWN_FAIL.
> Check eval_results_data.js total task count matches new eval_summary.json."

**Gate:** After the agent completes, verify at least one viz file was modified:
```bash
git diff --name-only visualizations/ 2>/dev/null
```

If no viz files changed, note it (may be fine if counts didn't change).

### Step 5: Generate Summary

Read the eval summary and create a one-page report:

```bash
source {{PROJECT_ROOT}}/env_parbench/bin/activate
cd {{PROJECT_ROOT}}

# Read the summary
cat results/evaluation/eval_summary.md
```

Create the output directory and write a summary:

```bash
mkdir -p {{PROJECT_ROOT}}/docs/eval-summaries
```

Write the summary to `docs/eval-summaries/YYYY-MM-DD-<model-or-all>.md` with this structure:

```markdown
# Eval Summary: <model or "All Models">

**Date:** YYYY-MM-DD
**Source:** results/evaluation/eval_summary.json

## Overall Pass Rates

| Model | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | Total | Rate |
|-------|------|-----------|----------|-------------|-------|------|
| ...   | ...  | ...       | ...      | ...         | ...   | ...  |

## Direction Breakdown

<pass rates by translation direction, extracted from eval_summary.json>

## Complexity Breakdown

<pass rates by complexity class, if translation_complexity.csv data is available>

## Notable Findings

- <any surprising results, anomalies, or patterns>
- <kernels that flip between models>
- <new failure patterns not seen before>

## Self-Repair Statistics

- <per-model repair rates, if available from attempts[] data>

## Gaps

<any missing (kernel, model, direction, level) combinations from --show-gaps output>
```

### Step 6: Report & Suggest Next Steps

Present a concise pipeline summary:

```
=== POST-EVAL PIPELINE COMPLETE ===

Step 1: Results verified    - <N> models, <N> total result files
Step 2: analyze_eval.py     - PASS / FAIL (eval_summary.json written)
Step 3: classify_pairs.py   - PASS / FAIL / SKIP (translation_complexity.csv)
Step 4: Dashboard refresh   - PASS / FAIL / NO_CHANGES
Step 5: Summary written     - docs/eval-summaries/YYYY-MM-DD-<name>.md

Output files:
  results/evaluation/eval_summary.json
  results/evaluation/eval_summary.md
  results/evaluation/translation_complexity.csv
  visualizations/eval_results_data.js
  docs/eval-summaries/YYYY-MM-DD-<name>.md

Suggested next steps:
  [ ] Review eval_summary.md for anomalies
  [ ] Run /reflect to capture learnings
  [ ] Run /validate before committing dashboard changes
  [ ] Check if paper sections need updating with new numbers
```

## Error Handling

If any step fails:
1. Report the specific error with the command that failed and stderr output
2. Mark that step as FAIL in the final summary
3. Continue to the next step if possible (steps are mostly independent after Step 2)
4. Do NOT retry failed steps automatically — let the user decide

## Context Management

Steps 2 and 3 run as bash commands in the main session (fast, deterministic).
Step 4 uses a subagent (dashboard-refresher) to keep dashboard logic isolated.
Step 5 reads eval_summary.md (already on disk) — no deep exploration needed.

Total context cost: moderate (~2-3K tokens for script output + summary generation).
