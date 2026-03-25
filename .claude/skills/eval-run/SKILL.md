# Eval Batch Launcher

Launch an LLM evaluation batch with automatic parameter collection, KNOWN_FAIL
exclusion checks, API key verification, and post-batch analysis.

**Trigger:** When user types `/eval-run` with optional arguments.

## Arguments

- `$ARGUMENTS` — optional shorthand `<suite> <direction>` (e.g., `rodinia cuda-to-omp`),
  or explicit flags `--suite X --direction X --models X --levels X --kernels X`.
  Omit entirely to be prompted interactively.

## Workflow

### Phase 1: Parse & Collect

Extract parameters from `$ARGUMENTS`. Use defaults below; prompt only for missing required values.

| Parameter      | Default                    | Notes                                            |
|----------------|----------------------------|--------------------------------------------------|
| Suite          | `rodinia`                  | rodinia, xsbench                                 |
| Direction      | **(required — prompt)**    | e.g. cuda-to-omp, omp-to-cuda, cuda-to-opencl   |
| Models         | all 4 (see below)          | space-separated model IDs                        |
| Augment levels | `0`                        | space-separated ints 0–4                         |
| Kernels        | (all eligible)             | restrict only for partial re-runs                |
| Resume         | `--resume`                 | pass `--no-resume` to force re-run               |
| Max retries    | `2`                        | LLM re-attempts per task on failure              |

**Default models (Gal's 4-model directive):**
```
azure-gpt-4.1
claude-sonnet-4-6
groq-llama-3.3-70b-versatile
gemini-2.5-flash-lite
```

**Direction → eligible kernels (Rodinia):**
- `cuda-to-omp` (17): backprop bfs bptree cfd heartwall hotspot hotspot3d kmeans lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster
- `omp-to-cuda` (16): same minus kmeans (CUDA target is KNOWN_FAIL)
- `cuda-to-opencl` (17): backprop bfs bptree cfd dwt2d gaussian heartwall hotspot hotspot3d lavamd lud myocyte nn nw particlefilter pathfinder srad streamcluster
- Other directions: consult `eval-batcher` agent for eligibility

**KNOWN_FAIL — never pass these as `--kernels`:**
See `.claude/rules/known-issues.md` §"KNOWN_FAIL Specs (6)".

### Phase 2: Pre-flight

Activate venv and verify API keys for the selected models only:

```bash
source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate
cd /home/samyak/Desktop/parbench_sam

# Claude (if running claude-sonnet-4-6):
python3 -c "import os; assert os.environ.get('ANTHROPIC_API_KEY'), 'ANTHROPIC_API_KEY not set'"

# Azure (if running azure-gpt-4.1):
python3 -c "import os; assert os.environ.get('AZURE_OPENAI_API_KEY'), 'AZURE_OPENAI_API_KEY not set'"
python3 -c "import os; assert os.environ.get('AZURE_OPENAI_ENDPOINT'), 'AZURE_OPENAI_ENDPOINT not set'"

# Groq (if running groq-llama-3.3-70b-versatile):
python3 -c "import os; assert os.environ.get('GROQ_API_KEY'), 'GROQ_API_KEY not set'"

# Google (if running gemini-2.5-flash-lite):
python3 -c "import os; assert os.environ.get('GOOGLE_AI_API_KEY'), 'GOOGLE_AI_API_KEY not set'"
```

Display pre-flight summary and **wait for user confirmation before running**:

```
=== EVAL BATCH PRE-FLIGHT ===
Suite:        <suite>
Direction:    <direction>
Models:       <model1>, <model2>, ...
Levels:       L<N>, ...
Kernels:      <N> eligible  [or: restricted to <list>]
Resume:       yes / no
Max retries:  <N>
API keys:     ✓ all verified  [or: ✗ <which key missing>]
Total tasks:  <N models> × <N kernels> × <N levels> = <total>

Proceed? (yes / no / modify params)
```

If user says **modify**, re-prompt for parameters. If an API key is missing, stop and tell the user which env var to set.

### Phase 3: Execute

```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite <suite> \
  --direction <direction> \
  --models <model1> <model2> ... \
  --augment-levels <levels> \
  [--kernels <k1> <k2> ...] \
  [--no-resume] \
  --max-retries <N> \
  --project-root /home/samyak/Desktop/parbench_sam \
  -v
```

**IMPORTANT:** Always pass `--project-root` (auto-detection broken) and `--suite` (prevents cross-suite collisions).

Monitor live output. If many consecutive failures appear, surface them to the user and confirm before continuing.

### Phase 4: Analyze & Report

After batch completes, regenerate analysis and dashboard:

```bash
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --write-dashboard \
  --show-gaps \
  --expected-models <model1> <model2> ... \
  --expected-directions <direction> \
  --expected-levels <levels>
```

Display results table:

```
=== RESULTS: <suite> <direction> L<levels> ===
Model                            PASS  BUILD_FAIL  RUN_FAIL  VERIFY_FAIL  TOTAL
azure-gpt-4.1                      ?       ?           ?          ?         ?
claude-sonnet-4-6                  ?       ?           ?          ?         ?
groq-llama-3.3-70b-versatile       ?       ?           ?          ?         ?
gemini-2.5-flash-lite              ?       ?           ?          ?         ?
──────────────────────────────────────────────────────────────────────────────
TOTAL                              ?       ?           ?          ?         ?

Batch summary: results/evaluation/batch_<direction>_<timestamp>.md
Analysis:      results/evaluation/eval_summary.{json,md}
```

Surface any notable failures — especially unexpected VERIFY_FAIL or new error patterns
not seen in previous batches.

### Phase 5: Refresh Dashboard

After any eval batch that adds new result files, the dashboard hardcoded numbers go stale.
**Always invoke `dashboard-refresher` agent after Phase 4 completes:**

```
Invoke the dashboard-refresher agent with prompt:
"Refresh the ParBench dashboard at /home/samyak/Desktop/parbench_sam.
New eval data: <suite> <direction> L<levels> just completed.
Run generate_viz_data.py, then fix all hardcoded counts in visualizations/*.html.
Canonical correct values: 60 Rodinia specs, 54/60 PASS, 6 KNOWN_FAIL.
Check eval_results_data.js total task count matches new eval_summary.json."
```

Then run `/review` on any dashboard HTML edits before committing:
```
/review visualizations/
```

Commit dashboard updates as a separate commit from eval results:
- Eval results commit: `"Session N: <suite> <direction> L<levels> — N/M PASS"`
- Dashboard commit: `"Refresh dashboard: update eval counts + <suite> results"`
