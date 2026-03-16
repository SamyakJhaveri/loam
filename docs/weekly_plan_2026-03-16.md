# ParBench Weekly Development Plan — 2026-03-16 to 2026-03-22

> **Goal:** Build the LLM evaluation pipeline, run SOTA model experiments, and start the SC26 paper.
> **How to use:** Feed each task block to Claude Code as a prompt. Tasks are ordered — complete them sequentially unless marked parallel.

---

## Prerequisites (Manual — Do Before Starting)

- [ ] Set `PAGES_PASSWORD` GitHub secret: repo Settings → Secrets → Actions → New secret
- [ ] Set env vars: `export ANTHROPIC_API_KEY=...` and `export OPENAI_API_KEY=...`
- [ ] Message Erel: "erel/aug is 26 commits behind main with 0 ahead — do you have unpushed work? If not I'll archive. Also please create the Overleaf and share the link."
- [ ] Message Gal: status update — curation complete, augmentation integrated (L2 recommended), 6 missing codes identified, starting SOTA model testing this week

---

## Task 1: Refresh Visualization Data

**Prompt for Claude Code:**

```
Activate the venv and run `python3 scripts/generate_viz_data.py` to refresh
the visualization JS data files from the latest augmentation results.
Then commit the updated files with message: "Refresh visualization data (2026-03-16)"
```

**Expected output:** Updated `visualizations/results_data.js` and `build_results_data.js`

---

## Task 2: Create LLM Evaluation Script — Single Spec

**Prompt for Claude Code:**

```
Create `scripts/evaluation/llm_evaluate.py` — an LLM-based code translation
evaluation script for ParBench.

## What it does

Given a source spec and target spec, it:
1. Loads both specs
2. Extracts source code via `harness.spec_loader.get_prompt_payload()`
3. Loads the target spec to know what files to produce and how to build/verify
4. Builds a translation prompt and sends it to an LLM (Claude or GPT)
5. Extracts code blocks from the LLM response
6. Backs up original target files, writes LLM output in their place
7. Runs `harness.builder.build_spec()` and `harness.runner.run_spec()` and
   `harness.verifier.verify_run()` on the target spec
8. Restores original files from backup
9. Saves results to `results/evaluation/{model}/{source_id}-to-{target_id}.json`

## CLI interface

python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model claude-sonnet-4-20250514 \
  --augment-level 0 \
  --project-root /home/samyak/Desktop/parbench_sam \
  -v

## Model adapters

Support two providers via a simple adapter pattern:
- `claude-*` models → use `anthropic` SDK (`ANTHROPIC_API_KEY` env var)
- `gpt-*` or `o1-*` or `o3-*` models → use `openai` SDK (`OPENAI_API_KEY` env var)

Max tokens: 16384 for response. Temperature: 0.

## Prompt template

System message:
"You are a parallel programming expert. Translate the provided {source_api}
code to {target_api}. Output ONLY the translated code. For each file, output
a markdown code fence with the filename on the opening line like:
```{language} filename={filename}
Preserve the algorithm, I/O behavior, and output format exactly."

User message should include:
- Kernel name and description from metadata
- Source API and target API
- List of target files needed (from target spec's prompt_payload)
- The target spec's build command (so LLM knows constraints)
- All source code files with clear delimiters

## Code extraction

Parse the LLM response to extract code blocks. Look for fenced code blocks
with `filename=X` on the opening line. If that fails, fall back to matching
filenames mentioned before code blocks. If only one target file is needed and
one code block exists, use that.

## File management

- Before writing LLM output: copy each original target file to `{file}.parbench_bak`
- After verify (pass or fail): restore from `.parbench_bak` and delete backups
- Use try/finally to ensure restore always happens

## Result JSON format

{
  "source_spec": "rodinia-bfs-cuda",
  "target_spec": "rodinia-bfs-omp",
  "model": "claude-sonnet-4-20250514",
  "augment_level": 0,
  "timestamp": "2026-03-17T10:30:00Z",
  "prompt_tokens": 1234,
  "completion_tokens": 567,
  "llm_response_time_seconds": 12.3,
  "build_status": "pass",
  "build_time_seconds": 2.1,
  "run_status": "pass",
  "run_time_seconds": 0.5,
  "verify_status": "pass",
  "verify_strategy": "exit_code",
  "overall_status": "pass",
  "error_message": null,
  "translated_files": {"bfs.cpp": "...first 200 chars..."}
}

## Important details

- Always activate venv: `source env_parbench/bin/activate`
- Project root: `/home/samyak/Desktop/parbench_sam`
- Reuse harness modules: import from `harness.spec_loader`, `harness.builder`,
  `harness.runner`, `harness.verifier`, `harness.models`
- Config paths: `config/paths.json` has `downloads_root`
- Create `scripts/evaluation/__init__.py` (empty)
- Create `results/evaluation/` directory
```

**Verify after:** `python3 scripts/evaluation/llm_evaluate.py --help` should show usage.

---

## Task 3: Pilot Test — Single Translation

**Prompt for Claude Code:**

```
Run a single pilot test of the LLM evaluation pipeline:

source env_parbench/bin/activate
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam \
  -v

If it fails, debug and fix the script. Common issues to watch for:
- Code extraction: LLM may not use exact `filename=X` format
- File paths: make sure resolved paths match where files actually live
- Build command: target spec's build command must work with translated files
- Restore: original files MUST be restored even on failure

After it passes (or after fixing), run one more test in the reverse direction:
  --source specs/rodinia-bfs-omp.json --target specs/rodinia-bfs-cuda.json

Then show me both result JSONs.
```

---

## Task 4: Pilot Test — Multiple Specs and Models

**Prompt for Claude Code:**

```
Run pilot tests across 5 easy kernels × 2 directions × 2 models. These 5
kernels all have 3 passing API baselines (cuda, omp, opencl):

Kernels: bfs, hotspot, backprop, nw, srad

For each kernel, test cuda→omp translation with both models:
- claude-sonnet-4-20250514
- gpt-4o

That's 10 evaluations. Run them sequentially (not parallel — we want to debug
issues one at a time).

Use the llm_evaluate.py script from Task 2. Collect all results, then print a
summary table:

| Kernel | Direction | Claude Sonnet | GPT-4o |
|--------|-----------|---------------|--------|
| bfs | cuda→omp | PASS/FAIL | PASS/FAIL |
...

Report any failures with the error details so we can fix them.
```

---

## Task 5: Create Batch Evaluation Runner

**Prompt for Claude Code:**

```
Create `scripts/evaluation/run_eval_batch.py` — a batch runner for LLM evaluation.

## What it does

Runs llm_evaluate.py logic across multiple spec pairs and models, with
checkpointing (skips if result JSON already exists).

## CLI interface

# All Rodinia cuda→omp translations with one model
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam

# All directions for specific kernels
python3 scripts/evaluation/run_eval_batch.py \
  --kernels bfs,hotspot,srad \
  --direction all \
  --models claude-sonnet-4-20250514,gpt-4o \
  --project-root /home/samyak/Desktop/parbench_sam

# Full Rodinia evaluation
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction all \
  --models claude-sonnet-4-20250514,gpt-4o \
  --augment-levels 0,2 \
  --project-root /home/samyak/Desktop/parbench_sam

## Arguments

- `--suite`: filter by source_suite (e.g., "rodinia")
- `--kernels`: comma-separated kernel names (overrides --suite)
- `--direction`: "cuda-to-omp", "omp-to-cuda", "cuda-to-opencl", or "all"
- `--models`: comma-separated model names
- `--augment-levels`: comma-separated augment levels (default: "0")
- `--project-root`: required, path to parbench_sam
- `--resume`: skip existing results (default: true)
- `--max-failures`: stop after N consecutive failures (default: 5)
- `-v`: verbose

## Pair selection

Use `harness.spec_loader.find_translation_pairs()` to get all valid pairs,
then filter by suite/kernels/direction. Only include pairs where BOTH source
and target specs have passing baselines (check `baseline_results.configurations.correctness.status == "pass"`).

## Output

- Per-task JSONs in `results/evaluation/{model}/{source}-to-{target}.json`
- Summary JSON: `results/evaluation/{model}_summary.json`
- Summary markdown: `results/evaluation/{model}_summary.md` with pass/fail matrix

## Checkpointing

Before each evaluation, check if the result JSON exists. If --resume is true
(default), skip it. Print "[SKIP] already evaluated: ..." and move on.

## Import the evaluation logic from llm_evaluate.py

Don't duplicate — import `evaluate_translation()` from `scripts.evaluation.llm_evaluate`.
Or refactor shared code into `scripts/evaluation/core.py` if cleaner.
```

---

## Task 6: Run Full Rodinia Evaluation — Claude

**Prompt for Claude Code:**

```
Run the full Rodinia evaluation with Claude Sonnet:

source env_parbench/bin/activate
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction all \
  --models claude-sonnet-4-20250514 \
  --augment-levels 0,2 \
  --project-root /home/samyak/Desktop/parbench_sam \
  -v

This will take a while. Let it run and report the results when done.

After completion, show me:
1. The summary markdown table
2. Overall pass rates: L0 vs L2
3. Which kernels/directions consistently fail
4. Any errors or issues encountered
```

---

## Task 7: Run Full Rodinia Evaluation — GPT-4o

**Prompt for Claude Code:**

```
Run the full Rodinia evaluation with GPT-4o (same as Task 6 but different model):

source env_parbench/bin/activate
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction all \
  --models gpt-4o \
  --augment-levels 0,2 \
  --project-root /home/samyak/Desktop/parbench_sam \
  -v

After completion, show me the summary and compare with Claude results from Task 6.
```

---

## Task 8: Create Results Analyzer

**Prompt for Claude Code:**

```
Create `scripts/evaluation/analyze_eval.py` — aggregates LLM evaluation results
into reports and visualization data.

## What it does

1. Reads all JSON files from `results/evaluation/`
2. Generates:
   - `results/evaluation/eval_summary.md` — full results matrix
   - `results/evaluation/eval_summary.json` — machine-readable aggregate
   - `visualizations/eval_results_data.js` — for the dashboard

## Summary table format

### By Model (augment_level=0)
| Kernel | cuda→omp | omp→cuda | cuda→ocl | ocl→cuda | omp→ocl | ocl→omp |
|--------|----------|----------|----------|----------|---------|---------|
| bfs | C:✓ G:✓ | C:✓ G:✗ | ... | ... | ... | ... |

(C = Claude, G = GPT-4o)

### Aggregate
| Model | L0 Pass | L0 Rate | L2 Pass | L2 Rate | Total Pairs |
|-------|---------|---------|---------|---------|-------------|
| claude-sonnet | 45/90 | 50% | 42/90 | 47% | 90 |
| gpt-4o | 38/90 | 42% | 35/90 | 39% | 90 |

## CLI

python3 scripts/evaluation/analyze_eval.py \
  --results-dir results/evaluation/ \
  --output-dir results/evaluation/ \
  --viz-output visualizations/eval_results_data.js
```

---

## Task 9: Add Evaluation Dashboard to GitHub Pages

**Prompt for Claude Code:**

```
Create a new visualization page `visualizations/eval_results.html` for the
LLM evaluation results.

Follow the same pattern as existing dashboards (copy nav structure from
`visualizations/overview.html`). The page should:

1. Load `eval_results_data.js`
2. Show a heatmap/matrix: kernel × translation direction, colored by pass/fail
3. Toggle between models (Claude vs GPT-4o)
4. Toggle between augment levels (L0 vs L2)
5. Show aggregate stats (pass rates per model, per direction, per kernel)

Also add a nav link to this page in ALL existing HTML files' nav bars.

Run `python3 scripts/evaluation/analyze_eval.py` first to generate the data file,
then update the dashboard.
```

---

## Task 10: Commit and Push Everything

**Prompt for Claude Code:**

```
Review all changes made this week, then:

1. Run `python3 scripts/validate_schema.py --all` to confirm no new errors
2. Run `python3 scripts/generate_viz_data.py` to refresh all viz data
3. Stage and commit in logical groups:
   - "Add LLM evaluation pipeline (scripts/evaluation/)"
   - "Add evaluation results for Claude Sonnet and GPT-4o"
   - "Add evaluation dashboard and refresh visualization data"
4. Push to main
5. Verify GitHub Pages deployment triggered
```

---

## Task 11 (Stretch): Start SC26 Paper Sections

**Prompt for Claude Code:**

```
Based on the ParBench project, draft the following SC26 paper sections as
markdown files in `docs/paper/`:

1. `docs/paper/01_introduction.md` — Motivation for ParBench (LLM code
   translation needs benchmarks, existing benchmarks don't cover parallel code)
2. `docs/paper/03_benchmark_corpus.md` — Survey of 35 repos, 656 kernels,
   selection of Rodinia (60 specs) and HeCBench (120 specs). Draw from
   `presentations/ParBench_Speaking_Notes.md` and `analysis/reports/`.
3. `docs/paper/06_evaluation.md` — Baseline results (augmentation pass rates)
   and LLM translation results from this week's experiments.

Use the actual data from `results/` — don't make up numbers. Include tables
and figure placeholders. These will be transferred to Overleaf LaTeX later.
```

---

## Quick Reference

| Item | Path |
|------|------|
| Evaluation script | `scripts/evaluation/llm_evaluate.py` |
| Batch runner | `scripts/evaluation/run_eval_batch.py` |
| Results analyzer | `scripts/evaluation/analyze_eval.py` |
| Per-task results | `results/evaluation/{model}/{src}-to-{tgt}.json` |
| Summary report | `results/evaluation/eval_summary.md` |
| Dashboard | `visualizations/eval_results.html` |
| Paper drafts | `docs/paper/` |

## Harness Commands (reference)

```bash
# Always activate venv first
source env_parbench/bin/activate

# Extract what LLM sees
python3 -m harness prompt specs/rodinia-bfs-cuda.json

# With augmentation
python3 -m harness prompt specs/rodinia-bfs-cuda.json --augment_level 2

# Full build/run/verify
python3 -m harness -v verify specs/rodinia-bfs-cuda.json

# List all translation pairs
python3 -m harness pairs

# Validate specs
python3 scripts/validate_schema.py --all
```

## 17 Good Candidate Kernels (2+ passing APIs)

```
backprop:  cuda ✓  omp ✓  opencl ✓
bfs:       cuda ✓  omp ✓  opencl ✓
bptree:    cuda ✓  omp ✓  opencl ✓
dwt2d:     cuda ✓         opencl ✓
gaussian:  cuda ✓         opencl ✓
heartwall: cuda ✓  omp ✓  opencl ✓
hotspot:   cuda ✓  omp ✓  opencl ✓
hotspot3d: cuda ✓  omp ✓  opencl ✓
lavamd:    cuda ✓  omp ✓  opencl ✓
lud:       cuda ✓  omp ✓  opencl ✓
myocyte:   cuda ✓  omp ✓  opencl ✓
nn:        cuda ✓  omp ✓  opencl ✗
nw:        cuda ✓  omp ✓  opencl ✓
particlefilter: cuda ✓ omp ✓ opencl ✓
pathfinder: cuda ✓ omp ✓  opencl ✗
srad:      cuda ✓  omp ✓  opencl ✓
streamcluster: cuda ✓ omp ✓ opencl ✓
```
