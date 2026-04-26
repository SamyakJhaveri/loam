# AGENTS.md — ParBench

<!-- PARBENCH_AGENTS_CANARY_2026 — used to verify Codex reads this file -->

ParBench is a kernel-centric benchmark for evaluating LLM-based parallel code
translation across CUDA, OpenMP, and OpenCL. Targeting NeurIPS 2026 Datasets &
Benchmarks track (deadline: May 1, 2026).

For full project rules, read `CLAUDE.md` in this same directory. The invariants
and architecture described there are authoritative. This file provides
Codex-specific review guidance.

## Architecture

| Path | Purpose |
|------|---------|
| `specs/` | Kernel spec JSONs (`{suite}-{slug}-{api}.json`) — 206 total |
| `manifest.jsonl` | Append-only kernel registry — never modify existing entries |
| `harness/` | Build → Run → Verify pipeline. Invoke: `python3 -m harness` |
| `scripts/evaluation/` | LLM eval pipeline (`run_eval_batch.py`, `llm_evaluate.py`) |
| `scripts/analysis/` | Result analysis and paper data generation |
| `results/` | Immutable eval + augmentation result JSONs |
| `c_augmentation/` | AST transforms (libclang). Tests: `pytest c_augmentation/test_transforms.py` |
| `schema/` | JSON schema for spec validation |
| `docs/paper/` | NeurIPS paper source and figures |

## Key Invariants

These rules are non-negotiable. Flag any violation during review:

1. **`manifest.jsonl` is append-only** — never modify or delete existing entries
2. **Result JSONs are immutable** — files in `results/` must never be modified after creation
3. **Never change spec run args** without verifying the source code's `argc` check
4. **9 KNOWN_FAIL specs** must be excluded from eval batches and pass-rate denominators
5. **~15 schema validation errors are expected** (from 5 deleted phantom specs) — do not fix

## KNOWN_FAIL Specs (9 total — exclude from all evaluations)

- `rodinia-kmeans-cuda` — texture<> removed in CUDA 12
- `rodinia-mummergpu-cuda` — texture<> removed in CUDA 12
- `rodinia-mummergpu-omp` — texture<> + cuMemGetInfo_v2 signature
- `rodinia-hybridsort-cuda` — GL/glew.h not found
- `rodinia-nn-opencl` — TIMEOUT / SIGSEGV
- `rodinia-kmeans-opencl` — SIGSEGV in OpenCL runtime
- `rodinia-backprop-opencl` — clEnqueueReadBuffer error
- `hecbench-stencil1d-omp_target` — BUILD_FAIL
- `hecbench-scan-omp_target` — VERIFY_FAIL

The canonical exclusion list is in `harness/constants.py` → `EXCLUDED_SPECS`.

## Build & Test Commands

```bash
source env_parbench/bin/activate                          # activate venv
python3 -m harness verify specs/rodinia-bfs-cuda.json     # verify single spec
python3 scripts/spec_tools/validate_schema.py --all       # schema check (~15 errors expected)
pytest c_augmentation/test_transforms.py                  # augmentation tests
pytest tests/                                             # unit tests
```

## End-of-Session Codex Review (Mandatory)

At the end of every Claude Code session with substantive changes, Codex must be
invoked for a cross-model second opinion: `/codex:rescue review the uncommitted
changes`. After review, `touch .codex_review_done` marks completion. The
pre-commit hook reminds if this step is skipped. Codex catches issues that
same-model self-review misses.

## Review Guidelines

When reviewing code in this repository, focus on these areas:

**Critical (must flag):**
- Modifications to existing entries in `manifest.jsonl`
- Modifications to existing result JSONs in `results/evaluation/`
- Spec `run_args` that don't match the source code's `argc` check
- KNOWN_FAIL specs included in eval batch configurations
- Pass-rate denominators that don't exclude KNOWN_FAIL specs
- API keys, secrets, or credentials in code

**Important (should flag):**
- Data races, memory model violations, or synchronization bugs in CUDA/OpenMP/OpenCL code
- Inconsistencies between `CLAUDE.md` / `known-issues.md` and actual code behavior
- Stale line numbers or function names in documentation
- Missing `--resume` flag on evaluation commands (risks overwriting results)
- Schema validation errors beyond the expected ~15 (indicates a real problem)

**Style (optional):**
- Python: must use `python3`, never `python`
- Prefer `source env_parbench/bin/activate` before running any Python commands

## What NOT to Do

- Do NOT modify any files during review — reviews are read-only
- Do NOT attempt to fix KNOWN_FAIL specs — they are deferred intentionally
- Do NOT trust documentation over source code — the code is authoritative
