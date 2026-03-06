# Smoke-Test: Verify Harness Works with Rodinia Specs

> **Session type:** OpusPlan — use Plan Mode for exploration, then implement.
> **Working directory:** `~/Desktop/parbench_sam/`
> **Venv:** Always activate first: `source env_parbench/bin/activate`. Then use `python3`.

---

## Context

This project (`parbench_sam`) benchmarks GPU kernels. Specs live in `specs/`, the harness is invoked as `python3 -m harness verify <spec.json> --config correctness -v` inside the activated `env_parbench` venv. Before running a full batch, verify 3 representative specs — one per parallel API — to catch path, build, or data-file issues early.

Key files to understand first:
- `specs/rodinia-bfs-cuda.json` — CUDA representative
- `specs/rodinia-hotspot-omp.json` — OpenMP representative
- `specs/rodinia-bfs-opencl.json` — OpenCL representative (only if OpenCL was confirmed working)
- `config/paths.json` — path resolution config
- `harness/` directory — harness source

---

## Phase 1 — Explore (Plan Mode, read-only)

**Enter Plan Mode before doing anything.**

Use the built-in **Explore subagent** to investigate the following in parallel, without modifying any files:

1. Read `config/paths.json` and confirm `project_root` and `downloads_root` are set correctly for this machine.
2. Read each of the 3 spec files above. For each, confirm:
   - `source_dir` resolves to a real path on disk
   - Required data files referenced in the spec exist
   - `parallel_api` matches the expected API (`cuda`, `omp`, `opencl`)
3. Inspect the `harness/` directory to understand how `python3 -m harness verify` dispatches build and run steps.

Summarize findings before proceeding. Do not run any commands yet.

---

## Phase 2 — Plan

Based on the Explore findings, produce a plan covering:

- Which specs are safe to test (source dir exists, data files present)
- Any path or config issues to fix before running
- The exact command for each spec test
- What a PASS looks like at each stage (build, run, verify)

**Do not start implementation until the plan is reviewed.**

---

## Phase 3 — Execute (parallel subagents, one per spec)

After plan approval, spawn **3 parallel subagents** — one per spec — each running independently:

### Subagent A — CUDA
```bash
source env_parbench/bin/activate && python3 -m harness verify specs/rodinia-bfs-cuda.json --config correctness -v
```

### Subagent B — OMP
```bash
source env_parbench/bin/activate && python3 -m harness verify specs/rodinia-hotspot-omp.json --config correctness -v
```

### Subagent C — OpenCL *(skip if OpenCL was not confirmed working)*
```bash
source env_parbench/bin/activate && python3 -m harness verify specs/rodinia-bfs-opencl.json --config correctness -v
```

Each subagent reports back **only** the structured result below — do not return raw build logs unless there is a failure.

---

## Required Output Format (per spec)

```
### Spec: <spec filename>
- Build:  PASS | FAIL — <one-line summary or error>
- Run:    PASS | FAIL — exit code <N>, first 5 lines of stdout
- Verify: PASS | FAIL — strategy matched: <strategy name> | no match
```

If **any stage fails**, the subagent must also report:
1. The full error output (stdout + stderr)
2. A diagnosis: what is the likely root cause? (path issue? missing data file? make.config? missing dependency?)
3. A proposed fix — but **do not apply any fix** without explicit user approval.

---

## Constraints

- **Do not modify** any spec file, source file, or `manifest.jsonl` without approval.
- **Do not proceed** to full-batch testing after this smoke test — report results and stop.
- If a fix is needed, state it clearly and wait for the user to say "go ahead" before touching anything.
- All 3 subagent results must be collected before presenting the final summary.

---

## Success Criteria

The smoke test passes when:
- All 3 specs reach **Build: PASS** and **Run: PASS** (exit code 0)
- At least one verify strategy matches for each spec
- No unexpected file-not-found or permission errors

If any spec fails, present a consolidated failure report and await direction before proceeding.
