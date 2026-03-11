# Full Batch: Run All Rodinia Specs and Generate Results Matrix

> **Session type:** OpusPlan — use Plan Mode for exploration, then implement.
> **Working directory:** `~/Desktop/parbench_sam/`
> **Venv:** Always activate first: `source env_parbench/bin/activate`. Then use `python3`.
> **Do not modify any spec file or `manifest.jsonl` without explicit approval.**

---

## Background

This project runs GPU benchmark harness verification across spec suites. Prior batches:
- CUDA/OMP (Phase 3): `scripts/run_cuda_batch.sh`, `scripts/run_omp_batch.sh`, results in `results/phase3/`
- HeCBench (Phase 5): results in `results/phase5/` with per-kernel `.log` + `.json`

This task adds **Rodinia** (60 specs across 3 APIs: `cuda`, `omp`, `opencl`). All spec files already exist at `specs/rodinia-*.json`.

---

## Phase 1 — Explore (Plan Mode, read-only)

**Enter Plan Mode before doing anything.**

Use **parallel Explore subagents** to read the following simultaneously — do not run any commands yet:

**Subagent A — Understand the batch runner pattern:**
- Read `scripts/run_cuda_batch.sh` in full
- Read `scripts/run_omp_batch.sh` in full
- Note: harness invocation syntax, log/JSON output paths, TSV summary format, timeout handling, progress printing

**Subagent B — Understand the analysis pattern:**
- Read `scripts/analyze_omp_batch.py` in full
- Read `scripts/analyze_cuda_batch.py` in full
- Read `scripts/generate_results_matrix.py` in full
- Note: how JSON logs are parsed, what fields are extracted, how the markdown table is structured

**Subagent C — Inventory the Rodinia specs:**
- List all files matching `specs/rodinia-*.json`
- Count them by API: how many `cuda`, `omp`, `opencl`
- Check `config/paths.json` and confirm `project_root` and `downloads_root` match this machine
- Spot-check 2–3 specs (one per API) to confirm the `source_dir` paths resolve to real directories on disk

Collect all 3 subagent reports, then summarize:
1. The exact harness command used in existing batch scripts
2. The per-kernel output file naming convention
3. The TSV and JSON summary structures
4. Total Rodinia spec count and per-API breakdown
5. Any path or config issues found

**Do not proceed past Phase 1 until the summary is reviewed.**

---

## Phase 2 — Plan

Based on Phase 1 findings, produce a written plan covering:

1. **`scripts/run_rodinia_batch.sh`** — what it will do differently from `run_cuda_batch.sh`:
   - It must loop over all 3 APIs (`cuda`, `omp`, `opencl`) or all `rodinia-*.json` specs in one pass
   - Output directories: `results/rodinia/logs/` for per-kernel `.log` and `.json`, `results/rodinia/logs/_summary.tsv` for the TSV
   - Timeout behavior (harness has a 300s timeout per spec; note any builds that might exceed this)
   - Progress output format

2. **`scripts/analyze_rodinia_batch.py`** — what it produces:
   - `results/rodinia/rodinia_results.json` — structured summary (same schema as `omp_batch_results.json`)
   - `results/rodinia/results_matrix_rodinia.md` — markdown table with columns for CUDA / OMP / OpenCL (3 APIs, unlike HeCBench's 2); rows are kernel names; cells show build status, run time, verify status

3. Any fixes needed to `config/paths.json` or the harness invocation before running

**Present the plan for approval before writing any files.**

---

## Phase 3 — Implement (scripts only, do not run yet)

After plan approval, create both scripts:

### Step 3a — `scripts/run_rodinia_batch.sh`

Model it on `scripts/run_cuda_batch.sh` with these requirements:
- Shebang: `#!/usr/bin/env bash`
- Create `results/rodinia/logs/` if it does not exist
- Loop over all `specs/rodinia-*.json` (glob, sorted)
- Activate the venv at the top of the script: `source "$(dirname "$0")/../env_parbench/bin/activate"`
- Per spec, run:
  ```bash
  python3 -m harness --json -v verify "$SPEC" --config correctness \
    > "results/rodinia/logs/${KERNEL}.log" 2>&1
  ```
  where `KERNEL` is the spec filename without `.json` (e.g., `rodinia-bfs-cuda`)
- Also save the JSON output separately as `results/rodinia/logs/${KERNEL}.json`
- Append one TSV row per spec to `results/rodinia/logs/_summary.tsv`: `kernel \t api \t build \t run_exit \t verify \t elapsed_s`
- Print progress: `[N/60] rodinia-bfs-cuda ... PASS` (or `FAIL`)
- Do not exit early on failure — always continue to the next spec

After writing the script, show it to me for review before proceeding.

### Step 3b — `scripts/analyze_rodinia_batch.py`

Model it on `scripts/analyze_omp_batch.py` with these requirements:
- Read all `.json` files from `results/rodinia/logs/`
- Parse build status, run exit code, verify result, and elapsed time from each
- Write `results/rodinia/rodinia_results.json` (same top-level schema as `omp_batch_results.json`)
- Write `results/rodinia/results_matrix_rodinia.md`:
  - One row per unique kernel name (the slug, e.g., `bfs`, `hotspot`, `lud`)
  - Three API columns: CUDA | OMP | OpenCL
  - Cell format: `BUILD_OK / RUN_OK / VERIFY_OK` or `BUILD_FAIL` etc., with elapsed time if available
  - Footer: total pass/fail counts per API
- Print a console summary: total specs, pass/fail per API, list of all failures with reason

After writing the script, show it to me for review before proceeding.

---

## Phase 4 — Run

After both scripts are reviewed and approved:

### Step 4a — Run the batch

```bash
bash scripts/run_rodinia_batch.sh
```

Run in the **foreground** so progress is visible. The harness has a 300s per-spec timeout built in. If any spec appears to hang beyond that, note it and move on — do not kill the whole batch.

Use a **subagent** to monitor and collect results so the verbose build/run output does not fill the main context. The subagent should:
- Watch for completion
- Return only: total specs run, count of PASS/FAIL, and any specs that errored unexpectedly (non-timeout failures)

### Step 4b — Run the analyzer

```bash
source env_parbench/bin/activate && python3 scripts/analyze_rodinia_batch.py
```

---

## Phase 5 — Final Report

After analysis completes, print the consolidated summary in this format:

```
## Rodinia Batch Results

Total specs: N
CUDA:   X pass / Y fail
OMP:    X pass / Y fail
OpenCL: X pass / Y fail

### Failures
| Spec | Stage | Reason |
|------|-------|--------|
| rodinia-XXX-cuda | build | <error summary> |
...

### Output files
- results/rodinia/logs/_summary.tsv
- results/rodinia/rodinia_results.json
- results/rodinia/results_matrix_rodinia.md
```

---

## Success Criteria

The task is complete when:
- [ ] `scripts/run_rodinia_batch.sh` exists and ran to completion (all 60 specs attempted)
- [ ] `results/rodinia/logs/` contains one `.log` and one `.json` per spec
- [ ] `results/rodinia/logs/_summary.tsv` exists with 60 rows
- [ ] `results/rodinia/rodinia_results.json` is valid JSON with per-kernel entries
- [ ] `results/rodinia/results_matrix_rodinia.md` renders a table with 3 API columns
- [ ] Final summary printed to console

If any step fails, stop, report the error and diagnosis, and wait for direction.
