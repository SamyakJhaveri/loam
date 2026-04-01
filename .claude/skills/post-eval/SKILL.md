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

- Project root: `/home/samyak/Desktop/parbench_sam`
- Venv: `source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate`
- An eval batch must have completed (result JSONs exist in `results/evaluation/`)

## Workflow

### Step 1: Verify Results Exist

```bash
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

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
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
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
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

python3 scripts/analysis/classify_translation_pairs.py \
  --project-root /home/samyak/Desktop/parbench_sam
```

**Gate:** Verify output:
```bash
ls -la results/evaluation/translation_complexity.csv 2>&1
wc -l results/evaluation/translation_complexity.csv
```

If the CSV is missing or has 0 rows, report and continue (complexity data is optional).

### Step 4: Refresh Dashboard

Invoke the `dashboard-refresher` agent with this prompt:

> "Refresh the ParBench dashboard at /home/samyak/Desktop/parbench_sam.
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
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Read the summary
cat results/evaluation/eval_summary.md
```

Create the output directory and write a summary:

```bash
mkdir -p /home/samyak/Desktop/parbench_sam/docs/eval-summaries
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
