---
paths:
  - "scripts/evaluation/**"
---

# Evaluation Pipeline Rules

> Auto-loaded when working on `scripts/evaluation/` files.

## Quick-Start Commands

```bash
source env_parbench/bin/activate

# Single translation (dry-run to check prompt) — Phase 1: azure-gpt-4.1
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model azure-gpt-4.1 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --dry-run

# Batch run — ALWAYS pass --suite to avoid matching hecbench kernels by name
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --kernels bfs nw srad backprop hotspot \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v

# Batch with retries (iterative repair on failure)
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-omp \
  --models azure-gpt-4.1 \
  --max-retries 3 \
  --project-root /home/samyak/Desktop/parbench_sam -v

# Phase 2 (after M7 Groq/Modal setup): add llama-70b and leaderboard model to --models
```

## Architecture Overview

`llm_evaluate.py` pipeline per task:
1. Read source spec (`prompt_payload` files) + support files → build prompt
2. Call LLM → extract translated files from response
3. Back up existing files in target working dir
4. Write LLM output to target working dir
5. **Stage source headers** → copy `.h/.hpp/.cuh` from source `support_files` to target dir (only if missing)
6. Build (target spec `build.commands.build`)
7. Run correctness config
8. Verify (exit code / stdout pattern)
9. Restore original files; **unstage staged headers**

## Critical: --suite Filter

Without `--suite rodinia`, the batch runner matches kernels by name across ALL suites.
`--kernels nw backprop` will match both `rodinia-nw-*` AND `hecbench-nw-*`.
**Always pass `--suite rodinia`** (or the relevant suite) in batch runs.

## Result File Layout

Per-task results: `results/evaluation/{model}/{src_id}-to-{tgt_id}.json`

Key fields in result JSON:
- `overall_status` — PASS / BUILD_FAIL / RUN_FAIL / VERIFY_FAIL / ERROR / SKIP
- `source_spec` / `target_spec` — spec IDs (e.g. `"rodinia-nw-cuda"`)
- `prompt_tokens` / `completion_tokens` — LLM token usage
- `attempts[]` — each attempt has `build_error_snippet` (head+tail of stderr)
- `run_stderr_snippet` / `run_stdout_snippet` — set on RUN_FAIL
- `error_message` — human-readable failure summary
- `speedup_ratio` / `timing_method` — set on PASS

## Python Gotcha: null JSON values

`dict.get("key", {})` returns `None` (not `{}`) when the key EXISTS with a null JSON value.
**Always use the `or {}` guard:**
```python
# WRONG — crashes when baseline_results is null
spec.get("baseline_results", {}).get("configurations", {})

# CORRECT
(spec.get("baseline_results") or {}).get("configurations", {})
```
This affects any spec field that can be `null` in JSON: `baseline_results`, `performance`, `hardware`, etc.

## Header Staging Mechanism

`_stage_support_headers()` in `llm_evaluate.py` copies `.h/.hpp/.cuh` files from the
**source spec's** `support_files` into the **target spec's** working directory — only if
they don't already exist there. They are removed in the `finally` block by `_unstage_support_headers()`.

This fixes the pattern where LLM translates CUDA code that `#include`s a header (e.g.
`needle.h`, `srad.h`) — the header doesn't exist in the OMP target directory, causing
BUILD_FAIL. The staged header is available during build, then cleaned up.

**Verification**: After every eval run, these directories should have NO `.h` files:
```bash
ls rodinia/openmp/{nw,srad/srad_v2,hotspot}/*.h 2>&1  # should all say "No such file"
```

## Prompt Enhancement

`_read_support_files()` reads source `support_files` and adds a "## Support / Header Files"
section to the LLM prompt. The LLM is instructed to **inline definitions** from headers
rather than emitting `#include` statements that won't resolve in the target directory.

Headers (`.h/.hpp/.cuh`) are always included. Code files (`.c/.cpp/.cu`) are included up
to `max_chars=50000` cumulative limit to avoid prompt bloat.

## OMP Spec Run Argument Patterns

Pitfall: CUDA binaries often take fewer args than OMP equivalents (OMP adds `nthreads`).
When writing or verifying OMP specs, check the reference OMP source `argc` check carefully.

Known-correct args (re-verified 2026-03-20 against source argc checks):
- `rodinia-nw-omp`: `['2048', '10', '4']` — 3 args: <dimension> <penalty> <num_threads> (needle.cpp:249 checks argc==4)
- `rodinia-hotspot-omp`: `['512', '512', '2', '4', 'temp_512', 'power_512', 'output.out']` — 7 args: <rows> <cols> <sim_time> <threads> <temp> <power> <output> (hotspot_openmp.cpp:282 checks argc!=8)
- `rodinia-srad-omp`: `['512', '512', '0', '127', '0', '127', '2', '0.5', '2']` — 9 args, position 7 is nthreads=2

Always run the reference binary to check: `./binary --help` or just run it with no args to see usage.

## Pilot Results (2026-03-17, cuda→omp)

| Kernel | claude-sonnet-4 | azure-gpt-4.1 | Failure category |
|--------|:-:|:-:|---|
| bfs | PASS | PASS | — |
| nw | PASS | PASS | Was infrastructure (needle.h) + spec arg bug |
| hotspot | BUILD_FAIL | PASS | claude: missing `#include <cstring>`; azure: was spec arg bug |
| srad | RUN_FAIL | RUN_FAIL | LLM drops nthreads arg (CUDA→OMP quality) |
| backprop | BUILD_FAIL | BUILD_FAIL | claude: dup `gettime`; azure: HEIGHT undeclared |

Pass rate improved from 20% (2/10) to 50% (5/10) after infrastructure + spec fixes.

## Git Worktrees — Submodule Warning

`rodinia/` is a git submodule. Git worktrees do NOT initialize submodules.
In a worktree, `rodinia/rodinia-src/openmp/` directories will be EMPTY — no Makefiles,
no source files. Any evaluation that needs to build Rodinia code will fail silently or
produce misleading results.

**Never run LLM evaluations in worktrees** unless you first symlink or copy the Rodinia
source dirs into the worktree. Use the main repo for all evaluations.
