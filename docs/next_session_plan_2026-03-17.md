# Next Session Plan — 2026-03-17

> **Goal:** Complete Tasks 4-5 from the weekly plan, fix speedup measurement, verify Erel's branch, audit repo for cleanup.
> **How to use:** Feed each task block to Claude Code as a prompt. Tasks are ordered by dependency.
> **Context:** Tasks 1-3 are DONE. See `docs/weekly_plan_2026-03-16.md` for the full weekly plan.

---

## Task D: Verify and Merge Erel's `erel/missing_codes` Branch

> Can start immediately — no API keys needed.

**Prompt for Claude Code:**

```
Verify Erel's `erel/missing_codes` branch before merging into main.

## Branch status (pre-analyzed)
- 1 commit ahead of main: `99022f3` "Add new benchmark specs and implementation updates"
- 1 commit behind main: `8e194af` (evaluation smoke test — no file overlap)
- Merge should be clean — erel touched specs/manifest, main touched evaluation scripts

## New content from erel
5 new Rodinia specs: gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl.
Plus: fix to rodinia-heartwall-opencl.json, 5 manifest entries, rodinia directory pointer update.

## Verification steps (do all of these):

1. Fetch the branch: `git fetch origin`

2. Schema validation — check each new spec (checkout the branch files first):
   ```bash
   git checkout origin/erel/missing_codes -- specs/rodinia-gaussian-omp.json specs/rodinia-huffman-omp.json specs/rodinia-huffman-opencl.json specs/rodinia-hybridsort-omp.json specs/rodinia-mummergpu-opencl.json
   for spec in gaussian-omp huffman-omp huffman-opencl hybridsort-omp mummergpu-opencl; do
     python3 scripts/validate_schema.py --spec specs/rodinia-${spec}.json
   done
   ```

3. Manifest cross-check — verify each new manifest entry's kernel_name matches the spec's identity.kernel_name.

4. Build/run smoke test — for each new spec, try:
   ```bash
   python3 -m harness -v verify specs/rodinia-{spec}.json
   ```
   Some may fail (hybridsort, mummergpu are known problematic). Record results — don't try to fix.

5. Review the heartwall-opencl diff: `git diff main...origin/erel/missing_codes -- specs/rodinia-heartwall-opencl.json`

6. Note: commits are authored by `root` — unusual. Check if this is Erel's machine.

7. After verification, merge with:
   ```bash
   git merge origin/erel/missing_codes --no-ff -m "Merge erel/missing_codes: 5 new Rodinia specs (gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl)"
   ```

Report the verification results table before merging — wait for my approval.
```

---

## Task A: Pilot Test — 5 Kernels × 2 Models (Task 4 from weekly plan)

**Prompt for Claude Code:**

```
Run pilot tests: 5 kernels × cuda→omp × 2 models = 10 evaluations.
1 already done (bfs with Claude) → 9 remaining.

## Prerequisites
First confirm API keys are set:
```bash
source env_parbench/bin/activate
python3 -c "import os; print('ANTHROPIC:', bool(os.environ.get('ANTHROPIC_API_KEY'))); print('OPENAI:', bool(os.environ.get('OPENAI_API_KEY')))"
```
If OPENAI_API_KEY is missing, run only the Claude evaluations and tell me.

## Run order (Claude first, then GPT-4o)
Run these sequentially, one at a time:

```bash
# 2. hotspot - Claude
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-hotspot-cuda.json \
  --target specs/rodinia-hotspot-omp.json \
  --model claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam -v

# 3. backprop - Claude
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-backprop-cuda.json \
  --target specs/rodinia-backprop-omp.json \
  --model claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam -v

# 4. nw - Claude
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-nw-cuda.json \
  --target specs/rodinia-nw-omp.json \
  --model claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam -v

# 5. srad - Claude
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-srad-cuda.json \
  --target specs/rodinia-srad-omp.json \
  --model claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam -v

# 6-10. Repeat for GPT-4o (bfs, hotspot, backprop, nw, srad)
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model gpt-4o \
  --project-root /home/samyak/Desktop/parbench_sam -v
# ... (same pattern for hotspot, backprop, nw, srad with --model gpt-4o)
```

## After all complete, print summary table:
| Kernel   | Claude Sonnet | GPT-4o |
|----------|---------------|--------|
| bfs      | PASS (done)   | ...    |
| hotspot  | ...           | ...    |
| backprop | ...           | ...    |
| nw       | ...           | ...    |
| srad     | ...           | ...    |

Debug any failures. Common issues:
- Code extraction: LLM may not use exact `filename=X` format
- Build: Makefile expects specific filenames
- File restore: confirm originals unchanged after each run

Then commit results: "Add pilot evaluation results (Task 4: 5 kernels × 2 models)"
```

---

## Task B: Create Batch Evaluation Runner (Task 5 from weekly plan)

**Prompt for Claude Code:**

```
Create `scripts/evaluation/run_eval_batch.py` — a batch runner for LLM evaluation.

## What it does

Runs llm_evaluate.py logic across multiple spec pairs and models, with
checkpointing (skips if result JSON already exists).

## Key design — REUSE existing code:
- Import `evaluate_translation()` from `scripts.evaluation.llm_evaluate`
- Import `find_translation_pairs()` + `load_manifest()` from `harness.spec_loader`
- Follow pattern from `scripts/augmentation/run_augment_batch.py` (progress counter, incremental writes)

## CLI interface

```bash
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
```

## Arguments
- `--suite`: filter by source_suite (e.g., "rodinia")
- `--kernels`: comma-separated kernel names (overrides --suite)
- `--direction`: "cuda-to-omp", "omp-to-cuda", "cuda-to-opencl", "opencl-to-cuda", "omp-to-opencl", "opencl-to-omp", or "all"
- `--models`: comma-separated model names (required)
- `--augment-levels`: comma-separated augment levels (default: "0")
- `--project-root`: required, path to parbench_sam
- `--max-retries`: per-eval LLM retry count (default: 1)
- `--resume` / `--no-resume`: skip existing results (default: true)
- `--max-failures`: stop after N consecutive failures (default: 5)
- `-v`: verbose

## Pair selection logic
1. `load_manifest()` → all entries
2. `find_translation_pairs()` → all (kernel, src_api, tgt_api) triples
3. Filter by --suite or --kernels
4. Filter by --direction
5. For each pair, load both specs and check `baseline_results.configurations.correctness.status == "pass"` for both. Skip pairs where either baseline fails.

## Checkpointing
Before each evaluation, check if `results/evaluation/{model}/{source_id}-to-{target_id}.json` exists.
If --resume and file exists → skip with "[SKIP] already evaluated: ..." message.

## Output
- Per-task JSONs: `results/evaluation/{model}/{source}-to-{target}.json` (via evaluate_translation)
- Batch summary JSON: `results/evaluation/batch_{model}_{direction}_{timestamp}.json`
- Batch summary markdown with pass/fail matrix

## Verify after:
```bash
python3 scripts/evaluation/run_eval_batch.py --help
```
Then do a test run on just the 5 pilot kernels (should SKIP all since Task A already ran them):
```bash
python3 scripts/evaluation/run_eval_batch.py \
  --kernels bfs,hotspot,backprop,nw,srad \
  --direction cuda-to-omp \
  --models claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam -v
```

Commit: "Add batch evaluation runner (Task 5)"
```

---

## Task C: Fix Speedup Measurement (Researcher Feedback)

**Prompt for Claude Code:**

```
Fix the speedup measurement in the evaluation pipeline. The research team says:
"Wall clock time is not a correct way to measure kernel performance. Use (1) kernel
execution time from a profiler, or (2) User CPU time + Sys CPU time."

## Current problem
Everything uses `time.monotonic()` (wall-clock around subprocess.run()):
- harness/runner.py:80-92 — RunResult.duration_seconds is wall-clock
- scripts/baselines/populate_baseline_results.py:83 — stored as wall_time_seconds
- scripts/evaluation/llm_evaluate.py:682-688 — speedup_ratio uses wall-clock

## Phase C1: Add `/usr/bin/time` CPU timing (do this first)

Modify `harness/runner.py` to optionally wrap run commands with `/usr/bin/time -v`:
1. Add `cpu_time_seconds: float | None = None` to `RunResult` in `harness/models.py`
2. In `harness/runner.py`, add `use_cpu_timing=False` parameter to `run_spec()`
3. When enabled, prefix the command with `/usr/bin/time -v` and parse stderr for:
   - `User time (seconds): X.XX`
   - `System time (seconds): X.XX`
   - cpu_time = user_time + sys_time
4. Store in `RunResult.cpu_time_seconds`
5. Important: `/usr/bin/time -v` writes to stderr — need to separate its output from the program's stderr (use a temp file for time output: `/usr/bin/time -v -o /tmp/parbench_time.txt`)

## Phase C2: Add `nsys` kernel timing for GPU Frameworks like CUDA, OpenAC, and OpenMP with GPU Offloading (do this second)

1. First check: `which nsys` or look in `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/`
2. Add `kernel_time_seconds: float | None = None` to `RunResult`
3. When `use_profiler=True` and spec's parallel_api is "cuda" or "openacc" or (ceck for when openmp is using GPU offloading pragmas or uses gpu FOR ANY PART OF THE PARALLELIZATION):
   - Wrap with: `nsys profile --stats=true -o /tmp/parbench_nsys --force-overwrite true {cmd}`
   - Parse total kernel time from nsys stats output
4. Only for CUDA, openacc, openmp using gpu for parallelization specs — OMP/OpenCL use CPU timing from C1

## Phase C3: Update speedup calculation

In `scripts/evaluation/llm_evaluate.py`:
1. Add `--use-cpu-timing` flag (default: True)
2. Add `--use-profiler` flag (default: False)
3. Compute speedup with priority: kernel_time > cpu_time > wall_time
4. Add new fields to result JSON: `cpu_time_seconds`, `kernel_time_seconds`,
   `baseline_cpu_time_seconds`, `baseline_kernel_time_seconds`, `speedup_method`

Do NOT re-run baselines yet — that will happen later when we get team API keys
for the full experiment run. For now, just add the infrastructure. 
Pause and ask me to give you put in the code api and teach me how to use a openai mode api given to me this way in the message "https://galor-m8yvytc2-swedencentral.cognitiveservices.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview", along with a long "key". i will not enter the "key" into claude code or any ai tool, i will enteri tmanualy in the terminal to set it up so tell me the commands to set it up using this resource that was given to me by the research team lead. 
The, once you have the keys in place, proceed to do the full scale runs using this openai model.  

Commit: "Add CPU/kernel timing to harness runner and evaluation pipeline"
```

---

## Task E: Repo Cleanup Audit (Report Only — Do NOT Delete Anything)

**Prompt for Claude Code:**

```
Audit the repo for bloat, stale files, and unmaintainable code. Do NOT delete anything —
just produce a report for my review.

## Areas to audit:

### 1. Large binary files tracked in git
List all binary files (png, pptx, xlsx, pdf, json >1MB) with sizes.
Known large files:
- presentations/ParBench_Presentation.pptx (7.8 MB)
- analysis/visualizations/*.png (~9.5 MB total, one is 5.8 MB)
- ParaCodex Results.pptx at REPO ROOT (1.5 MB — misplaced)
- examples/example_178_kernels.json (1.5 MB)

### 2. Stale/duplicate scripts
- scripts/archive/generate_phase3_specs.py.bak (86 KB .bak file in git)
- scripts/batch/ has 6 near-duplicate rodinia batch scripts
- scripts/baselines/ has 3 overlapping baseline population scripts

### 3. Oversized generators
- scripts/generators/generate_phase3_specs.py (1,737 lines)
- scripts/generators/generate_phase2_specs.py (1,373 lines)
These were run once — are they still needed?

### 4. Misplaced files
- ParaCodex Results.pptx at repo root (should be in presentations/)

### 5. Stale config
- .mcp.json has a `css-docs` MCP server — irrelevant for GPU benchmarks

### 6. Anything else suspicious
Look for any other files that seem redundant, stale, or out of place.

## Output format
Produce a markdown report at `docs/repo_cleanup_audit_2026-03-17.md` with:
- Each item categorized as HIGH/MEDIUM/LOW priority
- Size impact
- Recommendation (delete, move, consolidate, Git LFS, or keep)
- For each item: what breaks if we remove it?

Do NOT modify or delete anything. This is investigation only.
```

---

## Quick Reference

| Task | Deliverable | Depends on |
|------|-------------|------------|
| D | Merge 5 new specs from erel | Nothing |
| A | 10 pilot evaluation results | API keys |
| B | `scripts/evaluation/run_eval_batch.py` | Task A experience |
| C | CPU/kernel timing in harness + eval | Nothing (infrastructure) |
| E | Cleanup audit report | Nothing |

## After These Tasks

Remaining from weekly plan (awaiting team API keys for full experiments):
- Task 6: Full Rodinia eval — Claude (uses batch runner from B)
- Task 7: Full Rodinia eval — GPT-4o
- Task 8: Results analyzer script
- Task 9: Evaluation dashboard
- Task 10: Commit and push everything
- Task 11: SC26 paper sections (stretch)
